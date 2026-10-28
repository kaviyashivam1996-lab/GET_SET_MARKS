"""
app/main.py
-----------
FastAPI application entry point for GetSetMarks RAG & Exam POC backend.

Endpoints
---------
  GET  /health            ->  backend + DB liveness check
  POST /ask               ->  RAG retrieval & chatbot
  GET  /content/...       ->  Taxonomy, subjects, chapters, guides
  POST /practice/...      ->  Question sets & dynamic paper generator
  POST /exam/...          ->  Mock exam, anti-cheat proctoring log, submit
  POST /grade/...         ->  Board-rubric strict AI answer evaluation
  GET  /leaderboard/...   ->  Board/class partitioned leaderboards
  GET  /parent/...        ->  Parent progress dashboard
"""
from __future__ import annotations

import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from ingestion.db import get_connection
from app.config import APP_DEBUG
from app.api.rag import router as rag_router
from app.api.content import router as content_router
from app.api.practice import router as practice_router
from app.api.exam import router as exam_router
from app.api.grading import router as grading_router
from app.api.leaderboard import router as leaderboard_router
from app.api.parent import router as parent_router

app = FastAPI(
    title="GET_SET_MARKS — AI Exam Prep & RAG Platform",
    description="Full POC for CBSE & Tamil Nadu State Board (Classes 10 & 12) with RAG Chatbot, Dynamic Practice, Timed Proctored Exams, Board-Rubric Strict AI Evaluation & Leaderboards.",
    version="1.0.0",
    debug=APP_DEBUG,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(rag_router, tags=["RAG Chatbot"])
app.include_router(content_router)
app.include_router(practice_router)
app.include_router(exam_router)
app.include_router(grading_router)
app.include_router(leaderboard_router)
app.include_router(parent_router)

# Serve static files for POC UI
static_dir = Path(__file__).resolve().parents[1] / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/health", tags=["Health"])
async def health():
    """Liveness check. Returns API, DB status, and chunk count."""
    db_status = "ok"
    db_error = None
    chunk_count = None

    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM content_chunks;")
            chunk_count = cur.fetchone()[0]
        conn.close()
    except Exception as exc:
        db_status = "error"
        db_error = str(exc)

    return {
        "api": "ok",
        "db": db_status,
        "db_error": db_error,
        "chunk_count": chunk_count,
        "timestamp": time.time(),
    }
