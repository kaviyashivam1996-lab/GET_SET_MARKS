"""
app/api/exam.py
----------------
Timed Mock Exam Engine with anti-cheat proctoring log & AI answer evaluation.
"""
from __future__ import annotations

import json
import time
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ingestion.db import get_connection
from rag.evaluator import evaluate_written_answer

router = APIRouter(prefix="/exam", tags=["Exam & Proctoring"])

class StartExamRequest(BaseModel):
    student_id: str = "stu_101"
    student_name: str = "Kavya R."
    board_id: str = "TN_STATE"
    class_id: str = "tn_class_10"
    subject_id: str = "tn_10_english"
    exam_type: str = "full"
    duration_sec: int = 1800  # 30 mins

class ViolationSignal(BaseModel):
    event_type: str  # e.g., 'tab_switch', 'window_blur', 'fullscreen_exit', 'copy_attempt'
    timestamp_ms: int

class SubmitExamRequest(BaseModel):
    mcq_answers: dict[str, int]  # question_id -> chosen_index
    written_answers: dict[str, str]  # question_id -> text_answer

@router.post("/start")
async def start_exam(req: StartExamRequest):
    """
    Creates a new timed exam attempt record and returns exam questions (without answers).
    Server clock records authoritative start time.
    """
    exam_id = f"exam_{uuid.uuid4().hex[:10]}"
    now_iso = datetime.now(timezone.utc).isoformat()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Create attempt
            cur.execute("""
                INSERT INTO exam_attempts
                (id, student_id, student_name, board_id, class_id, subject_id, exam_type, started_at, duration_sec, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'in_progress');
            """, (exam_id, req.student_id, req.student_name, req.board_id, req.class_id, req.subject_id, req.exam_type, now_iso, req.duration_sec))

            # Fetch MCQs
            cur.execute("""
                SELECT mq.id, mq.question, mq.options
                FROM mcq_questions mq
                JOIN chapters c ON mq.chapter_id = c.id
                WHERE c.subject_id = %s LIMIT 5;
            """, (req.subject_id,))
            mcq_rows = cur.fetchall()
            mcqs = []
            for r in mcq_rows:
                opts = r[2] if isinstance(r[2], list) else json.loads(r[2])
                mcqs.append({"id": r[0], "question": r[1], "options": opts})

            # Fetch Written
            cur.execute("""
                SELECT aq.id, aq.question_type, aq.question, aq.max_marks
                FROM answer_questions aq
                JOIN chapters c ON aq.chapter_id = c.id
                WHERE c.subject_id = %s LIMIT 2;
            """, (req.subject_id,))
            written_rows = cur.fetchall()
            written = []
            for r in written_rows:
                written.append({"id": r[0], "type": r[1], "question": r[2], "max_marks": float(r[3])})

        conn.commit()
        return {
            "exam_id": exam_id,
            "started_at": now_iso,
            "duration_sec": req.duration_sec,
            "mcqs": mcqs,
            "written_questions": written,
        }
    finally:
        conn.close()

