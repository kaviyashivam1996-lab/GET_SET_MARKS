"""
ingestion/db.py
---------------
Supabase PostgreSQL connection and pgvector storage for Phase 2.

Responsibilities
----------------
- get_connection()          : psycopg2 sync connection from DATABASE_URL_SYNC
- ensure_table(conn)        : CREATE EXTENSION + TABLE + INDEX (all idempotent)
- upsert_chunks(...)        : bulk upsert chunks + embeddings (no duplicates)
- verify(conn)              : count and inspect stored embeddings
- get_sample_chunks(conn)   : retrieve N rows for manual inspection

Idempotency
-----------
chunk_id = sha256(document_name + str(chunk_index))
Upsert: INSERT ... ON CONFLICT (chunk_id) DO UPDATE
Re-running never creates duplicates — it updates in place.

Phase 3 hook
------------
The ivfflat index on `embedding` enables fast cosine similarity retrieval
via `ORDER BY embedding <=> query_vector LIMIT k`.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import TYPE_CHECKING

try:
    import psycopg2
    import psycopg2.extras
    _HAS_PSYCOPG2 = True
except Exception:
    _HAS_PSYCOPG2 = False

from dotenv import load_dotenv

if TYPE_CHECKING:
    from .models import Chunk

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

# ---------------------------------------------------------------------------
# DDL
# ---------------------------------------------------------------------------
_CREATE_EXTENSION = "CREATE EXTENSION IF NOT EXISTS vector;"

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS content_chunks (
    id              BIGSERIAL PRIMARY KEY,
    chunk_id        TEXT         UNIQUE NOT NULL,
    document_name   TEXT         NOT NULL,
    page_start      INT          NOT NULL,
    page_end        INT          NOT NULL,
    chapter_section TEXT,
    chunk_text      TEXT         NOT NULL,
    token_count     INT,
    embedding       VECTOR(768),
    created_at      TIMESTAMPTZ  DEFAULT NOW()
);
"""

# IVFFlat index — lists=20 is appropriate for ~200 rows (sqrt(193)≈14, rounded up)
# Increase lists proportionally as more documents are ingested.
_CREATE_INDEX = """
CREATE INDEX IF NOT EXISTS idx_content_chunks_embedding
    ON content_chunks
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 20);
"""

_CREATE_TEXT_INDEX = """
CREATE INDEX IF NOT EXISTS idx_content_chunks_doc
    ON content_chunks (document_name, page_start);
"""


# ---------------------------------------------------------------------------
# Connection
# ---------------------------------------------------------------------------

def get_connection():
    """Return a sync connection (psycopg2 or pg8000 fallback) using DATABASE_URL_SYNC from .env."""
    url = os.getenv("DATABASE_URL_SYNC")
    if not url:
        raise RuntimeError(
            "DATABASE_URL_SYNC is not set in .env. "
            "Example: postgresql://postgres:password@host:5432/postgres?sslmode=require"
        )
    if _HAS_PSYCOPG2:
        try:
            return psycopg2.connect(url)
        except Exception as e:
            if "DLL load failed" in str(e) or "Application Control" in str(e):
                print("  [db] psycopg2 blocked by Windows Security, falling back to pg8000 ...")
            else:
                raise e

    # Fallback to pg8000 (pure Python, immune to Windows Security DLL blocks)
    import urllib.parse
    import pg8000.dbapi
    p = urllib.parse.urlparse(url)
    ssl_ctx = True if ("sslmode=require" in p.query or "sslmode=verify" in p.query) else None
    user = urllib.parse.unquote(p.username) if p.username else ""
    password = urllib.parse.unquote(p.password) if p.password else ""
    return pg8000.dbapi.connect(
        user=user,
        password=password,
        host=p.hostname,
        port=p.port or 5432,
        database=p.path.lstrip("/"),
        ssl_context=ssl_ctx,
    )


# ---------------------------------------------------------------------------
# Schema management
# ---------------------------------------------------------------------------

def ensure_table(conn) -> None:
    """
    Create the pgvector extension, content_chunks table, and indexes.
    Safe to call multiple times — all statements use IF NOT EXISTS.
    """
    with conn.cursor() as cur:
        cur.execute(_CREATE_EXTENSION)
        cur.execute(_CREATE_TABLE)
        cur.execute(_CREATE_TEXT_INDEX)
        # IVFFlat index requires at least 1 row; skip on empty table
        cur.execute("SELECT COUNT(*) FROM content_chunks;")
        count = cur.fetchone()[0]
        if count > 0:
            cur.execute(_CREATE_INDEX)
        else:
            print(
                "  [db] Skipping IVFFlat index creation on empty table "
                "(will be created after first upsert)."
            )
    conn.commit()
    print("  [db] Schema ready — content_chunks table OK.")


def ensure_ivfflat_index(conn) -> None:
    """Create IVFFlat index after data is loaded (requires rows to exist)."""
    with conn.cursor() as cur:
        cur.execute(_CREATE_INDEX)
    conn.commit()
    print("  [db] IVFFlat index created/verified.")


# ---------------------------------------------------------------------------
# Chunk ID
# ---------------------------------------------------------------------------

