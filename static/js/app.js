const form = document.getElementById("comicForm");
const storyInput = document.getElementById("story");
const styleInput = document.getElementById("style");

const outlineSection = document.getElementById("outlineSection");
const outlineTitle = document.getElementById("outlineTitle");
const outlineLogline = document.getElementById("outlineLogline");
const charactersBox = document.getElementById("characters");
const outlinePanels = document.getElementById("outlinePanels");

const statusBox = document.getElementById("status");
const generateButton = document.getElementById("generateButton");
const pdfButton = document.getElementById("pdfButton");

let currentOutline = null;
let currentComic = null;


// =========================================================
// GENERATE OUTLINE
// =========================================================

if (form) {

    form.addEventListener("submit", async function (event) {

        event.preventDefault();

        const prompt = storyInput.value.trim();

        if (!prompt) {
            statusBox.textContent = "Please enter a story idea.";
            return;
        }

        currentOutline = null;
        currentComic = null;

        statusBox.textContent =
            "Generating your new comic outline...";

        const outlineButton =
            document.getElementById("outlineButton");

        if (outlineButton) {
            outlineButton.disabled = true;
        }

        try {

            const response = await fetch("/api/outline", {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    prompt: prompt,
                    visual_style: styleInput.value,
                    panel_count: 5
                })
            });

            const data = await response.json();

            if (!response.ok) {

                const detail =
                    typeof data.detail === "string"
                        ? data.detail
                        : JSON.stringify(data.detail);

                throw new Error(
                    detail || "Failed to generate outline."
                );
            }

            currentOutline = data;

            displayOutline(data);

            statusBox.textContent =
                "New outline generated successfully!";

        } catch (error) {

            console.error(error);

            statusBox.textContent =
                "Error: " + error.message;

        } finally {

            if (outlineButton) {
                outlineButton.disabled = false;
            }
        }
    });
}


// =========================================================
// DISPLAY OUTLINE
// =========================================================

function displayOutline(data) {

    if (outlineSection) {
        outlineSection.classList.remove("hidden");
    }

    if (outlineTitle) {
        outlineTitle.textContent =
            data.title || "Comic Outline";
    }

    if (outlineLogline) {
        outlineLogline.textContent =
            data.logline || "";
    }

    if (charactersBox) {

        charactersBox.innerHTML = "";

        if (data.characters) {

            data.characters.forEach(function (character) {

                const characterCard =
                    document.createElement("div");

                characterCard.className =
                    "character-card";

                characterCard.innerHTML = `
                    <h3>
                        ${escapeHtml(character.name || "")}
                    </h3>

                    <p>
                        ${escapeHtml(
                            character.description || ""
                        )}
                    </p>
                `;

                charactersBox.appendChild(characterCard);
            });
        }
    }

    if (outlinePanels) {

        outlinePanels.innerHTML = "";

        if (data.panels) {

            data.panels.forEach(function (panel) {

                const panelCard =
                    document.createElement("div");

                panelCard.className =
                    "panel-card";

                panelCard.innerHTML = `
                    <div class="panel-number">
                        Panel ${panel.panel_number}
                    </div>

                    <h3>
                        ${escapeHtml(panel.title || "")}
                    </h3>

                    <p>
                        ${escapeHtml(
                            panel.scene_description || ""
                        )}
                    </p>
                `;

                outlinePanels.appendChild(panelCard);
            });
        }
    }
}


// =========================================================
// GENERATE COMIC
// =========================================================

