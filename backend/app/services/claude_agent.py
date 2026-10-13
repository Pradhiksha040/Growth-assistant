"""
Anthropic Claude Agent SDK integration module for The Lenny Growth Assistant.
Defines in-process MCP tools using claude_agent_sdk.tool, registers an SDK MCP server,
and provides unified execution and fallback routing for conversational agent tasks.
"""
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.db.session import SessionLocal
from backend.app.services.retrieval_service import retrieval_service
from backend.app.services.artifact_service import artifact_service

try:
    from claude_agent_sdk import (
        tool,
        create_sdk_mcp_server,
        ClaudeAgentOptions,
        query as claude_sdk_query,
        ClaudeSDKClient,
        SdkMcpTool
    )
    CLAUDE_SDK_AVAILABLE = True
except ImportError as e:
    CLAUDE_SDK_AVAILABLE = False
    logger.warning(f"claude_agent_sdk could not be imported: {e}")

# Tool 1: Search Lenny's Podcast Transcripts
if CLAUDE_SDK_AVAILABLE:
    @tool(
        name="search_lenny_transcripts",
        description="Search genuine transcripts from Lenny's Podcast for product management and growth playbooks.",
        input_schema={"query": str}
    )
    async def search_lenny_transcripts_tool(args: Dict[str, Any]) -> Dict[str, Any]:
        query_text = args.get("query", "").strip()
        if not query_text:
            return {
                "content": [{"type": "text", "text": "Error: query parameter cannot be empty."}],
                "is_error": True
            }
        
        db = SessionLocal()
        try:
            chunks, sufficient = retrieval_service.search(query_text, db, top_k=5)
            citations = retrieval_service.to_citation_items(chunks)
            payload = {
                "query": query_text,
                "evidence_sufficient": sufficient,
                "chunks_count": len(chunks),
                "citations": [c.model_dump() for c in citations]
            }
            return {
                "content": [{"type": "text", "text": json.dumps(payload, indent=2)}]
            }
        except Exception as exc:
            return {
                "content": [{"type": "text", "text": f"Search failed: {str(exc)}"}],
                "is_error": True
            }
        finally:
            db.close()

    @tool(
        name="create_growth_artifact",
        description="Persist and render an isolated Markdown document or sandboxed HTML/CSS widget as an in-app Artifact.",
        input_schema={
            "session_id": str,
            "type": str, # 'markdown' or 'html'
            "title": str,
            "content": str
        }
    )
    async def create_growth_artifact_tool(args: Dict[str, Any]) -> Dict[str, Any]:
        from backend.app.schemas.artifact import ArtifactCreate
        session_id = args.get("session_id")
        artifact_type = args.get("type", "markdown").lower()
        title = args.get("title", "Generated Artifact")
        content = args.get("content", "")

        if not session_id or not content:
            return {
                "content": [{"type": "text", "text": "Error: session_id and content are required."}],
                "is_error": True
            }

        db = SessionLocal()
        try:
            artifact_in = ArtifactCreate(
                session_id=session_id,
                type=artifact_type,
                title=title,
                content=content
            )
            created = artifact_service.create_artifact(db, artifact_in)
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps({
                        "status": "created",
                        "id": created.id,
                        "type": created.type,
                        "title": created.title
                    })
                }]
            }
        except Exception as exc:
            return {
                "content": [{"type": "text", "text": f"Artifact creation failed: {str(exc)}"}],
                "is_error": True
            }
        finally:
            db.close()

else:
    search_lenny_transcripts_tool = None
    create_growth_artifact_tool = None


class ClaudeAgentIntegration:
    """Manages MCP server creation, tool orchestration, and Claude Agent SDK execution."""
    def __init__(self):
        self.is_sdk_installed = CLAUDE_SDK_AVAILABLE
        self._mcp_server = None

    def get_registered_tools(self) -> List[Any]:
        if not self.is_sdk_installed:
            return []
        return [search_lenny_transcripts_tool, create_growth_artifact_tool]

    def get_or_create_mcp_server(self):
        """Builds in-process SDK MCP server config."""
        if not self.is_sdk_installed:
            return None
        if self._mcp_server is None:
            self._mcp_server = create_sdk_mcp_server(
                name="lenny_growth_mcp_server",
                version="1.0.0",
                tools=self.get_registered_tools()
            )
            logger.info("Initialized Claude Agent SDK in-process MCP server.")
        return self._mcp_server

    async def execute_agent_query(
        self,
        prompt: str,
        session_id: str,
        system_prompt: str
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Attempts execution via Claude Agent SDK.
        Returns (response_text, error_or_diagnostic_message).
        """
        if not self.is_sdk_installed:
            return None, "Claude Agent SDK is not installed in the Python environment."

        try:
            server_config = self.get_or_create_mcp_server()
            options = ClaudeAgentOptions(
                system_prompt=system_prompt,
                mcp_servers={"lenny_tools": server_config} if server_config else {}
            )
            
            output_blocks = []
            async for msg in claude_sdk_query(prompt=prompt, options=options):
                if hasattr(msg, "content"):
                    for item in msg.content:
                        if hasattr(item, "text"):
                            output_blocks.append(item.text)
                elif hasattr(msg, "result"):
                    output_blocks.append(str(msg.result))

            full_text = "\n".join(output_blocks).strip()
            return full_text or None, None

        except Exception as exc:
            err_msg = str(exc)
            logger.info(f"Claude Agent SDK execution note: {err_msg}")
            # If Claude Code CLI is unauthenticated or not logged in, capture actionable detail
            if "Not logged in" in err_msg or "authentication" in err_msg.lower():
                diagnostic = (
                    "Claude Agent SDK requires active Claude Code authentication (`claude /login`). "
                    "Grounded responses are served seamlessly via the direct Anthropic / Grounded provider pipeline."
                )
            else:
                diagnostic = f"Claude Agent SDK invocation note: {err_msg}"
            return None, diagnostic


claude_agent_integration = ClaudeAgentIntegration()
