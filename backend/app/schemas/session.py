"""
Pydantic schemas for Chat Sessions.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class SessionBase(BaseModel):
    title: str = Field(default="New Conversation", max_length=255)

class SessionCreate(SessionBase):
    pass

class SessionUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)

class SessionResponse(SessionBase):
    id: str
    created_at: datetime
    updated_at: datetime
    metadata_json: Optional[str] = "{}"
    message_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)

class SessionListResponse(BaseModel):
    sessions: List[SessionResponse]
    total: int
