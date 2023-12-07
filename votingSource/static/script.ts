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

async function fetchVoteData() {
    let jsonData: votesSubmissions;
    try {
        const response = await fetch('/loadFromFile');
        jsonData = (await response.json() as votesSubmissions);
    } catch (error) {
        console.error('Error fetching data:', error);
    }

    const rightGrid = <HTMLDivElement>document.getElementById('rightGrid')
    displayVoteSubmissions(rightGrid, jsonData);
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
        checkBox.checked = true;
        voteRow.append(checkBox);

        let voter = document.createElement("span");
        voter.textContent = `${v.voter} : [votes here]`;
        voteRow.append(voter);

        containingDiv.appendChild(voteRow);
    })


}

function removeChangedClassFromRow(table: HTMLTableElement, rowIndex: number) {
    Object.keys(table.rows).forEach((rowKey) => {
        if (Number(rowKey) !== Number(rowIndex+1)) {
            return;
        }
        let affectedTableRow: HTMLTableRowElement = table.rows[rowKey];

        //remove class from all cells
        Object.keys(affectedTableRow.cells).forEach((columnKey) => {
            let cellInputs: HTMLElement[] = Array.from(affectedTableRow.cells[columnKey].getElementsByTagName('input'));
            let cellButtons: HTMLElement[] = Array.from(affectedTableRow.cells[columnKey].getElementsByTagName('button'));
            let cellTextAreas: HTMLElement[] = Array.from(affectedTableRow.cells[columnKey].getElementsByTagName('textarea'));

            let changedInputs: HTMLElement[] = cellInputs.concat(cellButtons).concat(cellTextAreas)

            if (changedInputs.length === 0){
                return;
            }

            changedInputs[0].classList.remove('changed')
        })

    })
}


async function postVoteSubmissionsToGetResults(table: HTMLTableElement) {

    const leftTextArea = <HTMLTextAreaElement>document.getElementById('leftTextArea')
    let dataToSave = {};

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



    let jsonData: resultData;
    try {
        const response = await fetch('/text');

    } catch (error) {
        console.error('Error fetching data:', error);
    }


}