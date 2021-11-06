def splitName(filename):
    print("\n\n")
    split = filename.split("-")

    # check if this has extra dashes inside of it
    if len(split) > 5:
        # get user intervention
        print("AMBIGUOUS DASHES!!!\n")
        print(split)
        combineString = input("Please input a combine index string (e.g. '0 1,2 3 4 5') where each comma will join two fragments:")
        split = mergeSplits(split, combineString, "-")

    rank = split[0]
    if rank == "ZZ":
        rank = "ALT"

    artist = split[1]
    game = split[2]
    title = split[3]

    if artist == "Anon":
        artist = "Anonymous DoD Contestant"

    return rank, artist, game, title

def mergeSplits(split, combineString, mergeCharacter):

    combines = combineString.split(" ")

    maxLen = len(split)

    result = []

    for c in combines:
        indexes = c.split(",")

        stringsToJoin = []
        for i in indexes:
            if int(i) > maxLen:
                raise Exception("value {i} is not an acceptable index")
            stringsToJoin.append(split[int(i)])
        result.append(mergeCharacter.join(stringsToJoin))

    return result
