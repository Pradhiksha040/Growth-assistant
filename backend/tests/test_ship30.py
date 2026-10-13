"""
Automated tests for Ship 30 for 30 Content Generation Skill.
Verifies structure, hook, citations, word count target, and insufficient evidence behavior.
"""
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_ship30_generation_success():
    # 1. Create a session
    sess_res = client.post("/api/v1/sessions", json={"title": "Ship 30 Test Session"})
    assert sess_res.status_code == 201
    session_id = sess_res.json()["id"]

    # 2. Generate Ship 30 essay on Casey Winters growth loops
    res = client.post("/api/v1/ship30/generate", json={
        "session_id": session_id,
        "topic": "Growth loops vs traditional marketing funnels"
    })
    assert res.status_code == 200
    data = res.json()

    assert data["evidence_sufficient"] is True
    assert len(data["title"]) > 0
    assert len(data["essay_markdown"]) > 100
    assert data["word_count"] >= 1000, f"Expected word count >= 1000, got {data['word_count']}"
    assert "Part I:" in data["essay_markdown"]
    assert "Part II:" in data["essay_markdown"]
    assert "Part III:" in data["essay_markdown"]
    assert "Part IV:" in data["essay_markdown"]
    assert "Part V:" in data["essay_markdown"]
    assert len(data["citations"]) > 0
    assert data["artifact"] is not None
    assert data["artifact"]["type"] == "markdown"
    assert data["artifact"]["session_id"] == session_id

def test_ship30_insufficient_evidence():
    # Create session
    sess_res = client.post("/api/v1/sessions", json={"title": "Ship 30 OOD Session"})
    session_id = sess_res.json()["id"]

    # Request essay on completely unrelated topic
    res = client.post("/api/v1/ship30/generate", json={
        "session_id": session_id,
        "topic": "Deep sea trench hydrothermal vents biology"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["evidence_sufficient"] is False
    assert "Insufficient Transcript Evidence" in data["essay_markdown"]
