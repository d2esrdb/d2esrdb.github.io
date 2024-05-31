import utils

class Socketable:
    def __init__(self, name, properties):
        self.name = name
        self.properties = properties
    
    def stats_string(self, gemapplytype):
        ret = ""
        allstats = []
        for prop in self.properties[gemapplytype]:
            for stat in prop.stats:
                allstats.append(stat)
        for stat in sorted(allstats, key=lambda x: int(x.priority)):
            ret = ret + stat.stat_string + "<br>"
        return ret

class Socketables_Generator:
    def __init__(self, tables, table_strings, utils):
        self.tables = tables
        self.table_strings = table_strings
        self.utils = utils

    def generate_socketables(self):
        ret = []
        for socketable in self.tables.socketables_table:
            if socketable["code"] == "":
                continue
            name = self.utils.get_item_name_from_code(socketable["code"])
            properties = [[], [], []]
            for i, socket_type in enumerate(["weapon", "helm", "shield"]):
                for j in range(3):
                    if socketable[socket_type + "Mod" + str(j+1) + "Code"] != "":
                        properties[i].append(utils.Property(socketable[socket_type + "Mod" + str(j+1) + "Code"],
                                                            socketable[socket_type + "Mod" + str(j+1) + "Param"],
                                                            socketable[socket_type + "Mod" + str(j+1) + "Min"],
                                                            socketable[socket_type + "Mod" + str(j+1) + "Max"]))
            for i in range(3):            
                for p in properties[i]:
                    self.utils.fill_property_stats(p)
                self.utils.fill_group_stats(properties[i])
            ret.append(Socketable(name, properties))
        return ret



