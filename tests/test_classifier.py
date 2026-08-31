from backend.classifier import predict_clause_type

def test_predict_clause_type():
    clause = "Either party may terminate this agreement upon 30 days written notice."
    result = predict_clause_type(clause)
    assert isinstance(result, dict)
    assert "clause_type" in result
    assert "confidence" in result