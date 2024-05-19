from table_strings import *
from load_txts import *
from stat_formats import *

class Stat:
    def __init__(self, name, stat_string, priority):
        self.name = name
        self.stat_string = stat_string
        self.priority = priority

class Property:
    def __init__(self, name, param, min, max, is_automod=False):
        self.name = name
        self.param = param
        self.min = min
        self.max = max
        self.is_automod = is_automod
        self.stats = []

class Item:
    def __init__(self, name, item_level, required_level, properties, base_code, mod_strings, tables):
        self.name = mod_strings.get(name, "MISSING tbl: " + name)
        self.item_level = item_level
        self.required_level = required_level
        self.properties = properties
        self.base_code = base_code
        self.bg_color_code = 101010
        self.utils = Utils(tables, mod_strings)
        self.gamble_item = self.utils.get_gamble_item_from_code(base_code)
        self.base_name = self.utils.get_item_name_from_code(base_code)
        self.utils.fill_automod(self.properties, base_code)
        self.staffmod = self.utils.get_staffmod(base_code)
        self.spelldesc = self.utils.get_spelldesc(base_code)

        for p in self.properties:
            self.utils.fill_property_stats(p)
        self.utils.fill_group_stats(self.properties)
         
    def get_stats_sorted(self):
        stats = []
        for prop in self.properties:
            for stat in prop.stats:
                stats.append(stat)
        return sorted(stats, key = lambda x: int(x.priority), reverse=True)

