import sys
import os

import config
import operator
import unique_items
import load_txts
from affixes import *
import table_strings
from utils import *
from mako.template import Template
from mako.lookup import TemplateLookup

class Runeword:
    def __init__(self, name, runes, allowed_bases, excluded_bases, properties):
        self.name = name
        self.runes = runes
        self.num_sockets = len(runes)
        self.allowed_bases = allowed_bases
        self.excluded_bases = excluded_bases
        self.properties = properties

    def rune_string(self):
        ret = ""
        for rune in self.runes:
            ret = ret + rune + "<br>"
        return ret

    def bases_string(self):
        ret = ""
        for base in self.allowed_bases:
            ret = ret + base + "<br>"
        for i, base in enumerate(self.excluded_bases):
            if i == 0:
                ret = ret + "<br>Excluded:<br>"
            ret = ret + base + "<br>"
        return ret

    def stats_string(self):
        ret = ""
        allstats = []
        for prop in self.properties:
            for stat in prop.stats:
                allstats.append(stat)
        #allstats.sort(key = lambda x: (int(x.item_level), int(x.required_level)))
        for stat in sorted(allstats, key=lambda x: int(x.priority)):
            ret = ret + stat.stat_string + "<br>"
        return ret


class Item_Group:
    def __init__(self, name):
        self.name = name
        self.items = []

