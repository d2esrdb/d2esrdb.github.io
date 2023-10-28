import os
import unique_items
import load_txts
import affixes
import table_strings
from utils import *
from mako.template import Template
from mako.lookup import TemplateLookup

mylookup = TemplateLookup(directories=[os.getcwd()])
mod_strings = table_strings.get_string_dict()

class Item_Group:
    def __init__(self, name):
        self.name = name
        self.items = []

def get_version():
    return "5.3A5"

def generate(body_template, filename):
    base_template = Template(filename="templates/base.htm", lookup=mylookup)
    base_rendered = base_template.render(body=body_template,
                                         version=get_version()).replace("\r","")
    open("../" + filename, "w").write(base_rendered)

def generate_simple():
    filenames = ["es3gem_n.htm", "es3map_n.htm", "es3runew_n.htm", "es3set_n.htm", "es3cube_n.htm", "es3gemw_n.htm", "index.htm"]
    for filename in filenames:
        template = Template(filename="templates/" + filename, lookup=mylookup)
        rendered = template.render()
        generate(rendered, filename)

def generate_armor():
    normal_armors = []
    exceptional_armors = []
    elite_armors = []
    for i, armor_row in enumerate(load_txts.armor_table):
        if armor_row[4] != "0":
            for item_type_row in load_txts.item_types_table:
                if armor_row[48] == item_type_row[1] and armor_row[48] != "":
                    item = Item(armor_row[18], 1, armor_row[14], [], armor_row[17])
                    automods = []
                    for p in item.properties:
                        if p.is_automod:
                            for s in p.stats:
                                automods.append(s.stat_string)

                    armor = [mod_strings.get(armor_row[18], armor_row[0]), #0: name
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
                             string_array_to_html(automods, 2),          #19: automods
                             item.staffmod,     #20: staffmods
                            ]
                    if armor_row[23] == armor_row[17]:
                        normal_armors.append(armor)
                    if armor_row[24] == armor_row[17]:
                        exceptional_armors.append(armor)
                    if armor_row[25] == armor_row[17]:
                        elite_armors.append(armor)

    # First sort normal armors by level req
    normal_armors.sort(key = lambda x: (int(x[2])))

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

    armor_template = Template(filename="templates/es3armo_n.htm", lookup=mylookup)
    armor_rendered = armor_template.render(armors)
    generate(armor_rendered, "es3armo_n.htm")

def generate_weapons():
    quick_links = ["Axes", "Bows", "Xbows", "Daggers", "Javelins", "Knuckles", "Maces", "Poles",
                   "Scepters", "Spears", "Staves", "Swords", "Throw", "Wands", "Ama", "Asn", "Bar",
                   "Dru", "Nec", "Pal", "Sor"]
    weapon_template = Template(filename="templates/es3weap_n.htm", lookup=mylookup)
    weapon_rendered = weapon_template.render(quick_links=quick_links)
    generate(weapon_rendered, "es3weap_n.htm")

def get_other_types(remaining_items):
    other_types = []
    for item in remaining_items:
        if item.base_code not in other_types:
            other_types.append(item.base_code)
    return other_types

def get_weapon_types():
    weapon_types = []
    for weapon in load_txts.weapons_table:
        if weapon[1] not in weapon_types:
            weapon_types.append(weapon[1])
    return weapon_types

def get_item_name_from_code(code):
    for row in load_txts.item_types_table:
        if row[1] == code:
            return row[0]

    for row in load_txts.misc_table:
        if row[13] == code:
            return row[0]
    return "Unknown: " + code

def get_armor_types():
    armor_types = []
    for armor in load_txts.armor_table:
        if armor[48] not in armor_types:
            armor_types.append(armor[48])
    return armor_types

def weapon_is_a_subtype_of(subtype_code, maintype_code):
    for weapon in load_txts.weapons_table:
        if weapon[3] == subtype_code and maintype_code == weapon[1]:
            return True
    return False

def armor_is_of_type(item_code, armor_code):
    for row in load_txts.armor_table:
        if row[17] == item_code and armor_code == row[48]:
            return True
    return False

def set_weapon_bg_color(item):
    for weapon in load_txts.weapons_table:
        if item.base_code == weapon[36]:
            item.bg_color_code = 303030
            return
        if item.base_code == weapon[35]:
            item.bg_color_code = 202020
            return

