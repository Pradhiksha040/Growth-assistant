"""
Artifact management and export endpoints.
Supports creation, retrieval, and download of Markdown and sandboxed HTML artifacts.
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.artifact import ArtifactCreate, ArtifactResponse, ArtifactListResponse
from backend.app.services.artifact_service import artifact_service

router = APIRouter(prefix="/artifacts", tags=["Artifacts"])

@router.get("", response_model=ArtifactListResponse)
def list_artifacts(session_id: Optional[str] = Query(None), db: Session = Depends(get_db)):
    """Lists artifacts, optionally filtered by session ID."""
    artifacts = artifact_service.list_artifacts(db, session_id)
    return ArtifactListResponse(
        artifacts=[ArtifactResponse.model_validate(a) for a in artifacts],
        total=len(artifacts)
    )

@router.post("", response_model=ArtifactResponse, status_code=status.HTTP_201_CREATED)
def create_artifact(artifact_in: ArtifactCreate, db: Session = Depends(get_db)):
    """Creates a new artifact with HTML isolation and security sanitization."""
    try:
        created = artifact_service.create_artifact(db, artifact_in)
        return created
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create artifact: {str(e)}")

@router.get("/{artifact_id}", response_model=ArtifactResponse)
def get_artifact(artifact_id: str, db: Session = Depends(get_db)):
    """Retrieves artifact by ID."""
    artifact = artifact_service.get_artifact(db, artifact_id)
    if not artifact:
        raise HTTPException(status_code=404, detail=f"Artifact '{artifact_id}' not found.")
    return artifact

@router.get("/{artifact_id}/export")
def export_artifact(artifact_id: str, db: Session = Depends(get_db)):
    """Exports artifact content as a downloadable file with correct headers."""
    artifact = artifact_service.get_artifact(db, artifact_id)
    if not artifact:
        raise HTTPException(status_code=404, detail=f"Artifact '{artifact_id}' not found.")
        
    content, media_type, filename = artifact_service.export_artifact_content(artifact)
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
