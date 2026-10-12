import { useState } from 'react';
import type { ProvidersResponse, ProviderInfo } from '../types';
import { api } from '../services/api';

interface ProviderModalProps {
  isOpen: boolean;
  onClose: () => void;
  providersData: ProvidersResponse | null;
  onProviderChanged: () => void;
}

export const ProviderModal: React.FC<ProviderModalProps> = ({
  isOpen,
  onClose,
  providersData,
  onProviderChanged
}) => {
  const [selectedKey, setSelectedKey] = useState<string>(
    providersData?.active_provider || 'offline'
  );
  const [customModel, setCustomModel] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [statusMsg, setStatusMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  if (!isOpen || !providersData) return null;

  const handleApply = async () => {
    setIsLoading(true);
    setStatusMsg(null);
    try {
      const res = await api.selectProvider(selectedKey, customModel.trim() || undefined);
      setStatusMsg({
        type: res.is_available ? 'success' : 'error',
        text: res.message
      });
      onProviderChanged();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      setStatusMsg({ type: 'error', text: `Failed to switch provider: ${msg}` });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-container" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-title-group">
            <span className="modal-icon">⚙️</span>
            <h2>LLM Provider & Model Selection</h2>
          </div>
          <button type="button" className="modal-close-btn" onClick={onClose}>
            ✕
          </button>
        </div>

        <div className="modal-body">
          <p className="modal-desc">
            Switch between local inference (Ollama), cloud models (Anthropic Claude, OpenAI), or the built-in Offline Grounded Engine.
          </p>

          {statusMsg && (
            <div className={`modal-alert ${statusMsg.type}`}>
              {statusMsg.type === 'success' ? '✓ ' : '⚠️ '}
              {statusMsg.text}
            </div>
          )}

          <div className="provider-cards-grid">
            {providersData.providers.map((p: ProviderInfo) => {
              const isSelected = selectedKey === p.name;
              return (
                <div
                  key={p.name}
                  className={`provider-card ${isSelected ? 'selected' : ''}`}
                  onClick={() => {
                    setSelectedKey(p.name);
                    setCustomModel(p.active_model);
                  }}
                >
                  <div className="provider-card-header">
                    <div className="provider-name-badge">
                      <input
                        type="radio"
                        name="provider_select"
                        checked={isSelected}
                        onChange={() => setSelectedKey(p.name)}
                        className="provider-radio"
                      />
                      <span className="provider-name">{p.display_name}</span>
                    </div>
                    <span
                      className={`provider-status-badge ${
                        p.is_available ? 'available' : 'unavailable'
                      }`}
                    >
                      {p.is_available ? 'Ready' : 'Offline / Missing'}
                    </span>
                  </div>

                  <div className="provider-model-info">
                    <span className="label">Active Model:</span>
                    <span className="value code-val">{p.active_model}</span>
                  </div>

                  <p className="provider-status-msg">{p.status_message}</p>

                  {/* Actionable guidance if Ollama is selected and offline */}
                  {p.name === 'ollama' && !p.is_available && (
                    <div className="ollama-help-box">
                      <div className="help-title">Quick Setup Commands:</div>
                      <div className="help-step">1. Run daemon: <code>ollama serve</code></div>
                      <div className="help-step">2. Pull model: <code>ollama pull {p.active_model}</code></div>
                    </div>
                  )}

                  {/* Cloud provider key status */}
                  {p.requires_key && (
                    <div className="cloud-key-status">
                      {p.has_key ? (
                        <span className="key-ok">✓ API Key Configured in .env</span>
                      ) : (
                        <span className="key-missing">⚠️ Key not found in .env</span>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          <div className="model-override-section">
            <label htmlFor="custom-model-input">Optional Model Override:</label>
            <input
              id="custom-model-input"
              type="text"
              placeholder="e.g. llama3.2, claude-3-5-sonnet-20241022, gpt-4o"
              value={customModel}
              onChange={(e) => setCustomModel(e.target.value)}
              className="custom-model-input"
            />
          </div>
        </div>

        <div className="modal-footer">
          <button type="button" className="btn-secondary" onClick={onClose}>
            Cancel
          </button>
          <button
            type="button"
            className="btn-primary"
            onClick={handleApply}
            disabled={isLoading}
          >
            {isLoading ? 'Connecting...' : 'Apply & Activate Provider'}
          </button>
        </div>
      </div>
    </div>
  );
};
