"""
rag/retriever.py
----------------
Phase 3 Step 1: Embed the user question and retrieve the top-K most
similar chunks from Supabase pgvector using cosine similarity.

Uses Gemini text-embedding-004 (768-dim) - same model used during ingestion.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from functools import lru_cache

from ingestion.db import get_connection
from app.config import DEFAULT_TOP_K, GEMINI_API_KEY


EMBEDDING_MODEL = "gemini-embedding-001"


@dataclass
class RetrievedChunk:
    chunk_id:        str
    document_name:   str
    page_start:      int
    page_end:        int
    chapter_section: str | None
    text:            str
    token_count:     int
    score:           float
    text_preview:    str


@lru_cache(maxsize=1)
def _get_client():
    from google import genai
    return genai.Client(api_key=GEMINI_API_KEY)


def embed_question(question: str) -> list[float]:
    """Embed a single question string using Gemini gemini-embedding-001 (768 dims)."""
    client   = _get_client()
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=[question],
        config={"output_dimensionality": 768},
    )
    return response.embeddings[0].values


def _get_conn():
    return get_connection()


def retrieve(
    question: str,
    top_k: int = DEFAULT_TOP_K,
    document_name: str | None = None,
) -> tuple[list[RetrievedChunk], float]:
    """
    Embed *question* and return the top-K most similar chunks.

    Returns
    -------
    (chunks, embed_ms)
    """
    t0       = time.perf_counter()
    q_vector = embed_question(question)
    embed_ms = (time.perf_counter() - t0) * 1000

    vec_str  = "[" + ",".join(f"{v:.8f}" for v in q_vector) + "]"

    if document_name:
        sql = """
            SELECT chunk_id, document_name, page_start, page_end,
                   chapter_section, chunk_text, token_count,
                   1 - (embedding <=> %s::vector) AS score
            FROM content_chunks
            WHERE document_name = %s AND embedding IS NOT NULL
            ORDER BY embedding <=> %s::vector
            LIMIT %s;
        """
        params = (vec_str, document_name, vec_str, top_k)
    else:
        sql = """
            SELECT chunk_id, document_name, page_start, page_end,
                   chapter_section, chunk_text, token_count,
                   1 - (embedding <=> %s::vector) AS score
            FROM content_chunks
            WHERE embedding IS NOT NULL
            ORDER BY embedding <=> %s::vector
            LIMIT %s;
        """
        params = (vec_str, vec_str, top_k)

    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
    finally:
        conn.close()

    chunks = [
        RetrievedChunk(
            chunk_id=row[0],
            document_name=row[1],
            page_start=row[2],
            page_end=row[3],
            chapter_section=row[4],
            text=row[5],
            token_count=row[6],
            score=float(row[7]),
            text_preview=row[5][:200],
        )
        for row in rows
    ]

    return chunks, embed_ms
