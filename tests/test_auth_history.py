import io
import uuid
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_auth_and_history_full_flow():
    uid = uuid.uuid4().hex[:8]
    # 1. Register User A
    user_a_email = f"testuser_a_{uid}@clauseguard.io"
    user_a_password = "password123"
    user_a_username = "Alice Law"

    reg_res = client.post("/auth/register", json={
        "email": user_a_email,
        "username": user_a_username,
        "password": user_a_password
    })
    assert reg_res.status_code == 200
    reg_data = reg_res.json()
    assert "access_token" in reg_data
    token_a = reg_data["access_token"]
    assert reg_data["user"]["email"] == user_a_email
    assert reg_data["user"]["username"] == user_a_username

    # 2. Duplicate registration should fail
    dup_res = client.post("/auth/register", json={
        "email": user_a_email,
        "username": "Duplicate",
        "password": "password123"
    })
    assert dup_res.status_code == 400
    assert "already exists" in dup_res.json()["detail"]

    # 3. Test /auth/me
    headers_a = {"Authorization": f"Bearer {token_a}"}
    me_res = client.get("/auth/me", headers=headers_a)
    assert me_res.status_code == 200
    assert me_res.json()["email"] == user_a_email

    # 4. Login User A
    login_res = client.post("/auth/login", json={
        "email": user_a_email,
        "password": user_a_password
    })
    assert login_res.status_code == 200
    token_a = login_res.json()["access_token"]

    # 5. Invalid login should fail
    bad_login = client.post("/auth/login", json={
        "email": user_a_email,
        "password": "wrongpassword"
    })
    assert bad_login.status_code == 401

    # 6. Authenticated contract analysis (should auto-save to history)
    sample_text = b"1. Payment Terms. Payment is due in 30 days.\n2. Liability. Contractor shall indemnify client for all damages."
    file_payload = ("nda_contract.txt", io.BytesIO(sample_text), "text/plain")

    analyze_res = client.post(
        "/analyze",
        files={"file": file_payload},
        headers=headers_a
    )
    assert analyze_res.status_code == 200
    analyze_data = analyze_res.json()
    assert analyze_data["file_name"] == "nda_contract.txt"
    assert analyze_data.get("history_id") is not None
    history_id = analyze_data["history_id"]

    # 7. Check /history list
    hist_res = client.get("/history", headers=headers_a)
    assert hist_res.status_code == 200
    history_list = hist_res.json()
    assert len(history_list) >= 1
    found_item = next((item for item in history_list if item["id"] == history_id), None)
    assert found_item is not None
    assert found_item["file_name"] == "nda_contract.txt"

    # 8. Check /history/{id} detail
    detail_res = client.get(f"/history/{history_id}", headers=headers_a)
    assert detail_res.status_code == 200
    detail_data = detail_res.json()
    assert detail_data["id"] == history_id
    assert detail_data["file_name"] == "nda_contract.txt"
    assert len(detail_data["clauses"]) >= 1

    # 9. Test User Isolation: Register User B
    user_b_email = f"testuser_b_{uid}@clauseguard.io"
    user_b_reg = client.post("/auth/register", json={
        "email": user_b_email,
        "username": "Bob Risk",
        "password": "password456"
    })
    token_b = user_b_reg.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User B should NOT be able to access User A's history item
    b_detail_res = client.get(f"/history/{history_id}", headers=headers_b)
    assert b_detail_res.status_code == 404

    # User B history should be empty
    b_hist_res = client.get("/history", headers=headers_b)
    assert b_hist_res.status_code == 200
    assert len(b_hist_res.json()) == 0

    # 10. Simulate Logout and Relogin for User A (Persistence test)
    # Re-authenticating with User A credentials
    relogin_res = client.post("/auth/login", json={
        "email": user_a_email,
        "password": user_a_password
    })
    assert relogin_res.status_code == 200
    new_token_a = relogin_res.json()["access_token"]
    new_headers_a = {"Authorization": f"Bearer {new_token_a}"}

    # History must still be present and persistent
    relogin_hist = client.get("/history", headers=new_headers_a)
    assert relogin_hist.status_code == 200
    assert any(item["id"] == history_id for item in relogin_hist.json())

    # 11. Delete history item
    del_res = client.delete(f"/history/{history_id}", headers=new_headers_a)
    assert del_res.status_code == 200

    # Item should now be gone
    get_del_res = client.get(f"/history/{history_id}", headers=new_headers_a)
    assert get_del_res.status_code == 404