def set_armor_bg_color(item):
    for armor in load_txts.armor_table:
        if item.base_code == armor[25]:
            item.bg_color_code = 303030
            return
        if item.base_code == armor[24]:
            item.bg_color_code = 202020
            return

def generate_uniques():
    unique_items_list = unique_items.get_unique_items()
    item_groups = []
    unique_weapon_template = Template(filename="templates/es3uarmo_n.htm",
                                      lookup=mylookup)
    for weapon_type in get_weapon_types():
        weapon_group = Item_Group(get_item_name_from_code(weapon_type))
        for item in list(unique_items_list):
            if weapon_is_a_subtype_of(item.base_code, weapon_type):
                set_weapon_bg_color(item)
                weapon_group.items.append(item)
                unique_items_list.remove(item)
        if len(weapon_group.items) > 0:
            item_groups.append(weapon_group)
    unique_weapon_rendered = unique_weapon_template.render(item_groups=item_groups)
    base_template = Template(filename="templates/base.htm", lookup=mylookup)
    base_rendered = base_template.render(body=unique_weapon_rendered,
                                         version=get_version()).replace("\r","")    
    open("../es3uweap_n.htm", "w").write(base_rendered)

    item_groups = []
    unique_armor_template = Template(filename="templates/es3uarmo_n.htm",
                                     lookup=mylookup)
    for armor_type in get_armor_types():
        armor_group = Item_Group(get_item_name_from_code(armor_type))
        for item in list(unique_items_list):
            #print("base code: " + item.base_code + " armor_type: " + armor_type)
            if armor_is_of_type(item.base_code, armor_type):
                set_armor_bg_color(item)
                armor_group.items.append(item)
                unique_items_list.remove(item)
        if len(armor_group.items) > 0:
            item_groups.append(armor_group)
    unique_armor_rendered = unique_armor_template.render(item_groups=item_groups)
    
    base_template = Template(filename="templates/base.htm", lookup=mylookup)
    base_rendered = base_template.render(body=unique_armor_rendered,
                                         version=get_version()).replace("\r","")
    open("../es3uarmo_n.htm", "w").write(base_rendered)

    # Remove ores
    for item in list(unique_items_list):
        if item.base_code == "ore":
            unique_items_list.remove(item)

    item_groups = []
    #others = Item_Group("Other")
    for other_type in get_other_types(unique_items_list):
        others = Item_Group(get_item_name_from_code(other_type))
        for item in list(unique_items_list):
            if item.base_code == other_type:
                others.items.append(item)
                others.items.sort(key = lambda x: (int(x.item_level), int(x.required_level)))
        item_groups.append(others)
        unique_armor_rendered = unique_armor_template.render(item_groups=item_groups)
        base_template = Template(filename="templates/base.htm", lookup=mylookup)
        base_rendered = base_template.render(body=unique_armor_rendered,
                                             version=get_version()).replace("\r","")
    
    open("../es3uother_n.htm", "w").write(base_rendered)

    return

    item_groups = []
    quick_links = ["Rings", "Amulets", "Charms", "Jewels", "Helms", "Circlets", "Armor", "Robes",
                   "Shields", "Gloves", "Boots", "Belts", "Bar", "Dru", "Nec", "Pal"]
    unique_armor_template = Template(filename="templates/es3uarmo_n.htm",
                                     lookup=mylookup)
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
    
    base_template = Template(filename="templates/base.htm", lookup=mylookup)
    base_rendered = base_template.render(body=unique_armor_rendered,
                                         version=get_version()).replace("\r","")
    
    open("../es3uarmo_n.htm", "w").write(base_rendered)

def generate_prefixes():
    prefixes = affixes.get_prefixes()
    armor_template = Template(filename="templates/es3affix_n.htm", lookup=mylookup)
    armor_rendered = armor_template.render(prefixes)
    generate(armor_rendered, "es3pref_n.htm")

def generate_suffixes():
    suffixes = affixes.get_suffixes()
    armor_template = Template(filename="templates/es3affix_n.htm", lookup=mylookup)
    armor_rendered = armor_template.render(suffixes)
    generate(armor_rendered, "es3suff_n.htm")

generate_armor()
generate_weapons()
generate_uniques()
generate_simple()
generate_prefixes()
generate_suffixes()
