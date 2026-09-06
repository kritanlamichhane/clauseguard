from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import shutil
import uuid
from typing import Optional, List, Dict, Any

from backend.extractor import extract_text
from backend.cleaner import clean_text
from backend.segmenter import segment_into_clauses
from backend.ner import extract_entities
from backend.rules import flag_clause
from backend.classifier import predict_clause_type
from backend.similarity import find_similar_risky_clause
from backend.analyzer import analyze_contract_batch
from backend.scorer import calculate_risk_score, count_risk_levels, get_risk_label

from backend.database import (
    create_user,
    get_user_by_email,
    save_analysis_history,
    get_user_history,
    get_history_detail,
    delete_history_item
)
from backend.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    get_optional_user
)
from backend.models import (
    UserRegister,
    UserLogin,
    UserProfile,
    TokenResponse,
    HistorySummaryItem,
    HistoryDetailResponse
)

app = FastAPI(title="ClauseGuard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/health")
def health_check():
    """Simple endpoint to check the server is alive"""
    return {"status": "ClauseGuard API is running"}


# ── Authentication Endpoints ───────────────────────────────────────────────────

@app.post("/auth/register", response_model=TokenResponse)
def register(req: UserRegister):
    """Registers a new user account and returns a JWT access token."""
    email = req.email.strip().lower()
    username = req.username.strip()

    if not email or "@" not in email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide a valid email address."
        )

    if not username or len(username) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username must be at least 2 characters long."
        )

    if not req.password or len(req.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters long."
        )

    existing_user = get_user_by_email(email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists."
        )

    hashed_pw = hash_password(req.password)
    user = create_user(email=email, username=username, hashed_password=hashed_pw)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user account. Please try again."
        )

    token = create_access_token(user_id=user["id"], email=user["email"], username=user["username"])
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }


@app.post("/auth/login", response_model=TokenResponse)
def login(req: UserLogin):
    """Authenticates user credentials and returns a JWT access token."""
    email = req.email.strip().lower()
    user = get_user_by_email(email)

    if not user or not verify_password(req.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    token = create_access_token(user_id=user["id"], email=user["email"], username=user["username"])
    user_profile = {
        "id": user["id"],
        "email": user["email"],
        "username": user["username"],
        "created_at": str(user["created_at"])
    }

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user_profile
    }


@app.get("/auth/me", response_model=UserProfile)
def get_me(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Returns the profile of the currently authenticated user."""
    return current_user


# ── History Endpoints ──────────────────────────────────────────────────────────

@app.get("/history", response_model=List[HistorySummaryItem])
def list_history(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Returns the list of previously analyzed documents for the authenticated user."""
    history_items = get_user_history(current_user["id"])
    return history_items


@app.get("/history/{history_id}", response_model=HistoryDetailResponse)
def get_history_item(history_id: int, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Returns the complete analysis report for a specific past document audit."""
    item = get_history_detail(history_id, current_user["id"])
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="History item not found or unauthorized access."
        )
    return item


@app.delete("/history/{history_id}")
def delete_history(history_id: int, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Deletes a past document audit record from the user's history."""
    deleted = delete_history_item(history_id, current_user["id"])
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="History item not found or unauthorized access."
        )
    return {"message": "Document audit deleted from history successfully.", "id": history_id}


# ── Document Analysis Endpoint ─────────────────────────────────────────────────

@app.post("/analyze")
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

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] analyze_contract failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing contract: {str(e)}"
        )
    finally:
        # Clean up — delete the uploaded file after processing
        if os.path.exists(file_path):
            os.remove(file_path)


# Serve frontend static files
if os.path.exists("frontend/dist"):
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="frontend")
elif os.path.exists("frontend"):
    app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")