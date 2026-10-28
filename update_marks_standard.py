import psycopg2
from ingestion.db import get_connection

def update_marks():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # 1. Update all Short Answer questions to exactly 2.0 marks
            cur.execute("""
                UPDATE answer_questions
                SET max_marks = 2.0,
                    rubric_points = jsonb_build_array(
                        jsonb_build_object('point_id', 'r1', 'description', 'Key factual point or principle identification', 'marks', 1.0),
                        jsonb_build_object('point_id', 'r2', 'description', 'Accurate scientific/contextual elaboration and outcome', 'marks', 1.0)
                    )
                WHERE question_type = 'short';
            """)

            # 2. Update all Long Answer questions to exactly 5.0 marks
            cur.execute("""
                UPDATE answer_questions
                SET max_marks = 5.0,
                    rubric_points = jsonb_build_array(
                        jsonb_build_object('point_id', 'r1', 'description', 'Concept definition, background context, or formula setup', 'marks', 1.0),
                        jsonb_build_object('point_id', 'r2', 'description', 'Core derivation, step-by-step reasoning, or plot mechanism', 'marks', 1.5),
                        jsonb_build_object('point_id', 'r3', 'description', 'Mathematical proof, scientific law application, or thematic analysis', 'marks', 1.5),
                        jsonb_build_object('point_id', 'r4', 'description', 'Conclusion, final units/significance, or takeaway', 'marks', 1.0)
                    )
                WHERE question_type = 'long';
            """)

            conn.commit()
            print("[x] Successfully standardized: Short Answers -> 2 Marks, Long Answers -> 5 Marks.")
    finally:
        conn.close()

if __name__ == "__main__":
    update_marks()
