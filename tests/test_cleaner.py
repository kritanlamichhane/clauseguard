import sys
sys.path.append(".")

from backend.extractor import extract_text
from backend.cleaner import clean_text

raw = extract_text("tests/sample_contract.pdf")
cleaned = clean_text(raw)

print("--- BEFORE ---")
print(raw[:500])
print("\n--- AFTER ---")
print(cleaned[:500])