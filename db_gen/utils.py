import stat_formats
import properties

class Utils:
    def __init__(self, tables, table_strings):
        self.table_strings = table_strings
        self.tables = tables
        self.log_errors = []

    def log(self, msg):
        if msg not in self.log_errors:
            self.log_errors.append(msg)

    def get_item_types_list(self, types):
        ret = []
        for item_type in self.tables.item_types_table:
            for t in types:
                if t == item_type["Code"]:
                    ret.append(item_type["Code"] + " = " + item_type["ItemType"])
        return ret
            
    def is_in_gamble_table(self, code):
        for row in self.tables.gamble_table:
            if row["code"] == code:
                return True
        return False

    def get_gamble_item_from_code(self, code):
        for row in self.tables.armor_table:
            if row["code"] == code and row["spawnable"] == str(1):
                for row_again in self.tables.armor_table:
                    if row_again["code"] != "" and row_again["code"] == row["normcode"] and self.is_in_gamble_table(row_again["code"]):
                        return self.get_item_name_from_code(row_again["code"]) + " (" + row_again["code"] + ")"
        for row in self.tables.weapons_table:
            if row["code"] == code and row["spawnable"] == str(1):
                for row_again in self.tables.weapons_table:
                    if row_again["code"] != "" and row_again["code"] == row["normcode"] and self.is_in_gamble_table(row_again["code"]):
                        return self.get_item_name_from_code(row_again["code"]) + " (" + row_again["code"] + ")"
        for row in self.tables.misc_table:
            if row["code"] != "" and row["code"] == code and row["spawnable"] == str(1) and self.is_in_gamble_table(row["code"]):
                return self.get_item_name_from_code(row["code"]) + " (" + row["code"] + ")"
        return "N/A"

    def get_all_equivalent_types(self, types):
        while True:
            keep_going = False
            for item_type in self.tables.item_types_table:
                if item_type["Code"] in types:
                    if item_type["Equiv1"] not in types:
                        types.append(item_type["Equiv1"])
                        keep_going = True
                    if item_type["Equiv2"] not in types:
                        types.append(item_type["Equiv2"])
                        keep_going = True
            if not keep_going:
                types.remove("")
                return types

    def is_of_item_type(self, types, include_types):
        # Build up a list of all types, then check if any of them are in include_types
        all_types = self.get_all_equivalent_types(types)
        return set(all_types) & set(include_types)

    def get_item_name_from_code(self, code):
        for row in self.tables.armor_table + self.tables.weapons_table + self.tables.misc_table:
            if row["code"] == code:
                if self.table_strings.get(row["namestr"]) is not None:
                    return self.table_strings[row["namestr"]]
        self.log("No name found for code: " + code)
        return code
    
    def get_level_req_from_code(self, code):
        for row in self.tables.armor_table + self.tables.weapons_table + self.tables.misc_table:
            if row["code"] == code:
                return row["levelreq"]
        self.log("Could not get level req for code: " + code)
        return 0
    
    def get_bg_color_from_code(self, code):
        for item in self.tables.weapons_table + self.tables.armor_table:
            if code == item["ultracode"]:
                return 303030
            if code == item["ubercode"]:
                return 202020
        return 101010


    def get_automods(self, group, type1, type2):
        automods = []
        if group == "":
            return
        for autos in self.tables.automagic_table:
            if group == autos["group"] and self.is_of_item_type([type1, type2], [autos["itype1"], autos["itype2"], autos["itype3"], autos["itype4"], autos["itype5"], autos["itype6"], autos["itype7"]]) and not self.is_of_item_type([type1, type2], [autos["etype1"], autos["etype2"], autos["etype3"]]):
                props = []
                for i in range(3):
                    if autos["mod" + str(i+1) + "code"] != "":
                        props.append(properties.Property(self,
                                                         autos["mod" + str(i+1) + "code"],
                                                         autos["mod" + str(i+1) + "param"],
                                                         autos["mod" + str(i+1) + "min"],
                                                         autos["mod" + str(i+1) + "max"]))
                automods.append(props)
        return automods

    def short_to_long_class(self, class_code):
        for c in self.tables.player_class_table:
            if c["Code"] == class_code:
                return c["Player Class"]
        self.log("Unknown class: " + class_code)
        return "Unknown"

    def get_staffmod(self, code):
        for item in self.tables.armor_table + self.tables.weapons_table + self.tables.misc_table:
            if item["code"] == code:
                for item_type in self.tables.item_types_table:
                    if item_type["Code"] == item["type"] and item_type["StaffMods"] != "":
                        return self.short_to_long_class(item_type["StaffMods"])
        return ""

    def get_spelldesc(self, code):
        for row in self.tables.misc_table:
            if row["code"] == code:
                return self.table_strings.get(row["spelldescstr"], "")

    def get_monster_from_id(self, mon_id):
        for mon_stat_row in self.tables.mon_stats_table:
            if mon_stat_row["hcIdx"] == mon_id:
                return self.table_strings[mon_stat_row["NameStr"]]



    def get_base_url(self, code):
        for weapon in self.tables.weapons_table:
            if weapon["code"] == code:
                return "weapons.htm#" + code
        for armor in self.tables.armor_table:
            if armor["code"] == code:
                return "armors.htm#" + code
        return ""

    def get_item_type_name_from_code(self, code):
        # Hard code "tors" because "Armor" is confusing
        if code == "tors":
            return "Body Armor"

        for row in self.tables.item_types_table:
            if row["Code"] == code:
                return row["ItemType"]

        for row in self.tables.misc_table:
            if row["code"] == code:
                return row["name"]
        return "Unknown: " + code

    def get_all_parent_types(self, types):
        ret = list(types)
        for t in types:
            if t == "":
                continue
            for pt in self.tables.parent_types[t]:
                if pt == "":
                    continue
                ret.append(pt)
        return set(ret)
    
    def get_all_sub_types(self, types):
        ret = list(types)
        for t in types:
            if t == "":
                continue
            for st in self.tables.sub_types[t]:
                if st == "":
                    continue
                ret.append(st)
        return set(ret)


    def get_stat_string(self, properties):
        ret = ""
        all_stats = []
        for prop in properties:
            for stat in prop.stats:
                all_stats.append(stat)

        for stat in sorted(all_stats, key=lambda x: int(x.priority), reverse=True):
            if stat.stat_string != "":
                ret = ret + stat.stat_string + "<br>"
            if stat.stat_string == "" and stat.stat not in ["poisonlength", "coldlength", "state"]:
                self.log("Could not get stat string for stat: " + stat.stat + " property: " + stat.property.code)
        return ret
