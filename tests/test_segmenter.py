from backend.segmenter import segment_into_clauses, detect_numbered_clauses, split_into_sentences

def test_detect_numbered_clauses():
    text = "1. Payment Terms. Payment is due in 30 days.\n2. Termination. Vendor may terminate anytime."
    clauses = detect_numbered_clauses(text)
    assert len(clauses) >= 2
    assert "1. Payment Terms" in clauses[0]

def test_segment_into_clauses():
    text = "1. First clause.\n2. Second clause."
    clauses = segment_into_clauses(text)
    assert len(clauses) == 2

def test_split_into_sentences_fallback():
    text = "This is sentence one. This is sentence two."
    sents = split_into_sentences(text)
    assert len(sents) == 2