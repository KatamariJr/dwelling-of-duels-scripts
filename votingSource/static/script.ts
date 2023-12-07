type resultData = {
    results: {
        place: number
        songTitle: string
        rating: string
        operand: string
        adjustment: number
    }[]
    deviants: {
       voter: string
       deviance: number
    }[]
}

type votesSubmissions = {
   votes: string
   voter: string
}[]

let voteSubmissionData: votesSubmissions;
let checkedIndexes: number[] = [];

async function fetchVoteSubmissions() {
    try {
        const response = await fetch('/loadFromFile');
        voteSubmissionData = (await response.json() as votesSubmissions);
    } catch (error) {
        console.error('Error fetching data:', error);
    }

    const rightGrid = <HTMLDivElement>document.getElementById('rightGrid')
    displayVoteSubmissions(rightGrid, voteSubmissionData);
}

// Function to create and display table rows from JSON data
function displayVoteResults(textArea :HTMLTextAreaElement, data: resultData) {
    let s = "";

    data.results.forEach((item, index) => {
        s = s.concat(`#${index+1} Artist - ${item.songTitle} - ${item.rating} ${item.operand}${item.adjustment}\n`)
    });

    textArea.rows = data.results.length + 5;
    textArea.textContent = s;
}

function displayVoteSubmissions(containingDiv: HTMLDivElement, data: votesSubmissions) {
    containingDiv.replaceChildren();

    data.forEach((v,i) => {
        let voteRow = document.createElement("div");

        let checkBox = document.createElement("input");
        checkBox.type = "checkbox";
        checkBox.id = String(i);
        checkBox.checked = true;
        checkBox.addEventListener("click", () => {
            if (checkedIndexes.includes(i)){
                checkedIndexes = checkedIndexes.filter((v) => {
                    return v != i;
                })
            } else {
                checkedIndexes.push(i)
            }
            postVoteSubmissionsToGetResults();
        })
        voteRow.append(checkBox);

        let voter = document.createElement("label");
        voter.setAttribute("for", String(i));
        voter.textContent = `${v.voter} : [votes here]`;
        voteRow.append(voter);

        containingDiv.appendChild(voteRow);
    })

}

async function postVoteSubmissionsToGetResults() {
    let jsonData: resultData;

    const leftTextArea = <HTMLTextAreaElement>document.getElementById('leftTextArea')

    let dataToSave = voteSubmissionData.flatMap((value, index) => {
        //if this row is checked, dont include it
        if (checkedIndexes.includes(index)) {
            return [];
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
            console.log('Data saved successfully!');
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