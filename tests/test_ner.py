import sys
sys.path.append(".")

from backend.extractor import extract_text
from backend.cleaner import clean_text
from backend.ner import extract_entities

raw = extract_text("tests/sample_contract.pdf")
cleaned = clean_text(raw)
entities = extract_entities(cleaned)

for category, items in entities.items():
    print(f"\n{category.upper()}:")
    for item in items:
        print(f"  - {item}")