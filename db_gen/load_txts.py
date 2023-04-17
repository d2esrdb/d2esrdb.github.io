import os
import csv
from re import I

include_header = False
data_path = ""
for root, dirs, files in os.walk("../"):
    if "Data" in dirs:
        data_path = os.path.join(root, "Data")

def load_table(table_name):
    table = open(data_path + "/global/excel/" + table_name, newline='')
    if include_header:
        return list(csv.reader(table, delimiter='\t'))
    return list(csv.reader(table, delimiter='\t'))[1:]

# For debugging
if __name__ == "__main__":
    include_header = True

weapons_table = load_table("Weapons.txt")
armor_table = load_table("Armor.txt")
skills_table = load_table("Skills.txt")
skill_desc_table = load_table("SkillDesc.txt")
unique_items_table = load_table("UniqueItems.txt")
properties_table = load_table("Properties.txt")
item_stat_cost_table = load_table("ItemStatCost.txt")
item_types_table = load_table("ItemTypes.txt")
misc_table = load_table("Misc.txt")
mon_stats_table = load_table("MonStats.txt")
automagic_table = load_table("automagic.txt")
prefixes_table = load_table("MagicPrefix.txt")
suffixes_table = load_table("MagicSuffix.txt")
gamble_table = load_table("gamble.txt")

#descstrs = set()
#first = None
#for i, row in enumerate(misc_table):
#    if i == 0:
#        first = row
#    if row[64] != "":
#        descstrs.add(row[64])
#print(descstrs)
#import table_strings
#for dstr in descstrs:
    #print(table_strings.mod_strings[dstr])
#for i, row in enumerate(first):
#    print(row + ": " + second[i] + str(i))

