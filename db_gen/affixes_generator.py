import stat_formats
import utils

class Affix:
    def __init__(self, name, rare, level, max_level, required_level, rarity, stat_string, item_types, exclude_types):
        self.name = name
        self.rare = rare
        self.level = level
        self.required_level = required_level
        self.max_level = max_level
        self.rarity = rarity
        self.stat_string = stat_string
        self.item_types = item_types
        self.exclude_types = exclude_types
        self.item_types_string = ", ".join(item_types)
        if len(exclude_types) != 0:
            self.item_types_string = self.item_types_string + "<br><br>Excluding:<br>" + ", ".join(exclude_types)

class Affix_Generator:
    def __init__(self, tables, mod_strings, utils):
        self.tables = tables
        self.mod_strings = mod_strings
        self.stat_formats = stat_formats.Stat_Formats(tables, mod_strings)
        self.utils = utils

    def get_group_prop(self, property):
        groups = {}
        # Make a dict of lists, containing the dgrp and the associated stats
        for row in self.tables.item_stat_cost_table:
            if row["dgrp"] != "":
                if row["dgrp"] in groups:
                    tmp = groups[row["dgrp"]]
                    tmp.append(row["Stat"])
                    groups[row["dgrp"]] = tmp
                else:
                    groups[row["dgrp"]] = [row["Stat"]]
        
        item_group_stats = {}
        for stat in property.stats:
            for row in self.tables.item_stat_cost_table:
                # If there is a group text for this mod
                if stat.name == row["Stat"] and row["dgrp"] != "":
                    item_group_stats[row["Stat"]] = [property.param, property.min, property.max, row["descpriority"], row["dgrpfunc"], row["dgrpstrpos"], row["dgrpstr2"], property]

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
                    prop = utils.Property("Group Property", param, min, max)
                    prop.stats.append(utils.Stat("Group Stat", self.stat_formats.get_stat_string1(int(func), self.utils.get_value_string(param, min, max), self.mod_strings.get(string1, "NONE"), param, min, max, self.mod_strings.get(string2, "NONE")), priority))
                    return prop

        self.utils.handle_hardcoded_groups(property)
        return property

    def get_affixes(self, table):
        affixes = []
        for affix in table:
            if affix["spawnable"] != str(1):
                continue
            prop1 = utils.Property(affix["mod1code"], affix["mod1param"], affix["mod1min"], affix["mod1max"])
            self.utils.fill_property_stats(prop1)
            prop1 = self.get_group_prop(prop1)
            prop2 = None
            prop3 = None
            if affix["mod2code"] != "":
                prop2 = utils.Property(affix["mod2code"], affix["mod2param"], affix["mod2min"], affix["mod2max"])
                self.utils.fill_property_stats(prop2)
                prop2 = self.get_group_prop(prop2)
            if affix["mod3code"] != "":
                prop3 = utils.Property(affix["mod3code"], affix["mod3param"], affix["mod3min"], affix["mod3max"])
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
            for i in range(7):
                if affix["itype" + str(i+1)] != "":
                    item_types.append(affix["itype" + str(i+1)])
            
            exclude_types = []
            for i in range(5):
                # prefixes have 5 columns for exclude types but suffix only has 3 #smart
                try:
                    if affix["etype" + str(i+1)] != "":
                        exclude_types.append(affix["etype" + str(i+1)])
                except:
                    pass

            affixes.append(Affix(affix["Name"], affix["rare"], affix["level"], affix["maxlevel"], affix["levelreq"], affix["frequency"], stat_string, item_types, exclude_types))
        return affixes

    def get_prefixes(self):
        return self.get_affixes(self.tables.prefixes_table)

    def get_suffixes(self):
        return self.get_affixes(self.tables.suffixes_table)
