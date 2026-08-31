from backend.cleaner import clean_text, normalize_quotes, remove_extra_whitespace

def test_normalize_quotes():
    raw = '\u201cSmart quotes\u201d and \u2018single quotes\u2019'
    cleaned = normalize_quotes(raw)
    assert '"Smart quotes"' in cleaned
    assert "'single quotes'" in cleaned

def test_remove_extra_whitespace():
    raw = "Multiple   spaces   here."
    cleaned = remove_extra_whitespace(raw)
    assert cleaned == "Multiple spaces here."

def test_clean_text():
    raw = '1. Payment terms\n\n\n\n2. Termination'
    cleaned = clean_text(raw)
    assert '1. Payment terms' in cleaned
    assert '2. Termination' in cleaned