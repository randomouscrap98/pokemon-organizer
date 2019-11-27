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
MAXPROCESS=10 # Change to 50 or so maybe
# MAXPOKEAPIPERMINUTE=50

# Probably won't change
POKEAPI="https://pokeapi.co/api/v2/"
LOCKFILE=".lock"
RAWDIR="raw"
THUMBDIR="thumb"
DATAFILE="data.json"


# Generic Utilities
def SerializeDate(date):
    if date is not None:
        return str(date)
    return date

def CreateDate(statData):
    return datetime.datetime.fromtimestamp(statData.st_mtime)

# Global functions for whatever
def CreatePokemonData(entry = None):
    data = {}
    data["name"] = os.path.splitext(entry.name)[0] if entry else None
    data["number"] = 0
    data["path"] = entry.path if entry else None
    data["created"] = str(CreateDate(entry.stat())) if entry else None
    data["processed"] = None
    return data

def CreateMasterData(existingData = []):
    data = {}
    data["list"] = existingData
    return data

# Get the data for all the raw files
def GetRawData(directory):
    with os.scandir(directory) as entries:
        return [ CreatePokemonData(entry) for entry in entries if entry.is_file() ]

# Get the existing "full" data
def GetFullData(file):
    try:
        # I guess default is read?
        with open(file) as f:
            return json.load(f)
    except Exception as ex:
        print("Warn: couldn't read full data, defaulting to blank: " + str(ex))
        return CreateMasterData()


# The main process loop.
# Posibility for race condition; probably won't happen though
if os.path.exists(LOCKFILE):
    print("Another process is processing pokemon files right now")
    sys.exit(1)

try:
    Path(LOCKFILE).touch()
    # print(json.dumps([x.AsSerializable() for x in GetRawData(RAWDIR)]))
    print(json.dumps(GetRawData(RAWDIR)))
finally:
    os.remove(LOCKFILE)
