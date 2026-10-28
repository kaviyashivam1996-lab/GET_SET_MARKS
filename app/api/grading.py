"""
app/api/grading.py
------------------
Standalone AI Written Answer Grading API endpoint.
"""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel
from rag.evaluator import evaluate_written_answer

router = APIRouter(prefix="/grade", tags=["AI Grading"])

class GradeWrittenRequest(BaseModel):
    question_text: str
    model_answer: str
    student_answer: str
    rubric_points: list[dict]
    max_marks: float = 5.0

@router.post("/written")
async def grade_written_answer(req: GradeWrittenRequest):
    """
    Directly evaluates a written answer using board-rubric strictness rules.
    Returns per-rubric point hit/miss analysis, score clamping status, and feedback.
    """
    return evaluate_written_answer(
        question_text=req.question_text,
        model_answer=req.model_answer,
        student_answer=req.student_answer,
        rubric_points=req.rubric_points,
        max_marks=req.max_marks
    )
