from backend.similarity import find_similar_risky_clause, cos_similarity
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