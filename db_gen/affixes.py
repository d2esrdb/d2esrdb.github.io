import stat_formats
from utils import *

class Affix:
    def __init__(self, name, rare, level, max_level, required_level, rarity, stat_string, item_types):
        self.name = name
        self.rare = rare
        self.level = level
        self.required_level = required_level
        self.max_level = max_level
        self.rarity = rarity
        self.stat_string = stat_string
        self.item_types = item_types
        self.item_types_string = ", ".join(item_types)

class Affix_Utils:
    def __init__(self, tables, mod_strings):
        self.tables = tables
        self.mod_strings = mod_strings
        self.stat_formats = Stat_Formats(tables, mod_strings)
        self.utils = Utils(tables, mod_strings)

    def get_group_prop(self, property):
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
                    prop = Property("Group Property", param, min, max)
                    prop.stats.append(Stat("Group Stat", self.stat_formats.get_stat_string1(int(func), self.utils.get_value_string(param, min, max), self.mod_strings.get(string1, "NONE"), param, min, max, self.mod_strings.get(string2, "NONE")), priority))
                    return prop

        self.utils.handle_hardcoded_groups(property)
        return property

    def get_affixes(self, table):
        affixes = []
        for i, affix in enumerate(table):
            if affix[2] != str(1):
                continue
            prop1 = Property(affix[12], affix[13], affix[14], affix[15])
            self.utils.fill_property_stats(prop1)
            prop1 = self.get_group_prop(prop1)
            prop2 = None
            prop3 = None
            if affix[16] != "":
                prop2 = Property(affix[16], affix[17], affix[18], affix[19])
                self.utils.fill_property_stats(prop2)
                prop2 = self.get_group_prop(prop2)
            if affix[20] != "":
                prop3 = Property(affix[20], affix[21], affix[22], affix[23])
                self.utils.fill_property_stats(prop3)
                prop3 = self.get_group_prop(prop3)
            stats = []
            for stat in prop1.stats:
                stats.append(stat.stat_string)
            if prop2 is not None:
                for stat in prop2.stats:
                    stats.append(stat.stat_string)
            if prop3 is not None:
                for stat in prop3.stats:
                    stats.append(stat.stat_string)
            stat_string = "<br>".join(stats)

            item_types = []
            for index in range(26, 33):
                if affix[index] != "":
                    item_types.append(affix[index])

            affixes.append(Affix(affix[0], affix[3], affix[4], affix[5], affix[6], affix[10], stat_string, item_types))
        return affixes

    def get_prefixes(self):
        return self.get_affixes(self.tables.prefixes_table)

    def get_suffixes(self):
        return self.get_affixes(self.tables.suffixes_table)
