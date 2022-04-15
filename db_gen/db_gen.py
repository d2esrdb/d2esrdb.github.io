import os
from mako.template import Template
from mako.lookup import TemplateLookup

mylookup = TemplateLookup(directories=[os.getcwd()])

def generate_index():
    index_template = Template(filename="templates/base.htm", lookup=mylookup)
    index_rendered = index_template.render(body="index.htm", quick_links=[])
    open("../index.htm", "w").write(index_rendered)

def generate_armor():
    armor_template = Template(filename="templates/base.htm", lookup=mylookup)
    armor_rendered = armor_template.render(body="es3armo_n.htm", quick_links=["Helms", "Circlets",
        "Armor", "Robes", "Shields", "Gloves", "Belts", "Boots", "Bar", "Dru", "Nec", "Pal"])
    open("../es3armo_n.htm", "w").write(armor_rendered)

generate_index()
generate_armor()