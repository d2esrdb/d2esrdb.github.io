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


class Item_Group:
    def __init__(self, name):
        self.name = name
        self.items = []

class Database_Generator:
    def __init__(self, db_code, db_name, db_version, string_tables):
        self.db_code = db_code
        self.db_name = db_name
        self.db_version = db_version
        self.string_tables = string_tables
        self.mod_strings = table_strings.get_string_dict(db_code, string_tables)
        self.mylookup = TemplateLookup(directories=[os.getcwd()])
        self.tables = Tables(db_code)
        self.utils = Utils(self.tables, self.mod_strings)

    def generate(self, body_template, filename):
        base_template = Template(filename="templates/base.htm", lookup=self.mylookup)
        base_rendered = base_template.render(body=body_template,
                                             name=self.db_name,
                                             version=self.db_version).replace("\r","")
        open("../" + self.db_code + "/" + filename, "w").write(base_rendered)

    def generate_static(self, extra=[]):
        filenames = ["gems.htm", "maps.htm", "runewords.htm", "sets.htm", "recipes.htm", "gemwords.htm"]
        filenames = filenames + extra
        for filename in filenames:
            template = Template(filename="templates/" + filename, lookup=self.mylookup)
            rendered = template.render()
            self.generate(rendered, filename)

    def generate_armor(self):
        normal_armors = []
        exceptional_armors = []
        elite_armors = []
        for i, armor_row in enumerate(self.tables.armor_table):
            if armor_row[4] != "0":
                for item_type_row in self.tables.item_types_table:
                    if armor_row[48] == item_type_row[1] and armor_row[48] != "":
                        item = Item(armor_row[18], 1, armor_row[14], [], armor_row[17], self.mod_strings, self.tables)
                        automods = []
                        for p in item.properties:
                            if p.is_automod:
                                for s in p.stats:
                                    automods.append(s.stat_string)

                        armor = [self.mod_strings.get(armor_row[18], armor_row[0]), #0: name
                                 item_type_row[0],  #1: category
                                 armor_row[14],     #2: req_level
                                 armor_row[17],     #3: code
                                 armor_row[23],     #4: norm_code
                                 armor_row[24],     #5: exceptional_code
                                 armor_row[25],     #6: elite code                           
                                 armor_row[5],      #7: min defense
                                 armor_row[6],      #8: max defense
                                 armor_row[11],     #9: durability
                                 armor_row[8],      #10: frw
                                 armor_row[13],     #11: qlvl
                                 armor_row[19],     #12: mag lvl
                                 armor_row[9],      #13: req str
                                 armor_row[10],     #14: block
                                 armor_row[63],     #15: min damage
                                 armor_row[64],     #16: max damage
                                 armor_row[31],     #17: sock
                                 armor_row[32],     #18: gem_type
                                 self.utils.string_array_to_html(automods, 2),          #19: automods
                                 item.staffmod,     #20: staffmods
                                ]
                        if armor_row[23] == armor_row[17]:
                            normal_armors.append(armor)
                        if armor_row[24] == armor_row[17]:
                            exceptional_armors.append(armor)
                        if armor_row[25] == armor_row[17]:
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

    def generate_weapons(self):
        quick_links = ["Axes", "Bows", "Xbows", "Daggers", "Javelins", "Knuckles", "Maces", "Poles",
                       "Scepters", "Spears", "Staves", "Swords", "Throw", "Wands", "Ama", "Asn", "Bar",
                       "Dru", "Nec", "Pal", "Sor"]
        weapon_template = Template(filename="templates/weapons.htm", lookup=self.mylookup)
        weapon_rendered = weapon_template.render(quick_links=quick_links)
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
            if weapon[1] not in weapon_types:
                weapon_types.append(weapon[1])
        return weapon_types

    def get_item_name_from_code(self, code):
        for row in self.tables.item_types_table:
            if row[1] == code:
                return row[0]

        for row in self.tables.misc_table:
            if row[13] == code:
                return row[0]
        return "Unknown: " + code

    def get_armor_types(self):
        armor_types = []
        for armor in self.tables.armor_table:
            if armor[48] not in armor_types:
                armor_types.append(armor[48])
        return armor_types

    def weapon_is_a_subtype_of(self, subtype_code, maintype_code):
        for weapon in self.tables.weapons_table:
            if weapon[3] == subtype_code and maintype_code == weapon[1]:
                return True
        return False

    def armor_is_of_type(self, item_code, armor_code):
        for row in self.tables.armor_table:
            if row[17] == item_code and armor_code == row[48]:
                return True
        return False

    def set_weapon_bg_color(self, item):
        for weapon in self.tables.weapons_table:
            if item.base_code == weapon[36]:
                item.bg_color_code = 303030
                return
            if item.base_code == weapon[35]:
                item.bg_color_code = 202020
                return

    def set_armor_bg_color(self, item):
        for armor in self.tables.armor_table:
            if item.base_code == armor[25]:
                item.bg_color_code = 303030
                return
            if item.base_code == armor[24]:
                item.bg_color_code = 202020
                return

    def generate_uniques(self):
        unique_items_list = unique_items.get_unique_items(self.tables, self.mod_strings)
        item_groups = []
        unique_weapon_template = Template(filename="templates/uniques.htm",
                                          lookup=self.mylookup)
        for weapon_type in self.get_weapon_types():
            weapon_group = Item_Group(self.get_item_name_from_code(weapon_type))
            for item in list(unique_items_list):
                if self.weapon_is_a_subtype_of(item.base_code, weapon_type):
                    self.set_weapon_bg_color(item)
                    weapon_group.items.append(item)
                    unique_items_list.remove(item)
            if len(weapon_group.items) > 0:
                item_groups.append(weapon_group)
        unique_weapon_rendered = unique_weapon_template.render(item_groups=item_groups)
        base_template = Template(filename="templates/base.htm", lookup=self.mylookup)
        base_rendered = base_template.render(body=unique_weapon_rendered,
                                             name=self.db_name,
                                             version=self.db_version).replace("\r","")    
        open("../" + self.db_code + "/" + "unique_weapons.htm", "w").write(base_rendered)

        item_groups = []
        unique_armor_template = Template(filename="templates/uniques.htm",
                                         lookup=self.mylookup)
        for armor_type in self.get_armor_types():
            armor_group = Item_Group(self.get_item_name_from_code(armor_type))
            for item in list(unique_items_list):
                #print("base code: " + item.base_code + " armor_type: " + armor_type)
                if self.armor_is_of_type(item.base_code, armor_type):
                    self.set_armor_bg_color(item)
                    armor_group.items.append(item)
                    unique_items_list.remove(item)
            if len(armor_group.items) > 0:
                item_groups.append(armor_group)
        unique_armor_rendered = unique_armor_template.render(item_groups=item_groups)
        
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
            others = Item_Group(self.get_item_name_from_code(other_type))
            for item in list(unique_items_list):
                if item.base_code == other_type:
                    others.items.append(item)
                    others.items.sort(key = lambda x: (int(x.item_level), int(x.required_level)))
            item_groups.append(others)
            unique_armor_rendered = unique_armor_template.render(item_groups=item_groups)
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
    
    def gen_all(self):
        self.generate_armor()
        self.generate_weapons()
        self.generate_uniques()
        self.generate_static()
        self.generate_prefixes()
        self.generate_suffixes()

def generate_static_links(db):
    prelinks = ""
    postlinks = ""
    extra_static = []
    for extra_links in db[4]:
        if extra_links[2] < 0:
            prelinks = prelinks + "<a href=\"./" + extra_links[1] + "\">[" + extra_links[0] + "]</a>\n"
            extra_static.append(extra_links[1])
        if extra_links[2] > 0:
            postlinks = postlinks + "<a href=\"./" + extra_links[1] + "\">[" + extra_links[0] + "]</a>\n"
            extra_static.append(extra_links[1])
    prelink_file = open("templates/prelinks.htm", "w")
    prelink_file.write(prelinks)
    prelink_file.close()
    postlink_file = open("templates/postlinks.htm", "w")
    postlink_file.write(postlinks)
    postlink_file.close()
    return extra_static

for db in config.databases:
    if len(sys.argv) == 1 or sys.argv[1] == db[0]:
        print("----GENERATING " + db[1] + "-----")
        extra_static = generate_static_links(db)
        db_gen = Database_Generator(db[0], db[1], db[2], db[3])
        db_gen.gen_all()
        db_gen.generate_static(extra_static)
        print("----DONE-----")
