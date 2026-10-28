"""
ingestion/embedder.py
----------------------
Embedding generation using Google Gemini text-embedding-004.

Model : text-embedding-004 (Google)
Dims  : 768  (matches EMBEDDING_DIMENSION=768 in .env)

No local model required - uses the Gemini Embeddings API.
Same API key as the chat model (GEMINI_API_KEY in .env).
"""
from __future__ import annotations

import os
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

EMBEDDING_MODEL   = "gemini-embedding-001"
EMBEDDING_DIM     = int(os.getenv("EMBEDDING_DIMENSION", "768"))
BATCH_SIZE        = int(os.getenv("EMBEDDING_BATCH_SIZE", "12"))
_GEMINI_API_KEY   = os.getenv("GEMINI_API_KEY", "")

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=_GEMINI_API_KEY)
    return _client


def get_embedder():
    """Return a sentinel object to keep the calling interface compatible."""
    client = _get_client()
    print(f"  [embedder] Using Gemini {EMBEDDING_MODEL} (dim={EMBEDDING_DIM})")
    return client


def embed_chunks(texts: list[str], model=None) -> list[list[float]]:
    """
    Generate embeddings for a list of text strings via Gemini API.

    Parameters
    ----------
    texts : list of chunk texts
    model : ignored (kept for interface compatibility)

    Returns
    -------
    list[list[float]]
        One 768-dimensional vector per input text.
    """
    client = _get_client()
    total  = len(texts)
    all_vectors: list[list[float]] = []

    # Use smaller batch size (12) if not specified to prevent 429 rate limit
    batch_size = int(os.getenv("EMBEDDING_BATCH_SIZE", "12"))

    for batch_start in range(0, total, batch_size):
        batch     = texts[batch_start: batch_start + batch_size]
        batch_end = min(batch_start + batch_size, total)
        print(
            f"  [embedder] Embedding chunks {batch_start + 1}-{batch_end} / {total} ...",
            flush=True,
        )

        max_retries = 6
        retry_delay = 5.0
        success = False

        for attempt in range(max_retries):
            try:
                response = client.models.embed_content(
                    model=EMBEDDING_MODEL,
                    contents=batch,
                    config={"output_dimensionality": EMBEDDING_DIM},
                )
                for emb in response.embeddings:
                    all_vectors.append(emb.values)
                success = True
                break
            except Exception as e:
                err_msg = str(e)
                if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg or "rate" in err_msg.lower():
                    print(
                        f"  [embedder] Rate limited (429). Retrying batch {batch_start + 1}-{batch_end} "
                        f"in {retry_delay:.0f}s (attempt {attempt + 1}/{max_retries}) ...",
                        flush=True,
                    )
                    time.sleep(retry_delay)
                    retry_delay *= 2.0
                else:
                    raise e

        if not success:
            raise RuntimeError(
                f"Failed to embed batch {batch_start + 1}-{batch_end} after {max_retries} attempts."
            )

        # Rate limit friendly delay between batches
        if batch_end < total:
            time.sleep(1.0)

    print(f"  [embedder] Done - {len(all_vectors)} embeddings generated.")
    return all_vectors

