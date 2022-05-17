from enum import unique
from operator import attrgetter
import os
import csv
import table_strings
import stat_formats
import load_txts

mod_strings = table_strings.get_string_dict()

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
    def __init__(self, name, item_level, required_level, properties, base_name, base_code, gamble_item):
        self.name = name
        self.item_level = item_level
        self.required_level = required_level
        self.properties = properties
        self.gamble_item = gamble_item
        self.base_name = base_name
        self.base_code = base_code
        self.bg_color_code = 101010
        
    def get_stats_sorted(self):
        stats = []
        for prop in self.properties:
            for stat in prop.stats:
                stats.append(stat)
        return sorted(stats, key = lambda x: int(x.priority), reverse=True)

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

def short_to_long_class(short):
    if short == "ama":
        return "Amazon"
    if short == "sor":
        return "Sorceress"
    if short == "nec":
        return "Necromancer"
    if short == "pal":
        return "Paladin"
    if short == "bar":
        return "Barbarian"
    if short == "dru":
        return "Druid"
    if short == "ass":
        return "Assassin"
    return "Unknown"

def get_class_from_tab_number(tab_number):
    tab_number = int(tab_number)
    if tab_number < 4:
        return "Amazon"
    if tab_number < 7:
        return "Paladin"
    if tab_number < 10:
        return "Necromancer"
    if tab_number < 13:
        return "Barbarian"
    if tab_number < 16:
        return "Sorceress"
    if tab_number < 19:
        return "Druid"
    if tab_number < 22:
        return "Assassin"
    return "Unknown"

def get_class_from_skill_name(skill_name):
    for skill_row in load_txts.skills_table:
        if str(skill_name) == str(skill_row[0]) or str(skill_name) == str(skill_row[1]):
            return short_to_long_class(skill_row[2])
    return "Unknown+" + skill_name

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
    if skill == "":
        return
    skill_desc = ""
    for skill_row in load_txts.skills_table:
        if skill.isdigit():
            if str(skill) == str(skill_row[1]):
                skill_desc = skill_row[3] 
        if str(skill).lower() == str(skill_row[0]).lower():
            skill_desc = skill_row[3]

    if skill_desc == "":
        print("Did not find skill desc for skill: " + skill)
        return skill
    
    for skill_desc_row in load_txts.skill_desc_table:
        if skill_desc == skill_desc_row[0]:
            skill_name = mod_strings.get(skill_desc_row[7], "")
            if skill_name != "":
                return skill_name

    print("Did not find skill name for skill: " + skill)
    return skill

def get_stat(stat_name, param, min, max, prop_name):
    for item_stat_cost_row in load_txts.item_stat_cost_table:
        if stat_name == item_stat_cost_row[0]:
            
            # Custom handling
            if stat_name == "item_numsockets":
                # @TODO Could be a bug with socket range 0-n, I think it can roll 0 but then gives 1? More testing needed (Faith shield)
                return Stat(stat_name, "Socketed (" + get_value_string(param, min, max) + ")", int(item_stat_cost_row[39]))
            if stat_name == "item_singleskill":
                # Seems to work but is there a better way to determine if it's +random skill or +specific skill?
                if param.isdigit() and get_class_from_skill_range(min, max) != "Unknown":
                    return Stat(stat_name, "+" + str(param) + " to Random " + get_class_from_skill_range(min, max) + " Skill", int(item_stat_cost_row[39]))
                return Stat(stat_name, "+" + get_value_string("", min, max) + " to " + get_skill_name(param) + " (" + get_class_from_skill_name(param) + " Only)", int(item_stat_cost_row[39]))
            if stat_name == "item_addskill_tab":
                # @TODO is there a better way to do this?
                if "0" == param:
                    param = "3"
                elif "1" == param:
                    param = "2"
                elif "2" == param:
                    param = "1"
                elif "3" ==  param:
                    param = "15"
                elif "4" == param:
                    param = "14"
                elif "5" == param:
                    param = "13"
                elif "6" == param:
                    param = "8"
                elif "8" == param:
                    param = "9"
                elif "9" == param:
                    param = "5"
                elif "10" == param:
                    param = "6"
                elif "11" == param:
                    param = "4"
                elif "13" == param:
                    param = "11"
                elif "14" == param:
                    param = "10"
                elif "15" == param or "16" == param or "17" == param or "18" == param or "19" == param or "20" == param:
                    param = str(int(param) + 1)
                return Stat(stat_name, mod_strings["StrSklTabItem" + str(int(param))].replace("%d", get_value_string("", min, max)) + " (" + get_class_from_tab_number(int(param)) + " Only)", int(item_stat_cost_row[39]))
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
            # @TODO could get rid of this case if we refactor stat_formats to take in param and min and max
            if stat_name == "item_addclassskills":
                return Stat(stat_name, "+" + str(get_value_string("", min, max)) + " to " + short_to_long_class(prop_name) + " Skill Levels", int(item_stat_cost_row[39]))
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
            # @TODO Negative string?
            string2 = mod_strings.get(item_stat_cost_row[44], "EMPTY")

            #@TODO there's a bunch of other parameters we need to find and pass in here
            if 0 == val:
                return Stat(stat_name, stat_formats.get_stat_string0(func, string1, string2, skill=get_skill_name(param), slvl=get_value_string("", min, max)), priority)
            if 1 == val:
                return Stat(stat_name, stat_formats.get_stat_string1(func, get_value_string(param, min, max), string1, string2), priority)
            if 2 == val:
                return Stat(stat_name, stat_formats.get_stat_string2(func, get_value_string(param, min, max), string1, string2), priority)
    return None

