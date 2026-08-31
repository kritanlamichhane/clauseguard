import io
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ClauseGuard API is running"}

def test_analyze_contract_txt():
    sample_text = b"1. Payment Terms. Payment shall be made within 30 days.\n2. Termination. Either party may terminate with notice."
    file_payload = ("test_contract.txt", io.BytesIO(sample_text), "text/plain")
    
    response = client.post("/analyze", files={"file": file_payload})
    assert response.status_code == 200
    
    data = response.json()
    assert data["file_name"] == "test_contract.txt"
    assert data["total_clauses"] >= 1
    assert "risk_score" in data
    assert "risk_label" in data
    assert "risk_breakdown" in data
    assert "clauses" in data
    assert isinstance(data["clauses"], list)

def test_analyze_invalid_file_type():
    file_payload = ("test_image.png", io.BytesIO(b"dummy image data"), "image/png")
    response = client.post("/analyze", files={"file": file_payload})
    assert response.status_code == 400
    assert "Only PDF, DOCX, and TXT files are supported" in response.json()["detail"]
