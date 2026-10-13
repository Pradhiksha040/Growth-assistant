"""
Pydantic schemas for Transcripts and Knowledge Base Ingestion.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class TranscriptMetadata(BaseModel):
    id: str
    guest: str
    title: str
    youtube_url: Optional[str] = None
    video_id: Optional[str] = None
    publish_date: Optional[str] = None
    duration: Optional[str] = None
    description: Optional[str] = None
    chunk_count: int = 0

class IngestRequest(BaseModel):
    source: Optional[str] = Field("local", max_length=50, description="'local' folder or 'github'")
    max_episodes: Optional[int] = Field(20, ge=1, le=100, description="Max episodes to ingest from remote")

class IngestResponse(BaseModel):
    status: str
    episodes_ingested: int
    chunks_created: int
    message: str
    errors: List[str] = []

class KnowledgeStatusResponse(BaseModel):
    total_episodes: int
    total_chunks: int
    episodes: List[TranscriptMetadata]
