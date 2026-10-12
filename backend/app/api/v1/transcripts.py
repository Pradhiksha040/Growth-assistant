"""
Transcript inspection and search endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.db.models import TranscriptModel, TranscriptChunkModel
from backend.app.schemas.transcript import TranscriptMetadata
from backend.app.services.retrieval_service import retrieval_service

router = APIRouter(prefix="/transcripts", tags=["Transcripts"])

@router.get("", response_model=List[TranscriptMetadata])
def list_transcripts(db: Session = Depends(get_db)):
    """Lists all transcripts currently in the knowledge base."""
    episodes = db.query(TranscriptModel).order_by(TranscriptModel.guest.asc()).all()
    res = []
    for ep in episodes:
        res.append(TranscriptMetadata(
            id=ep.id,
            guest=ep.guest,
            title=ep.title,
            youtube_url=ep.youtube_url,
            video_id=ep.video_id,
            publish_date=ep.publish_date,
            duration=ep.duration,
            description=ep.description,
            chunk_count=len(ep.chunks)
        ))
    return res

@router.get("/search")
def search_transcripts(q: str = Query(..., min_length=2), db: Session = Depends(get_db)):
    """Performs raw hybrid retrieval search against indexed transcript chunks."""
    chunks, sufficient = retrieval_service.search(q, db, top_k=6)
    citations = retrieval_service.to_citation_items(chunks)
    return {
        "query": q,
        "evidence_sufficient": sufficient,
        "results_count": len(chunks),
        "citations": citations
    }
