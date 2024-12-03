type resultData = {
    results: {
        place: number
        artist: string
        songTitle: string
        rating: string
        operand: string
        adjustment: number
    }[]
    voterCount: number
    deviants: {
       voter: string
       deviance: number
    }[]
}

type votesSubmissions = {
    submissionTime: string
    votes: string
    submitterEmail: string
    deviance: number
    uuid: string
}[]

let voteSubmissionData: votesSubmissions|null = null;
let disabledCheckedIndexes: number[] = [];
let reviewedCheckedIndexes: number[] = [];
let sortMethod: "time"|"deviance"|"email"|string = "time";

async function fetchVoteSubmissions() {
    try {
        const response = await fetch('/loadFromFile');
        voteSubmissionData = (await response.json() as votesSubmissions);
    } catch (error) {
        console.error('Error fetching data:', error);
        showModal("Error fetching data: " + error)
    }

    const rightGrid = <HTMLDivElement>document.getElementById('rightGrid')
    displayVoteSubmissions(rightGrid);
    postVoteSubmissionsToGetResults()
}

// event that is hooked onto the <option> element for changing votes sort.
function changeSort(e: InputEvent) {
    sortMethod = (e.target as HTMLSelectElement).value;
    if (voteSubmissionData === null) {
        return;
    }
    const rightGrid = <HTMLDivElement>document.getElementById('rightGrid')
    displayVoteSubmissions(rightGrid);
}

// Function to create and display table rows from JSON data
function displayVoteResults(textArea :HTMLTextAreaElement, data: resultData) {
    //update voteSubmission table with deviant info
    data.deviants.forEach((deviant) => {
        for (let vsd of voteSubmissionData) {
            if (vsd.submitterEmail === deviant.voter) {
                vsd.deviance = deviant.deviance;
                break;
            }
        }
    })
    const rightGrid = <HTMLDivElement>document.getElementById('rightGrid')
    displayVoteSubmissions(rightGrid);

    let s = "";

    data.results.forEach((item, index) => {
        s = s.concat(`#${index+1} ${item.artist} - ${item.songTitle} - ${item.rating} ${item.operand}${item.adjustment}\n`)
    });

    s += `\nVoters: ${data.voterCount}`

    textArea.rows = data.results.length + 5;
    textArea.textContent = s;
}

