# Diablo 2 Eastern Sun Rises Database Generator

A set of python scripts to generate a web based database for the D2ESR mod.

## Install/Requirements

1. Install Python3.10+ (https://www.python.org/downloads/)
2. Install Mako for Python3 (pip install Mako)

## Usage

Whenever a new ESR patch drops, the following steps will need to be taken to update the DB

1. Clone this repo (git clone https://github.com/d2esrdb/d2esrdb.github.io.git)
2. Copy the new patch files in to the ESR directory
3. Go in to the db_gen directory (cd d2esrdb.github.io/db_gen/)
4. Run the db_gen.py script (py db_gen.py)
5. All the files in the base repo directory are now updated. git add them, git commit them, git push them.
