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
        table_file = open("../" + self.db_name + "/" + table_name, newline='')
        table = csv.reader(table_file, delimiter='\t')
        fieldnames = []
        for headername in next(table):
            if headername not in fieldnames:
                fieldnames.append(headername)
            else:
                print("Warning: Duplicate column \"" + headername + "\" detected. Renaming second one to " + headername + "2.")
                fieldnames.append(headername + "2")
        return list(csv.DictReader(table_file, fieldnames=fieldnames, delimiter='\t'))

    def load_table_list(self, table_name):
        table_file = open("../" + self.db_name + "/" + table_name, newline='')
        return list(csv.reader(table_file, delimiter='\t'))
    
    def print_table_headers(self, table_name):
        table = self.load_table_list(table_name)
        first = None
        for i, row in enumerate(table):
            if i == 0:
                first = row
        for i, col in enumerate(first):
            print(str(i) + ": " + col)

    def print_row_with_cell_equal_to_list(self, table_name, cell_index, value):
        table = self.load_table_list(table_name)
        first = None
        for i, row in enumerate(table):
            if i == 0:
                first = row
            if row[cell_index] == value:
                for i, col in enumerate(first):
                    print(str(i) + ": " + col + ": " + row[i])

    def print_row_with_cell_equal_to(self, table_name, cell_name, value):
        table = self.load_table(table_name)
        first = None
        for i, row in enumerate(table):
            if i == 0:
                first = row
            if row[cell_name] == value:
                for i, col in enumerate(first):
                    print(str(i) + ": " + col + ": " + row[col])


if __name__ == "__main__":
    mytables = Tables("ESE")
    mytables.print_row_with_cell_equal_to("Weapons.txt", "name", "Throwing Knife")
