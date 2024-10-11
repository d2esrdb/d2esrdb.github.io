import json
import os
from pathlib import Path


def read_bytes(data, num_bytes):
    return int.from_bytes(data.read(num_bytes), byteorder="little")


def read_string(data):
    # @TODO There must be a better way of doing this...
    string_byte = data.read(1).decode("raw_unicode_escape")
    string = ""
    while string_byte != "\0":
        string = string + string_byte
        string_byte = data.read(1).decode("raw_unicode_escape")
    return string


def replace_code_with_color(value, code, color, count):
    if code in value:
        return value.replace(code, '<FONT COLOR="' + color + '">', 1), count + 1
    return value, count


"""
Ã¿c0 - Light Gray (Item Descriptions)
Ã¿c1 - Red
Ã¿c2 - Bright Green (Set Items)
Ã¿c3 - Blue (Magic Items)
Ã¿c4 - Gold (Unique Items)
Ã¿c5 - Dark Gray (Socketed/Ethereal Items)
Ã¿c6 - Transparent (Text Doesn't Show)
Ã¿c7 - Tan
Ã¿c8 - Orange (Crafted Items)
Ã¿c9 - Yellow (Rare Items)
Ã¿c: - Dark Green
Ã¿c; - Purple
Ã¿c/ - White (Brighter than Light Gray)
Ã¿c. - Messed Up White (Same as above but text is messed up)

Thanks Kieran zkier



d2r
ÿc0 white1
ÿc= white2
ÿc5 gray1
ÿcK gray2
ÿcI gray3
ÿc6 black1
ÿcM black2

ÿcE lightred
ÿc1 red1
ÿcU red2
ÿcS darkred

ÿc@ orange1
ÿc8 orange2
ÿcJ orange3
ÿcL orange4

ÿc7 lightgold1
ÿcH lightgold2
ÿc4 gold1
ÿcD gold2

ÿc9 yellow1
ÿcR yellow2

ÿc2 green1
ÿcQ green2
ÿcC green3
ÿc< green4
ÿcA darkgreen1
ÿc: darkgreen2

ÿcN turquoise
ÿcT skyblue
ÿcF lightblue1
ÿcP lightblue2
ÿc3 blue1
ÿcB blue2

ÿcG lightpink
ÿcO pink
ÿc; purple

Thanks LimpRock
"""


def d2_color_to_html_color(value):
    count = 0
    while True:
        start_count = count
        value, count = replace_code_with_color(value, "Ã¿c0", "LIGHTGRAY", count)
        value, count = replace_code_with_color(value, "Ã¿c1", "RED", count)
        value, count = replace_code_with_color(value, "Ã¿c2", "GREEN", count)
        value, count = replace_code_with_color(value, "Ã¿c3", "BLUE", count)
        value, count = replace_code_with_color(value, "Ã¿c4", "GOLD", count)
        value, count = replace_code_with_color(value, "Ã¿c5", "DARKGRAY", count)
        value, count = replace_code_with_color(value, "Ã¿c6", "BLACK", count)
        value, count = replace_code_with_color(value, "Ã¿c7", "GOLDENROD", count)
        value, count = replace_code_with_color(value, "Ã¿c8", "ORANGE", count)
        value, count = replace_code_with_color(value, "Ã¿c9", "YELLOW", count)
        value, count = replace_code_with_color(value, "Ã¿c:", "DARKGREEN", count)
        value, count = replace_code_with_color(value, "Ã¿c;", "PURPLE", count)
        value, count = replace_code_with_color(value, "Ã¿c/", "WHITE", count)
        value, count = replace_code_with_color(value, "Ã¿c.", "WHITE", count)
        # @TODO the colors below are for d2r and probably need to be better fine tuned
        value, count = replace_code_with_color(value, "ÿc0", "WHITE", count)
        value, count = replace_code_with_color(value, "ÿc=", "WHITE", count)
        value, count = replace_code_with_color(value, "ÿc5", "LIGHTGRAY", count)
        value, count = replace_code_with_color(value, "ÿcK", "LIGHTGRAY", count)
        value, count = replace_code_with_color(value, "ÿcI", "LIGHTGRAY", count)
        value, count = replace_code_with_color(value, "ÿc6", "BLACK", count)
        value, count = replace_code_with_color(value, "ÿcM", "BLACK", count)
        value, count = replace_code_with_color(value, "ÿcE", "RED", count)
        value, count = replace_code_with_color(value, "ÿc1", "RED", count)
        value, count = replace_code_with_color(value, "ÿcU", "RED", count)
        value, count = replace_code_with_color(value, "ÿcS", "DARKRED", count)
        value, count = replace_code_with_color(value, "ÿc@", "ORANGE", count)
        value, count = replace_code_with_color(value, "ÿc8", "ORANGE", count)
        value, count = replace_code_with_color(value, "ÿcJ", "ORANGE", count)
        value, count = replace_code_with_color(value, "ÿcL", "ORANGE", count)
        value, count = replace_code_with_color(value, "ÿc7", "GOLD", count)
        value, count = replace_code_with_color(value, "ÿcH", "GOLD", count)
        value, count = replace_code_with_color(value, "ÿc4", "GOLD", count)
        value, count = replace_code_with_color(value, "ÿcD", "GOLD", count)
        value, count = replace_code_with_color(value, "ÿc9", "YELLOW", count)
        value, count = replace_code_with_color(value, "ÿcR", "YELLOW", count)
        value, count = replace_code_with_color(value, "ÿc2", "GREEN", count)
        value, count = replace_code_with_color(value, "ÿcQ", "GREEN", count)
        value, count = replace_code_with_color(value, "ÿcC", "GREEN", count)
        value, count = replace_code_with_color(value, "ÿc<", "GREEN", count)
        value, count = replace_code_with_color(value, "ÿcA", "GREEN", count)
        value, count = replace_code_with_color(value, "ÿc:", "GREEN", count)
        value, count = replace_code_with_color(value, "ÿcN", "BLUE", count)
        value, count = replace_code_with_color(value, "ÿcT", "BLUE", count)
        value, count = replace_code_with_color(value, "ÿcF", "BLUE", count)
        value, count = replace_code_with_color(value, "ÿcP", "BLUE", count)
        value, count = replace_code_with_color(value, "ÿc3", "BLUE", count)
        value, count = replace_code_with_color(value, "ÿcB", "BLUE", count)
        value, count = replace_code_with_color(value, "ÿcG", "PINK", count)
        value, count = replace_code_with_color(value, "ÿcO", "PINK", count)
        value, count = replace_code_with_color(value, "ÿc;", "PURPLE", count)

        if start_count == count:
            break
    value = value + "</FONT>" * count
    return value


