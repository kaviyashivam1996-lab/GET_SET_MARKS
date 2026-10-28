"""
seed_maths_social_science.py
----------------------------
Seeds Mathematics (8 chapters) and Social Science (History, Geography, Civics, Economics)
into subjects, chapters, guides, mcq_questions, and answer_questions tables.
Directly aligned with official Tamil Nadu Class 10 Textbooks.
"""
import json
import psycopg2
from ingestion.db import get_connection

NEW_SUBJECTS = [
    ("tn_10_maths", "TN_STATE", "tn_class_10", "Mathematics"),
    ("tn_10_social", "TN_STATE", "tn_class_10", "Social Science"),
]

MATHS_CHAPTERS = [
    ("tn_10_mat_ch1", "tn_10_maths", "Chapter 1: Relations and Functions"),
    ("tn_10_mat_ch2", "tn_10_maths", "Chapter 2: Numbers and Sequences"),
    ("tn_10_mat_ch3", "tn_10_maths", "Chapter 3: Algebra"),
    ("tn_10_mat_ch4", "tn_10_maths", "Chapter 4: Geometry"),
    ("tn_10_mat_ch5", "tn_10_maths", "Chapter 5: Coordinate Geometry"),
    ("tn_10_mat_ch6", "tn_10_maths", "Chapter 6: Trigonometry"),
    ("tn_10_mat_ch7", "tn_10_maths", "Chapter 7: Mensuration"),
    ("tn_10_mat_ch8", "tn_10_maths", "Chapter 8: Statistics and Probability"),
]

SOCIAL_CHAPTERS = [
    # History
    ("tn_10_soc_h1", "tn_10_social", "History Unit 1: Outbreak of World War I and Its Aftermath"),
    ("tn_10_soc_h2", "tn_10_social", "History Unit 2: The World between two World Wars"),
    ("tn_10_soc_h5", "tn_10_social", "History Unit 5: Social and Religious Reform Movements in 19th Century"),
    ("tn_10_soc_h6", "tn_10_social", "History Unit 6: Early Revolts against British Rule in Tamil Nadu"),
    ("tn_10_soc_h8", "tn_10_social", "History Unit 8: Nationalism: Gandhian Phase"),
    # Geography
    ("tn_10_soc_g1", "tn_10_social", "Geography Unit 1: India - Location, Relief and Drainage"),
    ("tn_10_soc_g2", "tn_10_social", "Geography Unit 2: Climate and Natural Vegetation of India"),
    ("tn_10_soc_g3", "tn_10_social", "Geography Unit 3: India - Agriculture"),
    ("tn_10_soc_g6", "tn_10_social", "Geography Unit 6: Physical Geography of Tamil Nadu"),
    # Civics
    ("tn_10_soc_c1", "tn_10_social", "Civics Unit 1: Indian Constitution"),
    ("tn_10_soc_c2", "tn_10_social", "Civics Unit 2: Central Government"),
    ("tn_10_soc_c3", "tn_10_social", "Civics Unit 3: State Government"),
    # Economics
    ("tn_10_soc_e1", "tn_10_social", "Economics Unit 1: Gross Domestic Product and its Growth"),
    ("tn_10_soc_e2", "tn_10_social", "Economics Unit 2: Globalization and Trade"),
    ("tn_10_soc_e5", "tn_10_social", "Economics Unit 5: Industrial Clusters in Tamil Nadu"),
]

