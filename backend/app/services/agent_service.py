"""
Agent Orchestration Service.
Coordinates RAG retrieval, LLM generation, grounding verification,
automatic artifact extraction, and conversation state persistence.
"""
import re
import uuid
import time
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.db.models import SessionModel, MessageModel, ArtifactModel
from backend.app.schemas.artifact import ArtifactCreate
from backend.app.schemas.chat import ChatRequest, ChatResponse, MessageResponse, CitationItem
from backend.app.services.retrieval_service import retrieval_service
from backend.app.services.llm_provider import provider_manager
from backend.app.services.artifact_service import artifact_service
from backend.app.services.claude_agent import claude_agent_integration

SYSTEM_PROMPT = """You are "The Lenny Growth Assistant", an elite AI copilot for product managers and growth leaders.
Your knowledge is strictly grounded in genuine transcripts from Lenny's Podcast.

CORE OPERATIONAL RULES:
1. Strict Grounding: Answer questions using ONLY the facts, mental models, frameworks, and advice found in the provided transcript evidence.
2. Attribution: Whenever you present a principle or insight, explicitly attribute it to the guest and episode (e.g., "As Adam Fishman explained in his episode on growth teams...").
3. Insufficient Evidence: If the provided transcript excerpts do not contain the answer, you MUST state clearly:
   "The available Lenny's Podcast transcripts do not establish the answer to this question."
   Do NOT speculate, guess, or fabricate external facts.
4. Tone & Style: Be authoritative, structured, and pragmatic. Use bullet points, bold key terms, and concise paragraphs.
5. Actionable Advice: Product managers want frameworks and execution playbooks, not vague generalities.
"""

