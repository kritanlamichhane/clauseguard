import os
import shutil
import uuid
from typing import Optional, Dict, Any
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends

from backend.core.config import UPLOAD_DIR, ALLOWED_EXTENSIONS
from backend.core.database import save_analysis_history
from backend.core.dependencies import get_optional_user
from backend.core.rate_limiter import RateLimitExceeded
from backend.pipeline import (
    extract_text,
    clean_text,
    segment_into_clauses,
    extract_entities,
    flag_clause,
    predict_clause_type,
    find_similar_risky_clause,
    analyze_contract_batch,
    calculate_risk_score,
    count_risk_levels,
    get_risk_label,
)

router = APIRouter(tags=["Analysis"])


@router.post("/analyze")
async def analyze_contract(
    file: UploadFile = File(...),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """
    Main endpoint. Accepts a PDF/DOCX file, runs the full NLP pipeline,
    and returns a structured risk report. If the user is authenticated,
    the audit is automatically saved to their persistent history.
    """
    # Validate file type
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only PDF, DOCX, and TXT files are supported.")

    # Save uploaded file with a unique name
    unique_name = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # Step 1-3: extract, clean, segment
        raw_text = extract_text(file_path)
        if not raw_text or not raw_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from document. Please ensure the file is not empty or password protected."
            )

        cleaned = clean_text(raw_text)
        clauses = segment_into_clauses(cleaned)
        if not clauses:
            clauses = [cleaned] if cleaned else []

        # Step 4: entities (whole-contract level)
        entities = extract_entities(cleaned)

        # Step 5-8: compile clauses and analyze in a single batch
        processed_clauses = []
        for clause in clauses:
            processed_clauses.append({
                "text": clause,
                "classification": predict_clause_type(clause),
                "rule_matches": flag_clause(clause),
                "similarity_match": find_similar_risky_clause(clause)
            })

        clause_results, summary = analyze_contract_batch(processed_clauses)

        # Step 9: scoring
        score = calculate_risk_score(clause_results)
        counts = count_risk_levels(clause_results)
        label = get_risk_label(score)

        report_data = {
            "file_name": file.filename,
            "total_clauses": len(clauses),
            "risk_score": score,
            "risk_label": label,
            "risk_breakdown": counts,
            "entities": entities,
            "summary": summary,
            "clauses": clause_results
        }

        # Step 10: If authenticated user, persist audit in SQLite database
        history_id = None
        if current_user:
            try:
                history_id = save_analysis_history(
                    user_id=current_user["id"],
                    file_name=file.filename,
                    risk_score=score,
                    risk_label=label,
                    total_clauses=len(clauses),
                    risk_breakdown=counts,
                    entities=entities,
                    summary=summary,
                    clauses=clause_results
                )
            except Exception as save_err:
                print(f"[WARN] Failed to auto-save analysis history: {save_err}")

        report_data["history_id"] = history_id
        return report_data

    except RateLimitExceeded as rle:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=429,
            content={"detail": str(rle)},
            headers={"Retry-After": str(int(rle.retry_after_seconds))},
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] analyze_contract failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing contract: {str(e)}"
        )
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
