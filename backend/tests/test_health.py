"""
Automated tests for health and readiness probes.
"""
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "database" in data
    assert "active_provider" in data
    assert data["database"]["status"] == "connected"

def test_readiness_endpoint():
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert "ready" in data
    assert "episodes_indexed" in data
    assert "chunks_indexed" in data
    assert data["chunks_indexed"] > 0
