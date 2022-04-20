import os
import unique_items
from mako.template import Template
from mako.lookup import TemplateLookup

mylookup = TemplateLookup(directories=[os.getcwd()])

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

def generate_uniques():
    quick_links = ["Rings", "Amulets", "Charms", "Jewels", "Helms", "Circlets", "Armor", "Robes",
                   "Shields", "Gloves", "Boots", "Belts", "Bar", "Dru", "Nec", "Pal"]
    unique_armor_template = Template(filename="templates/es3uarmo_n.htm",
                                     lookup=mylookup)
    item_groups = []
    generic_rings = unique_items.Item_Group("Generic Rings", "Ring")
    for item in unique_items.get_unique_items():
        if item.base_type == "Ring" and item.subbase_type == "rin":
            generic_rings.items.append(item)
    generic_rings.items.sort(key = lambda x: int(x.item_level))

    assassin_rings = unique_items.Item_Group("Assassin's Spirals", "Ring")
    for item in unique_items.get_unique_items():
        if item.base_type == "Ring" and item.subbase_type == "arn":
            assassin_rings.items.append(item)
    assassin_rings.items.sort(key = lambda x: int(x.item_level))

    item_groups.append(generic_rings)
    item_groups.append(assassin_rings)

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