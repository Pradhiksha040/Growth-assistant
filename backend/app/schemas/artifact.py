"""
Pydantic schemas for Artifacts (Markdown & sandboxed HTML).
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

class ArtifactCreate(BaseModel):
    session_id: str
    message_id: Optional[str] = None
    type: str = Field(..., description="'markdown' or 'html'")
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)

class ArtifactResponse(BaseModel):
    id: str
    session_id: str
    message_id: Optional[str] = None
    type: str
    title: str
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ArtifactListResponse(BaseModel):
    artifacts: List[ArtifactResponse]
    total: int
