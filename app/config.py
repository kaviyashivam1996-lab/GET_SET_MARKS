"""
app/config.py
-------------
Single source of truth for all environment variables.
Loaded once at startup; all modules import from here.
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from the backend root
_ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(_ENV_PATH)


def _req(key: str) -> str:
    val = os.getenv(key, "").strip()
    if not val:
        raise RuntimeError(
            "Required env var '{}' is missing or empty in .env  (path: {})".format(key, _ENV_PATH)
        )
    return val


# Database
DATABASE_URL_SYNC: str = _req("DATABASE_URL_SYNC")

# Gemini
GEMINI_API_KEY: str    = _req("GEMINI_API_KEY")
GEMINI_CHAT_MODEL: str = os.getenv("GEMINI_CHAT_MODEL", "gemini-3.8-flash")
GEMINI_EVAL_MODEL: str = os.getenv("GEMINI_EVAL_MODEL", "gemini-3.8-flash")

# Redis
REDIS_URL: str        = os.getenv("REDIS_URL", "redis://localhost:6379/0")
RAG_CACHE_TTL: int    = int(os.getenv("REDIS_RAG_CACHE_TTL", "86400"))

# Embeddings
EMBEDDING_DIM: int    = int(os.getenv("EMBEDDING_DIMENSION", "768"))

# RAG retrieval
DEFAULT_TOP_K: int    = int(os.getenv("RAG_TOP_K", "5"))

# LLM behaviour
LLM_MAX_RETRIES: int  = int(os.getenv("LLM_MAX_RETRIES", "2"))
LLM_TIMEOUT: int      = int(os.getenv("LLM_TIMEOUT_SECONDS", "30"))

# App
APP_HOST: str         = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT: int         = int(os.getenv("APP_PORT", "8000"))
APP_DEBUG: bool       = os.getenv("APP_DEBUG", "true").lower() == "true"
CORS_ORIGINS: list    = [
    o.strip()
    for o in os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000").split(",")
    if o.strip()
]