def make_chunk_id(document_name: str, chunk_index: int) -> str:
    """Deterministic, stable identifier for upsert idempotency."""
    raw = f"{document_name}::{chunk_index}"
    return hashlib.sha256(raw.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Upsert
# ---------------------------------------------------------------------------

def upsert_chunks(
    conn,
    chunks: list,          # list[Chunk] — avoid circular import with TYPE_CHECKING
    embeddings: list[list[float]],
    batch_size: int = 50,
) -> int:
    """
    Bulk upsert chunks + embeddings into content_chunks.

    Uses ON CONFLICT (chunk_id) DO UPDATE so re-runs are safe.
    Returns the number of rows upserted.
    """
    if len(chunks) != len(embeddings):
        raise ValueError(
            f"chunks ({len(chunks)}) and embeddings ({len(embeddings)}) must have equal length."
        )

    upsert_sql = """
        INSERT INTO content_chunks
            (chunk_id, document_name, page_start, page_end,
             chapter_section, chunk_text, token_count, embedding)
        VALUES %s
        ON CONFLICT (chunk_id) DO UPDATE SET
            document_name   = EXCLUDED.document_name,
            page_start      = EXCLUDED.page_start,
            page_end        = EXCLUDED.page_end,
            chapter_section = EXCLUDED.chapter_section,
            chunk_text      = EXCLUDED.chunk_text,
            token_count     = EXCLUDED.token_count,
            embedding       = EXCLUDED.embedding;
    """

    total = len(chunks)
    upserted = 0

    with conn.cursor() as cur:
        for batch_start in range(0, total, batch_size):
            batch_chunks = chunks[batch_start : batch_start + batch_size]
            batch_embeds = embeddings[batch_start : batch_start + batch_size]

            rows = []
            for chunk, vector in zip(batch_chunks, batch_embeds):
                chunk_id = make_chunk_id(chunk.document_name, chunk.chunk_index)
                # pgvector accepts Python list as '[f1,f2,...]' string
                embedding_str = "[" + ",".join(f"{v:.8f}" for v in vector) + "]"
                rows.append((
                    chunk_id,
                    chunk.document_name,
                    chunk.page_start,
                    chunk.page_end,
                    chunk.chapter_section,
                    chunk.text,
                    chunk.token_count,
                    embedding_str,
                ))

            if _HAS_PSYCOPG2 and hasattr(psycopg2, "extras"):
                psycopg2.extras.execute_values(cur, upsert_sql, rows)
            else:
                single_upsert_sql = """
                    INSERT INTO content_chunks
                        (chunk_id, document_name, page_start, page_end,
                         chapter_section, chunk_text, token_count, embedding)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (chunk_id) DO UPDATE SET
                        document_name   = EXCLUDED.document_name,
                        page_start      = EXCLUDED.page_start,
                        page_end        = EXCLUDED.page_end,
                        chapter_section = EXCLUDED.chapter_section,
                        chunk_text      = EXCLUDED.chunk_text,
                        token_count     = EXCLUDED.token_count,
                        embedding       = EXCLUDED.embedding;
                """
                for row in rows:
                    cur.execute(single_upsert_sql, row)
            upserted += len(rows)
            batch_end = min(batch_start + batch_size, total)
            print(
                f"  [db] Upserted {batch_end}/{total} chunks ...",
                end="\r",
                flush=True,
            )

    conn.commit()
    print(f"\n  [db] Upsert complete — {upserted} rows written to content_chunks.")
    return upserted


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------

def verify(conn) -> dict:
    """
    Return a summary dict for the ingest_verify CLI.

    Keys
    ----
    total_chunks        : total rows in content_chunks
    total_with_embedding: rows where embedding IS NOT NULL
    missing_embeddings  : rows where embedding IS NULL
    embedding_dimension : length of a sample embedding vector (or None)
    documents           : list of distinct document_names
    """
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM content_chunks;")
        total = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM content_chunks WHERE embedding IS NOT NULL;")
        with_emb = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM content_chunks WHERE embedding IS NULL;")
        missing = cur.fetchone()[0]

        # Dimension from a live row
        dim = None
        cur.execute(
            "SELECT ARRAY_LENGTH(embedding::real[], 1) "
            "FROM content_chunks WHERE embedding IS NOT NULL LIMIT 1;"
        )
        row = cur.fetchone()
        if row:
            dim = row[0]

        cur.execute("SELECT DISTINCT document_name FROM content_chunks;")
        docs = [r[0] for r in cur.fetchall()]

    return {
        "total_chunks": total,
        "total_with_embedding": with_emb,
        "missing_embeddings": missing,
        "embedding_dimension": dim,
        "documents": docs,
    }


def get_sample_chunks(conn, n: int = 3) -> list[dict]:
    """Retrieve N sample rows (without the full embedding vector) for display."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT chunk_id, document_name, page_start, page_end,
                   chapter_section, token_count,
                   LEFT(chunk_text, 200) AS text_preview
            FROM content_chunks
            ORDER BY page_start
            LIMIT %s;
            """,
            (n,),
        )
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]
