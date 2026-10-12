"""
Database session management with resilient PostgreSQL connection
and seamless SQLite fallback for zero-downtime local operations.
"""
import os
from typing import Generator, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.db.models import Base

_active_engine = None
_active_backend_type = "unknown"
_db_connection_error = None

def create_db_engine():
    global _active_engine, _active_backend_type, _db_connection_error
    
    # 1. Try PostgreSQL if configured
    pg_url = settings.DATABASE_URL
    if pg_url and pg_url.startswith("postgres"):
        try:
            logger.info(f"Attempting connection to PostgreSQL: {pg_url.split('@')[-1] if '@' in pg_url else 'configured url'}")
            test_engine = create_engine(
                pg_url,
                pool_pre_ping=settings.DB_POOL_PRE_PING,
                echo=settings.DB_ECHO,
                connect_args={"connect_timeout": 1}
            )
            # Test connection
            with test_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            _active_engine = test_engine
            _active_backend_type = "postgresql"
            _db_connection_error = None
            logger.info("Successfully connected to PostgreSQL database.")
            return _active_engine
        except Exception as e:
            _db_connection_error = str(e)
            logger.warning(
                f"PostgreSQL connection failed ({e}). "
                "Engaging resilient SQLite fallback persistence to ensure uninterrupted operation."
            )
            
    # 2. Resilient SQLite Fallback
    try:
        os.makedirs(settings.DATA_DIR, exist_ok=True)
        sqlite_engine = create_engine(
            settings.SQLITE_FALLBACK_URL,
            connect_args={"check_same_thread": False},
            echo=settings.DB_ECHO
        )
        with sqlite_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        _active_engine = sqlite_engine
        _active_backend_type = "sqlite_fallback"
        logger.info(f"Database initialized on SQLite fallback: {settings.SQLITE_FALLBACK_URL}")
        return _active_engine
    except Exception as e:
        logger.error(f"Critical error initializing SQLite fallback database: {e}")
        raise e

# Initialize engine and sessionmaker
engine = create_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Create all tables in the active database engine."""
    global engine
    try:
        Base.metadata.create_all(bind=engine)
        logger.info(f"Database schema initialized successfully on {_active_backend_type}.")
    except Exception as e:
        logger.error(f"Failed to initialize database schema: {e}")
        raise e

def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for obtaining a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_status() -> Dict[str, Any]:
    """Inspect active database health, type, and operational status."""
    global engine, _active_backend_type, _db_connection_error
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {
            "status": "connected",
            "backend": _active_backend_type,
            "is_fallback": (_active_backend_type == "sqlite_fallback"),
            "target_pg_configured": bool(settings.DATABASE_URL and settings.DATABASE_URL.startswith("postgres")),
            "pg_connection_error": _db_connection_error,
        }
    except Exception as e:
        return {
            "status": "error",
            "backend": _active_backend_type,
            "error": str(e),
            "is_fallback": (_active_backend_type == "sqlite_fallback")
        }
