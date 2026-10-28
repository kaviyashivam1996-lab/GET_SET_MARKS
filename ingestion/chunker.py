"""
ingestion/chunker.py
---------------------
Token-aware sliding-window chunker for the GetSetMarks ingestion pipeline.

Strategy
--------
1. Concatenate all PageContent items into a flat sequence of (text, page_number,
   chapter_section) segments, preserving page boundaries as markers.
2. Tokenise the full text with tiktoken (cl100k_base — same tokeniser used by
   most embedding models, no LLM call required).
3. Slide a window of TARGET tokens across the token sequence, stepping by
   (TARGET − OVERLAP) tokens each time.
4. For each window, decode back to text and record:
   - page_start / page_end (the pages that contribute tokens to this window)
   - chapter_section (the heading active at the *start* of the window)
5. Never cut mid-sentence: after finding the nominal window end, walk back to
   the nearest sentence boundary ('. ', '? ', '! ', '.\n').

Phase 1: returns list[Chunk] — no embedding, no DB write.
Phase 2: caller passes chunks to the embedding + pgvector storage step.
"""
from __future__ import annotations

import re
from typing import NamedTuple

try:
    import tiktoken
except (ImportError, Exception):
    tiktoken = None

class _FallbackEncoding:
    """Fallback word-level encoding when tiktoken C-extension cannot be loaded."""
    def __init__(self):
        self._pattern = re.compile(r"\w+|[^\w\s]|\s+")
        self._str_to_id: dict[str, int] = {}
        self._id_to_str: dict[int, str] = {}
        self._next_id = 1

    def encode(self, text: str) -> list[int]:
        tokens: list[int] = []
        for match in self._pattern.finditer(text):
            tok_str = match.group(0)
            tok_id = self._str_to_id.get(tok_str)
            if tok_id is None:
                tok_id = self._next_id
                self._next_id += 1
                self._str_to_id[tok_str] = tok_id
                self._id_to_str[tok_id] = tok_str
            tokens.append(tok_id)
        return tokens

    def decode(self, token_ids: list[int]) -> str:
        return "".join(self._id_to_str.get(tid, "") for tid in token_ids)


def _get_encoding(encoding_name: str = "cl100k_base"):
    if tiktoken is not None:
        try:
            return tiktoken.get_encoding(encoding_name)
        except Exception:
            pass
    return _FallbackEncoding()

from .models import Chunk, PageContent

# ---------------------------------------------------------------------------
# Internal token-level data structure
# ---------------------------------------------------------------------------
class _TokenRecord(NamedTuple):
    """Metadata attached to each token in the document stream."""
    token_id: int
    page_number: int
    chapter_section: str | None


# ---------------------------------------------------------------------------
# Sentence boundary helpers
# ---------------------------------------------------------------------------
_SENTENCE_END = re.compile(r"(?<=[.?!])\s+")


def _find_sentence_boundary(text: str, preferred_end: int) -> int:
    """
    Starting from ``preferred_end``, walk *backwards* to the nearest sentence
    boundary.  Returns a character index (exclusive end of last sentence).
    Falls back to ``preferred_end`` if no boundary is found within 200 chars.
    """
    search_start = max(0, preferred_end - 200)
    segment = text[search_start:preferred_end]
    # Find all sentence-end positions within the segment
    boundaries = [m.end() + search_start for m in _SENTENCE_END.finditer(segment)]
    if boundaries:
        return boundaries[-1]
    # Fallback: look for a newline paragraph break
    nl_pos = segment.rfind("\n\n")
    if nl_pos != -1:
        return nl_pos + search_start + 2
    return preferred_end


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def chunk_pages(
    pages: list[PageContent],
    document_name: str,
    target_tokens: int = 650,
    overlap_tokens: int = 100,
    encoding_name: str = "cl100k_base",
) -> list[Chunk]:
    """
    Chunk a list of PageContent objects into token-bounded Chunk objects.

    Parameters
    ----------
    pages           : Extracted pages from extractor.extract_pages().
    document_name   : Source PDF filename (stored in every Chunk).
    target_tokens   : Desired chunk size in tokens (default 650).
    overlap_tokens  : Number of tokens to overlap between adjacent chunks (default 100).
    encoding_name   : tiktoken encoding to use (default "cl100k_base").

    Returns
    -------
    list[Chunk]
        Chunks in document order, each with full metadata.
    """
    enc = _get_encoding(encoding_name)
    step = target_tokens - overlap_tokens

    # -----------------------------------------------------------------------
    # Step 1: Build a flat token stream with per-token metadata
    # -----------------------------------------------------------------------
    token_records: list[_TokenRecord] = []

    for page in pages:
        if not page.raw_text.strip():
            continue  # skip blank pages

        page_tokens = enc.encode(page.raw_text)
        for tok_id in page_tokens:
            token_records.append(
                _TokenRecord(
                    token_id=tok_id,
                    page_number=page.page_number,
                    chapter_section=page.detected_heading,
                )
            )

    if not token_records:
        return []

    total_tokens = len(token_records)
    print(
        f"  [chunker] {total_tokens:,} total tokens | "
        f"target={target_tokens} overlap={overlap_tokens} step={step}"
    )

    # -----------------------------------------------------------------------
    # Step 2: Slide the window
    # -----------------------------------------------------------------------
    chunks: list[Chunk] = []
    start = 0

    while start < total_tokens:
        end = min(start + target_tokens, total_tokens)
        window = token_records[start:end]

        # Decode the window to text
        raw_text = enc.decode([r.token_id for r in window])

        # Trim to nearest sentence boundary (avoid cutting mid-sentence)
        # Only apply when we're not at the very end of the document
        if end < total_tokens:
            trimmed_text = raw_text[: _find_sentence_boundary(raw_text, len(raw_text))]
            # Re-encode trimmed text to get accurate token count
            trimmed_tokens = enc.encode(trimmed_text)
            actual_token_count = len(trimmed_tokens)
        else:
            trimmed_text = raw_text
            actual_token_count = len(window)

        trimmed_text = trimmed_text.strip()
        if not trimmed_text:
            start += step
            continue

        # Metadata from the first token in the window
        page_start = window[0].page_number
        page_end = window[-1].page_number
        chapter_section = window[0].chapter_section

        chunks.append(
            Chunk(
                document_name=document_name,
                page_start=page_start,
                page_end=page_end,
                chapter_section=chapter_section,
                token_count=actual_token_count,
                char_count=len(trimmed_text),
                text=trimmed_text,
                chunk_index=len(chunks),
            )
        )

        start += step

    print(f"  [chunker] Produced {len(chunks):,} chunks")
    return chunks