class Database_Generator:
    def __init__(self, db_code, db_name, db_version, string_tables, include_implicits_on_uniques, gemapplytype_names):
        self.db_code = db_code
        self.db_name = db_name
        self.db_version = db_version
        self.string_tables = string_tables
        self.mod_strings = table_strings.get_string_dict(db_code, string_tables)
        self.mylookup = TemplateLookup(directories=[os.getcwd()])
        self.tables = Tables(db_code)
        self.utils = Utils(self.tables, self.mod_strings)
        self.include_implicits_on_uniques = include_implicits_on_uniques
        self.gemapplytype_names = gemapplytype_names

    def generate(self, body_template, filename):
        base_template = Template(filename="templates/base.htm", lookup=self.mylookup)
        base_rendered = base_template.render(body=body_template,
                                             name=self.db_name,
                                             version=self.db_version).replace("\r","")
        open("../" + self.db_code + "/" + filename, "w").write(base_rendered)

    def generate_static(self, extra=[]):
        filenames = ["gems.htm", "maps.htm", "sets.htm", "recipes.htm", "gemwords.htm"]
        filenames = filenames + extra
        for filename in filenames:
            template = Template(filename="templates/" + filename, lookup=self.mylookup)
            rendered = template.render()
            self.generate(rendered, filename)

    def generate_armor(self):
        normal_armors = []
        exceptional_armors = []
        elite_armors = []
        for armor_row in self.tables.armor_table:
            if armor_row["spawnable"] != "0":
                for item_type_row in self.tables.item_types_table:
                    if armor_row["type"] == item_type_row["Code"] and armor_row["type"] != "":
                        item = Item(armor_row["namestr"], 1, armor_row["levelreq"], [], armor_row["code"], self.mod_strings, self.tables)
                        automods = []
                        for p in item.properties:
                            if p.is_automod:
                                for s in p.stats:
                                    automods.append(s.stat_string)
                        armor = [self.mod_strings.get(armor_row["namestr"], armor_row["name"]), #0: name
                                 item_type_row["ItemType"],  #1: category
                                 armor_row["levelreq"],      #2: req_level
                                 armor_row["code"],          #3: code
                                 armor_row["normcode"],      #4: norm_code
                                 armor_row["ubercode"],      #5: exceptional_code
                                 armor_row["ultracode"],     #6: elite code                           
                                 armor_row["minac"],         #7: min defense
                                 armor_row["maxac"],         #8: max defense
                                 armor_row["durability"],    #9: durability
                                 armor_row["speed"],         #10: frw
                                 armor_row["level"],         #11: qlvl
                                 armor_row["magic lvl"],     #12: mag lvl
                                 armor_row["reqstr"],        #13: req str
                                 armor_row["block"],         #14: block
                                 armor_row["mindam"],        #15: min damage
                                 armor_row["maxdam"],        #16: max damage
                                 armor_row["gemsockets"],    #17: sock
                                 armor_row["gemapplytype"],  #18: gem_type
                                 self.utils.string_array_to_html(automods, 2),          #19: automods
                                 item.staffmod,     #20: staffmods
                                ]
                        if armor_row["normcode"] == armor_row["code"]:
                            normal_armors.append(armor)
                        if armor_row["ubercode"] == armor_row["code"]:
                            exceptional_armors.append(armor)
                        if armor_row["ultracode"] == armor_row["code"]:
                            elite_armors.append(armor)

        # First sort normal armors by level req
        normal_armors.sort(key = operator.itemgetter(2))

        armors = list(normal_armors)
        # Now append exceptional armors in order
        for normal_armor in list(normal_armors):
            for exceptional_armor in list(exceptional_armors):
                if normal_armor[5] == exceptional_armor[3]:
                    armors.append(exceptional_armor)
                    exceptional_armors.remove(exceptional_armor)
                    break
        if len(exceptional_armors) != 0:
            print("Uh oh... we didn't find a matching base for all exceptional armors")

        # Now append elite armors in order
        for normal_armor in list(normal_armors):
            for elite_armor in list(elite_armors):
                if normal_armor[6] == elite_armor[3]:
                    armors.append(elite_armor)
                    elite_armors.remove(elite_armor)
                    break
        if len(elite_armors) != 0:
            print("Uh oh... we didn't find a matching base for all elite armors")

        armor_template = Template(filename="templates/armors.htm", lookup=self.mylookup)
        armor_rendered = armor_template.render(armors)
        self.generate(armor_rendered, "armors.htm")

    def replace_if_empty(self, string, replacement):
        if string == "":
            return replacement
        return string

    def get_avg(self, mindam, maxdam):
        ret = ""
        if mindam != "":
            ret = str(round((float(mindam) + float(maxdam)/2.0), 1)) + " Avg"
        return ret
    
    def get_dmg(self, mindam, maxdam):
        ret = ""
        if mindam != "":
            ret = str(mindam) + " to " + str(maxdam)
        return ret

    def generate_weapons(self):
        normal_weapons = []
        exceptional_weapons = []
        elite_weapons = []
        for weapon_row in self.tables.weapons_table:
            if weapon_row["spawnable"] != "0":
                for item_type_row in self.tables.item_types_table:
                    if weapon_row["type"] == item_type_row["Code"] and weapon_row["type"] != "":
                        item = Item(weapon_row["namestr"], 1, weapon_row["levelreq"], [], weapon_row["code"], self.mod_strings, self.tables)
                        automods = []
                        for p in item.properties:
                            if p.is_automod:
                                for s in p.stats:
                                    automods.append(s.stat_string)
                        weapon = [self.mod_strings.get(weapon_row["namestr"], weapon_row["name"]), #0: name
                                 item_type_row["ItemType"],  #1: category
                                 weapon_row["levelreq"],     #2: req_level
                                 weapon_row["code"],         #3: code
                                 weapon_row["normcode"],     #4: norm_code
                                 weapon_row["ubercode"],     #5: exceptional_code
                                 weapon_row["ultracode"],    #6: elite code                           
                                 self.get_dmg(weapon_row["mindam"], weapon_row["maxdam"]), #7
                                 self.get_avg(weapon_row["mindam"], weapon_row["maxdam"]), #8
                                 self.get_dmg(weapon_row["2handmindam"], weapon_row["2handmaxdam"]), #9
                                 self.get_avg(weapon_row["2handmindam"], weapon_row["2handmaxdam"]), #10
                                 self.get_dmg(weapon_row["minmisdam"], weapon_row["maxmisdam"]), #11
                                 self.get_avg(weapon_row["minmisdam"], weapon_row["maxmisdam"]), #12
                                 weapon_row["rangeadder"],   #13: range
                                 weapon_row["durability"],   #14: durability
                                 weapon_row["speed"],        #15: wsm?
                                 weapon_row["level"],        #16: qlvl
                                 weapon_row["magic lvl"],    #17: mag lvl
                                 weapon_row["reqstr"],       #18: req str
                                 weapon_row["reqdex"],       #19: req dex
                                 self.replace_if_empty(weapon_row["StrBonus"], 0), #20: str bonus
                                 self.replace_if_empty(weapon_row["DexBonus"], 0), #21: dex bonus
                                 weapon_row["gemsockets"],   #22: sock
                                 weapon_row["gemapplytype"], #23: gem_type
                                 self.utils.string_array_to_html(automods, 2), #24: automods
                                 item.staffmod,              #25: staffmods
                                ]
                        if weapon_row["normcode"] == weapon_row["code"]:
                            normal_weapons.append(weapon)
                        if weapon_row["ubercode"] == weapon_row["code"]:
                            exceptional_weapons.append(weapon)
                        if weapon_row["ultracode"] == weapon_row["code"]:
                            elite_weapons.append(weapon)

        # First sort normal weapons by level req
        normal_weapons.sort(key = operator.itemgetter(2))

        weapons = list(normal_weapons)
        # Now append exceptional weapons in order
        for normal_weapon in list(normal_weapons):
            for exceptional_weapon in list(exceptional_weapons):
                if normal_weapon[5] == exceptional_weapon[3]:
                    weapons.append(exceptional_weapon)
                    exceptional_weapons.remove(exceptional_weapon)
                    break
        if len(exceptional_weapons) != 0:
            print("Uh oh... we didn't find a matching base for all exceptional weapons")

        # Now append elite weapons in order
        for normal_weapon in list(normal_weapons):
            for elite_weapon in list(elite_weapons):
                if normal_weapon[6] == elite_weapon[3]:
                    weapons.append(elite_weapon)
                    elite_weapons.remove(elite_weapon)
                    break
        if len(elite_weapons) != 0:
            print("Uh oh... we didn't find a matching base for all elite weapons")

        weapon_template = Template(filename="templates/weapons.htm", lookup=self.mylookup)
        weapon_rendered = weapon_template.render(weapons)
        self.generate(weapon_rendered, "weapons.htm")

    def get_other_types(self, remaining_items):
        other_types = []
        for item in remaining_items:
            if item.base_code not in other_types:
                other_types.append(item.base_code)
        return other_types

    def get_weapon_types(self):
        weapon_types = []
        for weapon in self.tables.weapons_table:
            if weapon["type"] not in weapon_types:
                weapon_types.append(weapon["type"])
        return weapon_types

    def get_item_type_name_from_code(self, code):
        # Hard code "tors" because "Armor" is confusing
        if code == "tors":
            return "Body Armor"

        for row in self.tables.item_types_table:
            if row["Code"] == code:
                return row["ItemType"]

        for row in self.tables.misc_table:
            if row["code"] == code:
                return row["name"]
        return "Unknown: " + code

    def get_armor_types(self):
        armor_types = []
        for armor in self.tables.armor_table:
            if armor["type"] not in armor_types:
                armor_types.append(armor["type"])
        return armor_types

    def weapon_is_a_subtype_of(self, subtype_code, maintype_code):
        for weapon in self.tables.weapons_table:
            if weapon["code"] == subtype_code and maintype_code == weapon["type"]:
                return True
        return False

    def armor_is_of_type(self, item_code, armor_code):
        for row in self.tables.armor_table:
            if row["code"] == item_code and armor_code == row["type"]:
                return True
        return False

    def set_weapon_bg_color(self, item):
        for weapon in self.tables.weapons_table:
            if item.base_code == weapon["ultracode"]:
                item.bg_color_code = 303030
                return
            if item.base_code == weapon["ubercode"]:
                item.bg_color_code = 202020
                return

    def set_armor_bg_color(self, item):
        for armor in self.tables.armor_table:
            if item.base_code == armor["ultracode"]:
                item.bg_color_code = 303030
                return
            if item.base_code == armor["ubercode"]:
                item.bg_color_code = 202020
                return

    def generate_uniques(self):
        unique_items_list = unique_items.get_unique_items(self.tables, self.mod_strings, self.include_implicits_on_uniques)
        item_groups = []
        unique_weapon_template = Template(filename="templates/uniques.htm",
                                          lookup=self.mylookup)
        for weapon_type in self.get_weapon_types():
            weapon_group = Item_Group(self.get_item_type_name_from_code(weapon_type))
            for item in list(unique_items_list):
                if self.weapon_is_a_subtype_of(item.base_code, weapon_type):
                    self.set_weapon_bg_color(item)
                    weapon_group.items.append(item)
                    unique_items_list.remove(item)
            if len(weapon_group.items) > 0:
                item_groups.append(weapon_group)
        unique_weapon_rendered = unique_weapon_template.render(item_groups=item_groups, page="weapons")
        base_template = Template(filename="templates/base.htm", lookup=self.mylookup)
        base_rendered = base_template.render(body=unique_weapon_rendered,
                                             name=self.db_name,
                                             version=self.db_version).replace("\r","")    
        open("../" + self.db_code + "/" + "unique_weapons.htm", "w").write(base_rendered)

        item_groups = []
        unique_armor_template = Template(filename="templates/uniques.htm",
                                         lookup=self.mylookup)
        for armor_type in self.get_armor_types():
            armor_group = Item_Group(self.get_item_type_name_from_code(armor_type))
            for item in list(unique_items_list):
                #print("base code: " + item.base_code + " armor_type: " + armor_type)
                if self.armor_is_of_type(item.base_code, armor_type):
                    self.set_armor_bg_color(item)
                    armor_group.items.append(item)
                    unique_items_list.remove(item)
            if len(armor_group.items) > 0:
                item_groups.append(armor_group)
        unique_armor_rendered = unique_armor_template.render(item_groups=item_groups, page="armors")
        
        base_template = Template(filename="templates/base.htm", lookup=self.mylookup)
        base_rendered = base_template.render(body=unique_armor_rendered,
                                             name=self.db_name,
                                             version=self.db_version).replace("\r","")
        open("../" + self.db_code + "/" + "unique_armors.htm", "w").write(base_rendered)

        # Remove ores
        for item in list(unique_items_list):
            if item.base_code == "ore":
                unique_items_list.remove(item)

        item_groups = []
        #others = Item_Group("Other")
        for other_type in self.get_other_types(unique_items_list):
            others = Item_Group(self.get_item_type_name_from_code(other_type))
            for item in list(unique_items_list):
                if item.base_code == other_type:
                    others.items.append(item)
                    others.items.sort(key = lambda x: (int(x.item_level), int(x.required_level)))
            item_groups.append(others)
            unique_armor_rendered = unique_armor_template.render(item_groups=item_groups, page="misc")
            base_template = Template(filename="templates/base.htm", lookup=self.mylookup)
            base_rendered = base_template.render(body=unique_armor_rendered,
                                                 name=self.db_name,
                                                 version=self.db_version).replace("\r","")
        
        open("../" + self.db_code + "/" + "unique_others.htm", "w").write(base_rendered)

        return

        item_groups = []
        quick_links = ["Rings", "Amulets", "Charms", "Jewels", "Helms", "Circlets", "Armor", "Robes",
                       "Shields", "Gloves", "Boots", "Belts", "Bar", "Dru", "Nec", "Pal"]
        unique_armor_template = Template(filename="templates/uniques.htm",
                                         lookup=self.mylookup)
        ring_groups =   [
                            ["Generic Rings", "rin"],
                            ["Amazonian Loops", "zrn"],
                            ["Assassin's Spirals", "arn"],
                            ["Barbaric Hoops", "brg"],
                            ["Druid's Seals", "drn"],
                            ["Necromancer's Stones", "nrn"],
                            ["Paladic Halos", "prn"],
                            ["Sorcerer's Bands", "srn"],
                        ]
        for ring_group in ring_groups:
            rings = Item_Group("Rings")
            for item in list(unique_items_list):
                if item.base_name == "Ring" and item.base_code == ring_group[1]:
                    rings.items.append(item)
                    unique_items_list.remove(item)
            rings.items.sort(key = lambda x: (int(x.item_level), int(x.required_level)))
            item_groups.append(rings)

        amulet_groups = [
                            ["Generic Amulets", "amu"],
                            ["Amazonian Amulets", "zam"],
                            ["Assassin Amulets", "aam"],
                            ["Barbarian Amulets", "bam"],
                            ["Druid Amulets", "dam"],
                            ["Necromancer Amulets", "nam"],
                            ["Paladin Amulets", "pam"],
                            ["Sorceress Amulets", "sam"],
                        ]
        for amulet_group in amulet_groups:
            amulets = Item_Group("Amulets")
            for item in list(unique_items_list):
                if item.base_name == "Amulet" and item.base_code == amulet_group[1]:
                    amulets.items.append(item)
                    unique_items_list.remove(item)
            amulets.items.sort(key = lambda x: (int(x.item_level), int(x.required_level)))
            item_groups.append(amulets)

        charm_groups =  [
                            ["Small Charms", ["cm1"]],
                            ["Large Charms", ["cm2"]],
                            ["Grand Charms", ["cm3", "cmy", "cmx"]],
                        ]
        for charm_group in charm_groups:
            charms = Item_Group("Charms")
            for item in list(unique_items_list):
                if item.base_code in charm_group[1]:
                    charms.items.append(item)
                    unique_items_list.remove(item)
            charms.items.sort(key = lambda x: (int(x.item_level), int(x.required_level)))
            item_groups.append(charms)
        
        others = Item_Group("Other")
        for item in list(unique_items_list):
            others.items.append(item)
            others.items.sort(key = lambda x: (int(x.item_level), int(x.required_level)))
        item_groups.append(others)

        unique_armor_rendered = unique_armor_template.render(quick_links=quick_links,
                                                             item_groups=item_groups)
        
        base_template = Template(filename="templates/base.htm", lookup=self.mylookup)
        base_rendered = base_template.render(body=unique_armor_rendered,
                                             name=self.db_name,
                                             version=self.db_version).replace("\r","")
        
        open("../" + self.db_code + "/" + "unique_armors.htm", "w").write(base_rendered)

    def generate_prefixes(self):
        prefixes = Affix_Utils(self.tables, self.mod_strings).get_prefixes()
        armor_template = Template(filename="templates/affixes.htm", lookup=self.mylookup)
        armor_rendered = armor_template.render(prefixes)
        self.generate(armor_rendered, "prefixes.htm")

    def generate_suffixes(self):
        suffixes = Affix_Utils(self.tables, self.mod_strings).get_suffixes()
        armor_template = Template(filename="templates/affixes.htm", lookup=self.mylookup)
        armor_rendered = armor_template.render(suffixes)
        self.generate(armor_rendered, "suffixes.htm")


    def generate_runewords(self):
        runewords = []
        for rw in self.tables.runeword_table:
            allowed_bases = []
            excluded_bases = []
            runes = []
            properties = []
            for i in range(6):
                if rw["itype" + str(i+1)] != "":
                    allowed_bases.append(self.get_item_type_name_from_code(rw["itype" + str(i+1)]))
            for i in range(3):
                if rw["etype" + str(i+1)] != "":
                    excluded_bases.append(self.get_item_type_name_from_code(rw["etype" + str(i+1)]))
            for i in range(6):
                if rw["Rune" + str(i+1)] != "":
                    runes.append(self.utils.get_item_name_from_code(rw["Rune" + str(i+1)]))
            for j in range(6):
                # If the property doesn't have a name, then there isn't a property
                if rw["T1Code" + str(j+1)] != "":
                    properties.append(Property(rw["T1Code" + str(j+1)], rw["T1Param" + str(j+1)], rw["T1Min" + str(j+1)], rw["T1Max" + str(j+1)]))

            for p in properties:
                self.utils.fill_property_stats(p)
            self.utils.fill_group_stats(properties)
            runewords.append(Runeword(self.mod_strings.get(rw["Name"], rw["Rune Name"]), runes, allowed_bases, excluded_bases, properties))  
        filename ="runewords.htm"
        template = Template(filename="templates/" + filename, lookup=self.mylookup)
        rendered = template.render(runewords, self.gemapplytype_names)
        self.generate(rendered, filename)
    
    def gen_all(self):
        self.generate_runewords()
        self.generate_armor()
        self.generate_weapons()
        self.generate_uniques()
        self.generate_static()
        self.generate_prefixes()
        self.generate_suffixes()
        #self.generate_socketables()
        #self.generate_sets()
        #self.generate_recipes()

