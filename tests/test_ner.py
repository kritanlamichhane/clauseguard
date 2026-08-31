from backend.ner import extract_entities

def test_extract_entities_structure():
    text = "Agreement between ACME Corp and John Doe on January 1st, 2024 for $5,000 in California."
    entities = extract_entities(text)
    assert isinstance(entities, dict)
    assert "parties" in entities
    assert "dates" in entities
    assert "amounts" in entities
    assert "locations" in entities