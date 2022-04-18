import os
import csv
import table_strings
import stat_formats

mod_strings = table_strings.get_string_dict()
no_mod_strings = {}

class Stat:
    def __init__(self, name, stat_string, priority):
        self.name = name
        self.stat_string = stat_string
        self.priority = priority

class Property:
    def __init__(self, name, param, min, max):
        self.name = name
        self.param = param
        self.min = min
        self.max = max
        self.stats = []

class Unique_Item:
    def __init__(self, name, item_level, required_level, properties):
        self.name = name
        self.item_level = item_level
        self.required_level = required_level
        self.properties = properties

data_path = ""
for root, dirs, files in os.walk("../"):
    if "Data" in dirs:
        data_path = os.path.join(root, "Data")

# Get the list of armors
#def get_armor_bases():
#    armor_list = []
#    armors = open('../Data/global/excel/armor.txt', newline='')
#    items = csv.reader(armors, delimiter='\t')
#    for i, row in enumerate(items):
#        armor_list.append(row[0])
#    return armor_list

def print_item(item):
    print(item.name)
    print("    Item Level: " + item.item_level)
    print("    Required Level: " + item.required_level)
    for property in item.properties:
        #print("    Property: " + property.name)
        #print("        param: " + property.param)
        #print("        min: " + property.min)
        #print("        max: " + property.max)
        for stat in property.stats:
            if stat is not None and stat.stat_string is not None:
                print("    " + stat.stat_string)
            #if (property.param != ""):
            #    print("    " + property.param + " " + stat.name)
            #elif property.min == property.max:
            #    print("    " + property.min + " " + stat.name)
            #else:
            #    print("    " + property.min + "-" + str(property.max) + " " + stat.name)

def get_value_string(param, min, max):
    if param != "":
        return param
    
    if min == "" and max == "":
        return "NOVALUE"

    if min == "":
        return max

    if max == "":
        return min

    if min == max:
        return min
        
    return min + "-" + max

def get_class_from_skill_name(skill_name):
    skill_table = open(data_path + "/global/excel/Skills.txt", newline='')
    skill_rows = csv.reader(skill_table, delimiter='\t')
    
    for skill_row in skill_rows:
        if skill_name == skill_row[0]:
            if skill_row[2] == "ama":
                return "Amazon"
            if skill_row[2] == "sor":
                return "Sorceress"
            if skill_row[2] == "nec":
                return "Necromancer"
            if skill_row[2] == "pal":
                return "Paladin"
            if skill_row[2] == "bar":
                return "Barbarian"
            if skill_row[2] == "dru":
                return "Druid"
            if skill_row[2] == "ass":
                return "Assassin"
            return "Unknown"

def get_class_from_skill_range(start, end):
    start = int(start)
    end = int(end)
    if start >= 6 and end <= 35:
        return "Amazon"
    if start >= 36 and end <= 65:
        return "Sorceress"
    if start >= 66 and end <= 95:
        return "Necromancer"
    if start >= 96 and end <= 125:
        return "Paladin"
    if start >= 126 and end <= 155:
        return "Barbarian"
    if start >= 221 and end <= 250:
        return "Druid"
    if start >= 251 and end <= 280:
        return "Assassin"
    return "Unknown"

def get_skill_name(skill):
    skill_table = open(data_path + "/global/excel/Skills.txt", newline='')
    skill_rows = csv.reader(skill_table, delimiter='\t')
    skill_desc = ""
    for skill_row in skill_rows:
        if skill.isdigit():
            if str(skill) == str(skill_row[1]):
                skill_desc = skill_row[3] 
        if str(skill).lower() == str(skill_row[0]).lower():
            skill_desc = skill_row[3]

    if skill_desc == "":
        print("Did not find skill desc for skill: " + skill)
        return skill

    skill_desc_table = open(data_path + "/global/excel/SkillDesc.txt", newline='')
    skill_desc_rows = csv.reader(skill_desc_table, delimiter='\t')
    
    for skill_desc_row in skill_desc_rows:
        if skill_desc == skill_desc_row[0]:
            skill_name = mod_strings.get(skill_desc_row[7], "")
            if skill_name != "":
                return skill_name

    print("Did not find skill name for skill: " + skill)
    return skill

