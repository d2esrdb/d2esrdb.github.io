import os
import csv
from re import I
import table_strings
import stat_formats

data_path = ""
for root, dirs, files in os.walk("../"):
    if "Data" in dirs:
        data_path = os.path.join(root, "Data")

def load_table(table_name):
    table = open(data_path + "/global/excel/" + table_name, newline='')
    return list(csv.reader(table, delimiter='\t'))

weapons_table = load_table("Weapons.txt")
armor_table = load_table("Armor.txt")
skills_table = load_table("Skills.txt")
skill_desc_table = load_table("SkillDesc.txt")
unique_items_table = load_table("UniqueItems.txt")
properties_table = load_table("Properties.txt")
item_stat_cost_table = load_table("ItemStatCost.txt")
item_types = load_table("ItemTypes.txt")
misc_table = load_table("Misc.txt")
automagic_table = load_table("automagic.txt")
prefixes_table = load_table("MagicPrefix.txt")
suffixes_table = load_table("MagicSuffix.txt")

'''
first_row = None
for i, stat in enumerate(item_stat_cost_table):
    if i == 0:
        first_row = stat
        #for j, item in enumerate(first_row):
            #print(str(j) + ": " + item)
    if stat[25] != 0 and stat[25] != "" and i != 0 and int(stat[25]) > 5:
        print("name: " + str(stat[0]))
        print("op: " + str(stat[25]))
        print("op param: " + str(stat[26]))
        print("op base: " + str(stat[27]))
        print("op stat1: " + str(stat[28]))
        print("op stat2: " + str(stat[29]))
        print("op stat3: " + str(stat[30]))
'''
#for i, misc in enumerate(misc_table):
#    if i < 5:
#        print(misc[13])
'''
first_row = None
for i, item_type in enumerate(item_types):
    if i == 0:
        first_row = item_type
    if item_type[1] == "ashd":
        for j, element in enumerate(first_row):
            print(str(j) + " " + first_row[j] + ": " + item_type[j])



first_row = None
for i, armor in enumerate(armor_table):
    if i == 0:
        first_row = armor
    if armor[0] == "Sacred Targe":
        for j, element in enumerate(first_row):
            print(str(j) + " " + first_row[j] + ": " + armor[j])



first_row = None
for i, armor in enumerate(automagic_table):
    if i == 0:
        first_row = armor
    if armor[10] == str(304):
        for j, _ in enumerate(first_row):
            print(str(j) + ": " + first_row[j] + ": " + armor[j])
        print("")
        print("")

first_row = None
for i, prefix in enumerate(prefixes_table):
    if i == 0:
        first_row = prefix
    if prefix[3] != str(1):
        print(prefix[0] + ": " + prefix[3]) 

'''
first_row = None
for i, item_stat_cost in enumerate(item_stat_cost_table):
    if i == 0:
        first_row = item_stat_cost
        #for j, column in enumerate(item_stat_cost):
            #print(str(column) + ": " + str(j))
    if item_stat_cost[0] == "item_energy_perkill":
        print("energy")
        for i in range(50):
            print(first_row[i] + ": " + item_stat_cost[i])
    if item_stat_cost[0] == "min_firedmg_per_strength":
        print("fire")
        for i in range(50):
            print(first_row[i] + ": " + item_stat_cost[i])