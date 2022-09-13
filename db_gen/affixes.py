import unique_items
import stat_formats
import load_txts
import table_strings

mod_strings = table_strings.mod_strings

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

def get_value_string(min, max):
    min = str(min)
    max = str(max)
    if min == "" and max == "":
        return "NOVALUE"
    if min == "":
        return max
    if max == "":
        return min
    if min == max:
        return min
    return min + "-" + max

def get_group_prop(property):
    groups = {}
    # Make a dict of lists, containing the dgrp and the associated stats
    for i, row in enumerate(load_txts.item_stat_cost_table):
        if row[45] != "":
            if row[45] in groups:
                tmp = groups[row[45]]
                tmp.append(row[0])
                groups[row[45]] = tmp
            else:
                groups[row[45]] = [row[0]]
    
    item_group_stats = {}
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
                prop = unique_items.Property("Group Property", param, min, max)
                prop.stats.append(unique_items.Stat("Group Stat", stat_formats.get_stat_string1(int(func), unique_items.get_value_string(param, min, max), unique_items.mod_strings.get(string1, "NONE"), unique_items.mod_strings.get(string2, "NONE")), priority))
                return prop

    unique_items.handle_hardcoded_groups(property)
    return property

def get_affixes(table):
    affixes = []
    for i, affix in enumerate(table):
        if affix[2] != str(1):
            continue
        prop1 = unique_items.Property(affix[12], affix[13], affix[14], affix[15])
        unique_items.fill_property_stats(prop1)
        prop1 = get_group_prop(prop1)
        prop2 = None
        prop3 = None
        if affix[16] != "":
            prop2 = unique_items.Property(affix[16], affix[17], affix[18], affix[19])
            unique_items.fill_property_stats(prop2)
            prop2 = get_group_prop(prop2)
        if affix[20] != "":
            prop3 = unique_items.Property(affix[20], affix[21], affix[22], affix[23])
            unique_items.fill_property_stats(prop3)
            prop3 = get_group_prop(prop3)
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

def get_prefixes():
    return get_affixes(load_txts.prefixes_table)

def get_suffixes():
    return get_affixes(load_txts.suffixes_table)