from db_gen import properties
from db_gen.tables import Tables
from db_gen.utils import Utils


class Socketable:
    def __init__(self, utils: Utils, name: str, props: list[list[properties.Property]], level_req: str) -> None:
        self.name = name
        self.props = props
        self.utils = utils
        self.level_req = level_req

    def stats_string(self, gemapplytype: int) -> str:
        return self.utils.get_stat_string(self.props[gemapplytype])


class SocketablesGenerator:
    def __init__(self, tables: Tables, table_strings: dict[str, str], utils: Utils) -> None:
        self.tables = tables
        self.table_strings = table_strings
        self.utils = utils

    def generate_socketables(self) -> list:
        ret = []
        for socketable in self.tables.socketables_table:
            if socketable["code"] == "":
                continue
            name = self.utils.get_item_name_from_code(socketable["code"])
            level_req = self.utils.get_level_req_from_code(socketable["code"])
            props = [[], [], []]
            for i, socket_type in enumerate(["weapon", "helm", "shield"]):
                for j in range(3):
                    if socketable[socket_type + "Mod" + str(j + 1) + "Code"] != "":
                        props[i].append(
                            properties.Property(
                                self.utils,
                                socketable[socket_type + "Mod" + str(j + 1) + "Code"],
                                socketable[socket_type + "Mod" + str(j + 1) + "Param"],
                                socketable[socket_type + "Mod" + str(j + 1) + "Min"],
                                socketable[socket_type + "Mod" + str(j + 1) + "Max"],
                            ),
                        )
            ret.append(Socketable(self.utils, name, props, level_req))
        return ret
