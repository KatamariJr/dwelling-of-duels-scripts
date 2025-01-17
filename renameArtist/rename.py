#!/usr/bin/env python3

import os
import sys

from mp3_tagger import MP3File, VERSION_1, VERSION_2, VERSION_BOTH

SKIP_ARTIST_CHECK = False

def readFolderWithMP3s(directory, artistFind, artistReplace):
    print(directory)
    for d in os.listdir(directory):
        path = os.path.join(directory, d)

        if path.endswith(".mp3"):
            #do things with song
            #print(d + " mp3!!!")
            replaceArtistTags(path, artistFind, artistReplace)
            replaceInFilename(path, artistFind, artistReplace)


        if not os.path.isdir(path):
            continue


def replaceArtistTags(fileLocation, artistFind, artistReplace):
    songData = MP3File(fileLocation)
    songData.set_version(VERSION_2)
    artistTag = songData.artist
    try:
        if artistFind in artistTag:
            if SKIP_ARTIST_CHECK:
                choice = "y"
            else:
                choice = input("replace in tag: '%s' (y/n)?" % artistTag)
            if choice == "y":
                # do the replace
                artistTag = artistTag.replace(artistFind, artistReplace)
                print(artistTag)
                songData.artist = artistTag
                songData.save()
    except TypeError as err:
        print("Err: '%s' when reading file %s" % (err, fileLocation))

def replaceInFilename(fileLocation, artistFind, artistReplace):
    if artistFind in fileLocation:
        if SKIP_ARTIST_CHECK:
            choice = "y"
        else:
            choice = input("replace in filename: '%s' (y/n)?" % fileLocation)
        if choice == "y":
            newFileName = fileLocation.replace(artistFind, artistReplace)
            os.rename(fileLocation, newFileName)

if __name__ == '__main__':
    try:
        directory = sys.argv[1]
        print("directory: " + directory)
        artistFind = sys.argv[2]
        print("artistFind: " + artistFind)
        artistReplace = sys.argv[3]
        print("artistReplace: " + artistReplace)
        if len(sys.argv) == 5 and sys.argv[4] == "--yes":
           SKIP_ARTIST_CHECK = True
           print("SKIP_ARTIST_CHECK")
    except:
        print("must have a folder path as first arg, original artist name as second arg, replacement artist name as third arg")
        exit(1)
    print(os.getcwd())
    if not os.path.isdir(directory):
        sys.exit('Error: `{}` must be in {}'.format(directory, os.getcwd()))

    for d in os.listdir(directory):
        if os.path.isdir(os.path.join(directory, d)):
            readFolderWithMP3s(os.path.join(directory, d), artistFind, artistReplace)
