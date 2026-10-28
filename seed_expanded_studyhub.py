"""
seed_expanded_studyhub.py
-------------------------
Populates at least:
  - 20 MCQs
  - 10 Short Answer Questions (with model answers & rubric points)
  - 5 Long Answer Questions (with detailed model answers & rubric points)

for Class 10 Tamil Nadu State Board (English & Science).
"""
import json
import psycopg2
from ingestion.db import get_connection

# Ensure Science units exist in chapters table
SCIENCE_CHAPTERS = [
    ("tn_10_sci_ch1", "tn_10_science", "Unit 1: Laws of Motion"),
    ("tn_10_sci_ch2", "tn_10_science", "Unit 2: Optics"),
]

# =============================================================================
# 1. MCQS (>= 20 questions)
# =============================================================================
MCQS = [
    # --- Unit 1: His First Flight (Class 10 English) ---
    {
        "id": "mcq_eng1_1", "chapter_id": "tn_10_eng_ch1",
        "question": "Why was the young seagull afraid to fly?",
        "options": ["He had injured wings", "He was afraid the sea was too deep and his wings would not support him", "He disliked fish", "His parents forbade him to fly"],
        "correct_index": 1, "difficulty": "easy",
        "explanation": "He looked at the vast sea below and was frightened that his wings could never sustain his weight.",
        "source_page": "p. 2", "pdf_id": "10th_English.pdf"
    },
    {
        "id": "mcq_eng1_2", "chapter_id": "tn_10_eng_ch1",
        "question": "What compelled the young seagull to finally dive off the ledge?",
        "options": ["A sudden gust of wind", "Extreme hunger when his mother maddened him with fish", "A push from his father", "A predatory bird attacking him"],
        "correct_index": 1, "difficulty": "easy",
        "explanation": "Maddened by hunger, he dived towards the fish in his mother's beak and fell into space.",
        "source_page": "p. 3", "pdf_id": "10th_English.pdf"
    },
    {
        "id": "mcq_eng1_3", "chapter_id": "tn_10_eng_ch1",
        "question": "Who is the author of the story 'His First Flight'?",
        "options": ["Liam O'Flaherty", "Alphonse Daudet", "Satyajit Ray", "Arthur Conan Doyle"],
        "correct_index": 0, "difficulty": "easy",
        "explanation": "Liam O'Flaherty was an Irish novelist who wrote this inspirational story.",
        "source_page": "p. 1", "pdf_id": "10th_English.pdf"
    },
    {
        "id": "mcq_eng1_4", "chapter_id": "tn_10_eng_ch1",
        "question": "How long had the young seagull stayed alone on the ledge without food?",
        "options": ["12 hours", "24 hours", "36 hours", "48 hours"],
        "correct_index": 1, "difficulty": "medium",
        "explanation": "Since the previous day, twenty-four hours had elapsed without anyone approaching him.",
        "source_page": "p. 2", "pdf_id": "10th_English.pdf"
    },
    {
        "id": "mcq_eng1_5", "chapter_id": "tn_10_eng_ch1",
        "question": "What did the young seagull feel when he spread his wings in the air?",
        "options": ["He felt dizzy and sank", "The wind rushed against his breast feathers and he realized he was soaring", "His wings snapped painfully", "He hit the rock surface"],
        "correct_index": 1, "difficulty": "medium",
        "explanation": "The wind rushed against his breast feathers, under his stomach, and against his wingtips as fear departed.",
        "source_page": "p. 3", "pdf_id": "10th_English.pdf"
    },
    {
        "id": "mcq_eng1_6", "chapter_id": "tn_10_eng_ch1",
        "question": "What was the green flooring that the young seagull's feet sank into?",
        "options": ["Green grass pasture", "The green sea water", "Moss on the rock", "A fishing vessel deck"],
        "correct_index": 1, "difficulty": "easy",
        "explanation": "The green flooring was the emerald-green sea water upon which he successfully floated.",
        "source_page": "p. 4", "pdf_id": "10th_English.pdf"
    },
    {
        "id": "mcq_eng1_7", "chapter_id": "tn_10_eng_ch1",
        "question": "What kind of fish was the mother seagull tearing at on the plateau?",
        "options": ["Salmon", "Dogfish", "Herring", "Mackerel"],
        "correct_index": 1, "difficulty": "medium",
        "explanation": "She tore at a piece of fish (dogfish) lying at her feet to tempt him.",
        "source_page": "p. 3", "pdf_id": "10th_English.pdf"
    },
    {
        "id": "mcq_eng1_8", "chapter_id": "tn_10_eng_ch1",
        "question": "What did his parents and siblings offer him in praise after he floated on the sea?",
        "options": ["Scraps of dogfish", "Sea snails", "Crabs", "Grains"],
        "correct_index": 0, "difficulty": "easy",
        "explanation": "His family circled around him, screaming praise and offering scraps of dogfish from their beaks.",
        "source_page": "p. 4", "pdf_id": "10th_English.pdf"
    },
    {
        "id": "mcq_eng1_9", "chapter_id": "tn_10_eng_ch1",
        "question": "What was the emotional reaction of his brothers and sister when they learned to fly?",
        "options": ["They wept in fear", "They ran to the brink of the ledge, flapped their wings and flew away", "They refused to jump", "They hid inside holes"],
        "correct_index": 1, "difficulty": "easy",
        "explanation": "His two brothers and sister had shorter wings yet boldly ran to the edge and flew.",
        "source_page": "p. 2", "pdf_id": "10th_English.pdf"
    },
    {
        "id": "mcq_eng1_10", "chapter_id": "tn_10_eng_ch1",
        "question": "What moral or life lesson does 'His First Flight' convey?",
        "options": ["Relying on others brings wealth", "Overcoming fear and taking the first step leads to success", "Nature is cruel and punishing", "Birds have easier lives than humans"],
        "correct_index": 1, "difficulty": "easy",
        "explanation": "Courage and self-confidence are essential to conquer fear and achieve self-reliance.",
        "source_page": "p. 4", "pdf_id": "10th_English.pdf"
    },

    # --- Unit 1: Laws of Motion (Class 10 Science) ---
    {
        "id": "mcq_sci1_1", "chapter_id": "tn_10_sci_ch1",
        "question": "Inertia of a body depends on:",
        "options": ["Weight of the object", "Acceleration due to gravity", "Mass of the object", "Both weight and gravity"],
        "correct_index": 2, "difficulty": "easy",
        "explanation": "Mass of a body is the quantitative measure of its inertia (greater mass = greater inertia).",
        "source_page": "p. 13", "pdf_id": "Class_10_Science_English_2024.pdf"
    },
    {
        "id": "mcq_sci1_2", "chapter_id": "tn_10_sci_ch1",
        "question": "Impulse is equal to:",
        "options": ["Rate of change of momentum", "Rate of force and time", "Change of momentum (J = Δp)", "Rate of change of mass"],
        "correct_index": 2, "difficulty": "easy",
        "explanation": "Impulse J = F * Δt = change in linear momentum (Δp).",
        "source_page": "p. 13", "pdf_id": "Class_10_Science_English_2024.pdf"
    },
    {
        "id": "mcq_sci1_3", "chapter_id": "tn_10_sci_ch1",
        "question": "Newton's third law of motion is applicable for:",
        "options": ["A body at rest", "A body in motion", "Both bodies at rest and in motion", "Only bodies with equal masses"],
        "correct_index": 2, "difficulty": "easy",
        "explanation": "For every action there is an equal and opposite reaction, valid whether bodies are resting or moving.",
        "source_page": "p. 13", "pdf_id": "Class_10_Science_English_2024.pdf"
    },
    {
        "id": "mcq_sci1_4", "chapter_id": "tn_10_sci_ch1",
        "question": "Plotting momentum on Y-axis and time on X-axis, the slope of the momentum-time graph gives:",
        "options": ["Impulsive force", "Acceleration", "Force", "Rate of force"],
        "correct_index": 2, "difficulty": "medium",
        "explanation": "Slope = dp/dt = Force (by Newton's second law: F = dp/dt).",
        "source_page": "p. 13", "pdf_id": "Class_10_Science_English_2024.pdf"
    },
    {
        "id": "mcq_sci1_5", "chapter_id": "tn_10_sci_ch1",
        "question": "In which of the following activities is the turning effect of force (torque) used?",
        "options": ["Swimming", "Tennis", "Cycling", "Hockey"],
        "correct_index": 2, "difficulty": "easy",
        "explanation": "Turning pedals in cycling applies torque to rotate the sprocket wheel.",
        "source_page": "p. 13", "pdf_id": "Class_10_Science_English_2024.pdf"
    },
    {
        "id": "mcq_sci1_6", "chapter_id": "tn_10_sci_ch1",
        "question": "The SI unit of acceleration due to gravity 'g' is m·s⁻². It can also be expressed as:",
        "options": ["cm·s⁻¹", "N·kg⁻¹", "N·m²·kg⁻¹", "cm²·s⁻²"],
        "correct_index": 1, "difficulty": "medium",
        "explanation": "g = F/m = Newton / kilogram = N·kg⁻¹.",
        "source_page": "p. 13", "pdf_id": "Class_10_Science_English_2024.pdf"
    },
    {
        "id": "mcq_sci1_7", "chapter_id": "tn_10_sci_ch1",
        "question": "One kilogram force (1 kgf) equals:",
        "options": ["9.8 dyne", "9.8 × 10⁴ N", "98 × 10⁴ dyne", "980 dyne"],
        "correct_index": 2, "difficulty": "medium",
        "explanation": "1 kgf = 9.8 N = 9.8 × 10⁵ dyne = 98 × 10⁴ dyne.",
        "source_page": "p. 13", "pdf_id": "Class_10_Science_English_2024.pdf"
    },
    {
        "id": "mcq_sci1_8", "chapter_id": "tn_10_sci_ch1",
        "question": "The mass of a body is M kg on Earth. When taken to a planet of radius half that of Earth, its mass will be:",
        "options": ["4 M", "2 M", "M/4", "M"],
        "correct_index": 3, "difficulty": "easy",
        "explanation": "Mass is an intrinsic property that remains constant everywhere in the universe (only weight changes).",
        "source_page": "p. 13", "pdf_id": "Class_10_Science_English_2024.pdf"
    },
    {
        "id": "mcq_sci1_9", "chapter_id": "tn_10_sci_ch1",
        "question": "If the Earth shrinks to 50% of its radius with mass remaining constant, the weight of a body on Earth will:",
        "options": ["Decrease by 50%", "Increase by 50%", "Decrease by 25%", "Increase by 300%"],
        "correct_index": 3, "difficulty": "hard",
        "explanation": "g' = GM / (R/2)² = 4g. The weight increases from W to 4W, which is an increase of 3W (300%).",
        "source_page": "p. 13", "pdf_id": "Class_10_Science_English_2024.pdf"
    },
    {
        "id": "mcq_sci1_10", "chapter_id": "tn_10_sci_ch1",
        "question": "Which principle(s) are required for rocket propulsion?",
        "options": ["Newton's third law of motion only", "Newton's universal law of gravitation", "Law of conservation of linear momentum", "Both Newton's third law and conservation of linear momentum"],
        "correct_index": 3, "difficulty": "easy",
        "explanation": "Rocket propulsion is based on Newton's 3rd law (thrust) and the law of conservation of linear momentum.",
        "source_page": "p. 14", "pdf_id": "Class_10_Science_English_2024.pdf"
    },

    # --- Extra MCQs for Unit 2: Optics ---
    {
        "id": "mcq_sci2_1", "chapter_id": "tn_10_sci_ch2",
        "question": "The refractive index of substances A, B, C, D are 1.31, 1.43, 1.33, 2.4. Speed of light is maximum in:",
        "options": ["A (1.31)", "B (1.43)", "C (1.33)", "D (2.4)"],
        "correct_index": 0, "difficulty": "easy",
        "explanation": "v = c/μ. The smaller the refractive index, the higher the speed of light.",
        "source_page": "p. 29", "pdf_id": "Class_10_Science_English_2024.pdf"
    },
    {
        "id": "mcq_sci2_2", "chapter_id": "tn_10_sci_ch2",
        "question": "Where should an object be placed so that a real, inverted image of the same size is formed by a convex lens?",
        "options": ["At focus f", "At 2f", "At infinity", "Between f and 2f"],
        "correct_index": 1, "difficulty": "easy",
        "explanation": "When an object is placed at 2f, a real, inverted image of identical size is formed at 2f on the other side.",
        "source_page": "p. 29", "pdf_id": "Class_10_Science_English_2024.pdf"
    }
]

