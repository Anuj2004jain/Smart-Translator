# app.py
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from googletrans import Translator
import speech_recognition as sr
from docx import Document
import PyPDF2
from googletrans import LANGUAGES
print(LANGUAGES)

app = Flask(__name__)
CORS(app)
translator = Translator()

# Home route to render HTML template
@app.route('/')
def home():
    return render_template('index.html')

# Text-to-Text Translation Endpoint
@app.route('/translate_text', methods=['POST'])
def translate_text():
    data = request.json
    text = data['text']
    target_lang = data['target_lang']
    print(target_lang)
    result = translator.translate(text, dest=target_lang)
    return jsonify({'translated_text': result.text})

# Speech-to-Text Translation Endpoint
@app.route('/translate_speech', methods=['POST'])
def translate_speech():
    file = request.files['audio']
    recognizer = sr.Recognizer()
    with sr.AudioFile(file) as source:
        audio = recognizer.record(source)
    text = recognizer.recognize_google(audio)
    target_lang = request.form['target_lang']
    result = translator.translate(text, dest=target_lang)
    return jsonify({'translated_text': result.text})

# Document Translation Endpoint
def translate_document(text, target_lang):
    return translator.translate(text, dest=target_lang).text

@app.route('/translate_document', methods=['POST'])
def translate_doc():
    file = request.files['document']
    target_lang = request.form['target_lang']
    text = ""
    if file.filename.endswith('.pdf'):
        pdf_reader = PyPDF2.PdfFileReader(file)
        for page in range(pdf_reader.numPages):
            text += pdf_reader.getPage(page).extractText()
    elif file.filename.endswith('.docx'):
        doc = Document(file)
        for para in doc.paragraphs:
            text += para.text
    translated_text = translate_document(text, target_lang)
    return jsonify({'translated_text': translated_text})



if __name__ == '__main__':
    app.run(debug=True)
