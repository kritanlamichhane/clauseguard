# Reference library of high-risk clauses used for semantic similarity checks.
# Format: (clause_template_text, risk_type_label, risk_level)
RISKY_REFERENCE_CLAUSES = [
    (
        "This Agreement automatically renews unless cancelled in writing 90 days in advance.",
        "Auto-renewal trap",
        "high"
    ),
    (
        "The Company shall not be liable for any damages of any kind arising from this Agreement.",
        "One-sided liability",
        "high"
    ),
    (
        "Either party may terminate this Agreement at any time for any reason without notice.",
        "Unilateral termination",
        "high"
    ),
    (
        "All work product created shall become the sole and exclusive property of the Client.",
        "Broad IP transfer",
        "medium"
    ),
    (
        "Employee shall not engage in any competing business for a period of two years.",
        "Restrictive non-compete",
        "medium"
    ),
    (
        "Failure to comply shall result in liquidated damages and forfeiture of deposit.",
        "Financial penalty",
        "medium"
    ),
    (
        "Contractor shall indemnify and hold harmless the Company from any and all claims whatsoever.",
        "Broad indemnification",
        "medium"
    ),
]

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

