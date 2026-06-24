import spacy
import re

# Load spaCy's English model once (this is the NLP model)
nlp = spacy.load("en_core_web_sm")

def split_into_sentences(text):
    """Use spaCy to split text into linguistically correct sentences"""
    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
    return sentences

def detect_numbered_clauses(text):
    """
    Many contracts use numbered clauses like:
    1. Payment Terms...
    2. Termination...
    This regex finds those boundaries.
    """
    pattern = r'\n\s*\d+\.\s+'
    splits = re.split(pattern, text)
    return [s.strip() for s in splits if s.strip()]

def segment_into_clauses(text):
    """
    Main function — tries numbered clause detection first.
    Falls back to sentence-level splitting if no numbering found.
    """
    numbered = detect_numbered_clauses(text)

    if len(numbered) > 1:
        # Numbered clauses found — but each one might have multiple sentences
        # We keep them as-is since they're already meaningful units
        return numbered
    else:
        # No numbering — fall back to sentence splitting
        return split_into_sentences(text)