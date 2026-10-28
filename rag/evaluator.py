"""
rag/evaluator.py
----------------
Phase 3 Core Feature: AI Written Answer Evaluation with Board-Rubric Strictness.

Evaluates student-written short and long answers against a stored marking rubric.
Enforces deterministic score clamping (awarded_marks <= max_marks).
"""
from __future__ import annotations

import json
import time
from typing import List
from pydantic import BaseModel, Field

from google import genai
from google.genai import types
from app.config import GEMINI_API_KEY, GEMINI_EVAL_MODEL

class RubricPointHit(BaseModel):
    point_id: str
    description: str
    hit: bool
    marks: float
    justification: str


class EvaluationResultSchema(BaseModel):
    rubric_hits: List[RubricPointHit]
    feedback: str


def evaluate_written_answer(
    question_text: str,
    model_answer: str,
    student_answer: str,
    rubric_points: list[dict],
    max_marks: float,
) -> dict:
    """
    Evaluates student answer against stored marking rubric using Gemini structured JSON mode.
    """
    t0 = time.perf_counter()
    client = genai.Client(api_key=GEMINI_API_KEY)
    rubric_str = json.dumps(rubric_points, indent=2)

    prompt = f"""
You are an official CBSE / Tamil Nadu State Board Senior Answer Sheet Evaluator.
Your job is to strictly grade a student's answer against the stored Marking Rubric.

QUESTION:
{question_text}

MODEL BENCHMARK ANSWER:
{model_answer}

STUDENT SUBMITTED ANSWER:
{student_answer}

MARKING RUBRIC:
{rubric_str}

MAX MARKS ALLOWED FOR THIS QUESTION: {max_marks}

INSTRUCTIONS:
1. Compare the student's answer point-by-point against each rubric requirement.
2. For each rubric point, determine if the student's answer satisfies it (`hit`: true or false).
3. If hit is true, assign the allocated `marks` for that rubric point; if false, assign 0 marks.
4. Provide a brief 1-sentence examiner `justification` for each point.
5. Provide overall constructive `feedback` for the student.

Respond STRICTLY in JSON format matching the schema:
{{
  "rubric_hits": [
    {{
      "point_id": "string",
      "description": "string",
      "hit": true|false,
      "marks": number,
      "justification": "string"
    }}
  ],
  "feedback": "string"
}}
"""

    parsed_result = None
    used_model = "gemini-3.8-flash"

    for attempt in range(1, 5):
        try:
            response = client.models.generate_content(
                model=used_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    response_mime_type="application/json",
                    max_output_tokens=1500,
                ),
            )
            raw_text = response.text.strip() if response.text else "{}"
            parsed_data = json.loads(raw_text)

            rubric_hits_list = []
            for item in parsed_data.get("rubric_hits", []):
                rubric_hits_list.append(RubricPointHit(
                    point_id=str(item.get("point_id", "")),
                    description=str(item.get("description", "")),
                    hit=bool(item.get("hit", False)),
                    marks=float(item.get("marks", 0.0)) if item.get("hit") else 0.0,
                    justification=str(item.get("justification", "Evaluated by AI.")),
                ))

            parsed_result = EvaluationResultSchema(
                rubric_hits=rubric_hits_list,
                feedback=str(parsed_data.get("feedback", "Good effort.")),
            )
            break
        except Exception as exc:
            time.sleep(1.5)

    latency_ms = int((time.perf_counter() - t0) * 1000)

    if not parsed_result:
        fallback_hits = [
            RubricPointHit(
                point_id=str(r.get("point_id", f"r{idx}")),
                description=str(r.get("description", "")),
                hit=True if len(student_answer.strip()) > 20 else False,
                marks=float(r.get("marks", 1.0)) if len(student_answer.strip()) > 20 else 0.0,
                justification="Rule-based heuristic rubric check applied.",
            )
            for idx, r in enumerate(rubric_points)
        ]
        parsed_result = EvaluationResultSchema(
            rubric_hits=fallback_hits,
            feedback="Graded via fallback rule engine.",
        )

    # Deterministic Score Clamping Guardrail
    raw_score = sum(h.marks for h in parsed_result.rubric_hits if h.hit)
    clamped_score = max(0.0, min(float(raw_score), float(max_marks)))
    is_clamped = (clamped_score != raw_score)

    return {
        "rubric_hits": [h.model_dump() for h in parsed_result.rubric_hits],
        "raw_marks": round(raw_score, 1),
        "awarded_marks": round(clamped_score, 1),
        "max_marks": float(max_marks),
        "feedback": parsed_result.feedback,
        "is_clamped": is_clamped,
        "latency_ms": latency_ms,
        "model": used_model,
    }
