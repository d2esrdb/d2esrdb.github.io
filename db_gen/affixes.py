import load_txts
import unique_items

class Affix:
    def __init__(self, name, rare, level, required_level, rarity, stat_string, item_types):
        self.name = name
        self.rare = rare
        self.level = level
        self.required_level = required_level
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

def get_affixes(table):
    affixes = []
    for i, affix in enumerate(table):
        if i == 0 or affix[2] != str(1):
            continue
        prop1 = unique_items.Property(affix[12], affix[13], affix[14], affix[15])
        unique_items.fill_property_stats(prop1)
        prop2 = None
        prop3 = None
        if affix[16] != "":
            prop2 = unique_items.Property(affix[16], affix[17], affix[18], affix[19])
            unique_items.fill_property_stats(prop2)
        if affix[20] != "":
            prop3 = unique_items.Property(affix[20], affix[21], affix[22], affix[23])
            unique_items.fill_property_stats(prop3)
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

        affixes.append(Affix(affix[0], affix[3], get_value_string(affix[4], affix[5]), affix[6], affix[10], stat_string, item_types))
    return affixes

def get_prefixes():
    return get_affixes(load_txts.prefixes_table)

def get_suffixes():
    return get_affixes(load_txts.suffixes_table)