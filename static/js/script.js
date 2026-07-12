// script.js
// ---------
// Handles all frontend interactivity: drag-and-drop upload, sending the
// image to the Flask backend, and updating the page with results -
// all without a full page reload (using the Fetch API).

// Grab references to all the HTML elements we'll need to work with.
const dropZone = document.getElementById("dropZone");
const fileInput = document.getElementById("fileInput");
const loadingSpinner = document.getElementById("loadingSpinner");
const errorBox = document.getElementById("errorBox");
const resultsSection = document.getElementById("resultsSection");
const previewImage = document.getElementById("previewImage");
const extractedTextBox = document.getElementById("extractedText");
const confidenceScore = document.getElementById("confidenceScore");
const processingTime = document.getElementById("processingTime");
const copyBtn = document.getElementById("copyBtn");
const downloadBtn = document.getElementById("downloadBtn");
const clearHistoryBtn = document.getElementById("clearHistoryBtn");
const historyList = document.getElementById("historyList");

// ---------------------------------------------------------------------
// Drag-and-drop + click-to-browse upload handling
// ---------------------------------------------------------------------

// Clicking the drop zone opens the normal file picker
dropZone.addEventListener("click", () => fileInput.click());

// Highlight the drop zone while a file is being dragged over it
dropZone.addEventListener("dragover", (event) => {
    event.preventDefault();
    dropZone.classList.add("drag-over");
});

dropZone.addEventListener("dragleave", () => {
    dropZone.classList.remove("drag-over");
});

// When a file is dropped, treat it the same as a normal file selection
dropZone.addEventListener("drop", (event) => {
    event.preventDefault();
    dropZone.classList.remove("drag-over");
    const droppedFiles = event.dataTransfer.files;
    if (droppedFiles.length > 0) {
        handleFile(droppedFiles[0]);
    }
});

// When a file is chosen via the normal file picker
fileInput.addEventListener("change", () => {
    if (fileInput.files.length > 0) {
        handleFile(fileInput.files[0]);
    }
});

// ---------------------------------------------------------------------
// Core function: send the selected file to the backend for OCR
// ---------------------------------------------------------------------
function handleFile(file) {
    hideError();

    // Show a preview of the image immediately, before the server responds,
    // so the user gets instant feedback that their file was picked up.
    const previewUrl = URL.createObjectURL(file);
    previewImage.src = previewUrl;

    // Build the form data to send to Flask's /upload route
    const formData = new FormData();
    formData.append("image", file);

    loadingSpinner.classList.remove("d-none");
    resultsSection.classList.add("d-none");

    fetch("/upload", {
        method: "POST",
        body: formData
    })
        .then((response) => response.json().then((data) => ({ status: response.status, data })))
        .then(({ status, data }) => {
            loadingSpinner.classList.add("d-none");

            if (status !== 200) {
                showError(data.error || "Something went wrong.");
                return;
            }

            // Fill in the results section with the data Flask sent back
            extractedTextBox.value = data.text;
            confidenceScore.textContent = data.confidence;
            processingTime.textContent = data.processing_time;
            resultsSection.classList.remove("d-none");

            addHistoryEntry(file.name, data.text, data.confidence, data.processing_time);
        })
        .catch(() => {
            loadingSpinner.classList.add("d-none");
            showError("Could not reach the server. Please try again.");
        });
}

function showError(message) {
    errorBox.textContent = message;
    errorBox.classList.remove("d-none");
}

function hideError() {
    errorBox.classList.add("d-none");
    errorBox.textContent = "";
}

// ---------------------------------------------------------------------
// Copy-to-clipboard button
// ---------------------------------------------------------------------
copyBtn.addEventListener("click", () => {
    extractedTextBox.select();
    navigator.clipboard.writeText(extractedTextBox.value).then(() => {
        copyBtn.textContent = "✅ Copied!";
        setTimeout(() => (copyBtn.textContent = "📋 Copy Text"), 1500);
    });
});

// ---------------------------------------------------------------------
// Download-as-.txt button
// ---------------------------------------------------------------------
downloadBtn.addEventListener("click", () => {
    const formData = new FormData();
    formData.append("text", extractedTextBox.value);

    fetch("/download-text", {
        method: "POST",
        body: formData
    })
        .then((response) => response.blob())
        .then((blob) => {
            // Create a temporary link element to trigger the file download
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement("a");
            link.href = url;
            link.download = "extracted_text.txt";
            document.body.appendChild(link);
            link.click();
            link.remove();
        });
});

// ---------------------------------------------------------------------
// History list (added dynamically to the page, no reload needed)
// ---------------------------------------------------------------------
function addHistoryEntry(filename, text, confidence, time) {
    // Remove the "No uploads yet" placeholder text if it's still there
    const placeholder = document.getElementById("noHistoryText");
    if (placeholder) {
        placeholder.remove();
    }

    const shortText = text.length > 150 ? text.substring(0, 150) + "..." : text;

    const entryDiv = document.createElement("div");
    entryDiv.className = "border rounded p-2 mb-2";
    entryDiv.innerHTML = `
        <strong>${filename}</strong>
        <span class="badge bg-success">${confidence}%</span>
        <span class="badge bg-info text-dark">${time}s</span>
        <p class="mb-0 small text-muted">${shortText}</p>
    `;

    historyList.prepend(entryDiv);
}

clearHistoryBtn.addEventListener("click", () => {
    fetch("/clear-history", { method: "POST" }).then(() => {
        historyList.innerHTML = '<p id="noHistoryText" class="text-muted">No uploads yet this session.</p>';
    });
});
