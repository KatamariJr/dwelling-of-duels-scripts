#!/usr/bin/env python
import json
import os


fileDirectory = "./files"


fileDirectoryListing = os.listdir(fileDirectory)

outputVotesFiles = open("votes.txt", 'w', newline='\r\n')

outputText = ''

for filename in fileDirectoryListing:
    if "json" not in filename:
        continue
    splitFilename = filename.split(".")
    uuid = splitFilename[0]


    jsonData = json.loads(open(fileDirectory + '/' + filename, 'rb').read())

    # get all the names and stuff
    votes = jsonData['votes']
    submitter = jsonData['submitterEmail']

    outputText += '%s\n\n%s\n\n' % (submitter, votes)

#remove final newline
outputText = outputText[0:-1]
outputVotesFiles.write(outputText)