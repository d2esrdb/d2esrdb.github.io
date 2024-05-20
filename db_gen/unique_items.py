from enum import unique
from operator import attrgetter
from utils import *
import os
from table_strings import *
import load_txts

def get_unique_items(tables, mod_strings):
    unique_items = []
    for row in tables.unique_items_table:
        # If item is enabled... for some reason we have to use rarity??
        if row["rarity"].isdigit() and int(row["rarity"]) > 0:
            properties = []
            for j in range(12):
                # If the property doesn't have a name, then there isn't a property
                if row["prop" + str(j+1)] != "":
                    properties.append(Property(row["prop" + str(j+1)], row["par" + str(j+1)], row["min" + str(j+1)], row["max" + str(j+1)]))
            unique_items.append(Item(row["index"], row["lvl"], row["lvl req"], properties, row["code"], mod_strings, tables))
    
    return unique_items
