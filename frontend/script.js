
// ---------------------------------------
// GET HTML ELEMENTS
// ---------------------------------------

const pdfFile = document.getElementById("pdfFile");
const uploadBtn = document.getElementById("uploadBtn");
const uploadBox = document.getElementById("uploadBox");
const fileName = document.getElementById("fileName");

const status = document.getElementById("status");
const textPreview = document.getElementById("textPreview");
const chunkInfo = document.getElementById("chunkInfo");
const chunkPreview = document.getElementById("chunkPreview");

const chatMessages = document.getElementById("chatMessages");
const questionInput = document.getElementById("questionInput");
const sendBtn = document.getElementById("sendBtn");
const chatStatus = document.getElementById("chatStatus");


// ---------------------------------------
// TRACK UPLOAD STATUS
// ---------------------------------------

let selectedFile = null;
let documentUploaded = false;


// ---------------------------------------
// 1. HANDLE FILE SELECTION
// ---------------------------------------

pdfFile.addEventListener("change", function () {
    handleFile(this.files[0]);
});


// ---------------------------------------
// 2. DRAG AND DROP
// ---------------------------------------

uploadBox.addEventListener("dragover", function (event) {
    event.preventDefault();
    uploadBox.style.background = "#eef3fc";
});

uploadBox.addEventListener("dragleave", function () {
    uploadBox.style.background = "#fafbfe";
});

uploadBox.addEventListener("drop", function (event) {
    event.preventDefault();

    uploadBox.style.background = "#fafbfe";

    handleFile(event.dataTransfer.files[0]);
});


// ---------------------------------------
// 3. VALIDATE SELECTED FILE
// ---------------------------------------

function handleFile(file) {

    if (!file) return;

    if (
        file.type !== "application/pdf" &&
        !file.name.toLowerCase().endsWith(".pdf")
    ) {
        status.textContent = "Please select a PDF file.";
        status.style.color = "red";
        return;
    }

    selectedFile = file;

    documentUploaded = false;
    sendBtn.disabled = true;

    fileName.textContent = "Selected: " + file.name;

    status.textContent = "";
    chatStatus.textContent = "";

    textPreview.textContent =
        "Your extracted document text will appear here.";

    chunkInfo.textContent = "";

    chunkPreview.textContent =
        "Your document chunks will appear here.";

    uploadBtn.disabled = false;
}


// ---------------------------------------
// 4. UPLOAD PDF TO FLASK
// ---------------------------------------

uploadBtn.addEventListener("click", async function () {

    if (!selectedFile) return;

    const formData = new FormData();

    formData.append("file", selectedFile);

    uploadBtn.disabled = true;
    uploadBtn.textContent = "Uploading...";

    status.textContent = "Uploading and processing PDF...";
    status.style.color = "#315b9b";

    try {

        const response = await fetch("/api/upload", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "PDF upload failed.");
        }

        // Mark document as uploaded
        documentUploaded = true;

        status.textContent = data.message;
        status.style.color = "green";

        // Display extracted text
        textPreview.textContent = data.text_preview;

        // Display character and chunk count
        chunkInfo.textContent =
            `Total Characters: ${data.total_characters} | Total Chunks: ${data.total_chunks}`;

        // Display first three chunks
        chunkPreview.textContent = "";

        data.chunks_preview.forEach((chunk, index) => {

            const p = document.createElement("p");

            p.textContent = `Chunk ${index + 1}: ${chunk}`;

            chunkPreview.appendChild(p);

        });

        fileName.textContent = "Uploaded: " + data.filename;

        // Enable chatbot
        sendBtn.disabled = false;

        // Reset previous chat
        chatMessages.textContent = "";

        addMessage(
            "bot",
            "Your PDF has been processed successfully! You can now ask me questions about it."
        );

    } catch (error) {

        documentUploaded = false;
        sendBtn.disabled = true;

        status.textContent = error.message;
        status.style.color = "red";

    } finally {

        uploadBtn.disabled = false;
        uploadBtn.textContent = "Upload Document";

    }

});


// ---------------------------------------
// 5. DISPLAY CHAT MESSAGES
// ---------------------------------------

function addMessage(type, message) {

    const messageDiv = document.createElement("div");

    if (type === "user") {
        messageDiv.className = "user-message";
    } else {
        messageDiv.className = "bot-message";
    }

    messageDiv.textContent = message;

    chatMessages.appendChild(messageDiv);

    // Automatically scroll to latest message
    chatMessages.scrollTop = chatMessages.scrollHeight;

}


// ---------------------------------------
// 6. SEND QUESTION TO FLASK API
// ---------------------------------------

async function sendQuestion() {

    const question = questionInput.value.trim();

    if (!question) return;

    if (!documentUploaded) {

        addMessage("bot", "Please upload a PDF first.");

        return;
    }

    // Display user's question
    addMessage("user", question);

    questionInput.value = "";

    sendBtn.disabled = true;

    chatStatus.textContent = "Generating answer...";
    chatStatus.style.color = "#315b9b";

    try {

        const response = await fetch("/api/ask", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                question: question
            })

        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Failed to generate answer.");
        }

        // Display Gemini's answer
        addMessage("bot", data.answer);

        chatStatus.textContent = "";

    } catch (error) {

        addMessage("bot", "Error: " + error.message);

        chatStatus.textContent = "Could not generate an answer.";
        chatStatus.style.color = "red";

    } finally {

        sendBtn.disabled = !documentUploaded;

    }

}


// ---------------------------------------
// 7. SEND BUTTON CLICK
// ---------------------------------------

sendBtn.addEventListener("click", sendQuestion);


// ---------------------------------------
// 8. PRESS ENTER TO SEND QUESTION
// ---------------------------------------

questionInput.addEventListener("keydown", function (event) {

    if (event.key === "Enter") {

        sendQuestion();

    }

});