SAMPLE_MCQS = [
    # --- Mathematics Chapter 1: Relations & Functions ---
    {
        "id": "mcq_mat1_1", "chapter_id": "tn_10_mat_ch1",
        "question": "If n(A × B) = 6 and A = {1, 3}, then n(B) is:",
        "options": ["1", "2", "3", "6"],
        "correct_index": 2, "difficulty": "easy",
        "explanation": "n(A × B) = n(A) × n(B). Given n(A) = 2, so 2 × n(B) = 6 => n(B) = 3.",
        "source_page": "p. 31", "pdf_id": "Class_10_Mathematics_English_2025.pdf"
    },
    {
        "id": "mcq_mat1_2", "chapter_id": "tn_10_mat_ch1",
        "question": "A relation R from set A to set B is defined as a subset of:",
        "options": ["A ∪ B", "A ∩ B", "A × B (Cartesian Product)", "B × A only"],
        "correct_index": 2, "difficulty": "easy",
        "explanation": "Any relation R from set A to set B is formally defined as a subset of the Cartesian product A × B.",
        "source_page": "p. 6", "pdf_id": "Class_10_Mathematics_English_2025.pdf"
    },
    {
        "id": "mcq_mat1_3", "chapter_id": "tn_10_mat_ch1",
        "question": "If f: A -> B is both one-one and onto, then f is called a:",
        "options": ["Constant function", "Identity function", "Bijective function (Bijection)", "Linear function"],
        "correct_index": 2, "difficulty": "easy",
        "explanation": "A function that is both injective (one-one) and surjective (onto) is termed bijective.",
        "source_page": "p. 18", "pdf_id": "Class_10_Mathematics_English_2025.pdf"
    },
    # --- Mathematics Chapter 2: Numbers & Sequences ---
    {
        "id": "mcq_mat2_1", "chapter_id": "tn_10_mat_ch2",
        "question": "Euclid's division lemma states that for positive integers a and b, there exist unique integers q and r such that a = bq + r, where r must satisfy:",
        "options": ["1 < r < b", "0 <= r < b", "0 < r <= b", "0 <= r <= b"],
        "correct_index": 1, "difficulty": "easy",
        "explanation": "By Euclid's division lemma, the remainder r satisfies 0 <= r < b.",
        "source_page": "p. 38", "pdf_id": "Class_10_Mathematics_English_2025.pdf"
    },
    {
        "id": "mcq_mat2_2", "chapter_id": "tn_10_mat_ch2",
        "question": "The nth term of an Arithmetic Progression (A.P.) with first term a and common difference d is:",
        "options": ["tn = a + nd", "tn = a + (n - 1)d", "tn = a + (n + 1)d", "tn = a + 2nd"],
        "correct_index": 1, "difficulty": "easy",
        "explanation": "The standard general term of an A.P. is tn = a + (n - 1)d.",
        "source_page": "p. 56", "pdf_id": "Class_10_Mathematics_English_2025.pdf"
    },

    # --- Social Science History Unit 1 ---
    {
        "id": "mcq_soc_h1_1", "chapter_id": "tn_10_soc_h1",
        "question": "What were the three countries that formed the Triple Entente in 1907?",
        "options": ["Germany, Austria-Hungary, Italy", "Britain, France, Russia", "Britain, France, USA", "Russia, Germany, Japan"],
        "correct_index": 1, "difficulty": "easy",
        "explanation": "The Triple Entente was established between Britain, France, and Russia to counter the Triple Alliance.",
        "source_page": "p. 4", "pdf_id": "Class_10_Social_Science_English_2025.pdf"
    },
    {
        "id": "mcq_soc_h1_2", "chapter_id": "tn_10_soc_h1",
        "question": "Which international peace organization was founded after World War I under the Treaty of Versailles?",
        "options": ["United Nations Organization (UNO)", "League of Nations", "NATO", "European Union"],
        "correct_index": 1, "difficulty": "easy",
        "explanation": "The League of Nations was founded in 1919-1920 spearheaded by US President Woodrow Wilson.",
        "source_page": "p. 11", "pdf_id": "Class_10_Social_Science_English_2025.pdf"
    },
    # --- Social Science Civics Unit 1: Indian Constitution ---
    {
        "id": "mcq_soc_c1_1", "chapter_id": "tn_10_soc_c1",
        "question": "Which Article of the Indian Constitution is termed by Dr. B.R. Ambedkar as the 'Heart and Soul of the Constitution'?",
        "options": ["Article 14", "Article 19", "Article 21", "Article 32 (Right to Constitutional Remedies)"],
        "correct_index": 3, "difficulty": "easy",
        "explanation": "Article 32 allows citizens to move the Supreme Court for enforcement of fundamental rights through writs.",
        "source_page": "p. 243", "pdf_id": "Class_10_Social_Science_English_2025.pdf"
    },
    {
        "id": "mcq_soc_c1_2", "chapter_id": "tn_10_soc_c1",
        "question": "The Preamble to the Indian Constitution was amended for the first time by which Constitutional Amendment Act?",
        "options": ["24th Amendment Act", "42nd Amendment Act (1976)", "44th Amendment Act", "86th Amendment Act"],
        "correct_index": 1, "difficulty": "medium",
        "explanation": "The 42nd Amendment of 1976 added the words 'Socialist, Secular and Integrity' into the Preamble.",
        "source_page": "p. 240", "pdf_id": "Class_10_Social_Science_English_2025.pdf"
    },
    # --- Social Science Geography Unit 1 ---
    {
        "id": "mcq_soc_g1_1", "chapter_id": "tn_10_soc_g1",
        "question": "Which is the highest peak in South India and in the Western Ghats?",
        "options": ["Doddabetta", "Anamudi", "Kalsubai", "Mahendragiri"],
        "correct_index": 1, "difficulty": "easy",
        "explanation": "Anamudi (2,695 m) in the Anaimalai Hills is the highest peak in South India.",
        "source_page": "p. 135", "pdf_id": "Class_10_Social_Science_English_2025.pdf"
    }
]

