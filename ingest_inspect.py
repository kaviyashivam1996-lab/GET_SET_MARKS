# -*- coding: utf-8 -*-
"""
ingest_inspect.py
-----------------
CLI inspector for the GetSetMarks Phase 1 ingestion pipeline.

Usage
-----
    python ingest_inspect.py
    python ingest_inspect.py --pdf data/10th_English.pdf
    python ingest_inspect.py --pdf data/10th_English.pdf --show 10
    python ingest_inspect.py --pdf data/10th_English.pdf --export chunks.json

Output
------
  • Pipeline stats (pages, chars, words, chunks)
  • Chapter/section distribution table
  • First N chunks with full metadata and text preview
  • Optional JSON export of all chunks (for manual review)

This script does NOT:
  - Generate embeddings
  - Call any LLM
  - Write to the database
"""
from __future__ import annotations

import argparse
import io
import json
import sys
import textwrap

# Force UTF-8 output on Windows (avoids cp1252 UnicodeEncodeError)
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from collections import Counter
from pathlib import Path

# Ensure backend/ is on sys.path when run from any working directory
sys.path.insert(0, str(Path(__file__).resolve().parent))

from ingestion.pipeline import run_pipeline


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _separator(char: str = "-", width: int = 70) -> str:
    return char * width


def _print_chunk(chunk, show_full: bool = False) -> None:
    """Pretty-print a single chunk with metadata and text preview."""
    print(_separator())
    print(f"  Chunk #{chunk.chunk_index:04d}")
    print(f"  Document     : {chunk.document_name}")

    pages = (
        f"p.{chunk.page_start}"
        if chunk.page_start == chunk.page_end
        else f"p.{chunk.page_start} – p.{chunk.page_end}"
    )
    print(f"  Pages        : {pages}")
    print(f"  Chapter/Sec  : {chunk.chapter_section or '— (not detected)'}")
    print(f"  Tokens       : {chunk.token_count}")
    print(f"  Characters   : {chunk.char_count:,}")
    print()

    if show_full:
        text_display = chunk.text
    else:
        # Show first 400 chars, trimmed at word boundary
        text_display = textwrap.shorten(chunk.text, width=400, placeholder=" [...]")

    # Indent text block
    for line in text_display.splitlines():
        print(f"    {line}")
    print()


def _print_section_table(chunks) -> None:
    """Print a frequency table of chapter/section headings."""
    counter: Counter[str] = Counter()
    for c in chunks:
        key = c.chapter_section or "— (no heading)"
        counter[key] += 1

    print("\n  Chapter / Section Distribution")
    print(_separator("─", 70))
    print(f"  {'Section':<45} {'Chunks':>6}")
    print(_separator("─", 70))
    for section, count in counter.most_common():
        label = (section[:43] + "..") if len(section) > 45 else section
        print(f"  {label:<45} {count:>6}")
    print(_separator("─", 70))
    print(f"  {'TOTAL':<45} {sum(counter.values()):>6}")
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="GetSetMarks Phase 1 — PDF ingestion inspector"
    )
    parser.add_argument(
        "--pdf",
        default="data/10th_English.pdf",
        help="Path to the PDF file (default: data/10th_English.pdf)",
    )
    parser.add_argument(
        "--show",
        type=int,
        default=5,
        help="Number of chunks to display in detail (default: 5)",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Show full chunk text instead of 400-char preview",
    )
    parser.add_argument(
        "--export",
        metavar="FILE",
        default=None,
        help="Export all chunks to a JSON file for manual review",
    )
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    if not pdf_path.is_absolute():
        # Resolve relative to the script's directory (backend/)
        pdf_path = Path(__file__).resolve().parent / pdf_path

    # Run pipeline
    chunks = run_pipeline(pdf_path)

    if not chunks:
        print("\n  ⚠  No chunks produced — check that the PDF has extractable text.")
        return

    # -----------------------------------------------------------------------
    # Summary stats
    # -----------------------------------------------------------------------
    total_tokens = sum(c.token_count for c in chunks)
    avg_tokens = total_tokens / len(chunks)
    min_tokens = min(c.token_count for c in chunks)
    max_tokens = max(c.token_count for c in chunks)

    print("\n" + _separator("="))
    print("  INSPECTION REPORT")
    print(_separator("="))
    print(f"  Total chunks     : {len(chunks):,}")
    print(f"  Total tokens     : {total_tokens:,}")
    print(f"  Avg tokens/chunk : {avg_tokens:.0f}")
    print(f"  Min tokens/chunk : {min_tokens}")
    print(f"  Max tokens/chunk : {max_tokens}")
    print(f"  Pages spanned    : p.{chunks[0].page_start} → p.{chunks[-1].page_end}")
    print()

    # Section distribution
    _print_section_table(chunks)

    # -----------------------------------------------------------------------
    # First N chunks
    # -----------------------------------------------------------------------
    n = min(args.show, len(chunks))
    print(f"\n  First {n} Chunks (of {len(chunks):,} total)")
    print(_separator("="))
    for chunk in chunks[:n]:
        _print_chunk(chunk, show_full=args.full)

    # -----------------------------------------------------------------------
    # Optional JSON export
    # -----------------------------------------------------------------------
    if args.export:
        export_path = Path(args.export)
        export_data = [
            {
                "chunk_index": c.chunk_index,
                "document_name": c.document_name,
                "page_start": c.page_start,
                "page_end": c.page_end,
                "chapter_section": c.chapter_section,
                "token_count": c.token_count,
                "char_count": c.char_count,
                "text": c.text,
            }
            for c in chunks
        ]
        with open(export_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        print(f"\n  ✓ All {len(chunks):,} chunks exported → {export_path}")

    print(_separator("="))
    print("  Phase 1 complete. Next: run Phase 2 to generate embeddings.")
    print(_separator("=") + "\n")


if __name__ == "__main__":
    main()
