# Diablo 2 Eastern Sun Rises Database Generator

A set of python scripts to generate a web based database for Diablo 2 mods.

## Install/Requirements

1. Install Python3.10+ (https://www.python.org/downloads/)
2. Install Mako for Python3 (pip install Mako)

## Usage

1. Clone this repo (git clone https://github.com/d2esrdb/d2esrdb.github.io.git)
2. Make a new directory inside the repo, use shortname or acronym for your mod
3. Copy all your txt files from global/data in to it, as well as all your .tbl files
4. Open config.py and add a new entry for your mod
5. Add your mod to index.htm
6. Run the db_gen.py script (py db_gen.py)
7. All the files should get generated. git add them, git commit them, git push them.

## Known issues

1. In-game, any weapon type that is a subtype of "blunt" will get 50% increased damage to undead.
This is hard-coded in Diablo 2 and I'm probably never going to update the dbgen to account for this
because it's a useless stat in 99% of cases and many mods even remove this "issue" with code edits.

2. Some mods format strangely because I don't really have a good way (or understanding) of going
from properties param/min/max to stat strings.

3. Sometimes what's in the .txt files and what actually happens in game is different than it
*should* be. For example in ESR there's a unique shield called Faith that has 0-2 sockets, but in
game it never rolls 0 sockets, and seems to roll 1 socket more than 2 sockets. Another example:
setting up an item with 1-10 %mag but using 1 in the param field and 10 in the min field still
works in game for some reason, but the dbgen just shows 1% because of the invalid data in the txt.
