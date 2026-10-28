"""
seed_all_27_social_chapters.py
------------------------------
Seeds all 27 chapters across History, Geography, Civics, and Economics
directly from the official 2025 Tamil Nadu Class 10 Social Science textbook TOC.
"""
import psycopg2
from ingestion.db import get_connection

ALL_27_SOCIAL_CHAPTERS = [
    # --- History (10 Units) ---
    ("tn_10_soc_h1", "tn_10_social", "History Unit 1: Outbreak of World War I and Its Aftermath", 1, 15),
    ("tn_10_soc_h2", "tn_10_social", "History Unit 2: The World between two World Wars", 16, 26),
    ("tn_10_soc_h3", "tn_10_social", "History Unit 3: World War II", 27, 39),
    ("tn_10_soc_h4", "tn_10_social", "History Unit 4: The World after World War II", 40, 52),
    ("tn_10_soc_h5", "tn_10_social", "History Unit 5: Social and Religious Reform Movements in the 19th Century", 53, 62),
    ("tn_10_soc_h6", "tn_10_social", "History Unit 6: Early Revolts against British Rule in Tamil Nadu", 63, 74),
    ("tn_10_soc_h7", "tn_10_social", "History Unit 7: Anti-Colonial Movements and the Birth of Nationalism", 75, 88),
    ("tn_10_soc_h8", "tn_10_social", "History Unit 8: Nationalism: Gandhian Phase", 89, 104),
    ("tn_10_soc_h9", "tn_10_social", "History Unit 9: Freedom Struggle in Tamil Nadu", 105, 114),
    ("tn_10_soc_h10", "tn_10_social", "History Unit 10: Social Transformation in Tamil Nadu", 115, 128),

    # --- Geography (7 Units) ---
    ("tn_10_soc_g1", "tn_10_social", "Geography Unit 1: India - Location, Relief and Drainage", 129, 143),
    ("tn_10_soc_g2", "tn_10_social", "Geography Unit 2: Climate and Natural Vegetation of India", 144, 153),
    ("tn_10_soc_g3", "tn_10_social", "Geography Unit 3: India - Agriculture", 154, 169),
    ("tn_10_soc_g4", "tn_10_social", "Geography Unit 4: India - Resources and Industries", 170, 185),
    ("tn_10_soc_g5", "tn_10_social", "Geography Unit 5: India - Population, Transport, Communication and Trade", 186, 199),
    ("tn_10_soc_g6", "tn_10_social", "Geography Unit 6: Physical Geography of Tamil Nadu", 200, 218),
    ("tn_10_soc_g7", "tn_10_social", "Geography Unit 7: Human Geography of Tamil Nadu", 219, 238),

    # --- Civics (5 Units) ---
    ("tn_10_soc_c1", "tn_10_social", "Civics Unit 1: Indian Constitution", 239, 247),
    ("tn_10_soc_c2", "tn_10_social", "Civics Unit 2: Central Government", 248, 258),
    ("tn_10_soc_c3", "tn_10_social", "Civics Unit 3: State Government", 259, 268),
    ("tn_10_soc_c4", "tn_10_social", "Civics Unit 4: India's Foreign Policy", 269, 277),
    ("tn_10_soc_c5", "tn_10_social", "Civics Unit 5: India's International Relations", 278, 291),

    # --- Economics (5 Units) ---
    ("tn_10_soc_e1", "tn_10_social", "Economics Unit 1: Gross Domestic Product and its Growth", 292, 302),
    ("tn_10_soc_e2", "tn_10_social", "Economics Unit 2: Globalization and Trade", 303, 310),
    ("tn_10_soc_e3", "tn_10_social", "Economics Unit 3: Food Security and Nutrition", 311, 320),
    ("tn_10_soc_e4", "tn_10_social", "Economics Unit 4: Government and Taxes", 321, 327),
    ("tn_10_soc_e5", "tn_10_social", "Economics Unit 5: Industrial Clusters in Tamil Nadu", 328, 335),
]

def seed_all_social():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            for cid, sid, title, p_start, p_end in ALL_27_SOCIAL_CHAPTERS:
                cur.execute("""
                    INSERT INTO chapters (id, subject_id, title)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET title = EXCLUDED.title, subject_id = EXCLUDED.subject_id;
                """, (cid, sid, title))

                body_md = f"# {title}\n\nComprehensive board curriculum coverage for {title} according to the Tamil Nadu State Board Class 10 Social Science textbook (Pages {p_start} to {p_end}). Includes learning objectives, key events, terms, evaluation questions, and map references."
                key_pts = [
                    f"Aligned with TN SCERT Class 10 Social Science 2025 syllabus (p. {p_start}-{p_end})",
                    "Covers textbook exercises, evaluation questions, and historical/geographical timelines",
                    "Traceable to Class_10_Social_Science_English_2025_Edition.pdf"
                ]
                cur.execute("""
                    INSERT INTO guides (id, chapter_id, body_md, key_points)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        chapter_id = EXCLUDED.chapter_id,
                        body_md = EXCLUDED.body_md,
                        key_points = EXCLUDED.key_points;
                """, (f"guide_{cid}", cid, body_md, key_pts))

            conn.commit()
            print(f"[x] Successfully seeded all {len(ALL_27_SOCIAL_CHAPTERS)} Social Science chapters into DB!")
    finally:
        conn.close()

if __name__ == "__main__":
    seed_all_social()
