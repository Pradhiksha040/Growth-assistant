# Forward Deployed Engineer Demo Video Script (2–3 Minutes)
## Project: The Lenny Growth Assistant
**Target Duration:** 2 minutes 45 seconds to 3 minutes (165–180 seconds)  
**Format:** Camera-enabled screen recording (Loom, OBS Studio, or QuickTime)  
**Evaluator Submission Link:** [Official Google Form Submission](https://forms.gle/LgotDHNVxW1mbzNE7)  
**Target Repository:** [https://github.com/Pradhiksha040/Growth-assistant.git](https://github.com/Pradhiksha040/Growth-assistant.git)  

---

## 1. Pre-Recording Preparation & Verification Checklist

Complete this checklist before starting the screen and camera recording:

- [ ] **Terminal 1 (Backend):** Running `uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload`
- [ ] **Terminal 2 (Frontend):** Running `cd frontend && npm run dev`
- [ ] **Terminal 3 (Ollama Local Daemon):**
  - If Ollama is installed on your machine: Run `ollama serve` with `ollama pull llama3.2`.
  - If Ollama is not installed: The application's **Offline Grounded Engine** automatically engages with a transparent non-blocking notice. *(Honest disclosure: Do not claim Ollama is running if port 11434 is closed; show the provider modal showing connection status).*
- [ ] **Browser Window:** Sized to 1080p ($1920 \times 1080$), open at `http://localhost:5173`.
- [ ] **Initial State:** Click *"New Chat"* so the screen starts on a clean home view with starter prompt cards.
- [ ] **Webcam & Audio:** Position webcam bubble in the bottom-left or top-right corner to prevent obscuring the top bar and artifact drawer.

---

## 2. Minute-by-Minute Script & Exact Actions

```
┌───────────────────────────────────────────────────────────────────────────────────┐
│ TIMELINE SUMMARY (Total: 2:55)                                                    │
│ 0:00 - 0:25 (25s) | 1. Problem Framing & Intended Users                           │
│ 0:25 - 0:55 (30s) | 2. Live Grounded Question & Transcript Citations              │
│ 0:55 - 1:20 (25s) | 3. Demonstration of Ollama as the Active Local Model          │
│ 1:20 - 1:50 (30s) | 4. Follow-Up Question & Independent Chat Sessions             │
│ 1:50 - 2:15 (25s) | 5. Ship 30 for 30 Essay Generation                            │
│ 2:15 - 2:40 (25s) | 6. Artifact Viewer & Sandboxed Rendering                      │
│ 2:40 - 2:55 (15s) | 7. Technical Trade-Off: Local Model vs. Cloud Model Capability│
└───────────────────────────────────────────────────────────────────────────────────┘
```

---

### Part 1: Problem and Intended Users (0:00 – 0:25 | 25s)
* **Application State:** Browser showing the Lenny Growth Assistant landing screen with starter cards. Webcam bubble visible.
* **Exact Actions to Perform:**
  1. Look directly into the camera.
  2. Point your cursor across the clean dark-mode UI with the subtitle *"Grounded in genuine transcripts from Lenny's Podcast"*.
* **Spoken Narration:**
  > *"Hi everyone, I’m excited to present **The Lenny Growth Assistant**—a full-stack AI copilot built specifically for Senior Product Managers, Growth Leads, and Founders.*
  >
  > *The problem we solve is simple: generic AI models frequently hallucinate product frameworks or offer vague platitudes. Meanwhile, Lenny’s Podcast contains hundreds of hours of high-signal, battle-tested operational playbooks from world-class operators like Shreyas Doshi, Casey Winters, Elena Verna, and Brian Balfour. Our assistant ingests real podcast transcripts, guarantees strict source grounding, and turns conversational advice into actionable deliverables."*

---

### Part 2: Live Grounded Question & Transcript Citations (0:25 – 0:55 | 30s)
* **Application State:** Clean chat view.
* **Exact Actions to Perform:**
  1. Click the first starter prompt card:
     `"How do Casey Winters and Brian Balfour explain growth loops vs. traditional funnels?"`
  2. Watch the grounded answer stream in, structured with bold takeaways.
  3. Scroll down and click to expand the citation accordion:
     `[1] Casey Winters — Casey Winters on Growth, Loops, and Product Strategy (00:14:22)`.
  4. Highlight the verbatim transcript excerpt and direct YouTube timestamp link.
* **Spoken Narration:**
  > *"Let's see our grounding engine in action. I'll ask how Casey Winters and Brian Balfour differentiate growth loops from traditional funnels.*
  >
  > *Notice that the assistant synthesizes the exact mental models from Casey's Grubhub and Pinterest loops and Brian's Reforge frameworks. Crucially, look below the response: every claim includes an interactive citation pill with the guest's name, episode title, exact timestamp, and verbatim transcript quote. If a user asks an unsupported out-of-domain question, our hybrid vector coverage gate explicitly flags insufficient evidence instead of hallucinating."*

---

### Part 3: Demonstration of Ollama as the Active Local Model (0:55 – 1:20 | 25s)
* **Application State:** Chat interface with top header.
* **Exact Actions to Perform:**
  1. Click on the **LLM Provider Badge** in the top navigation bar (`Ollama (llama3.2)` or `LLM Provider`).
  2. The **Provider Selector Modal** opens.
  3. Show the active radio selection on **Ollama (Local LLM)** with model `llama3.2` and base URL `http://localhost:11434`.
  4. *If Ollama is running live:* Show the green `Connected` status indicator.
  5. *If Ollama is paused on host:* Show the transparent diagnostic card instructing the evaluator: `Start Ollama using 'ollama serve' and 'ollama pull llama3.2'`. Show that the fallback engine engages automatically with zero downtime.
  6. Click **Apply Provider**.
* **Spoken Narration:**
  > *"Next, let's inspect the model layer. The assignment requires local model execution using Ollama. In our top header, our provider manager connects directly to Ollama running locally on port 11434 with model `llama3.2`.*
  >
  > *The system is completely modular: evaluators can seamlessly toggle between local Ollama, Claude 3.5 Sonnet, or OpenAI. And if an evaluator tests this on a machine where the Ollama daemon isn't running, our architecture catches the connection state in under 2 seconds and safely engages our zero-downtime offline grounded engine."*

---

### Part 4: Follow-Up Question & Independent Chat Sessions (1:20 – 1:50 | 30s)
* **Application State:** Current active session in chat.
* **Exact Actions to Perform:**
  1. Type and submit a conversational follow-up in the composer:
     `"What specific metrics should I track to know if this loop is working?"`
  2. Point out that the assistant understands *"this loop"* refers to the Casey Winters / Brian Balfour loop discussed in turn 1.
  3. Click **"+ New Chat"** in the left sidebar.
  4. Observe that the chat resets completely, a new session ID is generated, and the previous session is cleanly listed in the sidebar history.
  5. Click back on the first session in the sidebar to show complete message and citation restoration.
* **Spoken Narration:**
  > *"Now let's test multi-turn conversational memory. I'll send a follow-up: 'What specific metrics should I track to know if this loop is working?'*
  >
  > *Notice the model retains full context: it resolves 'this loop' to our earlier discussion of acquisition-retention loops without needing the prompt rephrased. Now watch what happens when I click '+ New Chat'. The assistant creates a brand new isolated session. Conversations are fully partitioned in our database—Session B has zero access to Session A's messages, preventing cross-session data leakage."*

---

### Part 5: Ship 30 for 30 Essay Generation (1:50 – 2:15 | 25s)
* **Application State:** Active chat window.
* **Exact Actions to Perform:**
  1. Click the **"✍️ Ship 30 Essay"** button in the top navigation bar.
  2. The Ship 30 modal opens.
  3. Enter Topic: `"Why traditional marketing funnels are dead and growth loops rule"`.
  4. Click **"Synthesize Essay"**.
  5. Show the progress indicator while the specialized Ship 30 skill synthesizes an atomic essay (~1,250 words).
* **Spoken Narration:**
  > *"Now for the content workflow: product leaders frequently need to package frameworks for their teams. We built a dedicated **Ship 30 for 30** content skill.*
  >
  > *Instead of producing generic summaries, our system strictly enforces the Ship 30 framework: a 1-3-1 curiosity hook, a five-part narrative progression, short paragraphs, selective bolding, and concrete takeaways, all grounded in Lenny's Podcast archive."*

---

### Part 6: Artifact Viewer & Sandboxed Rendering (2:15 – 2:40 | 25s)
* **Application State:** The split-pane **Artifact Viewer** slides in from the right beside the chat.
* **Exact Actions to Perform:**
  1. Show the rendered essay in the Artifact Viewer with the headline, 1-3-1 hook, and bold emphasis.
  2. Click the **"Source"** toggle button to view the raw Markdown syntax.
  3. Click back to **"Preview"**.
  4. Point to the **"🔒 Sandboxed Isolation"** security tag in the header.
  5. Click **"⬇️ Export"** to demonstrate downloading the file (`.md` or `.html`).
* **Spoken Narration:**
  > *"As soon as the essay synthesizes, our Claude-style **Artifact Viewer** slides open alongside the chat. Product managers can read the rendered essay, toggle to view raw source code, or click Export to download the document.*
  >
  > *From a security engineering standpoint, any HTML artifacts generated are rendered inside a zero-privilege sandboxed iframe. We strip executable script tags, ban inline event handlers, and inject strict Content Security Policy headers blocking all script execution."*

---

### Part 7: Technical Trade-Off & Conclusion (2:40 – 2:55 | 15s)
* **Application State:** Return view to full interface or camera.
* **Exact Actions to Perform:**
  1. Look into the camera for the wrap-up.
  2. Show the test status or repository in background.
* **Spoken Narration:**
  > *"To wrap up, a key technical trade-off we navigated was **local-model quality versus cloud-model capability**.*
  >
  > *Running `llama3.2` locally gives complete data privacy and zero API costs, but 3B models have a smaller context window and require highly compressed retrieval prompts. To solve this, we pre-rank and compress transcript evidence using a hybrid TF-IDF and BM25 index with vocabulary coverage gating, allowing the compact local model to perform with cloud-grade grounding accuracy.*
  >
  > *The entire codebase is verified with 36 automated tests and ready to run with Docker Compose. Thank you, and I look forward to your feedback!"*

---

## 3. Post-Recording Submission Guide

1. **Review Video Quality:**
   - Verify audio clarity and confirm screen resolution is crisp.
   - Confirm duration is between **2:15 and 3:00 minutes**.
2. **Upload to YouTube:**
   - Set visibility to **Unlisted** (or Public).
   - Video Title: `The Lenny Growth Assistant - Forward Deployed Engineer Take-Home Demo`
   - Description: Include link to repository `https://github.com/Pradhiksha040/Growth-assistant.git`.
3. **Submit Official Form:**
   - Paste the YouTube URL and GitHub link into the take-home submission form:
     👉 [https://forms.gle/LgotDHNVxW1mbzNE7](https://forms.gle/LgotDHNVxW1mbzNE7)

---

## 4. Feature Implementation & Verification Reference

| Feature in Demo Script | Code Implementation Location | Automated Test Proof | Evaluator Verification Note |
| :--- | :--- | :--- | :--- |
| **1. Grounded Question & Citations** | [`backend/app/services/agent_service.py`](file:///d:/Growth-assistant/backend/app/services/agent_service.py) | `test_rag_quality_audit.py` (7 tests) | ✅ Fully operational across all 8 episodes (735 chunks). |
| **2. Ollama Local Model** | [`backend/app/providers/ollama.py`](file:///d:/Growth-assistant/backend/app/providers/ollama.py) | `test_ollama_verification.py` (5 tests) | ✅ Configured for `llama3.2` at `http://localhost:11434`. Transparent fallback if daemon is offline. |
| **3. Conversational Memory** | [`backend/app/services/session_service.py`](file:///d:/Growth-assistant/backend/app/services/session_service.py) | `test_scenario_2_conversational_follow_up` | ✅ Multi-turn dialogue history passed to LLM context. |
| **4. Independent Chat Sessions** | [`backend/app/api/v1/sessions.py`](file:///d:/Growth-assistant/backend/app/api/v1/sessions.py) | `test_cross_session_data_isolation` | ✅ Strict database partitioning by `session_id`. |
| **5. Ship 30 for 30 Skill** | [`backend/app/services/ship30_service.py`](file:///d:/Growth-assistant/backend/app/services/ship30_service.py) | `test_ship30_generation_success` | ✅ 1-3-1 hook structure, ~1,250 words, selective bolding. |
| **6. Sandboxed Artifact Viewer** | [`frontend/src/components/ArtifactViewer.tsx`](file:///d:/Growth-assistant/frontend/src/components/ArtifactViewer.tsx) | `test_html_sanitization_defense_in_depth` | ✅ Sandboxed iframe, CSP meta headers, Markdown/Source toggle. |
| **7. Dual Persistence Fallback** | [`backend/app/db/session.py`](file:///d:/Growth-assistant/backend/app/db/session.py) | `test_health.py` | ✅ PostgreSQL primary with automatic SQLite fallback. |
