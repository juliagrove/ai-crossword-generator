// crossword/static/js/crossword.js
function initCrosswordPage() {
    const form = document.getElementById('crosswordForm');
    if (!form) return;

    form.addEventListener('submit', function (e) {
        e.preventDefault();

        const formData = new FormData(form);
        const spinner = document.getElementById('loading-spinner');
        const loadingText = document.getElementById('loading-text');
        const container = document.getElementById('crossword-container');

        spinner.style.display = 'block';
        loadingText.style.display = 'block';
        container.innerHTML = '';

        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(response => response.text())
        .then(html => {
            container.innerHTML = html;
            spinner.style.display = 'none';
            loadingText.style.display = 'none';
            
            restoreProgressGridIfPresent();
            initAutoCheck();
            initClueHoverHighlight();
            initCellHoverClueHighlight();
        })
        .catch(err => {
            console.error(err);
            spinner.style.display = 'none';
            loadingText.style.display = 'none';
        });
    });
}

function initCellHoverClueHighlight() {
    const cells = document.querySelectorAll(".white-square");

    cells.forEach(td => {
        td.addEventListener("mouseenter", () => {
            const acrossNumber = td.dataset.acrossNumber;
            const downNumber = td.dataset.downNumber;

            const direction = acrossNumber ? "across" : "down";
            const clueNumber = acrossNumber || downNumber;
            if (!clueNumber) return;

            setWordHighlight(direction, clueNumber, true);
        });

        td.addEventListener("mouseleave", () => {
            const acrossNumber = td.dataset.acrossNumber;
            const downNumber = td.dataset.downNumber;
            const direction = acrossNumber ? "across" : "down";
            const clueNumber = acrossNumber || downNumber;
            if (!clueNumber) return;

            setWordHighlight(direction, clueNumber, false);
        });
    });
}


function initClueHoverHighlight() {
    const clueItems = document.querySelectorAll(".clue-item");

    clueItems.forEach(li => {
        const direction = li.dataset.direction;
        const clueNumber = li.dataset.clueNumber;

        li.addEventListener("mouseenter", () => {
            setWordHighlight(direction, clueNumber, true);
        });

        li.addEventListener("mouseleave", () => {
            setWordHighlight(direction, clueNumber, false);
        });
    });
}

// Helper: highlight both the word AND its clue
function setWordHighlight(direction, clueNumber, shouldHighlight) {
    if (!clueNumber) return;

    // highlight cells
    const cellSelector =
        direction === "across"
            ? `.white-square[data-across-number="${clueNumber}"]`
            : `.white-square[data-down-number="${clueNumber}"]`;

    document.querySelectorAll(cellSelector).forEach(td => {
        if (shouldHighlight) {
            td.classList.add("highlighted");
        } else {
            td.classList.remove("highlighted");
        }
    });

    // highlight clue
    const clueSelector = `.clue-item[data-direction="${direction}"][data-clue-number="${clueNumber}"]`;
    const clue = document.querySelector(clueSelector);
    if (clue) {
        if (shouldHighlight) {
            clue.classList.add("highlighted-clue");
        } else {
            clue.classList.remove("highlighted-clue");
        }
    }
}
// handles Auto Check + auto move cells
function initAutoCheck() {
    const inputs = Array.from(document.querySelectorAll(".crossword-input"));
    const toggle = document.getElementById("errorToggle");
    if (!toggle || !inputs.length) return;

    let autoCheck = toggle.checked;

    function styleInput(input) {
        const correct = (input.dataset.answer || "").toUpperCase();
        const val = (input.value || "").toUpperCase();

        if (val === "") {
            input.style.color = "black";
            input.style.fontWeight = "normal";
        } else if (val === correct) {
            input.style.color = "black";
            input.style.fontWeight = "bold";
        } else {
            input.style.color = "red";
            input.style.fontWeight = "bold";
        }
    }

    function checkAllInputs() {
        inputs.forEach(styleInput);
    }

    // Toggle for auto check feature
    toggle.addEventListener("change", () => {
        autoCheck = toggle.checked;
        if (autoCheck) {
            checkAllInputs();
        } else {
            inputs.forEach(input => {
                input.style.color = "black";
                input.style.fontWeight = "normal";
            });
        }
    });
    
    // handling cell inputs
    inputs.forEach((input, index) => {
        input.addEventListener("input", () => {
            let val = (input.value || "").toUpperCase();
            
            // prevent spaces as cell input
            if (val === " ") {
                input.value = "";
                return;
            }
            
            // keep only one character (last typed)
            if (val.length > 1) {
                val = val.slice(-1);
            }
            input.value = val;

            // auto move to next input if a character was entered (need to implement vertical wrods)
            if (val !== "" && index < inputs.length - 1) {
                inputs[index + 1].focus();
            }

            if (!autoCheck) return;
            styleInput(input);
        });

        // Auto move through cells on delete (need to implement for down words)
        input.addEventListener("keydown", (e) => {
            if (e.key === "Backspace" && input.value === "" && index > 0) {
                e.preventDefault();
                inputs[index - 1].focus();
                inputs[index - 1].value = "";
            }
        });
    });
}

 //helpers
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === name + "=") {
                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1)
                );
                break;
            }
        }
    }
    return cookieValue;
}

