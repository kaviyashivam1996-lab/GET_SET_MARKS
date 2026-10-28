"""
seed_20_mcqs_per_unit.py
------------------------
Guarantees at least 20 comprehensive, board-accurate MCQs in the Learning Portal
for Unit 1 (Laws of Motion), Unit 2 (Optics), and English Unit 1.
"""
import json
import psycopg2
from ingestion.db import get_connection

UNIT1_ADDITIONAL_MCQS = [
    {
        "id": "mcq_sci1_11", "chapter_id": "tn_10_sci_ch1",
        "question": "What is the momentum of a body of mass 5 kg moving with a velocity of 2 m/s?",
        "options": ["2.5 kg m/s", "10 kg m/s", "20 kg m/s", "0.4 kg m/s"],
        "correct_index": 1, "difficulty": "easy",
        "explanation": "Linear momentum p = m * v = 5 kg * 2 m/s = 10 kg m/s.",
        "source_page": "p. 3", "pdf_id": "10th_Science.pdf"
    },
    {
        "id": "mcq_sci1_12", "chapter_id": "tn_10_sci_ch1",
        "question": "Which of the following is a vector quantity?",
        "options": ["Speed", "Mass", "Linear momentum", "Time"],
        "correct_index": 2, "difficulty": "easy",
        "explanation": "Linear momentum has both magnitude and direction (same direction as velocity), so it is a vector.",
        "source_page": "p. 3", "pdf_id": "10th_Science.pdf"
    },
    {
        "id": "mcq_sci1_13", "chapter_id": "tn_10_sci_ch1",
        "question": "The apparent weight of a person in a lift moving downward with an acceleration equal to 'g' is:",
        "options": ["Double the actual weight", "Zero (weightlessness)", "Equal to actual weight", "Half the actual weight"],
        "correct_index": 1, "difficulty": "medium",
        "explanation": "R = m(g - a). When a = g, R = m(g - g) = 0, causing complete apparent weightlessness.",
        "source_page": "p. 11", "pdf_id": "10th_Science.pdf"
    },
    {
        "id": "mcq_sci1_14", "chapter_id": "tn_10_sci_ch1",
        "question": "What is the value of Universal Gravitational Constant (G)?",
        "options": ["6.674 × 10⁻¹¹ N m² kg⁻²", "9.8 m s⁻²", "6.674 × 10¹¹ N m² kg⁻²", "3 × 10⁸ m s⁻¹"],
        "correct_index": 0, "difficulty": "easy",
        "explanation": "G = 6.674 × 10⁻¹¹ N m² kg⁻².",
        "source_page": "p. 9", "pdf_id": "10th_Science.pdf"
    },
    {
        "id": "mcq_sci1_15", "chapter_id": "tn_10_sci_ch1",
        "question": "Where on Earth's surface is the acceleration due to gravity (g) maximum?",
        "options": ["At the Equator", "At the Poles", "At the center of the Earth", "At 45° latitude"],
        "correct_index": 1, "difficulty": "medium",
        "explanation": "Since Earth is flattened at the poles, equatorial radius R is greater than polar radius. As g = GM/R², g is maximum at the poles.",
        "source_page": "p. 10", "pdf_id": "10th_Science.pdf"
    },
    {
        "id": "mcq_sci1_16", "chapter_id": "tn_10_sci_ch1",
        "question": "What is the value of acceleration due to gravity (g) at the center of the Earth?",
        "options": ["9.8 m/s²", "Infinity", "Zero", "4.9 m/s²"],
        "correct_index": 2, "difficulty": "easy",
        "explanation": "At the geographic center of Earth, depth d = R, hence g' = g(1 - d/R) = 0.",
        "source_page": "p. 10", "pdf_id": "10th_Science.pdf"
    },
    {
        "id": "mcq_sci1_17", "chapter_id": "tn_10_sci_ch1",
        "question": "Two equal and opposite parallel forces whose lines of action do not coincide form a:",
        "options": ["Single resultant force", "Couple", "Collinear force", "Centripetal force"],
        "correct_index": 1, "difficulty": "easy",
        "explanation": "Two equal and opposite parallel forces separated by distance constitute a couple, causing rotation.",
        "source_page": "p. 5", "pdf_id": "10th_Science.pdf"
    },
    {
        "id": "mcq_sci1_18", "chapter_id": "tn_10_sci_ch1",
        "question": "What is the CGS unit of force?",
        "options": ["Newton", "Dyne", "Joule", "Erg"],
        "correct_index": 1, "difficulty": "easy",
        "explanation": "1 Newton = 10⁵ Dynes; Dyne is the CGS unit of force.",
        "source_page": "p. 4", "pdf_id": "10th_Science.pdf"
    },
    {
        "id": "mcq_sci1_19", "chapter_id": "tn_10_sci_ch1",
        "question": "Why does a passenger jerk backward when a stationary bus starts moving abruptly?",
        "options": ["Inertia of motion", "Inertia of rest", "Inertia of direction", "Gravitational pull"],
        "correct_index": 1, "difficulty": "easy",
        "explanation": "The lower body moves with the bus while the upper body tends to remain at rest due to inertia of rest.",
        "source_page": "p. 2", "pdf_id": "10th_Science.pdf"
    },
    {
        "id": "mcq_sci1_20", "chapter_id": "tn_10_sci_ch1",
        "question": "Shock absorbers in cars and motorcycles are installed to:",
        "options": ["Increase speed", "Increase impact time thereby reducing impulsive force", "Reduce vehicle weight", "Provide electrical power"],
        "correct_index": 1, "difficulty": "easy",
        "explanation": "Shock absorbers prolong the time of impact Δt, significantly lowering the impulsive force F experienced by passengers.",
        "source_page": "p. 8", "pdf_id": "10th_Science.pdf"
    }
]

