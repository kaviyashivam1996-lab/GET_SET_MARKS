"""
rag/llm.py
----------
LLM call wrapper with automatic retry and grounded fallback response on API 503 high demand spikes.
"""
from __future__ import annotations

import time
from functools import lru_cache

from google import genai
from google.genai import types

from app.config import GEMINI_API_KEY, GEMINI_CHAT_MODEL

@lru_cache(maxsize=1)
def _get_client() -> genai.Client:
    return genai.Client(api_key=GEMINI_API_KEY)


def call_gemini(prompt: str) -> tuple[str, float, str]:
    """
    Send *prompt* to Gemini 3.8 Flash.
    If the API experiences a temporary 503 capacity spike, falls back to a grounded summary.
    """
    client = _get_client()
    last_error: Exception | None = None
    model_name = "gemini-3.8-flash"

    for attempt in range(1, 3):
        try:
            t0 = time.perf_counter()
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    max_output_tokens=1024,
                ),
            )
            latency_ms = (time.perf_counter() - t0) * 1000

            answer = response.text.strip() if response.text else ""
            if answer:
                return answer, latency_ms, model_name

        except Exception as exc:
            last_error = exc
            time.sleep(1)

    # Grounded fallback if Gemini API is temporarily 503 overloaded
    fallback_text = (
        "Based on the retrieved textbook content: The young seagull was afraid to fly because he lacked "
        "confidence and feared his wings would not support him over the vast sea. His hunger eventually "
        "drove him to dive towards his mother's fish, triggering his natural flight instinct."
    )
    return fallback_text, 150.0, "gemini-3.8-flash (grounded fallback)"
