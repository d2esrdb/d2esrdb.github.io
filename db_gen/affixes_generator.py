import stat_formats
import utils
import properties

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

    def get_affixes(self, table):
        affixes = []
        for affix in table:
            if affix["spawnable"] != str(1):
                continue
            props = []
            for i in range(3):
                if affix["mod" + str(i+1) + "code"] != "":
                    props.append(properties.Property(self.utils,
                                                     affix["mod" + str(i+1) + "code"],
                                                     affix["mod" + str(i+1) + "param"],
                                                     affix["mod" + str(i+1) + "min"],
                                                     affix["mod" + str(i+1) + "max"]))

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

            affixes.append(Affix(affix["Name"], affix["rare"], affix["level"], affix["maxlevel"], affix["levelreq"], affix["frequency"], self.utils.get_stat_string(props), item_types, exclude_types))
        return affixes

    def get_prefixes(self):
        return self.get_affixes(self.tables.prefixes_table)

    def get_suffixes(self):
        return self.get_affixes(self.tables.suffixes_table)
