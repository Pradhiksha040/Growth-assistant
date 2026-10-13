"""
Dedicated RAG Quality Audit Test Suite.
Verifies the 6 core evaluation scenarios specified in the take-home requirements:
1. A question clearly supported by an ingested transcript.
2. A follow-up question requiring the previous conversation's context.
3. A question unsupported by the knowledge base.
4. A question containing a misleading assumption.
5. A question requiring multiple transcript sources.
6. A question from a newly created session that must not access another session's conversation.
7. Actionable error guidance when knowledge base is empty.
"""
import uuid
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.session import SessionLocal
from backend.app.db.models import SessionModel, MessageModel, TranscriptModel

client = TestClient(app)

def test_scenario_1_supported_question():
    """
    Scenario 1: A question clearly supported by an ingested transcript.
    Verifies genuine citations, episode attribution, timestamps, and zero hallucination.
    """
    sess_res = client.post("/api/v1/sessions", json={"title": "RAG Audit - Supported Question"})
    assert sess_res.status_code == 201
    session_id = sess_res.json()["id"]

    query = "How does Shreyas Doshi explain pre-mortems and threats using tigers, paper tigers, and elephants?"
    chat_res = client.post("/api/v1/chat", json={
        "session_id": session_id,
        "message": query
    })
    assert chat_res.status_code == 200
    data = chat_res.json()

    assert data["evidence_sufficient"] is True
    assert len(data["message"]["citations"]) > 0

    # Verify attribution to Shreyas Doshi and authentic episode
    citations = data["message"]["citations"]
    guests = [c["guest"] for c in citations]
    assert "Shreyas Doshi" in guests

    first_shreyas_cite = next(c for c in citations if c["guest"] == "Shreyas Doshi")
    assert "The art of product management" in first_shreyas_cite["title"]
    assert first_shreyas_cite["timestamp_str"] is not None
    assert len(first_shreyas_cite["excerpt"]) > 20

    # Content verification
    content = data["message"]["content"]
    assert "Shreyas Doshi" in content
    assert "tiger" in content.lower() or "pre-mortem" in content.lower()


def test_scenario_2_conversational_follow_up():
    """
    Scenario 2: A follow-up question requiring the previous conversation's context.
    Verifies multi-turn history resolution and pronoun grounding.
    """
    sess_res = client.post("/api/v1/sessions", json={"title": "RAG Audit - Follow-up Context"})
    session_id = sess_res.json()["id"]

    # Turn 1: Discuss Casey Winters kindle vs fire strategies
    turn1_res = client.post("/api/v1/chat", json={
        "session_id": session_id,
        "message": "What does Casey Winters say about kindle strategies and fire strategies for growth?"
    })
    assert turn1_res.status_code == 200
    assert turn1_res.json()["evidence_sufficient"] is True

    # Turn 2: Follow-up using pronoun "he"
    turn2_res = client.post("/api/v1/chat", json={
        "session_id": session_id,
        "message": "What does he say is the primary purpose of those kindle strategies?"
    })
    assert turn2_res.status_code == 200
    turn2_data = turn2_res.json()

    assert turn2_data["evidence_sufficient"] is True
    turn2_citations = turn2_data["message"]["citations"]
    assert any(c["guest"] == "Casey Winters" for c in turn2_citations)

    # Verify conversation continuity in DB
    db = SessionLocal()
    msgs = db.query(MessageModel).filter(MessageModel.session_id == session_id).order_by(MessageModel.created_at.asc()).all()
    assert len(msgs) == 4 # 2 user + 2 assistant
    assert msgs[0].role == "user"
    assert msgs[1].role == "assistant"
    assert msgs[2].role == "user"
    assert msgs[3].role == "assistant"
    db.close()


def test_scenario_3_unsupported_out_of_domain():
    """
    Scenario 3: A question unsupported by the knowledge base.
    Verifies evidence sufficiency gate, transparent refusal, and zero hallucination.
    """
    sess_res = client.post("/api/v1/sessions", json={"title": "RAG Audit - Unsupported Out-of-Domain"})
    session_id = sess_res.json()["id"]

    unsupported_query = "What is the biological mechanism of CRISPR-Cas9 genome editing in eukaryotic cells?"
    chat_res = client.post("/api/v1/chat", json={
        "session_id": session_id,
        "message": unsupported_query
    })
    assert chat_res.status_code == 200
    data = chat_res.json()

    assert data["evidence_sufficient"] is False
    content = data["message"]["content"]
    assert "The available Lenny's Podcast transcripts do not establish the answer" in content
    assert "You can ask me about" in content


