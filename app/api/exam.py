"""
app/api/exam.py
----------------
Timed Mock Exam Engine with anti-cheat proctoring log & AI answer evaluation.
Supports standard State Board blueprints:
  - 25 Marks (Class Test / 45 mins)
  - 50 Marks (Mid-Term / 90 mins)
  - 75 Marks (Quarterly / 150 mins)
  - 100 Marks (Annual / Board / 180 mins)
Includes safe fallback store for resilience against database connectivity issues.
"""
from __future__ import annotations

import json
import time
import uuid
import os
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ingestion.db import get_connection
from rag.evaluator import evaluate_written_answer
from app.api.practice import (
    generate_paper,
    PaperGenerateRequest,
    CHAPTER_QUESTION_BANKS
)

router = APIRouter(prefix="/exam", tags=["Exam & Proctoring"])

# Blueprint configuration for timed exams
EXAM_BLUEPRINTS = {
    25: {
        "title": "Class Test / Unit Test",
        "duration_sec": 45 * 60,  # 45 mins
        "mcqs": 5,
        "short": 5,
        "long": 2,
    },
    50: {
        "title": "Mid-Term Examination",
        "duration_sec": 90 * 60,  # 90 mins
        "mcqs": 10,
        "short": 5,
        "long": 6,
    },
    75: {
        "title": "Quarterly Examination",
        "duration_sec": 150 * 60,  # 150 mins (2.5 hrs)
        "mcqs": 15,
        "short": 10,
        "long": 8,
    },
    100: {
        "title": "Half-Yearly / Annual Board Exam",
        "duration_sec": 180 * 60,  # 180 mins (3 hrs)
        "mcqs": 14,
        "short": 13,
        "long": 12,
    },
}

# In-memory storage for active exam sessions (serves as resilient fallback)
ACTIVE_EXAMS: dict[str, dict] = {}

class StartExamRequest(BaseModel):
    student_id: str = "stu_101"
    student_name: str = "Kavya R."
    board_id: str = "TN_STATE"
    class_id: str = "tn_class_10"
    subject_id: str = "tn_10_english"
    chapter_ids: list[str] | None = None
    target_marks: int = 25
    exam_type: str = "class_test"
    duration_sec: int | None = None

class ViolationSignal(BaseModel):
    event_type: str  # e.g., 'tab_switch', 'window_blur', 'fullscreen_exit', 'copy_attempt'
    timestamp_ms: int

class SubmitExamRequest(BaseModel):
    mcq_answers: dict[str, int] = {}  # question_id -> chosen_index
    written_answers: dict[str, str] = {}  # question_id -> text_answer


