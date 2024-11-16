type submissionData = {
    data: submissionResult[]
    problems: problem[]
    deletedData?: submissionResult[]
}

type problem = {
    id: string
    kind: string
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

type identity = {
    ip: string
    caller: string
    userAgent: string
}

let currentSortKey = null;
let mainSubmissionDataResults : submissionResult[];
let altSubmissionDataResults : submissionResult[];
let problemSubmissionDataResults : submissionResult[];
let deletedSubmissionDataResults : submissionResult[];
let sortedMainSubmissionResultIndexes: number[]|null = null;
let sortedAltSubmissionResultIndexes: number[]|null = null;

// Function to fetch JSON data from the server
async function fetchSubmissionData() {
    let jsonData: submissionData;
    try {
        const response = await fetch('/fetch');
        jsonData = await response.json();
    } catch (error) {
        console.error('Error fetching data:', error);
    }

    //filter data into problem, main, alt, and deleted lists
    mainSubmissionDataResults = jsonData.data.filter((v) => {
        return v.isAlt === "false"
    })
    altSubmissionDataResults = jsonData.data.filter((v) => {
        return v.isAlt === "true"
    })
    console.debug(jsonData)

    problemSubmissionDataResults = jsonData.data.filter((v, index, array) => {

        return jsonData.problems.map(value => value.id).includes(v.uuid);
    })
    console.debug(problemSubmissionDataResults)
    deletedSubmissionDataResults = jsonData.deletedData;

    const mainTable = <HTMLTableElement>document.getElementById('mainTable');
    const altTable = <HTMLTableElement>document.getElementById('altTable');
    const problemDiv = <HTMLDivElement>document.getElementById('problemTable');
    const deletedTable = <HTMLTableElement>document.getElementById('deletedTable');
    if (mainSubmissionDataResults.length > 0) {
        displayData(mainTable, "main");
    }
    if (altSubmissionDataResults.length > 0) {
        displayData(altTable, "alt");
    }
    if (problemSubmissionDataResults.length > 0) {
        //TODO show this in a separate location with buttons to remove them
        problemSubmissionDataResults.forEach((v,i) => {

            let p = document.createElement("p");
            p.textContent = `orphaned song data: ${v.songTitle} by ${v.artistNames}`;
            let pButton = document.createElement("button")
            pButton.textContent = "remove"
            pButton.addEventListener("click", ev => {
                showModal("nothing yet")
            })
            p.appendChild(pButton);
            problemDiv.appendChild(p)
        })

    }
    if (deletedSubmissionDataResults.length > 0) {
        displayData(deletedTable, "deleted")
    }

    document.getElementById("songCount").textContent = `${jsonData.data.length} submissions, ${mainSubmissionDataResults.length} mains, ${altSubmissionDataResults.length} alts`
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
function displayData(table :HTMLTableElement, dataType: "alt"|"main"|"deleted") {
    table.replaceChildren();
    let data: submissionResult[];
    switch (dataType) {
        case "main":
            data = mainSubmissionDataResults;
            break;
        case "alt":
            data = altSubmissionDataResults;
            break;
        case "deleted":
            data = deletedSubmissionDataResults;
            break;
    }

    let indexes = Array.from(data.keys()).sort((a,b) => {
        if (currentSortKey === "submissionTime") {
            let aDate = Date.parse(data[a].submissionTime);
            let bDate = Date.parse(data[b].submissionTime);
            return aDate < bDate ? -1 : 1;
        }
        if (currentSortKey === "score") {
            let aScore = data[a].score;
            let bScore = data[b].score;
            return aScore < bScore ? -1 : 1;
        }
        if (currentSortKey === "songTitle"
            || currentSortKey === "artistNames"
            || currentSortKey === "gameNames"
            || currentSortKey === "comments"
            || currentSortKey === "filename"
            || currentSortKey == "isAlt"
            || currentSortKey == "submitterEmail"
            || currentSortKey == "lyrics"
            || currentSortKey == "uuid"
        ) {
            let aTitle = data[a][currentSortKey];
            let bTitle = data[b][currentSortKey];
            return aTitle.localeCompare(bTitle);
        }
        return 0
    })

    let head = table.createTHead()

    //get title row names
    const row = head.insertRow();

    row.insertCell()
    fieldNameList.push("save")

    Object.keys(data[0]).forEach(key => {
        if (key === "identity") {
            return
        }
        let headerCell = row.insertCell();
        headerCell.textContent = key;
        headerCell.addEventListener('click', () => {
            currentSortKey = key;
            displayData(table, dataType);
        });
        fieldNameList.push(key);
    });

    let body = table.createTBody()

    indexes.forEach((si, visualIndex) => {
        let item = data[si];
        let index = si;
        const saveButton = document.createElement('button');
        saveButton.textContent = 'Save';
        saveButton.addEventListener('click', () => {
            saveButton.textContent = 'Save ⏳';
            saveData(table, visualIndex + 1).then(r  =>{
                saveButton.textContent = 'Save ✔';
                removeChangedClassFromRow(table, visualIndex)
            }, r => {
                showModal(r)
                console.error(r)
                saveButton.textContent = 'Save ❌';
            });
        });

        const deleteButton = document.createElement('button');

        if (dataType !== "deleted") {
            deleteButton.textContent = 'Delete';
            deleteButton.addEventListener('click', async () => {
                deleteButton.textContent = 'Delete ⏳';
                let uuid = item.uuid.endsWith(".json") ? item.uuid.substring(0, item.uuid.length-5) : item.uuid;

                const response = await fetch(`/delete/${uuid}`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                })
                if (response.ok) {
                    deleteButton.textContent = 'Deleted ✔';
                    removeChangedClassFromRow(table, visualIndex)
                } else {
                    let errText = await response.text();
                    showModal(errText)
                    console.error(errText)
                    deleteButton.textContent = 'Delete ❌';
                }

            });
        } else { //it is a deleted song
            deleteButton.textContent = 'Un-delete';
            deleteButton.addEventListener('click', async () => {
                deleteButton.textContent = 'Un-delete ⏳';
                let uuid = item.uuid.endsWith(".json") ? item.uuid.substring(0, item.uuid.length-5) : item.uuid;

                const response = await fetch(`/undelete/${uuid}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                })
                if (response.ok) {
                    deleteButton.textContent = 'Un-deleted ✔';
                    removeChangedClassFromRow(table, visualIndex)
                } else {
                    let errText = await response.text();
                    showModal(errText)
                    console.error(errText)
                    deleteButton.textContent = 'Un-delete ❌';
                }
            });
        }


        const row = body.insertRow();
        row.insertCell().appendChild(saveButton);

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
            if (key === "isAlt" || key === "score") {
                input.setAttribute("size", "5")
            }
            if (key === "gameNames" || key === "artistNames") {
                input.setAttribute("size", "50")
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

        row.insertCell().appendChild(deleteButton);

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

    // loop over all cells in this row and try to get their content to save it
    for (let i = 0; i < cells.length - 1; i++) {
        const input = <HTMLInputElement|HTMLTextAreaElement|null>cells[i].querySelector('input,textarea');
        if (input === null) {
            continue
        }
        //NOTE: this minus one came from needing to offset the save button that was added at the front of the rows.
        //There must be a way we can relate these cells not directly by their index, but by the column they are in.
        //Maybe directly use the column names as a map?
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