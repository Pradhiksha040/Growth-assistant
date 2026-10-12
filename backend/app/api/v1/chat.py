"""
Chat endpoint for conversational assistant with transcript grounding.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat processing failed: {str(e)}"
        )
