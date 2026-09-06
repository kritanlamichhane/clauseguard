from backend.pipeline.similarity import (
    find_similar_risky_clause,
    find_similar_for_all_clauses,
    cos_similarity,
    get_embeddings_batch
)
import numpy as np


def test_cos_similarity():
    v1 = np.array([1.0, 0.0, 0.0])
    v2 = np.array([1.0, 0.0, 0.0])
    assert cos_similarity(v1, v2) == 1.0

    v3 = np.array([0.0, 1.0, 0.0])
    assert cos_similarity(v1, v3) == 0.0


def test_find_similar_risky_clause_returns_dict_or_none():
    clause = "The Vendor shall be liable for all indirect damages without limitation."
    match = find_similar_risky_clause(clause)
    assert match is None or isinstance(match, dict)
    if isinstance(match, dict):
        assert "risk_type" in match
        assert "similarity_score" in match


def test_find_similar_for_all_clauses_batch():
    clauses = [
        "The Vendor shall be liable for all indirect damages without limitation.",
        "Payment is due within 30 calendar days.",
        "Either party may terminate upon written notice."
    ]
    results = find_similar_for_all_clauses(clauses)
    assert len(results) == len(clauses)
    for res in results:
        assert "clause_text" in res
        assert "similarity_match" in res