import { useState, useRef, useEffect } from 'react';
import type { Message, ProviderInfo, CitationItem, Artifact } from '../types';
import { MarkdownRenderer } from './MarkdownRenderer';

interface ChatAreaProps {
  sessionTitle: string;
  messages: Message[];
  isLoading: boolean;
  onSendMessage: (text: string) => void;
  onOpenShip30: (initialTopic?: string) => void;
  onOpenProviders: () => void;
  activeProvider: ProviderInfo | null;
  onOpenSidebar: () => void;
  artifacts: Artifact[];
  onSelectArtifact: (artifact: Artifact) => void;
  isArtifactViewerOpen: boolean;
  onToggleArtifactViewer: () => void;
}

export const ChatArea: React.FC<ChatAreaProps> = ({
  sessionTitle,
  messages,
  isLoading,
  onSendMessage,
  onOpenShip30,
  onOpenProviders,
  activeProvider,
  onOpenSidebar,
  artifacts,
  onSelectArtifact,
  isArtifactViewerOpen,
  onToggleArtifactViewer
}) => {
  const [inputText, setInputText] = useState('');
  const [expandedCitationIdx, setExpandedCitationIdx] = useState<string | null>(null);
  const [copiedMsgId, setCopiedMsgId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  // Auto-resize textarea
  const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputText(e.target.value);
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 180)}px`;
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSend = () => {
    if (!inputText.trim() || isLoading) return;
    const msg = inputText.trim();
    setInputText('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
    onSendMessage(msg);
  };

  const handleCopyMessage = (msg: Message) => {
    navigator.clipboard.writeText(msg.content);
    setCopiedMsgId(msg.id);
    setTimeout(() => setCopiedMsgId(null), 2000);
  };

  const toggleCitation = (key: string) => {
    setExpandedCitationIdx(expandedCitationIdx === key ? null : key);
  };

  const starterPrompts = [
    {
      title: 'Loops vs. Funnels',
      prompt: 'How do Casey Winters and Brian Balfour explain growth loops versus traditional marketing funnels?',
      guest: 'Casey Winters & Brian Balfour'
    },
    {
      title: 'LNO Framework',
      prompt: "What is Shreyas Doshi's LNO framework and how should product leaders categorize Leverage, Neutral, and Overhead tasks?",
      guest: 'Shreyas Doshi'
    },
    {
      title: 'PLG to PLS Transition',
      prompt: 'How does Elena Verna recommend transitioning from Product-Led Growth (PLG) to Product-Led Sales (PLS)?',
      guest: 'Elena Verna'
    },
    {
      title: 'Structuring Growth Teams',
      prompt: 'What are the most common mistakes when structuring a first growth team according to Adam Fishman?',
      guest: 'Adam Fishman'
    }
  ];

  return (
    <div className="chat-area">
      {/* Top Navigation Bar */}
      <header className="chat-topbar">
        <div className="topbar-left">
          <button
            type="button"
            className="mobile-hamburger-btn"
            onClick={onOpenSidebar}
            aria-label="Open sidebar"
          >
            ☰
          </button>
          <div className="session-info">
            <h2 className="current-session-title">{sessionTitle}</h2>
          </div>
        </div>

        <div className="topbar-right">
          {/* Active provider pill */}
          <button
            type="button"
            className="provider-badge-btn"
            onClick={onOpenProviders}
            title="Inspect active LLM provider"
          >
            <span
              className={`provider-dot ${
                activeProvider?.is_available ? 'dot-green' : 'dot-red'
              }`}
            />
            <span className="provider-label">
              {activeProvider?.display_name || 'Provider'}
            </span>
            <span className="provider-model-tag">
              ({activeProvider?.active_model || 'default'})
            </span>
          </button>

          {/* Ship 30 action button */}
          <button
            type="button"
            id="ship30-quick-btn"
            className="topbar-action-btn ship30-btn"
            onClick={() => onOpenShip30()}
            title="Generate Ship 30 for 30 atomic essay from current context"
          >
            ✍️ Ship 30 Essay
          </button>

          {/* Artifact viewer toggle button */}
          {artifacts.length > 0 && (
            <button
              type="button"
              className={`topbar-action-btn artifact-toggle-btn ${
                isArtifactViewerOpen ? 'active' : ''
              }`}
              onClick={() => {
                if (!isArtifactViewerOpen && artifacts.length > 0) {
                  onSelectArtifact(artifacts[0]);
                }
                onToggleArtifactViewer();
              }}
              title="Toggle Artifact Viewer"
            >
              📄 Artifacts ({artifacts.length})
            </button>
          )}
        </div>
      </header>

      {/* Messages Stream */}
      <div className="messages-stream">
        {messages.length === 0 ? (
          <div className="empty-state">
            <div className="empty-hero-icon">🎙️</div>
            <h1 className="empty-title">The Lenny Growth Assistant</h1>
            <p className="empty-subtitle">
              An elite conversational AI copilot for product managers and growth teams,
              grounded strictly in genuine transcripts from Lenny’s Podcast.
            </p>

            <div className="empty-prompts-grid">
              {starterPrompts.map((p, idx) => (
                <div
                  key={idx}
                  className="starter-prompt-card"
                  onClick={() => onSendMessage(p.prompt)}
                >
                  <div className="prompt-card-header">
                    <span className="prompt-title">{p.title}</span>
                    <span className="prompt-guest">{p.guest}</span>
                  </div>
                  <p className="prompt-text">"{p.prompt}"</p>
                  <span className="prompt-action">Ask Lenny Assistant →</span>
                </div>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg) => {
            const isUser = msg.role === 'user';

            return (
              <div
                key={msg.id}
                className={`message-row ${isUser ? 'user-row' : 'assistant-row'}`}
              >
                <div className={`message-avatar ${isUser ? 'user-avatar' : 'asst-avatar'}`}>
                  {isUser ? '👤' : '🎙️'}
                </div>

                <div className="message-content-container">
                  {/* Assistant meta header */}
                  {!isUser && (
                    <div className="assistant-meta-header">
                      <span className="assistant-name">Lenny Assistant</span>
                      {msg.model_used && (
                        <span className="model-used-badge">{msg.model_used}</span>
                      )}
                      {msg.latency_ms && (
                        <span className="latency-badge">{msg.latency_ms}ms</span>
                      )}
                    </div>
                  )}

                  {/* Message body */}
                  <div className={`message-bubble ${isUser ? 'user-bubble' : 'asst-bubble'}`}>
                    {isUser ? (
                      <p className="user-message-text">{msg.content}</p>
                    ) : (
                      <MarkdownRenderer content={msg.content} />
                    )}
                  </div>

                  {/* Citations section */}
                  {!isUser && msg.citations && msg.citations.length > 0 && (
                    <div className="citations-container">
                      <div className="citations-header">
                        <span className="citations-title">
                          🔍 Grounded Podcast Sources ({msg.citations.length}):
                        </span>
                      </div>
                      <div className="citations-pills-list">
                        {msg.citations.map((cite: CitationItem, cIdx: number) => {
                          const citeKey = `${msg.id}_cite_${cIdx}`;
                          const isExpanded = expandedCitationIdx === citeKey;

                          return (
                            <div key={citeKey} className="citation-wrapper">
                              <button
                                type="button"
                                className={`citation-pill-btn ${isExpanded ? 'expanded' : ''}`}
                                onClick={() => toggleCitation(citeKey)}
                              >
                                <span className="citation-num">[{cIdx + 1}]</span>
                                <span className="citation-guest">{cite.guest}</span>
                                <span className="citation-ep-title">— {cite.title}</span>
                                {cite.timestamp_str && (
                                  <span className="citation-ts">({cite.timestamp_str})</span>
                                )}
                              </button>

                              {isExpanded && (
                                <div className="citation-detail-card">
                                  <div className="citation-detail-header">
                                    <strong>{cite.guest}</strong> in <em>{cite.title}</em>
                                    {cite.youtube_url && (
                                      <a
                                        href={cite.youtube_url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="cite-yt-link"
                                      >
                                        ▶ Watch on YouTube
                                      </a>
                                    )}
                                  </div>
                                  <blockquote className="citation-quote">
                                    "{cite.excerpt}"
                                  </blockquote>
                                  {cite.relevance_score && (
                                    <div className="relevance-score-tag">
                                      Relevance Match: {(cite.relevance_score * 100).toFixed(1)}%
                                    </div>
                                  )}
                                </div>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  )}

                  {/* Actions bar */}
                  {!isUser && (
                    <div className="message-actions-bar">
                      <button
                        type="button"
                        className="msg-action-btn"
                        onClick={() => handleCopyMessage(msg)}
                        title="Copy answer"
                      >
                        {copiedMsgId === msg.id ? '✓ Copied' : '📋 Copy'}
                      </button>
                      <button
                        type="button"
                        className="msg-action-btn"
                        onClick={() => onOpenShip30(msg.content.slice(0, 100))}
                        title="Convert into Ship 30 for 30 atomic essay"
                      >
                        ✍️ Generate Ship 30 Essay
                      </button>
                    </div>
                  )}
                </div>
              </div>
            );
          })
        )}

        {/* Loading Indicator */}
        {isLoading && (
          <div className="message-row assistant-row loading-row">
            <div className="message-avatar asst-avatar">🎙️</div>
            <div className="message-content-container">
              <div className="loading-bubble">
                <div className="loading-dots">
                  <span />
                  <span />
                  <span />
                </div>
                <span className="loading-text">
                  Retrieving podcast transcripts & synthesizing grounded insights...
                </span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Message Composer */}
      <footer className="composer-container">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="composer-form"
        >
          <textarea
            ref={textareaRef}
            id="chat-composer-textarea"
            value={inputText}
            onChange={handleTextChange}
            onKeyDown={handleKeyDown}
            placeholder="Ask about growth loops, PM prioritization, retention, or onboarding... (Enter to send, Shift+Enter for new line)"
            rows={1}
            disabled={isLoading}
            className="composer-textarea"
          />

          <button
            type="submit"
            id="send-message-btn"
            disabled={!inputText.trim() || isLoading}
            className="composer-send-btn"
            aria-label="Send message"
          >
            {isLoading ? (
              <span className="btn-spinner" />
            ) : (
              <span className="send-arrow">↑</span>
            )}
          </button>
        </form>

        <div className="composer-footer-note">
          <span>Grounded strictly in Lenny’s Podcast transcripts • Zero hallucination standard</span>
        </div>
      </footer>
    </div>
  );
};
