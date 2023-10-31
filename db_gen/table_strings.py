import os
from db_config import *

# List of string tables to parse. Parsed in order so higher indexed tables
# override lower tables in the case of duplicate strings  
string_tables = [
    "string.tbl",
    "expansionstring.tbl",
    "patchstring.tbl",
#    "ES AlphA.tbl",   
]

def read_bytes(data, num_bytes):
    return int.from_bytes(data.read(num_bytes), byteorder='little')

def read_string(data):
    # @TODO There must be a better way of doing this...
    string_byte = data.read(1).decode("raw_unicode_escape")
    string = ""
    while string_byte != '\0':
        string = string + string_byte
        string_byte = data.read(1).decode("raw_unicode_escape")
    return string

def replace_code_with_color(value, code, color, count):
    if code in value:
        return value.replace(code, "<FONT COLOR=\"" + color + "\">", 1), count+1
    return value, count

def d2_color_to_html_color(value):
    count = 0
    while True:
        start_count = count
        value, count = replace_code_with_color(value, "Ã¿c0", "WHITE", count)
        value, count = replace_code_with_color(value, "Ã¿c1", "RED", count)
        value, count = replace_code_with_color(value, "Ã¿c2", "GREEN", count)
        value, count = replace_code_with_color(value, "Ã¿c3", "BLUE", count)
        value, count = replace_code_with_color(value, "Ã¿c4", "GOLD", count)
        value, count = replace_code_with_color(value, "Ã¿c5", "DARKGRAY", count)
        value, count = replace_code_with_color(value, "Ã¿c6", "BLACK", count)
        value, count = replace_code_with_color(value, "Ã¿c7", "GOLDENROD", count)
        value, count = replace_code_with_color(value, "Ã¿c8", "ORANGE", count)
        value, count = replace_code_with_color(value, "Ã¿c9", "YELLOW", count)
        value, count = replace_code_with_color(value, "Ã¿c:", "GREEN", count)
        value, count = replace_code_with_color(value, "Ã¿c<<", "GREEN", count)
        value, count = replace_code_with_color(value, "Ã¿c;", "PURPLE", count)
        if start_count == count:
            break
    value = value + "</FONT>" * count
    return value

def get_string_dict():
    key_value_dict = {}
    for string_table in string_tables:
        strings = open(PROJECT_DIR + string_table, "rb")

        # HEADER 21 bytes
        read_bytes(strings, 2) # CRC, ignored
        num_elements = read_bytes(strings, 2)
        read_bytes(strings, 4) # Hash size, ignored
        read_bytes(strings, 1) # Unknown, ignored
        read_bytes(strings, 4) # Start Index, ignored
        read_bytes(strings, 4) # Max misses, ignored
        read_bytes(strings, 4) # End index, ignored

        # Array of two bytes per entry, gives index to next table
        indexes = []
        for i in range(num_elements):
            indexes.append(read_bytes(strings, 2))

        # Store this position, as this is the position used to index from
        start_pos = strings.tell()

        # Array of 17 bytes per entry
        for i in range(num_elements):
            strings.seek(start_pos + (indexes[i] * 17), 0)
            read_bytes(strings, 1) # Used byte, ignored
            read_bytes(strings, 2) # Index Number, ignored
            read_bytes(strings, 4) # Has Number, ignored
            key_offset = read_bytes(strings, 4)
            value_offset = read_bytes(strings, 4)
            read_bytes(strings, 2) # Length of value string, ignored
            
            # Get the key string
            strings.seek(key_offset)
            key_string = read_string(strings)

            # Get the value string
            strings.seek(value_offset)
            value_string = read_string(strings)
            
            # Create the key/value pair dict
            key_value_dict[key_string] = value_string

    # Convert the embedded color codes to html color
    for key, value in dict(key_value_dict).items():
        value = value.replace("\n", "<br>")
        key_value_dict[key] = d2_color_to_html_color(value)
    
    return key_value_dict

mod_strings = get_string_dict()

#for i in range(1,100):
#    print(str(i) + ": " + mod_strings["StrSklTabItem" + str(i)])

#for key, value in mod_strings.items():
#    print(key + ": " + value)
