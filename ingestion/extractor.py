"""
ingestion/extractor.py
----------------------
Extracts text from PDF pages using PyMuPDF (fitz) and detects
chapter/section headings common in Tamil Nadu State Board textbooks.

Heading patterns supported (10th English TN Board):
  - UNIT 1 / Unit 1 / UNIT I
  - PROSE / POEM / SUPPLEMENTARY READER
  - ALL-CAPS lines that look like section titles
  - Lines starting with Roman numerals (I. II. III.)

Phase 1: extraction only — no embeddings, no DB, no LLM.
"""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import fitz  # PyMuPDF

from .models import PageContent

# ---------------------------------------------------------------------------
# Heading detection patterns (ordered by specificity)
# ---------------------------------------------------------------------------
_HEADING_PATTERNS: list[re.Pattern[str]] = [
    # "UNIT 1", "Unit 1", "UNIT I", "Unit I"
    re.compile(r"^\s*(UNIT\s+[\dIVXivx]+)\s*$", re.IGNORECASE | re.MULTILINE),
    # "1. UNIT NAME" or "UNIT 1: NAME"
    re.compile(r"^\s*(UNIT\s+[\dIVXivx]+[\s:–\-]+[A-Z][A-Z\s]+)\s*$", re.MULTILINE),
    # Section type headers
    re.compile(
        r"^\s*(PROSE|POEM|POETRY|SUPPLEMENTARY\s+READER?|GRAMMAR|"
        r"VOCABULARY|READING\s+COMPREHENSION|WRITING|SPEAKING|LISTENING)\s*$",
        re.IGNORECASE | re.MULTILINE,
    ),
    # All-caps line of 4–60 chars (title-like)
    re.compile(r"^\s*([A-Z][A-Z\s\-']{3,59}[A-Z])\s*$", re.MULTILINE),
]

# Lines to skip during cleaning (page numbers, watermarks, headers/footers)
_NOISE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"^\s*\d+\s*$"),                         # lone page number
    re.compile(r"www\.tntextbooks\.in", re.IGNORECASE), # watermark
    re.compile(r"^\s*[_\-=]{3,}\s*$"),                  # divider lines
    re.compile(r"^\s*$"),                                # blank lines (handled separately)
]


def _collapse_vertical_text(text: str) -> str:
    """
    Collapse vertically-rendered letters into words.
    TN board PDFs sometimes render decorative section titles one character
    per line, e.g.:  E\nM\nP\nO\nW\nE\nR\nE\nD  → EMPOWERED
    """
    import re as _re
    # Match runs of 3+ single-character lines (letters only)
    pattern = _re.compile(r"(?m)^([A-Z])\n(?=[A-Z]\n|[A-Z]$)")

    def _join_run(text: str) -> str:
        lines = text.split("\n")
        result: list[str] = []
        i = 0
        while i < len(lines):
            # Collect a run of single-letter lines
            run: list[str] = []
            while i < len(lines) and len(lines[i].strip()) == 1 and lines[i].strip().isalpha():
                run.append(lines[i].strip())
                i += 1
            if len(run) >= 3:
                result.append("".join(run))
            else:
                result.extend(run)
                i += len(run) - len(run)  # already advanced
        # Fill back any non-run lines
        # Simpler: just do the join inline
        return text  # handled below

    # Simpler approach: replace runs of single-letter lines
    lines = text.split("\n")
    result: list[str] = []
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if len(stripped) == 1 and stripped.isalpha():
            run = [stripped]
            j = i + 1
            while j < len(lines) and len(lines[j].strip()) == 1 and lines[j].strip().isalpha():
                run.append(lines[j].strip())
                j += 1
            if len(run) >= 3:
                result.append("".join(run))
                i = j
            else:
                result.append(lines[i])
                i += 1
        else:
            result.append(lines[i])
            i += 1
    return "\n".join(result)


def _clean_text(raw: str) -> str:
    """
    Normalise unicode, remove ligatures/artifacts, collapse excessive whitespace.
    Preserves paragraph breaks (double newlines).
    """
    # Normalise unicode (handles ligatures like fi → fi)
    text = unicodedata.normalize("NFKC", raw)

    # Collapse vertically-rendered decorative letters (TN board artifact)
    text = _collapse_vertical_text(text)

    # Remove lines matching noise patterns
    lines = text.splitlines()
    cleaned_lines: list[str] = []
    for line in lines:
        if any(pat.match(line) for pat in _NOISE_PATTERNS):
            continue
        cleaned_lines.append(line.rstrip())

    # Collapse 3+ consecutive blank lines → single blank line
    result_lines: list[str] = []
    blank_run = 0
    for line in cleaned_lines:
        if line.strip() == "":
            blank_run += 1
            if blank_run <= 1:
                result_lines.append("")
        else:
            blank_run = 0
            result_lines.append(line)

    return "\n".join(result_lines).strip()


def _detect_heading(text: str) -> str | None:
    """
    Try each heading pattern against the page text.
    Returns the first match (stripped), or None.
    """
    for pattern in _HEADING_PATTERNS:
        match = pattern.search(text)
        if match:
            candidate = match.group(1).strip()
            # Reject if it's just a very short noise word
            if len(candidate) >= 3:
                return candidate
    return None


def extract_pages(pdf_path: str | Path) -> list[PageContent]:
    """
    Open ``pdf_path`` and extract text from every page.

    Parameters
    ----------
    pdf_path : str or Path
        Absolute path to the source PDF.

    Returns
    -------
    list[PageContent]
        One item per page, in document order.
        Pages with no extractable text are included with empty raw_text.
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    pages: list[PageContent] = []

    with fitz.open(str(pdf_path)) as doc:
        total_pages = len(doc)
        print(f"  [extractor] Opened '{pdf_path.name}' — {total_pages} pages")

        # Track the last known heading across pages (headings persist until
        # a new one is detected, matching textbook section structure)
        last_heading: str | None = None

        for page_index in range(total_pages):
            page = doc[page_index]
            raw = page.get_text("text")  # plain text extraction
            cleaned = _clean_text(raw)

            heading = _detect_heading(cleaned)
            if heading:
                last_heading = heading  # update running heading

            pages.append(
                PageContent(
                    page_number=page_index + 1,  # 1-indexed
                    raw_text=cleaned,
                    detected_heading=last_heading,  # carry forward
                )
            )

    return pages
