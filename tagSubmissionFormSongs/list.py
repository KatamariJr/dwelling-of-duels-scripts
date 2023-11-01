#!/usr/bin/env python
import csv
import json
import os

fileDirectory = "./files"

fileDirectoryListing = os.listdir(fileDirectory)

outputCSV = open("songs.csv", 'w')

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

    try:
        jsonData = json.loads(open(fileDirectory + '/' + filename, 'rb').read())
    except Exception as e:
        print("error reading file " + filename + ": ", e)
        quit(1)

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
    else:
        lyrics = ''
    isAlt = jsonData['isAlt'] == "true"

    wr.writerow([submissionTime, filename, submitter, songTitle, artistNames, gameNames, isAlt, comments, lyrics, problem])


outputCSV.close()
