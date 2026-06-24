import sys
sys.path.append(".")

from backend.extractor import extract_text
from backend.cleaner import clean_text
from backend.segmenter import segment_into_clauses
from backend.keywords import extract_keywords_tfidf, extract_keywords_yake

raw = extract_text("tests/sample_contract.pdf")
cleaned = clean_text(raw)
clauses = segment_into_clauses(cleaned)

print("=== TF-IDF keywords (per clause) ===")
tfidf_results = extract_keywords_tfidf(clauses)
for i, keywords in enumerate(tfidf_results[:5], 1):
    print(f"Clause {i}: {keywords}")

print("\n=== YAKE keywords (first clause only) ===")
yake_keywords = extract_keywords_yake(clauses[0])
print(yake_keywords)