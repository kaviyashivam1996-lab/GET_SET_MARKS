"""
rag/cache.py
------------
Phase 3 Step 4: Redis-backed 24h answer cache.

Cache key  : sha256(question.lower().strip())
Cache value: JSON-serialised AskResponse dict
TTL        : REDIS_RAG_CACHE_TTL seconds (default 86400 = 24h)

Redis is optional: if the connection fails, the cache is silently bypassed
and the pipeline continues without caching (graceful degradation).
"""
from __future__ import annotations

import hashlib
import json
import logging

from app.config import REDIS_URL, RAG_CACHE_TTL

logger = logging.getLogger(__name__)

_redis_client = None


def _get_redis():
    """Lazy-init Redis client; returns None if Redis is unavailable."""
    global _redis_client
    if _redis_client is not None:
        return _redis_client
    try:
        import redis
        client = redis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=2)
        client.ping()          # test the connection
        _redis_client = client
        return client
    except Exception as exc:
        logger.warning("Redis unavailable (%s) — cache disabled.", exc)
        return None


def _make_key(question: str) -> str:
    """Deterministic cache key from the normalised question."""
    normalised = question.lower().strip()
    return "gsm:rag:" + hashlib.sha256(normalised.encode()).hexdigest()


def cache_get(question: str) -> dict | None:
    """
    Return cached response dict if present, else None.
    Never raises — any Redis error returns None.
    """
    client = _get_redis()
    if client is None:
        return None
    try:
        key = _make_key(question)
        raw = client.get(key)
        if raw:
            data = json.loads(raw)
            data["cached"] = True      # mark as cache hit
            return data
    except Exception as exc:
        logger.warning("Cache GET failed: %s", exc)
    return None


def cache_set(question: str, response: dict) -> bool:
    """
    Store *response* dict in Redis with TTL.
    Returns True on success, False on any error.
    """
    client = _get_redis()
    if client is None:
        return False
    try:
        key = _make_key(question)
        payload = {**response, "cached": False}   # store with cached=False
        client.setex(key, RAG_CACHE_TTL, json.dumps(payload))
        return True
    except Exception as exc:
        logger.warning("Cache SET failed: %s", exc)
        return False
