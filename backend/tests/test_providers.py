"""
Automated tests for LLM Provider abstraction, availability inspection, and switching.
"""
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_list_providers():
    res = client.get("/api/v1/providers")
    assert res.status_code == 200
    data = res.json()
    assert "active_provider" in data
    assert "providers" in data
    provider_names = [p["name"] for p in data["providers"]]
    assert "ollama" in provider_names
    assert "anthropic" in provider_names
    assert "openai" in provider_names
    assert "offline" in provider_names

def test_select_provider_offline():
    res = client.post("/api/v1/providers/select", json={
        "provider": "offline",
        "model": "lenny-grounded-engine-v1"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["active_provider"] == "offline"
    assert data["is_available"] is True

def test_select_invalid_provider():
    res = client.post("/api/v1/providers/select", json={
        "provider": "non_existent_provider_xyz"
    })
    assert res.status_code == 400
