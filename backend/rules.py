import re
from backend.constants import RISK_PATTERNS


def flag_clause(clause_text):
    """
    Checks a single clause against all known risk patterns.
    Returns a list of matches found (can be multiple per clause).
    """
    matches = []
    text_lower = clause_text.lower()

    for risk_type, pattern, level, explanation in RISK_PATTERNS:
        if re.search(pattern, text_lower):
            matches.append({
                "risk_type": risk_type,
                "risk_level": level,
                "explanation": explanation
            })

    return matches


def flag_all_clauses(clauses):
    """
    Runs flag_clause on a whole list of clauses.
    Returns a list of dicts: {clause_text, matches}
    """
    results = []
    for clause in clauses:
        matches = flag_clause(clause)
        results.append({
            "clause_text": clause,
            "matches": matches
        })
    return results