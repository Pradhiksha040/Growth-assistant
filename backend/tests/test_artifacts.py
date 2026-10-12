"""
Automated tests for Artifact Management and HTML Security Isolation.
Verifies script stripping, event handler removal, CSP injection, and export endpoints.
"""
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.artifact_service import artifact_service

client = TestClient(app)

def test_html_sanitization_and_isolation():
    unsafe_html = """
    <div>
        <h2>Growth Dashboard</h2>
        <script>alert('XSS Attack');</script>
        <button onclick="stealCookies()">Click me</button>
        <a href="javascript:doEvil()">Malicious Link</a>
        <iframe src="http://attacker.com"></iframe>
        <p>Legitimate PM content</p>
    </div>
    """
    safe_html = artifact_service.sanitize_and_isolate_html(unsafe_html, "Dashboard")

    # Verify all dangerous elements and attributes are eliminated
    assert "<script>" not in safe_html
    assert "alert(" not in safe_html
    assert "onclick=" not in safe_html
    assert "javascript:" not in safe_html
    assert "<iframe" not in safe_html
    assert "Legitimate PM content" in safe_html

    # Verify Content-Security-Policy is present
    assert "Content-Security-Policy" in safe_html
    assert "default-src 'none'" in safe_html

def test_artifact_crud_and_export():
    # 1. Create a session
    sess_res = client.post("/api/v1/sessions", json={"title": "Artifacts Session"})
    session_id = sess_res.json()["id"]

    # 2. Create an HTML artifact
    html_res = client.post("/api/v1/artifacts", json={
        "session_id": session_id,
        "type": "html",
        "title": "Onboarding Funnel Metric Chart",
        "content": "<div class='card'><h3>Signups to Activation</h3><p>Rate: 42%</p><script>console.log('bad');</script></div>"
    })
    assert html_res.status_code == 201
    html_data = html_res.json()
    assert html_data["type"] == "html"
    assert "<script>" not in html_data["content"]
    assert "Content-Security-Policy" in html_data["content"]
    artifact_id = html_data["id"]

    # 3. Retrieve artifact
    get_res = client.get(f"/api/v1/artifacts/{artifact_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == artifact_id

    # 4. List artifacts for session
    list_res = client.get(f"/api/v1/artifacts?session_id={session_id}")
    assert list_res.status_code == 200
    assert list_res.json()["total"] >= 1

    # 5. Export artifact
    export_res = client.get(f"/api/v1/artifacts/{artifact_id}/export")
    assert export_res.status_code == 200
    assert "text/html" in export_res.headers["content-type"]
    assert "attachment; filename=" in export_res.headers["content-disposition"]