class Utils:
    def __init__(self, tables, mod_strings):
        self.mod_strings = mod_strings
        self.tables = tables
        self.stat_formats = Stat_Formats(tables, mod_strings)

    def get_value_string(self, param, min, max):
        if param != "":
            return str(param)
        
        if min == "" and max == "":
            return "NOVALUE"

        if min == "":
            return str(max)

        if max == "":
            return str(min)

        if min == max:
            return str(min)
            
        return str(min) + "-" + str(max)

    def short_to_long_class(self, short):
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
        return "Unknown class: " + short

    def get_class_from_tab_number(self, tab_number):
        tab_number = int(tab_number)
        if tab_number in (0,1,2):
            return "Amazon"
        if tab_number in (3,4,5):
            return "Sorceress"
        if tab_number in (6,7,8):
            return "Necromancer"
        if tab_number in (9,10,11):
            return "Paladin"
        if tab_number in (12,13,14):
            return "Barbarian"
        if tab_number in (15,16,17):
            return "Druid"
        if tab_number in (18,19,20):
            return "Assassin"
        return "Unknown"

    def get_class_from_skill_name(self, skill_name):
        for skill_row in self.tables.skills_table:
            if str(skill_name) == str(skill_row[0]) or str(skill_name) == str(skill_row[1]):
                return self.short_to_long_class(skill_row[2])
        return "Unknown+" + skill_name

    def get_class_from_skill_range(self, start, end):
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

    def get_skill_name(self, skill):
        if skill == "":
            return
        skill_desc = ""
        for skill_row in self.tables.skills_table:
            if skill.isdigit():
                if str(skill) == str(skill_row[1]):
                    skill_desc = skill_row[3] 
            if str(skill).lower() == str(skill_row[0]).lower():
                skill_desc = skill_row[3]

        if skill_desc == "":
            print("Did not find skill desc for skill: " + skill)
            return skill
        
        for skill_desc_row in self.tables.skill_desc_table:
            if skill_desc == skill_desc_row[0]:
                skill_name = self.mod_strings.get(skill_desc_row[7], "")
                if skill_name != "":
                    return skill_name

        print("Did not find skill name for skill: " + skill)
        return skill

    def get_item_name_from_code(self, code):
        # Use weapon/armor namestr if it exists, otherwise use misc.txt
        for row in self.tables.armor_table:
            if row[17] == code and row[4] == str(1):
                if self.mod_strings.get(row[18]) is not None:
                    return self.mod_strings[row[18]]
        for row in weapons_table:
            if row[3] == code and row[9] == str(1):
                if self.mod_strings.get(row[5]) is not None:
                    return self.mod_strings[row[5]]

        for row in self.tables.misc_table:
            if row[13] == code:
                return self.mod_strings[row[15]]
        if self.mod_strings.get(code) is not None:
            return self.mod_strings[code]
        print("No name found for code: " + code)
        return "NO_NAME"

    def is_in_gamble_table(self, code):
        for row in self.tables.gamble_table:
            if row[1] == code:
                return True
        return False

    def get_gamble_item_from_code(self, code):
        for row in self.tables.armor_table:
            if row[17] == code and row[4] == str(1):
                for row_again in self.tables.armor_table:
                    if row_again[17] != "" and row_again[17] == row[23] and self.is_in_gamble_table(row_again[17]):
                        return self.get_item_name_from_code(row_again[17]) + " (" + row_again[17] + ")"
        for row in self.tables.weapons_table:
            if row[3] == code and row[9] == str(1):
                for row_again in self.tables.weapons_table:
                    if row_again[3] != "" and row_again[3] == row[34] and self.is_in_gamble_table(row_again[3]):
                        return self.get_item_name_from_code(row_again[3]) + " (" + row_again[3] + ")"
        for row in self.tables.misc_table:
            if row[13] != "" and row[13] == code and row[8] == str(1) and self.is_in_gamble_table(row[13]):
                return self.get_item_name_from_code(row[13]) + " (" + row[13] + ")"
        return "N/A"

    def get_all_equivalent_types(self, types):
        while True:
            keep_going = False
            for item_type in self.tables.item_types_table:
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

    def is_of_item_type(self, types, include_types):
        # Build up a list of all types, then check if any of them are in include_types
        all_types = self.get_all_equivalent_types(types)
        return set(all_types) & set(include_types)

    def handle_op(self, value, op, op_param, op_base, op_stat1, op_stat2, op_stat3):
        if not value.isdigit():
            return value
        if op == str(1):
            if not op_base.isdigit():
                return value
            value = (value * int(op_base)) / 100
        if op == str(2):
            value = float(value) * 1 / pow(2, float(op_param))
        if op == str(3):
            value = float(value) * 1 / pow(2, float(op_param))
        if op == str(4):
            value = float(value) * 1 / pow(2, float(op_param))
        if op == str(5):
            value = float(value) * 1 / pow(2, float(op_param))
        # 6 and 7 don't work
        # @TODO 8 hardcoded for max mana?
        if op == str(8):
            return value
        # @TODO 9 hardcoded for max hp / stamina?
        if op == str(9):
            return value
        # 10 doesn't exist
        if op == str(11):
            if not op_base.isdigit():
                return value
            value = (value * int(op_base)) / 100
        # 12 doesn't exist
        if op == str(13):
            if not op_base.isdigit():
                return value
            value = (value * int(op_base)) / 100

        if value.is_integer():
            value = int(value)
        return str(value)

    def get_stat(self, stat_name, param, min, max, prop_name):
        for item_stat_cost_row in self.tables.item_stat_cost_table:
            if stat_name == item_stat_cost_row[0]:
                if item_stat_cost_row[25] != 0 and item_stat_cost_row[25] != "":
                    param = self.handle_op(param, item_stat_cost_row[25], item_stat_cost_row[26], item_stat_cost_row[27], item_stat_cost_row[28], item_stat_cost_row[29], item_stat_cost_row[30])
                    min = self.handle_op(min, item_stat_cost_row[25], item_stat_cost_row[26], item_stat_cost_row[27], item_stat_cost_row[28], item_stat_cost_row[29], item_stat_cost_row[30])
                    max = self.handle_op(max, item_stat_cost_row[25], item_stat_cost_row[26], item_stat_cost_row[27], item_stat_cost_row[28], item_stat_cost_row[29], item_stat_cost_row[30])

                # Custom handling
                if stat_name == "item_numsockets":
                    # @TODO Could be a bug with socket range 0-n, I think it can roll 0 but then gives 1? More testing needed (Faith shield)
                    return Stat(stat_name, "Socketed (" + self.get_value_string(param, min, max) + ")", int(item_stat_cost_row[39]))
                if stat_name == "item_singleskill":
                    # Seems to work but is there a better way to determine if it's +random skill or +specific skill?
                    if param.isdigit() and self.get_class_from_skill_range(min, max) != "Unknown":
                        return Stat(stat_name, "+" + str(param) + " to Random " + self.get_class_from_skill_range(min, max) + " Skill", int(item_stat_cost_row[39]))
                    return Stat(stat_name, "+" + self.get_value_string("", min, max) + " to " + self.get_skill_name(param) + " (" + self.get_class_from_skill_name(param) + " Only)", int(item_stat_cost_row[39]))
                if stat_name == "item_addskill_tab":
                    # Some hard coded nonsense... known issue though
                    skill_tab_conversion = [3, 2, 1, 15, 14, 13, 8, 7, 9, 6, 5, 4, 11, 12, 10, 16, 17, 18, 19, 20, 21];
                    param = str(int(param))
                    p = str(skill_tab_conversion[int(param)])
                    return Stat(stat_name, self.mod_strings["StrSklTabItem" + p].replace("%d", self.get_value_string("", min, max)) + " (" + self.get_class_from_tab_number(int(param)) + " Only)", int(item_stat_cost_row[39]))
                if stat_name == "item_nonclassskill":
                    return Stat(stat_name, "+" + self.get_value_string("", min, max) + " to " + self.get_skill_name(param), int(item_stat_cost_row[39]))
                if stat_name == "item_charged_skill":
                    return Stat(stat_name, "Level " + str(max) + " " + self.get_skill_name(param) + " (" + min + "/" + min + " Charges)", int(item_stat_cost_row[39]))
                if stat_name == "item_skillonhit":
                    return Stat(stat_name, str(min) + "% Chance To Cast Level " + str(max) + " " + self.get_skill_name(param) + " On Striking", int(item_stat_cost_row[39]))
                if stat_name == "item_skillongethit":
                     return Stat(stat_name, str(min) + "% Chance To Cast Level " + str(max) + " " + self.get_skill_name(param) + " When Struck", int(item_stat_cost_row[39]))
                if stat_name == "fade":
                    return Stat(stat_name, "Fade (Cosmetic Effect)", int(item_stat_cost_row[39]))
                if stat_name == "killheal_dummy":
                    return Stat(stat_name, self.mod_strings["healkillStr"].replace("%d%", str(min)), int(item_stat_cost_row[39]))
                if stat_name == "item_skillonattack":
                    return Stat(stat_name, str(min) + "% Chance To Cast Level " + str(max) + " " + self.get_skill_name(param) + " On Attack", int(item_stat_cost_row[39]))
                if stat_name == "item_skillonkill":
                    return Stat(stat_name, str(min) + "% Chance To Cast Level " + str(max) + " " + self.get_skill_name(param) + " When You Kill An Enemy", int(item_stat_cost_row[39]))
                if stat_name == "item_skillondeath":
                    return Stat(stat_name, str(min) + "% Chance To Cast Level " + str(max) + " " + self.get_skill_name(param) + " When You Die", int(item_stat_cost_row[39]))
                if stat_name == "item_skillonlevelup":
                    return Stat(stat_name, str(min) + "% Chance To Cast Level " + str(max) + " " + self.get_skill_name(param) + " When You Level Up", int(item_stat_cost_row[39]))
                # @TODO could get rid of this case if we refactor stat_formats to take in param and min and max
                if stat_name == "item_addclassskills":
                    return Stat(stat_name, "+" + str(self.get_value_string("", min, max)) + " to " + self.short_to_long_class(prop_name) + " Skill Levels", int(item_stat_cost_row[39]))
                if stat_name == "curse_resistance" or stat_name == "coldlength" or stat_name == "poisonlength" or stat_name == "heal_kill_per_maxhp":
                    return None
                
                priority = item_stat_cost_row[39]
                if not item_stat_cost_row[39].isdigit():
                    #print("No Priority for stat: " + stat_name + ". Using priority 0")
                    priority = 0
                if not item_stat_cost_row[40].isdigit():
                    print("Bad stat no func: " + stat_name)
                    return None
                func = int(item_stat_cost_row[40])
                if not item_stat_cost_row[41].isdigit():
                    print("Bad stat no val: " + stat_name)
                    return None
                val = int(item_stat_cost_row[41])

                string1 = self.mod_strings.get(item_stat_cost_row[42], "EMPTY")
                # @TODO Negative string?
                string2 = self.mod_strings.get(item_stat_cost_row[44], "EMPTY")

                #@TODO there's a bunch of other parameters we need to find and pass in here
                if 0 == val:
                    return Stat(stat_name, self.stat_formats.get_stat_string0(func, string1, param, min, max, string2, skill=self.get_skill_name(param), slvl=self.get_value_string("", min, max)), priority)
                if 1 == val:
                    return Stat(stat_name, self.stat_formats.get_stat_string1(func, self.get_value_string(param, min, max), string1, param, min, max, string2), priority)
                if 2 == val:
                    return Stat(stat_name, self.stat_formats.get_stat_string2(func, self.get_value_string(param, min, max), string1, param, min, max, string2), priority)
        return None

    def fill_property_stats(self, property):
        # Custom handling
        if property.name == "dmg%":
            # @TODO Figure out proper priority 
            property.stats.append(Stat(property.name, "+" + self.get_value_string(property.param, property.min, property.max) + "% Enhanced Damage", 144))
            return
        if property.name == "dmg-min":
            # @TODO Figure out proper string and priority
            property.stats.append(Stat(property.name, "+" + self.get_value_string(property.param, property.min, property.max) + " to Minimum Damage", 143))
            return
        if property.name == "dmg-max":
            # @TODO Figure out proper string and priority
            property.stats.append(Stat(property.name, "+" + self.get_value_string(property.param, property.min, property.max) + " to Maximum Damage", 142))
            return
        if property.name == "indestruct":
            # @TODO Figure out proper string and priority
            property.stats.append(Stat(property.name, "Indestructible", 5))
            return
        if property.name == "fear":
            # @TODO Figure out proper string and priority
            property.stats.append(Stat(property.name, "Hit Causes Monster to Flee " + self.get_value_string(property.param, property.min, property.max) + "%", 5))
            return

        foundone = False
        for property_row in self.tables.properties_table:
            if property.name == property_row[0]:
                for i in range(7):
                    if property_row[5+i*4] != "":
                        foundone = True
                        stat = self.get_stat(property_row[5+i*4], property.param, property.min, property.max, property.name)
                        if stat is not None:
                            property.stats.append(stat)
        if not foundone:
            print("Didn't find property stats for property: " + property.name)

    def get_item_name_from_code(self, code):
        # Use weapon/armor namestr if it exists, otherwise use misc.txt
        for row in self.tables.armor_table:
            if row[17] == code and row[4] == str(1):
                if self.mod_strings.get(row[18]) is not None:
                    return self.mod_strings[row[18]]
        for row in self.tables.weapons_table:
            if row[3] == code and row[9] == str(1):
                if self.mod_strings.get(row[5]) is not None:
                    return self.mod_strings[row[5]]

        for row in self.tables.misc_table:
            if row[13] == code:
                return self.mod_strings.get(row[15], "MISSING TBL: " + row[15])
        if self.mod_strings.get(code) is not None:
            return self.mod_strings[code]
        print("No name found for code: " + code)
        return "NO_NAME"

    def get_staffmod(self, code):
        for armor in self.tables.armor_table:
            if armor[17] == code:
                for item_type in self.tables.item_types_table:
                    if item_type[1] == armor[48] and item_type[25] != "":
                        return self.short_to_long_class(item_type[25])
        return ""

    def get_spelldesc(self, code):
        for row in self.tables.misc_table:
            if row[13] == code:
                return self.mod_strings.get(row[64], "")

    def fill_automod(self, properties, code):
        automods = {}
        for armor in self.tables.armor_table:
            if armor[17] == code and armor[20] != "":
                for autos in self.tables.automagic_table:
                    # @TODO Maybe look at exclude types too?
                    # @TODO look at item level too
                    if autos[10] == armor[20] and self.is_of_item_type([armor[48], armor[49]], [autos[25], autos[26], autos[27], autos[28], autos[29], autos[30], autos[31]]):
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
                properties.append(Property(key, automods[key][0], automods[key][1], automods[key][2], is_automod=True))

    # Custom handling for hardcoded groups
    def handle_hardcoded_groups(self, property):
        priority = 0
        if property.name == "dmg-fire":
            for stat in list(property.stats):
                priority = stat.priority
                property.stats.remove(stat)
            property.stats.append(Stat("Group Stat", self.mod_strings["strModFireDamageRange"].replace("%d-%d", self.get_value_string(property.param, property.min, property.max)).title(), priority))
        if property.name == "dmg-cold":
            for stat in list(property.stats):
                priority = stat.priority
                property.stats.remove(stat)
            property.stats.append(Stat("Group Stat", self.mod_strings["strModColdDamageRange"].replace("%d-%d", self.get_value_string("", property.min, property.max)).title(), priority))
        if property.name == "dmg-ltng":
            for stat in list(property.stats):
                priority = stat.priority
                property.stats.remove(stat)
            property.stats.append(Stat("Group Stat", self.mod_strings["strModLightningDamageRange"].replace("%d-%d", self.get_value_string(property.param, property.min, property.max)).title(), priority))
        if property.name == "dmg-mag":
            for stat in list(property.stats):
                priority = stat.priority
                property.stats.remove(stat)
            property.stats.append(Stat("Group Stat", self.mod_strings["strModMagicDamageRange"].replace("%d-%d", self.get_value_string(property.param, property.min, property.max)).title(), priority))
        if property.name == "dmg-norm":
            for stat in list(property.stats):
                priority = stat.priority
                property.stats.remove(stat)
            property.stats.append(Stat("Group Stat", self.mod_strings["strModMinDamageRange"].replace("%d-%d", self.get_value_string(property.param, property.min, property.max)).title(), priority))
        if property.name == "dmg-pois":
            for stat in list(property.stats):
                priority = stat.priority
                property.stats.remove(stat)
            real_length = int(int(property.param)/25)
            real_min = int(int(property.min)/256*real_length*25)
            real_max = int(int(property.max)/256*real_length*25)
            property.stats.append(Stat("Group Stat", self.mod_strings["strModPoisonDamageRange"].replace("%d-%d", self.get_value_string("", real_min, real_max)).replace("%d", str(real_length)).title(), priority))

    def fill_group_stats(self, properties):
        groups = {}
        # Make a dict of lists, containing the dgrp and the associated stats
        for i, row in enumerate(self.tables.item_stat_cost_table):
            if row[45] != "":
                if row[45] in groups:
                    tmp = groups[row[45]]
                    tmp.append(row[0])
                    groups[row[45]] = tmp
                else:
                    groups[row[45]] = [row[0]]
        
        item_group_stats = {}
        for property in properties:
            for stat in property.stats:
                for row in self.tables.item_stat_cost_table:
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
                    prop = Property("Group Property", param, min, max, props[0].is_automod)
                    prop.stats.append(Stat("Group Stat",
                                           self.stat_formats.get_stat_string1(int(func),
                                                                         self.get_value_string(param, min, max),
                                                                         self.mod_strings.get(string1, "NONE"),
                                                                         param,
                                                                         min,
                                                                         max,
                                                                         self.mod_strings.get(string2, "NONE")), priority))
                    properties.append(prop)
                    for p in list(props):
                        try:
                            properties.remove(p)
                        except:
                            pass
        # Custom handling for hard-coded flat damage adds
        for property in properties:
            self.handle_hardcoded_groups(property)

    def string_array_to_html(self, strs, numbr=1):
        br = "<br>"*numbr
        mystring = ""
        for s in strs:
            if mystring != "":
                mystring = mystring + br + s
            else:
                mystring = s
        return mystring
