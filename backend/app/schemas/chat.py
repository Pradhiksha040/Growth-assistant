"""
Pydantic schemas for Chat Messages and Grounded Retrieval.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class CitationItem(BaseModel):
    transcript_id: str = Field(..., description="Episode slug id")
    title: str = Field(..., description="Episode title")
    guest: str = Field(..., description="Guest speaker name")
    youtube_url: Optional[str] = Field(None, description="Direct URL to episode")
    timestamp_str: Optional[str] = Field(None, description="Timestamp in episode (e.g. 00:14:22)")
    excerpt: str = Field(..., description="Verbatim ground-truth excerpt")
    relevance_score: Optional[float] = Field(None, description="Similarity or relevance score")

class MessageCreate(BaseModel):
    role: str = Field(..., max_length=50, description="'user', 'assistant', or 'system'")
    content: str = Field(..., min_length=1, max_length=50000)

class MessageResponse(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    citations: List[CitationItem] = []
    model_used: Optional[str] = None
    latency_ms: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ChatRequest(BaseModel):
    session_id: Optional[str] = Field(None, max_length=100, description="Existing session id or null for new session")
    message: str = Field(..., min_length=1, max_length=10000, description="User prompt or question")
    provider: Optional[str] = Field(None, max_length=50, description="Override active provider ('ollama', 'anthropic', 'openai', 'offline')")
    model: Optional[str] = Field(None, max_length=100, description="Override model name")

class ChatResponse(BaseModel):
    session_id: str
    message: MessageResponse
    suggested_followups: List[str] = []
    evidence_sufficient: bool = True