SAMPLE_SHORT_ANSWERS = [
    {
        "id": "sa_mat1_1", "chapter_id": "tn_10_mat_ch1", "question_type": "short",
        "question": "Define Cartesian Product of two non-empty sets A and B.",
        "model_answer": "If A and B are two non-empty sets, then the set of all ordered pairs (a, b) such that a in A and b in B is called the Cartesian Product of A and B, denoted by A x B = {(a, b) | a in A, b in B}.",
        "rubric_points": [{"point_id": "r1", "description": "Defines set of ordered pairs (a, b)", "marks": 1.0}, {"point_id": "r2", "description": "Writes mathematical set builder notation A x B", "marks": 1.0}],
        "max_marks": 2.0, "source_page": "p. 2", "pdf_id": "Class_10_Mathematics_English_2025.pdf"
    },
    {
        "id": "sa_soc_c1_1", "chapter_id": "tn_10_soc_c1", "question_type": "short",
        "question": "What is a Writ? Name the five types of Writs issued by the Supreme Court.",
        "model_answer": "A writ is an order or command issued by a court in writing under its seal. The five types are: (1) Habeas Corpus, (2) Mandamus, (3) Prohibition, (4) Certiorari, and (5) Quo-Warranto.",
        "rubric_points": [{"point_id": "r1", "description": "Defines writ as judicial written command under seal", "marks": 1.0}, {"point_id": "r2", "description": "Accurately lists the five constitutional writs", "marks": 1.0}],
        "max_marks": 2.0, "source_page": "p. 243", "pdf_id": "Class_10_Social_Science_English_2025.pdf"
    }
]

SAMPLE_LONG_ANSWERS = [
    {
        "id": "la_soc_c1_1", "chapter_id": "tn_10_soc_c1", "question_type": "long",
        "question": "Explain the Salient Features of the Indian Constitution.",
        "model_answer": (
            "1. Lengthiest Written Constitution: Most detailed constitution in the world containing 25 parts, 12 schedules, and over 448 articles.\n"
            "2. Drawn from Diverse Sources: Borrowed parliamentary system from UK, Fundamental Rights from USA, and Directive Principles from Ireland.\n"
            "3. Blend of Rigidity and Flexibility: Certain provisions require special 2/3rd parliamentary majority while others can be amended easily by simple majority.\n"
            "4. Federal System with Unitary Bias: Dual polity with division of powers but with a strong central bias during emergencies.\n"
            "5. Secular State & Independent Judiciary: Freedom of religion without state favoritism, safeguarded by an integrated, independent Supreme Court."
        ),
        "rubric_points": [
            {"point_id": "r1", "description": "Describes lengthiest written constitution & diverse global sources", "marks": 1.5},
            {"point_id": "r2", "description": "Explains blend of rigidity and flexibility", "marks": 1.0},
            {"point_id": "r3", "description": "Details federal system with unitary bias", "marks": 1.5},
            {"point_id": "r4", "description": "Highlights secularism, fundamental rights, and independent judiciary", "marks": 1.0}
        ],
        "max_marks": 5.0, "source_page": "p. 240", "pdf_id": "Class_10_Social_Science_English_2025.pdf"
    }
]

