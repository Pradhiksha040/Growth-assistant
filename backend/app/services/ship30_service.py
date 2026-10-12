"""
Ship 30 for 30 Content Generation Skill.
Transforms grounded Lenny's Podcast knowledge into high-performing, ~1,250-word atomic essays.
Implements the Ship 30 for 30 writing framework:
- Catchy curiosity hook (The Golden Intersection)
- 1-3-1 sentence cadence
- Descriptive Roman numeral / H2 headers
- Selective bolding for skimmability
- Actionable frameworks and checklists
- Strict transcript evidence grounding
"""
from typing import Dict, Any, List, Optional
import uuid
from sqlalchemy.orm import Session

from backend.app.core.logging import logger
from backend.app.schemas.ship30 import Ship30Request, Ship30Response
from backend.app.schemas.chat import CitationItem
from backend.app.services.retrieval_service import retrieval_service
from backend.app.services.llm_provider import provider_manager
from backend.app.schemas.artifact import ArtifactResponse
from backend.app.db.models import ArtifactModel, MessageModel

SHIP30_SYSTEM_PROMPT = """You are an elite product writer trained in the Ship 30 for 30 framework.
Your task is to turn real insights from Lenny's Podcast transcripts into a masterclass atomic essay.

WRITING RULES:
1. Target Word Count: Aim for approximately 1,200 to 1,300 words.
2. Hook: Open with a punchy 1-sentence hook that subverts conventional wisdom. Follow with a 3-sentence setup, then a 1-sentence punchline (The 1-3-1 rhythm).
3. Narrative Structure:
   - Part I: The Hidden Problem (Why standard playbook fails)
   - Part II: The Core Mechanism (The transcript-grounded framework)
   - Part III: What Top Practitioners Do Differently (Specific guest case studies from the podcast)
   - Part IV: The Step-by-Step Execution Blueprint (3 concrete tactics)
   - Part V: The High-Agency Checklist (Takeaway summary)
4. Skimmability: Use short paragraphs (1-3 sentences max). Use bold emphasis on key insights. Use bullet points for steps.
5. Strict Grounding: Cite the guests, episode titles, and frameworks directly. Do NOT invent quotes or make claims unsupported by the evidence.
6. Output Format: Clean, polished GitHub Markdown with clear H1, H2, and bullet formatting.
"""

class Ship30Service:
    async def generate_essay(self, request: Ship30Request, db: Session) -> Ship30Response:
        logger.info(f"Generating Ship 30 for 30 essay on topic: '{request.topic}' for session: {request.session_id}")
        
        # 1. Retrieve relevant transcript evidence
        chunks, evidence_sufficient = retrieval_service.search(request.topic, db, top_k=7)
        citations = retrieval_service.to_citation_items(chunks)
        
        # 2. Handle insufficient evidence transparently
        if not evidence_sufficient or len(chunks) < 2:
            insufficient_msg = (
                f"# Insufficient Transcript Evidence for Topic: {request.topic}\n\n"
                "The available Lenny's Podcast transcripts do not contain sufficient evidence to ground a full 1,250-word Ship 30 for 30 essay on this topic.\n\n"
                "To uphold the core Forward Deployed Engineering standard of zero hallucination, we do not fabricate claims when source evidence is lacking.\n\n"
                "**Supported Core Topics in Lenny's Archive:**\n"
                "- How to build a high-performing growth team (Adam Fishman)\n"
                "- Four Fits Framework and growth loops vs funnels (Brian Balfour, Casey Winters)\n"
                "- Product-Led Growth and Product-Led Sales (Elena Verna)\n"
                "- Product management craft, LNO framework, high agency (Shreyas Doshi)\n"
                "- Adjacent User Theory and scaling activation (Bangaly Kaba)\n"
                "- Metric trees and experiment roadmaps (Fareed Mosavat)\n"
            )
            return Ship30Response(
                title=f"Insufficient Evidence: {request.topic}",
                essay_markdown=insufficient_msg,
                word_count=len(insufficient_msg.split()),
                citations=citations,
                evidence_sufficient=False,
                artifact=None
            )
            
        # 3. Format grounded evidence for generation
        evidence_blocks = []
        guests_featured = []
        for c in chunks:
            guests_featured.append(c["guest"])
            evidence_blocks.append(
                f"- **{c['guest']}** in *{c['title']}* (Timestamp: {c.get('timestamp_str', 'N/A')}):\n"
                f"  \"{c['content']}\""
            )
        unique_guests = list(dict.fromkeys(guests_featured))
        
        # 4. Generate essay using active provider
        active_key, provider = await provider_manager.get_active_provider()
        
        prompt = (
            f"Write a 1,250-word Ship 30 for 30 essay on: '{request.topic}'.\n"
            f"Grounded exclusively in the following Lenny's Podcast transcripts featuring {', '.join(unique_guests)}:\n\n"
            + "\n\n".join(evidence_blocks)
        )
        
        try:
            essay_text, latency = await provider.generate_response(
                prompt=prompt,
                system_prompt=SHIP30_SYSTEM_PROMPT,
                conversation_history=[],
                context_chunks=chunks
            )
        except Exception as e:
            logger.warning(f"Active provider {active_key} failed for Ship 30 generation ({e}). Falling back to deterministic synthesis.")
            fallback_provider = provider_manager.providers["offline"]
            essay_text, latency = await fallback_provider.generate_response(
                prompt=prompt,
                system_prompt=SHIP30_SYSTEM_PROMPT,
                conversation_history=[],
                context_chunks=chunks
            )

        # Ensure title extracted
        title_line = request.topic.title()
        lines = essay_text.strip().split("\n")
        if lines and lines[0].startswith("# "):
            title_line = lines[0].replace("# ", "").strip()
            
        word_count = len(essay_text.split())
        
        # 5. Persist as an Artifact in database
        artifact_id = str(uuid.uuid4())
        artifact = ArtifactModel(
            id=artifact_id,
            session_id=request.session_id,
            type="markdown",
            title=f"Ship 30 Essay: {title_line[:60]}",
            content=essay_text
        )
        db.add(artifact)
        db.commit()
        db.refresh(artifact)
        
        artifact_res = ArtifactResponse.model_validate(artifact)
        return Ship30Response(
            title=title_line,
            essay_markdown=essay_text,
            word_count=word_count,
            citations=citations,
            evidence_sufficient=True,
            artifact=artifact_res
        )

ship30_service = Ship30Service()
