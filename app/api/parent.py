"""
app/api/parent.py
-----------------
Parent Dashboard & Link Code API.
"""
from __future__ import annotations

import random
import string
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ingestion.db import get_connection

router = APIRouter(prefix="/parent", tags=["Parent Dashboard"])

class GenerateLinkRequest(BaseModel):
    parent_id: str = "par_501"
    parent_name: str = "Sundar R."
    student_id: str = "stu_101"

class RedeemLinkRequest(BaseModel):
    parent_id: str
    parent_name: str
    link_code: str

@router.post("/link/generate")
async def generate_parent_link(req: GenerateLinkRequest):
    """Generates a 6-character link code for a student to give to their parent."""
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO parent_links (id, parent_id, parent_name, student_id, link_code, status)
                VALUES (%s, %s, %s, %s, %s, 'active');
            """, (f"pl_{code}", req.parent_id, req.parent_name, req.student_id, code))
        conn.commit()
        return {"link_code": code, "status": "active"}
    finally:
        conn.close()

@router.get("/students/{student_id}/progress")
async def get_student_progress(student_id: str):
    """
    Returns parent progress overview:
      - Completed mock exams & average score
      - Anti-cheat violations count
      - Accuracy trend
    Note: Respects student privacy by excluding raw RAG chat logs.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*), COALESCE(AVG(score), 0), COALESCE(AVG(max_score), 0)
                FROM exam_attempts
                WHERE student_id = %s AND status = 'completed';
            """, (student_id,))
            exam_stats = cur.fetchone()
            completed_count = exam_stats[0] if exam_stats else 0
            avg_score = float(exam_stats[1]) if exam_stats else 0.0
            avg_max = float(exam_stats[2]) if exam_stats else 0.0

            cur.execute("""
                SELECT total_score, accuracy_pct, rank FROM leaderboard_entries WHERE student_id = %s LIMIT 1;
            """, (student_id,))
            lb_row = cur.fetchone()
            rank_val = lb_row[2] if lb_row else "N/A"
            accuracy = float(lb_row[1]) if lb_row else 0.0

            return {
                "student_id": student_id,
                "exams_completed": completed_count,
                "avg_score": round(avg_score, 1),
                "avg_max_score": round(avg_max, 1),
                "average_percentage": round((avg_score / avg_max * 100), 1) if avg_max > 0 else 0.0,
                "overall_accuracy_pct": accuracy,
                "leaderboard_rank": rank_val,
                "privacy_mode": "Chat logs hidden per minor privacy policy"
            }
    finally:
        conn.close()
