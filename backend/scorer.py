# Weight each risk level — higher risk contributes more to the score
RISK_WEIGHTS = {
    "high": 15,
    "medium": 7,
    "low": 2,
    "safe": 0,
    "unknown": 3
}

def calculate_risk_score(clause_results):
    """
    Calculates an overall risk score (0-100) from a list of clause analyses.
    Each clause contributes points based on its risk level.
    Score is capped at 100.
    """
    total_score = 0

    for result in clause_results:
        risk_level = result.get("risk_level", "unknown")
        total_score += RISK_WEIGHTS.get(risk_level, 3)

    # Cap at 100
    final_score = min(total_score, 100)
    return final_score


def count_risk_levels(clause_results):
    """Counts how many clauses fall into each risk category"""
    counts = {"high": 0, "medium": 0, "low": 0, "safe": 0, "unknown": 0}

    for result in clause_results:
        risk_level = result.get("risk_level", "unknown")
        counts[risk_level] = counts.get(risk_level, 0) + 1

    return counts


def get_risk_label(score):
    """Converts numeric score into a human-friendly label"""
    if score >= 60:
        return "High Risk"
    elif score >= 30:
        return "Medium Risk"
    elif score >= 10:
        return "Low Risk"
    else:
        return "Minimal Risk"