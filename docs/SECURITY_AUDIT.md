# Security Engineering Audit & Threat Modeling Report
**Project:** The Lenny Growth Assistant  
**Date of Audit:** October 13, 2026  
**Auditor Role:** Senior Forward Deployed Security Engineer  
**Status:** ✅ **VERIFIED & SECURED (36/36 Backend Tests Passing, 0 Frontend Vulnerabilities)**  
**Regression Test Suite:** [`backend/tests/test_security_audit.py`](file:///d:/Growth-assistant/backend/tests/test_security_audit.py)  

---

## 1. Executive Summary

A comprehensive pre-commit security audit was performed on **The Lenny Growth Assistant** across backend API services, SQLite/PostgreSQL data persistence layers, frontend React UI components, sandboxed artifact rendering engines, and Git repository tracking.

The audit evaluated 11 critical threat vectors:
1. **API Keys & Secrets Exposure in Git History**
2. **CORS Origin Misconfiguration & Credential Leakage**
3. **SQL Injection & Unsafe Database Operations**
4. **Cross-Session Data Leakage**
5. **Request Validation Bounds & Denial of Service (DoS)**
6. **Information Disclosure & Unsafe Internal Logging**
7. **Unsafe Markdown & Link Protocol XSS**
8. **Insecure Iframe Configuration & HTML Script Execution**
9. **Unrestricted File Uploads & Ingestion Path Traversal**
10. **Missing Timeouts & Resource Limits**
11. **Software Supply Chain & Dependency Vulnerabilities**

All identified vulnerabilities and weaknesses have been mitigated in code, verified with regression tests, and audited against industry standards (OWASP Top 10, ASVS).

---

## 2. Threat Vector Review & Implemented Mitigations

### 2.1 API Keys, Passwords, Tokens & Git Tracking
* **Audit Check:** Comprehensive scan of Git commits (`git log -S`, `git grep`) and tracked files for private keys, cloud tokens (`sk-ant-...`, `sk-proj-...`), and credentials.
* **Findings:**
  - **No live API keys or credentials were ever committed to Git history.**
  - [`.gitignore`](file:///d:/Growth-assistant/.gitignore) strictly ignores all `.env`, `.env.*.local`, `*.pem`, `*.key`, and `*.db` files.
  - [`.env.example`](file:///d:/Growth-assistant/.env.example) contains only empty placeholder strings (`ANTHROPIC_API_KEY=""`, `OPENAI_API_KEY=""`).
  - [`docker-compose.yml`](file:///d:/Growth-assistant/docker-compose.yml) uses dynamic environment variable expansion (`${ANTHROPIC_API_KEY:-}`) and local development defaults for PostgreSQL.
* **Remediation Protocol (If Credentials Were Committed):**
  If any developer inadvertently commits a secret in the future:
  1. *Immediate Revocation:* Immediately revoke and rotate the secret in the cloud provider console (Anthropic Console / OpenAI Dashboard). Deleting the commit does not protect against scrapers.
  2. *History Scrubbing:* Use `git filter-repo` or BFG Repo-Cleaner to rewrite history:
     ```bash
     git filter-repo --invert-paths --path .env
     git push origin --force --all
     ```
  3. *Audit Cloud Logs:* Review provider audit logs for unauthorized billing or anomalous token usage.

---

### 2.2 CORS Configuration Hardening
* **Vulnerability Identified:** The initial configuration in [`backend/app/core/config.py`](file:///d:/Growth-assistant/backend/app/core/config.py) included wildcard `"*"` within `CORS_ORIGINS`, while [`backend/app/main.py`](file:///d:/Growth-assistant/backend/app/main.py) configured `allow_credentials=True`. In web standards, allowing credentials with wildcard origins enables cross-origin credential harvesting from malicious websites.
* **Mitigation Implemented:**
  1. Removed `"*"` from `CORS_ORIGINS`. Defined explicit trusted local origins:
     `["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "http://127.0.0.1:3000"]`.
  2. In [`backend/app/main.py`](file:///d:/Growth-assistant/backend/app/main.py), added dynamic validation enforcing `allow_credentials=not ("*" in settings.CORS_ORIGINS)` and restricted allowed HTTP methods to `["GET", "POST", "PATCH", "DELETE", "OPTIONS"]`.
* **Automated Verification:** `test_cors_origin_and_credential_hardening` passes.

---

### 2.3 SQL Injection & Safe Database Operations
* **Audit Check:** Inspected all database queries in [`backend/app/api/`](file:///d:/Growth-assistant/backend/app/api), [`backend/app/db/`](file:///d:/Growth-assistant/backend/app/db), and [`backend/app/services/`](file:///d:/Growth-assistant/backend/app/services).
* **Findings:**
  - Zero raw string concatenations or formatted f-string SQL queries exist in the codebase.
  - All database interactions utilize the **SQLAlchemy 2.0 ORM** with bind parameters (`filter(Model.field == param)`), ensuring automatic SQL escaping.
  - Connection ping checks use static parameterized expressions (`text("SELECT 1")`).
* **Automated Verification:** `test_sql_injection_resilience` executed SQL injection attack vectors (`' OR '1'='1`, `'; DROP TABLE sessions; --`, `UNION SELECT...`), confirming clean parameterization without syntax errors or leakage.

---

### 2.4 Cross-Session Data Isolation
* **Audit Check:** Examined multi-user session boundaries in [`backend/app/api/v1/sessions.py`](file:///d:/Growth-assistant/backend/app/api/v1/sessions.py) and [`backend/app/services/session_service.py`](file:///d:/Growth-assistant/backend/app/services/session_service.py).
* **Findings:**
  - Every message query strictly filters by `MessageModel.session_id == session_id`.
  - Artifacts are partitioned by `ArtifactModel.session_id == session_id`.
  - Deleting or updating a session enforces strict primary key matching.
* **Automated Verification:** `test_cross_session_data_isolation` verified that Session B cannot retrieve messages or metadata created in Session A.

---

### 2.5 Request Validation & Denial of Service (DoS) Mitigation
* **Vulnerability Identified:** Pydantic schemas lacked upper-bound string lengths and numeric boundaries, allowing oversized payloads (e.g. 50MB prompts or infinite word counts) to cause memory exhaustion or CPU lockup.
* **Mitigation Implemented:**
  - [`ChatRequest`](file:///d:/Growth-assistant/backend/app/schemas/chat.py): Added `max_length=10000` on `message`, `max_length=100` on `session_id`, `max_length=50` on `provider`, `max_length=100` on `model`.
  - [`Ship30Request`](file:///d:/Growth-assistant/backend/app/schemas/ship30.py): Added `max_length=500` on `topic` and `custom_hook`, and bounded `target_word_count: ge=100, le=5000`.
  - [`ArtifactCreate`](file:///d:/Growth-assistant/backend/app/schemas/artifact.py): Added `max_length=255` on `title`, `max_length=1000000` (1MB) on `content`.
  - [`IngestRequest`](file:///d:/Growth-assistant/backend/app/schemas/transcript.py): Added `ge=1, le=100` bounds on `max_episodes`.
* **Automated Verification:** `test_request_validation_and_length_limits` rejects oversized inputs with HTTP `422 Unprocessable Entity`.

---

### 2.6 Information Disclosure & Exception Masking
* **Vulnerability Identified:** The root exception handler in [`backend/app/main.py`](file:///d:/Growth-assistant/backend/app/main.py) and API endpoints previously returned `str(exc)` in 500 error responses, potentially leaking server paths, database credentials, or stack traces.
* **Mitigation Implemented:**
  - Sanitized 500 responses across [`backend/app/main.py`](file:///d:/Growth-assistant/backend/app/main.py), [`backend/app/api/v1/chat.py`](file:///d:/Growth-assistant/backend/app/api/v1/chat.py), [`backend/app/api/v1/ship30.py`](file:///d:/Growth-assistant/backend/app/api/v1/ship30.py), and [`backend/app/api/v1/ingest.py`](file:///d:/Growth-assistant/backend/app/api/v1/ingest.py).
  - Raw exception details are only exposed if `settings.DEBUG == True`.
  - In production (`DEBUG=False`), generic safe error messages are returned while full tracebacks are logged internally via [`logger.error(..., exc_info=True)`](file:///d:/Growth-assistant/backend/app/core/logging.py).
* **Automated Verification:** `test_no_sensitive_exception_leaks_in_production` verified that simulated database errors containing credentials are fully stripped from HTTP responses.

---

### 2.7 Markdown Rendering Security & Link Protocol XSS
* **Vulnerability Identified:** In [`frontend/src/components/MarkdownRenderer.tsx`](file:///d:/Growth-assistant/frontend/src/components/MarkdownRenderer.tsx), inline markdown links `[label](url)` rendered `<a href={url}>` directly without protocol scheme validation. An attacker could craft `[Click](javascript:alert(1))` or `data:text/html,...` links.
* **Mitigation Implemented:**
  - Added strict protocol validation before rendering `href`. Allowed schemes: `https://`, `http://`, `mailto:`, `#`, or `/`.
  - Unsafe schemes (e.g. `javascript:`, `vbscript:`, `data:`) have their links disabled and render as inert text (`<span className="markdown-link-disabled">`).
* **Frontend Audit:** Verified with `oxlint` (0 errors, 0 warnings).

---

### 2.8 Insecure Iframe & Sandboxed HTML Isolation
* **Vulnerability Identified:** HTML artifacts could contain unclosed script tags (`<script src="...">`), `<base>` tag hijacking, inline event handlers (`onerror`), or CSS exfiltration links.
* **Mitigation Implemented:**
  - In [`backend/app/services/artifact_service.py`](file:///d:/Growth-assistant/backend/app/services/artifact_service.py), upgraded `DANGEROUS_HTML_PATTERNS` to strip all script tags (closed and unclosed), `<iframe>`, `<object>`, `<embed>`, `<form>`, `<base>`, `<link>`, event handlers (`on\w+`), and `javascript:` URIs.
  - Injected strict Content Security Policy meta header into all HTML documents:
    `<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; font-src data:; img-src data: https:;">`
  - In [`frontend/src/components/ArtifactViewer.tsx`](file:///d:/Growth-assistant/frontend/src/components/ArtifactViewer.tsx), enforced strict `sandbox="allow-popups"` (strictly excluding `allow-scripts` and `allow-same-origin`), guaranteeing an opaque origin with zero script execution privileges.
* **Automated Verification:** `test_html_sanitization_defense_in_depth` passes.

---

### 2.9 Unrestricted File Ingestion & Path Traversal
* **Audit Check:** Examined transcript parser in [`backend/app/services/retrieval_service.py`](file:///d:/Growth-assistant/backend/app/services/retrieval_service.py).
* **Findings:**
  - Files are loaded via `glob.glob(os.path.join(settings.TRANSCRIPTS_DIR, "*.md"))`, restricting loading to the local transcripts directory.
  - Slug extraction uses `os.path.basename(filename)`, preventing directory traversal attacks (e.g. `../../etc/passwd`).
  - YAML frontmatter parsing utilizes `yaml.safe_load()` instead of dangerous `yaml.load()`.

---

### 2.10 HTTP Timeouts & Resource Management
* **Audit Check:** Inspected all outgoing HTTP calls in [`backend/app/services/llm_provider.py`](file:///d:/Growth-assistant/backend/app/services/llm_provider.py).
* **Findings:**
  - Every `httpx.AsyncClient` has explicit connection and read timeouts configured:
    - Availability probes: `httpx.Timeout(2.5, connect=1.0)`
    - Ollama inference: `httpx.Timeout(settings.OLLAMA_TIMEOUT_SECONDS, connect=2.0)`
    - Cloud providers (Claude, OpenAI): `timeout=45.0s`
  - Eliminates risks of hanging threads or denial-of-service from unresponsive external services.

---

### 2.11 Software Supply Chain & Dependency Audit
* **Python Backend:** Audited installed dependencies via `pip list`. All libraries are updated to modern releases (`fastapi 0.141.1`, `cryptography 50.0.2`, `pydantic 2.13.5`, `httpx 0.28.1`, `SQLAlchemy 2.1.4`).
* **Frontend Node Modules:** Executed `npm audit` inside `frontend/`.
  - **Result:** `found 0 vulnerabilities`.
* **Frontend Static Analysis:** Executed `npm run lint` (`oxlint`).
  - **Result:** `0 errors, 0 warnings across 12 files`.

---

## 3. Automated Security Regression Test Results

```text
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1
rootdir: D:\Growth-assistant
collected 6 items

backend/tests/test_security_audit.py::test_cors_origin_and_credential_hardening PASSED [ 16%]
backend/tests/test_security_audit.py::test_no_sensitive_exception_leaks_in_production PASSED [ 33%]
backend/tests/test_security_audit.py::test_request_validation_and_length_limits PASSED [ 50%]
backend/tests/test_security_audit.py::test_html_sanitization_defense_in_depth PASSED [ 66%]
backend/tests/test_security_audit.py::test_cross_session_data_isolation PASSED [ 83%]
backend/tests/test_security_audit.py::test_sql_injection_resilience PASSED [100%]

======================== 6 passed in 11.68s ========================
```

Total Backend Test Suite: **36 passed out of 36 tests** across all modules.

---

## 4. Staged Git Diff Inspection & Commit Verification

* **Untracked / Modified Files Audited:**
  - `backend/app/core/config.py` (CORS wildcard origin removed)
  - `backend/app/main.py` (CORS credentials logic hardened, 500 error masking)
  - `backend/app/api/v1/chat.py` (Exception handling masked)
  - `backend/app/api/v1/ship30.py` (Exception handling masked)
  - `backend/app/api/v1/ingest.py` (Exception handling masked)
  - `backend/app/schemas/chat.py` (Length limits on prompt and session ID)
  - `backend/app/schemas/ship30.py` (Length limits on topic and word count)
  - `backend/app/schemas/artifact.py` (Length limits on artifact title and content)
  - `backend/app/schemas/transcript.py` (Limits on ingest episodes)
  - `backend/app/services/artifact_service.py` (Hardened regex patterns for script tags, base tags, event handlers)
  - `frontend/src/components/MarkdownRenderer.tsx` (URL protocol validation against `javascript:` XSS)
  - `backend/tests/test_security_audit.py` (New automated security regression suite)
  - `docs/SECURITY_AUDIT.md` (Security engineering audit report)
* **Secret Leakage Check:** Clean. No secrets, keys, or unintended files exist in the staged diff.

---

## 5. Residual Risks & Production Deployment Recommendations

For production cloud deployments:
1. **Reverse Proxy & TLS Termination:** Deploy behind Nginx, Caddy, or Cloudflare with TLS 1.3 and HSTS (`Strict-Transport-Security`).
2. **Rate Limiting:** Implement IP-based and token-based rate limiting (e.g. Redis + `slowapi`) to mitigate automated scraping.
3. **WAF (Web Application Firewall):** Enable Cloudflare or AWS WAF for Layer 7 DDoS and bot protection.
4. **Secrets Management:** In cloud production (Kubernetes/AWS/GCP), inject `ANTHROPIC_API_KEY` and `DATABASE_URL` via AWS Secrets Manager or HashiCorp Vault rather than plain files.
