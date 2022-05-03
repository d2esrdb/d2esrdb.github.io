import os
import unique_items
import load_txts
from mako.template import Template
from mako.lookup import TemplateLookup

mylookup = TemplateLookup(directories=[os.getcwd()])

class Item_Group:
    def __init__(self, name):
        self.name = name
        self.items = []

def get_version():
    for directory_name in os.listdir("../"):
        if directory_name.startswith("ESR"):
            return directory_name.replace("ESR", "").replace("_", "").strip()

def generate(body_template, filename):
    base_template = Template(filename="templates/base.htm", lookup=mylookup)
    base_rendered = base_template.render(body=body_template,
                                         version=get_version()).replace("\r","")
    open("../" + filename, "w").write(base_rendered)

def generate_index():
    index_template = Template(filename="templates/index.htm", lookup=mylookup)
    index_rendered = index_template.render()
    generate(index_rendered, "index.htm")

def generate_armor():
    quick_links = ["Helms", "Circlets", "Armor", "Robes", "Shields", "Gloves", "Belts", "Boots",
                   "Bar", "Dru", "Nec", "Pal"]
    armor_template = Template(filename="templates/es3armo_n.htm", lookup=mylookup)
    armor_rendered = armor_template.render(quick_links)
    generate(armor_rendered, "es3armo_n.htm")

def generate_weapons():
    quick_links = ["Axes", "Bows", "Xbows", "Daggers", "Javelins", "Knuckles", "Maces", "Poles",
                   "Scepters", "Spears", "Staves", "Swords", "Throw", "Wands", "Ama", "Asn", "Bar",
                   "Dru", "Nec", "Pal", "Sor"]
    weapon_template = Template(filename="templates/es3weap_n.htm", lookup=mylookup)
    weapon_rendered = weapon_template.render(quick_links=quick_links)
    generate(weapon_rendered, "es3weap_n.htm")

def get_weapon_types():
    weapon_types = []
    for i, weapon in enumerate(load_txts.weapons_table):
        if weapon[1] not in weapon_types and i != 0:
            weapon_types.append(weapon[1])
    return weapon_types

def get_item_name_from_code(code):
    for row in load_txts.item_types:
        if row[1] == code:
            return row[0]
    return "Unknown: " + code

def get_armor_types():
    armor_types = []
    for i, armor in enumerate(load_txts.armor_table):
        if armor[48] not in armor_types and i != 0:
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
                #set_armor_bg_color(item)
                armor_group.items.append(item)
                unique_items_list.remove(item)
        if len(armor_group.items) > 0:
            item_groups.append(armor_group)
    unique_armor_rendered = unique_armor_template.render(item_groups=item_groups)
    
    base_template = Template(filename="templates/base.htm", lookup=mylookup)
    base_rendered = base_template.render(body=unique_armor_rendered,
                                         version=get_version()).replace("\r","")
    open("../es3uarmo_n.htm", "w").write(base_rendered)

    item_groups = []
    others = Item_Group("Other")
    for item in list(unique_items_list):
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

generate_index()
generate_armor()
generate_weapons()
generate_uniques() #armors and weapons
#generate_sets()
#generate_gems_and_runes()
#generate_runewords()
#generate_gemwords()
#generate_recipes()
#generate_maps()