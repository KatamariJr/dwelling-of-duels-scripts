let currentSortKey = null;
let mainSubmissionDataResults;
let altSubmissionDataResults;
let sortedMainSubmissionResultIndexes = null;
let sortedAltSubmissionResultIndexes = null;
// Function to fetch JSON data from the server
async function fetchSubmissionData() {
    let jsonData;
    try {
        const response = await fetch('/fetch');
        jsonData = await response.json();
    }
    catch (error) {
        console.error('Error fetching data:', error);
    }
    if (jsonData.problemIDs.length > 0) {
        let problemsParagraph = document.getElementById('problems');
        problemsParagraph.textContent = "PROBLEMS: NO MP3: " + jsonData.problemIDs.join(", ");
    }
    //filter data based on IsAlt and display in either table
    mainSubmissionDataResults = jsonData.data.filter((v) => {
        return v.isAlt === "false";
    });
    altSubmissionDataResults = jsonData.data.filter((v) => {
        return v.isAlt === "true";
    });
    const mainTable = document.getElementById('mainTable');
    const altTable = document.getElementById('altTable');
    if (mainSubmissionDataResults.length > 0) {
        displayData(mainTable, "main");
    }
    if (altSubmissionDataResults.length > 0) {
        displayData(altTable, "alt");
    }
}
const fieldNameList = [];
const editableFieldNames = ["songTitle", "artistNames", "gameNames", "comments", "isAlt", "lyrics"];
const identityIndex = [];
function showModal(content) {
    let dialog = document.createElement("dialog");
    let contentP = document.createElement("p");
    contentP.textContent = content;
    dialog.append(contentP);
    let closeButton = document.createElement("button");
    closeButton.textContent = "Close";
    closeButton.addEventListener('click', ev => {
        dialog.close();
        dialog.remove();
    });
    dialog.append(closeButton);
    document.getElementsByTagName('body')[0].append(dialog);
    dialog.showModal();
}
// Function to create and display table rows from JSON data
function displayData(table, dataType) {
    table.replaceChildren();
    let data;
    if (dataType === "main") {
        data = mainSubmissionDataResults;
    }
    else if (dataType === "alt") {
        data = altSubmissionDataResults;
    }
    let indexes = Array.from(data.keys()).sort((a, b) => {
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
            || currentSortKey == "uuid") {
            let aTitle = data[a][currentSortKey];
            let bTitle = data[b][currentSortKey];
            return aTitle.localeCompare(bTitle);
        }
        return 0;
    });
    let head = table.createTHead();
    //get title row names
    const row = head.insertRow();
    Object.keys(data[0]).forEach(key => {
        if (key === "identity") {
            return;
        }
        let headerCell = row.insertCell();
        headerCell.textContent = key;
        headerCell.addEventListener('click', () => {
            currentSortKey = key;
            displayData(table, dataType);
        });
        fieldNameList.push(key);
    });
    let body = table.createTBody();
    indexes.forEach((si, visualIndex) => {
        let item = data[si];
        let index = si;
        const saveButton = document.createElement('button');
        saveButton.textContent = 'Save';
        saveButton.addEventListener('click', () => {
            saveButton.textContent = 'Save ⏳';
            saveData(table, visualIndex + 1).then(r => {
                saveButton.textContent = 'Save ✔';
                removeChangedClassFromRow(table, visualIndex);
            }, r => {
                showModal(r);
                console.error(r);
                saveButton.textContent = 'Save ❌';
            });
        });
        const row = body.insertRow();
        Object.keys(item).forEach(key => {
            const value = item[key];
            if (key === "identity") {
                identityIndex[index] = value;
                return;
            }
            const cell = row.insertCell();
            let input = document.createElement("input");
            input.type = "text";
            if (key === "comments" || key === "lyrics") {
                input = document.createElement("textarea");
                input.setAttribute("rows", "1");
            }
            input.value = value;
            if (!editableFieldNames.includes(key)) {
                input.setAttribute("disabled", "true");
            }
            cell.insertAdjacentElement('afterbegin', input);
            cell.addEventListener('input', () => {
                input.classList.add("changed");
                saveButton.classList.add("changed");
            });
        });
        row.insertCell().appendChild(saveButton);
    });
}
function removeChangedClassFromRow(table, rowIndex) {
    Object.keys(table.rows).forEach((rowKey) => {
        if (Number(rowKey) !== Number(rowIndex + 1)) {
            return;
        }
        let affectedTableRow = table.rows[rowKey];
        //remove class from all cells
        Object.keys(affectedTableRow.cells).forEach((columnKey) => {
            let cellInputs = Array.from(affectedTableRow.cells[columnKey].getElementsByTagName('input'));
            let cellButtons = Array.from(affectedTableRow.cells[columnKey].getElementsByTagName('button'));
            let cellTextAreas = Array.from(affectedTableRow.cells[columnKey].getElementsByTagName('textarea'));
            let changedInputs = cellInputs.concat(cellButtons).concat(cellTextAreas);
            if (changedInputs.length === 0) {
                return;
            }
            changedInputs[0].classList.remove('changed');
        });
    });
}
// Function to save edited data to the server
async function saveData(table, rowIndex) {
    const cells = table.rows[rowIndex].cells;
    const dataToSave = {};
    for (let i = 0; i < cells.length - 1; i++) {
        const input = cells[i].querySelector('input,textarea');
        const fieldName = fieldNameList[i];
        dataToSave[fieldName] = input.value;
        if (fieldName === "score") {
            dataToSave[fieldName] = Number.parseFloat(input.value);
        }
    }
    dataToSave.identity = identityIndex[rowIndex - 1];
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
        }
        else {
            throw new Error('Failed to save data: ' + response.statusText);
        }
    }
    catch (error) {
        throw new Error('Error saving data: ' + error);
    }
}
//# sourceMappingURL=script.js.map