def fill_property_stats(property):
    # Custom handling
    if property.name == "dmg%":
        # @TODO Figure out proper priority 
        property.stats.append(Stat(property.name, "+" + get_value_string(property.param, property.min, property.max) + "% Enhanced Damage", 144))
        return
    if property.name == "dmg-min":
        # @TODO Figure out proper string and priority
        property.stats.append(Stat(property.name, "+" + get_value_string(property.param, property.min, property.max) + " to Minimum Damage", 143))
        return
    if property.name == "dmg-max":
        # @TODO Figure out proper string and priority
        property.stats.append(Stat(property.name, "+" + get_value_string(property.param, property.min, property.max) + " to Maximum Damage", 142))
        return
    if property.name == "indestruct":
        # @TODO Figure out proper string and priority
        property.stats.append(Stat(property.name, "Indestructible", 5))
        return
    if property.name == "fear":
        # @TODO Figure out proper string and priority
        property.stats.append(Stat(property.name, "Hit Causes Monster to Flee " + get_value_string(property.param, property.min, property.max) + "%", 5))
        return

    foundone = False
    for property_row in load_txts.properties_table:
        if property.name == property_row[0]:
            for i in range(7):
                if property_row[5+i*4] != "":
                    foundone = True
                    stat = get_stat(property_row[5+i*4], property.param, property.min, property.max, property.name)
                    if stat is not None:
                        property.stats.append(stat)
    if not foundone:
        print("Didn't find property stats for property: " + property.name)

def get_gamble_item_from_code(code):
    for row in load_txts.armor_table:
        if row[17] == code and row[4] == str(1):
            for row_again in load_txts.armor_table:
                if row_again[17] == row[23]:
                    return row_again[0] + " (" + row_again[17] + ")"
    for row in load_txts.weapons_table:
        if row[3] == code and row[9] == str(1):
            for row_again in load_txts.weapons_table:
                if row_again[3] == row[34]:
                    return row_again[0] + " (" + row_again[3] + ")"

def get_all_equivalent_types(types):
    while True:
        keep_going = False
        for item_type in load_txts.item_types:
            if item_type[1] in types:
                if item_type[2] not in types:
                    types.append(item_type[2])
                    keep_going = True
                if item_type[3] not in types:
                    types.append(item_type[3])
                    keep_going = True
        if not keep_going:
            types.remove("")
            return types

def is_of_item_type(types, include_types):
    # Build up a list of all types, then check if any of them are in include_types
    all_types = get_all_equivalent_types(types)
    return set(all_types) & set(include_types)


def fill_automod(properties, code):
    automods = {}
    for armor in load_txts.armor_table:
        if armor[17] == code and armor[20] != "":
            for autos in load_txts.automagic_table:
                # @TODO Maybe look at exclude types too?
                # @TODO look at item level too
                if autos[10] == armor[20] and is_of_item_type([armor[48], armor[49]], [autos[25], autos[26], autos[27], autos[28], autos[29], autos[30], autos[31]]):
                    if autos[11] in automods:
                        automods[autos[11]] = [autos[12], min(autos[13], automods[autos[11]][1]), max(autos[14], automods[autos[11]][2])]
                    else:
                        automods[autos[11]] = [autos[12], autos[13], autos[14]]

                    if autos[15] in automods:
                        automods[autos[15]] = [autos[16], min(autos[17], automods[autos[15]][1]), max(autos[18], automods[autos[15]][2])]
                    else:
                        automods[autos[15]] = [autos[16], autos[17], autos[18]]

                    if autos[19] in automods:
                        automods[autos[19]] = [autos[20], min(autos[21], automods[autos[19]][1]), max(autos[22], automods[autos[19]][2])]
                    else:
                        automods[autos[19]] = [autos[20], autos[21], autos[22]]

    for key in automods:
        if key != "":
            properties.append(Property(key, automods[key][0], automods[key][1], automods[key][2]))