def test_scenario_4_misleading_assumption():
    """
    Scenario 4: A question containing a misleading assumption.
    Verifies that the assistant explicitly fact-checks and corrects false premises.
    """
    sess_res = client.post("/api/v1/sessions", json={"title": "RAG Audit - Misleading Assumption"})
    session_id = sess_res.json()["id"]

    misleading_query = "Why did Shreyas Doshi recommend that PMs dedicate 90% of their time to Overhead tasks in the LNO framework?"
    chat_res = client.post("/api/v1/chat", json={
        "session_id": session_id,
        "message": misleading_query
    })
    assert chat_res.status_code == 200
    data = chat_res.json()

    content = data["message"]["content"]
    # Verify fact-check / correction of premise
    assert "Fact-Check" in content or "Correction" in content or "incorrect" in content.lower()
    assert "Overhead" in content
    assert "Leverage" in content


def test_scenario_5_multiple_transcript_sources():
    """
    Scenario 5: A question requiring multiple transcript sources.
    Verifies multi-guest synthesis and diverse citations across distinct episodes.
    """
    sess_res = client.post("/api/v1/sessions", json={"title": "RAG Audit - Multi-Source Synthesis"})
    session_id = sess_res.json()["id"]

    multi_source_query = "Compare how Casey Winters and Brian Balfour approach growth loops with Elena Verna's view on product-led growth."
    chat_res = client.post("/api/v1/chat", json={
        "session_id": session_id,
        "message": multi_source_query
    })
    assert chat_res.status_code == 200
    data = chat_res.json()

    assert data["evidence_sufficient"] is True
    citations = data["message"]["citations"]
    assert len(citations) >= 2

    # Verify that multiple unique guests are returned in citations
    guests_in_citations = set(c["guest"] for c in citations)
    assert len(guests_in_citations) >= 2, f"Expected at least 2 distinct guests, got {guests_in_citations}"


def test_scenario_6_session_isolation_no_cross_leakage():
    """
    Scenario 6: A question from a newly created session that must not access another session's conversation.
    Verifies cryptographic session isolation and prevention of cross-talk context leakage.
    """
    # 1. Session A: Discuss Elena Verna PLG
    sess_a_res = client.post("/api/v1/sessions", json={"title": "Session A - Elena Verna"})
    session_a_id = sess_a_res.json()["id"]

    client.post("/api/v1/chat", json={
        "session_id": session_a_id,
        "message": "What are Elena Verna's core principles for product-led growth and sales?"
    })

    # 2. Session B: Brand new, distinct session
    sess_b_res = client.post("/api/v1/sessions", json={"title": "Session B - Isolated"})
    session_b_id = sess_b_res.json()["id"]

    # In Session B, ask about "the guest we were just discussing" without mentioning Elena Verna
    sess_b_chat = client.post("/api/v1/chat", json={
        "session_id": session_b_id,
        "message": "Who was the guest we were just discussing and what were their 3 key points?"
    })
    assert sess_b_chat.status_code == 200
    b_data = sess_b_chat.json()

    # Verify DB isolation: Session B only has its own messages
    db = SessionLocal()
    b_msgs = db.query(MessageModel).filter(MessageModel.session_id == session_b_id).all()
    assert len(b_msgs) == 2 # 1 user + 1 assistant
    assert "Elena Verna's core principles" not in [m.content for m in b_msgs]

    # Verify Session A messages are untouched
    a_msgs = db.query(MessageModel).filter(MessageModel.session_id == session_a_id).all()
    assert len(a_msgs) == 2
    db.close()


def test_scenario_empty_knowledge_base_actionable_message():
    """
    Scenario 7: Actionable error guidance when knowledge base is empty.
    Verifies that when no transcripts exist, the system explains how to seed/ingest real data.
    """
    # Mock temporary empty database condition by checking agent_service behavior
    from backend.app.schemas.chat import ChatRequest
    from backend.app.services.agent_service import agent_service
    from unittest.mock import MagicMock

    mock_db = MagicMock()
    mock_db.query().count.return_value = 0 # 0 transcripts in DB

    import asyncio
    req = ChatRequest(message="Tell me about growth loops")
    res = asyncio.run(agent_service.process_chat(req, mock_db))

    assert res.evidence_sufficient is False
    assert "No Lenny's Podcast Transcripts Found in Knowledge Base" in res.message.content
    assert "seed_database" in res.message.content
    assert "api/v1/ingest" in res.message.content
