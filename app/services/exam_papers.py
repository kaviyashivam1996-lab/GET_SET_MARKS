"""
app/services/exam_papers.py
----------------------------
Official Tamil Nadu State Board Class 10 Exam Blueprint Paper Generator:
Supports:
  1. Midterm Exam (1st / 2nd Midterm):
     - Duration: 90 mins (5400s)
     - Total Marks: 50 Marks
     - Section A: 7 MCQs (7 x 1m = 7m)
     - Section B: 5 Two-Mark Questions (5 x 2m = 10m)
     - Section C: 5 Five-Mark Questions (5 x 5m = 25m)
     - Section D: 1 Eight-Mark Practical/Geometry Question (1 x 8m = 8m)
     - Syllabus: 2 - 3 Initial Units/Chapters
  2. Quarterly Exam:
     - Duration: 150 mins (9000s) / 180 mins
     - Total Marks: 100 Marks
     - Section A: 14 MCQs (14 x 1m = 14m)
     - Section B: 10 Two-Mark Questions (10 x 2m = 20m)
     - Section C: 10 Five-Mark Questions (10 x 5m = 50m)
     - Section D: 2 Eight-Mark Questions (2 x 8m = 16m)
     - Syllabus: Units 1 to 4 (Term 1)
  3. Half-Yearly Exam:
     - Duration: 180 mins (10800s)
     - Total Marks: 100 Marks
     - Section A: 14 MCQs (14 x 1m = 14m)
     - Section B: 10 Two-Mark Questions (10 x 2m = 20m)
     - Section C: 10 Five-Mark Questions (10 x 5m = 50m)
     - Section D: 2 Eight-Mark Questions (2 x 8m = 16m)
     - Syllabus: Units 1 to 6/7 (Comprehensive Mid-Session)
"""
from __future__ import annotations

import random
from typing import Any
from ingestion.db import get_connection
from app.services.vector_questions import get_chunks_for_chapter, extract_qa_from_chunks

EXAM_CONFIGS = {
    "midterm": {
        "title": "Class 10 State Board Mid-Term Examination",
        "duration_sec": 5400, # 1 hr 30 mins
        "total_marks": 50,
        "mcq_count": 7,
        "two_mark_count": 5,
        "five_mark_count": 5,
        "eight_mark_count": 1,
        "chapter_slice": 3 # First 3 chapters
    },
    "quarterly": {
        "title": "Class 10 State Board Quarterly Examination",
        "duration_sec": 9000, # 2 hrs 30 mins
        "total_marks": 100,
        "mcq_count": 14,
        "two_mark_count": 10,
        "five_mark_count": 10,
        "eight_mark_count": 2,
        "chapter_slice": 4 # First 4 chapters
    },
    "half_yearly": {
        "title": "Class 10 State Board Half-Yearly Examination",
        "duration_sec": 10800, # 3 hours
        "total_marks": 100,
        "mcq_count": 14,
        "two_mark_count": 10,
        "five_mark_count": 10,
        "eight_mark_count": 2,
        "chapter_slice": 7 # Units 1 to 7
    }
}

