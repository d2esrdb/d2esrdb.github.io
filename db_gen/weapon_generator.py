import operator
import utils

class Weapon_Generator:
    def __init__(self, tables, table_strings, utils):
        self.tables = tables
        self.table_strings = table_strings
        self.utils = utils
    
    def replace_if_empty(self, string, replacement):
        if string == "":
            return replacement
        return string

    def get_avg(self, mindam, maxdam):
        ret = ""
        if mindam != "":
            ret = str(round((float(mindam) + float(maxdam)/2.0), 1)) + " Avg"
        return ret
    
    def get_dmg(self, mindam, maxdam):
        ret = ""
        if mindam != "":
            ret = str(mindam) + " to " + str(maxdam)
        return ret

    def generate_weapons(self):
        normal_weapons = []
        exceptional_weapons = []
        elite_weapons = []
        for weapon_row in self.tables.weapons_table:
            for item_type_row in self.tables.item_types_table:
                if weapon_row["type"] == item_type_row["Code"] and weapon_row["type"] != "":
                    item = utils.Item(weapon_row["namestr"], 1, weapon_row["levelreq"], [], weapon_row["code"], self.table_strings, self.tables)
                    automods = []
                    for p in item.properties:
                        if p.is_automod:
                            for s in p.stats:
                                automods.append(s.stat_string)
                    weapon = [self.table_strings.get(weapon_row["namestr"], weapon_row["name"]), #0: name
                             item_type_row["ItemType"],  #1: category
                             weapon_row["levelreq"],     #2: req_level
                             weapon_row["code"],         #3: code
                             weapon_row["normcode"],     #4: norm_code
                             weapon_row["ubercode"],     #5: exceptional_code
                             weapon_row["ultracode"],    #6: elite code                           
                             self.get_dmg(weapon_row["mindam"], weapon_row["maxdam"]), #7
                             self.get_avg(weapon_row["mindam"], weapon_row["maxdam"]), #8
                             self.get_dmg(weapon_row["2handmindam"], weapon_row["2handmaxdam"]), #9
                             self.get_avg(weapon_row["2handmindam"], weapon_row["2handmaxdam"]), #10
                             self.get_dmg(weapon_row["minmisdam"], weapon_row["maxmisdam"]), #11
                             self.get_avg(weapon_row["minmisdam"], weapon_row["maxmisdam"]), #12
                             weapon_row["rangeadder"],   #13: range
                             weapon_row["durability"],   #14: durability
                             weapon_row["speed"],        #15: wsm?
                             weapon_row["level"],        #16: qlvl
                             weapon_row["magic lvl"],    #17: mag lvl
                             weapon_row["reqstr"],       #18: req str
                             weapon_row["reqdex"],       #19: req dex
                             self.replace_if_empty(weapon_row["StrBonus"], 0), #20: str bonus
                             self.replace_if_empty(weapon_row["DexBonus"], 0), #21: dex bonus
                             weapon_row["gemsockets"],   #22: sock
                             weapon_row["gemapplytype"], #23: gem_type
                             self.utils.string_array_to_html(automods, 1), #24: automods
                             item.staffmod,              #25: staffmods
                            ]
                    if weapon_row["normcode"] == weapon_row["code"]:
                        normal_weapons.append(weapon)
                    if weapon_row["ubercode"] == weapon_row["code"]:
                        exceptional_weapons.append(weapon)
                    if weapon_row["ultracode"] == weapon_row["code"]:
                        elite_weapons.append(weapon)

        # First sort normal weapons by level req
        normal_weapons.sort(key = operator.itemgetter(2))

        weapons = list(normal_weapons)
        # Now append exceptional weapons in order
        for normal_weapon in list(normal_weapons):
            for exceptional_weapon in list(exceptional_weapons):
                if normal_weapon[5] == exceptional_weapon[3]:
                    weapons.append(exceptional_weapon)
                    exceptional_weapons.remove(exceptional_weapon)
                    break

        # Now append elite weapons in order
        for normal_weapon in list(normal_weapons):
            for elite_weapon in list(elite_weapons):
                if normal_weapon[6] == elite_weapon[3]:
                    weapons.append(elite_weapon)
                    elite_weapons.remove(elite_weapon)
                    break

        for exceptional_weapon in exceptional_weapons:
            weapons.append(exceptional_weapon)
            self.utils.log("Error: Exceptional weapon " + exceptional_weapon[0] + " could not find corresponding Normal weapon.")
        for elite_weapon in elite_weapons:
            self.utils.log("Error: Elite weapon " + elite_weapon[0] + " could not find corresponding Normal weapon.")
            weapons.append(elite_weapon)
        return weapons
