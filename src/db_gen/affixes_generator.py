from db_gen import properties
from db_gen.tables import Tables
from db_gen.utils import Utils


class Affix:
    def __init__(
        self,
        name: str,
        rare: str,
        level: str,
        max_level: str,
        required_level: str,
        rarity: str,
        stat_string: str,
        item_types: list[str],
        exclude_types: list[str],
        group: str,
    ) -> None:
        self.name = name
        self.rare = rare
        self.level = level
        self.required_level = required_level
        self.max_level = max_level
        self.rarity = rarity
        self.stat_string = stat_string
        self.item_types = item_types
        self.exclude_types = exclude_types
        self.item_types_string = ", ".join(item_types)
        self.group = group
        if len(exclude_types) != 0:
            self.item_types_string = self.item_types_string + "<br><br>Excluding:<br>" + ", ".join(exclude_types)


class AffixGenerator:
    def __init__(self, tables: Tables, mod_strings: dict[str, str], utils: Utils) -> None:
        self.tables = tables
        self.mod_strings = mod_strings
        self.utils = utils

    def get_affixes(self, table: list[dict[str, str]]) -> list[Affix]:
        affixes = []
        for affix in table:
            if affix["spawnable"] != str(1):
                continue
            props = [
                properties.Property(
                    self.utils,
                    affix["mod" + str(i + 1) + "code"],
                    affix["mod" + str(i + 1) + "param"],
                    affix["mod" + str(i + 1) + "min"],
                    affix["mod" + str(i + 1) + "max"],
                )
                for i in range(3)
                if affix["mod" + str(i + 1) + "code"] != ""
            ]

            item_types = [affix["itype" + str(i + 1)] for i in range(7) if affix.get("itype" + str(i + 1), "") != ""]

            exclude_types = [affix["etype" + str(i + 1)] for i in range(5) if affix.get("etype" + str(i + 1), "") != ""]

            affixes.append(
                Affix(
                    affix["Name"],
                    affix["rare"],
                    affix["level"],
                    affix["maxlevel"],
                    affix["levelreq"],
                    affix["frequency"],
                    self.utils.get_stat_string(props),
                    item_types,
                    exclude_types,
                    affix["group"]
                ),
            )
        return sorted(affixes, key=lambda x: x.group, reverse=False)

    def get_prefixes(self) -> list[Affix]:
        return self.get_affixes(self.tables.prefixes_table)

    def get_suffixes(self) -> list[Affix]:
        return self.get_affixes(self.tables.suffixes_table)
