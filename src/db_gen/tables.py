import csv
from pathlib import Path

if __name__ != "__main__":
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
        table_path = next((self.db_dir / self.db_name).glob(table_name, case_sensitive=False))
        table_file = table_path.open(
            newline="",
            errors="ignore",
        )
        table_reader = csv.reader(table_file, delimiter="\t")
        fieldnames = []
        for headername in next(table_reader):
            if headername not in fieldnames:
                fieldnames.append(headername)
            else:
                if __name__ != "__main__":
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

    def print_table_headers(self, table_name):
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
    def __init__(self, code: str) -> None:
        self.code = code
        self.children = []

    def addchild(self, child: "Node") -> None:
        self.children.append(child)

if __name__ == "__main__":
    myt = Tables(Path("../../data/"), "Eastern_Sun_Resurrected")
    myt.print_row_with_cell_equal_to("ItemStatCost.txt", "Stat", "item_addclassskills")
    print("")
    myt.print_row_with_cell_equal_to("Properties.txt", "code", "randclassskill")
    print("")
    myt.print_row_with_cell_equal_to("UniqueItems.txt", "index", "Hellfire Torch")
