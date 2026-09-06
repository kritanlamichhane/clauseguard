from typing import List, Dict, Any

RISK_WEIGHTS = {
    "high": 15,
    "medium": 7,
    "low": 2,
    "safe": 0,
    "unknown": 3
}


def calculate_risk_score(clause_results: List[Dict[str, Any]]) -> int:
    """
    Calculates an overall risk score (0-100) from a list of clause analyses.
    Each clause contributes points based on its risk level, capped at 100.
    """
    total_score = 0
    for result in clause_results:
        risk_level = result.get("risk_level", "unknown")
        total_score += RISK_WEIGHTS.get(risk_level, 3)

    return min(total_score, 100)


def count_risk_levels(clause_results: List[Dict[str, Any]]) -> Dict[str, int]:
    """Counts how many clauses fall into each risk category"""
    counts = {"high": 0, "medium": 0, "low": 0, "safe": 0, "unknown": 0}
    for result in clause_results:
        risk_level = result.get("risk_level", "unknown")
        counts[risk_level] = counts.get(risk_level, 0) + 1

    return counts


def get_risk_label(score: int) -> str:
    """Converts numeric score into a human-friendly label"""
    if score >= 60:
        return "High Risk"
    elif score >= 30:
        return "Medium Risk"
    elif score >= 10:
        return "Low Risk"
    else:
        return "Minimal Risk"
