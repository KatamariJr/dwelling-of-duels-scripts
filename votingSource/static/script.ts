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
    console.debug("clicked???")

    const leftTextArea = <HTMLTextAreaElement>document.getElementById('leftTextArea')
    let dataToSave = [
        "bob",
        "Baba Is You - Rocket Is Dust / good +0.16\n" +
        "Batman [NES] - Punch Punch / good -0.38\n" +
        "Blazing Chrome - Time to Blaze / good +0.38\n" +
        "Chrono Trigger - The Secret of the Forest / good +0.03\n" +
        "Contra 3: The Alien Wars, Contra 4 - Let's attack aBRASSively! / incredible -0.29\n" +
        "Environmental Station Alpha - 6-bit / average -0.47\n" +
        "Final Fantasy 5, Final Fantasy 6, Final Fantasy 7 - Let The Decisive Battle On The Big Bridge Begin! / incredible -0.26\n" +
        "Fire Emblem: Three Houses - God Shattering Star / incredible +0.00\n" +
        "Mega Man 6 - templant man / average -0.46\n" +
        "Metal Slug - Starry Cinnamon Skies / good -0.43\n" +
        "NieR: Automata - Milonga del Carnaval de las Máquinas Tristes (Milonga from the Carnival of the Sad Machines) / above average +0.12\n" +
        "Ninja Gaiden, Ninja Gaiden II: The Dark Sword of Chaos, Ninja Gaiden III: The Ancient Ship of Doom - Ninja Gaiden Trilogy / my song\n" +
        "Pac-Man 2: The New Adventures - Pac-Man 2: 1 Guitar / above average -0.29\n" +
        "Pictionary - Pictiognarly: Shred the Wet / above average +0.09\n" +
        "Pokemon Ruby/Sapphire - My Body Is Regi / below average +0.31\n" +
        "Punch-Out!! - Finished with Mike Tyson / below average +0.13\n" +
        "Resident Evil 4 - SAVE LEON K / below average -0.08\n" +
        "Terranigma - Sleepy Seaport / average -0.33\n" +
        "Undertale, Touhou 4: Lotus Land Story - That's Bullet Hell You're Walking Into / above average +0.16\n" +
        "Ys 6: The Ark of Napishtim - Ocean SpraYs / above average +0.28",
        "tibone",
        "Baba Is You - Rocket Is Dust / above average +0.00\n" +
        "Batman [NES] - Punch Punch / good +0.01\n" +
        "Blazing Chrome - Time to Blaze / incredible +0.00\n" +
        "Chrono Trigger - The Secret of the Forest / incredible -0.49\n" +
        "Contra 3: The Alien Wars, Contra 4 - Let's attack aBRASSively! / good +0.01\n" +
        "Environmental Station Alpha - 6-bit / average +0.42\n" +
        "Final Fantasy 5, Final Fantasy 6, Final Fantasy 7 - Let The Decisive Battle On The Big Bridge Begin! / good +0.38\n" +
        "Fire Emblem: Three Houses - God Shattering Star / incredible +0.00\n" +
        "Mega Man 6 - templant man / my song\n" +
        "Metal Slug - Starry Cinnamon Skies / good -0.01\n" +
        "NieR: Automata - Milonga del Carnaval de las Máquinas Tristes (Milonga from the Carnival of the Sad Machines) / average +0.00\n" +
        "Ninja Gaiden, Ninja Gaiden II: The Dark Sword of Chaos, Ninja Gaiden III: The Ancient Ship of Doom - Ninja Gaiden Trilogy / above average +0.49\n" +
        "Pac-Man 2: The New Adventures - Pac-Man 2: 1 Guitar / good +0.15\n" +
        "Pictionary - Pictiognarly: Shred the Wet / average +0.00\n" +
        "Pokemon Ruby/Sapphire - My Body Is Regi / average +0.00\n" +
        "Punch-Out!! - Finished with Mike Tyson / below average +0.01\n" +
        "Resident Evil 4 - SAVE LEON K / average +0.00\n" +
        "Terranigma - Sleepy Seaport / average +0.00\n" +
        "Undertale, Touhou 4: Lotus Land Story - That's Bullet Hell You're Walking Into / good +0.02\n" +
        "Ys 6: The Ark of Napishtim - Ocean SpraYs / good +0.42"
    ];

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