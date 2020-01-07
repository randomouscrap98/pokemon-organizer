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
MAXPROCESS=30 # Change to 50 or so maybe
THUMBSIZE=200,200
USER="Random"

# Probably won't change
POKEAPI="https://pokeapi.co/api/v2/"
LOCKFILE=".lock"
RAWDIR="raw"
THUMBDIR="thumb"
DATAFILE="data.json"
GENERATIONS=[
    "generation-i",
    "generation-ii",
    "generation-iii",
    "generation-iv",
    "generation-v",
    "generation-vi",
    "generation-vii",
    "generation-viii",
    "generation-ix",
    "generation-x"
]


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

def GetPokeApiSpeciesData(species):
    response = requests.get(POKEAPI+"pokemon-species/"+species)
    response.raise_for_status()
    return response.json()

def MergePokeApiData(pokeApi, pokeSpecies, raw):
    raw["number"] = int(pokeApi["id"])
    raw["species"] = pokeApi["species"]["name"]
    raw["processed"] = str(datetime.datetime.now())
    raw["generation"] = GENERATIONS.index(pokeSpecies["generation"]["name"]) + 1

def CreatePokeData(entry = None):
    data = {}
    data["name"] = os.path.splitext(entry.name)[0].lower() if entry else None
    data["number"] = 0
    data["thumb"] = None
    data["path"] = entry.path if entry else None
    data["created"] = str(CreateDate(entry.stat())) if entry else None
    data["processed"] = None
    data["species"] = None
    data["generation"] = None
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

# Find new pokemon data.
def DiscoverNew(fullData, rawData, maxDiscover):
    processed = 0
    for raw in rawData:
        if processed >= maxDiscover:
            print("Hit process cap (" + str(maxDiscover) + "), must quit")
            break
        if not raw["name"] in [x["name"] for x in fullData["list"]]:
            print("Looking up: " + raw["name"])
            newData = copy.deepcopy(raw)
            processed+=1
            try:
                pData = GetPokeApiData(raw["name"])
                pSpeciesData = GetPokeApiSpeciesData(pData["species"]["name"])
                MergePokeApiData(pData, pSpeciesData, newData)
            except Exception as ex:
                print("ERROR: Couldn't look up " + raw["name"] + ": " + str(ex))
            # Notice: append new data even if nothing was looked up.
            fullData["list"].append(newData)
    return processed

# Update missing thumbnails for all data in "fullData" (the whole data object,
# not just the list)
def UpdateThumbnails(fullData):
    processed = 0
    for data in fullData["list"]:
        if data["thumb"] is None or not os.path.exists(data["thumb"]):
            print("Creating thumbnail for " + data["path"])
            data["thumb"] = MakeThumbnail(data["path"])
            processed+=1
    return processed

# Removing items missing from rawData that are still in fullData
def RemoveMissing(fullData, rawData):
    removals=[]
    processed=0
    for data in fullData["list"]:
        if not data["name"] in [x["name"] for x in rawData]:
            removals.append(data)
            processed+=1
    for removal in removals:
        print("Removing missing pokemon " + removal["name"])
        fullData["list"].remove(removal)
    return processed

# The main process loop. Can be called anywhere
def Process():
    full=GetFullData(DATAFILE)
    rawData=GetRawData(RAWDIR)
    Path(THUMBDIR).mkdir(parents=True, exist_ok=True)

    processed = DiscoverNew(full, rawData, MAXPROCESS)
    processed += RemoveMissing(full, rawData)
    processed += UpdateThumbnails(full)

    # Only write back if something was processed
    if processed > 0:
        print("Writing " + DATAFILE)
        with open(DATAFILE, "w") as f:
            json.dump(full, f)


# Now just... run some code! yaaayyy
try:
    print("Started: " + str(datetime.datetime.now()))
    FileLockSingleProcess(Process, LOCKFILE)
except LockException:
    print("Another process is processing pokemon files right now")
    sys.exit(1)

