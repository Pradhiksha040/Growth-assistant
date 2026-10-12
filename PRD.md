# Product Requirements Document (PRD)
## The Lenny Growth Assistant
**Author:** Forward Deployed Engineering Team  
**Date:** October 12, 2026  
**Status:** Implemented & Verified  
**Target Repository:** [https://github.com/Pradhiksha040/Growth-assistant.git](https://github.com/Pradhiksha040/Growth-assistant.git)

---

## 1. Executive Summary & Forward Deployment Brief

### 1.1 Primary User & Problem Framing
* **Target Personas:** 
  1. **Senior & Lead Product Managers (PMs)** designing growth loops, onboarding funnels, and activation metrics.
  2. **Growth Leads & Heads of Growth** building high-performing growth squads, experimenting with PLG vs. PLS motions, and optimizing acquisition-retention loops.
* **The Core Problem:** 
  Product leaders are inundated with generic, non-contextual AI advice from generic chat models that hallucinate product frameworks or offer platitudes. Meanwhile, Lenny’s Podcast contains thousands of hours of high-signal, battle-tested operational playbooks from top operators (Shreyas Doshi, Elena Verna, Casey Winters, Brian Balfour, Adam Fishman, Bangaly Kaba). However, this knowledge is locked in lengthy audio recordings and text transcripts that are difficult to query, synthesize, cite, and convert into actionable deliverables.
* **Jobs to be Done (JTBD):**
  > *"When I am planning our product growth roadmap or diagnosing a retention leak, I want to query the exact playbooks and mental models used by top operators on Lenny's Podcast, so that I can validate our strategy against real-world evidence without spending hours skimming transcripts."*

### 1.2 Measurable Success Metrics
1. **Source Grounding Accuracy (Operational Metric):** $\ge 98\%$ of synthesized claims in grounded mode directly map to verbatim transcript excerpts.
2. **Hallucination Rate (Risk Metric):** $0\%$ fabricated quotes, false guest names, or unsupported episode attributions. When evidence is missing, the system strictly returns an explicit "insufficient evidence" notice.
3. **Time to Actionable Deliverable (Productivity Metric):** Reduction of Ship 30 for 30 essay generation and artifact drafting time from 2 hours to $< 15$ seconds.
4. **Zero-Configuration Availability (Operability Metric):** $100\%$ zero-downtime startup via local SQLite and offline grounded fallback even when external databases or LLM daemons are unreachable.

### 1.3 Key Assumptions
1. **Knowledge Boundary:** Lenny's Podcast transcripts serve as the sole source of truth for conversational claims; external general-knowledge speculation is intentionally restricted.
2. **Evaluator Environment Heterogeneity:** Client evaluators may run the application on diverse host environments (Mac, Linux, Windows) with or without Docker, with or without active Ollama daemons, and with or without cloud API keys. The system must degrade gracefully without crashing.
3. **Artifact Safety:** Evaluator browsers must never execute untrusted user/AI code; all generated HTML/CSS must be sandboxed.

### 1.4 Scope Choices (Included vs. Excluded)
* **Included in Scope:**
  * Full-stack application: FastAPI modular backend + React 19 / TypeScript / Vite frontend.
  * Ingestion and hybrid vector/lexical retrieval of 8 curated Lenny's Podcast transcripts (735 overlapping chunks).
  * Flexible multi-provider LLM abstraction: Ollama (Local mandatory), Anthropic Claude, OpenAI, and Offline Grounded Engine.
  * Claude-style Artifact Viewer for Markdown essays and sandboxed HTML/CSS widgets.
  * Dedicated Ship 30 for 30 content skill (~1,250 words, 1-3-1 hook, 5-part structure).
  * Dual-engine persistence: PostgreSQL with pgvector support, auto-falling back to SQLite.
  * Session isolation, conversation history, message citation drill-downs, and export capabilities.
* **Intentionally Excluded & Why:**
  * Multi-tenant authentication / OAuth: Excluded to eliminate evaluator onboarding friction. Sessions are tracked via isolated session IDs.
  * Web scraping of YouTube video streams at runtime: Excluded to prevent network flakiness, IP rate limits, and fragile external dependencies; replaced with a deterministic, local curated transcript repository.

---

## 2. User Flows & Interaction Architecture

### Flow 1: Grounded Growth Question & Citation Drill-down
1. User enters a query (e.g., *"How does Casey Winters think about growth loops vs funnels?"*).
2. The agent retrieves the top relevant transcript chunks via hybrid retrieval and scores relevance.
3. The response is synthesized and displayed in Markdown with guest attributions.
4. Interactive citation pills appear below the response (e.g., `[1] Casey Winters — Growth loops vs funnels (00:14:22)`).
5. User clicks a citation to inspect the verbatim excerpt quote, similarity score, and YouTube source link.

### Flow 2: Insufficient Evidence Handling
1. User asks an out-of-domain query (e.g., *"How do I bake a chocolate soufflé in Paris?"*).
2. The retrieval service analyzes vocabulary coverage and cosine similarity, determining evidence is $< 0.15$.
3. The system transparently replies: *"The available Lenny's Podcast transcripts do not establish the answer to this question..."* and suggests supported topics.

### Flow 3: Dedicated Ship 30 for 30 Essay Generation
1. User clicks the *"✍️ Ship 30 Essay"* button in the top bar or on any message.
2. User provides a topic (e.g., *"The LNO Framework for Product Leaders"*) and optional custom hook.
3. The Ship 30 skill synthesizes an atomic essay (~1,250 words) adhering to the 1-3-1 cadence and 5-part framework.
4. The essay is saved as a Markdown artifact and automatically opened in the Artifact Viewer.

### Flow 4: Sandboxed Artifact Viewing & Export
1. Assistant generates an interactive HTML widget or Markdown report.
2. The Artifact Viewer slides open alongside the chat.
3. If HTML: rendered inside a sandboxed iframe (`sandbox="allow-popups"` with CSP meta tags blocking scripts and external origins).
4. User toggles between "Preview" and "Source Code".
5. User clicks "Export" to download the file directly (`.html` or `.md`).

---

## 3. Risks & Trade-offs

| Risk Category | Potential Failure Mode | Implemented Mitigation |
| :--- | :--- | :--- |
| **Hallucination** | LLM inventing quotes or attributing false frameworks to guests | Grounding system prompt, strict transcript evidence injection, and vocabulary coverage gating. |
| **Local LLM Latency** | Ollama local inference timeouts or daemon unavailability | 2-second fast connection timeout with automatic fallback notice to Offline Grounded Engine. |
| **Host Setup Friction** | Evaluator lacking PostgreSQL or Docker | Resilient dual-engine database session manager: connects to PostgreSQL if available, otherwise runs SQLite. |
| **Artifact XSS / Injection** | Generated HTML hijacking application DOM or stealing cookies | Zero-privilege sandboxed iframe, CSP meta headers, server-side stripping of `<script>` and `on*` handlers. |
| **Context Leaks** | Chat sessions bleeding conversation history across tabs | Strict session isolation in database queries (`session_id` foreign keys and filters). |

---

## 4. Acceptance Criteria & Verification Matrix

* [x] **AC-1:** Backend runs on FastAPI with OpenAPI docs at `/docs` and health check at `/health`.
* [x] **AC-2:** Ollama integration verified; actionable error message shown when daemon/model is offline.
* [x] **AC-3:** Cloud LLM (Anthropic Claude / OpenAI) integrated with environment variable configuration.
* [x] **AC-4:** Knowledge base ingested with 8 episodes (735 chunks) and hybrid search functioning.
* [x] **AC-5:** Session isolation verified with automated test suite (`backend/tests/test_sessions.py`).
* [x] **AC-6:** Ship 30 for 30 skill generates formatted essay and stores it as an artifact.
* [x] **AC-7:** Artifact Viewer isolates untrusted HTML inside sandboxed iframe with CSP headers.
* [x] **AC-8:** Automated test suite passes with 100% green status across 12 tests.
