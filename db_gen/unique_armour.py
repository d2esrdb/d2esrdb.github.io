import csv
import strings

mod_strings = strings.get_string_dict()
no_mod_strings = {}

class stat:
    def __init__(self, name):
        self.name = name

class property:
    def __init__(self, name, param, min, max):
        self.name = name
        self.param = param
        self.min = min
        self.max = max
        self.stats = []

class unique_item:
    def __init__(self, name, item_level, required_level, properties):
        self.name = name
        self.item_level = item_level
        self.required_level = required_level
        self.properties = properties

# Get the list of armors
def get_armor_bases():
    armor_list = []
    armors = open('../Data/global/excel/armor.txt', newline='')
    items = csv.reader(armors, delimiter='\t')
    for i, row in enumerate(items):
        armor_list.append(row[0])
    return armor_list

def add_plus(value):
    if value.isdigit() and int(value) >= 0:
        return "+" + str(value)
    return str(value)

def print_item(item):
    print(item.name)
    print("    Item Level: " + item.item_level)
    print("    Required Level: " + item.required_level)
    for property in item.properties:
        #print("    Property: " + property.name)
        #print("        param: " + property.param)
        #print("        min: " + property.min)
        #print("        max: " + property.max)
        for stat in property.stats:
            if (property.param != ""):
                print("    " + add_plus(property.param) + " " + stat.name)
            elif property.min == property.max:
                print("    " + add_plus(property.min) + " " + stat.name)
            else:
                print("    " + add_plus(property.min) + "-" + str(property.max) + " " + stat.name)

def get_unique_items():
    unique_items_table = open('../Data/global/excel/uniqueitems.txt', newline='')
    unique_items_rows = csv.reader(unique_items_table, delimiter='\t')
    unique_items = []
    for i, row in enumerate(unique_items_rows):
        # Ignore header
        if i == 0:
            continue
        # If item is enabled
        if row[4].isdigit() and int(row[4]) > 0:
            properties = []
            for j in range(12):
                # If the property doesn't have a name, then there isn't a property
                if row[21+j*4] != "":
                    properties.append(property(row[21+j*4], row[22+j*4], row[23+j*4], row[24+j*4]))
            unique_items.append(unique_item(row[0], row[6], row[7], properties))
    return unique_items

def get_stat(item_name, stat_name):
    item_stat_cost_table = open('../Data/global/excel/ItemStatCost.txt', newline='')
    item_stat_cost_rows = csv.reader(item_stat_cost_table, delimiter='\t')

    for item_stat_cost_row in item_stat_cost_rows:
        if stat_name == item_stat_cost_row[0]:
            return (mod_strings.get(item_stat_cost_row[42], "") + " " + mod_strings.get(item_stat_cost_row[44], "")).strip()

def get_property_stats(item_name, property):
    properties_table = open('../Data/global/excel/Properties.txt', newline='')
    properties_rows = csv.reader(properties_table, delimiter='\t')
    
    for property_row in properties_rows:
        if property.name == property_row[0]:
            for i in range(7):
                if property_row[5+i*4] != "":
                    name = get_stat(item_name, property_row[5+i*4])
                    if name != "":
                        property.stats.append(stat(name))

def main():
    unique_items = get_unique_items()

    for unique_item in unique_items:
        for property in unique_item.properties:
            get_property_stats(unique_item.name, property)
        print_item(unique_item)
        

#print(mod_strings["healkillStr"])
main()
#print(no_mod_strings)


#items = get_unique_items()
#for item in items:
#    print_item(item)

#print(strings.get_string_dict()["ModStr4s"])

#strings = strings.get_string_dict()
#print(strings["ModStr1j"])
#for string in strings:
#    if "All Resistances" == strings[string]:
#        print(string)