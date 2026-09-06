from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any

# ── Authentication Models ──────────────────────────────────────────────────────

class UserRegister(BaseModel):
    email: str
    username: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserProfile(BaseModel):
    id: int
    email: str
    username: str
    created_at: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfile


# ── Analysis & Report Models ───────────────────────────────────────────────────

# A single clause extracted from the contract
class Clause(BaseModel):
    id: Optional[int] = None
    clause_text: str
    clause_type_predicted: Optional[str] = None
    risk_level: Optional[str] = "safe"
    risk_type: Optional[str] = "Standard"
    explanation: Optional[str] = ""
    recommendation: Optional[str] = ""
    rule_matches: Optional[List[Dict[str, Any]]] = None
    similarity_match: Optional[Dict[str, Any]] = None


# Named entities found in the full contract
class ContractEntities(BaseModel):
    parties: List[str] = []
    dates: List[str] = []
    amounts: List[str] = []
    locations: List[str] = []


class RiskBreakdown(BaseModel):
    high: int = 0
    medium: int = 0
    low: int = 0
    safe: int = 0


# The full risk report for one contract
class RiskReport(BaseModel):
    file_name: str
    total_clauses: int
    risk_score: int
    risk_label: str
    risk_breakdown: RiskBreakdown
    entities: ContractEntities
    summary: str
    clauses: List[Clause]


# ── History Summary & Detail Models ────────────────────────────────────────────

class HistorySummaryItem(BaseModel):
    id: int
    file_name: str
    risk_score: int
    risk_label: str
    total_clauses: int
    summary: str
    created_at: str


class HistoryDetailResponse(BaseModel):
    id: int
    user_id: int
    file_name: str
    risk_score: int
    risk_label: str
    total_clauses: int
    risk_breakdown: Dict[str, Any]
    entities: Dict[str, Any]
    summary: str
    clauses: List[Dict[str, Any]]
    created_at: str