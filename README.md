# The Lenny Growth Assistant 🎙️
### Full-Stack AI Conversational Copilot for Product Managers & Growth Teams
**Strictly grounded in genuine transcripts from Lenny’s Podcast**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.141.1-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React 19](https://img.shields.io/badge/React-19.2.8-61DAFB.svg?logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6.svg?logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1.svg?logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-black.svg?logo=ollama&logoColor=white)](https://ollama.com)
[![Tests Passing](https://img.shields.io/badge/Tests-36%20Passed%20(100%25)-10b981.svg)](https://pytest.org)

---

## 1. Project Overview

**The Lenny Growth Assistant** is an elite, full-stack conversational AI product designed for Senior Product Managers, Growth Leads, and Founders. It ingests genuine interview transcripts from **Lenny’s Podcast** (featuring top operators like Shreyas Doshi, Elena Verna, Casey Winters, Brian Balfour, Adam Fishman, and Bangaly Kaba) to answer complex product strategy, growth loop, retention, and leadership questions.

### Key Capabilities:
* **Strict Source Grounding:** Every insight cites real interview moments with guest names, episode titles, verbatim excerpts, relevance scores, and timestamps.
* **Zero-Hallucination Policy:** If the transcript knowledge base does not establish an answer, the assistant transparently reports insufficient evidence rather than guessing.
* **Flexible Multi-Provider Architecture:** Switch seamlessly between local inference (**Ollama**), cloud models (**Anthropic Claude**, **OpenAI**), or the built-in **Offline Grounded Engine**.
* **Claude-Style Artifact Viewer:** Renders generated Markdown documents and interactive HTML/CSS widgets side-by-side with the chat.
* **Defense-in-Depth HTML Sandbox:** Untrusted HTML artifacts are isolated inside a zero-privilege sandboxed `<iframe>` enforcing strict Content Security Policies (`script-src 'none'`).
* **Dedicated Ship 30 for 30 Skill:** Generates ~1,250-word atomic essays adhering to the 1-3-1 cadence, 5-part narrative structure, and selective bold formatting.
* **Zero-Downtime Dual Persistence:** Connects to PostgreSQL (with pgvector support) and automatically engages SQLite fallback if PostgreSQL is unreachable.

---

## 2. Architecture Summary

```
┌─────────────────────────────────────────────────────────────┐
│                 React 19 / TypeScript / Vite                │
│       (Chat Stream • Citations Accordion • Artifact Viewer) │
└──────────────────────────────┬──────────────────────────────┘
                               │ REST / JSON
┌──────────────────────────────▼──────────────────────────────┐
│                    FastAPI Backend Server                   │
│        (Pydantic v2 • Session Isolation • Security Sandbox) │
├──────────────────────────────┬──────────────────────────────┤
│    Hybrid Vector Retrieval   │    Provider Abstraction      │
│  (735 Chunks • TF-IDF + BM25)│(Ollama • Anthropic • OpenAI) │
└──────────────┬───────────────┴──────────────┬───────────────┘
               │                              │
┌──────────────▼───────────────┐ ┌────────────▼───────────────┐
│     PostgreSQL / SQLite      │ │   Local / Cloud LLM APIs   │
│   (Sessions, Chunks, Arts)   │ │  (Llama 3.2, Claude 3.5)   │
└──────────────────────────────┘ └────────────────────────────┘
```

---

## 3. Prerequisites

* **Node.js:** v18.0.0 or later (v20+ recommended)
* **Python:** v3.11 or v3.12
* **Git:** Installed on PATH
* *(Optional)* **Docker & Docker Compose:** For containerized deployment
* *(Optional)* **Ollama:** For local offline LLM demo (`http://localhost:11434`)

---

## 4. Quick-Start Instructions (Local Development)

### Step 1: Clone the Repository
```bash
git clone https://github.com/Pradhiksha040/Growth-assistant.git
cd Growth-assistant
```

### Step 2: Configure Environment
```bash
# Copy example configuration with safe defaults
cp .env.example .env
```
*(On Windows PowerShell: `Copy-Item .env.example .env`)*

### Step 3: Install Backend Dependencies & Seed Knowledge Base
```bash
# 1. Install Python requirements
pip install -r requirements.txt

# 2. Seed database & build hybrid vector index from Lenny's transcripts
python -m scripts.seed_database
```
*Output: `Successfully ingested 8 episodes (735 chunks). Search index built successfully.`*

### Step 4: Run Backend Server
```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
* Backend API: `http://localhost:8000`
* Interactive OpenAPI Docs: `http://localhost:8000/docs`
* Health Probe: `http://localhost:8000/health`

### Step 5: Install & Run Frontend
In a new terminal window:
```bash
cd frontend
npm install
npm run dev
```
* Access the UI at: **`http://localhost:5173`**

---

## 5. Docker Compose Deployment (One-Command)

Run PostgreSQL, FastAPI backend, and React frontend with a single command:
```bash
docker compose up --build
```
* Frontend: `http://localhost:3000`
* Backend API: `http://localhost:8000`
* PostgreSQL with pgvector: `localhost:5432`

---

## 6. LLM Provider Setup & Verification

### 6.1 Local Provider: Ollama (Mandatory for Demo)
1. **Download & Install Ollama:** Visit [ollama.com](https://ollama.com) and install for your OS.
2. **Start the Ollama daemon:**
   ```bash
   ollama serve
   ```
3. **Pull the configured model:**
   ```bash
   ollama pull llama3.2
   ```
4. **Verify Connectivity:** Open the app at `http://localhost:5173`, click the provider badge in the top-right header, select **Ollama (Local LLM)**, and click **Apply**. The badge will turn green and display `Ready`.

> **Note on Fallback Behavior:** If Ollama is not installed or the daemon is closed, the system detects this in $< 2$ seconds and automatically engages the **Offline Grounded Engine**, returning real verbatim transcript excerpts with an actionable notice.

### 6.2 Cloud Providers: Anthropic Claude & OpenAI (Optional)
To use cloud providers, simply populate your keys in `.env`:
```env
ANTHROPIC_API_KEY="sk-ant-api..."
ANTHROPIC_MODEL="claude-3-5-sonnet-20241022"

OPENAI_API_KEY="sk-proj-..."
OPENAI_MODEL="gpt-4o"
```
Switch to Anthropic or OpenAI anytime using the UI modal without restarting the server.

---

## 7. Automated Test Suite (36/36 Passing)

Run the comprehensive automated test suite covering all layers:

```bash
# Run all backend tests
python -m pytest backend/tests -v
```

### Complete Test Coverage Matrix (36 Tests):
* **`test_agent_sdk.py` (6 tests):** Claude Agent SDK tool registration, transcript search tool, growth artifact tool, and unauthenticated diagnostic handling.
* **`test_artifacts.py` (2 tests):** HTML sanitization, script tag stripping, CSP injection, and artifact CRUD/export.
* **`test_health.py` (2 tests):** `/health` liveness and `/ready` indexing readiness endpoints.
* **`test_ollama_verification.py` (5 tests):** Host daemon connectivity, local `llama3.2` model generation, request timeout resilience, multi-turn session preservation, and structured citations.
* **`test_providers.py` (3 tests):** Provider listing, dynamic provider switching, and invalid provider error handling.
* **`test_rag_quality_audit.py` (7 tests):** 7 dedicated audit scenarios: supported query, conversational follow-up, out-of-domain refusal, misleading assumption correction, multi-source synthesis, cross-session isolation, and empty database guidance.
* **`test_retrieval.py` (2 tests):** Hybrid semantic/lexical vector search, citation structuring, and transcript API endpoints.
* **`test_security_audit.py` (6 tests):** CORS origin hardening, production exception masking, request validation bounds (DoS mitigation), defense-in-depth HTML sanitization, cross-session isolation, and SQL injection parameterization.
* **`test_sessions.py` (1 test):** Session lifecycle, message chronological order, and isolation.
* **`test_ship30.py` (2 tests):** Atomic essay generation (~1,250 words), 1-3-1 hook structure, and transcript grounding.

---

## 8. Troubleshooting

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| **`PostgreSQL connection failed` warning on startup** | PostgreSQL service is not running on `localhost:5432`. | **No action needed.** The backend automatically engages its SQLite fallback (`./data/lenny_assistant.db`), ensuring 100% functionality. |
| **Ollama badge shows `Offline / Missing`** | Ollama background process is not running or model not pulled. | Run `ollama serve` in a terminal, and download model via `ollama pull llama3.2`. |
| **`tsc is not recognized` on frontend build** | Global TypeScript missing. | Run `npm install` inside the `frontend/` directory before building. |
| **Port 8000 already in use** | Another process is binding port 8000. | Start uvicorn on another port: `uvicorn backend.app.main:app --port 8080` and set `VITE_API_URL="http://localhost:8080"` in `frontend/.env`. |

---

## 9. Deliverables Directory Map

```
Growth-assistant/
├── PRD.md                  # Discovery brief, user personas, success metrics, scope choices
├── design.md               # UI/UX design rationale, typography, accessibility, split-pane architecture
├── architecture.md         # Component diagrams, DB schema, API contracts, security sandbox
├── agent-transcripts.md    # Index of coding agent execution transcripts and architectural decisions
├── agent-transcripts/
│   └── implementation_execution_log.md  # Detailed execution trajectory, trade-offs, and debug logs
├── docs/
│   ├── DEMO_SCRIPT.md      # 2-3 min video script, recording checklist, and technical trade-off
│   ├── OLLAMA_VERIFICATION.md # Dedicated Local Ollama Verification Report & Evaluator Guide
│   ├── RAG_QUALITY_AUDIT.md   # Dedicated 7-Scenario RAG Quality Audit Report
│   ├── SECURITY_AUDIT.md      # Pre-Commit Security Engineering Review & Threat Modeling Report
│   ├── UI_ACCEPTANCE_TEST_CHECKLIST.md # Frontend QA Acceptance Testing Checklist
│   └── Forward_Deployed_Engineer_Take_Home_Assignment_12_Oct_2026.docx
├── backend/
│   ├── app/                # FastAPI application (routers, schemas, services, models)
│   ├── migrations/         # PostgreSQL DDL init.sql script
│   ├── tests/              # 36 automated unit, integration, and security regression tests
│   ├── Dockerfile          # Backend container specification
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── src/                # React 19 application (components, services, types)
│   ├── Dockerfile          # Multi-stage production Nginx container specification
│   └── package.json        # Frontend scripts and dependencies
├── data/
│   └── transcripts/        # 8 curated Lenny's Podcast markdown transcripts (735 chunks)
├── scripts/
│   └── seed_database.py    # Database schema initialization and ingestion CLI
└── docker-compose.yml      # Orchestration for PostgreSQL, Backend, and Frontend
```

---

## 10. Verification Report & Handoff

* **GitHub Repository:** [https://github.com/Pradhiksha040/Growth-assistant.git](https://github.com/Pradhiksha040/Growth-assistant.git)
* **Branch:** `main`
* **Test Status:** **36/36 Automated Tests Passing** (`python -m pytest backend/tests -v`)
* **Frontend Quality:** **0 errors, 0 warnings** (`npm run lint`, `oxlint`), clean production build (`npm run build`)
* **Security Audit:** **Verified & Secured** (CORS hardened, HTML sandboxed, SQL parameterized, DoS bounded)

---

## 11. Known Limitations & Disclosure of Uncompleted Deliverables

In strict adherence to forward-deployed engineering integrity, the following operational states and external environment requirements are explicitly disclosed:

1. **Local Ollama Daemon Host Requirement:**
   - The application is fully wired and tested to connect to Ollama at `http://localhost:11434` with model `llama3.2`.
   - On host machines without Ollama pre-installed, the application automatically engages the **Lenny Offline Grounded Engine** without throwing 500 errors, displaying a transparent notice. Evaluators wishing to test local inference must follow the setup steps in [Section 6.1](#61-local-provider-ollama-mandatory-for-demo).
2. **Cloud API Keys:**
   - Anthropic Claude and OpenAI integrations require user-provided API keys in `.env`. If unconfigured, the application returns graceful diagnostic guidance rather than unhandled exceptions.
3. **Hardware Video Recording:**
   - Camera-enabled video recording requires physical audio/video capture devices. A complete, minute-by-minute script, visual staging cues, and spoken talking points are provided in [`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md) for recording with Loom, OBS, or QuickTime.

