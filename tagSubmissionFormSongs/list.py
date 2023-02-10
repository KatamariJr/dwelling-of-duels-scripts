import json
import os


fileDirectory = "./files"


fileDirectoryListing = os.listdir(fileDirectory)


for filename in fileDirectoryListing:
    if "json" not in filename:
        continue
    splitFilename = filename.split(".")
    uuid = splitFilename[0]

    if (uuid + '.mp3') not in fileDirectoryListing:
        print("MISSING MP3 FILE FOR UPLOAD")

    jsonData = json.loads(open(fileDirectory + '/' + filename, 'r').read())

    # get all the names and stuff
    songTitle = jsonData['songTitle']
    artistNames = jsonData['artistNames']
    gameNames = jsonData['gameNames']
    submitter = jsonData['submitterEmail']
    if 'comments' in jsonData:
        comments = jsonData['comments']
    else:
        comments = ''
    isAlt = jsonData['isAlt'] == "true"

    print('Filename: %s\nTitle: %s\nArtists: %s\nGames: %s\nIsAlt: %s\nSubmitter: %s\nComments: %s\n' % (filename, songTitle, artistNames, gameNames, isAlt, submitter, comments))

    input("Enter for next file")
    print('\n\n')
