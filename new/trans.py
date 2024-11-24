import streamlit as st
import pandas as pd
import nltk
from nltk import word_tokenize, pos_tag, ne_chunk
from nltk.tree import Tree
from nltk.stem import WordNetLemmatizer

# Ensure required NLTK resources are downloaded
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')
nltk.download('wordnet')

# Initialize WordNet Lemmatizer
lemmatizer = WordNetLemmatizer()

# Load the Excel file and create dictionaries
@st.cache
def load_translation_dictionaries(file_path):
    df = pd.read_excel(file_path)
    english_to_hindi = dict(zip(df['English'], df['Hindi']))
    hindi_to_english = {v: k for k, v in english_to_hindi.items()}
    return english_to_hindi, hindi_to_english

# Path to your Excel file
file_path = "Book1.xlsx"  # Replace with the actual path to your file

# Load dictionaries
english_to_hindi, hindi_to_english = load_translation_dictionaries(file_path)

# Tokenization function
def tokenize(text):
    return word_tokenize(text)

# NER detection using NLTK
def detect_named_entities(text):
    """
    Detect named entities using nltk.ne_chunk.
    Args:
        text (str): The input text.
    Returns:
        List[str]: Detected named entities.
    """
    tokens = tokenize(text)
    pos_tags = pos_tag(tokens)
    chunks = ne_chunk(pos_tags)
    entities = []
    for chunk in chunks:
        if isinstance(chunk, Tree):  # Check if the chunk is a named entity
            entity = " ".join(c[0] for c in chunk)
            entities.append(entity)
    return entities

# Lemmatization for morphological processing
def lemmatize_word(word):
    """
    Lemmatizes a word to its root form using WordNetLemmatizer.
    Args:
        word (str): The word to lemmatize.
    Returns:
        str: The lemmatized word.
    """
    pos_tagged = pos_tag([word])[0][1]
    pos = (
        'v' if pos_tagged.startswith('V') else
        'n' if pos_tagged.startswith('N') else
        'a' if pos_tagged.startswith('J') else
        'r' if pos_tagged.startswith('R') else
        None
    )
    return lemmatizer.lemmatize(word, pos) if pos else word

# Handling basic conjugation for English-to-Hindi translation
def conjugate_to_be(english_word, subject):
    if english_word == "am" and subject == "i":
        return "हूँ"
    elif english_word == "is":
        return "है"
    elif english_word == "are":
        return "हैं"
    return english_word

# Handle negation with correct sentence structure
def handle_negation_and_structure(words):
    subject = words[0].lower()
    verb = words[1].lower()
    negation = words[2].lower() if "not" in words else None
    object_words = words[3:] if negation else words[2:]

    subject_translated = english_to_hindi.get(subject, subject)
    object_translated = " ".join([english_to_hindi.get(word, word) for word in object_words])
    verb_translated = conjugate_to_be(verb, subject)

    if negation:
        negation_translated = english_to_hindi.get(negation, negation)
        return f"{subject_translated} {object_translated} {negation_translated} {verb_translated}।"
    else:
        return f"{subject_translated} {object_translated} {verb_translated}।"

# Handling conjugation for verbs in English-to-Hindi translation
# Updated verb conjugation for Hindi
def conjugate_verb_to_hindi(verb, subject):
    """
    Conjugates a verb to Hindi based on the subject.
    Args:
        verb (str): The base form of the verb in English.
        subject (str): The subject of the sentence.
    Returns:
        str: The conjugated verb in Hindi.
    """
    # Translate the base verb
    verb_translation = english_to_hindi.get(verb, verb)  

    # Handle common cases where "कर" is unnecessary
    if verb_translation in ["दौड़", "खेल", "खा", "सो"]:  # Add more verbs as needed
        if subject in ["i", "मैं"]:  # Subject is "I"
            return f"{verb_translation} रहा हूँ"
        elif subject in ["he", "she", "it", "वह", "यह"]:  # Subject is singular third-person
            return f"{verb_translation} रहा है"
        elif subject in ["we", "they", "हम", "वे"]:  # Subject is plural
            return f"{verb_translation} रहे हैं"
        elif subject in ["you", "तुम", "आप"]:  # Subject is second-person
            return f"{verb_translation} रहे हो"
    else:
        # Default case: include "कर" if verb needs an auxiliary
        if subject in ["i", "मैं"]:
            return f"{verb_translation} कर रहा हूँ"
        elif subject in ["he", "she", "it", "वह", "यह"]:
            return f"{verb_translation} कर रहा है"
        elif subject in ["we", "they", "हम", "वे"]:
            return f"{verb_translation} कर रहे हैं"
        elif subject in ["you", "तुम", "आप"]:
            return f"{verb_translation} कर रहे हो"

    return verb_translation


# Translate English to Hindi
def translate_to_hindi(text):
    words = tokenize(text)

    # Detect named entities dynamically and preserve them in the translation
    entities = detect_named_entities(text)
    for entity in entities:
        text = text.replace(entity, f"<ENTITY>{entity}</ENTITY>")

    # Morphological analysis: Lemmatize words
    lemmatized_words = [lemmatize_word(word.lower()) for word in words]

    if len(lemmatized_words) >= 2:  # Handle verb conjugation
        subject = lemmatized_words[0]
        verb = lemmatized_words[1]
        object_words = lemmatized_words[2:] if len(lemmatized_words) > 2 else []

        subject_translated = english_to_hindi.get(subject, subject)
        verb_conjugated = conjugate_verb_to_hindi(verb, subject)
        object_translated = " ".join([english_to_hindi.get(word, word) for word in object_words])

        return f"{subject_translated} {object_translated} {verb_conjugated}।"

    translated_words = [english_to_hindi.get(word, word) for word in lemmatized_words]
    translated_text = " ".join(translated_words).replace("<ENTITY>", "").replace("</ENTITY>", "")
    return translated_text



# Translate Hindi to English
def translate_to_english(text):
    words = tokenize(text)

    for entity in detect_named_entities(text):
        text = text.replace(entity, f"<ENTITY>{entity}</ENTITY>")

    lemmatized_words = [lemmatize_word(word) for word in words]
    translated_words = [hindi_to_english.get(word, word) for word in lemmatized_words]

    translated_text = " ".join(translated_words).replace("<ENTITY>", "").replace("</ENTITY>", "")
    return translated_text

# Streamlit App Interface
st.title("English to Hindi & Hindi to English Translator")
option = st.selectbox("Choose Translation Direction", ("English to Hindi", "Hindi to English"))

if option == "English to Hindi":
    text_input = st.text_area("Enter English Text")
    if st.button("Translate"):
        translated_text = translate_to_hindi(text_input)
        st.write(f"Translated Hindi: {translated_text}")
else:
    text_input = st.text_area("Enter Hindi Text")
    if st.button("Translate"):
        translated_text = translate_to_english(text_input)
        st.write(f"Translated English: {translated_text}")