# =============================================================================
# 2. SHORT ANSWER QUESTIONS (>= 10 questions)
# =============================================================================
SHORT_ANSWERS = [
    # --- English Unit 1 ---
    {
        "id": "sa_eng1_1", "chapter_id": "tn_10_eng_ch1", "question_type": "short",
        "question": "How did the young seagull's parents try to teach him to fly?",
        "model_answer": "His parents flew around calling shrilly, scolding him, and threatening to let him starve on his ledge unless he flew away.",
        "rubric_points": [
            {"point_id": "r1", "description": "Mentions calling shrilly and scolding him", "marks": 1.0},
            {"point_id": "r2", "description": "Mentions threatening starvation if he did not fly", "marks": 1.0}
        ],
        "max_marks": 2.0, "source_page": "p. 2", "pdf_id": "10th_English.pdf"
    },
    {
        "id": "sa_eng1_2", "chapter_id": "tn_10_eng_ch1", "question_type": "short",
        "question": "What did the young seagull do to attract his family's attention while standing on the ledge?",
        "model_answer": "He stepped slowly out to the brink of the ledge, stood on one leg with the other leg hidden under his wing, and closed one eye, then the other, pretending to be asleep.",
        "rubric_points": [
            {"point_id": "r1", "description": "Stood on one leg hiding the other", "marks": 1.0},
            {"point_id": "r2", "description": "Pretended to fall asleep to gain sympathy", "marks": 1.0}
        ],
        "max_marks": 2.0, "source_page": "p. 3", "pdf_id": "10th_English.pdf"
    },
    {
        "id": "sa_eng1_3", "chapter_id": "tn_10_eng_ch1", "question_type": "short",
        "question": "How did the young bird feel when his feet touched the sea water?",
        "model_answer": "His green legs sank into the water and he screamed with fright, attempting to flap his wings. But exhausted by hunger, his belly touched the water and he began floating naturally without sinking.",
        "rubric_points": [
            {"point_id": "r1", "description": "Initial panic and scream as feet sank", "marks": 1.0},
            {"point_id": "r2", "description": "Realization of floating safely as belly touched water", "marks": 1.0}
        ],
        "max_marks": 2.0, "source_page": "p. 4", "pdf_id": "10th_English.pdf"
    },
    {
        "id": "sa_eng1_4", "chapter_id": "tn_10_eng_ch1", "question_type": "short",
        "question": "What did his older brother catch during his flight training?",
        "model_answer": "His older brother caught his first herring and devoured it while standing on a rock as his proud parents circled around him raising a proud cackle.",
        "rubric_points": [
            {"point_id": "r1", "description": "Caught his first herring fish", "marks": 1.0},
            {"point_id": "r2", "description": "Parents circled with proud cackling", "marks": 1.0}
        ],
        "max_marks": 2.0, "source_page": "p. 2", "pdf_id": "10th_English.pdf"
    },
    {
        "id": "sa_eng1_5", "chapter_id": "tn_10_eng_ch1", "question_type": "short",
        "question": "Why did the young seagull utter a joyful scream when he saw his mother flying toward him?",
        "model_answer": "He uttered a joyful scream because his mother had picked up a piece of fish and was flying across the sea toward his ledge to feed him.",
        "rubric_points": [
            {"point_id": "r1", "description": "Saw mother carrying piece of fish in beak", "marks": 1.0},
            {"point_id": "r2", "description": "Anticipated relief from intense hunger", "marks": 1.0}
        ],
        "max_marks": 2.0, "source_page": "p. 3", "pdf_id": "10th_English.pdf"
    },

    # --- Science Unit 1: Laws of Motion ---
    {
        "id": "sa_sci1_1", "chapter_id": "tn_10_sci_ch1", "question_type": "short",
        "question": "Define inertia and give its classification.",
        "model_answer": "Inertia is the inherent property of a body to resist any change in its state of rest or uniform motion unless acted upon by an external unbalanced force. It is classified into: (1) Inertia of rest, (2) Inertia of motion, and (3) Inertia of direction.",
        "rubric_points": [
            {"point_id": "r1", "description": "Accurate scientific definition of inertia", "marks": 1.0},
            {"point_id": "r2", "description": "List all 3 types (rest, motion, direction)", "marks": 1.0}
        ],
        "max_marks": 2.0, "source_page": "p. 14", "pdf_id": "Class_10_Science_English_2024.pdf"
    },
    {
        "id": "sa_sci1_2", "chapter_id": "tn_10_sci_ch1", "question_type": "short",
        "question": "Differentiate between mass and weight.",
        "model_answer": "Mass is the quantity of matter contained in a body; it is a scalar quantity and remains constant everywhere (SI unit: kg). Weight is the gravitational force exerted on a body (W = mg); it is a vector quantity that varies with location (SI unit: Newton).",
        "rubric_points": [
            {"point_id": "r1", "description": "Mass: scalar, constant, unit kg", "marks": 1.0},
            {"point_id": "r2", "description": "Weight: vector, varies (W=mg), unit Newton", "marks": 1.0}
        ],
        "max_marks": 2.0, "source_page": "p. 14", "pdf_id": "Class_10_Science_English_2024.pdf"
    },
    {
        "id": "sa_sci1_3", "chapter_id": "tn_10_sci_ch1", "question_type": "short",
        "question": "State Newton's second law of motion.",
        "model_answer": "Newton's second law states that the force acting on a body is directly proportional to the rate of change of its linear momentum and the change takes place in the direction of the force (F = ma).",
        "rubric_points": [
            {"point_id": "r1", "description": "States force is proportional to rate of change of momentum", "marks": 1.0},
            {"point_id": "r2", "description": "Specifies direction of change and formula F = ma", "marks": 1.0}
        ],
        "max_marks": 2.0, "source_page": "p. 14", "pdf_id": "Class_10_Science_English_2024.pdf"
    },
    {
        "id": "sa_sci1_4", "chapter_id": "tn_10_sci_ch1", "question_type": "short",
        "question": "While catching a cricket ball, the fielder lowers his hands backwards. Why?",
        "model_answer": "By pulling hands backward, the fielder increases the contact time (Δt) during which momentum drops to zero. As Impulse J = F * Δt is constant, increasing time decreases the impact force F, preventing hand injury.",
        "rubric_points": [
            {"point_id": "r1", "description": "Explains that contact time (Δt) is increased", "marks": 1.0},
            {"point_id": "r2", "description": "Connects increased time to reduced impulsive force on hands", "marks": 1.0}
        ],
        "max_marks": 2.0, "source_page": "p. 14", "pdf_id": "Class_10_Science_English_2024.pdf"
    },
    {
        "id": "sa_sci1_5", "chapter_id": "tn_10_sci_ch1", "question_type": "short",
        "question": "State the principle of moments.",
        "model_answer": "The principle of moments states that when a number of like or unlike parallel forces act on a rigid body and the body is in equilibrium, the algebraic sum of moments about any point is zero: Sum of clockwise moments = Sum of anticlockwise moments.",
        "rubric_points": [
            {"point_id": "r1", "description": "States body in rotational equilibrium", "marks": 1.0},
            {"point_id": "r2", "description": "Formula: Clockwise moment = Anticlockwise moment", "marks": 1.0}
        ],
        "max_marks": 2.0, "source_page": "p. 14", "pdf_id": "Class_10_Science_English_2024.pdf"
    },
    {
        "id": "sa_sci1_6", "chapter_id": "tn_10_sci_ch1", "question_type": "short",
        "question": "Why is a spanner with a long handle preferred to loosen tight nuts?",
        "model_answer": "Torque is given by τ = F * d (force × perpendicular distance). A longer handle increases the distance (d) from the axis of rotation, allowing a person to produce a large turning moment with minimal applied force.",
        "rubric_points": [
            {"point_id": "r1", "description": "Quotes formula τ = F * d", "marks": 1.0},
            {"point_id": "r2", "description": "Explains larger distance yields greater torque with less effort", "marks": 1.0}
        ],
        "max_marks": 2.0, "source_page": "p. 14", "pdf_id": "Class_10_Science_English_2024.pdf"
    }
]

