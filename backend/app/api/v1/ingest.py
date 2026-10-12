"""
Knowledge base ingestion endpoints.
Triggers loading of local or remote transcripts, chunking, and index refreshing.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.db.session import get_db
from backend.app.db.models import TranscriptModel, TranscriptChunkModel
from backend.app.schemas.transcript import IngestRequest, IngestResponse, KnowledgeStatusResponse, TranscriptMetadata
from backend.app.services.retrieval_service import retrieval_service

router = APIRouter(prefix="/ingest", tags=["Ingestion"])

@router.post("", response_model=IngestResponse)
def run_ingestion(req: IngestRequest, db: Session = Depends(get_db)):
    """
    Ingests transcripts into PostgreSQL/SQLite database and rebuilds the hybrid vector index.
    Supports local transcripts folder.
    """
    try:
        result = retrieval_service.ingest_local_transcripts(db)
        return IngestResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ingestion process failed: {str(e)}"
        )

@router.get("/status", response_model=KnowledgeStatusResponse)
def get_knowledge_status(db: Session = Depends(get_db)):
    """Returns total episode and chunk count with metadata breakdown."""
    episodes = db.query(TranscriptModel).all()
    total_chunks = db.query(func.count(TranscriptChunkModel.id)).scalar() or 0
    
    meta_list = []
    for ep in episodes:
        c_count = db.query(func.count(TranscriptChunkModel.id)).filter(
            TranscriptChunkModel.transcript_id == ep.id
        ).scalar() or 0
        meta_list.append(TranscriptMetadata(
            id=ep.id,
            guest=ep.guest,
            title=ep.title,
            youtube_url=ep.youtube_url,
            video_id=ep.video_id,
            publish_date=ep.publish_date,
            duration=ep.duration,
            description=ep.description,
            chunk_count=c_count
        ))
        
    return KnowledgeStatusResponse(
        total_episodes=len(episodes),
        total_chunks=total_chunks,
        episodes=meta_list
    )