def get_stat(stat_name, param, min, max):
    item_stat_cost_table = open(data_path + "/global/excel/ItemStatCost.txt", newline='')
    item_stat_cost_rows = csv.reader(item_stat_cost_table, delimiter='\t')
    
    for item_stat_cost_row in item_stat_cost_rows:
        if stat_name == item_stat_cost_row[0]:
            
            # Custom handling
            if stat_name == "item_numsockets":
                return Stat(stat_name, "Socketed (" + get_value_string(param, min, max) + ")", int(item_stat_cost_row[39]))
            if stat_name == "item_singleskill":
                if min == max:
                    return Stat(stat_name, "+" + get_value_string("", min, max) + " to " + get_skill_name(param) + " (" + get_class_from_skill_name(param) + " Only)", int(item_stat_cost_row[39]))
                return Stat(stat_name, "+" + str(param) + " to Random " + get_class_from_skill_range(min, max) + " Skill", int(item_stat_cost_row[39]))
            if stat_name == "item_addskill_tab":
                # @TODO what's going on with skilltab 0 ?? everything seems off by 1 at some point
                return Stat(stat_name, mod_strings["StrSklTabItem" + str(int(param)+1)].replace("%d", get_value_string("", min, max)), int(item_stat_cost_row[39]))
            if stat_name == "item_nonclassskill":
                return Stat(stat_name, "+" + get_value_string("", min, max) + " to " + get_skill_name(param), int(item_stat_cost_row[39]))
            if stat_name == "item_charged_skill":
                return Stat(stat_name, "Level " + str(max) + " " + get_skill_name(param) + " (" + min + "/" + min + " Charges)", int(item_stat_cost_row[39]))
            if stat_name == "item_skillonhit":
                return Stat(stat_name, str(min) + "% Chance To Cast Level " + str(max) + " " + get_skill_name(param) + " On Striking", int(item_stat_cost_row[39]))
            if stat_name == "item_skillongethit":
                 return Stat(stat_name, str(min) + "% Chance To Cast Level " + str(max) + " " + get_skill_name(param) + " When Struck", int(item_stat_cost_row[39]))
            if stat_name == "fade":
                return Stat(stat_name, "Fade (Cosmetic Effect)", int(item_stat_cost_row[39]))
            if stat_name == "killheal_dummy":
                return Stat(stat_name, mod_strings["healkillStr"].replace("%d%", str(min)), int(item_stat_cost_row[39]))
            if stat_name == "item_skillonattack":
                return Stat(stat_name, str(min) + "% Chance To Cast Level " + str(max) + " " + get_skill_name(param) + " On Attack", int(item_stat_cost_row[39]))
            if stat_name == "item_skillonkill":
                return Stat(stat_name, str(min) + "% Chance To Cast Level " + str(max) + " " + get_skill_name(param) + " When You Kill An Enemy", int(item_stat_cost_row[39]))
            if stat_name == "item_skillondeath":
                return Stat(stat_name, str(min) + "% Chance To Cast Level " + str(max) + " " + get_skill_name(param) + " When You Die", int(item_stat_cost_row[39]))
            if stat_name == "item_skillonlevelup":
                return Stat(stat_name, str(min) + "% Chance To Cast Level " + str(max) + " " + get_skill_name(param) + " When You Level Up", int(item_stat_cost_row[39]))
            if stat_name == "curse_resistance" or stat_name == "coldlength" or stat_name == "poisonlength" or stat_name == "heal_kill_per_maxhp":
                return None
            
            priority = item_stat_cost_row[39]
            if not item_stat_cost_row[39].isdigit():
                print("No Priority for stat: " + stat_name + ". Using priority 0")
                priority = 0
            if not item_stat_cost_row[40].isdigit():
                print("Bad stat no func: " + stat_name)
                return None
            func = int(item_stat_cost_row[40])
            if not item_stat_cost_row[41].isdigit():
                print("Bad stat no val: " + stat_name)
                return None
            val = int(item_stat_cost_row[41])

            string1 = mod_strings.get(item_stat_cost_row[42], "EMPTY")
            string2 = mod_strings.get(item_stat_cost_row[44], "EMPTY")

            #@TODO there's a bunch of other parameters we need to find and pass in here
            if 0 == val:
                return Stat(stat_name, stat_formats.get_stat_string0(func, string1, string2), priority)
            if 1 == val:
                return Stat(stat_name, stat_formats.get_stat_string1(func, get_value_string(param, min, max), string1, string2), priority)
            if 2 == val:
                return Stat(stat_name, stat_formats.get_stat_string2(func, get_value_string(param, min, max), string1, string2), priority)

def fill_property_stats(property):
    properties_table = open(data_path + "/global/excel/Properties.txt", newline='')
    properties_rows = csv.reader(properties_table, delimiter='\t')
    
    for property_row in properties_rows:
        if property.name == property_row[0]:
            for i in range(7):
                if property_row[5+i*4] != "":
                    property.stats.append(get_stat(property_row[5+i*4], property.param, property.min, property.max))

def get_unique_items():
    unique_items_table = open(data_path + "/global/excel/uniqueitems.txt", newline='')
    unique_items_rows = csv.reader(unique_items_table, delimiter='\t')
    unique_items = []
    for i, row in enumerate(unique_items_rows):
        # Ignore header
        if i == 0:
            continue
        # If item is enabled
        if row[4].isdigit() and int(row[4]) > 0:
            properties = []
            for j in range(12):
                # If the property doesn't have a name, then there isn't a property
                if row[21+j*4] != "":
                    properties.append(Property(row[21+j*4], row[22+j*4], row[23+j*4], row[24+j*4]))
            unique_items.append(Unique_Item(row[0], row[6], row[7], properties))
    
    for unique_item in unique_items:
        for property in unique_item.properties:
            fill_property_stats(property)
    return unique_items

#get_unique_items()
for unique_item in get_unique_items():
    if unique_item.name.startswith("Thunder"):
        print_item(unique_item)