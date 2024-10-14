import operator
from logging import WARNING

from db_gen.properties import Property
from db_gen.tables import Tables
from db_gen.utils import Utils


class ArmorGenerator:
    def __init__(self, tables: Tables, table_strings: dict[str, str], utils: Utils) -> None:
        self.tables = tables
        self.table_strings = table_strings
        self.utils = utils

    def automods_string(self, automods: list[list[Property]] | None) -> str:
        if automods is None:
            return ""
        ret = ""
        for automod in automods:
            ret = ret + self.utils.get_stat_string(automod) + "<br>"
        if ret != "":
            return ret[:-4]
        return ret

    def generate_armor(self) -> list[list[str]]:
        normal_armors = []
        exceptional_armors = []
        elite_armors = []
        for armor_row in self.tables.armor_table:
            for item_type_row in self.tables.item_types_table:
                if armor_row["type"] == item_type_row["Code"] and armor_row["type"] != "":
                    armor = [
                        self.table_strings.get(
                            armor_row["namestr"],
                            armor_row["name"],
                        ),  # 0: name
                        item_type_row["ItemType"],  # 1: category
                        armor_row["levelreq"],  # 2: req_level
                        armor_row["code"],  # 3: code
                        armor_row["normcode"],  # 4: norm_code
                        armor_row["ubercode"],  # 5: exceptional_code
                        armor_row["ultracode"],  # 6: elite code
                        armor_row["minac"],  # 7: min defense
                        armor_row["maxac"],  # 8: max defense
                        armor_row["durability"],  # 9: durability
                        armor_row["speed"],  # 10: frw
                        armor_row["level"],  # 11: qlvl
                        armor_row["magic lvl"],  # 12: mag lvl
                        armor_row["reqstr"],  # 13: req str
                        armor_row["block"],  # 14: block
                        armor_row["mindam"],  # 15: min damage
                        armor_row["maxdam"],  # 16: max damage
                        armor_row["gemsockets"],  # 17: sock
                        armor_row["gemapplytype"],  # 18: gem_type
                        self.automods_string(
                            self.utils.get_automods(
                                armor_row["auto prefix"],
                                armor_row["type"],
                                armor_row["type2"],
                            ),
                        ),
                        self.utils.get_staffmod(armor_row["code"]),
                    ]
                    if armor_row["normcode"] == armor_row["code"]:
                        normal_armors.append(armor)
                    if armor_row["ubercode"] == armor_row["code"]:
                        exceptional_armors.append(armor)
                    if armor_row["ultracode"] == armor_row["code"]:
                        elite_armors.append(armor)

        # First sort normal armors by level req
        normal_armors.sort(key=operator.itemgetter(2))

        armors = list(normal_armors)
        # Now append exceptional armors in order
        for normal_armor in normal_armors:
            for exceptional_armor in list(exceptional_armors):
                if normal_armor[5] == exceptional_armor[3]:
                    armors.append(exceptional_armor)
                    exceptional_armors.remove(exceptional_armor)
                    break

        # Now append elite armors in order
        for normal_armor in normal_armors:
            for elite_armor in list(elite_armors):
                if normal_armor[6] == elite_armor[3]:
                    armors.append(elite_armor)
                    elite_armors.remove(elite_armor)
                    break

        for exceptional_armor in exceptional_armors:
            armors.append(exceptional_armor)
            self.utils.log(
                "Exceptional armor " + exceptional_armor[0] + " could not find corresponding Normal armor.",
                level=WARNING,
            )
        for elite_armor in elite_armors:
            self.utils.log(
                "Elite armor " + elite_armor[0] + " could not find corresponding Normal armor.", level=WARNING
            )
            armors.append(elite_armor)
        return armors
