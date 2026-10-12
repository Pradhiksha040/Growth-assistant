import { useState } from 'react';
import type { TranscriptMetadata } from '../types';
import { api } from '../services/api';

interface TranscriptsModalProps {
  isOpen: boolean;
  onClose: () => void;
  transcripts: TranscriptMetadata[];
  onRefresh: () => void;
}

export const TranscriptsModal: React.FC<TranscriptsModalProps> = ({
  isOpen,
  onClose,
  transcripts,
  onRefresh
}) => {
  const [isReindexing, setIsReindexing] = useState(false);
  const [reindexMsg, setReindexMsg] = useState<string | null>(null);

  if (!isOpen) return null;

  const totalChunks = transcripts.reduce((acc, t) => acc + (t.chunk_count || 0), 0);

  const handleReindex = async () => {
    setIsReindexing(true);
    setReindexMsg(null);
    try {
      const res = await api.triggerIngest();
      setReindexMsg(res.message);
      onRefresh();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      setReindexMsg(`Re-indexing failed: ${msg}`);
    } finally {
      setIsReindexing(false);
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-container transcripts-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-title-group">
            <span className="modal-icon">📚</span>
            <h2>Lenny's Podcast Knowledge Base</h2>
          </div>
          <button type="button" className="modal-close-btn" onClick={onClose}>
            ✕
          </button>
        </div>

        <div className="modal-body">
          <div className="transcripts-stats-banner">
            <div className="stat-card">
              <span className="stat-number">{transcripts.length}</span>
              <span className="stat-label">Episodes Ingested</span>
            </div>
            <div className="stat-card">
              <span className="stat-number">{totalChunks}</span>
              <span className="stat-label">Searchable Chunks</span>
            </div>
            <div className="stat-card">
              <span className="stat-number">100%</span>
              <span className="stat-label">Source Grounded</span>
            </div>
          </div>

          {reindexMsg && <div className="modal-alert success">✓ {reindexMsg}</div>}

          <div className="transcripts-grid">
            {transcripts.map((t) => (
              <div key={t.id} className="transcript-card">
                <div className="transcript-card-header">
                  <div className="transcript-guest-badge">{t.guest}</div>
                  <span className="chunk-pill">{t.chunk_count} chunks</span>
                </div>
                <h4 className="transcript-title">{t.title}</h4>
                {t.description && <p className="transcript-desc">{t.description}</p>}
                <div className="transcript-meta-row">
                  {t.duration && <span className="meta-tag">⏱️ {t.duration}</span>}
                  {t.publish_date && <span className="meta-tag">📅 {t.publish_date}</span>}
                  {t.youtube_url && (
                    <a
                      href={t.youtube_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="youtube-link"
                    >
                      ▶️ YouTube
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="modal-footer">
          <button
            type="button"
            className="btn-secondary"
            onClick={handleReindex}
            disabled={isReindexing}
          >
            {isReindexing ? 'Re-indexing knowledge base...' : '🔄 Re-index Archive'}
          </button>
          <button type="button" className="btn-primary" onClick={onClose}>
            Done
          </button>
        </div>
      </div>
    </div>
  );
};
