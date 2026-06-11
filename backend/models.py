from pydantic import BaseModel
from typing import List, Optional

# A single clause extracted from the contract
class Clause(BaseModel):
    id: int                        # clause number (1, 2, 3...)
    text: str                      # the actual clause text
    clause_type: Optional[str]     # "liability", "payment", "termination" etc
    risk_level: Optional[str]      # "high", "medium", "low", "safe"
    risk_reason: Optional[str]     # plain English explanation of the risk
    keywords: Optional[List[str]]  # important legal terms found
    entities: Optional[dict]       # names, dates, amounts found

# Named entities found in the full contract
class ContractEntities(BaseModel):
    parties: List[str]             # names of people/companies
    dates: List[str]               # dates mentioned
    amounts: List[str]             # money amounts mentioned
    locations: List[str]           # places mentioned

# The full risk report for one contract
class RiskReport(BaseModel):
    file_name: str                 # original file name
    total_clauses: int             # how many clauses found
    risk_score: int                # 0-100 overall risk score
    high_risk_count: int           # number of high risk clauses
    medium_risk_count: int         # number of medium risk clauses
    low_risk_count: int            # number of low risk clauses
    entities: ContractEntities     # all named entities
    clauses: List[Clause]          # all clauses with analysis
    summary: str                   # Gemini's plain English summary