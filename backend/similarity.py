# PREVIOUS PYTORCH IMPLEMENTATION
# from sentence_transformers import SentenceTransformer
# from sentence_transformers.util import cos_sim
# 
# # Load the embedding model once (downloads ~80MB on first run)
# model = SentenceTransformer("all-MiniLM-L6-v2")
# 
# # Pre-compute embeddings for the reference clauses (done once, reused for every contract)
# reference_texts = [item[0] for item in RISKY_REFERENCE_CLAUSES]
# reference_embeddings = model.encode(reference_texts)

import os
import numpy as np
import torch
from optimum.onnxruntime import ORTModelForFeatureExtraction
from transformers import AutoTokenizer

from backend.constants import RISKY_REFERENCE_CLAUSES

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "onnx_model")

tokenizer = None
model = None
reference_embeddings = None
onnx_loaded = None

def get_embedding(text: str) -> np.ndarray:
    """Helper to compute mean-pooled embeddings for a text using ONNX runtime"""
    if tokenizer is None or model is None:
        return None
    inputs = tokenizer(text, padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
    token_embeddings = outputs.last_hidden_state
    attention_mask = inputs['attention_mask']
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
    sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
    embedding = (sum_embeddings / sum_mask)[0]
    return embedding.cpu().numpy()

def cos_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
    """Compute cosine similarity between two 1D arrays"""
    if v1 is None or v2 is None:
        return 0.0
    dot_prod = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0
    return float(dot_prod / (norm_v1 * norm_v2))

def load_onnx_model():
    global tokenizer, model, reference_embeddings, onnx_loaded
    if onnx_loaded is not None:
        return onnx_loaded

    try:
        if not os.path.exists(MODEL_DIR):
            print(f"[WARNING] similarity.py: ONNX model directory '{MODEL_DIR}' does not exist.")
            onnx_loaded = False
            return False

        tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
        model = ORTModelForFeatureExtraction.from_pretrained(MODEL_DIR)
        reference_embeddings = [get_embedding(item[0]) for item in RISKY_REFERENCE_CLAUSES]
        onnx_loaded = True
        return True
    except Exception as e:
        print(f"[WARNING] similarity.py: Failed to load ONNX model from '{MODEL_DIR}': {e}")
        onnx_loaded = False
        return False


def find_similar_risky_clause(clause_text, threshold=0.55):
    """
    Compares one clause against all known risky reference clauses.
    Returns the best match if similarity is above the threshold, else None.
    """
    if not load_onnx_model() or not reference_embeddings:
        return None

    clause_embedding = get_embedding(clause_text)
    if clause_embedding is None:
        return None
    
    best_score = -1.0
    best_idx = -1
    
    for i, ref_emb in enumerate(reference_embeddings):
        score = cos_similarity(clause_embedding, ref_emb)
        if score > best_score:
            best_score = score
            best_idx = i

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