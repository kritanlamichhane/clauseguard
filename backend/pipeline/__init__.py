from backend.pipeline.constants import RISKY_REFERENCE_CLAUSES, RISK_PATTERNS
from backend.pipeline.extractor import extract_text, extract_from_pdf, extract_from_docx
from backend.pipeline.cleaner import clean_text
from backend.pipeline.segmenter import segment_into_clauses, split_into_sentences
from backend.pipeline.ner import extract_entities
from backend.pipeline.keywords import extract_keywords_tfidf, extract_keywords_yake
from backend.pipeline.rules import flag_clause, flag_all_clauses
from backend.pipeline.classifier import predict_clause_type, train_classifier, load_classifier
from backend.pipeline.similarity import (
    find_similar_risky_clause,
    find_similar_for_all_clauses,
    cos_similarity,
    get_embeddings_batch,
    get_embedding
)
from backend.pipeline.analyzer import analyze_contract_batch, generate_contract_summary
from backend.pipeline.scorer import calculate_risk_score, count_risk_levels, get_risk_label
