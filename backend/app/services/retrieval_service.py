"""
Knowledge retrieval and ingestion service for Lenny's Podcast transcripts.
Handles transcript ingestion, text normalization, speaker-aware chunking,
hybrid semantic/lexical vector search, and strict evidence grounding.
"""
import os
import re
import json
import glob
from typing import List, Dict, Any, Tuple, Optional
import yaml
from sqlalchemy.orm import Session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.db.models import TranscriptModel, TranscriptChunkModel
from backend.app.schemas.chat import CitationItem

class RetrievalService:
    def __init__(self):
        self._vectorizer: Optional[TfidfVectorizer] = None
        self._fitted_chunk_ids: List[str] = []
        self._tfidf_matrix = None
        self._chunk_cache: Dict[str, Dict[str, Any]] = {}

    def parse_transcript_markdown(self, file_content: str, filename: str) -> Tuple[Dict[str, Any], str]:
        """Extracts YAML frontmatter and transcript body text."""
        frontmatter = {}
        body = file_content
        
        # Check for YAML frontmatter between --- and ---
        if file_content.startswith("---"):
            parts = file_content.split("---", 2)
            if len(parts) >= 3:
                try:
                    frontmatter = yaml.safe_load(parts[1]) or {}
                    body = parts[2]
                except Exception as e:
                    logger.warning(f"Error parsing YAML frontmatter in {filename}: {e}")
                    body = file_content
                    
        # Derive slug id from filename
        slug = os.path.splitext(os.path.basename(filename))[0].lower()
        if not frontmatter.get("guest"):
            frontmatter["guest"] = slug.replace("-", " ").title()
        if not frontmatter.get("title"):
            frontmatter["title"] = f"Lenny's Podcast: {frontmatter['guest']}"
            
        frontmatter["id"] = slug
        return frontmatter, body

    def chunk_transcript(self, transcript_id: str, guest: str, body: str) -> List[Dict[str, Any]]:
        """
        Splits transcript into overlapping, speaker-aware chunks.
        Preserves timestamps and speaker attributions on each chunk.
        """
        lines = body.split("\n")
        chunks = []
        
        current_speaker = guest
        current_timestamp = "00:00:00"
        speaker_pattern = re.compile(r"^([A-Z][a-zA-Z\s\.\-]+)\s*\(((\d{1,2}:)?\d{2}:\d{2})\):")
        
        current_chunk_words = []
        current_chunk_speaker = current_speaker
        current_chunk_timestamp = current_timestamp
        chunk_idx = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            match = speaker_pattern.match(line)
            if match:
                current_speaker = match.group(1).strip()
                current_timestamp = match.group(2).strip()
                dialogue_text = line[match.end():].strip()
            else:
                dialogue_text = line
                
            words = dialogue_text.split()
            current_chunk_words.extend(words)
            
            # If current chunk exceeds target word count, create a chunk
            if len(current_chunk_words) >= (settings.CHUNK_SIZE // 5):  # ~130 words / chunk
                chunk_text = " ".join(current_chunk_words)
                chunk_id = f"{transcript_id}_chunk_{chunk_idx}"
                chunks.append({
                    "id": chunk_id,
                    "transcript_id": transcript_id,
                    "chunk_index": chunk_idx,
                    "speaker": current_chunk_speaker,
                    "timestamp_str": current_chunk_timestamp,
                    "content": chunk_text,
                    "token_count": len(current_chunk_words)
                })
                chunk_idx += 1
                # Overlap: keep the last 25 words
                overlap_words = current_chunk_words[-25:]
                current_chunk_words = list(overlap_words)
                current_chunk_speaker = current_speaker
                current_chunk_timestamp = current_timestamp
                
        # Remainder
        if current_chunk_words:
            chunk_text = " ".join(current_chunk_words)
            chunk_id = f"{transcript_id}_chunk_{chunk_idx}"
            chunks.append({
                "id": chunk_id,
                "transcript_id": transcript_id,
                "chunk_index": chunk_idx,
                "speaker": current_chunk_speaker,
                "timestamp_str": current_chunk_timestamp,
                "content": chunk_text,
                "token_count": len(current_chunk_words)
            })
            
        return chunks

    def ingest_local_transcripts(self, db: Session) -> Dict[str, Any]:
        """Ingests all transcript markdown files from data/transcripts into the database."""
        transcripts_dir = settings.TRANSCRIPTS_DIR
        files = glob.glob(os.path.join(transcripts_dir, "*.md"))
        
        episodes_ingested = 0
        chunks_created = 0
        errors = []
        
        for filepath in files:
            try:
                filename = os.path.basename(filepath)
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                meta, body = self.parse_transcript_markdown(content, filename)
                slug = meta["id"]
                
                # Check if already exists in DB
                existing = db.query(TranscriptModel).filter(TranscriptModel.id == slug).first()
                if existing:
                    # Delete old chunks to refresh
                    db.query(TranscriptChunkModel).filter(TranscriptChunkModel.transcript_id == slug).delete()
                    existing.guest = meta.get("guest", slug)
                    existing.title = meta.get("title", slug)
                    existing.youtube_url = meta.get("youtube_url")
                    existing.video_id = meta.get("video_id")
                    existing.publish_date = str(meta.get("publish_date", ""))
                    existing.duration = str(meta.get("duration", ""))
                    existing.description = str(meta.get("description", ""))
                    existing.source_file = filename
                else:
                    new_ep = TranscriptModel(
                        id=slug,
                        guest=meta.get("guest", slug),
                        title=meta.get("title", slug),
                        youtube_url=meta.get("youtube_url"),
                        video_id=meta.get("video_id"),
                        publish_date=str(meta.get("publish_date", "")),
                        duration=str(meta.get("duration", "")),
                        description=str(meta.get("description", "")),
                        source_file=filename
                    )
                    db.add(new_ep)
                    
                chunks = self.chunk_transcript(slug, meta.get("guest", slug), body)
                for ch in chunks:
                    chunk_obj = TranscriptChunkModel(
                        id=ch["id"],
                        transcript_id=slug,
                        chunk_index=ch["chunk_index"],
                        speaker=ch["speaker"],
                        timestamp_str=ch["timestamp_str"],
                        content=ch["content"],
                        token_count=ch["token_count"]
                    )
                    db.add(chunk_obj)
                    chunks_created += 1
                    
                db.commit()
                episodes_ingested += 1
                logger.info(f"Ingested {slug}: {len(chunks)} chunks.")
            except Exception as e:
                db.rollback()
                err_msg = f"Failed to ingest {filepath}: {str(e)}"
                logger.error(err_msg)
                errors.append(err_msg)
                
        # Re-build search index
        self.rebuild_search_index(db)
        
        return {
            "status": "success" if not errors else "partial",
            "episodes_ingested": episodes_ingested,
            "chunks_created": chunks_created,
            "message": f"Successfully ingested {episodes_ingested} episodes ({chunks_created} chunks).",
            "errors": errors
        }

    def rebuild_search_index(self, db: Session):
        """Builds in-memory TF-IDF semantic vector matrix across all chunks."""
        chunks = db.query(TranscriptChunkModel, TranscriptModel).join(
            TranscriptModel, TranscriptChunkModel.transcript_id == TranscriptModel.id
        ).all()
        
        if not chunks:
            logger.info("No chunks to index in search index.")
            return
            
        corpus = []
        self._fitted_chunk_ids = []
        self._chunk_cache = {}
        
        for chunk_model, ep_model in chunks:
            text = f"{ep_model.title} {ep_model.guest} {chunk_model.speaker} {chunk_model.content}"
            corpus.append(text)
            self._fitted_chunk_ids.append(chunk_model.id)
            self._chunk_cache[chunk_model.id] = {
                "chunk_id": chunk_model.id,
                "transcript_id": ep_model.id,
                "title": ep_model.title,
                "guest": ep_model.guest,
                "youtube_url": ep_model.youtube_url,
                "timestamp_str": chunk_model.timestamp_str,
                "speaker": chunk_model.speaker,
                "content": chunk_model.content
            }
            
        self._vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words="english",
            max_features=25000,
            sublinear_tf=True
        )
        self._tfidf_matrix = self._vectorizer.fit_transform(corpus)
        logger.info(f"Search index built successfully with {len(corpus)} chunks.")

    def search(self, query: str, db: Session, top_k: int = 5) -> Tuple[List[Dict[str, Any]], bool]:
        """
        Performs hybrid retrieval matching against query.
        Returns top relevant chunks with calculated relevance score and evidence sufficiency flag.
        """
        if self._vectorizer is None or self._tfidf_matrix is None or not self._fitted_chunk_ids:
            self.rebuild_search_index(db)
            
        if self._vectorizer is None or self._tfidf_matrix is None or not self._fitted_chunk_ids:
            return [], False
            
        query_vec = self._vectorizer.transform([query])
        sims = cosine_similarity(query_vec, self._tfidf_matrix).flatten()
        
        # Stopwords that frequently appear in conversational PM queries and speech
        common_words = {"about", "there", "their", "where", "which", "could", "would", "should", 
                        "thing", "things", "matter", "point", "think", "people", "really", "going", "know", "like", "with"}
        query_lower = query.lower()
        key_terms = [t for t in re.findall(r"\b[a-zA-Z]{3,}\b", query_lower) if t not in common_words]
        
        # Check if the query has any rare or distinct query terms in the vectorizer vocab
        feature_names = self._vectorizer.vocabulary_
        matched_vocab = [t for t in key_terms if t in feature_names]
        
        scored_results = []
        for idx, base_score in enumerate(sims):
            if base_score < 0.03:
                continue
            chunk_id = self._fitted_chunk_ids[idx]
            cached = self._chunk_cache[chunk_id]
            content_lower = cached["content"].lower()
            guest_lower = cached["guest"].lower()
            title_lower = cached["title"].lower()
            
            boost = 0.0
            for term in key_terms:
                if term in content_lower:
                    boost += 0.03
                if term in guest_lower or term in title_lower:
                    boost += 0.06
                    
            final_score = float(base_score + boost)
            result_item = dict(cached)
            result_item["base_score"] = float(base_score)
            result_item["relevance_score"] = round(final_score, 4)
            scored_results.append(result_item)
                
        scored_results.sort(key=lambda x: x["relevance_score"], reverse=True)
        top_results = scored_results[:top_k]
        
        # Grounding check: determine if evidence is sufficient
        # Must have:
        # 1. At least one chunk
        # 2. Vocabulary coverage of key terms >= 55%
        # 3. Base vector similarity >= 0.08 AND final score >= settings.SIMILARITY_THRESHOLD
        vocab_coverage = (len(matched_vocab) / len(key_terms)) if key_terms else 0.0
        evidence_sufficient = False
        if top_results and vocab_coverage >= 0.55:
            top_base = top_results[0].get("base_score", 0.0)
            top_score = top_results[0].get("relevance_score", 0.0)
            if top_base >= 0.08 and top_score >= settings.SIMILARITY_THRESHOLD:
                evidence_sufficient = True
            
        return top_results, evidence_sufficient

    def to_citation_items(self, chunks: List[Dict[str, Any]]) -> List[CitationItem]:
        """Converts raw chunk dicts into structured CitationItem schemas."""
        citations = []
        seen = set()
        for ch in chunks:
            key = (ch["transcript_id"], ch.get("timestamp_str"))
            if key in seen:
                continue
            seen.add(key)
            citations.append(CitationItem(
                transcript_id=ch["transcript_id"],
                title=ch["title"],
                guest=ch["guest"],
                youtube_url=ch.get("youtube_url"),
                timestamp_str=ch.get("timestamp_str"),
                excerpt=ch["content"][:240] + ("..." if len(ch["content"]) > 240 else ""),
                relevance_score=ch.get("relevance_score")
            ))
        return citations

retrieval_service = RetrievalService()