class AgentService:
    async def process_chat(self, request: ChatRequest, db: Session) -> ChatResponse:
        start_time = time.time()
        
        # 1. Resolve or create session
        session_id = request.session_id
        if not session_id:
            session_id = str(uuid.uuid4())
            # Derive title from first 6 words of message
            title_words = request.message.strip().split()[:6]
            session_title = " ".join(title_words)
            if len(request.message.strip().split()) > 6:
                session_title += "..."
            new_session = SessionModel(
                id=session_id,
                title=session_title or "New Conversation"
            )
            db.add(new_session)
            db.commit()
            logger.info(f"Created new session: {session_id} ('{session_title}')")
        else:
            session_obj = db.query(SessionModel).filter(SessionModel.id == session_id).first()
            if not session_obj:
                session_obj = SessionModel(id=session_id, title="New Conversation")
                db.add(session_obj)
                db.commit()

        # 2. Persist user message
        user_msg = MessageModel(
            id=str(uuid.uuid4()),
            session_id=session_id,
            role="user",
            content=request.message
        )
        db.add(user_msg)
        db.commit()

        # 3. Retrieve conversation history for context
        past_msgs = db.query(MessageModel).filter(
            MessageModel.session_id == session_id
        ).order_by(MessageModel.created_at.asc()).all()
        
        history_list = [{"role": m.role, "content": m.content} for m in past_msgs[:-1]] # exclude just-added user msg

        # 4. Search transcripts
        context_chunks, evidence_sufficient = retrieval_service.search(
            query=request.message,
            db=db,
            top_k=settings.TOP_K_RETRIEVAL
        )
        citations = retrieval_service.to_citation_items(context_chunks)

        # 5. Route to active LLM Provider
        provider_key, provider = await provider_manager.get_active_provider(request.provider)
        logger.info(f"Using provider '{provider_key}' for session {session_id} (evidence sufficient: {evidence_sufficient})")

        try:
            if not evidence_sufficient and not context_chunks:
                # Handle complete lack of evidence directly
                response_text = (
                    "The available Lenny's Podcast transcripts do not establish the answer to this question. "
                    "I am strictly grounded in genuine podcast interviews and will not fabricate information. "
                    "\n\n**You can ask me about:**\n"
                    "- Building high-performing growth teams (Adam Fishman)\n"
                    "- Growth loops vs. funnels and marketplace dynamics (Casey Winters, Brian Balfour)\n"
                    "- Product-Led Growth and Product-Led Sales (Elena Verna)\n"
                    "- Product leadership, high agency, and the LNO framework (Shreyas Doshi)\n"
                    "- The Adjacent User Theory (Bangaly Kaba)\n"
                    "- Reforge growth metrics and experimentation trees (Fareed Mosavat)"
                )
                latency_ms = int((time.time() - start_time) * 1000)
                model_used = f"{provider_key}/grounded-fallback"
            else:
                is_avail, status_msg, _ = await provider.check_availability()
                if not is_avail and provider_key != "offline":
                    logger.info(f"Provider {provider_key} is unavailable ({status_msg}). Engaging offline grounded engine with clear notice.")
                    fallback = provider_manager.providers["offline"]
                    fallback_text, latency_ms = await fallback.generate_response(
                        prompt=request.message,
                        system_prompt=SYSTEM_PROMPT,
                        conversation_history=history_list,
                        context_chunks=context_chunks
                    )
                    warning_header = (
                        f"> ℹ️ **Notice: {provider_key.upper()} is currently not active.** {status_msg}\n"
                        f"> *Grounded response generated seamlessly via the Lenny Offline Grounded Engine.*\n\n"
                    )
                    response_text = warning_header + fallback_text
                    model_used = f"{provider_key}->offline-grounded"
                else:
                    # Attempt Claude Agent SDK if provider is anthropic
                    sdk_response = None
                    if provider_key == "anthropic" and claude_agent_integration.is_sdk_installed:
                        sdk_text, sdk_diag = await claude_agent_integration.execute_agent_query(
                            prompt=request.message,
                            session_id=session_id,
                            system_prompt=SYSTEM_PROMPT
                        )
                        if sdk_text:
                            sdk_response = sdk_text
                            model_used = "anthropic/claude-agent-sdk"
                        elif sdk_diag:
                            logger.info(f"Claude Agent SDK note: {sdk_diag}")

                    if sdk_response:
                        response_text = sdk_response
                        latency_ms = int((time.time() - start_time) * 1000)
                    else:
                        response_text, latency_ms = await provider.generate_response(
                            prompt=request.message,
                            system_prompt=SYSTEM_PROMPT,
                            conversation_history=history_list,
                            context_chunks=context_chunks,
                            model=request.model
                        )
                        model_used = f"{provider_key}/{request.model or getattr(provider, 'default_model', 'default')}"
        except Exception as e:
            logger.warning(f"Provider {provider_key} encountered error: {e}. Falling back to offline grounded engine.")
            fallback = provider_manager.providers["offline"]
            response_text, latency_ms = await fallback.generate_response(
                prompt=request.message,
                system_prompt=SYSTEM_PROMPT,
                conversation_history=history_list,
                context_chunks=context_chunks
            )
            model_used = f"{provider_key}->offline-fallback"

        # 6. Extract generated artifacts (if assistant generated complete HTML or Markdown blocks)
        self._detect_and_persist_artifacts(db, session_id, response_text)

        # 7. Persist assistant message
        import json
        citations_json = json.dumps([c.model_dump() for c in citations])
        asst_msg = MessageModel(
            id=str(uuid.uuid4()),
            session_id=session_id,
            role="assistant",
            content=response_text,
            citations_json=citations_json,
            model_used=model_used,
            latency_ms=latency_ms
        )
        db.add(asst_msg)
        db.commit()
        db.refresh(asst_msg)

        # 8. Generate follow-up suggestions tailored to the response
        followups = self._generate_followups(context_chunks, request.message)

        return ChatResponse(
            session_id=session_id,
            message=MessageResponse(
                id=asst_msg.id,
                session_id=session_id,
                role=asst_msg.role,
                content=asst_msg.content,
                citations=citations,
                model_used=asst_msg.model_used,
                latency_ms=asst_msg.latency_ms,
                created_at=asst_msg.created_at
            ),
            suggested_followups=followups,
            evidence_sufficient=evidence_sufficient
        )

    def _detect_and_persist_artifacts(self, db: Session, session_id: str, text: str):
        """Scans response for code blocks that qualify as standalone artifacts."""
        # Check for HTML code blocks
        html_blocks = re.findall(r"```html\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
        for idx, html_content in enumerate(html_blocks):
            if len(html_content.strip()) > 80: # meaningful artifact
                artifact_service.create_artifact(
                    db=db,
                    artifact_in=ArtifactCreate(
                        session_id=session_id,
                        type="html",
                        title=f"Generated Visual Component #{idx+1}",
                        content=html_content.strip()
                    )
                )

        # Check for explicitly labeled Markdown artifacts
        md_blocks = re.findall(r"```markdown\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
        for idx, md_content in enumerate(md_blocks):
            if len(md_content.strip()) > 100:
                first_line = md_content.strip().split("\n")[0].replace("#", "").strip() or f"Generated Document #{idx+1}"
                artifact_service.create_artifact(
                    db=db,
                    artifact_in=ArtifactCreate(
                        session_id=session_id,
                        type="markdown",
                        title=first_line[:60],
                        content=md_content.strip()
                    )
                )

    def _generate_followups(self, chunks: List[Dict[str, Any]], query: str) -> List[str]:
        """Generates dynamic follow-up questions from the retrieved guests and themes."""
        if not chunks:
            return [
                "How should I structure a high-performing growth team?",
                "What is the difference between growth loops and funnels?",
                "How do top PMs use Shreyas Doshi's LNO framework?"
            ]
            
        guest = chunks[0]["guest"]
        suggestions = [
            f"What specific metrics does {guest} recommend tracking for this?",
            f"Can you generate a Ship 30 for 30 essay summarizing this framework?",
            f"What common failure modes does {guest} warn teams against?"
        ]
        return suggestions

agent_service = AgentService()
