import os
import csv
from re import I

class Tables:
    def __init__(self, db_name):
        self.include_header = False
        self.db_name = db_name
        self.weapons_table = self.load_table("Weapons.txt")
        self.armor_table = self.load_table("Armor.txt")
        self.skills_table = self.load_table("Skills.txt")
        self.skill_desc_table = self.load_table("SkillDesc.txt")
        self.unique_items_table = self.load_table("UniqueItems.txt")
        self.properties_table = self.load_table("Properties.txt")
        self.item_stat_cost_table = self.load_table("ItemStatCost.txt")
        self.item_types_table = self.load_table("ItemTypes.txt")
        self.misc_table = self.load_table("Misc.txt")
        self.mon_stats_table = self.load_table("MonStats.txt")
        self.automagic_table = self.load_table("automagic.txt")
        self.prefixes_table = self.load_table("MagicPrefix.txt")
        self.suffixes_table = self.load_table("MagicSuffix.txt")
        self.gamble_table = self.load_table("gamble.txt")

    def load_table(self, table_name):
        table = open("../" + self.db_name + "/" + table_name, newline='')
        if self.include_header:
            return list(csv.reader(table, delimiter='\t'))
        return list(csv.reader(table, delimiter='\t'))[1:]

    def print_table_headers(self, table_name):
        first = None
        for i, row in enumerate(table_name):
            if i == 0:
                first = row
        for i, col in enumerate(first):
            print(str(i) + ": " + col)

    def print_row_with_cell_equal_to(self, table_name, cell_index, value):
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
