"""
app/api/rag.py
--------------
FastAPI router exposing the /ask endpoint.

POST /ask
---------
Request body  : { "question": str, "top_k": int (optional, default 5) }
Response body : AskResponse (see below)

Full RAG pipeline:
  1. Check Redis cache  →  return immediately if hit
  2. Retrieve top-K chunks from pgvector  (rag/retriever.py)
  3. Build prompt from chunks + question  (rag/prompt.py)
  4. Call Gemini 2.5 Flash               (rag/llm.py)
  5. Store response in Redis cache       (rag/cache.py)
  6. Return response
"""
from __future__ import annotations

import time

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.config import DEFAULT_TOP_K, GEMINI_CHAT_MODEL
from rag.cache import cache_get, cache_set
from rag.llm import call_gemini
from rag.prompt import build_prompt, get_prompt_preview
from rag.retriever import retrieve

router = APIRouter()


# ── Request / Response models ─────────────────────────────────────────────────

class AskRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000,
                          description="The student's question")
    top_k: int    = Field(default=DEFAULT_TOP_K, ge=1, le=20,
                          description="Number of chunks to retrieve")
    document_name: str | None = Field(default=None,
                          description="Optional: filter to a specific document")


class SourceChunk(BaseModel):
    chunk_id:       str
    document_name:  str
    page_start:     int
    page_end:       int
    chapter_section: str | None
    text_preview:   str
    score:          float


class AskResponse(BaseModel):
    answer:         str
    sources:        list[SourceChunk]
    cached:         bool
    model:          str
    latency_ms:     int
    context_tokens: int
    prompt_preview: str
    top_k:          int


# ── /ask endpoint ─────────────────────────────────────────────────────────────

@router.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest) -> AskResponse:
    """
    Main RAG endpoint.  Runs the full 4-step pipeline and returns a
    grounded answer with source citations.
    """
    wall_start = time.perf_counter()
    question = req.question.strip()

    # ── Step 1: Cache check ───────────────────────────────────────────────────
    cached_data = cache_get(question)
    if cached_data:
        return AskResponse(**cached_data)

    # ── Step 2: Retrieve ──────────────────────────────────────────────────────
    try:
        chunks, embed_ms = retrieve(
            question=question,
            top_k=req.top_k,
            document_name=req.document_name,
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Retrieval failed: {exc}")

    # ── Step 3: Build prompt ──────────────────────────────────────────────────
    prompt, context_tokens = build_prompt(question, chunks)
    preview = get_prompt_preview(prompt)

    # ── Step 4: Call Gemini ───────────────────────────────────────────────────
    try:
        answer, llm_ms, model_name = call_gemini(prompt)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"LLM call failed: {exc}")

    # Total wall-clock latency
    total_ms = int((time.perf_counter() - wall_start) * 1000)

    # ── Build response ────────────────────────────────────────────────────────
    source_list = [
        SourceChunk(
            chunk_id=c.chunk_id,
            document_name=c.document_name,
            page_start=c.page_start,
            page_end=c.page_end,
            chapter_section=c.chapter_section,
            text_preview=c.text_preview,
            score=round(c.score, 4),
        )
        for c in chunks
    ]

    response_data = AskResponse(
        answer=answer,
        sources=source_list,
        cached=False,
        model=model_name,
        latency_ms=total_ms,
        context_tokens=context_tokens,
        prompt_preview=preview,
        top_k=req.top_k,
    )

    # ── Step 5: Cache the answer ──────────────────────────────────────────────
    cache_set(question, response_data.model_dump())

    return response_data
