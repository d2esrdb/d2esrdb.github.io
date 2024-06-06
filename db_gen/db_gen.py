import sys
import os
import config
from mako.template import Template
from mako.lookup import TemplateLookup

import table_strings 
import tables
import utils
import armor_generator
import weapon_generator
import affixes_generator 
import runeword_generator
import uniques_generator
import socketables_generator
import set_generator

class Database_Generator:
    def __init__(self, db_code, db_name, db_version, string_tables, gemapplytype_names):
        self.db_code = db_code
        self.db_name = db_name
        self.db_version = db_version
        self.table_strings = table_strings.get_string_dict(db_code, string_tables)
        self.mylookup = TemplateLookup(directories=[os.getcwd()])
        self.tables = tables.Tables(db_code)
        self.utils = utils.Utils(self.tables, self.table_strings)
        self.gemapplytype_names = gemapplytype_names

    def generate(self, body_template, filename):
        base_template = Template(filename="templates/base.htm", lookup=self.mylookup)
        base_rendered = base_template.render(body=body_template,
                                             name=self.db_name,
                                             version=self.db_version).replace("\r","")
        open("../" + self.db_code + "/" + filename, "w").write(base_rendered)

    def generate_static(self, extra=[]):
        filenames = ["recipes.htm",]
        filenames = filenames + extra
        for filename in filenames:
            #@TODO delete once we autogen recipes
            if filename in ["recipes.htm"]:
                template = Template(filename="templates/" + filename, lookup=self.mylookup)
            else:
                template = Template(filename="templates/" + self.db_code + "/" + filename, lookup=self.mylookup)
            rendered = template.render()
            self.generate(rendered, filename)

    def generate_armor(self):
        armors = armor_generator.Armor_Generator(self.tables, self.table_strings, self.utils).generate_armor()
        armor_template = Template(filename="templates/armors.htm", lookup=self.mylookup)
        armor_rendered = armor_template.render(armors)
        self.generate(armor_rendered, "armors.htm")
        
    def generate_weapons(self):
        weapons = weapon_generator.Weapon_Generator(self.tables, self.table_strings, self.utils).generate_weapons() 
        weapon_template = Template(filename="templates/weapons.htm", lookup=self.mylookup)
        weapon_rendered = weapon_template.render(weapons)
        self.generate(weapon_rendered, "weapons.htm")

    def generate_uniques(self):
        uniques_gen = uniques_generator.Uniques_Generator(self.tables, self.table_strings, self.utils)
        uniques_template = Template(filename="templates/uniques.htm", lookup=self.mylookup)

        unique_weapons = uniques_gen.get_unique_weapons()
        unique_weapon_rendered = uniques_template.render(item_groups=unique_weapons, page="weapons")
        self.generate(unique_weapon_rendered, "unique_weapons.htm")

        unique_armors = uniques_gen.get_unique_armors()
        unique_armor_rendered = uniques_template.render(item_groups=unique_armors, page="armors")
        self.generate(unique_armor_rendered, "unique_armors.htm")

        unique_misc = uniques_gen.get_unique_misc()
        unique_misc_rendered = uniques_template.render(item_groups=unique_misc, page="misc")
        self.generate(unique_misc_rendered,  "unique_others.htm")

    def generate_prefixes(self):
        prefixes = affixes_generator.Affix_Generator(self.tables, self.table_strings, self.utils).get_prefixes()
        all_types = []
        for prefix in prefixes:
            all_types = all_types + prefix.item_types + prefix.exclude_types
        affix_template = Template(filename="templates/affixes.htm", lookup=self.mylookup)
        affix_rendered = affix_template.render(prefixes, self.utils.get_item_types_list(list(set(all_types))))
        self.generate(affix_rendered, "prefixes.htm")

    def generate_suffixes(self):
        suffixes = affixes_generator.Affix_Generator(self.tables, self.table_strings, self.utils).get_suffixes()
        all_types = []
        for suffix in suffixes:
            all_types = all_types + suffix.item_types + suffix.exclude_types
        affix_template = Template(filename="templates/affixes.htm", lookup=self.mylookup)
        affix_rendered = affix_template.render(suffixes, self.utils.get_item_types_list(list(set(all_types))))
        self.generate(affix_rendered, "suffixes.htm")

    def generate_runewords(self):
        runewords = runeword_generator.Runeword_Generator(self.tables, self.table_strings, self.utils).generate_runewords()
        filename = "runewords.htm"
        template = Template(filename="templates/" + filename, lookup=self.mylookup)
        rendered = template.render(runewords, self.gemapplytype_names)
        self.generate(rendered, filename)
    
    def generate_socketables(self):
        socketables = socketables_generator.Socketables_Generator(self.tables, self.table_strings, self.utils).generate_socketables()
        filename = "gems.htm"
        template = Template(filename="templates/" + filename, lookup=self.mylookup)
        rendered = template.render(socketables, self.gemapplytype_names)
        self.generate(rendered, filename)
    
    def generate_sets(self):
        sets = set_generator.Set_Generator(self.tables, self.table_strings, self.utils).generate_sets()
        filename = "sets.htm"
        template = Template(filename="templates/" + filename, lookup=self.mylookup)
        rendered = template.render(sets)
        self.generate(rendered, filename)

    def gen_all(self):
        self.generate_sets()
        self.generate_weapons()
        self.generate_runewords()
        self.generate_uniques()
        self.generate_armor()
        self.generate_prefixes()
        self.generate_suffixes()
        self.generate_socketables()
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
                                    db["gemapplytype_names"])
        db_gen.gen_all()
        db_gen.generate_static(extra_static)
        print("----DONE-----")
        if False:
            for log in db_gen.utils.log_errors:
                print(log)
