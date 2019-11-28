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

# Posibility for race condition; probably won't happen though.
# Also, don't exit the program in your function lol
def FileLockSingleProcess(func, file):
    if os.path.exists(file):
        raise Exception("Lock can't be grabbed")
    try:
        Path(file).touch()
        func()
    finally:
        os.remove(file)


# Global functions for whatever
def CreatePokeData(entry = None):
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
        return [ CreatePokeData(entry) for entry in entries if entry.is_file() ]

# Get the existing "full" data
def GetFullData(file):
    try:
        # I guess default is read?
        with open(file) as f:
            return json.load(f)
    except Exception as ex:
        print("Warn: couldn't read full data, defaulting to blank: " + str(ex))
        return CreateMasterData()

# The main process loop. Can be called anywhere
def Process():
    full=GetFullData(DATAFILE)
    # full["list"].sort(key=ComparePokeData)
    processed=0
    # index=0
    for raw in GetRawData(RAWDIR): # sorted(GetRawData(RAWDIR),key=ComparePokeData):
        if processed >= MAXPROCESS:
            print("Hit process cap (" + str(MAXPROCESS) + "), must quit")
            break
        if not raw["name"] in [x["name"] for x in full["list"]]:
            print("Looking up: " + raw["name"])
            processed+=1
        # print(json.dumps(raw))
        # index+=1
    print("Writing " + DATAFILE)
    with open(DATAFILE, "w") as f:
        json.dump(full, f)


# Now just... run some code! yaaayyy
try:
    FileLockSingleProcess(Process, LOCKFILE)
except:
    print("Another process is processing pokemon files right now")
    sys.exit(1)

