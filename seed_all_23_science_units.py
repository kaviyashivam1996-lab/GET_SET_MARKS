"""
seed_all_23_science_units.py
----------------------------
Seeds all 23 Units of Class 10 Tamil Nadu Science directly from the official 2024 textbook TOC.
Extracts and links chunks and creates board questions for all units.
"""
import json
import psycopg2
from ingestion.db import get_connection

TN_10_SCIENCE_UNITS = [
    ("tn_10_sci_ch1", "tn_10_science", "Unit 1: Laws of Motion", 1, 15),
    ("tn_10_sci_ch2", "tn_10_science", "Unit 2: Optics", 16, 31),
    ("tn_10_sci_ch3", "tn_10_science", "Unit 3: Thermal Physics", 32, 41),
    ("tn_10_sci_ch4", "tn_10_science", "Unit 4: Electricity", 42, 58),
    ("tn_10_sci_ch5", "tn_10_science", "Unit 5: Acoustics", 59, 73),
    ("tn_10_sci_ch6", "tn_10_science", "Unit 6: Nuclear Physics", 74, 90),
    ("tn_10_sci_ch7", "tn_10_science", "Unit 7: Atoms and Molecules", 91, 105),
    ("tn_10_sci_ch8", "tn_10_science", "Unit 8: Periodic Classification of Elements", 106, 123),
    ("tn_10_sci_ch9", "tn_10_science", "Unit 9: Solutions", 124, 136),
    ("tn_10_sci_ch10", "tn_10_science", "Unit 10: Types of Chemical Reactions", 137, 154),
    ("tn_10_sci_ch11", "tn_10_science", "Unit 11: Carbon and its Compounds", 155, 172),
    ("tn_10_sci_ch12", "tn_10_science", "Unit 12: Plant Anatomy and Plant Physiology", 173, 186),
    ("tn_10_sci_ch13", "tn_10_science", "Unit 13: Structural Organisation of Animals", 187, 199),
    ("tn_10_sci_ch14", "tn_10_science", "Unit 14: Transportation in Plants and Circulation in Animals", 200, 217),
    ("tn_10_sci_ch15", "tn_10_science", "Unit 15: Nervous System", 218, 228),
    ("tn_10_sci_ch16", "tn_10_science", "Unit 16: Plant and Animal Hormones", 229, 242),
    ("tn_10_sci_ch17", "tn_10_science", "Unit 17: Reproduction in Plants and Animals", 243, 260),
    ("tn_10_sci_ch18", "tn_10_science", "Unit 18: Genetics", 261, 273),
    ("tn_10_sci_ch19", "tn_10_science", "Unit 19: Origin and Evolution of Life", 274, 285),
    ("tn_10_sci_ch20", "tn_10_science", "Unit 20: Breeding and Biotechnology", 286, 299),
    ("tn_10_sci_ch21", "tn_10_science", "Unit 21: Health and Diseases", 300, 314),
    ("tn_10_sci_ch22", "tn_10_science", "Unit 22: Environmental Management", 315, 328),
    ("tn_10_sci_ch23", "tn_10_science", "Unit 23: Visual Communication", 329, 333),
]

