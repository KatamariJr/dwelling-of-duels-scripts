import json
import os
import shutil
import eyed3


def renameAndCopy(isAlt: bool, artistNames: str, gameNames: str, songTitle: str, albumName: str, srcFile: str, outputDirectory: str) -> None:
    extension = ""
    originalUUID = ""
    if "json" in srcFile:
        extension = "json"
        originalUUID = "-" + srcFile[8:-5]
    elif "mp3" in srcFile:
        extension = "mp3"

    if isAlt:
        newFilename = "ZZ-%s-%s-%s-DoD%s.%s" % (artistNames, gameNames, songTitle, originalUUID, extension)
    else:
        newFilename = "%s-%s-%s-DoD%s.%s" % (artistNames, gameNames, songTitle, originalUUID, extension)

    newFilename = "".join(x for x in newFilename if x.isalnum() or x in "._- ,!")

    targetFilename = outputDirectory + '/' + newFilename

    print(newFilename)

    shutil.copyfile(srcFile, targetFilename)

    if extension == "mp3":
        retag(targetFilename, artistNames, gameNames, songTitle, albumName)


def retag(targetFilename: str, artistNames: str, gameNames: str, songTitle: str, albumName: str):
    audiofile = eyed3.load(targetFilename)
    if audiofile is None:
        raise "File mp3 open fail!!!"
    audiofile.initTag()
    audiofile.tag.artist = artistNames
    audiofile.tag.non_std_genre = gameNames
    audiofile.tag.title = songTitle
    audiofile.tag.album = albumName
    audiofile.tag.recording_date = "2023"
    audiofile.tag.comments.set('www.dwellingofduels.net')
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

    jsonData = json.loads(open(fileDirectory + '/' + filename, 'r').read())

    # get all the names and stuff
    songTitle = jsonData['songTitle']
    artistNames = jsonData['artistNames']
    gameNames = jsonData['gameNames']
    isAlt = jsonData['isAlt'] == "true"

    # create file for non-anonymized
    renameAndCopy(isAlt, artistNames, gameNames, songTitle, albumName, fileDirectory + '/' + uuid + '.mp3', fileDirectory + '/newSongs')
    renameAndCopy(isAlt, artistNames, gameNames, songTitle, albumName, fileDirectory + '/' + filename, fileDirectory + '/newSongs')

    # create file for anonymized
    renameAndCopy(isAlt, "Anonymous DoD Contestant", gameNames, songTitle, albumName, fileDirectory + '/' + uuid + '.mp3', fileDirectory + '/newSongsAnon')

