# The Lenny Growth Assistant — Manual UI Acceptance Test Checklist

This checklist provides an end-to-end verification protocol for evaluators and engineers to validate all functional, visual, security, and architectural requirements of **The Lenny Growth Assistant**.

---

## 1. Quickstart Verification & System Startup

| Step | Action | Expected Behavior | Status |
| :--- | :--- | :--- | :--- |
| **1.1** | Start the Backend: `uvicorn backend.app.main:app --host 0.0.0.0 --port 8000` | Server binds to `http://localhost:8000`. Health endpoint responds at `http://localhost:8000/health`. Logs show database initialization (PostgreSQL or SQLite fallback). | `PASS` |
| **1.2** | Start the Frontend: `cd frontend && npm run dev` | Vite dev server binds to `http://localhost:5173`. UI loads with modern dark aesthetic, Inter/Outfit typography, and glassmorphic cards. | `PASS` |
| **1.3** | Verify Health Status | Navigate to sidebar footer or `http://localhost:8000/health`. Shows database connection status (`ready`), active provider name, and transcript count ($\ge 8$ episodes, $735$ chunks). | `PASS` |

---

## 2. Transcript-Grounded Conversational Copilot

| Step | Action | Expected Behavior | Status |
| :--- | :--- | :--- | :--- |
| **2.1** | Click a Starter Prompt card (e.g. *"Loops vs. Funnels"*) | Input is populated, sent to backend, and response is generated. | `PASS` |
| **2.2** | Inspect Guest Attribution & Citations | Answer explicitly attributes insights to guest (e.g. Casey Winters, Brian Balfour). Citation pills appear beneath message showing `[1] Guest — Title (Timestamp)`. | `PASS` |
| **2.3** | Expand Citation Drawer | Clicking a citation pill unfolds the exact verbatim transcript quote, relevance match percentage, and a direct `▶ Watch on YouTube` link. | `PASS` |
| **2.4** | Message Actions | Hovering/inspecting assistant message displays `📋 Copy`, `🔄 Regenerate`, and `✍️ Generate Ship 30 Essay` action buttons. Clicking Copy provides visual feedback (`✓ Copied`). | `PASS` |
| **2.5** | Clickable Follow-up Chips | Suggested follow-up pill buttons appear below the assistant message. Clicking one immediately populates and dispatches the follow-up question. | `PASS` |

---

## 3. Strict Non-Hallucination & Out-of-Domain Boundaries

| Step | Action | Expected Behavior | Status |
| :--- | :--- | :--- | :--- |
| **3.1** | Submit Out-of-Domain Query: *"What is the metabolic cycle of deep sea vent tubeworms?"* | Assistant does **not** hallucinate or speculate. Responds transparently: *"The available Lenny's Podcast transcripts do not establish the answer to this question..."* and suggests supported topics. | `PASS` |
| **3.2** | Verify Evidence Sufficiency Indicator | Backend response sets `evidence_sufficient: false`. Citations list is empty or minimal without false positives. | `PASS` |

---

## 4. Multi-Provider LLM & Claude Agent SDK Orchestration

| Step | Action | Expected Behavior | Status |
| :--- | :--- | :--- | :--- |
| **4.1** | Open Provider Modal | Click active provider pill in topbar or sidebar footer. Displays Ollama, Anthropic Claude, OpenAI, and Offline Grounded Engine with real-time availability badges. | `PASS` |
| **4.2** | Select Offline Grounded Engine | Switch active provider to Offline Grounded Engine. Chat and Ship 30 generation operate locally and deterministically with zero API keys required. | `PASS` |
| **4.3** | Configure Ollama (Local LLM) | When Ollama is running locally with `llama3.2` or `mistral`, provider indicates green readiness. If offline, actionable installation commands (`ollama run llama3.2`) are displayed. | `PASS` |
| **4.4** | Claude Agent SDK Fallback | When Claude CLI is unauthenticated, agent transparently catches `ResultError: Not logged in`, logs diagnostic, and routes via direct Messages API or Grounded Engine. | `PASS` |

---

## 5. Ship 30 for 30 Content Generation Skill

| Step | Action | Expected Behavior | Status |
| :--- | :--- | :--- | :--- |
| **5.1** | Open Ship 30 Generator | Click `✍️ Ship 30 Essay` in topbar or message actions. Modal opens with topic input and optional custom hook field. | `PASS` |
| **5.2** | Generate Atomic Essay | Submit topic: *"Growth loops vs traditional marketing funnels"*. Generates structured atomic essay meeting: <br>• $\approx 1,250$ words ($\ge 1,000$ verified)<br>• 1-3-1 hook rhythm<br>• 5-part structure (Part I: Hidden Problem, Part II: Core Mechanism, Part III: Guest Evidence, Part IV: 3 Tactics, Part V: High-Agency Checklist). | `PASS` |
| **5.3** | Automated Artifact Creation | Generated essay is automatically saved as an Artifact in the database and displayed in the split-pane viewer. | `PASS` |

---

## 6. Sandboxed Artifact Viewer & Export Security

| Step | Action | Expected Behavior | Status |
| :--- | :--- | :--- | :--- |
| **6.1** | Split-Pane Artifact Viewer | Displays alongside the chat stream (Claude Artifacts UX pattern). Can be opened, closed, and toggled. | `PASS` |
| **6.2** | Preview vs. Code Toggle | "Preview" renders formatted Markdown or interactive HTML. "Source" displays raw syntax code block. | `PASS` |
| **6.3** | Sandboxed HTML Isolation | Interactive HTML widgets render inside `<iframe sandbox="allow-popups">` with Content Security Policy `default-src 'none'`. Script injection and cookie access are blocked. | `PASS` |
| **6.4** | Artifact Export | Clicking `⬇️ Export` downloads the artifact as a clean `.md` or `.html` file via `/api/v1/artifacts/{id}/export`. | `PASS` |

---

## 7. Session Management & Database Persistence

| Step | Action | Expected Behavior | Status |
| :--- | :--- | :--- | :--- |
| **7.1** | Create New Chat | Clicking `+ New Chat` creates a new isolated session and clears the conversation stream. | `PASS` |
| **7.2** | Session Title Autonaming | First user query automatically generates a concise 6-word title for the session in the sidebar. | `PASS` |
| **7.3** | Session Switching | Switching between sidebar session items dynamically loads the correct historical messages and associated artifacts. | `PASS` |
| **7.4** | Session Rename & Delete | Hovering over a session item in the sidebar allows inline renaming (pencil icon) or deletion (trash icon). | `PASS` |
| **7.5** | Persistence Resilience | In PostgreSQL mode, all records persist in PostgreSQL. In SQLite mode, all records persist in `data/lenny_assistant.db`. Survives server restarts. | `PASS` |

---

## 8. Code Quality & Automated Test Validation

| Test Suite | Command | Expected Outcome | Verified Result |
| :--- | :--- | :--- | :--- |
| **Backend Unit & Integration Tests** | `python -m pytest backend/tests -v` | All 18 tests pass | **18 passed in 31.5s** |
| **Frontend Linting** | `cd frontend && npm run lint` | 0 errors, 0 warnings | **0 errors, 0 warnings in 67ms** |
| **Frontend TypeScript & Bundle Build** | `cd frontend && npm run build` | Clean production build | **Built in 1.15s** |
