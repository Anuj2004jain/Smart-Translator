import string
from nltk.translate.bleu_score import sentence_bleu

# Updated dictionary with words and phrases
translation_dict = {
    # Individual words
    "hello": {"word": "नमस्ते", "pos": "UH"},
    "world": {"word": "दुनिया", "pos": "NN"},
    "how": {"word": "कैसे", "pos": "WRB"},
    "are": {"word": "हो", "pos": "VBP"},
    "you": {"word": "आप", "pos": "PRP"},
    "i": {"word": "मैं", "pos": "PRP"},
    "am": {"word": "हूँ", "pos": "VBP"},
    "was": {"word": "था", "pos": "VBD"},
    "were": {"word": "थे", "pos": "VBD_PLURAL"},
    "will be": {"word": "होगा", "pos": "VBP_FUTURE"},
    "fine": {"word": "ठीक", "pos": "JJ"},
    "what": {"word": "क्या", "pos": "WP"},
    "is": {"word": "है", "pos": "VBZ"},
    "your": {"word": "तुम्हारा", "pos": "PRP$"},
    "name": {"word": "नाम", "pos": "NN"},
    "a": {"word": "एक", "pos": "DT"},
    "book": {"word": "किताब", "pos": "NN"},
    "pen": {"word": "पेन", "pos": "NN"},
    "on": {"word": "पर", "pos": "IN"},
    "table": {"word": "मेज़", "pos": "NN"},
    "there": {"word": "वहाँ", "pos": "EX"},
    "and": {"word": "और", "pos": "CC"},
    "but": {"word": "लेकिन", "pos": "CC"},
    "notebook": {"word": "नोटबुक", "pos": "NN"},
    "missing": {"word": "गायब", "pos": "JJ"},
    "students": {"word": "छात्र", "pos": "NN"},
    "working": {"word": "काम कर रहे हैं", "pos": "VBG"},
    "their": {"word": "अपने", "pos": "PRP$"},
    "homework": {"word": "गृहकार्य", "pos": "NN"},
    "while": {"word": "जबकि", "pos": "IN"},
    "teacher": {"word": "शिक्षक", "pos": "NN"},
    "explaining": {"word": "समझा रहे हैं", "pos": "VBG"},
    "problem": {"word": "समस्या", "pos": "NN"},
    "board": {"word": "बोर्ड", "pos": "NN"},
    "train": {"word": "ट्रेन", "pos": "NN"},
    "delayed": {"word": "देरी से है", "pos": "VBN"},
    "because of": {"word": "के कारण", "pos": "IN"},
    "heavy rain": {"word": "भारी बारिश", "pos": "NN"},
    "the": {"word": "", "pos": "DT"},
    # Phrases
    "how are you": {"word": "आप कैसे हो", "pos": "PHRASE"},
    "on the table": {"word": "मेज़ पर", "pos": "PHRASE"},
    "there is": {"word": "वहाँ है", "pos": "PHRASE"},
    "the train was supposed to arrive": {"word": "आने वाली थी", "pos": "PHRASE"},
    "9 a.m.": {"word": "सुबह 9 बजे", "pos": "PHRASE"},
}

# Remove punctuation from a sentence
def clean_sentence(sentence):
    return sentence.translate(str.maketrans("", "", string.punctuation))

# Match phrases in a sentence
def match_phrases(sentence, dictionary):
    words = sentence.lower().split()
    matched_phrases = []
    i = 0
    while i < len(words):
        match_found = False
        for j in range(len(words), i, -1):
            phrase = " ".join(words[i:j])
            if phrase in dictionary:
                matched_phrases.append((phrase, dictionary[phrase]))
                i = j - 1
                match_found = True
                break
        if not match_found:
            word = words[i]
            matched_phrases.append((word, dictionary.get(word, {"word": word, "pos": "Unknown"})))
        i += 1
    return matched_phrases

# Grammar-aware sentence reconstruction
def apply_hindi_grammar(translations):
    subject = []
    objects = []
    verbs = []
    auxiliaries = []

    for word, pos in translations:
        if pos in {"NN", "PRP", "PRP$"}:
            subject.append(word)
        elif pos in {"JJ", "IN", "CC"}:
            objects.append(word)
        elif pos.startswith("VB") or pos == "VBG":
            verbs.append(word)
        elif pos in {"VBP", "VBD", "VBP_FUTURE"}:
            auxiliaries.append(word)

    # Construct Hindi sentence: Subject → Object → Verb → Auxiliary
    return " ".join(subject + objects + verbs + auxiliaries)

# Translate a sentence
def translate_with_phrases(sentence):
    sentence = clean_sentence(sentence)
    matches = match_phrases(sentence, translation_dict)
    return [(match[1]["word"], match[1]["pos"]) for match in matches]

def translate_sentence(sentence):
    translations = translate_with_phrases(sentence)
    hindi_sentence = apply_hindi_grammar(translations)
    return hindi_sentence, translations

# Evaluate BLEU score
def evaluate_translation(predicted, reference):
    predicted_tokens = predicted.split()
    reference_tokens = [reference.split()]
    return sentence_bleu(reference_tokens, predicted_tokens)

# Example sentences
examples = [
    ("Hello world!", "नमस्ते दुनिया"),
    ("How are you?", "आप कैसे हो"),
    ("I was fine.", "मैं ठीक था"),
    ("There is a book on the table.", "मेज़ पर एक किताब है"),
    ("The students are working on their homework while the teacher is explaining the problem on the board.",
     "छात्र अपने गृहकार्य पर काम कर रहे हैं जबकि शिक्षक बोर्ड पर समस्या समझा रहे हैं।"),
]

# Run translations and evaluate
for sentence, reference in examples:
    hindi_sentence, pos_translation = translate_sentence(sentence)
    bleu_score = evaluate_translation(hindi_sentence, reference)
    print(f"English: {sentence}")
    print(f"Predicted Hindi: {hindi_sentence}")
    print(f"Reference Hindi: {reference}")
    print(f"BLEU Score: {bleu_score:.4f}")
    print(f"POS Translation: {pos_translation}\n")