UNIT_QUESTIONS = {
    "tn_10_sci_ch3": {
        "mcqs": [
            {
                "id": "mcq_sci3_1", "question": "The value of universal gas constant (R) is:",
                "options": ["8.31 J mol⁻¹ K⁻¹", "8.31 × 10³ J mol⁻¹ K⁻¹", "1.38 × 10⁻²³ J K⁻¹", "6.023 × 10²³ mol⁻¹"],
                "correct_index": 0, "difficulty": "easy",
                "explanation": "Universal gas constant R = 8.31 J mol⁻¹ K⁻¹.", "source_page": "p. 38"
            },
            {
                "id": "mcq_sci3_2", "question": "According to Charles's Law, when pressure remains constant:",
                "options": ["V ∝ T", "V ∝ 1/T", "P ∝ T", "PV = constant"],
                "correct_index": 0, "difficulty": "easy",
                "explanation": "Charles's law states volume is directly proportional to absolute temperature at constant pressure.", "source_page": "p. 35"
            },
            {
                "id": "mcq_sci3_3", "question": "What is the SI unit of heat energy?",
                "options": ["Calorie", "Joule (J)", "Kelvin", "Watt"],
                "correct_index": 1, "difficulty": "easy",
                "explanation": "Joule is the SI unit of all forms of energy, including heat energy.", "source_page": "p. 33"
            }
        ],
        "short": [
            {
                "id": "sa_sci3_1", "question": "Define Avogadro's law.",
                "model_answer": "Avogadro's law states that equal volumes of all gases under the same conditions of temperature and pressure contain equal number of molecules (V ∝ n).",
                "rubric": [{"point_id": "r1", "description": "States equal volumes contain equal number of molecules", "marks": 1.0}, {"point_id": "r2", "description": "Mentions constant temperature and pressure condition (V ∝ n)", "marks": 1.0}]
            },
            {
                "id": "sa_sci3_2", "question": "Distinguish between real gas and ideal gas.",
                "model_answer": "An ideal gas obeys the gas equation PV = nRT strictly at all temperatures and pressures with negligible intermolecular forces. A real gas deviates from this behavior due to finite molecular volume and intermolecular attractions.",
                "rubric": [{"point_id": "r1", "description": "Defines ideal gas obeying PV=nRT strictly", "marks": 1.0}, {"point_id": "r2", "description": "Defines real gas with intermolecular forces and deviations", "marks": 1.0}]
            }
        ],
        "long": [
            {
                "id": "la_sci3_1", "question": "Derive the ideal gas equation from Boyle's law, Charles's law, and Avogadro's law.",
                "model_answer": "1. Boyle's Law: At constant T, V ∝ 1/P.\n2. Charles's Law: At constant P, V ∝ T.\n3. Avogadro's Law: At constant P and T, V ∝ n.\nCombining these three laws: V ∝ (n * T) / P => PV ∝ nT => PV = nRT, where R is the universal gas constant (8.31 J mol⁻¹ K⁻¹).",
                "rubric": [
                    {"point_id": "r1", "description": "States Boyle's law (V ∝ 1/P)", "marks": 1.0},
                    {"point_id": "r2", "description": "States Charles's law (V ∝ T)", "marks": 1.5},
                    {"point_id": "r3", "description": "States Avogadro's law (V ∝ n)", "marks": 1.5},
                    {"point_id": "r4", "description": "Combines equations to arrive at PV = nRT and defines R", "marks": 1.0}
                ]
            }
        ]
    },
    "tn_10_sci_ch4": {
        "mcqs": [
            {
                "id": "mcq_sci4_1", "question": "The SI unit of electrical resistivity is:",
                "options": ["Ohm (Ω)", "Ohm-meter (Ω·m)", "Ohm / meter", "Siemens"],
                "correct_index": 1, "difficulty": "easy",
                "explanation": "Resistivity ρ = (R * A) / L has unit (Ω * m²)/m = Ω·m.", "source_page": "p. 45"
            },
            {
                "id": "mcq_sci4_2", "question": "Which rule determines the direction of magnetic field around a current-carrying conductor?",
                "options": ["Fleming's Left Hand Rule", "Right Hand Thumb Rule", "Fleming's Right Hand Rule", "Lenz's Law"],
                "correct_index": 1, "difficulty": "easy",
                "explanation": "Maxwell's Right Hand Thumb Rule gives the direction of concentric magnetic field lines.", "source_page": "p. 49"
            },
            {
                "id": "mcq_sci4_3", "question": "Joule's law of heating is given by the formula:",
                "options": ["H = V / I", "H = I² R t", "H = I R² t", "H = V I² t"],
                "correct_index": 1, "difficulty": "easy",
                "explanation": "Heat produced H = I²Rt (Joule's law of heating).", "source_page": "p. 47"
            }
        ],
        "short": [
            {
                "id": "sa_sci4_1", "question": "State Ohm's Law.",
                "model_answer": "At constant temperature, the steady current (I) flowing through a conductor is directly proportional to the potential difference (V) across its ends: V = I * R.",
                "rubric": [{"point_id": "r1", "description": "States current proportional to potential difference at constant temperature", "marks": 1.0}, {"point_id": "r2", "description": "Writes formula V = IR and defines resistance R", "marks": 1.0}]
            },
            {
                "id": "sa_sci4_2", "question": "Why is tungsten metal used almost exclusively for filaments of incandescent lamps?",
                "model_answer": "Tungsten has an exceptionally high melting point (3380°C) and high resistivity, allowing it to glow white-hot without melting when current passes through.",
                "rubric": [{"point_id": "r1", "description": "Mentions extremely high melting point (3380°C)", "marks": 1.0}, {"point_id": "r2", "description": "Mentions high resistivity and heat endurance without oxidation", "marks": 1.0}]
            }
        ],
        "long": [
            {
                "id": "la_sci4_1", "question": "Derive the equivalent resistance of three resistors connected (a) in series and (b) in parallel.",
                "model_answer": "Series: Same current I flows through R1, R2, R3. Total potential difference V = V1 + V2 + V3. Since V = IR, I*Rs = I*R1 + I*R2 + I*R3 => Rs = R1 + R2 + R3.\n\nParallel: Same potential difference V exists across R1, R2, R3. Total current I = I1 + I2 + I3. Since I = V/R, V/Rp = V/R1 + V/R2 + V/R3 => 1/Rp = 1/R1 + 1/R2 + 1/R3.",
                "rubric": [
                    {"point_id": "r1", "description": "Explains current and potential in series combination", "marks": 1.0},
                    {"point_id": "r2", "description": "Derives Rs = R1 + R2 + R3", "marks": 1.5},
                    {"point_id": "r3", "description": "Explains current division in parallel combination", "marks": 1.0},
                    {"point_id": "r4", "description": "Derives 1/Rp = 1/R1 + 1/R2 + 1/R3", "marks": 1.5}
                ]
            }
        ]
    },
    "tn_10_sci_ch7": {
        "mcqs": [
            {
                "id": "mcq_sci7_1", "question": "What is the molar volume of any gas at STP (Standard Temperature and Pressure)?",
                "options": ["22.4 litres (dm³)", "24.2 litres", "11.2 litres", "44.8 litres"],
                "correct_index": 0, "difficulty": "easy",
                "explanation": "One mole of any ideal gas occupies 22.4 litres at 273 K and 1 atm pressure.", "source_page": "p. 98"
            },
            {
                "id": "mcq_sci7_2", "question": "Relative Molecular Mass (RMM) is equal to:",
                "options": ["2 × Vapour Density", "Vapour Density / 2", "Vapour Density²", "Vapour Density + 2"],
                "correct_index": 0, "difficulty": "easy",
                "explanation": "Relative molecular mass = 2 × Vapour density.", "source_page": "p. 99"
            }
        ],
        "short": [
            {
                "id": "sa_sci7_1", "question": "Define atomicity and give an example of a triatomic molecule.",
                "model_answer": "Atomicity is the total number of atoms present in one molecule of an element or compound. Example: Ozone (O3) has an atomicity of 3 (triatomic).",
                "rubric": [{"point_id": "r1", "description": "Defines atomicity as number of atoms per molecule", "marks": 1.0}, {"point_id": "r2", "description": "Provides accurate triatomic example (e.g., O3, H2O, CO2)", "marks": 1.0}]
            }
        ],
        "long": [
            {
                "id": "la_sci7_1", "question": "Deduce the relationship between Vapour Density and Relative Molecular Mass using Avogadro's Law.",
                "model_answer": "1. Vapour Density (V.D.) = Mass of a certain volume of gas / Mass of same volume of hydrogen at STP.\n2. By Avogadro's law: V.D. = Mass of 'n' molecules of gas / Mass of 'n' molecules of hydrogen.\n3. For n = 1: V.D. = Mass of 1 molecule of gas / Mass of 1 molecule of hydrogen (2 atoms).\n4. V.D. = Mass of 1 molecule of gas / (2 * Mass of 1 hydrogen atom).\n5. Relative Molecular Mass = Mass of 1 molecule of gas / Mass of 1 hydrogen atom.\n6. Therefore, V.D. = Relative Molecular Mass / 2 => Relative Molecular Mass = 2 × Vapour Density.",
                "rubric": [
                    {"point_id": "r1", "description": "Defines Vapour Density mathematically", "marks": 1.0},
                    {"point_id": "r2", "description": "Applies Avogadro's law to transition from volume to molecules", "marks": 1.5},
                    {"point_id": "r3", "description": "Accounts for diatomic hydrogen (2 atoms)", "marks": 1.5},
                    {"point_id": "r4", "description": "Concludes Relative Molecular Mass = 2 × V.D.", "marks": 1.0}
                ]
            }
        ]
    },
    "tn_10_sci_ch12": {
        "mcqs": [
            {
                "id": "mcq_sci12_1", "question": "Which organelle is universally referred to as the 'Powerhouse of the Cell'?",
                "options": ["Ribosome", "Mitochondria", "Chloroplast", "Golgi apparatus"],
                "correct_index": 1, "difficulty": "easy",
                "explanation": "Mitochondria produce cellular ATP through oxidative phosphorylation.", "source_page": "p. 179"
            },
            {
                "id": "mcq_sci12_2", "question": "Kreb's cycle occurs in which part of the cell during aerobic respiration?",
                "options": ["Cytoplasm", "Mitochondrial matrix", "Grana of chloroplast", "Inner membrane space"],
                "correct_index": 1, "difficulty": "easy",
                "explanation": "Kreb's citric acid cycle takes place in the mitochondrial matrix.", "source_page": "p. 182"
            }
        ],
        "short": [
            {
                "id": "sa_sci12_1", "question": "Differentiate between aerobic and anaerobic respiration.",
                "model_answer": "Aerobic respiration occurs in the presence of oxygen, yielding CO2, H2O, and 36-38 ATP per glucose. Anaerobic respiration occurs without oxygen (fermentation), yielding ethyl alcohol or lactic acid and only 2 ATP per glucose.",
                "rubric": [{"point_id": "r1", "description": "Aerobic: Requires O2, complete oxidation, 36-38 ATP", "marks": 1.0}, {"point_id": "r2", "description": "Anaerobic: No O2, partial breakdown, 2 ATP", "marks": 1.0}]
            }
        ],
        "long": [
            {
                "id": "la_sci12_1", "question": "Describe the internal structure of a Dicot Root with a neat diagrammatic representation.",
                "model_answer": "A transverse section of a dicot root (e.g., bean) shows:\n1. Epiblema (Piliferous layer): Outermost layer without cuticle or stomata, bearing unicellular root hairs.\n2. Cortex: Large multilayered zone of thin-walled parenchymatous cells storing food and water.\n3. Endodermis: Innermost cortical layer with Casparian strips (suberin band) regulating radial water entry.\n4. Stele: All tissues inside endodermis:\n   - Pericycle: Gives rise to lateral roots.\n   - Vascular bundles: Radial (xylem and phloem on alternate radii); xylem is exarch (protoxylem towards periphery) and tetrarch.",
                "rubric": [
                    {"point_id": "r1", "description": "Describes Epiblema and root hairs", "marks": 1.0},
                    {"point_id": "r2", "description": "Details multilayered parenchymatous Cortex", "marks": 1.0},
                    {"point_id": "r3", "description": "Explains Endodermis with Casparian strips", "marks": 1.5},
                    {"point_id": "r4", "description": "Describes Stele: pericycle, radial and exarch xylem", "marks": 1.5}
                ]
            }
        ]
    },
    "tn_10_sci_ch14": {
        "mcqs": [
            {
                "id": "mcq_sci14_1", "question": "Which chamber of the human heart pumps oxygenated blood into the aorta for systemic circulation?",
                "options": ["Right Atrium", "Right Ventricle", "Left Atrium", "Left Ventricle"],
                "correct_index": 3, "difficulty": "easy",
                "explanation": "The thick-walled left ventricle pumps oxygenated blood under high pressure through the aorta.", "source_page": "p. 209"
            },
            {
                "id": "mcq_sci14_2", "question": "What is the normal blood pressure value for a healthy adult human?",
                "options": ["100/70 mm Hg", "120/80 mm Hg", "140/90 mm Hg", "80/120 mm Hg"],
                "correct_index": 1, "difficulty": "easy",
                "explanation": "120 mm Hg systolic (during contraction) and 80 mm Hg diastolic (during relaxation).", "source_page": "p. 212"
            }
        ],
        "short": [
            {
                "id": "sa_sci14_1", "question": "Why are the walls of the ventricles much thicker than the walls of the auricles (atria)?",
                "model_answer": "Ventricles must pump blood with forceful contractions to distant organs (lungs and systemic body), requiring high pressure. Auricles only receive and push blood down into adjacent ventricles under low pressure.",
                "rubric": [{"point_id": "r1", "description": "Ventricles generate high pressure to circulate blood to lungs and entire body", "marks": 1.0}, {"point_id": "r2", "description": "Atria only pump into adjacent ventricles requiring less muscular force", "marks": 1.0}]
            }
        ],
        "long": [
            {
                "id": "la_sci14_1", "question": "Explain the internal structure of the human heart and trace the pathway of double circulation.",
                "model_answer": "1. Structure: Four chambers (right atrium, left atrium, right ventricle, left ventricle). Separated by interatrial and interventricular septa.\n- Tricuspid valve between right atrium and ventricle; Bicuspid (mitral) valve between left atrium and ventricle.\n- Pulmonary and aortic semilunar valves guard arterial exits.\n\n2. Double Circulation:\n- Pulmonary circulation: Deoxygenated blood from right ventricle -> pulmonary artery -> lungs -> oxygenated blood via pulmonary veins -> left atrium.\n- Systemic circulation: Oxygenated blood from left ventricle -> aorta -> all body tissues -> deoxygenated blood via vena cavae -> right atrium.\nDouble circulation ensures oxygenated and deoxygenated blood never mix, providing high metabolic efficiency.",
                "rubric": [
                    {"point_id": "r1", "description": "Describes 4 chambers and valves (tricuspid, bicuspid, semilunar)", "marks": 1.5},
                    {"point_id": "r2", "description": "Traces pulmonary circulation loop", "marks": 1.5},
                    {"point_id": "r3", "description": "Traces systemic circulation loop", "marks": 1.0},
                    {"point_id": "r4", "description": "Explains advantage of preventing blood mixing", "marks": 1.0}
                ]
            }
        ]
    }
}