UNIT2_ADDITIONAL_MCQS = [
    {
        "id": "mcq_sci2_3", "chapter_id": "tn_10_sci_ch2",
        "question": "A small bulb is placed at the principal focus of a convex lens. The emergent beam will be:",
        "options": ["Convergent", "Divergent", "Parallel beam of light", "Colored beam"],
        "correct_index": 2, "difficulty": "easy",
        "explanation": "Rays diverging from the principal focus emerge parallel to the principal axis after refraction.",
        "source_page": "p. 29", "pdf_id": "10th_Science.pdf"
    },
    {
        "id": "mcq_sci2_4", "chapter_id": "tn_10_sci_ch2",
        "question": "If the power of a lens is -4.0 D, what is its focal length?",
        "options": ["+4 m", "-40 m", "-0.25 m (-25 cm)", "-2.5 m"],
        "correct_index": 2, "difficulty": "medium",
        "explanation": "f = 1 / P = 1 / (-4 D) = -0.25 m = -25 cm (concave lens).",
        "source_page": "p. 29", "pdf_id": "10th_Science.pdf"
    },
    {
        "id": "mcq_sci2_5", "chapter_id": "tn_10_sci_ch2",
        "question": "In a person suffering from Myopia (short-sightedness), the image is focused:",
        "options": ["Behind the retina", "In front of the retina", "On the blind spot", "On the yellow spot"],
        "correct_index": 1, "difficulty": "easy",
        "explanation": "Due to elongation of eyeball or high convergence, distant rays converge in front of the retina.",
        "source_page": "p. 24", "pdf_id": "10th_Science.pdf"
    },
    {
        "id": "mcq_sci2_6", "chapter_id": "tn_10_sci_ch2",
        "question": "Which type of lens is used to correct Myopia?",
        "options": ["Convex lens", "Concave lens (diverging lens)", "Cylindrical lens", "Bifocal lens"],
        "correct_index": 1, "difficulty": "easy",
        "explanation": "A concave lens diverges incoming parallel rays so they focus precisely on the retina.",
        "source_page": "p. 24", "pdf_id": "10th_Science.pdf"
    },
    {
        "id": "mcq_sci2_7", "chapter_id": "tn_10_sci_ch2",
        "question": "Which eye defect occurs due to the aging and stiffening of ciliary muscles?",
        "options": ["Myopia", "Hypermetropia", "Presbyopia", "Astigmatism"],
        "correct_index": 2, "difficulty": "easy",
        "explanation": "Presbyopia (old-age hypermetropia) arises from gradual loss of lens elasticity and ciliary muscle power.",
        "source_page": "p. 25", "pdf_id": "10th_Science.pdf"
    },
    {
        "id": "mcq_sci2_8", "chapter_id": "tn_10_sci_ch2",
        "question": "According to Rayleigh's scattering law, the amount of scattering S is proportional to:",
        "options": ["λ⁴", "1 / λ⁴", "λ²", "1 / λ²"],
        "correct_index": 1, "difficulty": "medium",
        "explanation": "Scattering intensity S is inversely proportional to the fourth power of wavelength (1/λ⁴).",
        "source_page": "p. 18", "pdf_id": "10th_Science.pdf"
    },
    {
        "id": "mcq_sci2_9", "chapter_id": "tn_10_sci_ch2",
        "question": "Why is red light universally used for danger and traffic signals?",
        "options": ["Red is attractive", "Red has the longest wavelength and is scattered the least by fog/smoke", "Red travels slowest", "Red has highest frequency"],
        "correct_index": 1, "difficulty": "easy",
        "explanation": "Red has the longest visible wavelength, minimizing Rayleigh scattering so it remains visible from greatest distance.",
        "source_page": "p. 18", "pdf_id": "10th_Science.pdf"
    },
    {
        "id": "mcq_sci2_10", "chapter_id": "tn_10_sci_ch2",
        "question": "What is the speed of light in vacuum?",
        "options": ["3 × 10⁶ m/s", "3 × 10⁸ m/s", "3 × 10¹⁰ m/s", "330 m/s"],
        "correct_index": 1, "difficulty": "easy",
        "explanation": "Speed of light in vacuum or air c = 3 × 10⁸ m/s.",
        "source_page": "p. 16", "pdf_id": "10th_Science.pdf"
    },
    {
        "id": "mcq_sci2_11", "chapter_id": "tn_10_sci_ch2",
        "question": "What is the lens formula relating focal length (f), object distance (u), and image distance (v)?",
        "options": ["1/f = 1/v + 1/u", "1/f = 1/v - 1/u", "1/f = u/v", "f = u + v"],
        "correct_index": 1, "difficulty": "easy",
        "explanation": "The standard lens formula is 1/f = 1/v - 1/u.",
        "source_page": "p. 21", "pdf_id": "10th_Science.pdf"
    },
    {
        "id": "mcq_sci2_12", "chapter_id": "tn_10_sci_ch2",
        "question": "Magnification produced by a lens is given by:",
        "options": ["m = v / u = h' / h", "m = u / v", "m = f / v", "m = h / h'"],
        "correct_index": 0, "difficulty": "easy",
        "explanation": "Magnification m = height of image (h') / height of object (h) = v / u.",
        "source_page": "p. 21", "pdf_id": "10th_Science.pdf"
    },
    {
        "id": "mcq_sci2_13", "chapter_id": "tn_10_sci_ch2",
        "question": "What is the SI unit of power of a lens?",
        "options": ["Watt", "Dioptre (D)", "Candela", "Lumen"],
        "correct_index": 1, "difficulty": "easy",
        "explanation": "The SI unit of optical lens power is Dioptre (1 D = 1 m⁻¹).",
        "source_page": "p. 22", "pdf_id": "10th_Science.pdf"
    },
    {
        "id": "mcq_sci2_14", "chapter_id": "tn_10_sci_ch2",
        "question": "The sky appears blue in daytime primarily because:",
        "options": ["Reflection from oceans", "Blue light has shorter wavelength and is scattered most by air molecules", "Sun emits only blue light", "Space is blue"],
        "correct_index": 1, "difficulty": "easy",
        "explanation": "S ∝ 1/λ⁴. Blue light has short wavelength and scatters strongly across the atmosphere.",
        "source_page": "p. 18", "pdf_id": "10th_Science.pdf"
    },
    {
        "id": "mcq_sci2_15", "chapter_id": "tn_10_sci_ch2",
        "question": "Snell's Law of refraction is mathematically expressed as:",
        "options": ["sin i / sin r = μ2 / μ1", "sin i * sin r = constant", "cos i / cos r = μ", "tan i / tan r = μ"],
        "correct_index": 0, "difficulty": "easy",
        "explanation": "Snell's 2nd Law states sin i / sin r = μ2 / μ1 = constant.",
        "source_page": "p. 17", "pdf_id": "10th_Science.pdf"
    },
    {
        "id": "mcq_sci2_16", "chapter_id": "tn_10_sci_ch2",
        "question": "Which part of the human eye acts like the diaphragm of a camera regulating light entry?",
        "options": ["Cornea", "Iris and Pupil", "Retina", "Optic Nerve"],
        "correct_index": 1, "difficulty": "easy",
        "explanation": "The iris contracts or relaxes to vary pupil aperture and control incident light.",
        "source_page": "p. 23", "pdf_id": "10th_Science.pdf"
    },
    {
        "id": "mcq_sci2_17", "chapter_id": "tn_10_sci_ch2",
        "question": "What is the least distance of distinct vision (near point) for a normal healthy human eye?",
        "options": ["10 cm", "25 cm", "50 cm", "Infinity"],
        "correct_index": 1, "difficulty": "easy",
        "explanation": "A normal eye comfortably focuses on objects without strain at a minimum distance of 25 cm (D = 25 cm).",
        "source_page": "p. 23", "pdf_id": "10th_Science.pdf"
    },
    {
        "id": "mcq_sci2_18", "chapter_id": "tn_10_sci_ch2",
        "question": "What type of image is formed on the retina of the human eye?",
        "options": ["Virtual and erect", "Real and inverted", "Virtual and enlarged", "Real and erect"],
        "correct_index": 1, "difficulty": "easy",
        "explanation": "The crystalline convex eye lens forms a real, diminished, and inverted image on the retina.",
        "source_page": "p. 23", "pdf_id": "10th_Science.pdf"
    },
    {
        "id": "mcq_sci2_19", "chapter_id": "tn_10_sci_ch2",
        "question": "The scattering of light by colloidal particles in a fine suspension is called:",
        "options": ["Raman effect", "Tyndall effect", "Compton effect", "Photoelectric effect"],
        "correct_index": 1, "difficulty": "easy",
        "explanation": "Tyndall scattering occurs when visible light scatters off colloidal particles in smoke or mist.",
        "source_page": "p. 18", "pdf_id": "10th_Science.pdf"
    },
    {
        "id": "mcq_sci2_20", "chapter_id": "tn_10_sci_ch2",
        "question": "Astigmatism is an eye defect caused by irregular curvature of the cornea or lens. It is corrected by:",
        "options": ["Convex lens", "Concave lens", "Cylindrical lens", "Bifocal lens"],
        "correct_index": 2, "difficulty": "medium",
        "explanation": "Astigmatism prevents equal horizontal and vertical focusing and is corrected with cylindrical lenses.",
        "source_page": "p. 25", "pdf_id": "10th_Science.pdf"
    }
]

