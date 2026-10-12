import type {
  Session,
  Message,
  Artifact,
  ProvidersResponse,
  TranscriptMetadata,
  Ship30Response,
  HealthStatus
} from '../types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errorDetail = `Request failed with status ${res.status}`;
    try {
      const errorJson = await res.json();
      errorDetail = errorJson.detail || errorJson.message || errorDetail;
    } catch {
      // ignore
    }
    throw new Error(errorDetail);
  }
  return res.json();
}

export const api = {
  // Health & Readiness
  async getHealth(): Promise<HealthStatus> {
    const res = await fetch(`${API_BASE}/health`);
    return handleResponse<HealthStatus>(res);
  },

  // Sessions
  async listSessions(): Promise<Session[]> {
    const res = await fetch(`${API_BASE}/api/v1/sessions`);
    const data = await handleResponse<{ sessions: Session[]; total: number }>(res);
    return data.sessions;
  },

  async createSession(title?: string): Promise<Session> {
    const res = await fetch(`${API_BASE}/api/v1/sessions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: title || 'New Conversation' })
    });
    return handleResponse<Session>(res);
  },

  async updateSessionTitle(sessionId: string, title: string): Promise<Session> {
    const res = await fetch(`${API_BASE}/api/v1/sessions/${sessionId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title })
    });
    return handleResponse<Session>(res);
  },

  async deleteSession(sessionId: string): Promise<void> {
    const res = await fetch(`${API_BASE}/api/v1/sessions/${sessionId}`, {
      method: 'DELETE'
    });
    if (!res.ok && res.status !== 204) {
      throw new Error(`Failed to delete session: ${res.status}`);
    }
  },

  async getSessionMessages(sessionId: string): Promise<Message[]> {
    const res = await fetch(`${API_BASE}/api/v1/sessions/${sessionId}/messages`);
    return handleResponse<Message[]>(res);
  },

  // Chat
  async sendMessage(params: {
    sessionId?: string;
    message: string;
    provider?: string;
    model?: string;
  }): Promise<{
    session_id: string;
    message: Message;
    suggested_followups: string[];
    evidence_sufficient: boolean;
  }> {
    const res = await fetch(`${API_BASE}/api/v1/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: params.sessionId,
        message: params.message,
        provider: params.provider,
        model: params.model
      })
    });
    return handleResponse(res);
  },

  // Providers
  async listProviders(): Promise<ProvidersResponse> {
    const res = await fetch(`${API_BASE}/api/v1/providers`);
    return handleResponse<ProvidersResponse>(res);
  },

  async selectProvider(provider: string, model?: string): Promise<{
    status: string;
    active_provider: string;
    active_model: string;
    is_available: boolean;
    message: string;
    available_models: string[];
  }> {
    const res = await fetch(`${API_BASE}/api/v1/providers/select`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ provider, model })
    });
    return handleResponse(res);
  },

  // Transcripts & Ingestion
  async listTranscripts(): Promise<TranscriptMetadata[]> {
    const res = await fetch(`${API_BASE}/api/v1/transcripts`);
    return handleResponse<TranscriptMetadata[]>(res);
  },

  async triggerIngest(): Promise<{
    status: string;
    episodes_ingested: number;
    chunks_created: number;
    message: string;
  }> {
    const res = await fetch(`${API_BASE}/api/v1/ingest`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ source: 'local' })
    });
    return handleResponse(res);
  },

  // Ship 30 for 30
  async generateShip30(sessionId: string, topic: string, customHook?: string): Promise<Ship30Response> {
    const res = await fetch(`${API_BASE}/api/v1/ship30/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        topic,
        custom_hook: customHook,
        target_word_count: 1250
      })
    });
    return handleResponse<Ship30Response>(res);
  },

  // Artifacts
  async listArtifacts(sessionId?: string): Promise<Artifact[]> {
    const url = sessionId
      ? `${API_BASE}/api/v1/artifacts?session_id=${encodeURIComponent(sessionId)}`
      : `${API_BASE}/api/v1/artifacts`;
    const res = await fetch(url);
    const data = await handleResponse<{ artifacts: Artifact[]; total: number }>(res);
    return data.artifacts;
  },

  async getArtifact(artifactId: string): Promise<Artifact> {
    const res = await fetch(`${API_BASE}/api/v1/artifacts/${artifactId}`);
    return handleResponse<Artifact>(res);
  },

  getArtifactExportUrl(artifactId: string): string {
    return `${API_BASE}/api/v1/artifacts/${artifactId}/export`;
  }
};
