"""
ingestion/seed_data.py
----------------------
Seeds comprehensive taxonomy for Board (CBSE | TN_STATE) -> Class (10 | 12) -> Subject (Physics, Tamil, Commerce, English, Science) -> Chapter
with full Content Model and Leaderboards for ALL Classes (10 & 12).
"""
from __future__ import annotations

import json
from ingestion.db import get_connection

def seed_database():
    print("Seeding database with full Board -> Class -> Subject -> Chapter hierarchy & Leaderboards...")
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # 1. Boards
            cur.execute("""
                INSERT INTO boards (id, name) VALUES
                ('TN_STATE', 'Tamil Nadu State Board'),
                ('CBSE', 'Central Board of Secondary Education')
                ON CONFLICT (id) DO NOTHING;
            """)

            # 2. Classes
            cur.execute("""
                INSERT INTO classes (id, board_id, label) VALUES
                ('tn_class_10', 'TN_STATE', 'Class 10'),
                ('tn_class_12', 'TN_STATE', 'Class 12'),
                ('cbse_class_10', 'CBSE', 'Class 10'),
                ('cbse_class_12', 'CBSE', 'Class 12')
                ON CONFLICT (id) DO NOTHING;
            """)

            # 3. Subjects across Classes & Boards
            subjects_data = [
                # TN State 10th
                ('tn_10_english', 'TN_STATE', 'tn_class_10', 'English'),
                ('tn_10_tamil', 'TN_STATE', 'tn_class_10', 'Tamil (தமிழ்)'),
                ('tn_10_science', 'TN_STATE', 'tn_class_10', 'Science'),
                ('tn_10_maths', 'TN_STATE', 'tn_class_10', 'Maths'),
                ('tn_10_social', 'TN_STATE', 'tn_class_10', 'Social Science'),
                # TN State 12th
                ('tn_12_physics', 'TN_STATE', 'tn_class_12', 'Physics'),
                ('tn_12_commerce', 'TN_STATE', 'tn_class_12', 'Commerce'),
                ('tn_12_tamil', 'TN_STATE', 'tn_class_12', 'Tamil (தமிழ்)'),
                # CBSE 10th
                ('cbse_10_science', 'CBSE', 'cbse_class_10', 'Science'),
                ('cbse_10_english', 'CBSE', 'cbse_class_10', 'English Language & Lit'),
                ('cbse_10_maths', 'CBSE', 'cbse_class_10', 'Maths'),
                ('cbse_10_social', 'CBSE', 'cbse_class_10', 'Social Science'),
                # CBSE 12th
                ('cbse_12_physics', 'CBSE', 'cbse_class_12', 'Physics'),
                ('cbse_12_commerce', 'CBSE', 'cbse_class_12', 'Accountancy & Commerce')
            ]

            for s_id, b_id, c_id, name in subjects_data:
                cur.execute("""
                    INSERT INTO subjects (id, board_id, class_id, name)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;
                """, (s_id, b_id, c_id, name))

            # 4. Chapters
            chapters_data = [
                # TN 10th English
                ('tn_10_eng_ch1', 'tn_10_english', "Unit 1: His First Flight — Liam O'Flaherty", 1, 'published'),
                ('tn_10_eng_ch2', 'tn_10_english', 'Unit 2: Empowered Women Navigating The World', 2, 'published'),
                ('tn_10_eng_ch3', 'tn_10_english', 'Unit 3: The Attic — Satyajit Ray', 3, 'published'),
                ('tn_10_eng_ch4', 'tn_10_english', 'Unit 4: Tech Bloomers — Technology in Everyday Life', 4, 'published'),
                ('tn_10_eng_ch5', 'tn_10_english', 'Unit 5: The Last Lesson — Alphonse Daudet', 5, 'published'),
                ('tn_10_eng_ch6', 'tn_10_english', 'Unit 6: The Dying Detective — Arthur Conan Doyle', 6, 'published'),
                ('tn_10_eng_ch7', 'tn_10_english', 'Unit 7: A Dilemma — Silas Weir Mitchell', 7, 'published'),
                # TN 12th Physics
                ('tn_12_phy_ch1', 'tn_12_physics', 'Unit 1: Electrostatics', 1, 'published'),
                ('tn_12_phy_ch2', 'tn_12_physics', 'Unit 2: Current Electricity', 2, 'published'),
                # TN 12th Commerce
                ('tn_12_com_ch1', 'tn_12_commerce', 'Chapter 1: Principles of Management', 1, 'published'),
                # CBSE 10th Science
                ('cbse_10_sci_ch1', 'cbse_10_science', 'Chapter 1: Chemical Reactions and Equations', 1, 'published'),
                ('cbse_10_sci_ch2', 'cbse_10_science', 'Chapter 2: Acids, Bases and Salts', 2, 'published'),
                # CBSE 12th Physics
                ('cbse_12_phy_ch1', 'cbse_12_physics', 'Chapter 1: Electric Charges and Fields', 1, 'published')
            ]

            for ch in chapters_data:
                cur.execute("""
                    INSERT INTO chapters (id, subject_id, title, chapter_order, review_status)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET title = EXCLUDED.title, chapter_order = EXCLUDED.chapter_order;
                """, ch)

            # 5. Guides
            guides_data = [
                ('guide_eng_ch1', 'tn_10_eng_ch1', 
                '# Unit 1: His First Flight\n\n### Summary\nThis inspiring story by Liam O\'Flaherty tells the tale of a young seagull who is afraid to take his first flight. His family uses tough love: his mother shows him a piece of fish but stays just out of reach. Driven by intense hunger, the young seagull dives toward the fish, spreading his wings instinctively, and discovers that he can fly!',
                ['Fear is overcome by courage and necessity', 'Parents role in pushing children past comfort zones', 'Natural instinct takes over when action is taken'],
                'published'),

                ('guide_eng_ch2', 'tn_10_eng_ch2',
                '# Unit 2: Empowered Women Navigating The World\n\n### Summary\nThis chapter highlights the all-women crew of INSV Tarini who circumnavigated the globe in the Navika Sagar Parikrama expedition. Led by Lieutenant Commander Vartika Joshi, six brave female officers completed an extraordinary journey showcasing female empowerment, endurance, and teamwork.',
                ['INSV Tarini all-women naval expedition', 'Circumnavigation of the globe', 'Breakthrough in maritime gender equality'],
                'published'),

                ('guide_phy_ch1', 'tn_12_phy_ch1',
                '# Unit 1: Electrostatics\n\n### Summary\nElectrostatics deals with static electric charges, Coulomb\'s law, electric field intensity, electric potential, and capacitance. It explains Gauss\'s law and its applications in spherical and cylindrical charge distributions.',
                ['Coulomb\'s Law of Inverse Squares', 'Electric Field and Potential Difference', 'Capacitors and Energy Stored in Electric Fields'],
                'published'),

                ('guide_com_ch1', 'tn_12_com_ch1',
                '# Chapter 1: Principles of Management\n\n### Summary\nExplores Henri Fayol\'s 14 principles of management including division of work, authority & responsibility, unity of command, and scalar chain, alongside F.W. Taylor\'s scientific management principles.',
                ['Henri Fayol\'s 14 Management Principles', 'F.W. Taylor Scientific Management', 'Functions of Management in Modern Enterprise'],
                'published')
            ]

            for g_id, ch_id, body, kpts, status in guides_data:
                cur.execute("""
                    INSERT INTO guides (id, chapter_id, body_md, key_points, review_status)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET body_md = EXCLUDED.body_md, key_points = EXCLUDED.key_points;
                """, (g_id, ch_id, body, kpts, status))

            # 6. MCQ Bank
            mcqs = [
                ('mcq_eng_ch1_1', 'tn_10_eng_ch1', 'Why was the young seagull afraid to fly?', json.dumps(['He had injured his wings', 'He was afraid the sea was too deep and his wings would not support him', 'He did not like fish', 'His parents told him not to fly']), 1, 'easy', 'He felt certain his wings would never support him.', 'p. 6 - p. 7', '10th_English.pdf'),
                ('mcq_eng_ch1_2', 'tn_10_eng_ch1', 'What compelled the young seagull to dive off the ledge?', json.dumps(['A sudden gust of wind', 'Extreme hunger when his mother maddened him with fish', 'A push from his father', 'A predator attacking him']), 1, 'medium', 'He was maddened by hunger when his mother flew near with a fish.', 'p. 8 - p. 9', '10th_English.pdf'),
                ('mcq_eng_ch2_1', 'tn_10_eng_ch2', 'What was the name of the vessel used in Navika Sagar Parikrama?', json.dumps(['INS Vikrant', 'INSV Tarini', 'INS Arihant', 'INS Garuda']), 1, 'easy', 'Navika Sagar Parikrama was aboard INSV Tarini.', 'p. 34 - p. 36', '10th_English.pdf'),
                ('mcq_phy_ch1_1', 'tn_12_phy_ch1', 'What is the SI unit of electric dipole moment?', json.dumps(['Coulomb-meter (C m)', 'Newton/Coulomb', 'Volt/meter', 'Farad']), 0, 'easy', 'Electric dipole moment p = q * 2a, measured in Coulomb-meters.', 'p. 12 - p. 15', '12th_Physics_Vol1.pdf'),
                ('mcq_com_ch1_1', 'tn_12_com_ch1', 'Who is considered the Father of Modern Management?', json.dumps(['F.W. Taylor', 'Henri Fayol', 'Elton Mayo', 'Peter Drucker']), 1, 'easy', 'Henri Fayol formulated the 14 principles of general management.', 'p. 2 - p. 5', '12th_Commerce.pdf')
            ]

            for m in mcqs:
                cur.execute("""
                    INSERT INTO mcq_questions (id, chapter_id, question, options, correct_index, difficulty, explanation, source_page, pdf_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET source_page = EXCLUDED.source_page, pdf_id = EXCLUDED.pdf_id;
                """, m)

            # 7. Short & Long Answer Banks
            written_questions = [
                ('ans_eng_ch1_1', 'tn_10_eng_ch1', 'short', 'Describe the role of the mother seagull in helping the young seagull fly.', 'The mother seagull flew close holding a piece of fish, stopping out of reach to compel him to dive.', json.dumps([{"point_id": "r1", "description": "Mentions mother holding fish near ledge", "marks": 2.0}, {"point_id": "r2", "description": "States young seagull dived due to hunger", "marks": 2.0}, {"point_id": "r3", "description": "Explains how diving triggered flight instinct", "marks": 1.0}]), 5.0, 'p. 8 - p. 9', '10th_English.pdf'),
                ('ans_eng_ch2_1', 'tn_10_eng_ch2', 'long', 'Explain the challenges faced by the crew of INSV Tarini during their voyage.', 'Rough seas, severe weather, mid-ocean repairs, sleep deprivation, and team endurance.', json.dumps([{"point_id": "r1", "description": "Highlights extreme weather and rough seas", "marks": 2.5}, {"point_id": "r2", "description": "Mentions mid-ocean technical repair", "marks": 2.5}, {"point_id": "r3", "description": "Discusses team stamina and coordination", "marks": 2.5}, {"point_id": "r4", "description": "Concludes with significance of female empowerment", "marks": 2.5}]), 10.0, 'p. 36 - p. 40', '10th_English.pdf'),
                ('ans_phy_ch1_1', 'tn_12_phy_ch1', 'short', 'State Coulomb\'s Law in electrostatics.', 'Coulomb\'s Law states that the electrostatic force between two point charges is directly proportional to the product of their charges and inversely proportional to the square of distance between them.', json.dumps([{"point_id": "r1", "description": "States force proportional to product of magnitude of charges", "marks": 2.5}, {"point_id": "r2", "description": "States force inversely proportional to square of distance", "marks": 2.5}]), 5.0, 'p. 4 - p. 6', '12th_Physics_Vol1.pdf'),
                ('ans_com_ch1_1', 'tn_12_com_ch1', 'short', 'Explain the principle of Unity of Command.', 'Unity of Command states that an employee should receive orders from only one superior manager to avoid confusion and conflict.', json.dumps([{"point_id": "r1", "description": "States order received from single superior manager", "marks": 2.5}, {"point_id": "r2", "description": "Explains prevention of role conflict and confusion", "marks": 2.5}]), 5.0, 'p. 6 - p. 8', '12th_Commerce.pdf')
            ]

            for w in written_questions:
                cur.execute("""
                    INSERT INTO answer_questions (id, chapter_id, question_type, question, model_answer, rubric_points, max_marks, source_page, pdf_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET source_page = EXCLUDED.source_page, pdf_id = EXCLUDED.pdf_id;
                """, w)

            # 8. Leaderboard Entries FOR ALL 4 COMBINATIONS (10th & 12th for both TN_STATE & CBSE)
            leaderboard_data = [
                # TN State 10th
                ('lb_1', 'stu_101', 'Kavya R.', 'TN_STATE', 'tn_class_10', 485.0, 5, 97.0, 1),
                ('lb_2', 'stu_102', 'Arun Kumar', 'TN_STATE', 'tn_class_10', 460.0, 5, 92.0, 2),
                ('lb_3', 'stu_103', 'Priya S.', 'TN_STATE', 'tn_class_10', 445.0, 4, 89.0, 3),

                # TN State 12th
                ('lb_12_1', 'stu_201', 'Dinesh V.', 'TN_STATE', 'tn_class_12', 495.0, 5, 99.0, 1),
                ('lb_12_2', 'stu_202', 'Sharanya K.', 'TN_STATE', 'tn_class_12', 480.0, 5, 96.0, 2),
                ('lb_12_3', 'stu_203', 'Vignesh P.', 'TN_STATE', 'tn_class_12', 465.0, 4, 93.0, 3),

                # CBSE 10th
                ('lb_4', 'stu_104', 'Rahul M.', 'CBSE', 'cbse_class_10', 490.0, 5, 98.0, 1),
                ('lb_5', 'stu_105', 'Sneha V.', 'CBSE', 'cbse_class_10', 472.0, 5, 94.4, 2),

                # CBSE 12th
                ('lb_cbse12_1', 'stu_301', 'Aditya Sharma', 'CBSE', 'cbse_class_12', 498.0, 5, 99.6, 1),
                ('lb_cbse12_2', 'stu_302', 'Ananya Gupta', 'CBSE', 'cbse_class_12', 482.0, 5, 96.4, 2),
                ('lb_cbse12_3', 'stu_303', 'Rohan Verma', 'CBSE', 'cbse_class_12', 470.0, 4, 94.0, 3)
            ]

            for lb in leaderboard_data:
                cur.execute("""
                    INSERT INTO leaderboard_entries (id, student_id, student_name, board_id, class_id, total_score, exams_completed, accuracy_pct, rank)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET total_score = EXCLUDED.total_score, rank = EXCLUDED.rank;
                """, lb)

        conn.commit()
        print("Database seeded with Leaderboards for ALL Class 10 & Class 12 Boards!")
    finally:
        conn.close()

if __name__ == "__main__":
    seed_database()
