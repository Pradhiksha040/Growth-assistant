"""
Artifact Management and Security Isolation Service.
Handles Markdown and HTML/CSS artifacts.
Implements strict security boundaries:
- Strips executable script tags, event handlers, and dangerous URIs
- Injects restrictive Content-Security-Policy (CSP) headers into HTML documents
- Prepares documents for rendering in an isolated sandboxed iframe
"""
import re
import uuid
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException

from backend.app.db.models import ArtifactModel
from backend.app.schemas.artifact import ArtifactCreate, ArtifactResponse
from backend.app.core.logging import logger

DANGEROUS_HTML_PATTERNS = [
    re.compile(r"<\s*script[^>]*>.*?<\s*/\s*script\s*>", re.IGNORECASE | re.DOTALL),
    re.compile(r"<\s*iframe[^>]*>.*?<\s*/\s*iframe\s*>", re.IGNORECASE | re.DOTALL),
    re.compile(r"<\s*object[^>]*>.*?<\s*/\s*object\s*>", re.IGNORECASE | re.DOTALL),
    re.compile(r"<\s*embed[^>]*>", re.IGNORECASE),
    re.compile(r"<\s*form[^>]*>.*?<\s*/\s*form\s*>", re.IGNORECASE | re.DOTALL),
    re.compile(r"on\w+\s*=\s*[\"'][^\"']*[\"']", re.IGNORECASE), # onclick, onerror, etc.
    re.compile(r"on\w+\s*=\s*[^>\s]+", re.IGNORECASE),
    re.compile(r"href\s*=\s*[\"']\s*javascript:[^\"']*[\"']", re.IGNORECASE),
    re.compile(r"src\s*=\s*[\"']\s*javascript:[^\"']*[\"']", re.IGNORECASE),
]

SAFE_CSP_META = (
    '<meta http-equiv="Content-Security-Policy" '
    'content="default-src \'none\'; style-src \'unsafe-inline\'; font-src data:; img-src data: https:;">'
)

SANDBOX_CSS_TEMPLATE = """
<style>
  :root {
    --bg-primary: #0f172a;
    --text-primary: #f8fafc;
    --text-secondary: #94a3b8;
    --accent: #3b82f6;
    --card-bg: #1e293b;
    --border: #334155;
  }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    line-height: 1.6;
    color: #1e293b;
    background-color: #ffffff;
    padding: 24px;
    margin: 0;
  }
  @media (prefers-color-scheme: dark) {
    body {
      background-color: #0f172a;
      color: #f1f5f9;
    }
    .card { background-color: #1e293b; border-color: #334155; }
    table th { background-color: #1e293b; }
    table td, table th { border-color: #334155; }
  }
  h1, h2, h3 { font-weight: 700; line-height: 1.3; }
  table { width: 100%; border-collapse: collapse; margin: 16px 0; }
  table th, table td { padding: 10px 14px; border: 1px solid #e2e8f0; text-align: left; }
  table th { background-color: #f8fafc; font-weight: 600; }
  .badge { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; }
  .card { border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; margin: 12px 0; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
</style>
"""

class ArtifactService:
    def sanitize_and_isolate_html(self, raw_html: str, title: str) -> str:
        """
        Enforces defense-in-depth HTML sanitization:
        1. Strips dangerous elements (<script>, <iframe>, <object>, <embed>, <form>)
        2. Strips inline event handlers (onclick, onload, onerror)
        3. Strips javascript: URI references
        4. Injects strict CSP meta tag blocking script execution and external network requests
        5. Wraps in standard HTML boilerplate if missing
        """
        clean_html = raw_html
        for pattern in DANGEROUS_HTML_PATTERNS:
            clean_html = pattern.sub("", clean_html)
            
        # Check if complete document or fragment
        has_html_tag = "<html" in clean_html.lower()
        has_head_tag = "<head" in clean_html.lower()
        
        if has_html_tag and has_head_tag:
            # Inject CSP right after <head>
            clean_html = re.sub(r"(<head[^>]*>)", r"\1\n  " + SAFE_CSP_META, clean_html, flags=re.IGNORECASE)
            return clean_html
        else:
            # Wrap fragment into safe sandbox container
            return (
                "<!DOCTYPE html>\n"
                "<html lang=\"en\">\n"
                "<head>\n"
                "  <meta charset=\"UTF-8\">\n"
                "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n"
                f"  <title>{title}</title>\n"
                f"  {SAFE_CSP_META}\n"
                f"  {SANDBOX_CSS_TEMPLATE}\n"
                "</head>\n"
                "<body>\n"
                f"{clean_html}\n"
                "</body>\n"
                "</html>"
            )

    def create_artifact(self, db: Session, artifact_in: ArtifactCreate) -> ArtifactModel:
        artifact_type = artifact_in.type.lower()
        content = artifact_in.content
        
        if artifact_type == "html":
            content = self.sanitize_and_isolate_html(content, artifact_in.title)
            
        artifact_id = str(uuid.uuid4())
        db_obj = ArtifactModel(
            id=artifact_id,
            session_id=artifact_in.session_id,
            message_id=artifact_in.message_id,
            type=artifact_type,
            title=artifact_in.title,
            content=content
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        logger.info(f"Created artifact '{db_obj.title}' ({db_obj.type}) [id={db_obj.id}]")
        return db_obj

    def get_artifact(self, db: Session, artifact_id: str) -> Optional[ArtifactModel]:
        return db.query(ArtifactModel).filter(ArtifactModel.id == artifact_id).first()

    def list_artifacts(self, db: Session, session_id: Optional[str] = None) -> List[ArtifactModel]:
        query = db.query(ArtifactModel)
        if session_id:
            query = query.filter(ArtifactModel.session_id == session_id)
        return query.order_by(ArtifactModel.created_at.desc()).all()

    def export_artifact_content(self, artifact: ArtifactModel) -> Tuple[str, str, str]:
        """Returns (content_string, media_type, filename)"""
        if artifact.type == "html":
            filename = f"{re.sub(r'[^a-zA-Z0-9_-]', '_', artifact.title)}.html"
            return artifact.content, "text/html", filename
        else:
            filename = f"{re.sub(r'[^a-zA-Z0-9_-]', '_', artifact.title)}.md"
            return artifact.content, "text/markdown", filename

artifact_service = ArtifactService()
