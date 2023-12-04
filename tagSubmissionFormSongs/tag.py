#!/usr/bin/env python

import json
import os
import shutil
import eyed3


MAX_TOTAL_FILENAME_LENGTH = 180
MINIMUM_CHARACTERS_PER_FILENAME_FIELD = 10
ALBUM_NAME = "DoD23-10: Horror Games"
YEAR = "2023"

def renameAndCopy(isAlt: bool, artistNames: str, gameNames: str, songTitle: str, albumName: str, srcFile: str, outputDirectory: str, coverImageFilename: str) -> None:
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


    if isAlt:
        newFilename = "ZZ-%s-%s-%s-DoD%s.%s" % (truncatedArtistNames, truncatedGameNames, truncatedSongTitle, originalUUID, extension)
    else:
        newFilename = "%s-%s-%s-DoD%s.%s" % (truncatedArtistNames, truncatedGameNames, truncatedSongTitle, originalUUID, extension)

    newFilename = "".join(x for x in newFilename if x.isalnum() or x in "._- ,!")

    targetFilename = outputDirectory + '/' + newFilename

    print(newFilename)

    shutil.copyfile(srcFile, targetFilename)

    if extension == "mp3":
        retag(targetFilename, artistNames, gameNames, songTitle, albumName, coverImageFilename)


def retag(targetFilename: str, artistNames: str, gameNames: str, songTitle: str, albumName: str, coverImageFilename: str):
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
    imageBytes = None
    try:
        imageBytes = open(coverImageFilename, 'rb').read()
    except:
        print("Missing jpg for cover image in this folder!")
    audiofile.tag.images.set(3, imageBytes, 'image/jpeg')
    if isAlt:
        audiofile.tag.track_num = 99

    audiofile.tag.save()


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

    # get all the names and stuff
    songTitle = jsonData['songTitle']
    artistNames = jsonData['artistNames']
    gameNames = jsonData['gameNames']
    isAlt = jsonData['isAlt'] == "true"

    # create file for non-anonymized
    renameAndCopy(isAlt, artistNames, gameNames, songTitle, ALBUM_NAME, fileDirectory + '/' + uuid + '.mp3', fileDirectory + '/newSongs', coverImage)
    renameAndCopy(isAlt, artistNames, gameNames, songTitle, ALBUM_NAME, fileDirectory + '/' + filename, fileDirectory + '/newSongs', coverImage)

    # create file for anonymized
    renameAndCopy(isAlt, "Anonymous DoD Contestant", gameNames, songTitle, ALBUM_NAME, fileDirectory + '/' + uuid + '.mp3', fileDirectory + '/newSongsAnon', coverImage)

print("Done\n")
