import spacy

nlp = spacy.load("en_core_web_sm")

# Map spaCy's entity labels to our own simpler categories
LABEL_MAP = {
    "PERSON": "parties",
    "ORG": "parties",
    "DATE": "dates",
    "MONEY": "amounts",
    "GPE": "locations",   # GPE = Geo-Political Entity (countries, cities, states)
    "LOC": "locations",
}

def extract_entities(text):
    """
    Runs spaCy's NER model and groups results into our categories.
    Returns a dict like:
    {
        "parties": ["ABC Inc.", "John Doe"],
        "dates": ["1st January 2024"],
        "amounts": ["$5,000"],
        "locations": ["California"]
    }
    """
    doc = nlp(text)

    entities = {
        "parties": [],
        "dates": [],
        "amounts": [],
        "locations": []
    }

    for ent in doc.ents:
        category = LABEL_MAP.get(ent.label_)
        if category:
            # avoid duplicates
            if ent.text not in entities[category]:
                entities[category].append(ent.text)

    return entities