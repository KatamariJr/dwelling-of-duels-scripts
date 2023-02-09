import json
import os
import shutil

def renameAndMove(isAlt: bool, artistNames: str, gameNames: str, songTitle: str, srcFile: str, outputDirectory: str):
    newFilename = ""
    if isAlt:
        newFilename = "ZZ-%s-%s-%s-DoD.mp3" % (artistNames, gameNames, songTitle)
    else:
        newFilename = "%s-%s-%s-DoD.mp3" % (artistNames, gameNames, songTitle)

    newFilename = "".join(x for x in newFilename if x.isalnum() or x in "._- ,!")

    shutil.copyfile(srcFile, outputDirectory + '/' + newFilename)


fileDirectory = "./files"

fileDirectoryListing = os.listdir(fileDirectory)

if "newSongs" not in fileDirectoryListing:
    os.mkdir(fileDirectory + "/newSongs")
if "newSongsAnon" not in fileDirectoryListing:
    os.mkdir(fileDirectory + "/newSongsAnon")

for filename in fileDirectoryListing:
    if "json" not in filename:
        continue
    splitFilename = filename.split(".")
    uuid = splitFilename[0]
    extension = splitFilename[1]

    jsonData = json.loads(open(fileDirectory + '/' + filename, 'r').read())

    # get all the names and stuff
    songTitle = jsonData['songTitle']
    artistNames = jsonData['artistNames']
    gameNames = jsonData['gameNames']
    isAlt = jsonData['isAlt'] == "true"


    # create file for non-anonymized
    renameAndMove(isAlt, artistNames, gameNames, songTitle, fileDirectory + '/' + filename, fileDirectory + '/newSongs')


    # create file for anonymized
    renameAndMove(isAlt, "Anonymous DoD Contestant", gameNames, songTitle, fileDirectory + '/' + filename, fileDirectory + '/newSongsAnon')




