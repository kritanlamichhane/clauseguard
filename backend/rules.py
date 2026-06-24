import re

# Each rule: (risk_type, regex_pattern, risk_level, explanation)
RISK_PATTERNS = [
    (
        "Auto-renewal",
        r"automatically renew|auto-renew|shall renew unless",
        "high",
        "This clause locks you into renewing unless you actively cancel — easy to miss the deadline."
    ),
    (
        "One-sided liability",
        r"shall not be liable|no liability|disclaims all liability|not responsible for any",
        "high",
        "This shifts all risk to you — the other party takes no responsibility for damages."
    ),
    (
        "Unilateral termination",
        r"may terminate.*sole discretion|may terminate.*at any time without",
        "high",
        "The other party can end this agreement whenever they want, with no real obligation to you."
    ),
    (
        "IP ownership transfer",
        r"shall (become|be) the (sole )?property of|assigns all (rights|right, title)",
        "medium",
        "You may be giving up ownership of work or ideas created under this agreement."
    ),
    (
        "Non-compete",
        r"shall not compete|non-compete|restrict.*engaging in similar business",
        "medium",
        "This may restrict your ability to work with others or start a similar business."
    ),
    (
        "Penalty clause",
        r"penalty of|liquidated damages|forfeit",
        "medium",
        "There's a financial penalty if certain conditions aren't met — check the amount carefully."
    ),
    (
        "Confidentiality / NDA",
        r"confidential information|non-disclosure|shall not disclose",
        "low",
        "Standard confidentiality clause — generally reasonable but check the duration."
    ),
    (
        "Indemnification",
        r"indemnify|hold harmless",
        "medium",
        "You may be required to cover the other party's legal costs or damages in certain situations."
    ),
]


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