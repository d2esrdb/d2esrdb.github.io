import os
import csv
from db_config import *
from re import I

include_header = False

def load_table(table_name):
    table = open(PROJECT_DIR + table_name, newline='')
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

def print_table_headers(table_name):
    first = None
    for i, row in enumerate(table_name):
        if i == 0:
            first = row
    for i, col in enumerate(first):
        print(str(i) + ": " + col)

def print_row_with_cell_equal_to(table_name, cell_index, value):
    first = None
    for i, row in enumerate(table_name):
        if i == 0:
            first = row
        if row[cell_index] == value:
            for i, col in enumerate(first):
                print(str(i) + ": " + col + ": " + row[i])



#print_row_with_cell_equal_to(properties_table, 0, "all-stats")
#print_row_with_cell_equal_to(unique_items_table, 0, "The Bishop")
#print_row_with_cell_equal_to(unique_items_table, 0, "Soulstone")
#print_row_with_cell_equal_to(misc_table, 0, "Grand Charm4")
#print_row_with_cell_equal_to(armor_table, 0, "Robe")
#print_table_headers(armor_table)