def get_string_dict(db_dir: Path, db_code, string_tables):
    key_value_dict = {}
    if string_tables[0].endswith("json"):
        directory = os.fsencode(db_dir / db_code / "strings-legacy")
        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            if filename.endswith(".json"):
                st = open(
                    db_dir / db_code / "strings-legacy" / filename, encoding="utf-8-sig"
                )
                data = json.load(st)
                for i in data:
                    key_value_dict[i["Key"]] = i["enUS"]
        directory = os.fsencode(db_dir / db_code / "strings")
        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            if filename.endswith(".json"):
                st = open(db_dir / db_code / "strings" / filename, encoding="utf-8-sig")
                data = json.load(st)
                for i in data:
                    key_value_dict[i["Key"]] = i["enUS"]
    else:
        for string_table in string_tables:
            strings = open(db_dir / db_code / string_table, "rb")

            # HEADER 21 bytes
            read_bytes(strings, 2)  # CRC, ignored
            num_elements = read_bytes(strings, 2)
            read_bytes(strings, 4)  # Hash size, ignored
            read_bytes(strings, 1)  # Unknown, ignored
            read_bytes(strings, 4)  # Start Index, ignored
            read_bytes(strings, 4)  # Max misses, ignored
            read_bytes(strings, 4)  # End index, ignored

            # Array of two bytes per entry, gives index to next table
            indexes = []
            for i in range(num_elements):
                indexes.append(read_bytes(strings, 2))

            # Store this position, as this is the position used to index from
            start_pos = strings.tell()

            # Array of 17 bytes per entry
            for i in range(num_elements):
                strings.seek(start_pos + (indexes[i] * 17), 0)
                read_bytes(strings, 1)  # Used byte, ignored
                read_bytes(strings, 2)  # Index Number, ignored
                read_bytes(strings, 4)  # Has Number, ignored
                key_offset = read_bytes(strings, 4)
                value_offset = read_bytes(strings, 4)
                read_bytes(strings, 2)  # Length of value string, ignored

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


if __name__ == "__main__":
    stringtables = [
        "string.tbl",
        "expansionstring.tbl",
        "patchstring.tbl",
        # "ES AlphA.tbl",
    ]
    my = get_string_dict(Path("."), "Lord_Of_Destruction", stringtables)
    for key, value in my.items():
        if "weapon" == value.lower():
            print(key + ": " + my[key])

    # print(my["weap"])
