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

async function fetchVoteData() {
    let jsonData: resultData;
    try {
        const response = await fetch('/');
        jsonData = await response.json();
    } catch (error) {
        console.error('Error fetching data:', error);
    }

    const mainTable = <HTMLTableElement>document.getElementById('leftTable');
    const leftTextArea = <HTMLTextAreaElement>document.getElementById('leftTextArea')
    displayData(leftTextArea, jsonData);
}

const fieldNameList : string[] = [];
const editableFieldNames: string[] = ["songTitle", "artistNames", "gameNames", "comments", "isAlt", "lyrics"]

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
function displayData(textArea :HTMLTextAreaElement, data: resultData) {
    let s = "";

    data.results.forEach((item, index) => {
        s = s.concat(`#${index+1} Artist - ${item.songTitle} - ${item.rating} ${item.operand}${item.adjustment}\n`)
    });

    textArea.rows = data.results.length + 5;
    textArea.textContent = s;
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

// Function to save edited data to the server
async function postVoteSubmissionsToGetResults(table: HTMLTableElement) {
    // const cells = table.rows[rowIndex].cells;
    // const dataToSave: submissionResult = <submissionResult>{};
    //
    // for (let i = 0; i < cells.length - 1; i++) {
    //     const input = <HTMLInputElement|HTMLTextAreaElement>cells[i].querySelector('input,textarea');
    //     const fieldName = fieldNameList[i];
    //     dataToSave[fieldName] = input.value;
    //     if (fieldName === "score") {
    //         dataToSave[fieldName] = Number.parseFloat(input.value)
    //     }
    // }
    //
    // try {
    //     const response = await fetch('/', {
    //         method: 'POST',
    //         headers: {
    //             'Content-Type': 'application/json'
    //         },
    //         body: JSON.stringify(dataToSave)
    //     });
    //
    //     if (response.ok) {
    //         console.log('Data saved successfully!');
    //     } else {
    //         throw new Error('Failed to save data: ' + response.statusText);
    //     }
    // } catch (error) {
    //     throw new Error('Error saving data: ' +  error);
    // }
}