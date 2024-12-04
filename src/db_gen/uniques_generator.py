from collections.abc import Iterable
from logging import ERROR

from db_gen import properties
from db_gen.tables import Tables
from db_gen.utils import Utils


class UniqueItem:
    def __init__(
        self, utils: Utils, namestr: str, lvl: str, req_lvl: str, properties: list[properties.Property], code: str
    ) -> None:
        self.utils = utils
        self.name = utils.table_strings.get(namestr, namestr)
        self.base_name = self.utils.get_item_name_from_code(code)
        self.base_code = code
        self.gamble_item = self.utils.get_gamble_item_from_code(code)
        self.spelldesc = self.utils.get_spelldesc(code)
        self.item_level = lvl
        self.required_level = req_lvl
        self.properties = properties
        self.bg_color_code = self.utils.get_bg_color_from_code(code)


class ItemGroup:
    def __init__(self, name: str) -> None:
        self.name = name
        self.items = []


class UniquesGenerator:
    def __init__(self, tables: Tables, table_strings: dict[str, str], utils: Utils) -> None:
        self.tables = tables
        self.table_strings = table_strings
        self.utils = utils
        self.unique_weapons = []
        self.unique_armors = []
        self.unique_misc = []
        # Fills in the above 3 items
        self.generate_uniques()

    def get_weapon_types(self) -> list:
        weapon_types = []
        for weapon in self.tables.weapons_table:
            if weapon["type"] not in weapon_types:
                weapon_types.append(weapon["type"])
        return weapon_types

    def get_other_types(self, remaining_items: Iterable) -> list:
        other_types = []
        for item in remaining_items:
            if item.base_code not in other_types:
                other_types.append(item.base_code)
        return other_types

    def get_armor_types(self) -> list:
        armor_types = []
        for armor in self.tables.armor_table:
            if armor["type"] not in armor_types:
                armor_types.append(armor["type"])
        return armor_types

    def weapon_is_a_subtype_of(self, subtype_code: str, maintype_code: str) -> bool:
        for weapon in self.tables.weapons_table:
            if weapon["code"] == subtype_code and maintype_code == weapon["type"]:
                return True
        return False

    def armor_is_of_type(self, item_code: str, armor_code: str) -> bool:
        return any(row["code"] == item_code and armor_code == row["type"] for row in self.tables.armor_table)

    def get_unique_weapons(self) -> list[ItemGroup]:
        return self.unique_weapons

    def get_unique_armors(self) -> list[ItemGroup]:
        return self.unique_armors

    def get_unique_misc(self) -> list[ItemGroup]:
        return self.unique_misc

    def generate_uniques(self) -> None:
        all_uniques = self.get_unique_items()
        weapons_groups = []
        for weapon_type in self.get_weapon_types():
            weapon_group = ItemGroup(
                self.utils.get_item_type_name_from_code(weapon_type),
            )
            for item in list(all_uniques):
                if self.weapon_is_a_subtype_of(item.base_code, weapon_type):
                    weapon_group.items.append(item)
                    all_uniques.remove(item)
            if len(weapon_group.items) > 0:
                weapons_groups.append(weapon_group)
        self.unique_weapons = weapons_groups

        item_groups = []
        for armor_type in self.get_armor_types():
            armor_group = ItemGroup(
                self.utils.get_item_type_name_from_code(armor_type),
            )
            for item in list(all_uniques):
                if self.armor_is_of_type(item.base_code, armor_type):
                    armor_group.items.append(item)
                    all_uniques.remove(item)
            if len(armor_group.items) > 0:
                item_groups.append(armor_group)
        self.unique_armors = item_groups

        item_groups = []
        for other_type in self.get_other_types(all_uniques):
            others = ItemGroup(self.utils.get_item_type_name_from_code(other_type))
            for item in list(all_uniques):
                if item.base_code == other_type:
                    others.items.append(item)
                    others.items.sort(
                        key=lambda x: (int(x.item_level), int(x.required_level)),
                    )
                    all_uniques.remove(item)
            item_groups.append(others)
        self.unique_misc = item_groups

        if len(all_uniques) != 0:
            self.utils.log("Could not find group for unique item: " + str(all_uniques), level=ERROR)

    def get_unique_items(self) -> list[UniqueItem]:
        unique_items = []
        for row in self.tables.unique_items_table:
            # @TODO If item is enabled... for some reason we have to use rarity?? Maybe this is only an ES thing? I feel like this should be removed...
            #if row["rarity"].isdigit() and int(row["rarity"]) > 0 and row["enabled"] == "1" and row["code"] != "":
            props = [
                properties.Property(
                    self.utils,
                    row["prop" + str(j + 1)],
                    row["par" + str(j + 1)],
                    row["min" + str(j + 1)],
                    row["max" + str(j + 1)],
                )
                for j in range(12)
                if row["prop" + str(j + 1)] != ""
            ]
            unique_items.append(
                UniqueItem(
                    self.utils,
                    row["index"],
                    row["lvl"],
                    row["lvl req"],
                    props,
                    row["code"],
                ),
            )
        return unique_items
