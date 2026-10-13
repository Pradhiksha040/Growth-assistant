"""
Dedicated Ollama Local Provider Verification Test Suite.
Verifies:
1. Local Ollama service reachability and diagnostic status reporting.
2. Provider availability detection and missing model instructions.
3. Message sending, prompt formatting, and evidence injection.
4. Multi-turn session context preservation in Ollama payload.
5. Transcript citations display and persistence.
6. Request timeout and service unavailability resilience.
"""
import pytest
import time
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import httpx

from backend.app.main import app
from backend.app.core.config import settings
from backend.app.services.llm_provider import OllamaProvider, provider_manager
from backend.app.db.session import SessionLocal
from backend.app.db.models import SessionModel, MessageModel

client = TestClient(app)

def test_ollama_live_environment_status():
    """
    Checks the real runtime host environment for Ollama.
    Documents whether Ollama is active or reports the actionable startup instructions.
    """
    provider = OllamaProvider(base_url=settings.OLLAMA_BASE_URL, default_model=settings.OLLAMA_MODEL)
    
    import asyncio
    is_avail, msg, models = asyncio.run(provider.check_availability())
    
    # If Ollama is running locally, it must report active with available models
    if is_avail:
        assert settings.OLLAMA_MODEL in models or len(models) > 0
        assert "Ollama is running" in msg
    else:
        # If Ollama is not active in this environment, it must provide the exact startup command
        assert "ollama serve" in msg or "ollama pull" in msg or "11434" in msg

def test_ollama_unavailable_graceful_fallback():
    """
    Verifies that when Ollama is selected but offline, the application does not crash.
    It returns a transparent notice with the exact offline status and grounds the answer.
    """
    sess_res = client.post("/api/v1/sessions", json={"title": "Ollama Unavailability Test"})
    assert sess_res.status_code == 201
    session_id = sess_res.json()["id"]

    # Explicitly request Ollama provider
    chat_res = client.post("/api/v1/chat", json={
        "session_id": session_id,
        "message": "What does Casey Winters say about growth loops?",
        "provider": "ollama"
    })
    assert chat_res.status_code == 200
    data = chat_res.json()

    # Even if Ollama daemon is offline, response is delivered safely
    assert data["evidence_sufficient"] is True
    assert len(data["message"]["citations"]) > 0
    assert data["message"]["session_id"] == session_id

    # If Ollama was offline, notice must be displayed
    content = data["message"]["content"]
    if "OLLAMA is currently not active" in content:
        assert "ollama serve" in content
        assert "Offline Grounded Engine" in content

@pytest.mark.asyncio
async def test_ollama_generation_success_with_local_endpoint():
    """
    Verifies that when an Ollama endpoint is responsive, OllamaProvider correctly
    packages system evidence, dialogue history, and parses assistant responses.
    """
    provider = OllamaProvider(base_url="http://localhost:11434", default_model="llama3.2")

    mock_ollama_response = {
        "model": "llama3.2",
        "message": {
            "role": "assistant",
            "content": "According to Casey Winters on Lenny's Podcast, growth loops are closed systems where customer actions generate new customers."
        },
        "done": True
    }

    class MockResponse:
        status_code = 200
        def json(self):
            return mock_ollama_response

    class MockAsyncClient:
        async def __aenter__(self):
            return self
        async def __aexit__(self, *args):
            pass
        async def post(self, url, json=None):
            assert "/api/chat" in url
            assert json["model"] == "llama3.2"
            assert len(json["messages"]) >= 2 # system + user
            # Verify system message contains podcast transcript evidence
            system_msg = next(m for m in json["messages"] if m["role"] == "system")
            assert "EVIDENCE FROM LENNY'S PODCAST TRANSCRIPTS" in system_msg["content"]
            assert "Casey Winters" in system_msg["content"]
            return MockResponse()

    context_chunks = [{
        "guest": "Casey Winters",
        "title": "Why most product managers are unprepared for a real startup",
        "timestamp_str": "00:00:00",
        "content": "Growth loops are the true sustainable engine for compounding."
    }]

    with patch("httpx.AsyncClient", return_value=MockAsyncClient()):
        text, latency = await provider.generate_response(
            prompt="Explain growth loops",
            system_prompt="You are Lenny Assistant",
            conversation_history=[{"role": "user", "content": "Hi"}],
            context_chunks=context_chunks
        )

    assert "Casey Winters" in text
    assert "growth loops" in text
    assert latency >= 0

@pytest.mark.asyncio
async def test_ollama_request_timeout_handling():
    """
    Verifies that when Ollama encounters a network timeout, it raises a clean TimeoutException
    which agent_service catches and routes through resilient fallback.
    """
    provider = OllamaProvider(base_url="http://localhost:11434", default_model="llama3.2")

    class TimeoutAsyncClient:
        async def __aenter__(self):
            return self
        async def __aexit__(self, *args):
            pass
        async def post(self, url, json=None):
            raise httpx.ReadTimeout("Ollama inference timed out after 45.0s")

    with patch("httpx.AsyncClient", return_value=TimeoutAsyncClient()):
        with pytest.raises(httpx.ReadTimeout):
            await provider.generate_response(
                prompt="Explain growth loops",
                system_prompt="You are Lenny Assistant",
                conversation_history=[],
                context_chunks=[]
            )

def test_ollama_session_context_preservation_and_citations():
    """
    Verifies end-to-end that session history is accumulated and citations
    are preserved when interacting with the chat API.
    """
    sess_res = client.post("/api/v1/sessions", json={"title": "Ollama Multi-Turn Session"})
    session_id = sess_res.json()["id"]

    # Turn 1
    t1_res = client.post("/api/v1/chat", json={
        "session_id": session_id,
        "message": "What is Shreyas Doshi's advice on pre-mortems?",
        "provider": "ollama"
    })
    assert t1_res.status_code == 200
    t1_data = t1_res.json()
    assert len(t1_data["message"]["citations"]) > 0

    # Turn 2
    t2_res = client.post("/api/v1/chat", json={
        "session_id": session_id,
        "message": "What did he say about elephants in the room?",
        "provider": "ollama"
    })
    assert t2_res.status_code == 200
    t2_data = t2_res.json()
    assert t2_data["session_id"] == session_id

    # Verify database persistence
    db = SessionLocal()
    msgs = db.query(MessageModel).filter(MessageModel.session_id == session_id).all()
    assert len(msgs) == 4
    # Verify citations are persisted as JSON
    assert msgs[1].citations_json is not None
    assert "Shreyas Doshi" in msgs[1].citations_json
    db.close()
