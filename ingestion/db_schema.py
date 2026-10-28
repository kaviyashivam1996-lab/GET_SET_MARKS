"""
ingestion/db_schema.py
----------------------
Schema definition and creation script for Phase 2 & Phase 3 tables:
  - boards, classes, subjects, chapters, guides
  - mcq_questions, answer_questions (with JSONB rubrics & source_page tracking)
  - exam_attempts, evaluation_results
  - leaderboard_entries
  - parent_links
"""
from __future__ import annotations

from ingestion.db import get_connection

_CREATE_PHASE2_TABLES = """
-- 1. Taxonomy
CREATE TABLE IF NOT EXISTS boards (
    id VARCHAR(32) PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS classes (
    id VARCHAR(32) PRIMARY KEY,
    board_id VARCHAR(32) REFERENCES boards(id) ON DELETE CASCADE,
    label VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS subjects (
    id VARCHAR(64) PRIMARY KEY,
    board_id VARCHAR(32) REFERENCES boards(id) ON DELETE CASCADE,
    class_id VARCHAR(32) REFERENCES classes(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS chapters (
    id VARCHAR(64) PRIMARY KEY,
    subject_id VARCHAR(64) REFERENCES subjects(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    chapter_order INT DEFAULT 1,
    review_status VARCHAR(32) DEFAULT 'published'
);

CREATE TABLE IF NOT EXISTS guides (
    id VARCHAR(64) PRIMARY KEY,
    chapter_id VARCHAR(64) REFERENCES chapters(id) ON DELETE CASCADE,
    body_md TEXT NOT NULL,
    key_points TEXT[],
    review_status VARCHAR(32) DEFAULT 'published'
);

-- 2. Question Banks with Source Page Traceability
CREATE TABLE IF NOT EXISTS mcq_questions (
    id VARCHAR(64) PRIMARY KEY,
    chapter_id VARCHAR(64) REFERENCES chapters(id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    options JSONB NOT NULL, -- Array of 4 option strings
    correct_index INT NOT NULL,
    difficulty VARCHAR(20) DEFAULT 'medium',
    explanation TEXT,
    source_page VARCHAR(50) DEFAULT 'p. 1-10',
    pdf_id VARCHAR(100) DEFAULT '10th_English.pdf'
);

CREATE TABLE IF NOT EXISTS answer_questions (
    id VARCHAR(64) PRIMARY KEY,
    chapter_id VARCHAR(64) REFERENCES chapters(id) ON DELETE CASCADE,
    question_type VARCHAR(20) NOT NULL, -- 'short' or 'long'
    question TEXT NOT NULL,
    model_answer TEXT NOT NULL,
    rubric_points JSONB NOT NULL, -- Array of {point_id, description, marks}
    max_marks NUMERIC(4,1) NOT NULL,
    source_page VARCHAR(50) DEFAULT 'p. 1-10',
    pdf_id VARCHAR(100) DEFAULT '10th_English.pdf'
);

-- 3. Exam & Evaluation
CREATE TABLE IF NOT EXISTS exam_attempts (
    id VARCHAR(64) PRIMARY KEY,
    student_id VARCHAR(64) NOT NULL,
    student_name VARCHAR(100) DEFAULT 'Student',
    board_id VARCHAR(32) NOT NULL,
    class_id VARCHAR(32) NOT NULL,
    subject_id VARCHAR(64) NOT NULL,
    exam_type VARCHAR(20) DEFAULT 'full', -- 'mini' or 'full'
    started_at TIMESTAMPTZ NOT NULL,
    submitted_at TIMESTAMPTZ,
    duration_sec INT NOT NULL,
    violation_log JSONB DEFAULT '[]'::jsonb,
    score NUMERIC(5,2) DEFAULT 0.0,
    max_score NUMERIC(5,2) DEFAULT 0.0,
    status VARCHAR(32) DEFAULT 'in_progress'
);

CREATE TABLE IF NOT EXISTS evaluation_results (
    id VARCHAR(64) PRIMARY KEY,
    exam_attempt_id VARCHAR(64) REFERENCES exam_attempts(id) ON DELETE CASCADE,
    question_id VARCHAR(64) NOT NULL,
    question_text TEXT NOT NULL,
    student_answer TEXT NOT NULL,
    rubric_hits JSONB NOT NULL, -- Array of {point_id, description, hit: bool, marks: num, justification: str}
    marks_awarded NUMERIC(4,1) NOT NULL,
    max_marks NUMERIC(4,1) NOT NULL,
    feedback TEXT
);

-- 4. Leaderboard & Parent Links
CREATE TABLE IF NOT EXISTS leaderboard_entries (
    id VARCHAR(64) PRIMARY KEY,
    student_id VARCHAR(64) NOT NULL,
    student_name VARCHAR(100) NOT NULL,
    board_id VARCHAR(32) NOT NULL,
    class_id VARCHAR(32) NOT NULL,
    total_score NUMERIC(7,2) DEFAULT 0.0,
    exams_completed INT DEFAULT 0,
    accuracy_pct NUMERIC(5,2) DEFAULT 0.0,
    rank INT DEFAULT 0,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS parent_links (
    id VARCHAR(64) PRIMARY KEY,
    parent_id VARCHAR(64) NOT NULL,
    parent_name VARCHAR(100) NOT NULL,
    student_id VARCHAR(64) NOT NULL,
    link_code VARCHAR(10) UNIQUE NOT NULL,
    status VARCHAR(32) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
"""

def create_schema():
    print("Creating Phase 2 & 3 schema tables with Source Page Traceability in PostgreSQL...")
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(_CREATE_PHASE2_TABLES)
            # Alter existing tables if source_page/pdf_id columns do not exist
            cur.execute("ALTER TABLE mcq_questions ADD COLUMN IF NOT EXISTS source_page VARCHAR(50) DEFAULT 'p. 1-10';")
            cur.execute("ALTER TABLE mcq_questions ADD COLUMN IF NOT EXISTS pdf_id VARCHAR(100) DEFAULT '10th_English.pdf';")
            cur.execute("ALTER TABLE answer_questions ADD COLUMN IF NOT EXISTS source_page VARCHAR(50) DEFAULT 'p. 1-10';")
            cur.execute("ALTER TABLE answer_questions ADD COLUMN IF NOT EXISTS pdf_id VARCHAR(100) DEFAULT '10th_English.pdf';")
        conn.commit()
        print("Schema tables updated successfully!")
    finally:
        conn.close()

if __name__ == "__main__":
    create_schema()
