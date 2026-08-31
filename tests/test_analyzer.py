from backend.analyzer import analyze_contract_batch, generate_contract_summary

def test_analyze_contract_batch():
    processed_clauses = [
        {
            "text": "1. Payment terms within 30 days.",
            "classification": {"clause_type": "Payment", "confidence": 0.9},
            "rule_matches": [],
            "similarity_match": None
        },
        {
            "text": "2. Client agrees to indemnify Vendor for all damages without limit.",
            "classification": {"clause_type": "Indemnification", "confidence": 0.95},
            "rule_matches": [{"risk_type": "Unlimited Liability", "risk_level": "high", "explanation": "Unlimited liability."}],
            "similarity_match": None
        }
    ]

    results, summary = analyze_contract_batch(processed_clauses)
    assert len(results) == 2
    assert summary != ""
    assert isinstance(summary, str)
    assert "risk_level" in results[0]
    assert "explanation" in results[0]

def test_generate_contract_summary_fallback():
    clause_results = [
        {"risk_level": "high", "risk_type": "Unlimited Liability"},
        {"risk_level": "safe", "risk_type": "Safe"}
    ]
    summary = generate_contract_summary(clause_results)
    assert "Warning" in summary or "high-risk" in summary.lower()
