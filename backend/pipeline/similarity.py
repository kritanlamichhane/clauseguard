import os
from typing import Optional, List, Dict, Any
import numpy as np
import torch
from optimum.onnxruntime import ORTModelForFeatureExtraction
from transformers import AutoTokenizer

from backend.core.config import MODEL_DIR
from backend.pipeline.constants import RISKY_REFERENCE_CLAUSES

tokenizer = None
model = None
reference_matrix: Optional[np.ndarray] = None  # Shape: (N, D) pre-computed unit vectors
onnx_loaded = None


def get_embeddings_batch(texts: List[str]) -> Optional[np.ndarray]:
    """
    Computes mean-pooled, L2-normalized embeddings for a batch of strings using ONNX runtime.
    Returns a 2D numpy array of shape (len(texts), embedding_dim) where each row is a unit vector.
    """
    if tokenizer is None or model is None or not texts:
        return None

    try:
        inputs = tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt"
        )
        with torch.no_grad():
            outputs = model(**inputs)

        token_embeddings = outputs.last_hidden_state
        attention_mask = inputs['attention_mask']
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
        sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
        embeddings = sum_embeddings / sum_mask
        embeddings_np = embeddings.cpu().numpy()

        norms = np.linalg.norm(embeddings_np, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1e-9, norms)
        return embeddings_np / norms
    except Exception as e:
        print(f"[WARN] similarity.py: Error generating embeddings: {e}")
        return None


def get_embedding(text: str) -> Optional[np.ndarray]:
    """Helper to compute a single normalized 1D embedding array of shape (embedding_dim,)."""
    batch = get_embeddings_batch([text])
    if batch is not None and len(batch) > 0:
        return batch[0]
    return None


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


def load_onnx_model() -> bool:
    """
    Loads the ONNX embedding model and pre-computes the reference embeddings matrix.
    """
    global tokenizer, model, reference_matrix, onnx_loaded
    if onnx_loaded is not None:
        return onnx_loaded

    try:
        if not os.path.exists(MODEL_DIR):
            print(f"[WARNING] similarity.py: ONNX model directory '{MODEL_DIR}' does not exist.")
            onnx_loaded = False
            return False

        tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
        model = ORTModelForFeatureExtraction.from_pretrained(MODEL_DIR)

        reference_texts = [item[0] for item in RISKY_REFERENCE_CLAUSES]
        reference_matrix = get_embeddings_batch(reference_texts)

        onnx_loaded = reference_matrix is not None
        return onnx_loaded
    except Exception as e:
        print(f"[WARNING] similarity.py: Failed to load ONNX model from '{MODEL_DIR}': {e}")
        onnx_loaded = False
        return False


def find_similar_risky_clause(clause_text: str, threshold: float = 0.55) -> Optional[Dict[str, Any]]:
    """
    Compares a single clause against all known risky reference clauses using vectorized matrix multiplication.
    """
    if not load_onnx_model() or reference_matrix is None:
        return None

    clause_vec = get_embedding(clause_text)
    if clause_vec is None:
        return None

    scores = np.dot(reference_matrix, clause_vec)
    best_idx = int(np.argmax(scores))
    best_score = float(scores[best_idx])

    if best_score >= threshold:
        matched_text, risk_type, risk_level = RISKY_REFERENCE_CLAUSES[best_idx]
        return {
            "risk_type": risk_type,
            "risk_level": risk_level,
            "similarity_score": round(best_score, 2),
            "matched_reference": matched_text
        }
    return None


def find_similar_for_all_clauses(clauses: List[str], threshold: float = 0.55) -> List[Dict[str, Any]]:
    """
    Batch comparison: embeds all input clauses in a single ONNX pass and computes
    pairwise matrix similarities.
    """
    if not clauses:
        return []

    if not load_onnx_model() or reference_matrix is None:
        return [{"clause_text": c, "similarity_match": None} for c in clauses]

    clause_embs = get_embeddings_batch(clauses)
    if clause_embs is None:
        return [{"clause_text": c, "similarity_match": None} for c in clauses]

    similarity_matrix = np.dot(clause_embs, reference_matrix.T)
    best_indices = np.argmax(similarity_matrix, axis=1)
    best_scores = np.max(similarity_matrix, axis=1)

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
