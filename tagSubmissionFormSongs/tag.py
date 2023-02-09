import json
import os
import shutil
import eyed3

def renameAndMove(isAlt: bool, artistNames: str, gameNames: str, songTitle: str, albumName: str, srcFile: str, outputDirectory: str) -> None:
    if isAlt:
        newFilename = "ZZ-%s-%s-%s-DoD.mp3" % (artistNames, gameNames, songTitle)
    else:
        newFilename = "%s-%s-%s-DoD.mp3" % (artistNames, gameNames, songTitle)

    newFilename = "".join(x for x in newFilename if x.isalnum() or x in "._- ,!")

    targetFilename = outputDirectory + '/' + newFilename

    print(targetFilename)

    shutil.copyfile(srcFile, targetFilename)

    audiofile = eyed3.load(targetFilename)
    if audiofile is None:
        raise("File mp3 open fail!!!")
    audiofile.initTag()
    audiofile.tag.artist = artistNames
    audiofile.tag.non_std_genre = gameNames
    audiofile.tag.title = songTitle
    audiofile.tag.album = albumName
    audiofile.tag.original_release_date = 2023
    if isAlt:
        audiofile.tag.track_num = 99

    audiofile.tag.save()



fileDirectory = "./files"

albumName = "DoD-23-01: Testing Theme"

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
    renameAndMove(isAlt, artistNames, gameNames, songTitle, albumName, fileDirectory + '/' + uuid + '.mp3', fileDirectory + '/newSongs')


    # create file for anonymized
    renameAndMove(isAlt, "Anonymous DoD Contestant", gameNames, songTitle, albumName, fileDirectory + '/' + uuid + '.mp3', fileDirectory + '/newSongsAnon')




