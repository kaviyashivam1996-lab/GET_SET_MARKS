# -*- coding: utf-8 -*-
"""
ingest_embed.py
---------------
Phase 2 CLI: Extract chunks (Phase 1) -> Generate embeddings -> Store in Supabase pgvector.

Usage
-----
    python ingest_embed.py
    python ingest_embed.py --pdf data/10th_English.pdf
    python ingest_embed.py --dry-run   # skip DB write, just show embedding stats

Flow
----
1. Run Phase 1 pipeline  -> list[Chunk]
2. Load sentence-transformer model (all-mpnet-base-v2, 768 dims)
3. Embed all chunk texts in batches of 32
4. Ensure content_chunks table + IVFFlat index exist in Supabase
5. Bulk upsert all chunks + embeddings (idempotent via chunk_id)
6. Print summary report

No API key required.
No embeddings are hardcoded.
No secrets are logged.
"""
from __future__ import annotations

import argparse
import io
import sys
import time
from pathlib import Path

# Force UTF-8 on Windows console
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ingestion.db import ensure_ivfflat_index, ensure_table, get_connection, upsert_chunks
from ingestion.embedder import embed_chunks, get_embedder
from ingestion.pipeline import run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(
        description="GetSetMarks Phase 2 — embed chunks and store in Supabase pgvector"
    )
    parser.add_argument(
        "--pdf",
        default="data/10th_English.pdf",
        help="Path to PDF (default: data/10th_English.pdf)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run extraction + embedding but skip writing to the database",
    )
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    if not pdf_path.is_absolute():
        pdf_path = Path(__file__).resolve().parent / pdf_path

    t_start = time.time()

    # ------------------------------------------------------------------
    # Step 1: Phase 1 — extract + chunk
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("  Phase 2 — Embedding + pgvector Storage")
    print("=" * 60)

    chunks = run_pipeline(pdf_path)
    print(f"\n  [phase2] Phase 1 produced {len(chunks)} chunks.")

    # ------------------------------------------------------------------
    # Step 2: Generate embeddings
    # ------------------------------------------------------------------
    print("\n  [phase2] Loading embedding model ...")
    model = get_embedder()

    texts = [c.text for c in chunks]
    print(f"  [phase2] Generating {len(texts)} embeddings ...")
    embeddings = embed_chunks(texts, model=model)

    # Validate dimensions
    dims = set(len(v) for v in embeddings)
    if len(dims) != 1:
        print(f"  [phase2] ERROR: inconsistent embedding dims: {dims}")
        sys.exit(1)
    dim = dims.pop()
    print(f"  [phase2] Embedding dim: {dim} | Total: {len(embeddings)}")

    if args.dry_run:
        print("\n  [phase2] --dry-run flag set: skipping database write.")
        print(f"  [phase2] Would store {len(embeddings)} x {dim}-dim vectors.")
        elapsed = time.time() - t_start
        print(f"\n  Dry-run completed in {elapsed:.1f}s")
        return

    # ------------------------------------------------------------------
    # Step 3: Store in Supabase
    # ------------------------------------------------------------------
    print("\n  [phase2] Connecting to Supabase ...")
    conn = get_connection()
    print("  [phase2] Connected OK.")

    print("  [phase2] Ensuring schema (table + indexes) ...")
    ensure_table(conn)

    print(f"  [phase2] Upserting {len(chunks)} chunks into content_chunks ...")
    upserted = upsert_chunks(conn, chunks, embeddings)

    # Build IVFFlat index after data is loaded (requires rows to exist)
    print("  [phase2] Building IVFFlat index ...")
    ensure_ivfflat_index(conn)

    conn.close()

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    elapsed = time.time() - t_start
    print("\n" + "=" * 60)
    print("  PHASE 2 COMPLETE")
    print("=" * 60)
    print(f"  Chunks produced   : {len(chunks)}")
    print(f"  Embeddings stored : {upserted}")
    print(f"  Embedding dim     : {dim}")
    print(f"  Model             : all-mpnet-base-v2 (local, no API key)")
    print(f"  Storage           : Supabase PostgreSQL + pgvector")
    print(f"  Table             : public.content_chunks")
    print(f"  Elapsed           : {elapsed:.1f}s")
    print("=" * 60)
    print("\n  Next step: run `python ingest_verify.py` to confirm all 193 embeddings.")
    print()


if __name__ == "__main__":
    main()
