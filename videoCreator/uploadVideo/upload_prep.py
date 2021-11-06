import os

from utils import splitName

DESC = "Dwelling of Duels is a monthly music competition based around video game soundtracks. Competitors anonymously submit redone versions of video game music in which the main instrument must be performed live, not sequenced, and the entries are voted upon by the community.\nhttp://dwellingofduels.net/  \nhttps://www.facebook.com/dwellingofduels"
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

FULL_DESC = "{}\n{}".format(descInfo, DESC)
print(FULL_DESC)

for filename in os.listdir("."):
    if filename.endswith(".mp4"):
        print("\n\n")
        rank, artist, game, title = splitName(filename)

        if rank is None:
            formattedTitle = "{} - {} - {}".format(artist, game, title)
        else:
            formattedTitle = "{} {} - {} - {}".format(rank, artist, game, title)

        if len(formattedTitle) >= 100:
            formattedTitle = formattedTitle[0:99]
            print("***WARNING: Title too long! Truncated!")

        print(formattedTitle)

        os.system("upload_video.py --file=\"{}\" --privacyStatus=\"{}\" --title=\"{}\" --category={} --description=\"{} \" ".format(filename, "private", formattedTitle, CATEGORY, repr(FULL_DESC)))
        continue
    else:
        continue
