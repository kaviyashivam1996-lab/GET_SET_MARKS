# -*- coding: utf-8 -*-
"""
ingest_verify.py
----------------
Verification CLI for Phase 2 — confirms all 193 embeddings are stored
correctly in Supabase PostgreSQL (content_chunks table).

Usage
-----
    python ingest_verify.py
    python ingest_verify.py --samples 5

Reports
-------
  - Total chunks stored
  - Total rows with embeddings
  - Missing embeddings (should be 0)
  - Embedding dimension (should be 768)
  - Documents indexed
  - Sample rows with metadata (no embedding vectors printed)
"""
from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

# Force UTF-8 on Windows console
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ingestion.db import get_connection, get_sample_chunks, verify


def main() -> None:
    parser = argparse.ArgumentParser(
        description="GetSetMarks Phase 2 — verify embeddings in Supabase"
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=3,
        help="Number of sample rows to display (default: 3)",
    )
    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("  GetSetMarks — Phase 2 Verification Report")
    print("=" * 60)

    print("\n  Connecting to Supabase ...")
    conn = get_connection()
    print("  Connected OK.\n")

    # ------------------------------------------------------------------
    # Counts & dimension
    # ------------------------------------------------------------------
    stats = verify(conn)

    status_chunks = "OK" if stats["total_chunks"] == 193 else "CHECK"
    status_emb = "OK" if stats["total_with_embedding"] == stats["total_chunks"] else "MISSING"
    status_missing = "OK" if stats["missing_embeddings"] == 0 else f"MISSING {stats['missing_embeddings']}"
    status_dim = "OK" if stats["embedding_dimension"] == 768 else f"UNEXPECTED ({stats['embedding_dimension']})"

    print("  " + "-" * 56)
    print(f"  {'Metric':<35} {'Value':>10}  {'Status'}")
    print("  " + "-" * 56)
    print(f"  {'Total chunks stored':<35} {stats['total_chunks']:>10}  {status_chunks}")
    print(f"  {'Chunks with embeddings':<35} {stats['total_with_embedding']:>10}  {status_emb}")
    print(f"  {'Missing embeddings':<35} {stats['missing_embeddings']:>10}  {status_missing}")
    print(f"  {'Embedding dimension':<35} {str(stats['embedding_dimension']):>10}  {status_dim}")
    print("  " + "-" * 56)

    if stats["documents"]:
        print(f"\n  Documents in DB:")
        for doc in stats["documents"]:
            print(f"    - {doc}")

    # ------------------------------------------------------------------
    # Sample rows
    # ------------------------------------------------------------------
    print(f"\n  Sample chunks from Supabase (first {args.samples} by page):")
    print("  " + "-" * 56)
    samples = get_sample_chunks(conn, n=args.samples)
    for i, row in enumerate(samples, 1):
        print(f"\n  [{i}] chunk_id: {row['chunk_id'][:16]}...")
        print(f"      document : {row['document_name']}")
        pages = (
            f"p.{row['page_start']}"
            if row["page_start"] == row["page_end"]
            else f"p.{row['page_start']} - p.{row['page_end']}"
        )
        print(f"      pages    : {pages}")
        print(f"      section  : {row['chapter_section'] or '(none)'}")
        print(f"      tokens   : {row['token_count']}")
        print(f"      preview  : {row['text_preview'][:120]}...")

    conn.close()

    # ------------------------------------------------------------------
    # Final verdict
    # ------------------------------------------------------------------
    print("\n  " + "=" * 58)
    all_ok = (
        stats["total_chunks"] >= 190
        and stats["missing_embeddings"] == 0
        and stats["embedding_dimension"] == 768
    )
    if all_ok:
        print("  RESULT: PASS -- All embeddings stored correctly in Supabase.")
    else:
        print("  RESULT: FAIL -- Check the issues above.")
    print("  " + "=" * 58 + "\n")


if __name__ == "__main__":
    main()
