from enum import unique
from operator import attrgetter
from utils import *
import os
from table_strings import *
import load_txts

def get_unique_items():
    unique_items = []
    for i, row in enumerate(load_txts.unique_items_table):
        # If item is enabled
        if row[4].isdigit() and int(row[4]) > 0:
            properties = []
            for j in range(12):
                # If the property doesn't have a name, then there isn't a property
                if row[21+j*4] != "":
                    properties.append(Property(row[21+j*4], row[22+j*4], row[23+j*4], row[24+j*4]))
            unique_items.append(Item(row[0], row[6], row[7], properties, row[8]))
    
    return unique_items
