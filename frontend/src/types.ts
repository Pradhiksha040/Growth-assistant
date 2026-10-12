export interface CitationItem {
  transcript_id: string;
  title: string;
  guest: string;
  youtube_url?: string | null;
  timestamp_str?: string | null;
  excerpt: string;
  relevance_score?: number | null;
}

export interface Message {
  id: string;
  session_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  citations: CitationItem[];
  model_used?: string | null;
  latency_ms?: number | null;
  created_at: string;
}

export interface Session {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count?: number;
  metadata_json?: string;
}

export interface Artifact {
  id: string;
  session_id: string;
  message_id?: string | null;
  type: 'markdown' | 'html';
  title: string;
  content: string;
  created_at: string;
  updated_at: string;
}

export interface ProviderInfo {
  name: string;
  display_name: string;
  is_active: boolean;
  is_available: boolean;
  status_message: string;
  active_model: string;
  available_models: string[];
  is_local: boolean;
  requires_key: boolean;
  has_key: boolean;
}

export interface ProvidersResponse {
  active_provider: string;
  active_model: string;
  providers: ProviderInfo[];
}

export interface TranscriptMetadata {
  id: string;
  guest: string;
  title: string;
  youtube_url?: string | null;
  video_id?: string | null;
  publish_date?: string | null;
  duration?: string | null;
  description?: string | null;
  chunk_count: number;
}

export interface Ship30Response {
  title: string;
  essay_markdown: string;
  word_count: number;
  citations: CitationItem[];
  evidence_sufficient: boolean;
  artifact?: Artifact | null;
}

export interface HealthStatus {
  status: string;
  app: string;
  version: string;
  environment: string;
  database: {
    status: string;
    backend: string;
    is_fallback: boolean;
    target_pg_configured: boolean;
    pg_connection_error?: string | null;
  };
  active_provider: string;
}