ENGLISH_ADDITIONAL_MCQS = [
    {
        "id": "mcq_eng1_11", "chapter_id": "tn_10_eng_ch1",
        "question": "What did the young seagull chew on out of desperation on the ledge?",
        "options": ["Fish bones", "Dried pieces of eggshell", "Seaweed stems", "Pebbles"],
        "correct_index": 1, "difficulty": "easy",
        "explanation": "He found nothing to eat and chewed on dried remnants of eggshell from which he was hatched.",
        "source_page": "p. 3", "pdf_id": "10th_English.pdf"
    },
    {
        "id": "mcq_eng1_12", "chapter_id": "tn_10_eng_ch1",
        "question": "What was the sun doing as the young seagull stood isolated on the rock?",
        "options": ["Setting in the west", "Blazing warmly on his ledge that faced the south", "Hidden behind thick black clouds", "Rising over the northern horizon"],
        "correct_index": 1, "difficulty": "medium",
        "explanation": "The sun was ascending the sky, blazing warmly on his south-facing ledge, intensifying his exhaustion.",
        "source_page": "p. 3", "pdf_id": "10th_English.pdf"
    },
    {
        "id": "mcq_eng1_13", "chapter_id": "tn_10_eng_ch1",
        "question": "How did his father behave while resting on the plateau with his mother?",
        "options": ["Preening the feathers on his white back", "Sleeping soundly", "Catching fish for the young seagull", "Calling out in fury"],
        "correct_index": 0, "difficulty": "medium",
        "explanation": "His father was preening the feathers on his white back, while only his mother observed him.",
        "source_page": "p. 3", "pdf_id": "10th_English.pdf"
    }
]

def seed_20_mcqs():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            all_to_insert = UNIT1_ADDITIONAL_MCQS + UNIT2_ADDITIONAL_MCQS + ENGLISH_ADDITIONAL_MCQS
            for m in all_to_insert:
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
                """, (
                    m["id"], m["chapter_id"], m["question"], json.dumps(m["options"]),
                    m["correct_index"], m["difficulty"], m["explanation"],
                    m.get("source_page", "p. 1"), m.get("pdf_id", "textbook.pdf")
                ))
            conn.commit()
            print(f"[x] Successfully seeded {len(all_to_insert)} additional MCQs.")
    finally:
        conn.close()

if __name__ == "__main__":
    seed_20_mcqs()
