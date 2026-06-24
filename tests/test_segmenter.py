import sys
sys.path.append(".")

from backend.extractor import extract_text
from backend.cleaner import clean_text
from backend.segmenter import segment_into_clauses

raw = extract_text("tests/sample_contract.pdf")
cleaned = clean_text(raw)
clauses = segment_into_clauses(cleaned)

print(f"Total clauses found: {len(clauses)}\n")
for i, clause in enumerate(clauses[:5], 1):
    print(f"--- Clause {i} ---")
    print(clause)
    print()