def generate_static_links(db):
    prelinks = ""
    postlinks = ""
    extra_static = []
    for extra_links in db["extra_pages"]:
        if extra_links["position"] < 0:
            prelinks = prelinks + "<a href=\"./" + extra_links["file"] + "\">[" + extra_links["name"] + "]</a>\n"
            extra_static.append(extra_links["file"])
        if extra_links["position"] > 0:
            postlinks = postlinks + "<a href=\"./" + extra_links["file"] + "\">[" + extra_links["name"] + "]</a>\n"
            extra_static.append(extra_links["file"])
    prelink_file = open("templates/prelinks.htm", "w")
    prelink_file.write(prelinks)
    prelink_file.close()
    postlink_file = open("templates/postlinks.htm", "w")
    postlink_file.write(postlinks)
    postlink_file.close()
    return extra_static

for db in config.databases:
    if len(sys.argv) == 1 or sys.argv[1] == db["shortname"]:
        print("----GENERATING " + db["name"] + "-----")
        extra_static = generate_static_links(db)
        db_gen = Database_Generator(db["shortname"], 
                                    db["name"],
                                    db["version"],
                                    db["tablestring_files"],
                                    db["include_staff_and_automods_on_uniques"],
                                    db["gemapplytype_names"])
        db_gen.gen_all()
        db_gen.generate_static(extra_static)
        print("----DONE-----")
