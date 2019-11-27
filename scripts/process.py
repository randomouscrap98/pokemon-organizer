# Carlos Sanchez
# November, 2019
# A script for periodically processing pokemon images

# This script is expected to run in the root directory of all related files.

import os
import datetime
import sys
import json
from pathlib import Path

# Tweak Config stuff
MAXPROCESS=10

# Probably won't change
POKEAPI="https://pokeapi.co/api/v2/"
LOCKFILE=".lock"
RAWDIR="raw"
THUMBDIR="thumb"
DATAFILE="data.json"


def CreatePokemonData(entry = None):
    data = {}
    data["number"] = 0
    return data

# Classes to hold standardized data
class PokemonData:
    def __init__(self):
        self.name = None
        self.path = None
        self.number = 0
        self.created = None
        self.processed = None

    def FromFileEntry(entry):
        data = PokemonData()
        data.path = entry.path
        data.name = os.path.splitext(entry.name)[0]
        data.created = CreateDate(entry.stat())
        return data

    def AsSerializable(self):
        base = self.__dict__
        base["created"] = SerializeDate(base["created"])
        base["processed"] = SerializeDate(base["processed"])
        return base


class FullData:
    def __init__(self):
        self.list = []

    def AsSerialize(self):
        base = self.__dict__
        base["list"] = [x.AsSerializable() for x in base["list"]]
        return base


def SerializeDate(date):
    if date is not None:
        return str(date)
    return date

# Global functions for whatever
def CreateDate(statData):
    return datetime.datetime.fromtimestamp(statData.st_mtime)

# Get the data for all the raw files
def GetRawData(directory):
    result = []
    with os.scandir(directory) as entries:
        for entry in entries:
            if entry.is_file():
                result.append(PokemonData.FromFileEntry(entry))
    return result

# The main process loop.
# Posibility for race condition; probably won't happen though
if os.path.exists(LOCKFILE):
    print("Another process is processing pokemon files right now")
    sys.exit(1)

try:
    Path(LOCKFILE).touch()
    print(json.dumps([x.AsSerializable() for x in GetRawData(RAWDIR)]))
finally:
    os.remove(LOCKFILE)