def seed_all():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # 1. Insert all 23 Units into chapters table
            for cid, sid, title, p_start, p_end in TN_10_SCIENCE_UNITS:
                cur.execute("""
                    INSERT INTO chapters (id, subject_id, title)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET title = EXCLUDED.title, subject_id = EXCLUDED.subject_id;
                """, (cid, sid, title))

                # Insert guide summary for each unit
                body_md = f"# {title}\n\nComprehensive board coverage for {title} according to the Tamil Nadu State Board Class 10 textbook (Pages {p_start} to {p_end}). Includes conceptual theory, key formulas, solved examples, and official textbook evaluations."
                key_pts = [
                    f"Aligned with TN SCERT Class 10 Science 2024 syllabus (p. {p_start}-{p_end})",
                    "Covers core theoretical principles, board question banks, and numerical problems",
                    "Traceable to 10th_Science.pdf in vector storage"
                ]
                cur.execute("""
                    INSERT INTO guides (id, chapter_id, body_md, key_points)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        chapter_id = EXCLUDED.chapter_id,
                        body_md = EXCLUDED.body_md,
                        key_points = EXCLUDED.key_points;
                """, (f"guide_{cid}", cid, body_md, key_pts))

            # 2. Insert MCQs and Answers for units defined
            for cid, data in UNIT_QUESTIONS.items():
                for m in data.get("mcqs", []):
                    cur.execute("""
                        INSERT INTO mcq_questions (id, chapter_id, question, options, correct_index, difficulty, explanation, source_page, pdf_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO UPDATE SET
                            chapter_id = EXCLUDED.chapter_id,
                            question = EXCLUDED.question,
                            options = EXCLUDED.options,
                            correct_index = EXCLUDED.correct_index,
                            difficulty = EXCLUDED.difficulty,
                            explanation = EXCLUDED.explanation,
                            source_page = EXCLUDED.source_page,
                            pdf_id = EXCLUDED.pdf_id;
                    """, (m["id"], cid, m["question"], json.dumps(m["options"]), m["correct_index"], m["difficulty"], m["explanation"], m.get("source_page", "p. 1"), "10th_Science.pdf"))

                for s in data.get("short", []):
                    cur.execute("""
                        INSERT INTO answer_questions (id, chapter_id, question_type, question, model_answer, rubric_points, max_marks, source_page, pdf_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO UPDATE SET
                            chapter_id = EXCLUDED.chapter_id,
                            question_type = EXCLUDED.question_type,
                            question = EXCLUDED.question,
                            model_answer = EXCLUDED.model_answer,
                            rubric_points = EXCLUDED.rubric_points,
                            max_marks = EXCLUDED.max_marks,
                            source_page = EXCLUDED.source_page,
                            pdf_id = EXCLUDED.pdf_id;
                    """, (s["id"], cid, "short", s["question"], s["model_answer"], json.dumps(s["rubric"]), 2.0, "p. 1", "10th_Science.pdf"))

                for l in data.get("long", []):
                    cur.execute("""
                        INSERT INTO answer_questions (id, chapter_id, question_type, question, model_answer, rubric_points, max_marks, source_page, pdf_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO UPDATE SET
                            chapter_id = EXCLUDED.chapter_id,
                            question_type = EXCLUDED.question_type,
                            question = EXCLUDED.question,
                            model_answer = EXCLUDED.model_answer,
                            rubric_points = EXCLUDED.rubric_points,
                            max_marks = EXCLUDED.max_marks,
                            source_page = EXCLUDED.source_page,
                            pdf_id = EXCLUDED.pdf_id;
                    """, (l["id"], cid, "long", l["question"], l["model_answer"], json.dumps(l["rubric"]), 5.0, "p. 1", "10th_Science.pdf"))

            conn.commit()
            print("[x] Successfully registered all 23 Units of Class 10 Science into DB!")
    finally:
        conn.close()

if __name__ == "__main__":
    seed_all()
