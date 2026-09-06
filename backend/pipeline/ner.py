import re
from typing import Dict, List
import spacy

nlp = None


def get_nlp():
    global nlp
    if nlp is None:
        try:
            nlp = spacy.load("en_core_web_sm")
        except Exception:
            try:
                import spacy.cli
                spacy.cli.download("en_core_web_sm")
                nlp = spacy.load("en_core_web_sm")
            except Exception as e:
                print(f"[WARNING] ner.py: spaCy model 'en_core_web_sm' could not be loaded: {e}")
                nlp = False
    return nlp if nlp is not False else None


# Map spaCy's entity labels to our own simpler categories
LABEL_MAP = {
    "PERSON": "parties",
    "ORG": "parties",
    "DATE": "dates",
    "MONEY": "amounts",
    "GPE": "locations",
    "LOC": "locations",
}


def _extract_fallback_entities(text: str) -> Dict[str, List[str]]:
    """Heuristic regex extractors if spaCy is missing or fails."""
    entities: Dict[str, List[str]] = {
        "parties": [],
        "dates": [],
        "amounts": [],
        "locations": []
    }

    # Extract dates
    date_patterns = [
        r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}\b',
        r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
        r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b'
    ]
    for pat in date_patterns:
        matches = re.findall(pat, text, flags=re.IGNORECASE)
        for m in matches:
            if m not in entities["dates"]:
                entities["dates"].append(m)

    # Extract amounts
    amount_patterns = [
        r'\$\s*\d+(?:,\d{3})*(?:\.\d{2})?',
        r'\b\d+(?:,\d{3})*(?:\.\d{2})?\s*(?:USD|EUR|GBP|INR|NPR|dollars)\b'
    ]
    for pat in amount_patterns:
        matches = re.findall(pat, text, flags=re.IGNORECASE)
        for m in matches:
            if m not in entities["amounts"]:
                entities["amounts"].append(m)

    # Extract common party keywords (e.g. "between X and Y", "Client", "Contractor", "Company")
    party_pattern = r'\b(?:between|among)\s+([A-Z][A-Za-z0-9\s,\.\&]+?)\s+(?:and|with)\s+([A-Z][A-Za-z0-9\s,\.\&]+?)(?:\.|\n|,\s*dated)'
    match = re.search(party_pattern, text)
    if match:
        p1 = match.group(1).strip()
        p2 = match.group(2).strip()
        if len(p1) < 50 and p1 not in entities["parties"]:
            entities["parties"].append(p1)
        if len(p2) < 50 and p2 not in entities["parties"]:
            entities["parties"].append(p2)

    return entities


def extract_entities(text: str) -> Dict[str, List[str]]:
    """
    Runs spaCy's NER model and groups results into categories:
    {
        "parties": ["ABC Inc.", "John Doe"],
        "dates": ["1st January 2024"],
        "amounts": ["$5,000"],
        "locations": ["California"]
    }
    Includes fallback heuristics if spaCy is unavailable.
    """
    entities: Dict[str, List[str]] = {
        "parties": [],
        "dates": [],
        "amounts": [],
        "locations": []
    }

    if not text or not text.strip():
        return entities

    nlp_model = get_nlp()
    if not nlp_model:
        return _extract_fallback_entities(text)

    try:
        doc = nlp_model(text[:100000])  # limit max characters to prevent timeout

        for ent in doc.ents:
            category = LABEL_MAP.get(ent.label_)
            if category:
                cleaned_ent = ent.text.strip()
                if cleaned_ent and cleaned_ent not in entities[category]:
                    entities[category].append(cleaned_ent)

        # If spaCy missed obvious amounts/dates, supplement with regex
        fallback = _extract_fallback_entities(text)
        for key in ["amounts", "dates"]:
            for item in fallback[key]:
                if item not in entities[key]:
                    entities[key].append(item)

        return entities
    except Exception as e:
        print(f"[WARNING] ner.py: Exception during spaCy parsing: {e}")
        return _extract_fallback_entities(text)
