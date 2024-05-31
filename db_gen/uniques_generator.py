import utils 

class Item_Group:
    def __init__(self, name):
        self.name = name
        self.items = []

class Uniques_Generator():
    def __init__(self, tables, table_strings, utils):
        self.tables = tables
        self.table_strings = table_strings
        self.utils = utils
        self.unique_weapons = None
        self.unique_armors = None
        self.unique_misc = None
        # Fills in the above 3 items
        self.generate_uniques()
    
    def get_weapon_types(self):
        weapon_types = []
        for weapon in self.tables.weapons_table:
            if weapon["type"] not in weapon_types:
                weapon_types.append(weapon["type"])
        return weapon_types
    
    def get_other_types(self, remaining_items):
        other_types = []
        for item in remaining_items:
            if item.base_code not in other_types:
                other_types.append(item.base_code)
        return other_types

    def get_armor_types(self):
        armor_types = []
        for armor in self.tables.armor_table:
            if armor["type"] not in armor_types:
                armor_types.append(armor["type"])
        return armor_types

    def weapon_is_a_subtype_of(self, subtype_code, maintype_code):
        for weapon in self.tables.weapons_table:
            if weapon["code"] == subtype_code and maintype_code == weapon["type"]:
                return True
        return False

    def armor_is_of_type(self, item_code, armor_code):
        for row in self.tables.armor_table:
            if row["code"] == item_code and armor_code == row["type"]:
                return True
        return False

    def set_weapon_bg_color(self, item):
        for weapon in self.tables.weapons_table:
            if item.base_code == weapon["ultracode"]:
                item.bg_color_code = 303030
                return
            if item.base_code == weapon["ubercode"]:
                item.bg_color_code = 202020
                return

    def set_armor_bg_color(self, item):
        for armor in self.tables.armor_table:
            if item.base_code == armor["ultracode"]:
                item.bg_color_code = 303030
                return
            if item.base_code == armor["ubercode"]:
                item.bg_color_code = 202020
                return

    def get_unique_weapons(self):
        return self.unique_weapons

    def get_unique_armors(self):
        return self.unique_armors

    def get_unique_misc(self):
        return self.unique_misc

    def generate_uniques(self):
        all_uniques = self.get_unique_items()
        weapons_groups = []
        for weapon_type in self.get_weapon_types():
            weapon_group = Item_Group(self.utils.get_item_type_name_from_code(weapon_type))
            for item in list(all_uniques):
                if self.weapon_is_a_subtype_of(item.base_code, weapon_type):
                    self.set_weapon_bg_color(item)
                    weapon_group.items.append(item)
                    all_uniques.remove(item)
            if len(weapon_group.items) > 0:
                weapons_groups.append(weapon_group)
        self.unique_weapons = weapons_groups
        
        item_groups = []
        for armor_type in self.get_armor_types():
            armor_group = Item_Group(self.utils.get_item_type_name_from_code(armor_type))
            for item in list(all_uniques):
                if self.armor_is_of_type(item.base_code, armor_type):
                    self.set_armor_bg_color(item)
                    armor_group.items.append(item)
                    all_uniques.remove(item)
            if len(armor_group.items) > 0:
                item_groups.append(armor_group)
        self.unique_armors = item_groups

        item_groups = []
        for other_type in self.get_other_types(all_uniques):
            others = Item_Group(self.utils.get_item_type_name_from_code(other_type))
            for item in list(all_uniques):
                if item.base_code == other_type:
                    others.items.append(item)
                    others.items.sort(key = lambda x: (int(x.item_level), int(x.required_level)))
                    all_uniques.remove(item)
            item_groups.append(others)
        self.unique_misc = item_groups

        if len(all_uniques) != 0:
            print("Could not find group for unique item: " + str(all_uniques))


        

    def get_unique_items(self):
        unique_items = []
        for row in self.tables.unique_items_table:
            # @TODO If item is enabled... for some reason we have to use rarity?? Maybe this is only an ES thing? I feel like this should be removed...
            if row["rarity"].isdigit() and int(row["rarity"]) > 0:
                properties = []
                for j in range(12):
                    if row["prop" + str(j+1)] != "":
                        properties.append(utils.Property(row["prop" + str(j+1)], row["par" + str(j+1)], row["min" + str(j+1)], row["max" + str(j+1)]))
                unique_items.append(utils.Item(row["index"], row["lvl"], row["lvl req"], properties, row["code"], self.table_strings, self.tables, False))
        
        return unique_items