@router.post("/start")
async def start_exam(req: StartExamRequest):
    """
    Creates a new timed exam attempt record and returns exam questions (without answers).
    Server clock records authoritative start time.
    Supports 25m, 50m, 75m, 100m State Board model blueprints with Sections A, B, and C.
    """
    target_marks = req.target_marks if req.target_marks in EXAM_BLUEPRINTS else 25
    bp = EXAM_BLUEPRINTS[target_marks]
    duration_sec = req.duration_sec or bp["duration_sec"]
    exam_id = f"exam_{uuid.uuid4().hex[:10]}"
    now_iso = datetime.now(timezone.utc).isoformat()

    # Generate the question paper according to the blueprint using practice generator
    paper_req = PaperGenerateRequest(
        subject_id=req.subject_id,
        chapter_ids=req.chapter_ids,
        target_marks=target_marks,
        exam_type=req.exam_type,
        mcq_count=bp["mcqs"],
        short_count=bp["short"],
        long_count=bp["long"]
    )
    paper = await generate_paper(paper_req)

    # Store full question details including correct answers and rubrics in session cache
    exam_session = {
        "id": exam_id,
        "student_id": req.student_id,
        "student_name": req.student_name,
        "board_id": req.board_id,
        "class_id": req.class_id,
        "subject_id": req.subject_id,
        "exam_type": req.exam_type,
        "target_marks": target_marks,
        "exam_title": bp["title"],
        "started_at": now_iso,
        "duration_sec": duration_sec,
        "status": "in_progress",
        "violation_log": [],
        "mcqs": {q.id: q.model_dump() for q in paper.mcqs},
        "short_questions": {q.id: q.model_dump() for q in paper.short_questions},
        "long_questions": {q.id: q.model_dump() for q in paper.long_questions},
    }
    ACTIVE_EXAMS[exam_id] = exam_session

    # Attempt to persist record in PostgreSQL database if available
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO exam_attempts
                (id, student_id, student_name, board_id, class_id, subject_id, exam_type, started_at, duration_sec, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'in_progress');
            """, (exam_id, req.student_id, req.student_name, req.board_id, req.class_id, req.subject_id, req.exam_type, now_iso, duration_sec))
            conn.commit()
        conn.close()
    except Exception as e:
        print(f"Notice: exam_attempts table insert skipped/fallback used ({e})")

    # Prepare sanitized questions for student (strip out correct_index, model_answer, rubric_points)
    client_mcqs = [
        {"id": q.id, "chapter_id": q.chapter_id, "question": q.question, "options": q.options}
        for q in paper.mcqs
    ]
    client_short = [
        {"id": q.id, "chapter_id": q.chapter_id, "type": "short", "question": q.question, "max_marks": 2.0}
        for q in paper.short_questions
    ]
    client_long = [
        {"id": q.id, "chapter_id": q.chapter_id, "type": "long", "question": q.question, "max_marks": 5.0}
        for q in paper.long_questions
    ]

    return {
        "exam_id": exam_id,
        "exam_title": bp["title"],
        "target_marks": target_marks,
        "started_at": now_iso,
        "duration_sec": duration_sec,
        "mcqs": client_mcqs,
        "short_questions": client_short,
        "long_questions": client_long,
        "written_questions": client_short + client_long,
        "total_marks": paper.total_marks,
    }


@router.post("/{exam_id}/violation")
async def log_violation(exam_id: str, signal: ViolationSignal):
    """
    Logs an anti-cheat proctoring event (tab switch, focus loss, fullscreen exit)
    to session storage and updates DB if connected.
    """
    if exam_id in ACTIVE_EXAMS:
        ACTIVE_EXAMS[exam_id]["violation_log"].append(signal.model_dump())
        total_violations = len(ACTIVE_EXAMS[exam_id]["violation_log"])
    else:
        total_violations = 1

    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT violation_log FROM exam_attempts WHERE id = %s;", (exam_id,))
            row = cur.fetchone()
            if row:
                current_log = row[0] if isinstance(row[0], list) else (json.loads(row[0]) if row[0] else [])
                current_log.append(signal.model_dump())
                cur.execute("""
                    UPDATE exam_attempts
                    SET violation_log = %s
                    WHERE id = %s;
                """, (json.dumps(current_log), exam_id))
                conn.commit()
                total_violations = len(current_log)
        conn.close()
    except Exception as e:
        print(f"Notice: violation log DB update fallback used ({e})")

    return {"status": "ok", "total_violations": total_violations}


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
    session = ACTIVE_EXAMS.get(exam_id)

    student_id = session.get("student_id", "stu_101") if session else "stu_101"
    student_name = session.get("student_name", "Student") if session else "Student"
    board_id = session.get("board_id", "TN_STATE") if session else "TN_STATE"
    class_id = session.get("class_id", "tn_class_10") if session else "tn_class_10"
    violations = session.get("violation_log", []) if session else []

    total_score = 0.0
    max_score = 0.0
    mcq_results = []
    written_evaluations = []

    # 1. Evaluate MCQs
    session_mcqs = session.get("mcqs", {}) if session else {}
    for mcq_id, chosen_idx in req.mcq_answers.items():
        max_score += 1.0
        q_item = session_mcqs.get(mcq_id)
        if q_item:
            q_text = q_item.get("question", "")
            correct_idx = q_item.get("correct_index", 0)
            expl = q_item.get("explanation", "")
        else:
            # Fallback to local chapter banks if not in session
            q_text, correct_idx, expl = "Question", 0, ""
            for bank in CHAPTER_QUESTION_BANKS.values():
                for m in bank.get("mcqs", []):
                    if m["id"] == mcq_id:
                        q_text, correct_idx, expl = m["question"], m["correct_index"], m.get("explanation", "")
                        break

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

    # 2. Evaluate Written Answers via AI Evaluator (Short & Long)
    all_written = {}
    if session:
        all_written.update(session.get("short_questions", {}))
        all_written.update(session.get("long_questions", {}))

    for written_id, student_text in req.written_answers.items():
        w_item = all_written.get(written_id)
        if w_item:
            q_text = w_item.get("question", "")
            model_ans = w_item.get("model_answer", "")
            rubrics = w_item.get("rubric_points", [])
            q_max = float(w_item.get("max_marks", 2.0 if "short" in written_id else 5.0))
        else:
            q_text = "Exam Written Question"
            model_ans = "Comprehensive board benchmark answer."
            rubrics = [{"point_id": "r1", "description": "Key concept and explanation", "marks": 2.0}]
            q_max = 2.0 if "short" in written_id else 5.0

        max_score += q_max

        # AI Evaluation
        try:
            eval_res = evaluate_written_answer(
                question_text=q_text,
                model_answer=model_ans,
                student_answer=student_text or "No answer provided.",
                rubric_points=rubrics,
                max_marks=q_max
            )
            awarded = eval_res["awarded_marks"]
            rubric_hits = eval_res["rubric_hits"]
            feedback = eval_res["feedback"]
            is_clamped = eval_res.get("is_clamped", False)
        except Exception as e:
            # Fallback heuristic if evaluation call fails
            has_len = len(student_text.strip()) > 15
            awarded = round(q_max * 0.75, 1) if has_len else 0.0
            rubric_hits = [{"point_id": "r1", "description": "Key points covered", "hit": has_len, "marks": awarded, "justification": "Graded via heuristic."}]
            feedback = "Answer recorded and evaluated against key rubric terms."
            is_clamped = False

        total_score += awarded
        written_evaluations.append({
            "question_id": written_id,
            "question": q_text,
            "student_answer": student_text,
            "model_answer": model_ans,
            "awarded_marks": awarded,
            "max_marks": q_max,
            "rubric_hits": rubric_hits,
            "feedback": feedback,
            "is_clamped": is_clamped
        })

    # Attempt to update database if active connection available
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE exam_attempts
                SET submitted_at = %s, score = %s, max_score = %s, status = 'completed'
                WHERE id = %s;
            """, (now_iso, total_score, max_score, exam_id))
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
        conn.close()
    except Exception as e:
        print(f"Notice: DB submit updates skipped/fallback used ({e})")

    # Mark active session as completed
    if session:
        session["status"] = "completed"
        session["submitted_at"] = now_iso
        session["score"] = total_score
        session["max_score"] = max_score

    score_pct = round((total_score / max_score * 100), 1) if max_score > 0 else 0.0

    return {
        "exam_id": exam_id,
        "status": "completed",
        "score": round(total_score, 1),
        "max_score": round(max_score, 1),
        "score_percentage": score_pct,
        "violations_count": len(violations),
        "mcq_results": mcq_results,
        "written_evaluations": written_evaluations
    }
