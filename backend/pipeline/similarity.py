from typing import Optional, List, Dict, Any
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from backend.pipeline.constants import RISKY_REFERENCE_CLAUSES

_vectorizer: Optional[TfidfVectorizer] = None
_reference_matrix = None


def _get_vectorizer_and_matrix():
    """Initializes a lightweight TF-IDF vectorizer and reference similarity matrix."""
    global _vectorizer, _reference_matrix
    if _vectorizer is None:
        ref_texts = [item[0] for item in RISKY_REFERENCE_CLAUSES]
        _vectorizer = TfidfVectorizer(ngram_range=(1, 3), sublinear_tf=True)
        _reference_matrix = _vectorizer.fit_transform(ref_texts)
    return _vectorizer, _reference_matrix


def cos_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
    """Compute cosine similarity between two 1D vectors."""
    if v1 is None or v2 is None:
        return 0.0
    dot_prod = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0
    return float(dot_prod / (norm_v1 * norm_v2))


def get_embeddings_batch(texts: List[str]) -> Optional[np.ndarray]:
    """Computes normalized TF-IDF vector arrays for batch of strings."""
    if not texts:
        return None
    try:
        vectorizer, _ = _get_vectorizer_and_matrix()
        matrix = vectorizer.transform(texts)
        return matrix.toarray()
    except Exception as e:
        print(f"[WARN] similarity.py: Error generating vector representations: {e}")
        return None


def get_embedding(text: str) -> Optional[np.ndarray]:
    """Helper to compute a single 1D vector representation."""
    batch = get_embeddings_batch([text])
    if batch is not None and len(batch) > 0:
        return batch[0]
    return None


def find_similar_risky_clause(clause_text: str, threshold: float = 0.45) -> Optional[Dict[str, Any]]:
    """
    Compares a single clause against all known risky reference clauses using
    high-speed TF-IDF n-gram cosine similarity (zero memory overhead).
    """
    if not clause_text or not clause_text.strip():
        return None

    try:
        vectorizer, ref_matrix = _get_vectorizer_and_matrix()
        clause_vec = vectorizer.transform([clause_text])
        sims = cosine_similarity(clause_vec, ref_matrix)[0]

        best_idx = int(np.argmax(sims))
        best_score = float(sims[best_idx])

        if best_score >= threshold:
            matched_text, risk_type, risk_level = RISKY_REFERENCE_CLAUSES[best_idx]
            return {
                "risk_type": risk_type,
                "risk_level": risk_level,
                "similarity_score": round(best_score, 2),
                "matched_reference": matched_text
            }
    except Exception as e:
        print(f"[WARN] similarity.py: Error in find_similar_risky_clause: {e}")

    return None


def find_similar_for_all_clauses(clauses: List[str], threshold: float = 0.45) -> List[Dict[str, Any]]:
    """
    Batch comparison: compares all clauses against risky reference clauses in one matrix multiply.
    """
    if not clauses:
        return []

    try:
        vectorizer, ref_matrix = _get_vectorizer_and_matrix()
        clause_matrix = vectorizer.transform(clauses)
        sim_matrix = cosine_similarity(clause_matrix, ref_matrix)

        best_indices = np.argmax(sim_matrix, axis=1)
        best_scores = np.max(sim_matrix, axis=1)

        results = []
        for i, clause in enumerate(clauses):
            score = float(best_scores[i])
            idx = int(best_indices[i])
            if score >= threshold:
                matched_text, risk_type, risk_level = RISKY_REFERENCE_CLAUSES[idx]
                match = {
                    "risk_type": risk_type,
                    "risk_level": risk_level,
                    "similarity_score": round(score, 2),
                    "matched_reference": matched_text
                }
            else:
                match = None
            results.append({"clause_text": clause, "similarity_match": match})
        return results
    except Exception as e:
        print(f"[WARN] similarity.py: Error in batch similarity: {e}")
        return [{"clause_text": c, "similarity_match": None} for c in clauses]
