from db_gen import properties
from db_gen.utils import Utils


class Set:
    def __init__(
        self,
        utils: Utils,
        name: str,
        items: list["SetItem"],
        partial_bonus_properties: list[list[properties.Property]],
        full_bonus_properties: list[properties.Property],
    ) -> None:
        self.utils = utils
        self.name = name
        self.items = items
        self.partial_bonus_properties = partial_bonus_properties
        self.full_bonus_properties = full_bonus_properties

    def partial_stats_string(self) -> str:
        ret = ""
        for i, props in enumerate(self.partial_bonus_properties):
            if len(props) != 0:
                ret = ret + self.utils.get_stat_string(props)
                ret = ret + "(" + str(i + 2) + " items)<br><br>"
        while ret[-4:] == "<br>":
            ret = ret[:-4]
        return ret

    def full_stats_string(self) -> str:
        return self.utils.get_stat_string(self.full_bonus_properties)


class SetItem:
    def __init__(
        self,
        utils: Utils,
        name: str,
        base_code: str,
        base_name: str,
        gamble_string: str,
        required_level: str,
        level: str,
        item_properties: list[properties.Property],
        bonus_properties: list[list[properties.Property]],
        base_url: str,
    ) -> None:
        self.utils = utils
        self.name = name
        self.base_code = base_code
        self.base_name = base_name
        self.required_level = required_level
        self.level = level
        self.item_properties = item_properties
        self.bonus_properties = bonus_properties
        self.gamble_item_string = gamble_string
        self.base_url = base_url

    def stats_string(self) -> str:
        return self.utils.get_stat_string(self.item_properties)

    def bonus_stats_string(self) -> str:
        ret = ""
        for i, props in enumerate(self.bonus_properties):
            if len(props) != 0:
                ret = ret + self.utils.get_stat_string(props)
                ret = ret + "(" + str(i + 2) + " items)<br><br>"
        while ret[-4:] == "<br>":
            ret = ret[:-4]
        return ret


class SetGenerator:
    def __init__(self, utils: Utils) -> None:
        self.utils = utils

    def generate_sets(self) -> list[Set]:
        sets = []
        for _set in self.utils.tables.sets_table:
            if _set["name"] == "":
                continue
            name = self.utils.table_strings[_set["name"]]
            partial_properties = [[], [], [], []]
            for i in range(4):
                if _set["PCode" + str(i + 2) + "a"] != "":
                    partial_properties[i].append(
                        properties.Property(
                            self.utils,
                            _set["PCode" + str(i + 2) + "a"],
                            _set["PParam" + str(i + 2) + "a"],
                            _set["PMin" + str(i + 2) + "a"],
                            _set["PMax" + str(i + 2) + "a"],
                        ),
                    )
                if _set["PCode" + str(i + 2) + "b"] != "":
                    partial_properties[i].append(
                        properties.Property(
                            self.utils,
                            _set["PCode" + str(i + 2) + "b"],
                            _set["PParam" + str(i + 2) + "b"],
                            _set["PMin" + str(i + 2) + "b"],
                            _set["PMax" + str(i + 2) + "b"],
                        ),
                    )

            full_properties = [
                properties.Property(
                    self.utils,
                    _set["FCode" + str(i + 1)],
                    _set["FParam" + str(i + 1)],
                    _set["FMin" + str(i + 1)],
                    _set["FMax" + str(i + 1)],
                )
                for i in range(8)
                if _set["FCode" + str(i + 1)] != ""
            ]
            items = []
            for item in self.utils.tables.set_items_table:
                if item["set"] == _set["index"]:
                    item_name = self.utils.table_strings[item["index"]]
                    item_base_code = item["item"]
                    item_base_name = self.utils.get_item_name_from_code(item_base_code)
                    item_required_level = item["lvl req"]
                    item_level = item["lvl"]
                    item_partial_properties = [[], [], [], [], []]
                    for i in range(5):
                        if item["aprop" + str(i + 1) + "a"] != "":
                            item_partial_properties[i].append(
                                properties.Property(
                                    self.utils,
                                    item["aprop" + str(i + 1) + "a"],
                                    item["apar" + str(i + 1) + "a"],
                                    item["amin" + str(i + 1) + "a"],
                                    item["amax" + str(i + 1) + "a"],
                                ),
                            )
                        if item["aprop" + str(i + 1) + "b"] != "":
                            item_partial_properties[i].append(
                                properties.Property(
                                    self.utils,
                                    item["aprop" + str(i + 1) + "b"],
                                    item["apar" + str(i + 1) + "b"],
                                    item["amin" + str(i + 1) + "b"],
                                    item["amax" + str(i + 1) + "b"],
                                ),
                            )
                    item_properties = [
                        properties.Property(
                            self.utils,
                            item["prop" + str(i + 1)],
                            item["par" + str(i + 1)],
                            item["min" + str(i + 1)],
                            item["max" + str(i + 1)],
                        )
                        for i in range(9)
                        if item["prop" + str(i + 1)] != ""
                    ]

                    gamble_string = self.utils.get_gamble_item_from_code(item_base_code)
                    items.append(
                        SetItem(
                            self.utils,
                            item_name,
                            item_base_code,
                            item_base_name,
                            gamble_string,
                            item_required_level,
                            item_level,
                            item_properties,
                            item_partial_properties,
                            self.utils.get_base_url(item_base_code),
                        ),
                    )
            sets.append(
                Set(self.utils, name, items, partial_properties, full_properties),
            )
        return sets