// Build a 2D array from the current DOM grid
function buildProgressGrid() {
    const rows = Array.from(
        document.querySelectorAll(".crossword-table tr")
    );

    return rows.map((row) => {
        const cells = Array.from(row.querySelectorAll("td"));
        return cells.map((td) => {
            const input = td.querySelector("input.crossword-input");

            if (!input) {
                // black square
                return "-";
            }

            const val = input.value.toUpperCase();
            return val || "";
        });
    });
}

function getCrosswordDataFromDom() {
    const solutionEl = document.getElementById("solution-grid-data");
    const acrossEl = document.getElementById("across-clues-data");
    const downEl = document.getElementById("down-clues-data");
    const categoryEl = document.getElementById("category-data");

    if (!solutionEl || !acrossEl || !downEl || !categoryEl) {
        return null;
    }

    return {
        solutionGrid: JSON.parse(solutionEl.textContent),
        acrossClues: JSON.parse(acrossEl.textContent),
        downClues: JSON.parse(downEl.textContent),
        category: JSON.parse(categoryEl.textContent),
    };
}

// --- Event delegation for Save button ---

document.addEventListener("click", async (event) => {
    const target = event.target;

    // Reveal grid button
    if (target && target.id === "reveal-solution-btn") {
        if (!confirm("Are you sure you want to reveal the full solution?")) {
            return;
        }
        const inputs = Array.from(document.querySelectorAll(".crossword-input"));

        inputs.forEach((input) => {
            const correct = (input.dataset.answer || "").toUpperCase();
            input.value = correct;

            const evt = new Event("input", { bubbles: true });
            input.dispatchEvent(evt);
        });

        return;
    }

    // save crossword button
    if (target && target.id === "save-crossword-btn") {
        const data = getCrosswordDataFromDom();
        if (!data) {
            alert("Crossword data not found in DOM.");
            return;
        }

        const progressGrid = buildProgressGrid();
        const csrftoken = getCookie("csrftoken");
        const saveUrl = target.dataset.saveUrl;

        try {
            const response = await fetch(saveUrl, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrftoken,
                    "X-Requested-With": "XMLHttpRequest",
                },
                body: JSON.stringify({
                    category: data.category,
                    solution_grid: data.solutionGrid,
                    progress_grid: progressGrid,
                    across_clues: data.acrossClues,
                    down_clues: data.downClues,
                }),
            });

            const json = await response.json();

            if (json.success) {
                alert("Crossword Successfully Saved!");
            } else {
                alert("Failed to save crossword: " + (json.error || "Unknown error"));
            }
        } catch (err) {
            console.error(err);
            alert("Network error while saving crossword.");
        }
    }
});

function restoreProgressGridIfPresent() {
    const progressEl = document.getElementById("progress-grid-data");
    if (!progressEl) return;

    let progressGrid;
    try {
        progressGrid = JSON.parse(progressEl.textContent);
    } catch (e) {
        console.warn("Could not parse progress grid", e);
        return;
    }
    if (!Array.isArray(progressGrid) || progressGrid.length === 0) {
        return;
    }

    const rows = Array.from(document.querySelectorAll(".crossword-table tr"));

    rows.forEach((rowEl, r) => {
        const cells = Array.from(rowEl.querySelectorAll("td"));
        cells.forEach((td, c) => {
            const input = td.querySelector("input.crossword-input");
            if (!input) return;

            if (
                r < progressGrid.length &&
                Array.isArray(progressGrid[r]) &&
                c < progressGrid[r].length
            ) {
                const val = progressGrid[r][c];
                if (val && typeof val === "string") {
                    input.value = val.toUpperCase();
                }
            }
        });
    });
}

document.addEventListener("DOMContentLoaded", () => {
    initCrosswordPage();
    restoreProgressGridIfPresent();
    initAutoCheck();
    initClueHoverHighlight();
    initCellHoverClueHighlight();
});
