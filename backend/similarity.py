from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim

# Load the embedding model once (downloads ~80MB on first run)
model = SentenceTransformer("all-MiniLM-L6-v2")

# Known risky clause examples — the "reference library"
RISKY_REFERENCE_CLAUSES = [
    ("This Agreement automatically renews unless cancelled in writing 90 days in advance.", "Auto-renewal trap", "high"),
    ("The Company shall not be liable for any damages of any kind arising from this Agreement.", "One-sided liability", "high"),
    ("Either party may terminate this Agreement at any time for any reason without notice.", "Unilateral termination", "high"),
    ("All work product created shall become the sole and exclusive property of the Client.", "Broad IP transfer", "medium"),
    ("Employee shall not engage in any competing business for a period of two years.", "Restrictive non-compete", "medium"),
    ("Failure to comply shall result in liquidated damages and forfeiture of deposit.", "Financial penalty", "medium"),
    ("Contractor shall indemnify and hold harmless the Company from any and all claims whatsoever.", "Broad indemnification", "medium"),
]

# Pre-compute embeddings for the reference clauses (done once, reused for every contract)
reference_texts = [item[0] for item in RISKY_REFERENCE_CLAUSES]
reference_embeddings = model.encode(reference_texts)


def find_similar_risky_clause(clause_text, threshold=0.55):
    """
    Compares one clause against all known risky reference clauses.
    Returns the best match if similarity is above the threshold, else None.
    """
    clause_embedding = model.encode([clause_text])
    similarities = cos_sim(clause_embedding, reference_embeddings)[0]

    best_idx = similarities.argmax().item()
    best_score = similarities[best_idx].item()

    if best_score >= threshold:
        matched_text, risk_type, risk_level = RISKY_REFERENCE_CLAUSES[best_idx]
        return {
            "risk_type": risk_type,
            "risk_level": risk_level,
            "similarity_score": round(best_score, 2),
            "matched_reference": matched_text
        }
    return None


def find_similar_for_all_clauses(clauses, threshold=0.55):
    """Runs similarity check on a whole list of clauses"""
    results = []
    for clause in clauses:
        match = find_similar_risky_clause(clause, threshold)
        results.append({"clause_text": clause, "similarity_match": match})
    return results