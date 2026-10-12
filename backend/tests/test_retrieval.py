"""
Automated tests for Knowledge Retrieval, Hybrid Vector Search, and Grounding.
Verifies grounded citations and insufficient-evidence behavior.
"""
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.session import SessionLocal
from backend.app.services.retrieval_service import retrieval_service

client = TestClient(app)

def test_retrieval_service_direct():
    db = SessionLocal()
    try:
        # 1. Search for a core guest topic: Casey Winters and growth loops
        chunks, sufficient = retrieval_service.search("Casey Winters growth loops vs funnels", db, top_k=5)
        assert len(chunks) > 0
        assert sufficient is True
        assert any("casey-winters" in c["transcript_id"] or "Winters" in c["guest"] for c in chunks)

        # 2. Search for Elena Verna and PLG
        chunks_elena, sufficient_elena = retrieval_service.search("Elena Verna product led growth B2B", db, top_k=5)
        assert len(chunks_elena) > 0
        assert sufficient_elena is True
        assert any("elena" in c["transcript_id"].lower() for c in chunks_elena)

        # 3. Test citation formatting
        citations = retrieval_service.to_citation_items(chunks)
        assert len(citations) > 0
        first_cite = citations[0]
        assert first_cite.guest != ""
        assert first_cite.title != ""
        assert first_cite.excerpt != ""

        # 4. Search for completely out-of-domain query (Insufficient Evidence)
        chunks_ood, sufficient_ood = retrieval_service.search("quantum electrodynamics subatomic particle collision", db, top_k=5)
        assert sufficient_ood is False
    finally:
        db.close()

def test_transcripts_api_endpoints():
    # Test list transcripts
    res = client.get("/api/v1/transcripts")
    assert res.status_code == 200
    episodes = res.json()
    assert len(episodes) >= 8
    guests = [ep["guest"] for ep in episodes]
    assert any("Casey Winters" in g for g in guests)
    assert any("Elena Verna" in g for g in guests)

    # Test search transcripts endpoint
    search_res = client.get("/api/v1/transcripts/search?q=growth+loops")
    assert search_res.status_code == 200
    search_data = search_res.json()
    assert search_data["evidence_sufficient"] is True
    assert len(search_data["citations"]) > 0

    # Test search transcripts with out-of-domain query
    ood_res = client.get("/api/v1/transcripts/search?q=astrophysics+dark+matter")
    assert ood_res.status_code == 200
    ood_data = ood_res.json()
    assert ood_data["evidence_sufficient"] is False
