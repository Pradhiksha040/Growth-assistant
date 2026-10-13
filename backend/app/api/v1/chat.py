"""
Chat endpoint for conversational assistant with transcript grounding.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.db.session import get_db
from backend.app.schemas.chat import ChatRequest, ChatResponse
from backend.app.services.agent_service import agent_service

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("", response_model=ChatResponse)
async def send_chat_message(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Sends a question or follow-up prompt to The Lenny Growth Assistant.
    Retrieves grounded evidence from Lenny's transcripts and returns an authoritative answer with citations.
    """
    try:
        response = await agent_service.process_chat(request, db)
        return response
    except Exception as e:
        logger.error(f"Chat processing error: {e}", exc_info=True)
        detail = f"Chat processing failed: {str(e)}" if settings.DEBUG else "Chat processing encountered an unexpected internal error."
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )
