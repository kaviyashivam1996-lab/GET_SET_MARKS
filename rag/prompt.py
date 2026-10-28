"""
rag/prompt.py
-------------
Phase 3 Step 2: Build the prompt sent to Gemini.

Structure
---------
  [SYSTEM]
  You are GetSetMarks AI, a helpful tutor for Tamil Nadu State Board students
  (Classes 9-12). Answer ONLY from the context provided below...

  [CONTEXT]
  --- Chunk 1 (10th_English.pdf, p.23-24, Chapter 2) ---
  <text>
  ...

  [USER QUESTION]
  <question>
"""
from __future__ import annotations

from rag.retriever import RetrievedChunk

_SYSTEM_PROMPT = """You are GetSetMarks AI, an expert tutor for Tamil Nadu State Board students (Classes 9‒12).

RULES:
1. Answer ONLY using the context passages provided below.
2. If the answer is not found in the context, say: "I couldn't find this in the provided textbook content."
3. Be concise, clear, and student-friendly.
4. Cite the page number(s) when relevant (e.g., "As mentioned on page 23...").
5. Do NOT hallucinate facts not in the context.
6. If the question is in Tamil, respond in Tamil.
"""


def build_prompt(question: str, chunks: list[RetrievedChunk]) -> tuple[str, int]:
    """
    Assemble the full prompt string and estimate token count.

    Returns
    -------
    (prompt_text, estimated_tokens)
    """
    context_parts: list[str] = []

    for i, chunk in enumerate(chunks, 1):
        pages = (
            f"p.{chunk.page_start}"
            if chunk.page_start == chunk.page_end
            else f"p.{chunk.page_start}–{chunk.page_end}"
        )
        section = f", {chunk.chapter_section}" if chunk.chapter_section else ""
        header = f"--- Context {i} ({chunk.document_name}, {pages}{section}) ---"
        context_parts.append(f"{header}\n{chunk.text}")

    context_block = "\n\n".join(context_parts) if context_parts else "(No context retrieved.)"

    prompt = (
        f"{_SYSTEM_PROMPT}\n\n"
        f"=== TEXTBOOK CONTEXT ===\n{context_block}\n\n"
        f"=== STUDENT QUESTION ===\n{question}"
    )

    # Rough token estimate: ~4 chars per token
    estimated_tokens = len(prompt) // 4

    return prompt, estimated_tokens


def get_prompt_preview(prompt: str, max_chars: int = 400) -> str:
    """Return the first max_chars of the prompt for display in the frontend."""
    if len(prompt) <= max_chars:
        return prompt
    return prompt[:max_chars] + "..."
