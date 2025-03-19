from db_gen import properties
from db_gen.tables import Tables
from db_gen.utils import Utils


class Runeword:
    def __init__(
        self,
        name: str,
        runes: list[str],
        allowed_bases: list[str],
        excluded_bases: list[str],
        properties: list[properties.Property],
        rune_properties: list[list[properties.Property]],
    ) -> None:
        self.name = name
        self.runes = runes
        self.num_sockets = len(runes)
        self.allowed_bases = allowed_bases
        self.excluded_bases = excluded_bases
        self.properties = properties
        self.rune_properties = rune_properties
        self.gemapplytype = [False, False, False]
        # Keep track of first found valid base for each gemapplytype, add as a comment in html for debugging purposes
        self.types = ["", "", ""]

    def rune_string(self) -> str:
        ret = ""
        for rune in self.runes:
            ret = ret + rune + "<br>"
        return ret

    def bases_string(self) -> str:
        ret = ""
        for base in self.allowed_bases:
            ret = ret + base + "<br>"
        for i, base in enumerate(self.excluded_bases):
            if i == 0:
                ret = ret + "<br>Excluded:<br>"
            ret = ret + base + "<br>"
        return ret

    def stats_string(self) -> str:
        ret = ""
        allstats = []
        for prop in self.properties:
            allstats.extend(prop.stats)
        for stat in sorted(allstats, key=lambda x: int(x.priority), reverse=True):
            ret = ret + stat.stat_string + "<br>"
        return ret

    def rune_stats_string(self, gemapplytype: int) -> str:
        ret = ""
        allstats = []
        for prop in self.rune_properties[gemapplytype]:
            allstats.extend(prop.stats)
        for stat in sorted(allstats, key=lambda x: int(x.priority), reverse=True):
            ret = ret + stat.stat_string + "<br>"
        return ret


class RunewordGenerator:
    def __init__(self, tables: Tables, table_strings: dict[str, str], utils: Utils) -> None:
        self.tables = tables
        self.table_strings = table_strings
        self.utils = utils
        self.items = [
            item
            for item in self.tables.armor_table + self.tables.weapons_table + self.tables.misc_table
            if item["gemapplytype"] != "" and item["hasinv"] == "1"
        ]

    def set_gemapplytypes(self, rw: Runeword, include_types: list[str], exclude_types: list[str]) -> None:
        # Get the intersection of all the armor types and its subtypes and the rw include types and it's subtypes
        intersected_types = self.utils.get_all_sub_types(
            include_types,
        ) - self.utils.get_all_sub_types(exclude_types)
        for item in self.items:
            if int(item["gemsockets"]) >= rw.num_sockets and not rw.gemapplytype[int(item["gemapplytype"])]:
                # If there's even 1 item remaining in the intersected types after removing the exclude types, we have a valid item that can use the rw
                if item["type"] in intersected_types or item["type2"] in intersected_types:
                    rw.gemapplytype[int(item["gemapplytype"])] = True
                    rw.types[int(item["gemapplytype"])] = (
                        rw.types[int(item["gemapplytype"])]
                        + "<br>"
                        + self.table_strings.get(item["namestr"], item["namestr"])
                    )

    def generate_runewords(self) -> list[Runeword]:
        runewords = []
        for rw in self.tables.runeword_table:
            allowed_bases = [
                self.utils.get_item_type_name_from_code(
                    rw["itype" + str(i + 1)],
                )
                for i in range(6)
                if rw["itype" + str(i + 1)] != ""
            ]
            include_types = [rw["itype" + str(i + 1)] for i in range(6) if rw["itype" + str(i + 1)] != ""]

            excluded_bases = [
                self.utils.get_item_type_name_from_code(
                    rw["etype" + str(i + 1)],
                )
                for i in range(3)
                if rw["etype" + str(i + 1)] != ""
            ]
            exclude_types = [rw["etype" + str(i + 1)] for i in range(3) if rw["etype" + str(i + 1)] != ""]

            runes = [
                self.utils.get_item_name_from_code(rw["Rune" + str(i + 1)])
                for i in range(6)
                if rw["Rune" + str(i + 1)] != ""
            ]
            props = [
                properties.Property(
                    self.utils,
                    rw["T1Code" + str(j + 1)],
                    rw["T1Param" + str(j + 1)],
                    rw["T1Min" + str(j + 1)],
                    rw["T1Max" + str(j + 1)],
                )
                for j in range(7)
                if rw["T1Code" + str(j + 1)] != ""
            ]

            rune_properties = [[], [], []]
            for socketable in self.tables.socketables_table:
                for i in range(6):
                    if socketable["code"] == rw["Rune" + str(i + 1)]:
                        for j in range(3):
                            for k, sockettype in enumerate(
                                ["weapon", "helm", "shield"],
                            ):
                                if socketable[sockettype + "Mod" + str(j + 1) + "Code"] != "":
                                    found = False
                                    for p in rune_properties[k]:
                                        if p.code == socketable[sockettype + "Mod" + str(j + 1) + "Code"]:
                                            if p.min != "":
                                                p.min = str(
                                                    int(p.min)
                                                    + int(
                                                        socketable[sockettype + "Mod" + str(j + 1) + "Min"],
                                                    ),
                                                )
                                            if p.max != "":
                                                p.max = str(
                                                    int(p.max)
                                                    + int(
                                                        socketable[sockettype + "Mod" + str(j + 1) + "Max"],
                                                    ),
                                                )
                                            found = True
                                    # @TODO this doesn't actually work, and can't work with the way it's written above, because it doesn't affect "param" and we don't know if we want to "double" param or not
                                    #if not found:
                                    rune_properties[k].append(
                                        properties.Property(
                                            self.utils,
                                            socketable[sockettype + "Mod" + str(j + 1) + "Code"],
                                            socketable[sockettype + "Mod" + str(j + 1) + "Param"],
                                            socketable[sockettype + "Mod" + str(j + 1) + "Min"],
                                            socketable[sockettype + "Mod" + str(j + 1) + "Max"],
                                        ),
                                    )

            
            new_rw = Runeword(
                self.table_strings.get(rw["Name"], rw["Rune Name"]),
                runes,
                allowed_bases,
                excluded_bases,
                props,
                rune_properties,
            )
            self.set_gemapplytypes(new_rw, include_types, exclude_types)
            runewords.append(new_rw)
        return runewords