function displayVoteSubmissions(containingDiv: HTMLDivElement) {
    containingDiv.replaceChildren();

    //sort voteSubmissionData in a new array and use those indexes to map back onto the original data
    let sortedIndexes = Array.from(voteSubmissionData.keys())
        .sort((a, b) => {
            if (sortMethod === 'time') {
                let aDate = Date.parse(voteSubmissionData[a].submissionTime);
                let bDate = Date.parse(voteSubmissionData[b].submissionTime);
                return aDate < bDate ? -1 : 1;
            }
            if (sortMethod === "email") {
                let aEmail = voteSubmissionData[a].submitterEmail;
                let bEmail = voteSubmissionData[b].submitterEmail;
                return aEmail.localeCompare(bEmail);
            }
            if (sortMethod === "deviance") {
                let aDeviance = voteSubmissionData[a].deviance;
                let bDeviance = voteSubmissionData[b].deviance;
                return aDeviance < bDeviance ? -1 : 1;
            }
            return 0;
        })


    sortedIndexes.forEach((si) => {
        let v = voteSubmissionData[si];
        let i = si;
        let voteRow = document.createElement("div");

        let voteDate = new Date(Date.parse(v.submissionTime));

        let voter = document.createElement("span");
        let voterShortUUID = v.uuid.substring(0, 4);
        voter.textContent = `${v.submitterEmail} (${voterShortUUID}): ${voteDate.getMonth().toString().padStart(2, '0')}-${voteDate.getDate().toString().padStart(2, '0')} ${voteDate.getHours().toString().padStart(2, '0')}:${voteDate.getMinutes().toString().padStart(2, '0')}  deviance: ${v.deviance}`;
        voter.classList.add("clickable");

        voter.addEventListener("click", () => {
            putVotesInTextArea(<HTMLDivElement>document.getElementById('bottom'), v.submitterEmail, i);
        });

        let disableCheckBox = document.createElement("input");
        disableCheckBox.type = "checkbox";
        disableCheckBox.id = String(i);
        disableCheckBox.title = "Strike these votes from the results";
        if (disabledCheckedIndexes.includes(i)) {
            voter.classList.add("strike")
        }
        disableCheckBox.checked = !disabledCheckedIndexes.includes(i);
        disableCheckBox.addEventListener("change", () => {
            if (disabledCheckedIndexes.includes(i)){
                disabledCheckedIndexes = disabledCheckedIndexes.filter((v) => {
                    return v != i;
                })
            } else {
                disabledCheckedIndexes.push(i)
            }
            postVoteSubmissionsToGetResults();
        })
        voteRow.append(disableCheckBox);

        let reviewedCheckBox = document.createElement("input")
        reviewedCheckBox.type = "checkbox";
        reviewedCheckBox.title = "This voter left reviews";
        if (reviewedCheckedIndexes.includes(i)) {
            voter.classList.add("highlight")
        }
        reviewedCheckBox.checked = reviewedCheckedIndexes.includes(i);
        reviewedCheckBox.addEventListener("change", () => {
            if (reviewedCheckedIndexes.includes(i)){
                reviewedCheckedIndexes = reviewedCheckedIndexes.filter((v) => {
                    return v != i;
                })
            } else {
                reviewedCheckedIndexes.push(i)
            }
            postVoteSubmissionsToGetResults();
        })
        voteRow.append(reviewedCheckBox);

        voteRow.append(voter);

        containingDiv.appendChild(voteRow);
    })

}

async function postVoteSubmissionsToGetResults() {
    return sendVoteSubmissions("/process", true)
}

async function postVoteSubmissionsToSave() {
    return sendVoteSubmissions("/saveResults", false).then(() => {
        showModal("Results saved to results.json and results_for_discord.txt")
    })
}

async function sendVoteSubmissions(endpoint: string, displayOutput: boolean) {
    let jsonData: resultData;

    const leftTextArea = <HTMLTextAreaElement>document.getElementById('leftTextArea')

    let dataToSave = voteSubmissionData.flatMap((value, index) => {
        //if this row is checked, dont include it
        if (disabledCheckedIndexes.includes(index)) {
            return [];
        }
        if (reviewedCheckedIndexes.includes(index)) {
            return [value.submitterEmail + " (reviewed)", value.votes]
        }
        return [value.submitterEmail, value.votes]
    })

    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(dataToSave)
        });

        if (response.ok) {
            if (displayOutput){
                jsonData = await response.json();
                displayVoteResults(leftTextArea, jsonData);
            }
        } else {
            throw new Error('Failed to save data: ' + response.statusText);
        }
    } catch (error) {
        throw new Error('Error saving data: ' +  error);
    }

}

function putVotesInTextArea(element: HTMLDivElement, name: string, voteIndex: number) {
    if (voteSubmissionData === null) {
        return;
    }
    element.textContent = "";
    let vote = voteSubmissionData[voteIndex];
    let titleDiv = document.createElement("div");
    titleDiv.id = "titleDiv";
    let title = document.createElement("h3");
    title.textContent = "Votes for " + name;
    titleDiv.classList.add("stickyTop")
    titleDiv.append(title);
    element.append(titleDiv)
    let vDiv = document.createElement("div");
    vDiv.textContent = vote.votes;
    element.append(vDiv);

}

function showModal(content) {
    let dialog = document.createElement("dialog");

    let contentP = document.createElement("p")
    contentP.textContent = content;
    dialog.append(contentP)

    let closeButton = document.createElement("button")
    closeButton.textContent = "Close";
    closeButton.addEventListener('click', ev => {
        dialog.close();
        dialog.remove();
    })
    dialog.append(closeButton);

    document.getElementsByTagName('body')[0].append(dialog);
    dialog.showModal()
}