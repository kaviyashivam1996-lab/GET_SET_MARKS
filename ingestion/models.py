"""
ingestion/models.py
-------------------
Pure data models for the GetSetMarks ingestion pipeline.
No database dependencies — these are plain Python dataclasses.

Phase 1: PDF extraction + chunking only.
Phase 2 (next): add pgvector storage using these same models.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PageContent:
    """
    Raw text extracted from a single PDF page.

    Attributes
    ----------
    page_number     : 1-indexed page number from the PDF.
    raw_text        : Cleaned text content of the page.
    detected_heading: The chapter/section heading detected on this page,
                      or None if no heading was found.
    char_count      : Number of characters in raw_text.
    word_count      : Approximate word count of raw_text.
    """
    page_number: int
    raw_text: str
    detected_heading: str | None = None

    @property
    def char_count(self) -> int:
        return len(self.raw_text)

    @property
    def word_count(self) -> int:
        return len(self.raw_text.split())

    def __repr__(self) -> str:
        heading = f'"{self.detected_heading}"' if self.detected_heading else "None"
        return (
            f"PageContent(page={self.page_number}, "
            f"heading={heading}, "
            f"chars={self.char_count}, words={self.word_count})"
        )


@dataclass
class Chunk:
    """
    A single text chunk ready for embedding in Phase 2.

    Attributes
    ----------
    document_name   : Filename of the source PDF (e.g. "10th_English.pdf").
    page_start      : First page (1-indexed) this chunk spans.
    page_end        : Last page (1-indexed) this chunk spans.
    chapter_section : Detected heading at the time of chunking, or None.
    token_count     : Number of tokens (tiktoken cl100k_base).
    char_count      : Number of characters in text.
    text            : The actual chunk text.
    chunk_index     : Zero-based global index across all chunks in the document.
    """
    document_name: str
    page_start: int
    page_end: int
    chapter_section: str | None
    token_count: int
    char_count: int
    text: str
    chunk_index: int = 0

    def summary(self) -> str:
        """Single-line summary for inspection output."""
        pages = (
            f"p.{self.page_start}"
            if self.page_start == self.page_end
            else f"p.{self.page_start}–{self.page_end}"
        )
        section = self.chapter_section or "—"
        return (
            f"[Chunk #{self.chunk_index:04d}] {pages} | "
            f"{self.token_count} tokens | {section}"
        )

    def __repr__(self) -> str:
        return self.summary()
