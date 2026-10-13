"""
Pydantic schemas for Ship 30 for 30 essay generation skill.
"""
from typing import Optional, List
from pydantic import BaseModel, Field
from backend.app.schemas.chat import CitationItem
from backend.app.schemas.artifact import ArtifactResponse

class Ship30Request(BaseModel):
    session_id: str = Field(..., max_length=100, description="Session ID")
    topic: str = Field(..., min_length=3, max_length=500, description="Topic or question to convert into a Ship 30 for 30 essay")
    custom_hook: Optional[str] = Field(None, max_length=500, description="Optional custom hook angle")
    target_word_count: Optional[int] = Field(1250, ge=100, le=5000, description="Target word count (approx. 1,250 words)")

class Ship30Response(BaseModel):
    title: str
    essay_markdown: str
    word_count: int
    citations: List[CitationItem]
    evidence_sufficient: bool
    artifact: Optional[ArtifactResponse] = None
