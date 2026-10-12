import { useState } from 'react';
import type { Session, HealthStatus, ProviderInfo } from '../types';

interface SidebarProps {
  sessions: Session[];
  activeSessionId: string | null;
  onSelectSession: (id: string) => void;
  onNewChat: () => void;
  onDeleteSession: (id: string) => void;
  onRenameSession: (id: string, newTitle: string) => void;
  health: HealthStatus | null;
  activeProvider: ProviderInfo | null;
  onOpenTranscripts: () => void;
  onOpenProviders: () => void;
  isOpen: boolean;
  onClose: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  sessions,
  activeSessionId,
  onSelectSession,
  onNewChat,
  onDeleteSession,
  onRenameSession,
  health,
  activeProvider,
  onOpenTranscripts,
  onOpenProviders,
  isOpen,
  onClose
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [editingSessionId, setEditingSessionId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState('');

  const filteredSessions = sessions.filter((s) =>
    s.title.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const startEditing = (s: Session, e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingSessionId(s.id);
    setEditTitle(s.title);
  };

  const saveEditing = (id: string, e: React.FormEvent) => {
    e.preventDefault();
    if (editTitle.trim()) {
      onRenameSession(id, editTitle.trim());
    }
    setEditingSessionId(null);
  };

  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && <div className="sidebar-backdrop" onClick={onClose} />}

      <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
        {/* Brand header */}
        <div className="sidebar-header">
          <div className="brand">
            <div className="brand-icon">🎙️</div>
            <div className="brand-text">
              <span className="brand-title">Lenny Growth</span>
              <span className="brand-subtitle">Product & Growth Copilot</span>
            </div>
          </div>
          <button
            type="button"
            className="mobile-close-btn"
            onClick={onClose}
            aria-label="Close menu"
          >
            ✕
          </button>
        </div>

        {/* New chat action */}
        <div className="sidebar-actions">
          <button
            type="button"
            id="new-chat-btn"
            className="new-chat-btn"
            onClick={() => {
              onNewChat();
              onClose();
            }}
          >
            <span className="plus-icon">+</span>
            <span>New Conversation</span>
          </button>
        </div>

        {/* Search filter */}
        <div className="search-box">
          <input
            type="text"
            placeholder="Search conversations..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
            aria-label="Search conversations"
          />
        </div>

        {/* Sessions list */}
        <div className="sessions-list">
          <div className="sessions-header-label">Recent Chats</div>
          {filteredSessions.length === 0 ? (
            <div className="empty-sessions">
              {searchTerm ? 'No matching conversations' : 'No conversations yet'}
            </div>
          ) : (
            filteredSessions.map((s) => {
              const isActive = s.id === activeSessionId;
              const isEditing = s.id === editingSessionId;

              return (
                <div
                  key={s.id}
                  className={`session-item ${isActive ? 'active' : ''}`}
                  onClick={() => {
                    onSelectSession(s.id);
                    onClose();
                  }}
                >
                  <span className="session-icon">💬</span>

                  {isEditing ? (
                    <form
                      onSubmit={(e) => saveEditing(s.id, e)}
                      onClick={(e) => e.stopPropagation()}
                      className="edit-session-form"
                    >
                      <input
                        type="text"
                        value={editTitle}
                        onChange={(e) => setEditTitle(e.target.value)}
                        autoFocus
                        onBlur={() => setEditingSessionId(null)}
                        className="edit-session-input"
                      />
                    </form>
                  ) : (
                    <span className="session-title" title={s.title}>
                      {s.title}
                    </span>
                  )}

                  <div className="session-item-actions">
                    <button
                      type="button"
                      className="item-action-btn"
                      title="Rename"
                      onClick={(e) => startEditing(s, e)}
                    >
                      ✏️
                    </button>
                    <button
                      type="button"
                      className="item-action-btn delete-btn"
                      title="Delete"
                      onClick={(e) => {
                        e.stopPropagation();
                        if (confirm('Delete this conversation?')) {
                          onDeleteSession(s.id);
                        }
                      }}
                    >
                      🗑️
                    </button>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Footer status badges */}
        <div className="sidebar-footer">
          {/* Knowledge base status pill */}
          <button
            type="button"
            className="footer-status-card"
            onClick={onOpenTranscripts}
            title="Inspect Lenny's Podcast transcripts"
          >
            <div className="status-indicator ready" />
            <div className="status-info">
              <span className="status-label">Knowledge Base</span>
              <span className="status-detail">8 Episodes • 735 Chunks</span>
            </div>
            <span className="status-arrow">›</span>
          </button>

          {/* Active provider pill */}
          <button
            type="button"
            className="footer-status-card"
            onClick={onOpenProviders}
            title="Configure LLM model provider"
          >
            <div
              className={`status-indicator ${
                activeProvider?.is_available ? 'ready' : 'offline'
              }`}
            />
            <div className="status-info">
              <span className="status-label">LLM Provider</span>
              <span className="status-detail">
                {activeProvider?.display_name || 'Loading...'}
              </span>
            </div>
            <span className="status-arrow">⚙️</span>
          </button>

          {/* DB Persistence indicator */}
          <div className="persistence-indicator">
            <span className="db-dot" />
            <span className="db-text">
              {health?.database.backend === 'postgresql'
                ? 'PostgreSQL Persistent'
                : 'Resilient SQLite Persistence'}
            </span>
          </div>
        </div>
      </aside>
    </>
  );
};
