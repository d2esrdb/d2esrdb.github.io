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
        self.runeword_table = self.load_table("Runes.txt")
        self.socketables_table = self.load_table("Gems.txt")
        self.sets_table = self.load_table("Sets.txt")
        self.set_items_table = self.load_table("SetItems.txt")
        self.char_stats_table = self.load_table("CharStats.txt")
        self.player_class_table = self.load_table("PlayerClass.txt")

        # For efficiency sake we should just build this dict once
        self.parent_types = {}
        for t in self.item_types_table:
            if t["Code"] == "":
                continue
            self.parent_types[t["Code"]] = [t["Code"]]
            self.add_code_to_type(t["Equiv1"], t["Code"])
            self.add_code_to_type(t["Equiv2"], t["Code"])
            self.parent_types[t["Code"]] = set(self.parent_types[t["Code"]])

        self.sub_types = {}
        for t in self.item_types_table:
            if t["Code"] == "":
                continue
            self.sub_types[t["Code"]] = [t["Code"]]
            self.add_sub_codes_to_type(t["Code"], t["Code"])
            self.sub_types[t["Code"]] = set(self.sub_types[t["Code"]])

    def add_sub_codes_to_type(self, code, t):
        if code == "":
            return
        for _type in self.item_types_table:
            if _type["Equiv1"] == code:
                self.sub_types[t].append(_type["Code"])
                self.add_sub_codes_to_type(_type["Code"], t)
            if _type["Equiv2"] == code:
                self.sub_types[t].append(_type["Code"])
                self.add_sub_codes_to_type(_type["Code"], t)

    def add_code_to_type(self, code, t):
        if code == "":
            return
        self.parent_types[t].append(code)
        for _type in self.item_types_table:
            if _type["Code"] == code:
                self.add_code_to_type(_type["Equiv1"], t)
                self.add_code_to_type(_type["Equiv2"], t)

    def load_table(self, table_name):
        table_file = open("../" + self.db_name + "/" + table_name, newline='')
        table = csv.reader(table_file, delimiter='\t')
        fieldnames = []
        for headername in next(table):
            if headername not in fieldnames:
                fieldnames.append(headername)
            else:
                print("Warning: Duplicate column \"" + headername + "\" detected. Renaming second one to " + headername + "2. (this is normal for mindam and maxdam)")
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
    
    def print_row_with_cell_not_equal_to(self, table_name, cell_name, value):
        table = self.load_table(table_name)
        first = None
        for i, row in enumerate(table):
            if i == 0:
                first = row
            if row[cell_name] != value:
                print(row[cell_name])
                #for i, col in enumerate(first):
                #    print(str(i) + ": " + col + ": " + row[col])


class Node:
    def __init__(self, code):
        self.code = code
        self.children = []
    
    def addchild(self, child):
        self.children.append(child)

def fillsubtype(node):
    if node.code == "":
        return
    
    #print("filling subtype: " + node.code)
    for itemtype in mytables.item_types_table:
        if itemtype["Equiv1"] == node.code or itemtype["Equiv2"] == node.code:
            child = Node(itemtype["Code"])
            node.addchild(child)
            fillsubtype(child)

def printtree(node, indent):
    if node.code is None:
        return
    print(indent + node.code)
    for child in node.children:
        printtree(child, indent + "  ")

def printItemTypesTree():
    mytables = Tables("ESE")
    root = Node(None)
    for itemtype in mytables.item_types_table:
        if itemtype["Equiv1"] == "":
            root.addchild(Node(itemtype["Code"]))
    for child in root.children:
        fillsubtype(child)
    for child in root.children:
        printtree(child, "")

if __name__ == "__main__":
    mytables = Tables("LOD")
    #mytables.print_row_with_cell_not_equal_to("Misc.txt", "spelldescstr", "")
    mytables.print_row_with_cell_equal_to("ItemStatCost.txt", "Stat", "firemindam")
    #mytables.print_row_with_cell_equal_to("Properties.txt", "code", "dmg-fire")
    #mytables.print_row_with_cell_equal_to("UniqueItems.txt", "code", "dmg-fire")

    #for armor in mytables.armor_table:
    #    if armor["type"] in mytables.sub_types["tors"] or armor["type2"] in mytables.sub_types["tors"]:
    #        print(armor["name"] + ": " + armor["gemapplytype"]) 
    #mytables.print_row_with_cell_equal_to("Properties.txt", "code", "fire-multi")
    #mytables.print_row_with_cell_equal_to("ItemStatCost.txt", "Stat", "fire_multi")
    #for key in mytables.sub_types:
    #    print(key + ": " + str(mytables.sub_types[key]))