# =============================================================================
# 3. LONG ANSWER QUESTIONS (>= 5 questions)
# =============================================================================
LONG_ANSWERS = [
    # --- English Unit 1 ---
    {
        "id": "la_eng1_1", "chapter_id": "tn_10_eng_ch1", "question_type": "long",
        "question": "Describe the trials and triumphs of the young seagull in making his first flight.",
        "model_answer": (
            "The young seagull was paralyzed by fear. Although his younger siblings with shorter wings flew effortlessly, "
            "he felt convinced his wings could never support him over the vast sea. His parents scolded and threatened him "
            "with starvation, abandoning him on the ledge for 24 hours.\n\n"
            "Tormented by hunger, he watched his mother tearing at fish. She flew toward him with a piece in her beak but "
            "halted just beyond his reach. Maddened by hunger, the seagull took an involuntary dive into empty space. "
            "Monstrous terror gripped him for a minute, but suddenly his wings opened outward, wind rushed against his feathers, "
            "and he found himself soaring. He cried with triumph, mastered diving and skimming the waves, and finally rested "
            "safely on the green sea, greeted by his praising family."
        ),
        "rubric_points": [
            {"point_id": "r1", "description": "Depicts initial fear and comparison with siblings", "marks": 1.0},
            {"point_id": "r2", "description": "Describes parents' tough love strategy and starvation", "marks": 1.0},
            {"point_id": "r3", "description": "Explains mother's clever bait and involuntary dive", "marks": 1.5},
            {"point_id": "r4", "description": "Details sensations of soaring and joyful landing", "marks": 1.5}
        ],
        "max_marks": 5.0, "source_page": "p. 2 - p. 4", "pdf_id": "10th_English.pdf"
    },
    {
        "id": "la_eng1_2", "chapter_id": "tn_10_eng_ch1", "question_type": "long",
        "question": "How did parental guidance and motherly wisdom play a crucial role in the young seagull's survival?",
        "model_answer": (
            "Parental encouragement in nature often requires firmness rather than pampering. The young seagull's parents recognized "
            "that spoon-feeding him would leave him helpless for life. When gentle coaxing failed, they employed tough love—calling shrilly, "
            "upbraiding him, and letting him fast on the bare ledge.\n\n"
            "The mother's ingenuity was decisive: knowing that instinct surpasses fear when hunger is desperate, she brought food near him "
            "and halted. This compelled him to jump into the air. By turning his desperation into action, she activated his latent instincts. "
            "Once he conquered the initial panic, his family joined him, cackling praise and feeding him dogfish. Thus, wise parental firmness "
            "transformed a fearful fledgling into an independent bird."
        ),
        "rubric_points": [
            {"point_id": "r1", "description": "Analyzes the necessity of tough love vs pampering", "marks": 1.5},
            {"point_id": "r2", "description": "Details mother's psychological bait strategy", "marks": 2.0},
            {"point_id": "r3", "description": "Highlights celebration and reinforcement of independence", "marks": 1.5}
        ],
        "max_marks": 5.0, "source_page": "p. 2 - p. 4", "pdf_id": "10th_English.pdf"
    },

    # --- Science Unit 1: Laws of Motion ---
    {
        "id": "la_sci1_1", "chapter_id": "tn_10_sci_ch1", "question_type": "long",
        "question": "State and prove the Law of Conservation of Linear Momentum using Newton's third law of motion.",
        "model_answer": (
            "Statement: In the absence of an external unbalanced force, the total linear momentum of a system of colliding bodies remains constant.\n\n"
            "Proof:\n"
            "1. Let two bodies A and B have masses m1 and m2, moving along a straight line with initial velocities u1 and u2 (where u1 > u2).\n"
            "2. During collision lasting time t, body A exerts an action force F_B on B, and B exerts a reaction force F_A on A.\n"
            "3. By Newton's second law: Force on B is F_B = m2(v2 - u2)/t; Force on A is F_A = m1(v1 - u1)/t.\n"
            "4. According to Newton's third law: Action = -Reaction => F_B = -F_A.\n"
            "5. m2(v2 - u2)/t = -m1(v1 - u1)/t => m2 v2 - m2 u2 = -m1 v1 + m1 u1.\n"
            "6. Rearranging terms: m1 u1 + m2 u2 = m1 v1 + m2 v2.\n"
            "Hence, total momentum before collision equals total momentum after collision."
        ),
        "rubric_points": [
            {"point_id": "r1", "description": "Clear statement of Law of Conservation of Momentum", "marks": 1.0},
            {"point_id": "r2", "description": "Defines parameters (m1, m2, u1, u2, v1, v2) and diagrams setup", "marks": 1.0},
            {"point_id": "r3", "description": "Applies Newton's 2nd Law for both bodies", "marks": 1.5},
            {"point_id": "r4", "description": "Applies Newton's 3rd Law (F_B = -F_A) and derives final equality", "marks": 1.5}
        ],
        "max_marks": 5.0, "source_page": "p. 14", "pdf_id": "Class_10_Science_English_2024.pdf"
    },
    {
        "id": "la_sci1_2", "chapter_id": "tn_10_sci_ch1", "question_type": "long",
        "question": "Describe the principle and mechanism of rocket propulsion.",
        "model_answer": (
            "Principle: Rocket propulsion is based on two fundamental physics principles:\n"
            "1. Law of conservation of linear momentum.\n"
            "2. Newton's third law of motion ('For every action there is an equal and opposite reaction').\n\n"
            "Mechanism:\n"
            "1. Rockets are filled with propellant (fuel and oxidizer) in the combustion chamber.\n"
            "2. When ignited, burning fuels produce hot gases at immense pressure, which are ejected downward at high velocity through the nozzle (Action).\n"
            "3. By Newton's third law, the escaping exhaust gas imparts an equal and opposite upward reaction thrust force on the rocket.\n"
            "4. By conservation of linear momentum, as the rocket burns fuel its total mass decreases continuously. "
            "To conserve momentum, the forward velocity of the rocket progressively accelerates until reaching escape velocity or orbit."
        ),
        "rubric_points": [
            {"point_id": "r1", "description": "States both principles (Conservation of Momentum + Newton 3rd Law)", "marks": 1.5},
            {"point_id": "r2", "description": "Explains fuel ejection (Action) and upward thrust (Reaction)", "marks": 2.0},
            {"point_id": "r3", "description": "Explains effect of mass depletion leading to acceleration", "marks": 1.5}
        ],
        "max_marks": 5.0, "source_page": "p. 14", "pdf_id": "Class_10_Science_English_2024.pdf"
    },
    {
        "id": "la_sci1_3", "chapter_id": "tn_10_sci_ch1", "question_type": "long",
        "question": "State Newton's Universal Law of Gravitation and derive the mathematical expression for acceleration due to gravity (g).",
        "model_answer": (
            "Newton's Universal Law of Gravitation:\n"
            "Every particle of matter in the universe attracts every other particle with a force directly proportional to the product of their masses "
            "and inversely proportional to the square of the distance between their centers.\n"
            "F = G * (M * m) / R²\n\n"
            "Relation between g and G:\n"
            "1. Consider an object of mass m resting on the surface of the Earth of mass M and radius R.\n"
            "2. The gravitational force between Earth and object is: F = G * M * m / R².\n"
            "3. By Newton's second law, weight of the object is: W = F = m * g.\n"
            "4. Equating both expressions: m * g = G * M * m / R².\n"
            "5. Canceling mass m on both sides gives: g = G * M / R².\n"
            "This proves acceleration due to gravity depends solely on Earth's mass and radius, independent of the falling object's mass."
        ),
        "rubric_points": [
            {"point_id": "r1", "description": "States Newton's Universal Law of Gravitation clearly", "marks": 1.5},
            {"point_id": "r2", "description": "Writes gravitational formula F = G*M*m/R²", "marks": 1.0},
            {"point_id": "r3", "description": "Equates with weight F = mg and cancels m", "marks": 1.5},
            {"point_id": "r4", "description": "Derives g = GM/R² and states independence from object mass", "marks": 1.0}
        ],
        "max_marks": 5.0, "source_page": "p. 14", "pdf_id": "Class_10_Science_English_2024.pdf"
    }
]


def seed_all():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # 1. Ensure Science chapters exist
            for cid, sid, title in SCIENCE_CHAPTERS:
                cur.execute("""
                    INSERT INTO chapters (id, subject_id, title)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET title = EXCLUDED.title;
                """, (cid, sid, title))

            # 2. Insert MCQs
            for m in MCQS:
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

            # 3. Insert Short & Long Answers
            for a in SHORT_ANSWERS + LONG_ANSWERS:
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
            print(f"[x] Successfully seeded:")
            print(f"    - {len(MCQS)} MCQs")
            print(f"    - {len(SHORT_ANSWERS)} Short Answer Questions")
            print(f"    - {len(LONG_ANSWERS)} Long Answer Questions")
    finally:
        conn.close()


if __name__ == "__main__":
    seed_all()
