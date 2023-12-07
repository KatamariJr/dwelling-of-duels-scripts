type resultData = {
    results: {
        place: number
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
    votes: string
    voter: string
    deviance: number
}[]

let voteSubmissionData: votesSubmissions;
let disabledCheckedIndexes: number[] = [];
let reviewedCheckedIndexes: number[] = [];

async function fetchVoteSubmissions() {
    try {
        const response = await fetch('/loadFromFile');
        voteSubmissionData = (await response.json() as votesSubmissions);
    } catch (error) {
        console.error('Error fetching data:', error);
    }

    const rightGrid = <HTMLDivElement>document.getElementById('rightGrid')
    displayVoteSubmissions(rightGrid, voteSubmissionData);
    postVoteSubmissionsToGetResults()
}

// Function to create and display table rows from JSON data
function displayVoteResults(textArea :HTMLTextAreaElement, data: resultData) {
    //update voteSubmission table with deviant info
    data.deviants.forEach((deviant) => {
        for (let vsd of voteSubmissionData) {
            if (vsd.voter === deviant.voter) {
                vsd.deviance = deviant.deviance;
                break;
            }
        }
    })
    const rightGrid = <HTMLDivElement>document.getElementById('rightGrid')
    displayVoteSubmissions(rightGrid, voteSubmissionData);

    let s = "";

    data.results.forEach((item, index) => {
        s = s.concat(`#${index+1} Artist - ${item.songTitle} - ${item.rating} ${item.operand}${item.adjustment}\n`)
    });

    s += `\nVoters: ${data.voterCount}`

    textArea.rows = data.results.length + 5;
    textArea.textContent = s;
}

function displayVoteSubmissions(containingDiv: HTMLDivElement, data: votesSubmissions) {
    containingDiv.replaceChildren();

    data.forEach((v,i) => {
        let voteRow = document.createElement("div");

        let voter = document.createElement("label");
        voter.setAttribute("for", String(i));
        voter.textContent = `${v.voter} : [votes here]   deviance: ${v.deviance}`;

        let disableCheckBox = document.createElement("input");
        disableCheckBox.type = "checkbox";
        disableCheckBox.id = String(i);
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
    let jsonData: resultData;

    const leftTextArea = <HTMLTextAreaElement>document.getElementById('leftTextArea')

    let dataToSave = voteSubmissionData.flatMap((value, index) => {
        //if this row is checked, dont include it
        if (disabledCheckedIndexes.includes(index)) {
            return [];
        }
        if (reviewedCheckedIndexes.includes(index)) {
            return [value.voter + " (reviewed)", value.votes]
        }
        return [value.voter, value.votes]
    })

    try {
        const response = await fetch('/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(dataToSave)
        });

        if (response.ok) {
            console.log('Votes processed successfully!');
            jsonData = await response.json();
            displayVoteResults(leftTextArea, jsonData);
        } else {
            throw new Error('Failed to save data: ' + response.statusText);
        }
    } catch (error) {
        throw new Error('Error saving data: ' +  error);
    }

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