# Custom handling for hardcoded groups
def handle_hardcoded_groups(property):
    priority = 0
    if property.name == "dmg-fire":
        for stat in list(property.stats):
            priority = stat.priority
            property.stats.remove(stat)
        property.stats.append(Stat("Group Stat", mod_strings["strModFireDamageRange"].replace("%d-%d", get_value_string(property.param, property.min, property.max)), priority))
    if property.name == "dmg-cold":
        for stat in list(property.stats):
            priority = stat.priority
            property.stats.remove(stat)
        property.stats.append(Stat("Group Stat", mod_strings["strModColdDamageRange"].replace("%d-%d", get_value_string(property.param, property.min, property.max)), priority))
    if property.name == "dmg-ltng":
        for stat in list(property.stats):
            priority = stat.priority
            property.stats.remove(stat)
        property.stats.append(Stat("Group Stat", mod_strings["strModLightningDamageRange"].replace("%d-%d", get_value_string(property.param, property.min, property.max)), priority))
    if property.name == "dmg-mag":
        for stat in list(property.stats):
            priority = stat.priority
            property.stats.remove(stat)
        property.stats.append(Stat("Group Stat", mod_strings["strModMagicDamageRange"].replace("%d-%d", get_value_string(property.param, property.min, property.max)), priority))
    if property.name == "dmg-norm":
        for stat in list(property.stats):
            priority = stat.priority
            property.stats.remove(stat)
        property.stats.append(Stat("Group Stat", mod_strings["strModMinDamageRange"].replace("%d-%d", get_value_string(property.param, property.min, property.max)), priority))
    if property.name == "dmg-pois":
        for stat in list(property.stats):
            priority = stat.priority
            property.stats.remove(stat)
        property.stats.append(Stat("Group Stat", mod_strings["strModPoisonDamageRange"].replace("%d-%d", get_value_string("", property.min, property.max)).replace("%d", property.param), priority))


def fill_group_stats(unique_item):
    groups = {}
    # Make a dict of lists, containing the dgrp and the associated stats
    for i, row in enumerate(load_txts.item_stat_cost_table):
        if i == 0:
            continue
        if row[45] != "":
            if row[45] in groups:
                tmp = groups[row[45]]
                tmp.append(row[0])
                groups[row[45]] = tmp
            else:
                groups[row[45]] = [row[0]]
    
    item_group_stats = {}
    for property in unique_item.properties:
        for stat in property.stats:
            for row in load_txts.item_stat_cost_table:
                # If there is a group text for this mod
                if stat.name == row[0] and row[45] != "":
                    item_group_stats[row[0]] = [property.param, property.min, property.max, row[39], row[46], row[48], row[50], property]

    for key in groups:
        found = True
        # if all stats in group are present on item
        for stat in groups[key]:
            if stat not in item_group_stats:
                found = False
        if found:
            use_group_string = True
            # if all found group stats are equal
            param = None
            min = None
            max = None
            priority = None
            func = None
            props = []
            for i, stat in enumerate(groups[key]):
                props.append(item_group_stats[stat][7])
                if i == 0:
                    param = item_group_stats[stat][0]
                    min = item_group_stats[stat][1]
                    max = item_group_stats[stat][2]
                    priority = item_group_stats[stat][3]
                    func = item_group_stats[stat][4]
                    string1 = item_group_stats[stat][5]
                    string2 = item_group_stats[stat][6]
                if param != item_group_stats[stat][0] or min != item_group_stats[stat][1] or max != item_group_stats[stat][2]:
                    use_group_string = False
            if use_group_string:
                prop = Property("Group Property", param, min, max)
                prop.stats.append(Stat("Group Stat", stat_formats.get_stat_string1(int(func), get_value_string(param, min, max), mod_strings.get(string1, "NONE"), mod_strings.get(string2, "NONE")), priority))
                unique_item.properties.append(prop)
                for p in list(props):
                    try:
                        unique_item.properties.remove(p)
                    except:
                        pass
    # Custom handling for hard-coded flat damage adds
    for property in unique_item.properties:
        handle_hardcoded_groups(property)




                





def get_unique_items():
    unique_items = []
    for i, row in enumerate(load_txts.unique_items_table):
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
            fill_automod(properties, row[8])
            unique_items.append(Unique_Item(row[0], row[6], row[7], properties, row[9], row[8], get_gamble_item_from_code(row[8])))
    
    for unique_item in unique_items:
        for property in unique_item.properties:
            fill_property_stats(property)
        fill_group_stats(unique_item)
    return unique_items

#get_unique_items()