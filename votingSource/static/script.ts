type submissionData = {
    data: submissionResult[]
    problemIDs: string[]
}

type submissionResult = {
    uuid: string
    submissionTime: string
    songTitle: string
    artistNames: string
    gameNames: string
    comments: string
    submitterEmail: string
    isAlt: boolean | string
    filename: string
    lyrics: string
    score: number
    identity: identity
}

type voteData = voteResult[]

type voteResult = {
    uuid: string
    submissionTime: string
    submitterEmail: string
    score: number
    identity: identity
}

type identity = {
    ip: string
    caller: string
    userAgent: string
}

async function fetchVoteData() {
    let jsonData: voteData;
    try {
        const response = await fetch('/');
        jsonData = await response.json();
    } catch (error) {
        console.error('Error fetching data:', error);
    }

    const mainTable = <HTMLTableElement>document.getElementById('mainTable');
    displayData(mainTable, jsonData);
}

const fieldNameList : string[] = [];
const editableFieldNames: string[] = ["songTitle", "artistNames", "gameNames", "comments", "isAlt", "lyrics"]
const identityIndex: identity[] = [];

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
function displayData(table :HTMLTableElement, data: submissionResult[]|voteResult[]) {
    let head = table.createTHead()

    //get title row names
    const row = head.insertRow();

    Object.keys(data[0]).forEach(key => {
        if (key === "identity") {
            return
        }
        row.insertCell().textContent = key;
        fieldNameList.push(key);
    });

    let body = table.createTBody()

    data.forEach((item, index) => {

        const saveButton = document.createElement('button');
        saveButton.textContent = 'Save';
        saveButton.addEventListener('click', () => {
            saveButton.textContent = 'Save ⏳';
            saveData(table, index + 1).then(r  =>{
                saveButton.textContent = 'Save ✔';
                removeChangedClassFromRow(table, index)
            }, r => {
                showModal(r)
                console.error(r)
                saveButton.textContent = 'Save ❌';
            });
        });

        const row = body.insertRow();
        Object.keys(item).forEach(key => {
            const value = item[key]
            if (key === "identity") {
                identityIndex[index] = value;
                return
            }

            const cell = row.insertCell();
            let input: HTMLInputElement | HTMLTextAreaElement = document.createElement("input");
            input.type = "text";
            if (key === "comments" || key === "lyrics") {
                input = document.createElement("textarea");
                input.setAttribute("rows", "1");
            }
            if (key === "votes") {
                input = document.createElement("textarea");
                input.setAttribute("rows", "35");
                input.setAttribute("cols", "100");
                input.setAttribute("wrap", "off");
            }
            input.value = value;
            if (!editableFieldNames.includes(key)) {
                input.setAttribute("disabled", "true")
            }
            cell.insertAdjacentElement('afterbegin', input)

            cell.addEventListener('input', () => {
                input.classList.add("changed")
                saveButton.classList.add("changed")
            })

        });

        row.insertCell().appendChild(saveButton);
    });
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
async function saveData(table: HTMLTableElement, rowIndex: number) {
    const cells = table.rows[rowIndex].cells;
    const dataToSave: submissionResult = <submissionResult>{};

    for (let i = 0; i < cells.length - 1; i++) {
        const input = <HTMLInputElement|HTMLTextAreaElement>cells[i].querySelector('input,textarea');
        const fieldName = fieldNameList[i];
        dataToSave[fieldName] = input.value;
        if (fieldName === "score") {
            dataToSave[fieldName] = Number.parseFloat(input.value)
        }
    }

    dataToSave.identity = identityIndex[rowIndex-1]

    try {
        const response = await fetch('/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(dataToSave)
        });

        if (response.ok) {
            console.log('Data saved successfully!');
        } else {
            throw new Error('Failed to save data: ' + response.statusText);
        }
    } catch (error) {
        throw new Error('Error saving data: ' +  error);
    }
}