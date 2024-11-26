////UI
copyBtn.addEventListener(MouseEvent.CLICK, copyVotes)
function copyVotes(e:MouseEvent) {
	System.setClipboard(phpbb.text)
}


////calculation
var songs:Array = []
var i:Number
var theData:String
var theResults:Array = []

var averagesTotal:Array
var averagedZscoresTotal:Array
var finalZscores:Array

var myTextLoader:URLLoader = new URLLoader();

myTextLoader.addEventListener(Event.COMPLETE, onLoaded);

function onLoaded(e:Event):void {
	theData = e.target.data
	sortData()
	
	averages()
	averagedZscores()
	
	calculateResults(averagedZscoresTotal)
	
	findDeviants(averagedZscoresTotal)
}

myTextLoader.load(new URLRequest("votes.txt"));

function sortData() {
	var dataArray:Array = theData.split("\r\n")
	
	var voter:String
	var reviewed:Boolean
	var scores:Array = []
	
	var process:Number = 0
	
	function resetData() {
		process = 0
		theResults.push({voter:voter, scores:scores, reviewed:reviewed})
		voter = ""
		reviewed = false
		scores = []
	}
	
	//populate songs list
	for (i = 2; i < 100; i++) {
		var songTitle:String = dataArray[i].split(" / ")[0]
		if (songTitle == "") {
			i = 100
		} else {
			songs.push(songTitle)
		}
	}
	
	for (i = 0; i < dataArray.length; i++) {
		if (process == 0) {
			voter = dataArray[i]
			if (dataArray[i].split("reviewed").length > 1) {
				reviewed = true
			}
			process ++
		} else if (process == 1) {
			process ++
		} else if (process == 2) {
			if (dataArray[i] == "") {
				resetData()
			} else {
				var theRating:String = dataArray[i].split(" / ")[1]
				if (theRating.toLowerCase() == "my song") {
					num = undefined
				} else {
					var word:String = theRating.split(" +0")[0]
					word = word.split(" -0")[0]
					var modifier:Number
					if (theRating.split(" +0").length > 1) modifier = Number(theRating.split(" +0")[1])
					else {
						modifier = -Number(theRating.split(" -0")[1])
					}
					word = word.toLowerCase()
					
					var num:Number
					if (word == "terrible") num = 1
					if (word == "bad") num = 2
					if (word == "below average") num = 3
					if (word == "average") num = 4
					if (word == "above average") num = 5
					if (word == "good") num = 6
					if (word == "incredible") num = 7
					if (word == "my song") num = undefined
				}
				
				scores.push(num + modifier)
				//trace(i, num, modifier, theRating)
				
				if (i == dataArray.length - 1) {
					resetData()
				}
			}
		}
	}
}

function averages() {
	var counts:Array = []
	var totals:Array = []
	var ratingCounts:Array = []
	
	//populate arrays
	for (i = 0; i < theResults[0].scores.length; i++) {
		counts[i] = 0
		totals[i] = 0
	}
	for (i = 0; i < 7; i++) {
		ratingCounts[i] = 0
	}
	
	//total up the averages
	for (i = 0; i < theResults.length; i++) {
		//trace("RANK " + theResults[i].ranks)
		for (var j = 0; j < theResults[i].scores.length; j++) {
			if (!isNaN(theResults[i].scores[j])) {
				totals[j] += theResults[i].scores[j]
				counts[j] ++
				ratingCounts[theResults[i].scores[j] - 1]++
			}
		}
	}
	
	//trace(ratingCounts)
	
	for (i = 0; i < theResults[0].scores.length; i++) {
		totals[i] /= counts[i]
	}
	
	averagesTotal = totals
	//trace(totals.sort(Array.RETURNINDEXEDARRAY | Array.NUMERIC | Array.DESCENDING))
}

