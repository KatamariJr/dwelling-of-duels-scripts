import json
import os
import shutil

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
    newFilename = ""
    if isAlt:
        newFilename = "ZZ-%s-%s-%s-DoD.mp3" % (artistNames, gameNames, songTitle)
    else:
        newFilename = "%s-%s-%s-DoD.mp3" % (artistNames, gameNames, songTitle)

    newFilename = "".join(x for x in newFilename if x.isalnum() or x in "._- ,!")

    shutil.copyfile(fileDirectory + '/' + filename, fileDirectory + '/newSongs/' + newFilename)



    # create file for anonymized
    artistNames = "Anonymous DoD Contestant"
    newFilenameAnon = ""
    if isAlt:
        newFilenameAnon = "ZZ-%s-%s-%s-DoD.mp3" % (artistNames, gameNames, songTitle)
    else:
        newFilenameAnon = "%s-%s-%s-DoD.mp3" % (artistNames, gameNames, songTitle)

    newFilenameAnon = "".join(x for x in newFilenameAnon if x.isalnum() or x in "._- ,!")

    shutil.copyfile(fileDirectory + '/' + filename, fileDirectory + '/newSongsAnon/' + newFilenameAnon)




