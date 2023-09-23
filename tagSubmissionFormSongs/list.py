#!/usr/bin/env python
import csv
import json
import os

fileDirectory = "./files"

fileDirectoryListing = os.listdir(fileDirectory)

lyricsFile = open("lyrics.txt", 'w')

outputCSV = open("list.csv", 'w')

wr = csv.writer(outputCSV)
wr.writerow(["submitTime", "filename", "submitter", "songTitle", "artistNames", "gameNames", "isAlt", "comments", "lyrics", "problem"])

for filename in fileDirectoryListing:
    if "json" not in filename:
        continue
    splitFilename = filename.split(".")
    uuid = splitFilename[0]
    problem = ''

    if (uuid + '.mp3') not in fileDirectoryListing:
        problem = "MISSING MP3 FILE FOR UPLOAD"

    jsonData = json.loads(open(fileDirectory + '/' + filename, 'rb').read())

    # get all the names and stuff
    songTitle = jsonData['songTitle']
    artistNames = jsonData['artistNames']
    gameNames = jsonData['gameNames']
    submitter = jsonData['submitterEmail']
    submissionTime = jsonData['submissionTime']
    if 'comments' in jsonData:
        comments = jsonData['comments']
    else:
        comments = ''
    if 'lyrics' in jsonData:
        lyrics = jsonData['lyrics']
        if lyrics != "":
            lyricsFile.write("%s\n\n%s\n\n\n\n\n" % (songTitle, lyrics))
    else:
        lyrics = ''
    isAlt = jsonData['isAlt'] == "true"

    wr.writerow([submissionTime, filename, submitter, songTitle, artistNames, gameNames, isAlt, comments, lyrics, problem])


outputCSV.close()
lyricsFile.close()