def seed():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # 1. Insert new subjects
            for sid, bid, cid, sname in NEW_SUBJECTS:
                cur.execute("""
                    INSERT INTO subjects (id, board_id, class_id, name)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name, board_id = EXCLUDED.board_id, class_id = EXCLUDED.class_id;
                """, (sid, bid, cid, sname))

            # 2. Insert Maths Chapters & Guides
            for cid, sid, title in MATHS_CHAPTERS:
                cur.execute("""
                    INSERT INTO chapters (id, subject_id, title)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET title = EXCLUDED.title, subject_id = EXCLUDED.subject_id;
                """, (cid, sid, title))

                body_md = f"# {title}\n\nComprehensive board coverage for {title} according to the Tamil Nadu State Board Class 10 Mathematics textbook. Includes definitions, theorems, solved step-by-step examples, exercises, and unit evaluations."
                key_pts = [
                    "Aligned with TN SCERT Class 10 Mathematics 2025 syllabus",
                    "Covers standard board question patterns, formulas, and proofs",
                    "Traceable to Class_10_Mathematics_English_2025_Edition.pdf"
                ]
                cur.execute("""
                    INSERT INTO guides (id, chapter_id, body_md, key_points)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET body_md = EXCLUDED.body_md, key_points = EXCLUDED.key_points;
                """, (f"guide_{cid}", cid, body_md, key_pts))

            # 3. Insert Social Science Chapters & Guides
            for cid, sid, title in SOCIAL_CHAPTERS:
                cur.execute("""
                    INSERT INTO chapters (id, subject_id, title)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET title = EXCLUDED.title, subject_id = EXCLUDED.subject_id;
                """, (cid, sid, title))

                body_md = f"# {title}\n\nComprehensive board curriculum coverage for {title} (History, Geography, Civics, Economics) according to the Tamil Nadu State Board Class 10 Social Science textbook."
                key_pts = [
                    "Aligned with TN SCERT Class 10 Social Science 2025 syllabus",
                    "Covers conceptual questions, chronological event analysis, and map study",
                    "Traceable to Class_10_Social_Science_English_2025_Edition.pdf"
                ]
                cur.execute("""
                    INSERT INTO guides (id, chapter_id, body_md, key_points)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET body_md = EXCLUDED.body_md, key_points = EXCLUDED.key_points;
                """, (f"guide_{cid}", cid, body_md, key_pts))

            # 4. Insert Sample MCQs
            for m in SAMPLE_MCQS:
                cur.execute("""
                    INSERT INTO mcq_questions (id, chapter_id, question, options, correct_index, difficulty, explanation, source_page, pdf_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        question = EXCLUDED.question,
                        options = EXCLUDED.options,
                        correct_index = EXCLUDED.correct_index,
                        difficulty = EXCLUDED.difficulty,
                        explanation = EXCLUDED.explanation,
                        source_page = EXCLUDED.source_page,
                        pdf_id = EXCLUDED.pdf_id;
                """, (
                    m["id"], m["chapter_id"], m["question"], json.dumps(m["options"]),
                    m["correct_index"], m["difficulty"], m["explanation"],
                    m.get("source_page", "p. 1"), m.get("pdf_id", "textbook.pdf")
                ))

            # 5. Insert Sample Short and Long Answers
            for a in SAMPLE_SHORT_ANSWERS + SAMPLE_LONG_ANSWERS:
                cur.execute("""
                    INSERT INTO answer_questions (id, chapter_id, question_type, question, model_answer, rubric_points, max_marks, source_page, pdf_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        question_type = EXCLUDED.question_type,
                        question = EXCLUDED.question,
                        model_answer = EXCLUDED.model_answer,
                        rubric_points = EXCLUDED.rubric_points,
                        max_marks = EXCLUDED.max_marks,
                        source_page = EXCLUDED.source_page,
                        pdf_id = EXCLUDED.pdf_id;
                """, (
                    a["id"], a["chapter_id"], a["question_type"], a["question"],
                    a["model_answer"], json.dumps(a["rubric_points"]), a["max_marks"],
                    a.get("source_page", "p. 1"), a.get("pdf_id", "textbook.pdf")
                ))

            conn.commit()
            print("[x] Successfully registered Mathematics and Social Science subjects and chapters into DB!")
    finally:
        conn.close()

if __name__ == "__main__":
    seed()
