"""
ingestion/pipeline.py
---------------------
Orchestrates the full Phase 1 ingestion pipeline:
    PDF → extract_pages() → chunk_pages() → list[Chunk]

Configuration is read from environment variables (via .env) so no secrets
are hardcoded.  Falls back to sensible defaults if variables are not set.

Phase 2 hook: callers receive list[Chunk] and can pass it directly to the
embedding + pgvector storage step without any changes to this module.
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

from .chunker import chunk_pages
from .extractor import extract_pages
from .models import Chunk

# Load .env from the backend root (two levels up from this file)
_ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(_ENV_PATH)


def run_pipeline(
    pdf_path: str | Path,
    document_name: str | None = None,
) -> list[Chunk]:
    """
    Run the full extraction + chunking pipeline on a single PDF.

    Parameters
    ----------
    pdf_path      : Path to the PDF file.
    document_name : Optional override for the document name stored in each
                    Chunk.  Defaults to the PDF filename.

    Returns
    -------
    list[Chunk]
        All chunks in document order, ready for Phase 2 embedding.
    """
    pdf_path = Path(pdf_path)
    doc_name = document_name or pdf_path.name

    # Read chunking config from .env (with defaults matching the PRD)
    target_tokens = int(os.getenv("CHUNK_TARGET_TOKENS", "650"))
    overlap_tokens = int(os.getenv("CHUNK_OVERLAP_TOKENS", "100"))

    print(f"\n{'='*60}")
    print(f"  GetSetMarks Ingestion Pipeline — Phase 1")
    print(f"  Document : {doc_name}")
    print(f"  PDF path : {pdf_path}")
    print(f"  Target   : {target_tokens} tokens/chunk | overlap: {overlap_tokens}")
    print(f"{'='*60}\n")

    # Step 1: Extract text page by page
    pages = extract_pages(pdf_path)

    total_chars = sum(p.char_count for p in pages)
    total_words = sum(p.word_count for p in pages)
    non_empty = sum(1 for p in pages if p.raw_text.strip())
    headings_found = {p.detected_heading for p in pages if p.detected_heading}

    print(f"\n  [pipeline] Extraction complete:")
    print(f"    Pages total    : {len(pages)}")
    print(f"    Pages with text: {non_empty}")
    print(f"    Total chars    : {total_chars:,}")
    print(f"    Total words    : {total_words:,}")
    print(f"    Unique headings: {len(headings_found)}")
    print()

    # Step 2: Chunk
    chunks = chunk_pages(
        pages=pages,
        document_name=doc_name,
        target_tokens=target_tokens,
        overlap_tokens=overlap_tokens,
    )

    return chunks
