from logging import WARNING

from db_gen.tables import Tables
from db_gen.utils import Utils


class Damage:
    def __init__(
        self,
        mindam: str,
        maxdam: str,
        _2handmindam: str,
        _2handmaxdam: str,
        minmisdam: str,
        maxmisdam: str,
    ) -> None:
        self.mindam = mindam
        self.maxdam = maxdam
        self.dam = self.get_dmg(mindam, maxdam)
        self.avg = self.get_avg(mindam, maxdam)
        self._2handmindam = _2handmindam
        self._2handmaxdam = _2handmaxdam
        self._2handdam = self.get_dmg(_2handmindam, _2handmaxdam)
        self._2handavg = self.get_avg(_2handmindam, _2handmaxdam)
        self.minmisdam = minmisdam
        self.maxmisdam = maxmisdam
        self.misdam = self.get_dmg(minmisdam, maxmisdam)
        self.misavg = self.get_avg(minmisdam, maxmisdam)

    def get_avg(self, mindam: str | int, maxdam: str | int) -> str:
        ret = ""
        if mindam != "":
            ret = str(round(((float(mindam) + float(maxdam)) / 2.0), 1)) + " Avg"
        return ret

    def get_dmg(self, mindam: str | int, maxdam: str | int) -> str:
        ret = ""
        if mindam != "":
            ret = str(mindam) + " to " + str(maxdam)
        return ret


class Weapon:
    def __init__(
        self,
        name: str,
        category: str,
        req_level: str,
        code: str,
        norm_code: str,
        exceptional_code: str,
        elite_code: str,
        damage: Damage,
        rangeadder: str,
        durability: str,
        speed: str,
        level: str,
        magic_lvl: str,
        reqstr: str,
        reqdex: str,
        strbonus: str | int,
        dexbonus: str | int,
        gemsockets: str,
        gemapplytype: str,
        automods: list,
        staffmods: str,
    ) -> None:
        self.name = name
        self.category = category
        self.req_level = req_level
        self.code = code
        self.norm_code = norm_code
        self.exceptional_code = exceptional_code
        self.elite_code = elite_code
        self.damage = damage
        self.rangeadder = rangeadder
        self.durability = durability
        self.speed = speed
        self.level = level
        self.magic_lvl = magic_lvl
        self.reqstr = reqstr
        self.reqdex = reqdex
        self.strbonus = strbonus
        self.dexbonus = dexbonus
        self.gemsockets = gemsockets
        self.gemapplytype = gemapplytype
        self.automods = automods
        self.staffmods = staffmods

    def automods_string(self) -> str:
        ret = ""
        if self.automods is None:
            return ""
        for automod in self.automods:
            for p in automod:
                allstats = []
                for stat in p.stats:
                    allstats.append(stat)
                for stat in sorted(
                    allstats,
                    key=lambda x: int(x.priority),
                    reverse=True,
                ):
                    ret = ret + stat.stat_string + "<br>"
            ret = ret + "<br>"
        return ret[:-4]


class WeaponGenerator:
    def __init__(self, tables: Tables, table_strings: dict[str, str], utils: Utils) -> None:
        self.tables = tables
        self.table_strings = table_strings
        self.utils = utils

    def replace_if_empty(self, string: str, replacement: str | int) -> str | int:
        if string == "":
            return replacement
        return string

    def generate_weapons(self) -> list:
        normal_weapons = []
        exceptional_weapons = []
        elite_weapons = []
        for weapon_row in self.tables.weapons_table:
            damage = Damage(
                weapon_row["mindam"],
                weapon_row["maxdam"],
                weapon_row["2handmindam"],
                weapon_row["2handmaxdam"],
                weapon_row["minmisdam"],
                weapon_row["maxmisdam"],
            )
            weapon = Weapon(
                self.table_strings.get(weapon_row["namestr"], weapon_row["name"]),
                self.utils.get_item_type_name_from_code(weapon_row["type"]),
                weapon_row["levelreq"],
                weapon_row["code"],
                weapon_row["normcode"],
                weapon_row["ubercode"],
                weapon_row["ultracode"],
                damage,
                weapon_row["rangeadder"],
                weapon_row["durability"],
                weapon_row["speed"],
                weapon_row["level"],
                weapon_row["magic lvl"],
                weapon_row["reqstr"],
                weapon_row["reqdex"],
                self.replace_if_empty(weapon_row["StrBonus"], 0),
                self.replace_if_empty(weapon_row["DexBonus"], 0),
                weapon_row["gemsockets"],
                weapon_row["gemapplytype"],
                self.utils.get_automods(
                    weapon_row["auto prefix"],
                    weapon_row["type"],
                    weapon_row["type2"],
                ),
                self.utils.get_staffmod(weapon_row["code"]),
            )

            if weapon_row["normcode"] == weapon_row["code"]:
                normal_weapons.append(weapon)
            if weapon_row["ubercode"] == weapon_row["code"]:
                exceptional_weapons.append(weapon)
            if weapon_row["ultracode"] == weapon_row["code"]:
                elite_weapons.append(weapon)

        # First sort normal weapons by level req
        normal_weapons.sort(key=lambda x: x.req_level)

        weapons = list(normal_weapons)
        # Now append exceptional weapons in order
        for normal_weapon in list(normal_weapons):
            for exceptional_weapon in list(exceptional_weapons):
                if normal_weapon.exceptional_code == exceptional_weapon.code:
                    weapons.append(exceptional_weapon)
                    exceptional_weapons.remove(exceptional_weapon)
                    break

        # Now append elite weapons in order
        for normal_weapon in list(normal_weapons):
            for elite_weapon in list(elite_weapons):
                if normal_weapon.elite_code == elite_weapon.code:
                    weapons.append(elite_weapon)
                    elite_weapons.remove(elite_weapon)
                    break

        for exceptional_weapon in exceptional_weapons:
            weapons.append(exceptional_weapon)
            self.utils.log(
                "Exceptional weapon " + exceptional_weapon.name + " could not find corresponding Normal weapon.",
                level=WARNING,
            )
        for elite_weapon in elite_weapons:
            self.utils.log(
                "Elite weapon " + elite_weapon.name + " could not find corresponding Normal weapon.", level=WARNING
            )
            weapons.append(elite_weapon)
        return weapons
