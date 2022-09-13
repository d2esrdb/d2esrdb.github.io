import os

# List of string tables to parse. Parsed in order so higher indexed tables
# override lower tables in the case of duplicate strings  
string_tables = [
    "string.tbl",
    "expansionstring.tbl",
    "patchstring.tbl",
    "ES AlphA.tbl",   
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

def get_string_dict():
    data_path = ""
    for root, dirs, files in os.walk("../"):
        if "Data" in dirs:
            data_path = os.path.join(root, "Data")

    key_value_dict = {}
    for string_table in string_tables:
        strings = open(data_path + "/local/LNG/eng/" + string_table, "rb")

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
    return key_value_dict

mod_strings = get_string_dict()
#for i in range(1,100):
#    print(str(i) + ": " + get_string_dict()["StrSklTabItem" + str(i)])

#for i in range(1,100):
#    print(get_string_dict()["StrSklTabItem" + str(i)])
#print(get_string_dict()["item_singleskill"])

