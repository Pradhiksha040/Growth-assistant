"""
SQLAlchemy models for PostgreSQL and SQLite persistence.
Persists chat sessions, messages with citations, knowledge transcripts/chunks, and artifacts.
"""
from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, Float
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

def get_utc_now():
    return datetime.now(timezone.utc)

class SessionModel(Base):
    __tablename__ = "sessions"
    
    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False, default="New Conversation")
    created_at = Column(DateTime, default=get_utc_now, nullable=False)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now, nullable=False)
    metadata_json = Column(Text, nullable=True, default="{}")
    
    # Relationships
    messages = relationship("MessageModel", back_populates="session", cascade="all, delete-orphan", order_by="MessageModel.created_at")
    artifacts = relationship("ArtifactModel", back_populates="session", cascade="all, delete-orphan", order_by="ArtifactModel.created_at")

class MessageModel(Base):
    __tablename__ = "messages"
    
    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(64), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(32), nullable=False) # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    citations_json = Column(Text, nullable=True, default="[]")
    model_used = Column(String(128), nullable=True)
    latency_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=get_utc_now, nullable=False)
    
    session = relationship("SessionModel", back_populates="messages")

class TranscriptModel(Base):
    __tablename__ = "transcripts"
    
    id = Column(String(128), primary_key=True) # slug identifier, e.g. 'adam-fishman'
    guest = Column(String(255), nullable=False)
    title = Column(String(500), nullable=False)
    youtube_url = Column(String(500), nullable=True)
    video_id = Column(String(64), nullable=True)
    publish_date = Column(String(64), nullable=True)
    duration = Column(String(64), nullable=True)
    description = Column(Text, nullable=True)
    source_file = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=get_utc_now, nullable=False)
    
    chunks = relationship("TranscriptChunkModel", back_populates="transcript", cascade="all, delete-orphan")

class TranscriptChunkModel(Base):
    __tablename__ = "transcript_chunks"
    
    id = Column(String(128), primary_key=True) # slug_chunk_0
    transcript_id = Column(String(128), ForeignKey("transcripts.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    speaker = Column(String(255), nullable=True)
    timestamp_str = Column(String(32), nullable=True)
    content = Column(Text, nullable=False)
    token_count = Column(Integer, default=0)
    embedding_json = Column(Text, nullable=True) # JSON serialized embedding vector
    created_at = Column(DateTime, default=get_utc_now, nullable=False)
    
    transcript = relationship("TranscriptModel", back_populates="chunks")

class ArtifactModel(Base):
    __tablename__ = "artifacts"
    
    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(64), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    message_id = Column(String(64), nullable=True)
    type = Column(String(32), nullable=False) # 'markdown' or 'html'
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=get_utc_now, nullable=False)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now, nullable=False)
    
    session = relationship("SessionModel", back_populates="artifacts")
