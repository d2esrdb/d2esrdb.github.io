import utils
import properties

class Stat:
    def __init__(self, stat, set, val, func, prop):
        self.stat = stat
        self.set = set
        self.val = val
        self.func = func
        self.priority = 0
        self.stat_string = ""
        self.property = prop

class Property:
    def __init__(self, utils, code, param, min, max):
        self.utils = utils
        self.code = code
        self.param = param
        self.min = min
        self.max = max
        self.stats = []

        for p in self.utils.tables.properties_table:
            if p["code"].lower() == code.lower():
                for i in range(1,8):
                    if p["stat" + str(i)] != "":
                        self.stats.append(Stat(p["stat" + str(i)],
                                               p["set" + str(i)],
                                               p["val" + str(i)],
                                               p["func" + str(i)],
                                               self))
        
        # Special handling for properties with hardcoded stats
        if code == "dmg-min":
            self.stats.append(Stat("mindamage", "", "", "5", self))
        if code == "dmg-max":
            self.stats.append(Stat("maxdamage", "", "", "6", self))
        if code == "dmg%":
            stat = Stat("", "", "", "7", self)
            stat.priority = 1000
            stat.stat_string = "+" + self.get_property_value_string(stat) + "% " + self.get_descstr("strModEnhancedDamage") 
            self.stats.append(stat)
        if code == "indestruct":
            self.stats.append(Stat("item_indesctructible", "", "", "20", self))    
        if code == "fear":
            stat = Stat("", "", "", "7", self)
            stat.priority = 1000
            stat.stat_string = "Hit Causes Monster to Flee " + self.get_property_value_string(stat) + "%" 
            self.stats.append(stat)
        if code == "ethereal":
            stat = Stat("", "", "", "0", self)
            stat.priority = 1000
            stat.stat_string = "Ethereal (Cannot be Repaired)" 
            self.stats.append(stat)
            
        for stat in self.stats:
            for isc in self.utils.tables.item_stat_cost_table:
                if isc["Stat"].lower() == stat.stat.lower():
                    if isc["descpriority"] != "":
                        stat.priority = int(isc["descpriority"])
                    stat.stat_string = self.get_stat_string(stat, isc)


        if len(self.stats) == 0:
            self.utils.log("No stats for property: " + code)

    def strmin(self, v1, v2):
        if v1 == "":
            return v2
        if v2 == "":
            return v1
        return str(min(int(v1), int(v2)))

    def strmax(self, v1,  v2):
        if v1 == "":
            return v2
        if v2 == "":
            return v1
        return str(max(int(v1), int(v2)))
    
    def get_property_value_string(self, stat):
        # @TODO Figure out if we need to treat empty min/max or even param columns as zeros?
        match stat.func:
            case "1" | "3" | "5" | "6" | "7" | "8" | "9" | "10" | "22" | "24":
                if self.min == self.max:
                    return self.min
                return "(" + self.strmin(self.min, self.max) + " to " + self.strmax(self.min, self.max) + ")"
            case "2" | "4" | "16":
                return self.max
            case "12":
                return self.param
            case "14":
                if self.min != "" and self.min == self.max:
                    return "(" + self.min + ")"
                if self.min != "" or self.max != "":
                    return "(" + self.strmin(self.min, self.max) + " to " + self.strmax(self.min, self.max) + ")"
                return "(" + self.param + ")"
            case "15":
                return self.min
            case "17":
                if self.param != "":
                    return self.param
                if self.min == "" and self.max == "":
                    return "0"
                if self.min == "":
                    return "(" + self.strmin(0, self.max) + " to " + self.strmax(0, self.max) + ")"
                if self.max == "":
                    return "(" + self.strmin(self.min, 0) + " to " + self.strmax(self.min, 0) + ")"
                if self.min == self.max:
                    return self.min
                return "(" + self.strmin(self.min, self.max) + " to " + self.strmax(self.min, self.max) + ")"
            case "21":
                # @TODO this is actually dangerous because you need to ensure you call get_property_value_string before you use param...
                self.param = stat.val
                if self.min == self.max:
                    return self.min
                return "(" + self.strmin(self.min, self.max) + " to " + self.strmax(self.min, self.max) + ")"
            case "36":
                return stat.val
            case _:
                self.utils.log("Could not get property value string for stat " + stat.stat + " func " + stat.func)
                return "UNKNOWN PROPERTY STAT FUNC " + stat.func
               
    def is_always_negative(self):
        if self.min != "" and int(self.min) < 0 and self.max != "" and int(self.max) < 0:
            return True
        return False
    
    def get_skilltab_descstr_from_param(self, param):
        skilltabs = []
        classes = []
        for row in self.utils.tables.char_stats_table:
            if row["StrSkillTab1"] != "":
                skilltabs.append(row["StrSkillTab1"])
                classes.append(row["class"])
            if row["StrSkillTab2"] != "":
                skilltabs.append(row["StrSkillTab2"])
                classes.append(row["class"])
            if row["StrSkillTab3"] != "":
                skilltabs.append(row["StrSkillTab3"])
                classes.append(row["class"])
        return skilltabs[int(param)], classes[int(param)]
    
    def get_allskills_descstr_from_class_number(self, class_number):
        i = 0
        for pc in self.utils.tables.player_class_table:
            if pc["Code"] == "":
                continue
            if str(i) == class_number:
                for cs in self.utils.tables.char_stats_table:
                    if pc["Player Class"] == cs["class"]:
                        return cs["StrAllSkills"]
            i = i + 1
        self.utils.log("Did not find allskillstr for class: " + class_number)
        return "Unknown class"
    

    def get_descstr(self, descstr):
        if descstr == "":
            return ""
        if "NOT FOUND" == self.utils.table_strings.get(descstr, "NOT FOUND"):
            self.utils.log("No descstr found for: " + descstr + " property:" + self.code)
            return descstr
        return self.utils.table_strings[descstr]

    def get_skill_name_from_skill_id(self, skill_id):
        for s in self.utils.tables.skills_table:
            if s["skill"].lower() == skill_id.lower() or s["Id"].lower() == skill_id.lower():
                for sd in self.utils.tables.skill_desc_table:
                    if sd["skilldesc"].lower() == s["skilldesc"].lower():
                        return self.utils.table_strings[sd["str name"]]
        self.utils.log("get skill name failed for skill id: " + skill_id)
        return "Unknown Skill"
    
    def get_class_name_from_skill_id(self, skill_id):
        for s in self.utils.tables.skills_table:
            if s["skill"].lower() == skill_id.lower() or s["Id"].lower() == skill_id.lower():
                for pc in self.utils.tables.player_class_table:
                    if pc["Code"] == s["charclass"]:
                        return pc["Player Class"]
        self.utils.log("get class failed for skill id: " + skill_id)
        return "Unknown Class"
    
    def get_classonly_from_skill_id(self, skill_id):
        for s in self.utils.tables.skills_table:
            if s["skill"].lower() == skill_id.lower() or s["Id"].lower() == skill_id.lower():
                for pc in self.utils.tables.player_class_table:
                    if pc["Code"] == s["charclass"]:
                        for cs in self.utils.tables.char_stats_table:
                            if pc["Player Class"] == cs["class"]:
                                if self.utils.table_strings.get(cs["StrClassOnly"], None) == None:
                                    self.utils.log("Skill: " + s["skill"] + " is not assigned to a class. (Class Only) stat doesn't make sense. Setting to Unassigned")
                                return self.utils.table_strings.get(cs["StrClassOnly"],"(Unassigned Only)")
        self.utils.log("get classonly failed for skill id: " + skill_id)
        return "(Unknown Only)"

    def get_stat_string0(self, stat, isc, descstr):
        match isc["descfunc"]:
            case "0" | "":
                # Just return what it's already set to, which is either "" or some hard-coded thing set previously
                return stat.stat_string
            case "1" | "2" | "3" | "4" | "5" | "12" | "20" | "25" | "26":
                return descstr
            case "6" | "7" | "8" | "9" | "10":
                return descstr + " " + self.get_descstr(isc["descstr2"])
            case "11":
                # @TODO ESR/d2smallutility changes repair to replenish/frames and doesn't do the param calc?
                # Also official docs say ModStre9t but ESE ESR and LOD seem to use 9u?
                # Also do we always use 1 in the first %d?
                if "frame" in self.get_descstr("ModStre9t").lower():
                    return self.get_descstr("ModStre9u").replace("%d", "1", 1).replace("%d", self.param, 1)
                return self.get_descstr("ModStre9u").replace("%d", "1", 1).replace("%d", str(int(100/int(self.param))), 1)
            case "14":
                # @TODO this doesn't seem quite right.. do we really manually append (class only)? can probably do it like 27 below
                descstr, _class = self.get_skilltab_descstr_from_param(self.param)
                return self.get_descstr(descstr).replace("%d", self.get_property_value_string(stat)) + " (" + _class + " Only)" 
            case "15":
                return descstr.replace("%d%", self.min, 1).replace("%d", self.max, 1).replace("%s", self.get_skill_name_from_skill_id(self.param), 1)
            case "16":
                return descstr.replace("%d", self.get_property_value_string(stat), 1).replace("%s", self.get_skill_name_from_skill_id(self.param), 1)
            case "19":
                return descstr.replace("%d%", self.get_property_value_string(stat), 1) + " " + self.get_descstr(isc["descstr2"])
            case "24":
                return "Level " + self.max + " " + self.get_skill_name_from_skill_id(self.param) + " " + descstr.replace("%d", self.min)
            case "27":
                if stat.func == "12":
                    _class = self.get_class_name_from_skill_id(self.min)
                    classOnly = self.get_classonly_from_skill_id(self.min)
                    #@TODO this isn't quite right... technically you could have a rand-skill across multiple class ranges... maybe need to investigate a dropdown or something
                    return "+" + self.param + " To Random " + _class + " Skill " + classOnly
                skill = self.get_skill_name_from_skill_id(self.param)
                classonly = self.get_classonly_from_skill_id(self.param)
                return "+" + self.get_property_value_string(stat) + " To " + skill + " " + classonly
            case "28":
                return "+" + self.get_property_value_string(stat) + " To " + self.get_skill_name_from_skill_id(self.param)
            case _:
                self.utils.log("descfunc" + isc["descfunc"] + " descval 0 not implemented (stat " + stat.stat + ")")
                return "descfunc" + isc["descfunc"] + " descval 0 not implemented"
    
    def get_stat_string1(self, stat, isc, descstr):
        match isc["descfunc"]:
            case "0" | "":
                # Just return what it's already set to, which is either "" or some hard-coded thing set previously
                return stat.stat_string
            case "1":
                return "+" + self.get_property_value_string(stat) + " " + descstr
            case "2":
                return self.get_property_value_string(stat) + "% " + descstr
            case "3":
                return self.get_property_value_string(stat) + " " + descstr
            case "4":
                return "+" + self.get_property_value_string(stat) + "% " + descstr
            case "6":
                return "+" + self.get_property_value_string(stat) + " " + descstr + " " + self.get_descstr(isc["descstr2"])
            case "7":
                return self.get_property_value_string(stat) + "% " + descstr + " " + self.get_descstr(isc["descstr2"])
            case "8":
                return "+" + self.get_property_value_string(stat) + "% " + descstr + " " + self.get_descstr(isc["descstr2"])
            case "13":
                # Not great... 
                if stat.func == "36":
                    return "+" + self.get_property_value_string(stat) + " to Random Class Skill Levels"
                return "+" + self.get_property_value_string(stat) + " " + self.get_descstr(self.get_allskills_descstr_from_class_number(self.param))
            case "20":
                return "-" + self.get_property_value_string(stat) + "% " + descstr
            case "23":
                return self.get_property_value_string(stat) + "% " + descstr + " " + self.utils.get_monster_from_id(self.param)
            case _:
                self.utils.log("descfunc" + isc["descfunc"] + " descval 1 not implemented (stat " + stat.stat + ")")
                return "descfunc" + isc["descfunc"] + " descval 1 not implemented"
    
    def get_stat_string2(self, stat, isc, descstr):
        match isc["descfunc"]:
            case "0" | "":
                # Just return what it's already set to, which is either "" or some hard-coded thing set previously
                return stat.stat_string
            case "1":
                return descstr + " +" + self.get_property_value_string(stat)
            case "2":
                return descstr + " " + self.get_property_value_string(stat) + "%"
            case "3":
                return descstr + " " + self.get_property_value_string(stat)
            case "4":
                return descstr + " +" + self.get_property_value_string(stat) + "%"
            case "5":
                #“+[value * 100 / 128]% [descstr]”
                if self.min != "":
                    self.min = str(int(int(self.min) * 100 / 128))
                if self.max != "":
                    self.max = str(int(int(self.max) * 100 / 128))
                if self.param != "":
                    self.param = str(int(int(self.param) * 100 / 128))
                return descstr + " " + self.get_property_value_string(stat) + "%"
            case "7":
                return descstr + " " + self.get_property_value_string(stat) + "% " + self.get_descstr(isc["descstr2"])
            case "8":
                return descstr + " +" + self.get_property_value_string(stat) + "% " + self.get_descstr(isc["descstr2"])
            case "9":
                return descstr + " " + self.get_property_value_string(stat) + " " + self.get_descstr(isc["descstr2"])
            case "12":
                 #@TODO vidalas full set just says freezes target but this says freezes target +1
                 return descstr + " +" + self.get_property_value_string(stat)
            case _:
                self.utils.log("descfunc" + isc["descfunc"] + " descval 2 not implemented (stat " + stat.stat + ")")
                return "descfunc" + isc["descfunc"] + " descval 2 not implemented"

    #@TODO remove
    def handle_hardcoded(self, stat):
        if stat.stat == "firemindam" and any(s.stat == "firemaxdam" for s in self.stats):
            for s in self.stats:
                if s.stat == "firemaxdam":
                    return True, self.utils.table_strings["strModFireDamageRange"].replace("%d", self.min, 1).replace("%d", s.max, 1) 
        if stat.stat == "firemaxdam":
            for s in self.stats:
                if s.stat == "firemindam":
                    return True, self.utils.table_strings["strModFireDamageRange"].replace("%d", s.min, 1).replace("%d", self.max, 1) 
        return False, None
        if stat.stat == "lightmindam" and any(s.stat == "lightmaxdam"):
            return True
        if stat.stat == "magicmindam" and any(s.stat == "magicmaxdam"):
            return True
        if stat.stat == "coldmindam" and any(s.stat == "coldmaxdam"):
            return True
        if stat.stat == "poisonmindam" and any(s.stat == "poisonmaxdam"):
            return True
        if stat.stat == "mindamage" and any(s.stat == "maxdamage"):
            return True
        return False, None

    def get_stat_string(self, stat, isc):
        # Special handling for hardcoded nonsense...
        if stat.stat == "item_numsockets":
            return self.get_descstr("Socketable") + " " + self.get_property_value_string(stat) 
        
        descstr = self.get_descstr(isc["descstrpos"])
        # Since we only display the stats range and don't actually roll for it, it's possible for
        # a stat to have negative and positive range, so we'll always use the positive one unless
        # the stat is always negative
        if self.is_always_negative():
            descstr = self.get_descstr(isc["descstrneg"])

        if isc["descval"] == "" or isc["descval"] == "0":
            return self.get_stat_string0(stat, isc, descstr)
        if isc["descval"] == "1":
            return self.get_stat_string1(stat, isc, descstr)
        if isc["descval"] == "2":
            return self.get_stat_string2(stat, isc, descstr)
        self.utils.log("invalid descval: " + isc["descval"] + " for stat: " + stat.stat + " property: " + self.code)
        return "invalid descval: " + isc["descval"]

        return ret
