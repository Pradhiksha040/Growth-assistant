"""
Session and message persistence endpoints.
Ensures independent conversation sessions and isolation.
"""
from typing import List
import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.db.session import get_db
from backend.app.db.models import SessionModel, MessageModel
from backend.app.schemas.session import SessionCreate, SessionUpdate, SessionResponse, SessionListResponse
from backend.app.schemas.chat import MessageResponse, CitationItem

router = APIRouter(prefix="/sessions", tags=["Sessions"])

@router.get("", response_model=SessionListResponse)
def list_sessions(db: Session = Depends(get_db)):
    """Lists all conversation sessions ordered by most recently updated."""
    sessions = db.query(SessionModel).order_by(SessionModel.updated_at.desc()).all()
    
    res = []
    for s in sessions:
        msg_count = db.query(func.count(MessageModel.id)).filter(MessageModel.session_id == s.id).scalar() or 0
        res.append(SessionResponse(
            id=s.id,
            title=s.title,
            created_at=s.created_at,
            updated_at=s.updated_at,
            metadata_json=s.metadata_json or "{}",
            message_count=msg_count
        ))
        
    return SessionListResponse(sessions=res, total=len(res))

@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(session_in: SessionCreate, db: Session = Depends(get_db)):
    """Creates a new isolated conversation session."""
    session_obj = SessionModel(title=session_in.title)
    db.add(session_obj)
    db.commit()
    db.refresh(session_obj)
    return SessionResponse(
        id=session_obj.id,
        title=session_obj.title,
        created_at=session_obj.created_at,
        updated_at=session_obj.updated_at,
        metadata_json=session_obj.metadata_json or "{}",
        message_count=0
    )

@router.get("/{session_id}", response_model=SessionResponse)
def get_session(session_id: str, db: Session = Depends(get_db)):
    """Retrieves session details by ID."""
    s = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not s:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")
    msg_count = db.query(func.count(MessageModel.id)).filter(MessageModel.session_id == s.id).scalar() or 0
    return SessionResponse(
        id=s.id,
        title=s.title,
        created_at=s.created_at,
        updated_at=s.updated_at,
        metadata_json=s.metadata_json or "{}",
        message_count=msg_count
    )

@router.patch("/{session_id}", response_model=SessionResponse)
def update_session(session_id: str, update_in: SessionUpdate, db: Session = Depends(get_db)):
    """Updates session metadata (e.g. title)."""
    s = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not s:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")
    if update_in.title is not None:
        s.title = update_in.title
    db.commit()
    db.refresh(s)
    msg_count = db.query(func.count(MessageModel.id)).filter(MessageModel.session_id == s.id).scalar() or 0
    return SessionResponse(
        id=s.id,
        title=s.title,
        created_at=s.created_at,
        updated_at=s.updated_at,
        metadata_json=s.metadata_json or "{}",
        message_count=msg_count
    )

@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(session_id: str, db: Session = Depends(get_db)):
    """Deletes a conversation session and all its messages and artifacts."""
    s = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not s:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")
    db.delete(s)
    db.commit()
    return None

@router.get("/{session_id}/messages", response_model=List[MessageResponse])
def get_session_messages(session_id: str, db: Session = Depends(get_db)):
    """Retrieves chronological message history for a session."""
    s = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not s:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")
        
    msgs = db.query(MessageModel).filter(
        MessageModel.session_id == session_id
    ).order_by(MessageModel.created_at.asc()).all()
    
    results = []
    for m in msgs:
        citations = []
        if m.citations_json:
            try:
                raw_cits = json.loads(m.citations_json)
                citations = [CitationItem(**c) for c in raw_cits]
            except Exception:
                citations = []
                
        results.append(MessageResponse(
            id=m.id,
            session_id=m.session_id,
            role=m.role,
            content=m.content,
            citations=citations,
            model_used=m.model_used,
            latency_ms=m.latency_ms,
            created_at=m.created_at
        ))
        
    return results
