"""
Main entry point for The Lenny Growth Assistant FastAPI Application.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.db.session import init_db, SessionLocal
from backend.app.db.models import TranscriptChunkModel
from backend.app.services.retrieval_service import retrieval_service
from backend.app.api.v1.router import api_v1_router
from backend.app.api.v1.health import router as root_health_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle startup and shutdown hooks."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION} ({settings.ENVIRONMENT})...")
    
    # 1. Initialize DB schema (PostgreSQL or SQLite fallback)
    try:
        init_db()
    except Exception as e:
        logger.error(f"Error during schema initialization: {e}")
        
    # 2. Check if transcripts need initial ingestion
    try:
        db = SessionLocal()
        chunk_count = db.query(TranscriptChunkModel).count()
        if chunk_count == 0:
            logger.info("Knowledge base is empty. Running automatic seed ingestion of curated Lenny's Podcast transcripts...")
            res = retrieval_service.ingest_local_transcripts(db)
            logger.info(f"Automatic seed ingestion completed: {res['message']}")
        else:
            logger.info(f"Knowledge base already contains {chunk_count} indexed chunks. Rebuilding in-memory search index...")
            retrieval_service.rebuild_search_index(db)
        db.close()
    except Exception as e:
        logger.warning(f"Could not complete initial transcript indexing during startup: {e}")

    yield
    
    logger.info(f"Shutting down {settings.APP_NAME}...")

app = FastAPI(
    title=settings.APP_NAME,
    description="Full-stack AI Conversational Copilot for Product Managers and Growth Teams, grounded in genuine transcripts from Lenny's Podcast.",
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# Secure CORS Configuration
is_wildcard_cors = "*" in settings.CORS_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=not is_wildcard_cors,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Request Timing & Logging Middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}s"
    return response

# Exception Handlers
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    content = {
        "detail": "An unexpected server error occurred. Please consult backend logs."
    }
    if settings.DEBUG:
        content["error"] = str(exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=content
    )

# Include root health and v1 routers
app.include_router(root_health_router)
app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)

@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online",
        "docs_url": "/docs",
        "api_v1": settings.API_V1_PREFIX
    }
