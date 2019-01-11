import os


f=open("uploadSettings.txt", "r")
for line in f:
    if line.startswith("playlistTitle="):
        playlistTitle = line[14:]
        break
f.close()


idListName = "uploadedIDs.txt"

playlistDesc = "Dwelling of Duels"

os.system("playlist.py --file=\"{}\" --privacyStatus=\"{}\" --title=\"{}\" --description=\"{}\"".format(idListName, "private", playlistTitle, playlistDesc))
