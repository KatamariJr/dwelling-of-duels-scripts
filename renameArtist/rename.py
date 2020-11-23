#!/usr/bin/env python3

import os
import sys

from mp3_tagger import MP3File, VERSION_1, VERSION_2, VERSION_BOTH

SKIP_ARTIST_CHECK = True

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
    if artistFind in artistTag:
        if SKIP_ARTIST_CHECK:
            choice = "y"
        else:
            choice = input("replace in %s (y/n)?" % artistTag)
        if choice == "y":
            # do the replace
            artistTag = artistTag.replace(artistFind, artistReplace)
            print(artistTag)
            songData.artist = artistTag
            songData.save()

def replaceInFilename(fileLocation, artistFind, artistReplace):
    if artistFind in fileLocation:
        choice = input("replace in %s (y/n)?" % fileLocation)
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
    except:
        print("must have a folder path as first arg, artist name as second arg")
        exit(1)
    print(os.getcwd())
    if not os.path.isdir(directory):
        sys.exit('Error: `{}` must be in {}'.format(directory, os.getcwd()))

    for d in os.listdir(directory):
        readFolderWithMP3s(os.path.join(directory, d), artistFind, artistReplace)