@router.post("/{exam_id}/violation")
async def log_violation(exam_id: str, signal: ViolationSignal):
    """
    Logs an anti-cheat proctoring event (tab switch, focus loss, fullscreen exit)
    to the server-side violation_log JSONB column for this attempt.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT violation_log FROM exam_attempts WHERE id = %s;", (exam_id,))
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Exam attempt not found.")

            current_log = row[0] if isinstance(row[0], list) else (json.loads(row[0]) if row[0] else [])
            current_log.append(signal.model_dump())

            cur.execute("""
                UPDATE exam_attempts
                SET violation_log = %s
                WHERE id = %s;
            """, (json.dumps(current_log), exam_id))
        conn.commit()
        return {"status": "ok", "total_violations": len(current_log)}
    finally:
        conn.close()

@router.post("/{exam_id}/submit")
async def submit_exam(exam_id: str, req: SubmitExamRequest):
    """
    Submits student exam answers:
      1. Scores MCQs deterministically against stored answer key.
      2. Runs written answers through the Board-Rubric Strict AI Evaluator.
      3. Clamps awarded scores to max marks.
      4. Stores evaluation records & updates student score in leaderboard.
    """
    now_iso = datetime.now(timezone.utc).isoformat()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT student_id, student_name, board_id, class_id, subject_id, started_at, violation_log
                FROM exam_attempts WHERE id = %s AND status = 'in_progress';
            """, (exam_id,))
            attempt = cur.fetchone()
            if not attempt:
                raise HTTPException(status_code=400, detail="Exam attempt not found or already submitted.")

            student_id, student_name, board_id, class_id, subject_id, started_at, viol_log = attempt
            violations = viol_log if isinstance(viol_log, list) else (json.loads(viol_log) if viol_log else [])

            total_score = 0.0
            max_score = 0.0
            mcq_results = []
            written_evaluations = []

            # 1. Evaluate MCQs
            for mcq_id, chosen_idx in req.mcq_answers.items():
                cur.execute("SELECT question, correct_index, explanation FROM mcq_questions WHERE id = %s;", (mcq_id,))
                r = cur.fetchone()
                if r:
                    q_text, correct_idx, expl = r
                    max_score += 1.0
                    is_correct = (chosen_idx == correct_idx)
                    score = 1.0 if is_correct else 0.0
                    total_score += score
                    mcq_results.append({
                        "question_id": mcq_id,
                        "question": q_text,
                        "chosen_index": chosen_idx,
                        "correct_index": correct_idx,
                        "is_correct": is_correct,
                        "score": score,
                        "explanation": expl
                    })

            # 2. Evaluate Written Answers via AI Evaluator
            for written_id, student_text in req.written_answers.items():
                cur.execute("""
                    SELECT question, model_answer, rubric_points, max_marks
                    FROM answer_questions WHERE id = %s;
                """, (written_id,))
                r = cur.fetchone()
                if r:
                    q_text, model_ans, rubrics, q_max = r
                    rubric_list = rubrics if isinstance(rubrics, list) else json.loads(rubrics)
                    q_max_float = float(q_max)
                    max_score += q_max_float

                    eval_res = evaluate_written_answer(
                        question_text=q_text,
                        model_answer=model_ans,
                        student_answer=student_text,
                        rubric_points=rubric_list,
                        max_marks=q_max_float
                    )

                    awarded = eval_res["awarded_marks"]
                    total_score += awarded

                    # Save evaluation_result
                    eval_id = f"eval_{uuid.uuid4().hex[:8]}"
                    cur.execute("""
                        INSERT INTO evaluation_results
                        (id, exam_attempt_id, question_id, question_text, student_answer, rubric_hits, marks_awarded, max_marks, feedback)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                    """, (
                        eval_id, exam_id, written_id, q_text, student_text,
                        json.dumps(eval_res["rubric_hits"]), awarded, q_max_float, eval_res["feedback"]
                    ))

                    written_evaluations.append({
                        "question_id": written_id,
                        "question": q_text,
                        "student_answer": student_text,
                        "model_answer": model_ans,
                        "awarded_marks": awarded,
                        "max_marks": q_max_float,
                        "rubric_hits": eval_res["rubric_hits"],
                        "feedback": eval_res["feedback"],
                        "is_clamped": eval_res["is_clamped"]
                    })

            # 3. Update exam attempt record
            cur.execute("""
                UPDATE exam_attempts
                SET submitted_at = %s, score = %s, max_score = %s, status = 'completed'
                WHERE id = %s;
            """, (now_iso, total_score, max_score, exam_id))

            # 4. Update Leaderboard Entry
            cur.execute("""
                INSERT INTO leaderboard_entries
                (id, student_id, student_name, board_id, class_id, total_score, exams_completed, accuracy_pct)
                VALUES (%s, %s, %s, %s, %s, %s, 1, %s)
                ON CONFLICT (id) DO UPDATE SET
                total_score = leaderboard_entries.total_score + EXCLUDED.total_score,
                exams_completed = leaderboard_entries.exams_completed + 1,
                accuracy_pct = (leaderboard_entries.total_score + EXCLUDED.total_score) / (leaderboard_entries.exams_completed + 1),
                updated_at = CURRENT_TIMESTAMP;
            """, (
                f"lb_{student_id}", student_id, student_name, board_id, class_id,
                total_score, (total_score / max_score * 100) if max_score > 0 else 0
            ))

        conn.commit()
        return {
            "exam_id": exam_id,
            "status": "completed",
            "score": total_score,
            "max_score": max_score,
            "score_percentage": round((total_score / max_score * 100), 1) if max_score > 0 else 0.0,
            "violations_count": len(violations),
            "mcq_results": mcq_results,
            "written_evaluations": written_evaluations
        }
    finally:
        conn.close()
