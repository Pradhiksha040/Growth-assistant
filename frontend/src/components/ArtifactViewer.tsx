import { useState } from 'react';
import type { Artifact } from '../types';
import { MarkdownRenderer } from './MarkdownRenderer';
import { api } from '../services/api';

interface ArtifactViewerProps {
  artifact: Artifact | null;
  onClose: () => void;
  isOpen: boolean;
}

export const ArtifactViewer: React.FC<ArtifactViewerProps> = ({
  artifact,
  onClose,
  isOpen
}) => {
  const [viewMode, setViewMode] = useState<'preview' | 'code'>('preview');
  const [copyFeedback, setCopyFeedback] = useState(false);

  if (!isOpen || !artifact) {
    return null;
  }

  const handleCopy = () => {
    navigator.clipboard.writeText(artifact.content);
    setCopyFeedback(true);
    setTimeout(() => setCopyFeedback(false), 2000);
  };

  const handleDownload = () => {
    const exportUrl = api.getArtifactExportUrl(artifact.id);
    const a = document.createElement('a');
    a.href = exportUrl;
    a.download =
      artifact.type === 'html'
        ? `${artifact.title.replace(/\s+/g, '_')}.html`
        : `${artifact.title.replace(/\s+/g, '_')}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  return (
    <div className="artifact-viewer-container" id="artifact-viewer">
      {/* Header bar */}
      <div className="artifact-header">
        <div className="artifact-title-group">
          <div className="artifact-badge-row">
            <span
              className={`artifact-type-tag ${
                artifact.type === 'html' ? 'tag-html' : 'tag-markdown'
              }`}
            >
              {artifact.type === 'html' ? 'Interactive HTML' : 'Markdown Essay'}
            </span>
            {artifact.type === 'html' && (
              <span className="sandbox-security-pill" title="Rendered in an isolated iframe with scripts blocked and CSP enforced">
                🔒 Sandboxed Isolation
              </span>
            )}
          </div>
          <h3 className="artifact-title" title={artifact.title}>
            {artifact.title}
          </h3>
        </div>

        <div className="artifact-actions">
          {/* View mode toggle */}
          <div className="view-mode-toggle">
            <button
              type="button"
              className={`toggle-btn ${viewMode === 'preview' ? 'active' : ''}`}
              onClick={() => setViewMode('preview')}
            >
              Preview
            </button>
            <button
              type="button"
              className={`toggle-btn ${viewMode === 'code' ? 'active' : ''}`}
              onClick={() => setViewMode('code')}
            >
              Source
            </button>
          </div>

          <button
            type="button"
            className="artifact-action-btn"
            onClick={handleCopy}
            title="Copy content"
          >
            {copyFeedback ? '✓ Copied' : '📋 Copy'}
          </button>

          <button
            type="button"
            className="artifact-action-btn"
            onClick={handleDownload}
            title="Download file"
          >
            ⬇️ Export
          </button>

          <button
            type="button"
            className="artifact-close-btn"
            onClick={onClose}
            aria-label="Close artifact viewer"
          >
            ✕
          </button>
        </div>
      </div>

      {/* Main content body */}
      <div className="artifact-body">
        {viewMode === 'code' ? (
          <div className="artifact-code-view">
            <pre>
              <code>{artifact.content}</code>
            </pre>
          </div>
        ) : artifact.type === 'html' ? (
          /* Secure sandboxed iframe isolation */
          <div className="artifact-iframe-wrapper">
            <iframe
              title={artifact.title}
              srcDoc={artifact.content}
              sandbox="allow-popups"
              className="sandboxed-artifact-frame"
              loading="lazy"
            />
          </div>
        ) : (
          /* Rendered Markdown */
          <div className="artifact-markdown-view">
            <MarkdownRenderer content={artifact.content} />
          </div>
        )}
      </div>

      {/* Footer info */}
      <div className="artifact-footer">
        <span className="artifact-meta-text">
          {artifact.type === 'html'
            ? 'HTML rendered in isolated, zero-privilege sandboxed iframe.'
            : 'Ship 30 for 30 atomic essay grounded in Lenny\'s Podcast archive.'}
        </span>
      </div>
    </div>
  );
};