def generate_board_exam_paper(subject_id: str, exam_category: str = "quarterly") -> dict[str, Any]:
    """
    Fetches official chapters for standard 10th stateboard and assembles
    the complete paper with MCQs, 2-marks, 5-marks, and 8-marks.
    """
    category = exam_category.lower().replace("-", "_").replace(" ", "_")
    if category not in EXAM_CONFIGS:
        category = "quarterly"

    config = EXAM_CONFIGS[category]
    conn = get_connection()

    chapters = []
    subject_name = "Mathematics"
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT name FROM subjects WHERE id = %s;", (subject_id,))
            srow = cur.fetchone()
            if srow:
                subject_name = srow[0]

            cur.execute("""
                SELECT id, title, chapter_order
                FROM chapters
                WHERE subject_id = %s
                ORDER BY chapter_order;
            """, (subject_id,))
            chapters = cur.fetchall()
    finally:
        conn.close()

    if not chapters:
        # Fallback to standard 10th maths chapters
        chapters = [
            ("tn_10_mat_ch1", "Chapter 1: Relations and Functions", 1),
            ("tn_10_mat_ch2", "Chapter 2: Numbers and Sequences", 2),
            ("tn_10_mat_ch3", "Chapter 3: Algebra", 3),
            ("tn_10_mat_ch4", "Chapter 4: Geometry", 4),
            ("tn_10_mat_ch5", "Chapter 5: Coordinate Geometry", 5),
            ("tn_10_mat_ch6", "Chapter 6: Trigonometry", 6),
            ("tn_10_mat_ch7", "Chapter 7: Mensuration", 7),
            ("tn_10_mat_ch8", "Chapter 8: Statistics and Probability", 8),
        ]

    # Slice chapters according to exam syllabus scope
    syllabus_chapters = chapters[:config["chapter_slice"]]
    
    all_mcqs = []
    all_two_marks = []
    all_five_marks = []

    for cid, ctitle, _ in syllabus_chapters:
        # Retrieve chunks from pgvector
        chunks = get_chunks_for_chapter(cid, ctitle, limit=8)
        mcq_sub, short_sub, long_sub = extract_qa_from_chunks(
            cid, ctitle, chunks, target_mcq=5, target_short=4, target_long=3
        )
        all_mcqs.extend(mcq_sub)
        all_two_marks.extend(short_sub)
        all_five_marks.extend(long_sub)

    random.shuffle(all_mcqs)
    random.shuffle(all_two_marks)
    random.shuffle(all_five_marks)

    selected_mcqs = all_mcqs[:config["mcq_count"]]
    selected_twos = all_two_marks[:config["two_mark_count"]]
    selected_fives = all_five_marks[:config["five_mark_count"]]

    # Construct Section D (8-Mark Practical Geometry / Graph / Essay Questions)
    eight_marks = []
    for i in range(config["eight_mark_count"]):
        ch_ref = syllabus_chapters[i % len(syllabus_chapters)]
        eight_marks.append({
            "id": f"exam_8m_{i+1}",
            "question_type": "eight_mark",
            "question": f"Construct and demonstrate the comprehensive practical problem / theorem in {ch_ref[1]}: Provide the complete construction steps, verification proof, or analytical graph.",
            "model_answer": f"Detailed board step-by-step construction/solution for {ch_ref[1]}: 1. Given data & Rough diagram (2m), 2. Fair construction / step-by-step working (4m), 3. Calculation & concluding verification (2m).",
            "rubric_points": [
                {"description": "Given data, assumptions and rough sketch", "marks": 2.0},
                {"description": "Accurate construction / core mathematical derivation steps", "marks": 4.0},
                {"description": "Verification, final values, and unit conclusions", "marks": 2.0}
            ],
            "max_marks": 8.0,
            "source_page": "Board Blueprint Reference",
            "pdf_id": "Class_10_Textbook.pdf"
        })

    # Number questions sequentially
    q_counter = 1
    for m in selected_mcqs:
        m["serial_no"] = q_counter
        q_counter += 1

    for s in selected_twos:
        s["serial_no"] = q_counter
        s["max_marks"] = 2.0
        q_counter += 1

    for f in selected_fives:
        f["serial_no"] = q_counter
        f["max_marks"] = 5.0
        q_counter += 1

    for e in eight_marks:
        e["serial_no"] = q_counter
        q_counter += 1

    return {
        "title": f"{config['title']} — {subject_name}",
        "subject_name": subject_name,
        "exam_category": category,
        "duration_sec": config["duration_sec"],
        "total_marks": config["total_marks"],
        "syllabus_covered": [c[1] for c in syllabus_chapters],
        "section_a_mcqs": selected_mcqs,
        "section_b_two_marks": selected_twos,
        "section_c_five_marks": selected_fives,
        "section_d_eight_marks": eight_marks
    }
