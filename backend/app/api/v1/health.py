"""
Health and readiness endpoints.
Provides operational visibility into database connectivity, Ollama status,
and knowledge base indexing state.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.db.session import get_db, get_db_status
from backend.app.db.models import TranscriptModel, TranscriptChunkModel
from backend.app.services.llm_provider import provider_manager
from backend.app.core.config import settings

router = APIRouter(tags=["Health"])

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Liveness probe: verifies basic service health and database availability."""
    db_stat = get_db_status()
    active_key, active_provider = await provider_manager.get_active_provider()
    provider_available, status_msg, _ = await active_provider.check_availability()
    
    return {
        "status": "healthy" if db_stat["status"] == "connected" else "degraded",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": db_stat,
        "active_provider": {
            "key": active_key,
            "available": provider_available,
            "message": status_msg
        }
    }

@router.get("/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """Readiness probe: checks knowledge base indexing and query readiness."""
    db_stat = get_db_status()
    try:
        ep_count = db.query(func.count(TranscriptModel.id)).scalar() or 0
        chunk_count = db.query(func.count(TranscriptChunkModel.id)).scalar() or 0
    except Exception:
        ep_count = 0
        chunk_count = 0

    active_key, active_provider = await provider_manager.get_active_provider()
    provider_available, status_msg, _ = await active_provider.check_availability()
    
    is_ready = (db_stat["status"] == "connected" and chunk_count > 0)
    
    return {
        "ready": is_ready,
        "episodes_indexed": ep_count,
        "chunks_indexed": chunk_count,
        "database": db_stat,
        "active_provider": active_key,
        "provider_ready": provider_available,
        "provider_message": status_msg
    }
