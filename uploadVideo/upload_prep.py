import os

DESC = "Dwelling of Duels is a monthly music competition based around video game soundtracks. Competitors anonymously submit redone versions of video game music in which the main instrument must be performed live, not sequenced, and the entries are voted upon by the community.\\nhttp://dwellingofduels.net/\\nhttps://www.facebook.com/dwellingofduels"
# category 10 is music
CATEGORY = "10"

f = open("uploadSettings.txt", "r")
for line in f:
    if line.startswith("descInfo="):
        descInfo = line[9:]
        break
f.close()

if descInfo is None:
    descInfo = ""

FULL_DESC = "{}\\n{}".format(descInfo, DESC)

for filename in os.listdir("."):
    if filename.endswith(".mp4"):
        print("\n\n")
        rank = filename.split("-")[0]
        if rank == "ZZ":
            rank = "ALT"
            artist = filename.split("-")[1]
            game = filename.split("-")[2]
            title = filename.split("-")[3]
        elif not rank.isdigit():
            rank = None
            artist = filename.split("-")[0]
            game = filename.split("-")[1]
            title = filename.split("-")[2]
        else:
            artist = filename.split("-")[1]
            game = filename.split("-")[2]
            title = filename.split("-")[3]

        if artist == "Anon":
            artist = "Anonymous DoD Contestant"

        if rank is None:
            formattedTitle = "{} - {} - {}".format(artist, game, title)
        else:
            formattedTitle = "{} {} - {} - {}".format(rank, artist, game, title)

        if len(formattedTitle) >= 100:
            formattedTitle = formattedTitle[0:99]
            print("***WARNING: Title too long! Truncated!")

        print(formattedTitle)
        os.system("upload_video.py --file=\"{}\" --privacyStatus=\"{}\" --title=\"{}\" --description=\"{}\" --category=10".format(filename, "private", formattedTitle, FULL_DESC))
        continue
    else:
        continue
