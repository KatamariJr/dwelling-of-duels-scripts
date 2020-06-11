import numpy as np
from scipy import stats

data = open('votes.txt','r').read()
# split the text file by double carriage return
lines = data.split("\n\n")
# populate the list of songs
songNames = []
songsCondensed = []
for i in lines[1].split("\n"):
    name = i.split(" / ")[0]
    songNames.append(name)
    songsCondensed.append(''.join(name.lower().split(" ")))
ratingNames = ["terrible", "bad", "below", "average", "above", "good", "incredible", "my"]
ratingNamesFull = ["terrible", "bad", "below average", "average", "above average", "good", "incredible"]

# parse the score ratings
allScores = []
voters = []
averages = []
for i in range(0,len(lines),2):
    voter = lines[i]
    voters.append(voter)
    reviewed = False
    if len(voter.split("(reviewed)")) > 1:
        reviewed = True
    # turn the word rating into a number and add it to a list
    scores = np.empty(len(songNames))
    for j in lines[i + 1].split("\n"):
        line = j.strip().split(" / ")
        songName = ''.join(line[0].lower().split(" "))
        songIndex = songsCondensed.index(songName)
        words = line[1].split(" ")
        rating = ratingNames.index(words[0].lower())
        if words[-1].lower() != "song":
            try:
                rating += float(words[-1])
            except:
                print(voter, words)
        scores[songIndex] = rating
    # substitute the average vote value in for a contestant's own song, which makes no modification to their score
    average = np.average(scores[scores != 7])
    scores[scores == 7] = average
    averages.append(scores)
    # get z scores
    zscores = stats.zscore(scores)
    if reviewed:
        zscores *= 1.2
    allScores.append(zscores)



# tally up the results
totals = np.sum(allScores, axis=0)
ranks = np.argsort(totals)[::-1]
# the following variables are for coming up with ratings to describe the songs
highScore = averages[ranks[0]]
lowScore = averages[ranks[-1]]

print(highScore)
print(lowScore)

zHigh = totals[ranks[0]]
zLow = totals[ranks[-1]]



mult = (highScore - lowScore) / (zHigh - zLow)

print np.array(songNames)[ranks]

for i, r in enumerate(ranks):
    #print totals[ranks[i]]
    pulledScore = (totals[ranks[i]] - zLow) * mult + lowScore
    roundedScore = int(np.round(pulledScore))
    adj = pulledScore - roundedScore
    operand = " +"
    if (adj < 0): operand = " -"
    adj = np.abs(np.floor(adj * 100) / 100)
    print roundedScore
    print "#" + str(i + 1) + " Artist - " + songNames[r] + " - " + ratingNamesFull[roundedScore]



