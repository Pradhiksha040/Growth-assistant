# Design System & UI/UX Documentation
## The Lenny Growth Assistant
**Author:** Forward Deployed Engineering Team  
**Date:** October 12, 2026

---

## 1. UI/UX Principles & Aesthetic Philosophy

1. **Information Density with Extreme Clarity:** Product managers and growth operators parse dense strategic data. The interface prioritizes clean typographic hierarchy, generous micro-spacing, and clear grouping rather than bloated white space.
2. **First-Class Grounding Visibility:** Every claim made by the assistant must wear its provenance proudly. Citations are not hidden at the end of an obscure link; they are interactive, prominent pills showing guest, episode title, timestamp, and verbatim excerpt.
3. **Contextual Co-Presence (The Split-Pane Metaphor):** Following the paradigm established by modern AI workspaces (like Claude Artifacts), strategic deliverables (essays, reports, widgets) live side-by-side with the conversation stream, avoiding context loss caused by modal takeovers or page navigation.
4. **Resilience & State Transparency:** The user always knows whether the local Ollama model, cloud provider, or offline engine is active, what model is running, and the operational latency.

---

## 2. Visual Palette & Typographic System

### 2.1 Color Palette
* **Canvas Background (`--bg-app`):** `#080c14` (Deep obsidian slate)
* **Sidebar Canvas (`--bg-sidebar`):** `#0d121f` (Midnight slate with 1px border)
* **Card & Bubble Surface (`--bg-card`):** `#131a2b` (Deep indigo tinted slate)
* **Primary Accent Gradient:** `linear-gradient(135deg, #6366f1 0%, #a855f7 100%)` (Indigo to Violet)
* **Grounded Citation Highlight:** `#10b981` (Emerald green, signaling trusted verified evidence)
* **Interactive HTML Tag:** `#06b6d4` (Cyan / Sky blue)
* **Security & Isolation Tag:** `#38bdf8` / `#10b981`

### 2.2 Typography
* **Primary Font:** `Inter` (Google Fonts), optimized for UI legibility at small sizes.
* **Monospace Code Font:** `JetBrains Mono` (Google Fonts), for code snippets, model names, and timestamps.
* **Weights:** Regular (400) for body text; Medium (500) for labels; Semi-bold (600) for titles and buttons; Bold (700/800) for headers and guest tags.

---

## 3. Information Architecture & Key Layout Views

```
+---------------------------------------------------------------------------------------------------+
|  SIDEBAR (290px)            |  CHAT AREA (Flexible)                  |  ARTIFACT VIEWER (520px)    |
|                             |                                        |                             |
|  [🎙️ Lenny Growth]         |  [☰] Current Session Title             |  [Markdown / HTML Badge]    |
|  [+ New Conversation]       |  [Provider Status Badge] [✍️ Ship 30]   |  Title: Growth Loops vs...  |
|  [Search conversations...]  |                                        |  [Preview | Source] [Export]|
|                             |  ------------------------------------  |  -------------------------  |
|  Recent Chats:              |  User: How does Casey Winters...       |  <!DOCTYPE html>            |
|  💬 Casey Winters Loops ✏️🗑️ |                                        |  <div class="growth-card">  |
|  💬 Elena Verna PLG         |  Assistant: In his episode...          |    <h3>Acquisition Loop</h3>|
|  💬 Shreyas Doshi LNO       |  [1] Casey Winters (00:14:22)          |  </div>                     |
|                             |  [2] Brian Balfour (00:31:05)          |                             |
|  -------------------------  |  ------------------------------------  |  -------------------------  |
|  📚 8 Episodes / 735 Chunks |  [Composer: Ask about growth loops...] |  🔒 Sandboxed Iframe (CSP)  |
|  ⚙️ Ollama (llama3.2)       |  [↑ Send]                              |                             |
+---------------------------------------------------------------------------------------------------+
```

---

## 4. Key Interaction States

### 4.1 Empty State
* Illustrated with a floating mic badge and clear mission statement.
* Features 4 prominent starter cards covering core podcast themes (Growth Loops, LNO Framework, PLG to PLS, Growth Teams).
* Clicking any card immediately starts the conversation with zero typing.

### 4.2 Loading & Streaming State
* Composer send button morphs into a smooth circular CSS spinner.
* Assistant message row displays a rhythmic 3-dot pulse animation with helper text:
  *"Retrieving podcast transcripts & synthesizing grounded insights..."*
* Input is preserved and error banners display clear retry buttons if network fails.

### 4.3 Citation Exploration
* Citations appear as compact green pills beneath assistant answers.
* Clicking any pill toggles an accordion card revealing:
  * Guest name and full episode title.
  * Verbatim excerpt text enclosed in a blockquote with left border.
  * Exact podcast timestamp.
  * Calculated relevance match percentage.
  * Direct clickable link to the YouTube recording.

### 4.4 Artifact Viewer States
* **Markdown Mode:** Rendered through custom `MarkdownRenderer` with styled headings, blockquotes, bullet points, and code syntax blocks.
* **HTML Mode:** Rendered inside a zero-privilege sandboxed iframe. Script execution is strictly blocked, navigation is constrained, and Content Security Policy meta tags prevent cross-origin exfiltration.
* **Source Mode:** Allows copying raw HTML/Markdown code or inspecting structure.
* **Export Action:** Triggers native file download with content disposition headers (`.html` or `.md`).

---

## 5. Responsive Behavior

* **Desktop ($\ge 1200\text{px}$):** Full 3-column layout (Sidebar, Chat Area, Artifact Viewer side-by-side).
* **Tablet ($900\text{px} - 1199\text{px}$):** Sidebar collapses or stays fixed; Artifact Viewer slides over chat or splits 50/50.
* **Mobile ($< 900\text{px}$):**
  * Sidebar is a slide-in drawer toggled by the hamburger button (`☰`).
  * Artifact Viewer opens as a full-screen accessible modal panel.
  * Composer and citation cards optimize padding for touch targets ($\ge 44\text{px}$).

---

## 6. Accessibility & Contrast

* **Color Contrast:** All text meets or exceeds WCAG 2.1 AA standards (minimum contrast ratio of 4.5:1 against dark backgrounds).
* **Keyboard Navigation:** 
  * `Enter` submits composer; `Shift + Enter` inserts line breaks.
  * All interactive buttons, modals, and tabs include explicit `aria-label`, `role`, and focus rings.
* **Screen Reader Semantic Tags:** Uses semantic HTML5 elements (`<aside>`, `<main>`, `<header>`, `<footer>`, `<nav>`, `<blockquote>`).
