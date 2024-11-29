from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction

translation_dict = {
    "hello": {"word": "नमस्ते", "pos": "UH"},
    "world": {"word": "दुनिया", "pos": "NN"},
    "how": {"word": "कैसे", "pos": "WRB"},
    "are": {"word": "हो", "pos": "VBP"},
    "you": {"word": "आप", "pos": "PRP"},
    "i": {"word": "मैं", "pos": "PRP"},
    "am": {"word": "हूँ", "pos": "VBP"},
    "was": {"word": "था", "pos": "VBD"},
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
    "explaining": {"word": "समझा रहे", "pos": "VBG"},
    "problem": {"word": "समस्या", "pos": "NN"},
    "board": {"word": "बोर्ड", "pos": "NN"},
    "train": {"word": "ट्रेन", "pos": "NN"},
    "delayed": {"word": "देरी से", "pos": "VBN"},
    "because of": {"word": "के कारण", "pos": "IN"},
    "heavy rain": {"word": "भारी बारिश", "pos": "NN"},
    "the": {"word": "", "pos": "DT"},
    # Phrases
    "how are you": {"word": "आप कैसे", "pos": "PHRASE"},
    "on the table": {"word": "मेज़ पर", "pos": "PHRASE"},
    "there is": {"word": "वहाँ", "pos": "PHRASE"},
    "a piece of cake": {"word": "बहुत आसान", "pos": "PHRASE"},
    "break a leg": {"word": "आपको कामयाबी मिले", "pos": "PHRASE"},
    "was supposed to arrive": {"word": "आने वाली थी", "pos": "PHRASE"},
    "9 a.m.": {"word": "सुबह 9 बजे", "pos": "PHRASE"},
}


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
def apply_hindi_grammar(translations, original_sentence):
    # print(translations)
    words = [word for word, _ in translations]
    auxiliary_map = {
        "is": "है",
        "are": "हैं",
        "was": "था",
        "were": "थे",
        "will be": "होगा",
    }
    auxiliary_verb = None
    for eng_aux, hindi_aux in auxiliary_map.items():
        if eng_aux in original_sentence.lower():
            auxiliary_verb = hindi_aux
            break

    if auxiliary_verb and auxiliary_verb in words:
        words.remove(auxiliary_verb)
        words.append(auxiliary_verb)

    for i, word in enumerate(words):
        if word == "पर" and i > 0:
            words[i - 1], words[i] = words[i], words[i - 1]

    if auxiliary_verb and auxiliary_verb not in words:
        words.append(auxiliary_verb)

    punctuations = [".", ",", "?", "!", ":", ";", "'", "\"", "-", "_", "(", ")", "[", "]", "{", "}", "/", "\\", "|",
                    "&"]
    # print(translations)
    subject = []
    objects = []
    verbs = []
    auxiliaries = []
    adverbs = []
    expletives = []
    phrases = []

    for word, pos in translations:
        if pos == "PHRASE":
            phrases.append(word)  # Keep phrases intact and in order
        if word in punctuations:
            phrases.append(word)
        elif pos in {"NN", "PRP", "PRP$", "EX"}:
            subject.append(word)
        elif pos in {"JJ", "IN", "CC", "DT"}:
            objects.append(word)
        elif pos.startswith("VB") or pos in {"VBG", "VBN"}:
            verbs.append(word)
        elif pos in {"VBP", "VBD", "VBP_FUTURE", "VBZ"}:
            auxiliaries.append(word)
        elif pos == "WRB":
            adverbs.append(word)
        elif pos == "UH":
            expletives.append(word)

    # Construct the Hindi sentence by keeping phrases in order
    reconstructed_sentence = []
    for word, pos in translations:
        if pos == "PHRASE" or "Unknown":
            reconstructed_sentence.append(word)  # Add the phrase as it appears
        elif word in subject:
            reconstructed_sentence.append(word)
            subject.remove(word)
        elif word in objects:
            reconstructed_sentence.append(word)
            objects.remove(word)
        elif word in verbs:
            reconstructed_sentence.append(word)
            verbs.remove(word)
        elif word in auxiliaries:
            reconstructed_sentence.append(word)
            auxiliaries.remove(word)
        elif word in expletives:
            reconstructed_sentence.append(word)
            expletives.remove(word)
        elif word in adverbs:
            reconstructed_sentence.append(word)
            adverbs.remove(word)

    reconstructed = " ".join(reconstructed_sentence)

    words = reconstructed.split()  # Split the reconstructed sentence into words
    auxiliary_verb = None

    # Find the appropriate auxiliary verb based on the original English sentence
    for eng_aux, hindi_aux in auxiliary_map.items():
        if eng_aux in original_sentence.lower():
            auxiliary_verb = hindi_aux
            break

    # Rearrange auxiliary verb to the end of the sentence if present
    if auxiliary_verb and auxiliary_verb in words:
        words.remove(auxiliary_verb)
        words.append(auxiliary_verb)

    # Append the auxiliary verb if it is not already present
    if auxiliary_verb and auxiliary_verb not in words:
        words.append(auxiliary_verb)

    # Join the words back into a sentence

    adjusted_sentence = " ".join(words)
    return adjusted_sentence

    # return " ".join(words)


# Translate a sentence
def translate_with_phrases(sentence):
    matches = match_phrases(sentence, translation_dict)
    # print(matches)
    return [(match[1]["word"], match[1]["pos"]) for match in matches]


def punctuation_handle(sentence):
    punctuations = [".", ",", "?", "!", ":", ";", "'", "\"", "-", "_", "(", ")", "[", "]", "{", "}", "/", "\\", "|",
                    "&"]
    # sent = sentence.split(' ')
    for punct in punctuations:
        if punct in sentence:
            # print("TRUE")
            sentence = sentence.replace(punct, f" {punct}")
        if "." in sentence:
            sentence = sentence.replace(".", "")

    return sentence


def translate_sentence(sentence):
    translations = translate_with_phrases(sentence)
    hindi_sentence = apply_hindi_grammar(translations, sentence)
    return hindi_sentence, translations


# Evaluate BLEU score
def evaluate_translation(predicted, reference):
    predicted_tokens = predicted.split()
    reference_tokens = [reference.split()]
    chencherry = SmoothingFunction()
    return sentence_bleu(reference_tokens, predicted_tokens, smoothing_function=chencherry.method1)


examples = [
    ("Hello world", "नमस्ते दुनिया"),
    ("How are you", "आप कैसे है"),
    ("I was fine", "मैं ठीक था"),
    ("There is a book on the table", "मेज़ पर एक किताब है"),
    ("Break a leg", "आपको कामयाबी मिले"),
    ("A piece of cake", "बहुत आसान"),
    ("There is a book and a pen on the table, but the notebook is missing.",
     "मेज़ पर एक किताब और एक पेन है, लेकिन नोटबुक गायब है"),
    ("The train is delayed", "ट्रेन देरी से चल रही है"),
    # ("The teacher is explaining the homework", "शिक्षक गृहकार्य समझा रहे हैं"),
]
# Run translations and evaluate
for sentence, reference in examples:
    sentence = punctuation_handle(sentence)
    hindi_sentence, pos_translation = translate_sentence(sentence)
    bleu_score = evaluate_translation(hindi_sentence, reference)
    print(f"English: {sentence}")
    print(f"Predicted Hindi: {hindi_sentence}")
    print(f"Reference Hindi: {reference}")
    print(f"BLEU Score: {bleu_score:.4f}")
    # print(f"POS Translation: {pos_translation}\n")