function averagedZscores() {
	var counts:Array = []
	var totals:Array = []
	var means:Array = []
	var meanBalance:Array = []
	var means2:Array = []
	var stddevs:Array = []
	var theZscores:Array = []
	var j:Number
	var count:Number
	var count2:Number
	var allTotal:Number
	var songTotal:Number
	var entrants:Array = []
	
	//populate arrays
	for (i = 0; i < theResults.length; i++) {
		means[i] = 0
		meanBalance[i] = 0
		stddevs[i] = 0
		theZscores[i] = []
	}
	for (i = 0; i < theResults[0].scores.length; i++) {
		means2[i] = 0
		counts[i] = 0
		totals[i] = 0
	}
	
	//find means
	for (i = 0; i < theResults.length; i++) {
		count = 0
		for (j = 0; j < theResults[i].scores.length; j++) {
			if (!isNaN(theResults[i].scores[j])) {
				count ++
				means[i] += theResults[i].scores[j]
			}
		}
		means[i] /= count
	}
	
	//create the auto vote
	for (i = 0; i < theResults.length; i++) {
		for (j = 0; j < theResults[i].scores.length; j++) {
			if (isNaN(theResults[i].scores[j])) {
				//get all others' average
				count = 0
				allTotal = 0
				count2 = 0
				songTotal = 0
				for (var k = 0; k < theResults.length; k++) {
					if (k != i) {
						for (var m = 0; m < theResults[k].scores.length; m++) {
							if (!isNaN(theResults[k].scores[m])) {
								count++
								allTotal += theResults[k].scores[m]
								//get song average
								if (m == j) {
									count2++
									songTotal += theResults[k].scores[m]
								}
							}
						}
					}
				}
				allTotal /= count
				songTotal /= count2
				entrants.push([i, j, means[i] + songTotal - allTotal])
			}
		}
	}
	
	for (i = 0; i < entrants.length; i++) {
		theResults[entrants[i][0]].scores[entrants[i][1]] = entrants[i][2]
	}
	
	//find stddevs
	for (i = 0; i < theResults.length; i++) {
		count = 0
		for (j = 0; j < theResults[i].scores.length; j++) {
			if (!isNaN(theResults[i].scores[j])) {
				count ++
				stddevs[i] += Math.pow(theResults[i].scores[j] - means[i], 2)
			}
		}
		stddevs[i] = Math.sqrt(stddevs[i] / count)
	}
	
	//calculate zscores
	for (i = 0; i < theResults.length; i++) {
		count = 0
		for (j = 0; j < theResults[i].scores.length; j++) {
			if ((!isNaN(theResults[i].scores[j])) && (stddevs[i] != 0)) {
				theZscores[i][j] = (theResults[i].scores[j] - means[i]) / stddevs[i]
			} else theZscores[i][j] = undefined
		}
	}
	
	//add up the zscores
	for (i = 0; i < theZscores.length; i++) {
		var reviewModifier:Number = 1
		if (theResults[i].reviewed == true) reviewModifier = 1.2
		for (j = 0; j < theZscores[i].length; j++) {
			if (!isNaN(theZscores[i][j])) {
				counts[j] ++
				totals[j] += theZscores[i][j] * reviewModifier
			}
		}
	}
	
	for (i = 0; i < totals.length; i++) {
		totals[i] /= counts[i]
	}
	
	averagedZscoresTotal = totals
	//trace(totals.sort(Array.RETURNINDEXEDARRAY | Array.NUMERIC | Array.DESCENDING))
	finalZscores = theZscores
}

function calculateResults(theArray:Array) {
	var finals:Array = theArray.sort(Array.NUMERIC | Array.DESCENDING | Array.RETURNINDEXEDARRAY)
	var num:Number
	
	var highScore:Number = averagesTotal[finals[0]]
	var lowScore:Number = averagesTotal[finals[finals.length - 1]]
	var zHigh:Number = theArray[finals[0]]
	var zLow:Number = theArray[finals[finals.length - 1]]
	
	var multiplier:Number = (highScore - lowScore) / (zHigh - zLow)
	var subtracter:Number = zLow
	var adder:Number = lowScore
	
	for (var k = 0; k < finals.length; k++) {
		if (k > 0) {
			if (theArray[finals[k]] != theArray[finals[k - 1]]) num = k
		} else num = k
		
		var pulledScore:Number = (theArray[finals[k]] - subtracter) * multiplier + adder
		var roundedScore:Number = Math.round(pulledScore)
		var word:String
		
		if (roundedScore == 1) word = "terrible"
		if (roundedScore == 2) word = "bad"
		if (roundedScore == 3) word = "below average"
		if (roundedScore == 4) word = "average"
		if (roundedScore == 5) word = "above average"
		if (roundedScore == 6) word = "good"
		if (roundedScore == 7) word = "incredible"
		
		var adj:Number = pulledScore - roundedScore
		var operand:String
		if (adj < 0) operand = " -"
		else operand = " +"
		adj = Math.abs(Math.floor(adj * 100) / 100)
		
		var percentage:Number = (theArray[finals[k]] - zLow) / (zHigh - zLow)
		var red:String = ((1 - percentage) * 255).toString(16)
		while (red.length < 2) red = "0" + red
		var green:String = (percentage * 255).toString(16)
		while (green.length < 2) green = "0" + green
		var color:String = "[color=#" + red + green + "00]"
		
		phpbb.appendText("#" + (num + 1) + " Artist - " + songs[finals[k]] + " - " + color + word + operand + adj + "[/color]\n")
	}
	phpbb.appendText("Voters: " + theResults.length)
}

function findDeviants(theArray:Array) {
	var devTotals:Array = []
	var avgDev:Number = 0
	for (i = 0; i < finalZscores.length; i++) {
		var devTotal:Number = 0
		for (var j = 0; j < finalZscores[i].length; j++) {
			devTotal += Math.pow(finalZscores[i][j] - theArray[j], 2)
		}
		devTotal /= finalZscores[i].length
		devTotals.push(devTotal)
		avgDev += devTotal
	}
	avgDev /= finalZscores.length
	
	var ia:Array = devTotals.sort(Array.NUMERIC | Array.RETURNINDEXEDARRAY | Array.DESCENDING)
	for (i = 0; i < finalZscores.length; i++) {
		deviants.appendText(theResults[ia[i]].voter + ": " + Math.round(devTotals[ia[i]] * 100) / 100 + "\n")
	}
	deviants.appendText("\nDeviance average: " + avgDev)
}