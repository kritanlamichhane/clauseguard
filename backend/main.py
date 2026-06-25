from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import shutil
import uuid

from backend.extractor import extract_text
from backend.cleaner import clean_text
from backend.segmenter import segment_into_clauses
from backend.ner import extract_entities
from backend.rules import flag_clause
from backend.classifier import predict_clause_type
from backend.similarity import find_similar_risky_clause
from backend.analyzer import analyze_clause, generate_contract_summary
from backend.scorer import calculate_risk_score, count_risk_levels, get_risk_label

app = FastAPI(title="ClauseGuard API")

# Allow the frontend (running on a different port) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
def health_check():
    """Simple endpoint to check the server is alive"""
    return {"status": "ClauseGuard API is running"}


@app.post("/analyze")
async def analyze_contract(file: UploadFile = File(...)):
    """
    Main endpoint. Accepts a PDF/DOCX file, runs the full NLP pipeline,
    and returns a structured risk report.
    """
    # Validate file type
    allowed_extensions = [".pdf", ".docx", ".txt"]
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Only PDF, DOCX, and TXT files are supported.")

    # Save uploaded file with a unique name (avoid collisions)
    unique_name = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # Step 1-3: extract, clean, segment
        raw_text = extract_text(file_path)
        cleaned = clean_text(raw_text)
        clauses = segment_into_clauses(cleaned)

        # Step 4: entities (whole-contract level)
        entities = extract_entities(cleaned)

        # Step 5-8: per-clause analysis
        clause_results = []
        for clause in clauses:
            rule_matches = flag_clause(clause)
            classification = predict_clause_type(clause)
            similarity_match = find_similar_risky_clause(clause)

            analysis = analyze_clause(clause, rule_matches, classification, similarity_match)
            analysis["clause_text"] = clause
            analysis["clause_type_predicted"] = classification["clause_type"]
            clause_results.append(analysis)

        # Step 9: scoring
        score = calculate_risk_score(clause_results)
        counts = count_risk_levels(clause_results)
        label = get_risk_label(score)
        summary = generate_contract_summary(clause_results)

        return {
            "file_name": file.filename,
            "total_clauses": len(clauses),
            "risk_score": score,
            "risk_label": label,
            "risk_breakdown": counts,
            "entities": entities,
            "summary": summary,
            "clauses": clause_results
        }

    finally:
        # Clean up — delete the uploaded file after processing
        if os.path.exists(file_path):
            os.remove(file_path)