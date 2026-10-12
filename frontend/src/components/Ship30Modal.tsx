import { useState } from 'react';
import { api } from '../services/api';
import type { Artifact } from '../types';

interface Ship30ModalProps {
  isOpen: boolean;
  onClose: () => void;
  sessionId: string | null;
  onEssayGenerated: (artifact: Artifact) => void;
}

export const Ship30Modal: React.FC<Ship30ModalProps> = ({
  isOpen,
  onClose,
  sessionId,
  onEssayGenerated
}) => {
  const [topic, setTopic] = useState('Growth loops vs traditional marketing funnels');
  const [customHook, setCustomHook] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!sessionId) {
      setErrorMsg('Please select or create an active conversation first.');
      return;
    }
    if (!topic.trim()) {
      setErrorMsg('Please enter a topic.');
      return;
    }

    setIsGenerating(true);
    setErrorMsg(null);

    try {
      const res = await api.generateShip30(sessionId, topic.trim(), customHook.trim() || undefined);
      if (res.artifact) {
        onEssayGenerated(res.artifact);
        onClose();
      } else {
        // Insufficient evidence handled cleanly
        setErrorMsg(
          'Insufficient evidence found in Lenny\'s Podcast archive to ground a full 1,250-word essay on this topic. Try topics featuring Casey Winters, Elena Verna, Shreyas Doshi, or Adam Fishman.'
        );
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      setErrorMsg(`Generation failed: ${msg}`);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-container ship30-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-title-group">
            <span className="modal-icon">✍️</span>
            <h2>Ship 30 for 30 Content Skill</h2>
          </div>
          <button type="button" className="modal-close-btn" onClick={onClose}>
            ✕
          </button>
        </div>

        <form onSubmit={handleGenerate}>
          <div className="modal-body">
            <p className="modal-desc">
              Generate a high-converting, ~1,250-word atomic essay strictly grounded in genuine Lenny's Podcast transcripts.
            </p>

            <div className="ship30-framework-pill-grid">
              <span className="ship30-pill">⚡ 1-3-1 Hook Cadence</span>
              <span className="ship30-pill">📖 5-Part Narrative Arc</span>
              <span className="ship30-pill">🎯 ~1,250 Words Target</span>
              <span className="ship30-pill">🔍 Strict Transcript Grounding</span>
            </div>

            {errorMsg && <div className="modal-alert error">⚠️ {errorMsg}</div>}

            <div className="form-group">
              <label htmlFor="ship30-topic">Essay Core Topic / Concept:</label>
              <input
                id="ship30-topic"
                type="text"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="e.g. Growth loops vs funnels, The LNO Framework, Product-Led Sales"
                required
                className="modal-input"
              />
            </div>

            <div className="form-group">
              <label htmlFor="ship30-hook">Optional Custom Hook Angle:</label>
              <input
                id="ship30-hook"
                type="text"
                value={customHook}
                onChange={(e) => setCustomHook(e.target.value)}
                placeholder="e.g. Why 90% of SaaS funnels leak cash before activation"
                className="modal-input"
              />
            </div>

            <div className="suggested-topics-box">
              <span className="suggested-title">Popular Lenny's Podcast Topics:</span>
              <div className="suggested-chips">
                <button
                  type="button"
                  className="chip-btn"
                  onClick={() => setTopic('Why traditional marketing funnels are dead and growth loops rule')}
                >
                  Loops vs Funnels (Winters)
                </button>
                <button
                  type="button"
                  className="chip-btn"
                  onClick={() => setTopic('How top PMs master the LNO framework')}
                >
                  LNO Framework (Doshi)
                </button>
                <button
                  type="button"
                  className="chip-btn"
                  onClick={() => setTopic('Transitioning from Product-Led Growth to Product-Led Sales')}
                >
                  PLG to PLS (Verna)
                </button>
                <button
                  type="button"
                  className="chip-btn"
                  onClick={() => setTopic('How to structure and scale your first growth team')}
                >
                  Growth Teams (Fishman)
                </button>
              </div>
            </div>
          </div>

          <div className="modal-footer">
            <button type="button" className="btn-secondary" onClick={onClose} disabled={isGenerating}>
              Cancel
            </button>
            <button type="submit" className="btn-primary" disabled={isGenerating}>
              {isGenerating ? 'Synthesizing Essay (~1,250 words)...' : 'Generate Atomic Essay'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
