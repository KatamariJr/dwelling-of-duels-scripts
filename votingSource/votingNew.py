import numpy as np
from scipy import stats
from typing import TypedDict, List


class SongVoteData:
    voter: str
    scores: List[float]
    reviewed: bool

    def __init__(self, voter="", scores=[], reviewed=False):
        self.voter = voter
        self.scores = scores
        self.reviewed = reviewed

    def __str__(self):
        return f"{self.voter} {self.reviewed} {self.scores}"


theData = open('votes.txt', 'r').read()
# split the text file by double carriage return
dataArray = theData.split("\n\n")

# populate the list of songs from the list in the first vote block
songNames = []
songsCondensed = []
for i in dataArray[1].split("\n"):
    songTitle = i.split(" / ")[0]
    songNames.append(songTitle)
    songsCondensed.append(''.join(songTitle.lower().split(" ")))
ratingNames = ["terrible", "bad", "below", "average", "above", "good", "incredible", "my"]
ratingNamesFull = ["terrible", "bad", "below average", "average", "above average", "good", "incredible"]

# parse the score ratings (aka sortData())
voters = []
theResults = []
for i in range(0, len(dataArray), 2):
    voter = dataArray[i]
    voters.append(voter)
    reviewed = False
    if len(voter.split("(reviewed)")) > 1:
        reviewed = True
    # turn the word rating into a number and add it to a list
    scores = np.empty(len(songNames))
    for j in dataArray[i + 1].split("\n"):
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
    average = np.average(scores[scores != 7])
    scores[scores == 7] = average
    theResults.append(SongVoteData(voter, scores, reviewed))

# get the averages for the data (aka averages())
averagesList = np.average([res.scores for res in theResults], axis=0)

# get the averages z scores for the data (aka averagedZscores())
listOfListOfVotes = []
for r in theResults:
    listOfListOfVotes.append(r.scores)

finalZScores = stats.zscore([res.scores for res in theResults], axis=1)
for i in range(len(theResults)):
    if theResults[i].reviewed:
        print("reviewed")
        finalZScores[i] = [score * 1.2 for score in finalZScores[i]]
averagedZScoresTotal = np.average(finalZScores, axis=0)

#do things aka calculateResults()
theArray = averagedZScoresTotal
finals = np.argsort(theArray)[::-1]  # flips the order so highest is first

print(finals)
print(averagesList)
print(theArray)

highScore = averagesList[finals[0]]
lowScore = averagesList[finals[-1]]
zHigh = theArray[finals[0]]
zLow = theArray[finals[-1]]

print(highScore)

num = 0

multiplier = (highScore - lowScore) / (zHigh - zLow)
subtracter = zLow
adder = lowScore

for k in range(0, len(finals)):
    if k > 0:
        if (theArray[finals[k]] != theArray[finals[k-1]]):
            num = k
    else:
        num = k
    pulledScore = (theArray[finals[k]] - subtracter) * multiplier + adder
    roundedScore = int(np.round(pulledScore))

    adj = pulledScore - roundedScore
    operand = "+"
    if adj < 0:
        operand = "-"
    adj = np.abs(np.floor(adj * 100)/100)

    #todo - used for color coding
    #percentage = (theArray[finals[k]] - zLow) / (zHigh - zLow)

    #print(pulledScore, roundedScore, songs[finals[k]])
    print(f"#{num+1} Artist - {songNames[finals[k]]} - {ratingNamesFull[roundedScore]} {operand}{adj}")
print(f"Voters: {len(theResults)}")


#aka findDeviants()
devTotals = []
avgDev = 0
for iScore in finalZScores:
    devTotal = 0
    for j in range (0, len(iScore)):
        jScore = iScore[j]
        devTotal += np.power(jScore - theArray[j], 2)
    devTotal /= len(iScore)
    devTotals.append(devTotal)
    avgDev += devTotal
avgDev /= len(finalZScores)
print("Deviants:")
print(devTotals)

ia = np.argsort(devTotals)[::-1]
for i in range(len(finalZScores)):
    print(f"{theResults[ia[i]].voter}: {np.round(devTotals[ia[i]] * 100) / 100}")