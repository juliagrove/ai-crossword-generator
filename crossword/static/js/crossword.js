// crossword/static/js/crossword.js
function initCrosswordPage() {
    document.getElementById('crosswordForm').addEventListener('submit', function (e) {
        e.preventDefault();
    
        const form = this;
        const formData = new FormData(form);
        const spinner = document.getElementById('loading-spinner');
        const loadingText = document.getElementById('loading-text');
        const container = document.getElementById('crossword-container');
    
        // loading symbol
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
            initAutoCheck();
        })
        .catch(err => {
            console.error(err);
            spinner.style.display = 'none';
            loadingText.style.display = 'none';
        });
    });
    
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
}
document.addEventListener('DOMContentLoaded', initCrosswordPage);

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function getGridState() {
    const table = document.querySelector(".crossword-table");
    const rows = [];

    if (!table) return rows;

    table.querySelectorAll("tr").forEach(tr => {
        const row = [];
        tr.querySelectorAll("input.crossword-input").forEach(input => {
            row.push(input.value || "");
        });
        rows.push(row);
    });

    return rows;
}

document.addEventListener("DOMContentLoaded", () => {
    const saveBtn = document.getElementById("save-crossword-btn");
    if (!saveBtn) return;

    saveBtn.addEventListener("click", () => {
        const gridState = getGridState();
        const category = window.CROSSWORD_CATEGORY || "";

        fetch(window.SAVE_CROSSWORD_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken"),
            },
            body: JSON.stringify({
                category: category,
                grid_state: gridState,
            }),
        })
        .then(res => res.json())
        .then(data => {
            console.log("Saved:", data);
            alert("Crossword saved!");
        })
        .catch(err => {
            console.error(err);
            alert("Error saving crossword.");
        });
    });
});
