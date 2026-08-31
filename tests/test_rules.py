from backend.rules import flag_clause, flag_all_clauses

def test_flag_clause_indemnification():
    clause = "Contractor agrees to indemnify and hold harmless the Company from any claims."
    matches = flag_clause(clause)
    assert len(matches) > 0
    assert any(m["risk_type"] == "Indemnification" for m in matches)

def test_flag_clause_one_sided_liability():
    clause = "The Company shall not be liable for any damages of any kind."
    matches = flag_clause(clause)
    assert len(matches) > 0
    assert any(m["risk_type"] == "One-sided liability" for m in matches)

def test_flag_all_clauses():
    clauses = ["Contractor disclaims all liability.", "Standard payment terms."]
    results = flag_all_clauses(clauses)
    assert len(results) == 2
    assert "matches" in results[0]