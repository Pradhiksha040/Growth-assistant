"""
Ship 30 for 30 Content Skill endpoint.
Generates an atomic essay (~1,250 words) from grounded Lenny transcripts.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.ship30 import Ship30Request, Ship30Response
from backend.app.services.ship30_service import ship30_service

router = APIRouter(prefix="/ship30", tags=["Ship 30 for 30"])

@router.post("/generate", response_model=Ship30Response)
async def generate_ship30_essay(request: Ship30Request, db: Session = Depends(get_db)):
    """
    Executes the Ship 30 for 30 content generation skill.
    Retrieves grounded evidence from Lenny's Podcast, applies the Ship 30 framework,
    and returns a structured Markdown essay, storing it as an Artifact.
    """
    try:
        response = await ship30_service.generate_essay(request, db)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ship 30 essay generation failed: {str(e)}"
        )
