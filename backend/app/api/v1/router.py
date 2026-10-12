"""
Aggregates all API v1 endpoints into a unified router.
"""
from fastapi import APIRouter

from backend.app.api.v1.health import router as health_router
from backend.app.api.v1.sessions import router as sessions_router
from backend.app.api.v1.chat import router as chat_router
from backend.app.api.v1.providers import router as providers_router
from backend.app.api.v1.ingest import router as ingest_router
from backend.app.api.v1.transcripts import router as transcripts_router
from backend.app.api.v1.ship30 import router as ship30_router
from backend.app.api.v1.artifacts import router as artifacts_router

api_v1_router = APIRouter()

api_v1_router.include_router(health_router)
api_v1_router.include_router(sessions_router)
api_v1_router.include_router(chat_router)
api_v1_router.include_router(providers_router)
api_v1_router.include_router(ingest_router)
api_v1_router.include_router(transcripts_router)
api_v1_router.include_router(ship30_router)
api_v1_router.include_router(artifacts_router)
