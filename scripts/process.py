# Carlos Sanchez
# November, 2019
# A script for periodically processing pokemon images

# This script is expected to run in the root directory of all related files.

import os
import datetime
import sys
import json
import requests
import copy
from PIL import Image
from pathlib import Path

# Tweak Config stuff
MAXPROCESS=10 # Change to 50 or so maybe
THUMBSIZE=200,200
USER="Random"

# Probably won't change
POKEAPI="https://pokeapi.co/api/v2/"
LOCKFILE=".lock"
RAWDIR="raw"
THUMBDIR="thumb"
DATAFILE="data.json"


# Just a class so I can say "Hey the lock wasn't grabbed" instead of just
# EXCEPTION AAAAA
class LockException(Exception):
    pass

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
        raise LockException("Lock can't be grabbed")
    try:
        Path(file).touch()
        func()
    finally:
        os.remove(file)

def GetPokeApiData(name):
    response = requests.get(POKEAPI+"pokemon/"+name)
    response.raise_for_status()
    return response.json()

def MergePokeApiData(pokeApi, raw):
    raw["number"] = int(pokeApi["id"])
    raw["processed"] = str(datetime.datetime.now())

def CreatePokeData(entry = None):
    data = {}
    data["name"] = os.path.splitext(entry.name)[0] if entry else None
    data["number"] = 0
    data["thumb"] = None
    data["path"] = entry.path if entry else None
    data["created"] = str(CreateDate(entry.stat())) if entry else None
    data["processed"] = None
    return data

def CreateMasterData(existingData = []):
    data = {}
    data["list"] = existingData
    data["user"] = USER
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

# Make thumbnail using "defaults"
def MakeThumbnail(file):
    im = Image.open(file)
    im.thumbnail(THUMBSIZE, Image.ANTIALIAS)
    thumbFile = THUMBDIR+"/"+os.path.basename(file)
    im.save(thumbFile, quality=95)
    return thumbFile

# The main process loop. Can be called anywhere
def Process():
    full=GetFullData(DATAFILE)
    processed=0
    Path(THUMBDIR).mkdir(parents=True, exist_ok=True)

    for raw in GetRawData(RAWDIR):
        if processed >= MAXPROCESS:
            print("Hit process cap (" + str(MAXPROCESS) + "), must quit")
            break
        if not raw["name"] in [x["name"] for x in full["list"]]:
            print("Looking up: " + raw["name"])
            processed+=1
            try:
                pData = GetPokeApiData(raw["name"])
            except Exception as ex:
                print("ERROR: Couldn't look up " + raw["name"] + ": " + str(ex))
                continue
            newData = copy.deepcopy(raw)
            MergePokeApiData(pData, newData)
            full["list"].append(newData)

    for data in full["list"]:
        if data["thumb"] is None or not os.path.exists(data["thumb"]):
            print("Creating thumbnail for " + data["path"])
            data["thumb"] = MakeThumbnail(data["path"])
            processed+=1

    if processed > 0:
        print("Writing " + DATAFILE)
        with open(DATAFILE, "w") as f:
            json.dump(full, f)


# Now just... run some code! yaaayyy
try:
    FileLockSingleProcess(Process, LOCKFILE)
except LockException:
    print("Another process is processing pokemon files right now")
    sys.exit(1)

