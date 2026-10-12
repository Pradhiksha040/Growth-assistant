# Demo Video Script & Evaluator Recording Guide
## The Lenny Growth Assistant
**Video Length Target:** 2 to 3 minutes  
**Format:** Camera-enabled screen recording (Loom, OBS Studio, or QuickTime)  
**Deliverable Link:** [YouTube Upload Guide & Script]

---

## 1. Recording Checklist & Prerequisites

Before starting the video recording:
- [ ] Ensure terminal 1 is running the backend: `uvicorn backend.app.main:app --host 0.0.0.0 --port 8000`
- [ ] Ensure terminal 2 is running the frontend: `cd frontend && npm run dev`
- [ ] Ensure terminal 3 is running Ollama: `ollama serve` (with `llama3.2` pulled)
- [ ] Browser window open at `http://localhost:5173`
- [ ] Webcam enabled in a corner bubble (Loom / OBS) with good lighting and audio
- [ ] Browser window sized to 1080p ($1920 \times 1080$) for crisp text readability

---

## 2. Minute-by-Minute Demo Script

### 0:00 - 0:35 | Introduction & Problem Framing (Face + Screen)
* **Visual:** Speaker webcam full-screen or corner bubble over the Lenny Growth Assistant home interface.
* **Spoken Script:**
  > *"Hi everyone, I'm excited to present **The Lenny Growth Assistant**—a full-stack AI conversational copilot built specifically for product managers and growth leaders.*
  >
  > *The problem we solve is simple: generic AI models often provide vague product platitudes or hallucinate frameworks. But top operators have shared real, battle-tested playbooks on **Lenny's Podcast**. Our assistant ingests real podcast transcripts, enforces strict source grounding, generates atomic Ship 30 for 30 essays, and renders live visual artifacts natively inside the app without compromising security.*
  >
  > *Let's jump straight into the product."*

### 0:35 - 1:15 | Core Conversational Grounding & Citations (Screen Walkthrough)
* **Visual:** Click on one of the starter prompt cards: *"How do Casey Winters and Brian Balfour explain growth loops vs. traditional funnels?"*
* **Action:**
  1. Show the query submitting.
  2. Point to the streaming response citing Casey Winters from Pinterest/Grubhub and Brian Balfour from Reforge.
  3. Expand the interactive citation pill `[1] Casey Winters — Growth loops vs funnels (00:14:22)`.
* **Spoken Script:**
  > *"Here, notice our grounding architecture in action. The assistant answers directly from Casey Winters's and Brian Balfour's transcript chunks. Below the answer, you see interactive citations with exact timestamps, verbatim excerpts, and direct links to YouTube.*
  >
  > *Now, what happens if we ask an out-of-domain question, like 'How do I bake a chocolate cake in Paris?' Let's run it.*
  > *Notice that instead of making up a speculative response, our hybrid vector engine flags that the transcript coverage is insufficient and explicitly refuses to speculate. Zero hallucination is a non-negotiable standard for our deployment."*

### 1:15 - 1:55 | Local Ollama Model & Provider Switching
* **Visual:** Click on the LLM Provider badge in the top bar. Open the Provider Selection Modal.
* **Action:**
  1. Highlight the 4 available providers: Ollama (Local), Anthropic Claude (Cloud), OpenAI (Cloud), and the Offline Grounded Engine.
  2. Show Ollama running locally at `http://localhost:11434` with model `llama3.2`.
  3. Show the setup instructions displayed if Ollama is paused (`ollama serve` and `ollama pull llama3.2`).
* **Spoken Script:**
  > *"Next, let's inspect the model layer. The assignment requires local model execution using Ollama. In our top header, we have an active provider manager. It checks Ollama availability, displays real-time model status, and allows switching to cloud models like Claude 3.5 Sonnet or OpenAI without rewriting any application code.*
  >
  > *If an evaluator runs this on a machine without Ollama or Docker, our zero-downtime offline grounded engine seamlessly engages, ensuring the product is 100% testable out of the box."*

### 1:55 - 2:35 | Ship 30 for 30 Skill & Artifact Viewer
* **Visual:** Click the *"✍️ Ship 30 Essay"* button in the top bar.
* **Action:**
  1. Submit topic: *"Why traditional marketing funnels are dead and growth loops rule"*.
  2. Watch the Ship 30 for 30 skill synthesize a ~1,250-word atomic essay.
  3. Watch the split-pane **Artifact Viewer** slide open alongside the chat.
  4. Toggle between "Preview" and "Source Code".
  5. Click "Export" to demonstrate downloading the `.md` or `.html` file.
* **Spoken Script:**
  > *"Now for the content workflow: product leaders need to communicate frameworks to their teams. We built a dedicated Ship 30 for 30 content skill.*
  >
  > *Notice that it doesn't just write a generic summary. It follows the proven Ship 30 framework: a 1-3-1 curiosity hook, a 5-part narrative progression, short paragraphs, selective bolding, and actionable takeaways.*
  >
  > *Beside our chat, our Artifact Viewer natively renders the result. It supports Markdown and interactive HTML widgets. To prevent XSS vulnerabilities, HTML artifacts are rendered inside a zero-privilege sandboxed iframe with strict Content Security Policy meta headers blocking script execution."*

### 2:35 - 3:00 | Technical Trade-off & Conclusion (Face + Screen)
* **Visual:** Return to webcam + repository view.
* **Spoken Script:**
  > *"One key technical trade-off we navigated was **hybrid retrieval scoring versus local inference latency**. Rather than relying solely on high-dimensional dense neural embeddings that require heavy GPU dependencies on fresh evaluator machines, we built a hybrid semantic-lexical TF-IDF index with concept boosting and vocabulary coverage gating. This provides sub-50ms retrieval, deterministic grounding, and zero cold-start delay on any CPU.*
  >
  > *The complete project is open-source, fully tested with 12 automated pytest suites, and ready to deploy with Docker Compose.*
  > *Thank you, and I look forward to your feedback!"*

---

## 3. Post-Recording Submission Steps

1. Upload the recorded MP4/WebM video to YouTube as **Unlisted** (or Public).
2. Set title: `The Lenny Growth Assistant - Forward Deployed Engineer Demo`.
3. Copy the YouTube video URL.
4. Submit the URL alongside the repository link to the official submission form:
   [https://forms.gle/LgotDHNVxW1mbzNE7](https://forms.gle/LgotDHNVxW1mbzNE7)
