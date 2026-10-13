"""
Automated tests for Claude Agent SDK integration and in-process MCP tools.
Verifies tool registration, tool execution, schema validation, and fallback handling.
"""
import pytest
import json
import uuid
from backend.app.services.claude_agent import (
    CLAUDE_SDK_AVAILABLE,
    search_lenny_transcripts_tool,
    create_growth_artifact_tool,
    claude_agent_integration
)
from backend.app.db.session import SessionLocal
from backend.app.db.models import SessionModel, ArtifactModel

def test_claude_sdk_tools_registration():
    """Verifies that MCP tools are defined and registered with the integration."""
    assert CLAUDE_SDK_AVAILABLE is True
    tools = claude_agent_integration.get_registered_tools()
    assert len(tools) == 2
    assert search_lenny_transcripts_tool.name == "search_lenny_transcripts"
    assert "query" in search_lenny_transcripts_tool.input_schema
    assert create_growth_artifact_tool.name == "create_growth_artifact"
    assert "session_id" in create_growth_artifact_tool.input_schema
    server = claude_agent_integration.get_or_create_mcp_server()
    assert server is not None

@pytest.mark.asyncio
async def test_search_lenny_transcripts_tool_valid():
    """Verifies the search tool executes against the transcript database and returns citations."""
    res = await search_lenny_transcripts_tool.handler({"query": "growth loops"})
    assert "content" in res
    assert len(res["content"]) > 0
    text_data = res["content"][0]["text"]
    parsed = json.loads(text_data)
    assert parsed["query"] == "growth loops"
    assert "citations" in parsed
    assert parsed["chunks_count"] > 0

@pytest.mark.asyncio
async def test_search_lenny_transcripts_tool_empty():
    """Verifies empty query yields error payload."""
    res = await search_lenny_transcripts_tool.handler({"query": "   "})
    assert res.get("is_error") is True

@pytest.mark.asyncio
async def test_create_growth_artifact_tool_valid():
    """Verifies the artifact creation MCP tool persists artifacts to DB."""
    db = SessionLocal()
    sess_id = str(uuid.uuid4())
    test_sess = SessionModel(id=sess_id, title="SDK Artifact Test Session")
    db.add(test_sess)
    db.commit()
    db.close()

    res = await create_growth_artifact_tool.handler({
        "session_id": sess_id,
        "type": "markdown",
        "title": "SDK Generated Retention Playbook",
        "content": "# Retention Playbook\n\nHigh agency cohort analysis."
    })
    assert "content" in res
    parsed = json.loads(res["content"][0]["text"])
    assert parsed["status"] == "created"
    assert parsed["type"] == "markdown"
    assert parsed["title"] == "SDK Generated Retention Playbook"

    # Verify persisted in database
    db = SessionLocal()
    persisted = db.query(ArtifactModel).filter(ArtifactModel.id == parsed["id"]).first()
    assert persisted is not None
    assert persisted.session_id == sess_id
    assert "Retention Playbook" in persisted.content
    db.close()

@pytest.mark.asyncio
async def test_create_growth_artifact_tool_missing_params():
    """Verifies error handling when required params are missing."""
    res = await create_growth_artifact_tool.handler({"session_id": ""})
    assert res.get("is_error") is True

@pytest.mark.asyncio
async def test_execute_agent_query_unauthenticated_graceful_diagnostic():
    """Verifies that execute_agent_query handles unauthenticated Claude CLI cleanly."""
    res, diag = await claude_agent_integration.execute_agent_query(
        prompt="Tell me about growth loops",
        session_id=str(uuid.uuid4()),
        system_prompt="You are Lenny Growth Assistant"
    )
    # When Claude CLI is not logged in, it must return diagnostic rather than crashing
    assert res is None or isinstance(res, str)
    if res is None:
        assert diag is not None
        assert "Claude" in diag
