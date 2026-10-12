-- The Lenny Growth Assistant - PostgreSQL Database Schema
-- Compatible with PostgreSQL 15+, Supabase, Railway, and Neon

-- 1. Enable extensions if available
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. Sessions table
CREATE TABLE IF NOT EXISTS sessions (
    id VARCHAR(64) PRIMARY KEY,
    title VARCHAR(255) NOT NULL DEFAULT 'New Conversation',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    metadata_json TEXT DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_sessions_updated_at ON sessions(updated_at DESC);

-- 3. Messages table
CREATE TABLE IF NOT EXISTS messages (
    id VARCHAR(64) PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    role VARCHAR(32) NOT NULL,
    content TEXT NOT NULL,
    citations_json TEXT DEFAULT '[]',
    model_used VARCHAR(128),
    latency_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_messages_session_id ON messages(session_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at ASC);

-- 4. Transcripts table (Episodes)
CREATE TABLE IF NOT EXISTS transcripts (
    id VARCHAR(128) PRIMARY KEY,
    guest VARCHAR(255) NOT NULL,
    title VARCHAR(500) NOT NULL,
    youtube_url VARCHAR(500),
    video_id VARCHAR(64),
    publish_date VARCHAR(64),
    duration VARCHAR(64),
    description TEXT,
    source_file VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_transcripts_guest ON transcripts(guest);

-- 5. Transcript Chunks table
CREATE TABLE IF NOT EXISTS transcript_chunks (
    id VARCHAR(128) PRIMARY KEY,
    transcript_id VARCHAR(128) NOT NULL REFERENCES transcripts(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    speaker VARCHAR(255),
    timestamp_str VARCHAR(32),
    content TEXT NOT NULL,
    token_count INTEGER DEFAULT 0,
    embedding_json TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chunks_transcript_id ON transcript_chunks(transcript_id);

-- 6. Artifacts table (Markdown & Sandboxed HTML)
CREATE TABLE IF NOT EXISTS artifacts (
    id VARCHAR(64) PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    message_id VARCHAR(64),
    type VARCHAR(32) NOT NULL, -- 'markdown' or 'html'
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_artifacts_session_id ON artifacts(session_id);
