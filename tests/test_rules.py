import sys
sys.path.append(".")

from backend.extractor import extract_text
from backend.cleaner import clean_text
from backend.segmenter import segment_into_clauses
from backend.rules import flag_all_clauses

raw = extract_text("tests/sample_contract.pdf")
cleaned = clean_text(raw)
clauses = segment_into_clauses(cleaned)
flagged = flag_all_clauses(clauses)

for i, result in enumerate(flagged, 1):
    if result["matches"]:
        print(f"\n--- Clause {i} ---")
        print(result["clause_text"][:150], "...")
        for match in result["matches"]:
            print(f"  [WARNING] {match['risk_type']} ({match['risk_level']}): {match['explanation']}")