# One of the following functions are called, depending on descval
# Strings from https://d2mods.info/forum/kb/viewarticle?a=448
import re

class Stat_Formats:
    def __init__(self, tables, mod_strings):
        self.tables = tables
        self.mod_strings = mod_strings

    def get_monster_from_id(self, mon_id):
        for mon_stat_row in self.tables.mon_stats_table:
            if mon_stat_row["hcIdx"] == mon_id:
                return self.mod_strings[mon_stat_row["NameStr"]]

    def get_value_string(self, param, min, max):
        if param != "":
            return param
        
        if min == "" and max == "":
            return "NOVALUE"

        if min == "":
            return max

        if max == "":
            return min

        if min == max:
            return min
            
        return min + "-" + max

    # No value (descval 0)
    def get_stat_string0(self, descfunc, string1, param, min, max, string2=None, _class=None, skilltab=None, chance=None, slvl=None, skill=None, event=None, time=None, monster=None):
        match descfunc:
            case 1:
                return string1
            case 2:
                return string1
            case 3:
                return string1
            case 4:
                return string1
            case 5:
                return string1
            case 6:
                return string1 + " " + string2
            case 7:
                return string1 + " " + string2
            case 8:
                return string1 + " " + string2
            case 9:
                return string1 + " " + string2 
            case 10:
                return string1 + " " + string2
            case 11:
                # Greasy hack for d2smallutility that changes the default repair string that has 1 %d to replenish per frame with two %d but the first one is hard-coded to 1?
                if string1.count("%d") == 2:
                    return string1.replace("%d", "1", 1).replace("%d", param) 
                return "Repairs 1 Durability In " + str(int(100/int(param))) + " Seconds"
            case 12:
                return string1
            case 13:
                # ???
                return "to " + _class + " Skill Levels"
            case 14:
                return "+" + " to " + skilltab + " Skill Levels (" + _class + " Only)"
            case 15:
                return chance + "% to cast Level " + slvl + " " + skill + " on " + event
            case 16:
                #return "AURAS NOT IMPLEMENTED YET"
                return "Level " + slvl + " " + skill + " Aura When Equipped"
            case 17:
                return string1 + " (Increases near " + time + ")"
            case 18:
                return string1 + " (Increases near " + time + ")"
            case 19:
                #TODO this won't handle all cases
                return re.sub(r'%\S*', self.get_value_string(param, min, max), string1, count=1)
            case 20:
                return string1
            case 21:
                return string1
            case 22:
                return "Apparently this format string is bugged"
            case 23:
                return string1 + " " + monster
            case 24:
                return "gotta figure out charges string"
            case 25:
                return "we don't know what 25 looks like"
            case 26:
                return "we don't know what 26 looks like"
            case 27:
                # ???
                return "to " + skill + " (" + _class + " Only)"
            case 28:
                # ???
                return "to " + skill
        return "Invalid descfunc: " + descfunc + " descval: 0"

    # Value comes before string (descval 1)
    def get_stat_string1(self, descfunc, value, string1, param, min, max, string2=None, _class=None, skilltab=None, chance=None, slvl=None, skill=None, event=None, time=None, monster=None):
        value = str(value)
        match descfunc:
            case 1:
                if value.startswith("-"):
                    return value + " " + string1
                return "+" + value + " " + string1
            case 2:
                return value + "% " + string1
            case 3:
                return value + " " + string1
            case 4:
                return "+" + value + "% " + string1
            case 5:
                return str(int(value)*100/128) + "% " + string1
            case 6:
                return "+" + value + " " + string1 + " " + string2
            case 7:
                return value + "%" + " " + string1 + " " + string2
            case 8:
                return "+" + value + "% " + string1 + " " + string2
            case 9:
                return value + " " + string1 + " " + string2 
            case 10:
                return str(int(value*100/128)) + "%" + string1 + " " + string2
            case 11:
                # Greasy hack for d2smallutility that changes the default repair string that has 1 %d to replenish per frame with two %d but the first one is hard-coded to 1?
                if string1.count("%d") == 2:
                    return string1.replace("%d", "1", 1).replace("%d", param) 
                return "Repairs 1 Durability In " + str(int(100/int(param))) + " Seconds"
            case 12:
                return "+" + value + " " + string1
            case 13:
                #return "CLASS SKILL LEVELS NOT IMPLEMENTED YET"
                return "+" + value + " to " + _class + " Skill Levels"
            case 14:
                return "+" + " to " + skilltab + " Skill Levels (" + _class + " Only)"
            case 15:
                return chance + "% to cast Level " + slvl + " " + skill + " on " + event
            case 16:
                return "Level " + slvl + " " + skill + " Aura When Equipped"
            case 17:
                return value + " " + string1 + " (Increases near " + time + ")"
            case 18:
                return value + "% " + string1 + " (Increases near " + time + ")"
            case 19:
                #TODO this won't handle all cases
                return re.sub(r'%\S*', self.get_value_string(param, min, max), string1, count=1)
            case 20:
                if "-" in value:
                    return "-(" + value + ")% " + string1
                return str(int(value) * -1) + "% " + string1
            case 21:
                return str(int(value) * -1) + " " + string1
            case 22:
                return "Apparently this format string is bugged"
            case 23:
                return self.get_value_string("", min, max) + "% " + string1 + " " + self.get_monster_from_id(param)
            case 24:
                return "gotta figure out charges string"
            case 25:
                return "we don't know what 25 looks like"
            case 26:
                return "we don't know what 26 looks like"
            case 27:
                return "+" + value + " to " + skill + " (" + _class + " Only)"
            case 28:
                return "+" + value + " to " + skill
        return "Invalid descfunc: " + descfunc + " descval: 1"

    # Value comes after string (descval 2)
    def get_stat_string2(self, descfunc, value, string1, param, min, max, string2=None, _class=None, skilltab=None, chance=None, slvl=None, skill=None, event=None, time=None, monster=None):
        value = str(value)
        match descfunc:
            case 1:
                if value.startswith("-"):
                    return value + " " + string1
                return string1 + " +" + value
            case 2:
                return string1 + " " + value + "%"
            case 3:
                return string1 + " " + value
            case 4:
                if value.startswith("-"):
                    return string1 + " " + value + "%"
                return string1 + " +" + value + "%" 
            case 5:
                # @TODO this would be cleaner if we took in min/max/param instead of value
                #-10--5 (both numbers negative)
                if str(value).count("-") == 3:
                    min,max = value.replace("--"," ").replace("-","").split(" ")
                    return string1 + " -" + str(int(int(min)*100/128)) + "--" + str(int(int(max)*100/128)) + "%"
                #-10-5 (one number negative)
                if str(value).count("-") == 2:
                    min,max = value.replace("-"," ").strip().split(" ")
                    return string1 + " -" + str(int(int(min)*100/128)) + "-" + str(int(int(max)*100/128)) + "%"
                #5-10 (both numbers positive)
                if str(value).count("-") == 1:
                    min,max = value.replace("-"," ").split(" ")
                    return string1 + str(int(int(min)*100/128)) + "-" + str(int(int(max)*100/128)) + "%"
                return string1 + " " + str(int(int(value)*100/128)) + "%"
            case 6:
                return string1 + " " + string2 + " +" + value
            case 7:
                return string1 + " " + value + "% " + string2
            case 8:
                return string1 + " +" + value + "% " + string2
            case 9:
                return string1 + " " + value + " " + string2
            case 10:
                return string1 + " " + str(int(value*100/128)) + "% " + string2
            case 11:
                # Greasy hack for d2smallutility that changes the default repair string that has 1 %d to replenish per frame with two %d but the first one is hard-coded to 1?
                if string1.count("%d") == 2:
                    return string1.replace("%d", "1", 1).replace("%d", param) 
                return "Repairs 1 Durability In " + str(int(100/int(param))) + " Seconds"
            case 12:
                return string1 + " +" + value
            case 13:
                # same as 1?
                return "+" + value + " to " + _class + " Skill Levels"
            case 14:
                # same as 1?
                return "+" + " to " + skilltab + " Skill Levels (" + _class + " Only)"
            case 15:
                # same as 1?
                return chance + "% to cast Level " + slvl + " " + skill + " on " + event
            case 16:
                # same as 1?
                return "Level " + slvl + " " + skill + " Aura When Equipped"
            case 17:
                return string1 + " " + value + " (Increases near " + time + ")"
            case 18:
                return string1 + " " + value + "% (Increases near " + time + ")"
            case 19:
                #TODO this won't handle all cases
                return re.sub(r'%\S*', self.get_value_string(param, min, max), string1, count=1)
            case 20:
                if "-" in value:
                    return string1 + " -(" + value + ")%"
                return string1 + " " + str(int(value) * -1) + "%"
            case 21:
                return string1 + " " + str(int(value) * -1) 
            case 22:
                return "Apparently this format string is bugged"
            case 23:
                return string1 + " " + value + "% " + monster
            case 24:
                return "gotta figure out charges string"
            case 25:
                return "we don't know what 25 looks like"
            case 26:
                return "we don't know what 26 looks like"
            case 27:
                # same as 1?
                return "+" + value + " to " + skill + " (" + _class + " Only)"
            case 28:
                # same as 1?
                return "+" + value + " to " + skill
        return "Invalid descfunc: " + descfunc + " descval: 2"

