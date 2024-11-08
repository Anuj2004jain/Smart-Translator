// Global variable to hold speech recognition instance
let speechRecognition;
let recognizedText = '';

// Function to start speech recognition and display recognized text in real-time
function startSpeechRecognition() {
    if (!('webkitSpeechRecognition' in window)) {
        alert("Sorry, your browser doesn't support speech recognition.");
        return;
    }

    speechRecognition = new webkitSpeechRecognition();
    speechRecognition.lang = document.getElementById('detectedLang').value;
    speechRecognition.continuous = true;
    speechRecognition.interimResults = true;

    // Display recognized text in the text area in real-time
    speechRecognition.onresult = function(event) {
        recognizedText = event.results[0][0].transcript;
        document.getElementById('textInput').value = recognizedText;
    };

    speechRecognition.start();
}

// Function to handle file upload and preview document content (PDF or DOCX)
function previewDocument(event) {
    const file = event.target.files[0];
    if (!file) {
        console.log("No file selected");
        return;
    }

    const fileType = file.name.split('.').pop().toLowerCase();
    console.log(`Selected file type: ${fileType}`);

    if (fileType === 'pdf') {
        previewPDF(file);
    } else if (fileType === 'docx') {
        previewDOCX(file);
    } else {
        alert("Unsupported file type. Please upload a PDF or DOCX document.");
    }
}

// Function to preview PDF content
function previewPDF(file) {
    const reader = new FileReader();
    reader.onload = async function(e) {
        const pdfData = e.target.result;

        try {
            const pdf = await pdfjsLib.getDocument({ data: pdfData }).promise;
            let textContent = '';

            for (let i = 1; i <= pdf.numPages; i++) {
                const page = await pdf.getPage(i);
                const text = await page.getTextContent();
                const pageText = text.items.map(item => item.str).join(' ');
                textContent += `\n${pageText}`;
            }

            document.getElementById('textInput').value = textContent;
        } catch (error) {
            console.error("Error reading PDF:", error);
            alert("Failed to load PDF content.");
        }
    };
    reader.readAsArrayBuffer(file);
}

// Function to preview DOCX content
function previewDOCX(file) {
    const reader = new FileReader();
    reader.onload = function(e) {
        const arrayBuffer = e.target.result;

        mammoth.extractRawText({ arrayBuffer: arrayBuffer })
            .then(result => {
                document.getElementById('textInput').value = result.value;
            })
            .catch(error => {
                console.error("Error reading DOCX:", error);
                alert("Failed to load DOCX content.");
            });
    };
    reader.readAsArrayBuffer(file);
}

// Function to send text for translation to the backend and display the result
async function translateContent() {
    const text = document.getElementById('textInput').value;
    const targetLang = document.getElementById('targetLang').value;

    if (!text) {
        alert("Please enter or upload some text to translate.");
        return;
    }

    try {
        const response = await fetch('/translate_text', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, target_lang: targetLang })
        });

        if (response.ok) {
            const data = await response.json();
            document.getElementById('translatedText').value = data.translated_text;
        } else {
            console.error("Translation failed:", response.statusText);
            alert("Translation failed. Please try again.");
        }
    } catch (error) {
        console.error("Error during translation:", error);
        alert("An error occurred. Please try again.");
    }
}

