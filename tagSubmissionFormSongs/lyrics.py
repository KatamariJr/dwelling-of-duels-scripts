#!/usr/bin/env python
import json
import os

fileDirectory = "./files"

fileDirectoryListing = os.listdir(fileDirectory)

outputLyricsTxt = open(fileDirectory + "/newSongs/lyrics.txt", 'w')
outputLyricsAnonTxt = open(fileDirectory + "/newSongsAnon/lyrics.txt", 'w')


for filename in fileDirectoryListing:
    if "json" not in filename:
        continue
    splitFilename = filename.split(".")
    uuid = splitFilename[0]
    problem = ''

    if (uuid + '.mp3') not in fileDirectoryListing:
        continue

    jsonData = json.loads(open(fileDirectory + '/' + filename, 'rb').read())
    if 'lyrics' not in jsonData:
        continue

    # get all the names and stuff
    songTitle = jsonData['songTitle']
    lyrics = jsonData['lyrics']
    if lyrics == '':
        continue

    outputLyricsTxt.write("%s\n\n%s\n\n\n\n" % (songTitle, lyrics))
    outputLyricsAnonTxt.write("%s\n\n%s\n\n\n\n" % (songTitle, lyrics))


outputLyricsTxt.close()
outputLyricsAnonTxt.close()
