"""
Automated tests for Session Management, message persistence, and session isolation.
"""
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_session_lifecycle_and_isolation():
    # 1. Create Session A
    resp_a = client.post("/api/v1/sessions", json={"title": "Session A - Growth Loops"})
    assert resp_a.status_code == 201
    session_a = resp_a.json()
    id_a = session_a["id"]
    assert session_a["title"] == "Session A - Growth Loops"

    # 2. Create Session B
    resp_b = client.post("/api/v1/sessions", json={"title": "Session B - Retention"})
    assert resp_b.status_code == 201
    session_b = resp_b.json()
    id_b = session_b["id"]
    assert id_a != id_b

    # 3. Send message in Session A
    msg_a = client.post("/api/v1/chat", json={
        "session_id": id_a,
        "message": "How does Casey Winters think about growth loops?"
    })
    assert msg_a.status_code == 200
    data_a = msg_a.json()
    assert data_a["session_id"] == id_a

    # 4. Check messages in Session A
    msgs_a = client.get(f"/api/v1/sessions/{id_a}/messages")
    assert msgs_a.status_code == 200
    list_a = msgs_a.json()
    assert len(list_a) == 2  # user + assistant

    # 5. Check messages in Session B (Isolation verification: must be completely empty!)
    msgs_b = client.get(f"/api/v1/sessions/{id_b}/messages")
    assert msgs_b.status_code == 200
    list_b = msgs_b.json()
    assert len(list_b) == 0, "Session B must have zero messages (strict session context isolation)"

    # 6. Update session title
    patch_resp = client.patch(f"/api/v1/sessions/{id_a}", json={"title": "Updated Growth Loops"})
    assert patch_resp.status_code == 200
    assert patch_resp.json()["title"] == "Updated Growth Loops"

    # 7. Delete session B
    del_resp = client.delete(f"/api/v1/sessions/{id_b}")
    assert del_resp.status_code == 204

    # 8. Verify session B is gone
    get_b = client.get(f"/api/v1/sessions/{id_b}")
    assert get_b.status_code == 404