if (generateButton) {

    generateButton.addEventListener(
        "click",
        async function () {

            if (!currentOutline) {

                statusBox.textContent =
                    "Please generate the outline first.";

                return;
            }

            statusBox.textContent =
                "Generating comic pictures...";

            generateButton.disabled = true;

            const comicGrid =
                document.getElementById("comicGrid");

            const resultSection =
                document.getElementById("resultSection");

            if (comicGrid) {
                comicGrid.innerHTML = "";
            }

            if (resultSection) {
                resultSection.classList.add("hidden");
            }

            try {

                const response = await fetch(
                    "/api/generate",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type": "application/json"
                        },

                        body: JSON.stringify({
                            outline: currentOutline
                        })
                    }
                );

                const data = await response.json();

                if (!response.ok) {

                    const detail =
                        typeof data.detail === "string"
                            ? data.detail
                            : JSON.stringify(data.detail);

                    throw new Error(
                        detail || "Comic generation failed."
                    );
                }

                currentComic = data;

                localStorage.setItem(
                    "comiccraft_current_comic",
                    JSON.stringify(data)
                );

                showGeneratedComic(data);

                statusBox.textContent =
                    "Comic pictures generated successfully!";

            } catch (error) {

                console.error(error);

                statusBox.textContent =
                    "Comic Error: " + error.message;

            } finally {

                generateButton.disabled = false;
            }
        }
    );
}


// =========================================================
// SHOW GENERATED COMIC - PICTURE ONLY
// =========================================================

function showGeneratedComic(comic) {

    const resultSection =
        document.getElementById("resultSection");

    const comicGrid =
        document.getElementById("comicGrid");

    if (!comicGrid) {
        return;
    }

    if (resultSection) {
        resultSection.classList.remove("hidden");
    }

    comicGrid.innerHTML = "";

    if (!comic.panels || comic.panels.length === 0) {

        comicGrid.innerHTML =
            "<p>No images were generated.</p>";

        return;
    }

    comic.panels.forEach(function (panel) {

        const card =
            document.createElement("div");

        card.className = "comic-panel";

        if (panel.image_url) {

            const image =
                document.createElement("img");

            image.src =
                panel.image_url.startsWith("http")
                    ? panel.image_url
                    : window.location.origin +
                      panel.image_url;

            image.alt =
                "Comic Panel " +
                panel.panel_number;

            image.style.width = "100%";
            image.style.display = "block";

            image.onerror = function () {

                console.error(
                    "Image failed to load:",
                    image.src
                );
            };

            card.appendChild(image);

        } else {

            card.innerHTML =
                "<p>Image not available.</p>";
        }

        comicGrid.appendChild(card);
    });

    resultSection.scrollIntoView({
        behavior: "smooth"
    });
}


// =========================================================
// EXPORT PDF
// =========================================================

if (pdfButton) {

    pdfButton.addEventListener(
        "click",
        async function () {

            if (!currentComic) {

                statusBox.textContent =
                    "Please generate the comic first.";

                return;
            }

            statusBox.textContent =
                "Creating PDF...";

            pdfButton.disabled = true;

            try {

                const response =
                    await fetch(
                        "/api/export/pdf",
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body: JSON.stringify({
                                comic: currentComic
                            })
                        }
                    );

                const data =
                    await response.json();

                if (!response.ok) {

                    const detail =
                        typeof data.detail === "string"
                            ? data.detail
                            : JSON.stringify(data.detail);

                    throw new Error(
                        detail ||
                        "PDF export failed."
                    );
                }

                if (data.pdf_url) {

                    window.open(
                        data.pdf_url,
                        "_blank"
                    );

                    statusBox.textContent =
                        "PDF created successfully!";

                } else {

                    statusBox.textContent =
                        "PDF created, but URL was not returned.";
                }

            } catch (error) {

                console.error(error);

                statusBox.textContent =
                    "PDF Error: " + error.message;

            } finally {

                pdfButton.disabled = false;
            }
        }
    );
}


// =========================================================
// ESCAPE HTML
// =========================================================

function escapeHtml(value) {

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


// =========================================================
// START APP
// =========================================================

window.addEventListener(
    "DOMContentLoaded",
    function () {

        currentComic = null;
        currentOutline = null;

        console.log(
            "ComicCraft started."
        );
    }
);