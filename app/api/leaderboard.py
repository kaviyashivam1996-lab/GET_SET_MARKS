"""
app/api/leaderboard.py
----------------------
Board & Class partitioned Leaderboard API.
"""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel
from ingestion.db import get_connection

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])

class LeaderboardEntryResponse(BaseModel):
    rank: int
    student_id: str
    student_name: str
    board_id: str
    class_id: str
    total_score: float
    exams_completed: int
    accuracy_pct: float

@router.get("/{board_id}/{class_id}", response_model=list[LeaderboardEntryResponse])
async def get_leaderboard(board_id: str, class_id: str, limit: int = 20):
    """
    Returns top ranked students partitioned strictly by board and class.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT student_id, student_name, board_id, class_id, total_score, exams_completed, accuracy_pct
                FROM leaderboard_entries
                WHERE board_id = %s AND class_id = %s
                ORDER BY total_score DESC, accuracy_pct DESC
                LIMIT %s;
            """, (board_id, class_id, limit))
            rows = cur.fetchall()
            results = []
            for rank_idx, r in enumerate(rows, start=1):
                results.append(LeaderboardEntryResponse(
                    rank=rank_idx,
                    student_id=r[0],
                    student_name=r[1],
                    board_id=r[2],
                    class_id=r[3],
                    total_score=float(r[4]),
                    exams_completed=r[5],
                    accuracy_pct=float(r[6])
                ))
            return results
    finally:
        conn.close()
