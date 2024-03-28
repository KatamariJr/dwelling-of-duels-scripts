#!/usr/bin/env python

import json
import os
import shutil
import eyed3
import sys

MAX_TOTAL_FILENAME_LENGTH = 175
MINIMUM_CHARACTERS_PER_FILENAME_FIELD = 10
ALBUM_NAME = "DoD24-03: HAL Laboratory"
YEAR = "2024"


def renameAndCopy(isAlt: bool, trackNum: int, artistNames: str, gameNames: str, songTitle: str, albumName: str, srcFile: str, outputDirectory: str, coverImageFilename: str) -> None:
    extension = ""
    originalUUID = ""
    if "json" in srcFile.lower():
        extension = "json"
        originalUUID = "-" + srcFile[8:-5]
    elif "mp3" in srcFile.lower():
        extension = "mp3"

    # check maximum lengths for names for filename
    truncatedArtistNames = artistNames
    truncatedGameNames = gameNames
    truncatedSongTitle = songTitle
    if len(artistNames) + len(gameNames) + len(songTitle) > MAX_TOTAL_FILENAME_LENGTH:
        remainingCharacters = MAX_TOTAL_FILENAME_LENGTH
        if len(artistNames) > remainingCharacters:
            truncatedArtistNames = artistNames[:remainingCharacters]
            remainingCharacters = MINIMUM_CHARACTERS_PER_FILENAME_FIELD
        else:
            remainingCharacters -= len(artistNames)

        if len(gameNames) > remainingCharacters:
            truncatedGameNames = gameNames[:remainingCharacters]
            remainingCharacters = MINIMUM_CHARACTERS_PER_FILENAME_FIELD
        else:
            remainingCharacters -= len(gameNames)

        if len(songTitle) > remainingCharacters:
            truncatedSongTitle = songTitle[:remainingCharacters]
            remainingCharacters = MINIMUM_CHARACTERS_PER_FILENAME_FIELD
        else:
            remainingCharacters -= len(songTitle)

    placePrefix = ""
    if isAlt:
        placePrefix = "ZZ-"
        trackNum = 99
    elif trackNum is not None:
        placePrefix = f"{trackNum:02}-"
    else:
        trackNum = 0

    newFilename = "%s%s-%s-%s-DoD%s.%s" % (placePrefix, truncatedArtistNames, truncatedGameNames, truncatedSongTitle, originalUUID, extension)

    newFilename = "".join(x for x in newFilename if x.isalnum() or x in "._- ,!")

    targetFilename = outputDirectory + '/' + newFilename

    print(newFilename)

    shutil.copyfile(srcFile, targetFilename)

    if extension == "mp3":
        retag(targetFilename, trackNum, artistNames, gameNames, songTitle, albumName, coverImageFilename)


def retag(targetFilename: str, trackNum: int, artistNames: str, gameNames: str, songTitle: str, albumName: str, coverImageFilename: str):
    audiofile = eyed3.load(targetFilename)
    if audiofile is None:
        raise "File mp3 open fail!!!"
    audiofile.initTag()
    audiofile.tag.artist = artistNames
    audiofile.tag.non_std_genre = gameNames
    audiofile.tag.title = songTitle
    audiofile.tag.album = albumName
    audiofile.tag.recording_date = YEAR
    audiofile.tag.comments.set('www.dwellingofduels.net')
    audiofile.tag.track_num = trackNum
    imageBytes = None
    try:
        imageBytes = open(coverImageFilename, 'rb').read()
    except:
        print("Missing jpg for cover image in this folder!")
    audiofile.tag.images.set(3, imageBytes, 'image/jpeg')

    audiofile.tag.save()


def parseResultsJson(filename: str) -> list[dict]:
    with open(filename, "r") as f:
        jdict = json.load(f)
    return jdict


def main(resultsData: list[dict] | None = None) -> int:
    fileDirectory = "./files"

    fileDirectoryListing = os.listdir(fileDirectory)

    if "newSongs" not in fileDirectoryListing:
        os.mkdir(fileDirectory + "/newSongs")
    if "newSongsAnon" not in fileDirectoryListing:
        os.mkdir(fileDirectory + "/newSongsAnon")

    coverImage = ""
    for filename in fileDirectoryListing:
        if "jpg" not in filename.lower():
            continue
        coverImage = fileDirectory + '/' + filename
        break

    for filename in fileDirectoryListing:
        if "json" not in filename:
            continue
        splitFilename = filename.split(".")
        uuid = splitFilename[0]

        try:
            jsonData = json.loads(open(fileDirectory + '/' + filename, 'rb').read())
        except Exception as e:
            print("error reading file " + filename + ": " + e)
            return 2

        # get all the names and stuff
        songTitle = jsonData['songTitle']
        artistNames = jsonData['artistNames']
        gameNames = jsonData['gameNames']
        isAlt = jsonData['isAlt'] == "true"
        trackNum = None

        # if resultsFile was passed in, try finding a placement record with same title
        if resultsData is not None and isAlt is not True:
            matchingTitle = f"{gameNames.strip()} - {songTitle.strip()}".strip()
            success = False
            for r in resultsData:
                if r["songTitle"] == matchingTitle:
                    trackNum = r["place"]
                    success = True
                    break
            if not success:
                #raise Exception(f"didnt find record for {matchingTitle} in results data")
                print(f"didnt find record for {matchingTitle} in results data")


        # create file for non-anonymized
        renameAndCopy(isAlt, trackNum, artistNames, gameNames, songTitle, ALBUM_NAME, fileDirectory + '/' + uuid + '.mp3', fileDirectory + '/newSongs', coverImage)
        renameAndCopy(isAlt, trackNum, artistNames, gameNames, songTitle, ALBUM_NAME, fileDirectory + '/' + filename, fileDirectory + '/newSongs', coverImage)

        # create file for anonymized
        renameAndCopy(isAlt, None, "Anonymous DoD Contestant", gameNames, songTitle, ALBUM_NAME, fileDirectory + '/' + uuid + '.mp3', fileDirectory + '/newSongsAnon', coverImage)

    print("Done\n")
    return 0

if __name__ == '__main__':
    if len(sys.argv) == 2:
        filepath = sys.argv[1]
        if '.json' not in filepath:
            print("first parameter should be a json file or nothing")
            sys.exit(1)
        print(f'using {filepath} as results file')
        resultsListDict = parseResultsJson(filepath)
        sys.exit(main(resultsListDict))
    sys.exit(main())
