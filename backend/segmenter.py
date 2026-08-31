import spacy
import re

nlp = None

def get_nlp():
    global nlp
    if nlp is None:
        try:
            nlp = spacy.load("en_core_web_sm")
        except Exception as e:
            print(f"[WARNING] segmenter.py: spaCy model 'en_core_web_sm' could not be loaded: {e}")
            nlp = False
    return nlp if nlp is not False else None

def split_into_sentences(text):
    """Use spaCy to split text into linguistically correct sentences, with regex fallback"""
    nlp_model = get_nlp()
    if nlp_model:
        doc = nlp_model(text)
        return [sent.text.strip() for sent in doc.sents if sent.text.strip()]
    
    # Fallback if spaCy model is not installed/loaded
    raw_sents = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in raw_sents if s.strip()]


def detect_numbered_clauses(text):
    """
    Many contracts use numbered clauses like:
    1. Payment Terms...
    2. Termination...
    Or markdown headings like:
    ## 1. Payment Terms...
    This regex finds those boundaries and segments the text while preserving the headers.
    """
    # Matches patterns like:
    # 1. Services
    # ## 1. Services
    # Section 1. Services
    # Article 1. Services
    pattern = r'(?:\n|^)\s*(?:##\s*|Section\s+|Article\s+)?(\d+\.\s+)'
    
    matches = list(re.finditer(pattern, text))
    if not matches:
        return []
        
    clauses = []
    # If there is text before the first clause, keep it as the first item (preamble)
    first_span_start = matches[0].start()
    preamble = text[:first_span_start].strip()
    if preamble:
        clauses.append(preamble)
        
    for i in range(len(matches)):
        start = matches[i].start()
        # Adjust start if it matched leading newline
        match_str = matches[i].group(0)
        if match_str.startswith('\n'):
            start += 1
            
        end = matches[i+1].start() if i + 1 < len(matches) else len(text)
        clause_content = text[start:end].strip()
        if clause_content:
            clauses.append(clause_content)
            
    return clauses

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