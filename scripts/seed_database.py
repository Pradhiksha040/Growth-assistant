"""
CLI script to initialize database and ingest Lenny's Podcast transcripts.
Can be run on fresh environments: python -m scripts.seed_database
"""
import sys
import os

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.db.session import init_db, SessionLocal, get_db_status
from backend.app.services.retrieval_service import retrieval_service
from backend.app.core.logging import logger

def main():
    logger.info("Initializing database schema...")
    init_db()
    
    status = get_db_status()
    logger.info(f"Database status: {status['backend']} (connected: {status['status'] == 'connected'})")
    
    db = SessionLocal()
    try:
        logger.info("Ingesting transcripts from data/transcripts/...")
        res = retrieval_service.ingest_local_transcripts(db)
        logger.info(f"Ingestion result: {res['message']}")
        if res["errors"]:
            for err in res["errors"]:
                logger.error(f"Ingestion warning: {err}")
    finally:
        db.close()
        
    logger.info("Database seeding complete!")

if __name__ == "__main__":
    main()
