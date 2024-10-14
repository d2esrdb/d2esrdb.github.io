import csv
from pathlib import Path

from db_gen import logger


class Tables:
    def __init__(self, db_dir: Path, db_name: str) -> None:
        self.db_dir = db_dir
        self.include_header = False
        self.db_name = db_name
        self.weapons_table = self.load_table("Weapons.txt")
        self.armor_table = self.load_table("Armor.txt")
        self.skills_table = self.load_table("Skills.txt")
        self.skill_desc_table = self.load_table("SkillDesc.txt")
        self.unique_items_table = self.load_table("UniqueItems.txt")
        self.properties_table = self.load_table("Properties.txt")
        self.properties_dict = self.table_to_dict(self.properties_table, "code", lower=True)
        self.item_stat_cost_table = self.load_table("ItemStatCost.txt")
        self.item_stat_cost_dict = self.table_to_dict(self.item_stat_cost_table, "Stat", lower=True)
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
        self.recipes_table = self.load_table("CubeMain.txt")

        # For efficiency sake we should just build this dict once
        self.parent_types: dict[str, list[str]] = {}
        for t in self.item_types_table:
            if t["Code"] == "":
                continue
            self.parent_types[t["Code"]] = [t["Code"]]
            self.add_code_to_type(t["Equiv1"], t["Code"])
            self.add_code_to_type(t["Equiv2"], t["Code"])
            self.parent_types[t["Code"]] = list(set(self.parent_types[t["Code"]]))

        self.sub_types = {}
        for t in self.item_types_table:
            if t["Code"] == "":
                continue
            self.sub_types[t["Code"]] = [t["Code"]]
            self.add_sub_codes_to_type(t["Code"], t["Code"])
            self.sub_types[t["Code"]] = set(self.sub_types[t["Code"]])

    def add_sub_codes_to_type(self, code: str, t: str) -> None:
        if code == "":
            return
        for _type in self.item_types_table:
            if _type["Equiv1"] == code:
                self.sub_types[t].append(_type["Code"])
                self.add_sub_codes_to_type(_type["Code"], t)
            if _type["Equiv2"] == code:
                self.sub_types[t].append(_type["Code"])
                self.add_sub_codes_to_type(_type["Code"], t)

    def add_code_to_type(self, code: str, t: str) -> None:
        if code == "":
            return
        self.parent_types[t].append(code)
        for _type in self.item_types_table:
            if _type["Code"] == code:
                self.add_code_to_type(_type["Equiv1"], t)
                self.add_code_to_type(_type["Equiv2"], t)

    def load_table(self, table_name: str) -> list[dict[str, str]]:
        table_file = (self.db_dir / self.db_name / table_name).open(
            newline="",
            errors="ignore",
        )
        table_reader = csv.reader(table_file, delimiter="\t")
        fieldnames = []
        for headername in next(table_reader):
            if headername not in fieldnames:
                fieldnames.append(headername)
            else:
                logger.warning(
                    'Duplicate column "'
                    + headername
                    + '" detected. Renaming second one to '
                    + headername
                    + "2. (this is normal for mindam and maxdam)",
                )
                fieldnames.append(headername + "2")
        table: list[dict[str, str]] = list(csv.DictReader(table_file, fieldnames=fieldnames, delimiter="\t"))
        for row in table:
            # Avoid repeated lower() calls for select properties
            for key in ("skill", "Id", "skilldesc"):
                row[f"_l{key}"] = row.get(key, "").lower()
        return table

    @staticmethod
    def table_to_dict(
        table: list[dict[str, str]], unique_key: str, *, lower: bool = False
    ) -> dict[str, dict[str, str]]:
        if lower:
            return {r[unique_key].lower(): r for r in table}
        return {r[unique_key]: r for r in table}


class Node:
    def __init__(self, code: str) -> None:
        self.code = code
        self.children = []

    def addchild(self, child: "Node") -> None:
        self.children.append(child)
