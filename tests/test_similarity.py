import sys
sys.path.append(".")

from backend.extractor import extract_text
from backend.cleaner import clean_text
from backend.segmenter import segment_into_clauses
from backend.similarity import find_similar_for_all_clauses

raw = extract_text("tests/sample_contract.pdf")
cleaned = clean_text(raw)
clauses = segment_into_clauses(cleaned)
results = find_similar_for_all_clauses(clauses)

for i, result in enumerate(results, 1):
    if result["similarity_match"]:
        match = result["similarity_match"]
        print(f"\n--- Clause {i} ---")
        print(result["clause_text"][:150], "...")
        print(f"  🔍 Matched: {match['risk_type']} (similarity: {match['similarity_score']})")
        print(f"     Reference: \"{match['matched_reference']}\"")