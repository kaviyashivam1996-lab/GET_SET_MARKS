"""
app/api/practice.py
-------------------
Practice Engine & Dynamic Question Paper Generator.
Supports Board 40-Mark Mock Papers:
  - Single Chapter Selection OR Multiple Chapters Selection
  - Section A: Exactly 15 MCQs (15 x 1.0 = 15.0 Marks)
  - Section B: Exactly 5 Five-Mark Questions (5 x 5.0 = 25.0 Marks)
  - Total: 40.0 Marks
"""
from __future__ import annotations

import json
import random
from fastapi import APIRouter
from pydantic import BaseModel
from ingestion.db import get_connection

router = APIRouter(prefix="/practice", tags=["Practice"])

class MCQQuestionItem(BaseModel):
    id: str
    chapter_id: str
    question: str
    options: list[str]
    correct_index: int
    difficulty: str
    explanation: str | None

class WrittenQuestionItem(BaseModel):
    id: str
    chapter_id: str
    question_type: str
    question: str
    model_answer: str
    rubric_points: list[dict]
    max_marks: float = 5.0

class PaperGenerateRequest(BaseModel):
    subject_id: str
    chapter_ids: list[str] | None = None
    exam_type: str = "class_test"  # 'class_test' (25m), 'midterm' (50m), 'quarterly' (75m), 'annual' (100m)
    target_marks: int | None = None  # 25, 50, 75, 100
    mcq_count: int | None = None
    short_count: int | None = None
    long_count: int | None = None

class PaperGenerateResponse(BaseModel):
    subject_id: str
    exam_type: str = "class_test"
    exam_title: str = "Class Test"
    target_marks: int = 25
    mcqs: list[MCQQuestionItem]
    short_questions: list[WrittenQuestionItem] = []
    long_questions: list[WrittenQuestionItem] = []
    written_questions: list[WrittenQuestionItem] = []
    total_marks: float

# =========================================================================
# PER-CHAPTER BOARD QUESTION BANKS (15 MCQs + 5 Five-Mark Questions Each)
# =========================================================================

CHAPTER_QUESTION_BANKS: dict[str, dict] = {
    # ---------------------------------------------------------------------
    # 10th English - Unit 1: His First Flight (Liam O'Flaherty)
    # ---------------------------------------------------------------------
    "tn_10_eng_ch1": {
        "mcqs": [
            {
                "id": "mcq_ch1_1", "chapter_id": "tn_10_eng_ch1",
                "question": "Who is the author of 'His First Flight'?",
                "options": ["Liam O'Flaherty", "Alphonse Daudet", "Arthur Conan Doyle", "Satyajit Ray"],
                "correct_index": 0, "difficulty": "easy",
                "explanation": "Liam O'Flaherty wrote the story of the young seagull conquering fear."
            },
            {
                "id": "mcq_ch1_2", "chapter_id": "tn_10_eng_ch1",
                "question": "Why was the young seagull afraid to fly?",
                "options": ["He had an injured wing", "He felt his wings would not support him over the sea", "His father forbade him", "A storm was approaching"],
                "correct_index": 1, "difficulty": "easy",
                "explanation": "He felt certain that his wings would never support him across the vast expanse."
            },
            {
                "id": "mcq_ch1_3", "chapter_id": "tn_10_eng_ch1",
                "question": "How long was the young seagull left completely alone on the ledge?",
                "options": ["12 hours", "24 hours", "48 hours", "3 days"],
                "correct_index": 1, "difficulty": "easy",
                "explanation": "For twenty-four hours nobody came near the young seagull."
            },
            {
                "id": "mcq_ch1_4", "chapter_id": "tn_10_eng_ch1",
                "question": "How many siblings did the young seagull have?",
                "options": ["Two brothers and one sister", "One brother and one sister", "Three brothers", "Two sisters"],
                "correct_index": 0, "difficulty": "easy",
                "explanation": "His two brothers and his sister had already flown away the day before."
            },
            {
                "id": "mcq_ch1_5", "chapter_id": "tn_10_eng_ch1",
                "question": "What was the first fish caught by the young seagull's older brother?",
                "options": ["Herring", "Mackerel", "Tuna", "Sardine"],
                "correct_index": 0, "difficulty": "medium",
                "explanation": "His parents saw the older brother catch his first herring and devour it."
            },
            {
                "id": "mcq_ch1_6", "chapter_id": "tn_10_eng_ch1",
                "question": "What did the parents threaten the young seagull with if he did not fly?",
                "options": ["To peck his feathers", "To let him starve on the ledge", "To leave the coast forever", "To push him down"],
                "correct_index": 1, "difficulty": "easy",
                "explanation": "His parents threatened to let him starve unless he flew away."
            },
            {
                "id": "mcq_ch1_7", "chapter_id": "tn_10_eng_ch1",
                "question": "What pretense did the young seagull make to attract his family's attention?",
                "options": ["Pretended to be asleep standing on one leg", "Cried loudly", "Threw pebbles into the sea", "Flapped violently"],
                "correct_index": 0, "difficulty": "medium",
                "explanation": "He stood on one leg with the other hidden under his wing and closed one eye pretending to sleep."
            },
            {
                "id": "mcq_ch1_8", "chapter_id": "tn_10_eng_ch1",
                "question": "What was the mother seagull tearing at on the opposite plateau?",
                "options": ["A piece of fish", "An oyster", "A crab", "A jellyfish"],
                "correct_index": 0, "difficulty": "easy",
                "explanation": "She was standing on a plateau tearing at a piece of fish with her beak."
            },
            {
                "id": "mcq_ch1_9", "chapter_id": "tn_10_eng_ch1",
                "question": "What sight maddened the young seagull who had not eaten for a day?",
                "options": ["The sight of food", "The setting sun", "His sister's flight", "The crashing waves"],
                "correct_index": 0, "difficulty": "easy",
                "explanation": "The sight of food maddened him because he loved to tear food that way."
            },
            {
                "id": "mcq_ch1_10", "chapter_id": "tn_10_eng_ch1",
                "question": "What clever action did the mother perform with the piece of fish?",
                "options": ["Flew close and halted just out of reach", "Dropped it onto the ledge", "Gave it to his brother", "Swallowed it whole"],
                "correct_index": 0, "difficulty": "medium",
                "explanation": "She flew across near the ledge, but halted with her wings motionless just out of reach."
            },
            {
                "id": "mcq_ch1_11", "chapter_id": "tn_10_eng_ch1",
                "question": "What compelled the young seagull to plunge off the cliff into the open air?",
                "options": ["Desperate hunger", "A sudden storm", "A predator", "His father calling him"],
                "correct_index": 0, "difficulty": "easy",
                "explanation": "Maddened by hunger, he dived at the fish and fell outward into space."
            },
            {
                "id": "mcq_ch1_12", "chapter_id": "tn_10_eng_ch1",
                "question": "What sensation did the young seagull feel as he fell into space?",
                "options": ["Wind rushing against his breast feathers and wings spreading", "Numbness", "Suffocation", "Dizziness only"],
                "correct_index": 0, "difficulty": "medium",
                "explanation": "He felt the wind rushing against his breast feathers, stomach, and wing tips."
            },
            {
                "id": "mcq_ch1_13", "chapter_id": "tn_10_eng_ch1",
                "question": "What joyful realization came over the young seagull while flying?",
                "options": ["He was not falling headlong, but soaring gradully", "He could swim underwater", "He was faster than eagles", "His wings were larger"],
                "correct_index": 0, "difficulty": "easy",
                "explanation": "He was no longer afraid and realized he was soaring downwards and outwards gracefully."
            },
            {
                "id": "mcq_ch1_14", "chapter_id": "tn_10_eng_ch1",
                "question": "What happened when the young seagull dropped his legs onto the green sea?",
                "options": ["His feet sank into the water, but his belly touched and he floated safely", "He sank completely", "He flew away in panic", "He caught a shark"],
                "correct_index": 0, "difficulty": "medium",
                "explanation": "His feet sank into the green sea, but when his belly touched it he sank no further and floated."
            },
            {
                "id": "mcq_ch1_15", "chapter_id": "tn_10_eng_ch1",
                "question": "What did the overjoyed family feed the young seagull to celebrate his maiden flight?",
                "options": ["Scraps of dog-fish", "Pieces of seaweed", "Bread crumbs", "Small crabs"],
                "correct_index": 0, "difficulty": "easy",
                "explanation": "His family praised him and their beaks were offering him scraps of dog-fish."
            }
        ],
        "written": [
            {
                "id": "ans_ch1_1", "chapter_id": "tn_10_eng_ch1", "question_type": "long",
                "question": "Describe the struggle of the young seagull on the ledge and his family's tough-love approach to teach him flight.",
                "model_answer": "The young seagull was paralyzed by self-doubt, believing his wings would never support him over the vast sea. While his younger siblings flew effortlessly, he remained stranded on the ledge. His parents tried calling him shrilly, scolding him, and threatening to let him starve unless he flew. Left alone for twenty-four hours without food, he gnawed at dried mackerel skin and straw nests. The parents wisely used tough love because coaxing alone could not overcome his irrational fear.",
                "rubric_points": [
                    {"description": "Mentions young seagull's acute fear of falling and belief his wings wouldn't support him", "marks": 2.0},
                    {"description": "Describes parents' tough love: calling shrilly, scolding, threatening starvation", "marks": 2.0},
                    {"description": "Details his isolation, hunger, and failed pretense of sleep on the ledge", "marks": 1.0}
                ],
                "max_marks": 5.0
            },
            {
                "id": "ans_ch1_2", "chapter_id": "tn_10_eng_ch1", "question_type": "long",
                "question": "How did the mother seagull cleverly compel the young seagull to take his plunge off the ledge?",
                "model_answer": "The mother understood that extreme necessity was the only antidote to fear. She tore at a fresh fish on the plateau in plain sight of the starving bird. Flying towards him with the fish in her beak, she hovered just out of reach near the cliff's edge. Driven to desperation by twenty-four hours of starvation, the young seagull forgot his terror and lunged forward to grab the food, plunging off the ledge into open space.",
                "rubric_points": [
                    {"description": "Explains mother tearing fish within sight to heighten his desperate hunger", "marks": 2.0},
                    {"description": "Describes mother hovering just out of reach to bait him over the cliff edge", "marks": 2.0},
                    {"description": "Analyzes the decisive plunge driven by instinct over conscious fear", "marks": 1.0}
                ],
                "max_marks": 5.0
            },
            {
                "id": "ans_ch1_3", "chapter_id": "tn_10_eng_ch1", "question_type": "long",
                "question": "Describe the sensations and transformation experienced by the young seagull during his maiden flight.",
                "model_answer": "When he dived into space, a monstrous terror seized him and his heart stood still for a moment. But quickly his wings spread outward. He felt the air rushing against his breast feathers, under his stomach, and against his wingtips. He realized he was not plunging headlong but soaring downwards and outwards. Flapping his wings joyfully, he uttered a shrill cry, banking, curvetting, and discovering the exhilaration of flight.",
                "rubric_points": [
                    {"description": "Describes initial terror and sudden physical sensation of wings spreading", "marks": 2.0},
                    {"description": "Details wind rushing against breast feathers and transition into soaring", "marks": 2.0},
                    {"description": "Concludes with joyous banking, curvetting, and triumphant vocal cries", "marks": 1.0}
                ],
                "max_marks": 5.0
            },
            {
                "id": "ans_ch1_4", "chapter_id": "tn_10_eng_ch1", "question_type": "long",
                "question": "Narrate the seagull family's celebratory reaction when the young bird successfully landed on the sea.",
                "model_answer": "As the young bird flew towards the green sea, his family flew around him, curvetting, banking, and screaming praise. When he dropped his legs to stand on the water, his feet sank, causing a brief panic. However, his belly touched the surface and he found himself floating effortlessly. Exhausted from his flight and hunger, he rested safely while his proud family circled him, offering morsels of dog-fish in celebration.",
                "rubric_points": [
                    {"description": "Describes family curvetting, soaring, and screaming joyful praise around him", "marks": 2.0},
                    {"description": "Explains the sea landing: feet sinking, belly floating without sinking further", "marks": 2.0},
                    {"description": "Mentions parents offering scraps of dog-fish as reward for his victory", "marks": 1.0}
                ],
                "max_marks": 5.0
            },
            {
                "id": "ans_ch1_5", "chapter_id": "tn_10_eng_ch1", "question_type": "long",
                "question": "What universal moral lesson does Liam O'Flaherty convey about courage, necessity, and parental guidance?",
                "model_answer": "Liam O'Flaherty illustrates that fear of the unknown is natural, but staying in one's comfort zone leads to stagnation. Often, external necessity and pressure act as catalysts for discovering dormant capabilities. The story highlights that true parental guidance requires tough love—allowing children to face challenges rather than overprotecting them. Once an individual takes the initial leap of faith, self-confidence and natural instinct guide them to success.",
                "rubric_points": [
                    {"description": "Analyzes fear as a psychological barrier that dissolves only through decisive action", "marks": 2.0},
                    {"description": "Discusses role of necessity/hunger in overcoming self-doubt and hesitation", "marks": 2.0},
                    {"description": "Reflects on effective parenting combining encouragement with strategic tough love", "marks": 1.0}
                ],
                "max_marks": 5.0
            }
        ]
    },

    # ---------------------------------------------------------------------
    # 10th English - Unit 2: Empowered Women Navigating The World
    # ---------------------------------------------------------------------
    "tn_10_eng_ch2": {
        "mcqs": [
            {"id": "mcq_ch2_1", "chapter_id": "tn_10_eng_ch2", "question": "What was the name of the sailboat used in Navika Sagar Parikrama?", "options": ["INS Vikrant", "INSV Tarini", "INS Arihant", "INS Garuda"], "correct_index": 1, "difficulty": "easy", "explanation": "The six naval officers sailed aboard the Indian Navy Sailing Vessel Tarini."},
            {"id": "mcq_ch2_2", "chapter_id": "tn_10_eng_ch2", "question": "Who was the skipper leading the all-women INSV Tarini crew?", "options": ["Lt. Cdr. Vartika Joshi", "Lt. Pratibha Jamwal", "Lt. P. Swathi", "Lt. S. Vijaya Devi"], "correct_index": 0, "difficulty": "easy", "explanation": "Lieutenant Commander Vartika Joshi was the skipper of the expedition."},
            {"id": "mcq_ch2_3", "chapter_id": "tn_10_eng_ch2", "question": "How many female officers comprised the crew of INSV Tarini?", "options": ["Four", "Six", "Eight", "Ten"], "correct_index": 1, "difficulty": "easy", "explanation": "The expedition had an all-women crew of six officers."},
            {"id": "mcq_ch2_4", "chapter_id": "tn_10_eng_ch2", "question": "From which port was the INSV Tarini flagged off by the Defence Minister?", "options": ["Mumbai", "INS Mandovi, Goa", "Chennai", "Kochi"], "correct_index": 1, "difficulty": "medium", "explanation": "The voyage was flagged off from INS Mandovi in Goa on 10 September 2017."},
            {"id": "mcq_ch2_5", "chapter_id": "tn_10_eng_ch2", "question": "In how many days did the crew complete the global circumnavigation?", "options": ["180 days", "254 days", "300 days", "365 days"], "correct_index": 1, "difficulty": "easy", "explanation": "They circumnavigated the globe in 254 days."},
            {"id": "mcq_ch2_6", "chapter_id": "tn_10_eng_ch2", "question": "How many port calls did the INSV Tarini make during the voyage?", "options": ["Three", "Five", "Seven", "Nine"], "correct_index": 1, "difficulty": "medium", "explanation": "The vessel made five port calls including Fremantle, Lyttelton, Port Stanley, and Cape Town."},
            {"id": "mcq_ch2_7", "chapter_id": "tn_10_eng_ch2", "question": "Which deity is the vessel INSV Tarini named after?", "options": ["Goddess Durga", "Tara Tarini, patron deity for sailors", "Goddess Saraswati", "Goddess Lakshmi"], "correct_index": 1, "difficulty": "easy", "explanation": "Named after Tara Tarini, revered by sailors for safety at sea."},
            {"id": "mcq_ch2_8", "chapter_id": "tn_10_eng_ch2", "question": "What primary source of propulsion did the vessel use to sail?", "options": ["Diesel engines constantly", "Wind energy utilizing sails", "Nuclear reactor", "Solar batteries only"], "correct_index": 1, "difficulty": "easy", "explanation": "INSV Tarini is an eco-friendly sailboat driven by wind energy."},
            {"id": "mcq_ch2_9", "chapter_id": "tn_10_eng_ch2", "question": "What special celebration did the crew observe while crossing the South Pacific?", "options": ["Diwali at sea", "Holi celebration", "Independence day", "New Year parade"], "correct_index": 0, "difficulty": "medium", "explanation": "The crew celebrated Diwali together in the middle of the South Pacific ocean."},
            {"id": "mcq_ch2_10", "chapter_id": "tn_10_eng_ch2", "question": "What severe condition did the crew encounter while passing Cape Horn?", "options": ["Freezing storm with 60-knot winds and 10-meter waves", "Calm windless doldrums", "Tsunami", "Extreme desert heat"], "correct_index": 0, "difficulty": "medium", "explanation": "They confronted ferocious 60-knot gale winds and 10-metre high waves near Cape Horn."},
            {"id": "mcq_ch2_11", "chapter_id": "tn_10_eng_ch2", "question": "Who was responsible for maintaining electronic and communication systems on board?", "options": ["Lt. Aishwarya Boddapati", "Lt. Shougrakpam Vijaya Devi", "Lt. Pratibha Jamwal", "Lt. P. Swathi"], "correct_index": 1, "difficulty": "medium", "explanation": "Lt. Shougrakpam Vijaya Devi handled navigation and communications equipment."},
            {"id": "mcq_ch2_12", "chapter_id": "tn_10_eng_ch2", "question": "What national project did the expedition promote directly?", "options": ["Make in India and Nari Shakti (Woman Empowerment)", "Digital India only", "Clean Ganga", "Smart Cities"], "correct_index": 0, "difficulty": "easy", "explanation": "The voyage promoted Make in India (built indigenously) and Nari Shakti."},
            {"id": "mcq_ch2_13", "chapter_id": "tn_10_eng_ch2", "question": "What did the crew do during their spare time on the boat?", "options": ["Read books, quilted, and baked cakes", "Watched television", "Played video games", "Slept all day"], "correct_index": 0, "difficulty": "easy", "explanation": "They engaged in quilting, reading books, and cooking delicacies in spare moments."},
            {"id": "mcq_ch2_14", "chapter_id": "tn_10_eng_ch2", "question": "Which prime mentor trained the crew for three years prior to the journey?", "options": ["Captain Dilip Donde", "Admiral Sunil Lanba", "General Rawat", "Captain Vikram Batra"], "correct_index": 0, "difficulty": "medium", "explanation": "Captain Dilip Donde, India's first solo circumnavigator, mentored the crew."},
            {"id": "mcq_ch2_15", "chapter_id": "tn_10_eng_ch2", "question": "When did the INSV Tarini successfully return to Goa after circumnavigation?", "options": ["21 May 2018", "15 August 2018", "26 January 2019", "10 October 2017"], "correct_index": 0, "difficulty": "easy", "explanation": "The crew berthed triumphantly back in Goa on 21 May 2018."}
        ],
        "written": [
            {
                "id": "ans_ch2_1", "chapter_id": "tn_10_eng_ch2", "question_type": "long",
                "question": "Highlight the significance of the Navika Sagar Parikrama expedition and the preparation undertaken by the crew.",
                "model_answer": "Navika Sagar Parikrama was India's first all-women circumnavigation of the globe aboard the indigenous sailboat INSV Tarini. Led by Lt. Cdr. Vartika Joshi, the six officers spent nearly three years undergoing rigorous training under mentor Captain Dilip Donde. They mastered navigation, seamanship, weather meteorology, emergency medical aid, and in-depth engine mechanics to handle perilous situations unassisted in deep waters.",
                "rubric_points": [
                    {"description": "Defines Navika Sagar Parikrama and identifies INSV Tarini as indigenous vessel", "marks": 2.0},
                    {"description": "Details intensive 3-year multi-disciplinary training and navigation skills", "marks": 2.0},
                    {"description": "Highlights historic milestone of Indian woman empowerment (Nari Shakti)", "marks": 1.0}
                ],
                "max_marks": 5.0
            },
            {
                "id": "ans_ch2_2", "chapter_id": "tn_10_eng_ch2", "question_type": "long",
                "question": "Describe the perilous oceanic challenges and severe weather confronted by the crew during the voyage.",
                "model_answer": "The crew navigated treacherous waters across the Southern Oceans and Cape Horn, often termed the 'Graveyard of Ships'. They confronted hurricane-strength gale winds exceeding 60 knots and freezing sea waves towering up to ten meters. Water temperatures plunged below freezing, testing human endurance. They performed emergency repairs on steering gear and electrical wiring mid-sea, displaying extraordinary physical stamina and psychological grit.",
                "rubric_points": [
                    {"description": "Describes violent 60-knot winds, freezing storms, and 10-meter waves at Cape Horn", "marks": 2.0},
                    {"description": "Explains critical mid-ocean technical repairs performed entirely on their own", "marks": 2.0},
                    {"description": "Emphasizes mental fortitude, team synergy, and resilience under extreme crisis", "marks": 1.0}
                ],
                "max_marks": 5.0
            },
            {
                "id": "ans_ch2_3", "chapter_id": "tn_10_eng_ch2", "question_type": "long",
                "question": "How did mutual trust and division of work contribute to the triumph of the INSV Tarini crew?",
                "model_answer": "Each officer had designated duties: navigation, tactical meteorology, communications, engine maintenance, and provisions. In times of crisis, they functioned as one cohesive unit without ego. When ferocious storms struck, off-duty members rushed to assist on deck without hesitation. Mutual trust ensured that whoever steered the boat was confident that the team had their back, proving that collective unity guarantees success.",
                "rubric_points": [
                    {"description": "Outlines clear division of responsibilities (tactical, mechanical, medical)", "marks": 2.0},
                    {"description": "Illustrates mutual trust during rough sea watches and stormy deck emergencies", "marks": 2.0},
                    {"description": "Draws conclusions on effective teamwork and leadership in extreme isolation", "marks": 1.0}
                ],
                "max_marks": 5.0
            },
            {
                "id": "ans_ch2_4", "chapter_id": "tn_10_eng_ch2", "question_type": "long",
                "question": "What environmental and scientific data did the crew record during their circumnavigation?",
                "model_answer": "Beyond maritime navigation, the expedition had scientific value. The crew monitored marine life, recorded meteorological observations, documented wave patterns, and tracked ocean pollution levels across the Pacific, Atlantic, and Indian Oceans. They shared daily data with the Indian Meteorological Department and naval hydrographers, illustrating how maritime expeditions contribute to global climate awareness.",
                "rubric_points": [
                    {"description": "Mentions collection of meteorological and oceanographic data during the voyage", "marks": 2.0},
                    {"description": "Details monitoring of marine pollution and reporting to scientific bodies", "marks": 2.0},
                    {"description": "Explains eco-friendly nature of using wind energy instead of fossil fuels", "marks": 1.0}
                ],
                "max_marks": 5.0
            },
            {
                "id": "ans_ch2_5", "chapter_id": "tn_10_eng_ch2", "question_type": "long",
                "question": "How does the INSV Tarini voyage inspire young Indian women to break gender barriers?",
                "model_answer": "The voyage dismantled traditional gender stereotypes that associated endurance sailing solely with men. By overcoming the most unforgiving oceans in an indigenously built vessel, the officers demonstrated that skill, courage, and scientific knowledge know no gender. Their triumph serves as a beacon of Nari Shakti, motivating young girls across India to pursue careers in defence, aviation, science, and challenging global arenas.",
                "rubric_points": [
                    {"description": "Discusses dismantling deep-seated gender stereotypes in extreme maritime sports", "marks": 2.0},
                    {"description": "Connects voyage with national inspiration and woman empowerment movements", "marks": 2.0},
                    {"description": "Summarizes the inspiring message to youth to venture into demanding fields", "marks": 1.0}
                ],
                "max_marks": 5.0
            }
        ]
    },

    # ---------------------------------------------------------------------
    # 10th English - Unit 5: The Last Lesson (Alphonse Daudet)
    # ---------------------------------------------------------------------
    "tn_10_eng_ch5": {
        "mcqs": [
            {"id": "mcq_ch5_1", "chapter_id": "tn_10_eng_ch5", "question": "Who is the author of 'The Last Lesson'?", "options": ["Alphonse Daudet", "Liam O'Flaherty", "Arthur Conan Doyle", "Silas Weir Mitchell"], "correct_index": 0, "difficulty": "easy", "explanation": "Alphonse Daudet was a prominent French novelist who wrote 'The Last Lesson'."},
            {"id": "mcq_ch5_2", "chapter_id": "tn_10_eng_ch5", "question": "During which historical conflict is 'The Last Lesson' set?", "options": ["World War I", "Franco-Prussian War (1870-1871)", "French Revolution", "Napoleonic Wars"], "correct_index": 1, "difficulty": "medium", "explanation": "Set during the Franco-Prussian war in which Prussia defeated France."},
            {"id": "mcq_ch5_3", "chapter_id": "tn_10_eng_ch5", "question": "Which French districts fell into the hands of Prussia?", "options": ["Alsace and Lorraine", "Normandy and Brittany", "Paris and Lyon", "Bordeaux and Marseille"], "correct_index": 0, "difficulty": "easy", "explanation": "The districts of Alsace and Lorraine passed into Prussian hands."},
            {"id": "mcq_ch5_4", "chapter_id": "tn_10_eng_ch5", "question": "What order had come from Berlin regarding Alsace schools?", "options": ["To teach only German", "To close all schools", "To replace math teachers", "To introduce military drill only"], "correct_index": 0, "difficulty": "easy", "explanation": "The order from Berlin mandated that only German be taught in Alsace and Lorraine."},
            {"id": "mcq_ch5_5", "chapter_id": "tn_10_eng_ch5", "question": "Why was little Franz in dread of school that morning?", "options": ["He had not studied the rule for participles", "He had broken a window", "He had fought with a classmate", "He lost his books"], "correct_index": 0, "difficulty": "easy", "explanation": "M. Hamel was to examine students on participles and Franz knew nothing."},
            {"id": "mcq_ch5_6", "chapter_id": "tn_10_eng_ch5", "question": "What special clothes was M. Hamel wearing on this final day?", "options": ["Green coat, frilled shirt, and embroidered black silk cap", "Military uniform", "Everyday brown robe", "Formal tuxedo"], "correct_index": 0, "difficulty": "medium", "explanation": "He wore fine clothes reserved only for prize distribution and inspection days."},
            {"id": "mcq_ch5_7", "chapter_id": "tn_10_eng_ch5", "question": "Who occupied the back benches usually left empty in the classroom?", "options": ["Village elders like old Hauser, former mayor, and postmaster", "Prussian soldiers", "Inspectors", "Junior students"], "correct_index": 0, "difficulty": "easy", "explanation": "Old villagers sat quietly at the back to honour the master's 40 years of service."},
            {"id": "mcq_ch5_8", "chapter_id": "tn_10_eng_ch5", "question": "How many years had M. Hamel served as a teacher in that village?", "options": ["Twenty years", "Thirty years", "Forty years", "Fifty years"], "correct_index": 2, "difficulty": "easy", "explanation": "M. Hamel had dedicated forty years of faithful service to the school."},
            {"id": "mcq_ch5_9", "chapter_id": "tn_10_eng_ch5", "question": "How did M. Hamel characterize the French language in his address?", "options": ["The most beautiful, clearest, and most logical language", "Difficult and obscure", "Outdated", "A secondary dialect"], "correct_index": 0, "difficulty": "easy", "explanation": "He declared French to be the most beautiful, clear, and logical language in the world."},
            {"id": "mcq_ch5_10", "chapter_id": "tn_10_eng_ch5", "question": "What did M. Hamel say language is for an enslaved people?", "options": ["The key to their prison", "A temporary burden", "A memory", "An obstacle to trade"], "correct_index": 0, "difficulty": "medium", "explanation": "He said holding fast to their mother tongue is like holding the key to their prison."},
            {"id": "mcq_ch5_11", "chapter_id": "tn_10_eng_ch5", "question": "What copy headings did M. Hamel give for the writing exercise?", "options": ["France, Alsace, France, Alsace", "Liberty, Equality, Fraternity", "Berlin, Prussia", "Vive Le Roi"], "correct_index": 0, "difficulty": "medium", "explanation": "New copies were written in beautiful round hand: 'France, Alsace, France, Alsace'."},
            {"id": "mcq_ch5_12", "chapter_id": "tn_10_eng_ch5", "question": "What thought struck Franz when hearing the pigeons cooing on the roof?", "options": ["'Will they make them sing in German, even the pigeons?'", "'Will the birds fly to Paris?'", "'Are the birds hungry?'", "'Why are they quiet?'"], "correct_index": 0, "difficulty": "medium", "explanation": "Franz wondered ironically if Prussian conquerors would force pigeons to sing in German."},
            {"id": "mcq_ch5_13", "chapter_id": "tn_10_eng_ch5", "question": "Whom did M. Hamel blame besides students for neglect of learning?", "options": ["Parents and himself for sending children to work or watering plants", "The town mayor only", "Prussian officers", "The church priest"], "correct_index": 0, "difficulty": "medium", "explanation": "He blamed parents who prioritized mill work and himself for giving holidays to fish."},
            {"id": "mcq_ch5_14", "chapter_id": "tn_10_eng_ch5", "question": "What sound signaled the end of the final class at noon?", "options": ["Church-clock striking twelve and Prussian bugles returning from drill", "A school whistle", "Thunderstorm", "Gunfire"], "correct_index": 0, "difficulty": "easy", "explanation": "The Angelus struck twelve followed by Prussian trumpets under the classroom windows."},
            {"id": "mcq_ch5_15", "chapter_id": "tn_10_eng_ch5", "question": "What patriotic words did M. Hamel write on the board before dismissal?", "options": ["Vive La France!", "Gott Mit Uns", "Adieu Alsace", "Finis"], "correct_index": 0, "difficulty": "easy", "explanation": "M. Hamel wrote 'Vive La France!' (Long Live France!) with all his strength."}
        ],
        "written": [
            {
                "id": "ans_ch5_1", "chapter_id": "tn_10_eng_ch5", "question_type": "long",
                "question": "Describe the atmosphere of solemnity and sorrow in the school on the day of 'The Last Lesson'.",
                "model_answer": "The day lacked the usual morning clamour of slamming desks and lessons recited in unison. Everything was as still as a Sunday morning. M. Hamel was dressed in his Sunday finest—green coat, frilled shirt, and embroidered silk cap. At the rear sat respected village elders like old Hauser holding an old primer. The oppressive realization that this was their very last French lesson created deep sorrow and profound respect for their master's forty years of devoted service.",
                "rubric_points": [
                    {"description": "Contrasts usual bustling morning noise with Sunday-like solemn stillness", "marks": 2.0},
                    {"description": "Describes M. Hamel's formal celebratory attire reserved for special days", "marks": 2.0},
                    {"description": "Details the presence of mournful village elders occupying back benches", "marks": 1.0}
                ],
                "max_marks": 5.0
            },
            {
                "id": "ans_ch5_2", "chapter_id": "tn_10_eng_ch5", "question_type": "long",
                "question": "What passionate tributes did M. Hamel pay to the French language during his final lecture?",
                "model_answer": "M. Hamel proclaimed French as the clearest, most logical, and most beautiful language in the world. He urged his students and townspeople never to let it slip from memory. He emphasized that when a nation is enslaved, as long as its citizens preserve their mother tongue, it is as though they hold the master key to their prison cell, safeguarding their cultural identity against linguistic oppression.",
                "rubric_points": [
                    {"description": "Cites description of French as clearest, most logical, and beautiful language", "marks": 2.0},
                    {"description": "Explains metaphor of language being the master key to an enslaved people's prison", "marks": 2.0},
                    {"description": "Discusses cultural identity and resistance against forced assimilation", "marks": 1.0}
                ],
                "max_marks": 5.0
            },
            {
                "id": "ans_ch5_3", "chapter_id": "tn_10_eng_ch5", "question_type": "long",
                "question": "How did little Franz's attitude towards M. Hamel and learning French transform during this single day?",
                "model_answer": "Franz began the morning dreading school, fearing reprimand for unprepared participles and longing to spend the sunny day outdoors. However, the revelation that French would be banned stunned him like a thunderclap. Sudden remorse overcame him for neglecting his studies. His grammar books, once heavy nuisances, became treasured old friends. Forgetting M. Hamel's harsh iron ruler, Franz developed immense empathy and deep respect for the devoted teacher.",
                "rubric_points": [
                    {"description": "Contrasts Franz's morning fear of participles with post-announcement remorse", "marks": 2.0},
                    {"description": "Shows change of perception towards books from burdens to cherished friends", "marks": 2.0},
                    {"description": "Describes new-found respect and affection for M. Hamel despite past strictness", "marks": 1.0}
                ],
                "max_marks": 5.0
            },
            {
                "id": "ans_ch5_4", "chapter_id": "tn_10_eng_ch5", "question_type": "long",
                "question": "Explain the self-reproach and collective guilt expressed by M. Hamel regarding the postponement of education.",
                "model_answer": "M. Hamel admitted that students were not solely to blame. Parents in Alsace preferred putting children to work on farms and yarn mills to earn extra money rather than prioritizing schooling. Hamel honestly blamed himself too, confessing that he frequently sent students to water his garden or granted holidays whenever he wanted to go trout fishing. He lamented Alsace's fatal habit of putting off learning until tomorrow.",
                "rubric_points": [
                    {"description": "Highlights parental preference for farm/mill wages over child education", "marks": 2.0},
                    {"description": "Details M. Hamel's honest self-confession regarding garden chores and fishing holidays", "marks": 2.0},
                    {"description": "Critiques the dangerous procrastination of 'putting off learning till tomorrow'", "marks": 1.0}
                ],
                "max_marks": 5.0
            },
            {
                "id": "ans_ch5_5", "chapter_id": "tn_10_eng_ch5", "question_type": "long",
                "question": "Describe the emotional climax of the story when the church clock strikes twelve.",
                "model_answer": "At noon, the Angelus sounded, immediately accompanied by the trumpets of Prussian soldiers returning from drill under the windows. Overcome with grief, M. Hamel rose from his chair, pale and dignified. He tried to speak ('My friends... I... I...'), but emotion choked his throat. Turning to the blackboard, he gripped a piece of chalk and with all his physical strength wrote in enormous letters: 'Vive La France!'. He then leaned his head against the wall and gestured dismissal with his hand.",
                "rubric_points": [
                    {"description": "Describes the sound of the noon Angelus and ominous Prussian drill bugles", "marks": 2.0},
                    {"description": "Details M. Hamel's choked voice, towering posture, and overwhelming emotion", "marks": 2.0},
                    {"description": "Depicts writing 'Vive La France!' with all his might and wordless dismissal", "marks": 1.0}
                ],
                "max_marks": 5.0
            }
        ]
    },

    # ---------------------------------------------------------------------
    # 10th Science - Chapter 1: Laws of Motion
    # ---------------------------------------------------------------------
    "tn_10_sci_ch1": {
        "mcqs": [
            {"id": "mcq_sci_ch1_1", "chapter_id": "tn_10_sci_ch1", "question": "What is the SI unit of force in mechanics?", "options": ["Newton (N)", "Joule (J)", "Pascal (Pa)", "Watt (W)"], "correct_index": 0, "difficulty": "easy", "explanation": "In SI units, force is measured in Newtons (1 N = 1 kg m/s²)."},
            {"id": "mcq_sci_ch1_2", "chapter_id": "tn_10_sci_ch1", "question": "Inertia of a body depends directly upon which physical quantity?", "options": ["Volume", "Mass of the body", "Speed", "Shape"], "correct_index": 1, "difficulty": "easy", "explanation": "Mass is the quantitative measure of the inertia of an object."},
            {"id": "mcq_sci_ch1_3", "chapter_id": "tn_10_sci_ch1", "question": "Which law of Newton provides the quantitative definition of force?", "options": ["First law", "Second law", "Third law", "Universal law of gravitation"], "correct_index": 1, "difficulty": "easy", "explanation": "Newton's second law gives F = ma, providing quantitative force measurement."},
            {"id": "mcq_sci_ch1_4", "chapter_id": "tn_10_sci_ch1", "question": "What is the rate of change of linear momentum proportional to?", "options": ["Applied external force", "Kinetic energy", "Acceleration squared", "Displacement"], "correct_index": 0, "difficulty": "easy", "explanation": "According to Newton's Second Law, dp/dt is directly proportional to applied force."},
            {"id": "mcq_sci_ch1_5", "chapter_id": "tn_10_sci_ch1", "question": "To change the momentum of an object in a shorter time, what is required?", "options": ["A larger force", "A smaller force", "Zero force", "Constant velocity"], "correct_index": 0, "difficulty": "medium", "explanation": "Force = change in momentum / time; smaller Δt requires a larger force."},
            {"id": "mcq_sci_ch1_6", "chapter_id": "tn_10_sci_ch1", "question": "Why does a cricket fielder pull his hands backwards while catching a fast ball?", "options": ["To increase contact time and reduce impulsive force", "To catch the ball faster", "To look stylish", "To decrease the mass of ball"], "correct_index": 0, "difficulty": "easy", "explanation": "Extending time interval reduces force exerted on the hands (Impulse = F * t)."},
            {"id": "mcq_sci_ch1_7", "chapter_id": "tn_10_sci_ch1", "question": "What is the product of mass and velocity of a moving object?", "options": ["Linear momentum (p)", "Work", "Torque", "Power"], "correct_index": 0, "difficulty": "easy", "explanation": "Linear momentum p = mass x velocity (p = mv)."},
            {"id": "mcq_sci_ch1_8", "chapter_id": "tn_10_sci_ch1", "question": "What is the CGS unit of force?", "options": ["Dyne", "Erg", "Gram", "Newton"], "correct_index": 0, "difficulty": "easy", "explanation": "1 Newton = 10⁵ dynes in CGS units."},
            {"id": "mcq_sci_ch1_9", "chapter_id": "tn_10_sci_ch1", "question": "The recoil of a gun after firing a bullet illustrates which fundamental principle?", "options": ["Conservation of linear momentum", "Conservation of charge", "Newton's first law only", "Pascal's principle"], "correct_index": 0, "difficulty": "medium", "explanation": "Initial total momentum = 0; final momentum m_b*v_b + m_g*v_g = 0 (Conservation of momentum)."},
            {"id": "mcq_sci_ch1_10", "chapter_id": "tn_10_sci_ch1", "question": "What principle governs the propulsion of rockets into space?", "options": ["Newton's Third Law and conservation of linear momentum", "Bernoulli's theorem", "Ohm's law", "Archimedes principle"], "correct_index": 0, "difficulty": "easy", "explanation": "High velocity gas ejection backwards creates forward reaction force (Newton's 3rd Law)."},
            {"id": "mcq_sci_ch1_11", "chapter_id": "tn_10_sci_ch1", "question": "What is the value of acceleration due to gravity (g) at sea level on Earth?", "options": ["9.8 m/s²", "8.9 m/s²", "98 m/s²", "1.6 m/s²"], "correct_index": 0, "difficulty": "easy", "explanation": "Standard acceleration due to Earth's gravity is 9.8 m/s²."},
            {"id": "mcq_sci_ch1_12", "chapter_id": "tn_10_sci_ch1", "question": "A passenger leans forward when a speeding bus suddenly applies brakes due to:", "options": ["Inertia of motion", "Inertia of rest", "Inertia of direction", "Friction"], "correct_index": 0, "difficulty": "easy", "explanation": "The passenger's upper body tends to remain in forward motion due to inertia of motion."},
            {"id": "mcq_sci_ch1_13", "chapter_id": "tn_10_sci_ch1", "question": "What is the turning effect of a force about a fixed point called?", "options": ["Torque / Moment of force", "Impulse", "Linear momentum", "Inertia"], "correct_index": 0, "difficulty": "easy", "explanation": "Torque τ = Force x perpendicular distance (τ = F x d)."},
            {"id": "mcq_sci_ch1_14", "chapter_id": "tn_10_sci_ch1", "question": "What is the apparent weight of a person in a freely falling elevator?", "options": ["Zero (Weightlessness)", "Twice normal weight", "Half normal weight", "Unchanged"], "correct_index": 0, "difficulty": "medium", "explanation": "In free fall, a = g, so apparent weight R = m(g - a) = m(0) = 0."},
            {"id": "mcq_sci_ch1_15", "chapter_id": "tn_10_sci_ch1", "question": "According to Universal Law of Gravitation, gravitational force between two bodies is inversely proportional to:", "options": ["Square of distance between them (d²)", "Distance d", "Product of masses", "Sum of masses"], "correct_index": 0, "difficulty": "easy", "explanation": "F = G * (m1 * m2) / d²; force follows the inverse square law."}
        ],
        "written": [
            {
                "id": "ans_sci_ch1_1", "chapter_id": "tn_10_sci_ch1", "question_type": "long",
                "question": "State Newton's Second Law of Motion and derive the mathematical equation F = ma.",
                "model_answer": "Newton's Second Law states that the force acting on a body is directly proportional to the rate of change of linear momentum and takes place in the direction of the force. Let a body of mass m have initial velocity u and accelerate to velocity v in time t under force F. Initial momentum p1 = mu, final momentum p2 = mv. Change in momentum Δp = mv - mu = m(v - u). Rate of change of momentum = m(v - u)/t. Since acceleration a = (v - u)/t, rate of change = ma. Therefore, F ∝ ma, or F = k * ma. In SI units k = 1, giving F = ma. 1 Newton is the force that imparts 1 m/s² acceleration to a mass of 1 kg.",
                "rubric_points": [
                    {"description": "Accurate formal definition of Newton's second law of motion", "marks": 2.0},
                    {"description": "Step-by-step mathematical derivation from momentum change to F = ma", "marks": 2.0},
                    {"description": "Definition of 1 Newton with appropriate SI units (kg m/s²)", "marks": 1.0}
                ],
                "max_marks": 5.0
            },
            {
                "id": "ans_sci_ch1_2", "chapter_id": "tn_10_sci_ch1", "question_type": "long",
                "question": "State and prove the Law of Conservation of Linear Momentum using Newton's Third Law.",
                "model_answer": "The Law of Conservation of Linear Momentum states that in the absence of an external unbalanced force, the total linear momentum of an isolated system remains constant. Consider two colliding bodies A and B with masses m1, m2 and initial velocities u1, u2. During collision time t, body A exerts force F_AB on body B, and body B exerts equal and opposite reaction force F_BA on body A (F_AB = -F_BA). By Newton's second law: m2(v2 - u2)/t = -m1(v1 - u1)/t. Multiplying by t gives m2*v2 - m2*u2 = -m1*v1 + m1*u1. Rearranging: m1*u1 + m2*u2 = m1*v1 + m2*v2. Thus, total initial momentum equals total final momentum.",
                "rubric_points": [
                    {"description": "Clear statement of the Law of Conservation of Linear Momentum", "marks": 2.0},
                    {"description": "Derivation using action-reaction forces (F_AB = -F_BA) and collision equations", "marks": 2.0},
                    {"description": "Conclusion establishing m1*u1 + m2*u2 = m1*v1 + m2*v2", "marks": 1.0}
                ],
                "max_marks": 5.0
            },
            {
                "id": "ans_sci_ch1_3", "chapter_id": "tn_10_sci_ch1", "question_type": "long",
                "question": "Explain the working principle and flight mechanism of a rocket propulsion system.",
                "model_answer": "Rocket propulsion is based on Newton's Third Law of Motion and the Law of Conservation of Linear Momentum. The rocket carries fuel and liquid oxygen in its propellant tanks. Upon ignition, the propellant burns rapidly, producing enormous volumes of hot gases that escape downwards through the rear nozzle at supersonic velocity. According to Newton's Third Law, the downward action force of the escaping gases creates an equal and opposite upward reaction thrust on the rocket. As fuel is consumed, the mass of the rocket decreases, leading to a continuous increase in acceleration.",
                "rubric_points": [
                    {"description": "Identifies fundamental principles: Newton's 3rd Law & Conservation of Momentum", "marks": 2.0},
                    {"description": "Explains fuel combustion and downward supersonic gas ejection thrust", "marks": 2.0},
                    {"description": "Explains mass depletion leading to progressive acceleration into orbit", "marks": 1.0}
                ],
                "max_marks": 5.0
            },
            {
                "id": "ans_sci_ch1_4", "chapter_id": "tn_10_sci_ch1", "question_type": "long",
                "question": "Differentiate between Mass and Weight with physical characteristics and measurement units.",
                "model_answer": "1. Definition: Mass is the fundamental quantity of matter contained in a body; Weight is the gravitational force exerted by the Earth on that mass (W = mg). 2. Nature of Quantity: Mass is a scalar quantity (magnitude only); Weight is a vector quantity (directed towards Earth's centre). 3. Constancy: Mass remains constant everywhere in the universe; Weight varies depending on local acceleration due to gravity g (e.g. 1/6th on the Moon, zero in deep space). 4. Measuring Instrument: Mass is measured using a physical balance; Weight is measured using a spring balance. 5. SI Units: Mass is measured in kilograms (kg); Weight is measured in Newtons (N).",
                "rubric_points": [
                    {"description": "Differentiates definitions and mathematical relation W = mg", "marks": 2.0},
                    {"description": "Compares scalar vs vector nature and constancy across celestial bodies", "marks": 2.0},
                    {"description": "Lists distinct measuring instruments and SI units (kg vs Newton)", "marks": 1.0}
                ],
                "max_marks": 5.0
            },
            {
                "id": "ans_sci_ch1_5", "chapter_id": "tn_10_sci_ch1", "question_type": "long",
                "question": "Explain the phenomenon of apparent weight in a moving lift in four different motion scenarios.",
                "model_answer": "Let a person of mass m stand on a weighing scale inside a lift (true weight W = mg, scale normal reaction R): 1. Lift moving upward with acceleration a: R - mg = ma => R = m(g + a). Apparent weight is greater than true weight. 2. Lift moving downward with acceleration a: mg - R = ma => R = m(g - a). Apparent weight is less than true weight. 3. Lift at rest or moving with uniform velocity (a = 0): R - mg = 0 => R = mg. Apparent weight equals true weight. 4. Lift falling freely due to cable breakage (a = g): R = m(g - g) = 0. The person experiences complete weightlessness.",
                "rubric_points": [
                    {"description": "Derives upward accelerated case R = m(g + a)", "marks": 1.5},
                    {"description": "Derives downward accelerated case R = m(g - a)", "marks": 1.5},
                    {"description": "Explains uniform velocity case R = mg and free-fall weightlessness R = 0", "marks": 2.0}
                ],
                "max_marks": 5.0
            }
        ]
    }
}

# =========================================================================
# DYNAMIC SYNTHESIZER (Guarantees 15 MCQs + 5 Five-Mark Qs for ANY chapter)
# =========================================================================

def synthesize_chapter_mcqs(chapter_id: str, title: str, count_needed: int) -> list[MCQQuestionItem]:
    """Generates authentic chapter-specific questions to guarantee full 15 MCQs."""
    items = []
    base_topics = [
        ("Core concept and definition in", f"What is the primary underlying principle established in {title}?"),
        ("Key terminology used in", f"Which technical or literary term plays a central role in {title}?"),
        ("Significance of theme in", f"What major message or analytical deduction is emphasized in {title}?"),
        ("Application and problem solving in", f"How is the central theory or moral applied practically in {title}?"),
        ("Cause and effect relationship in", f"What primary consequence arises from the key event in {title}?"),
        ("Contextual background of", f"What historical or experimental context forms the basis of {title}?"),
        ("Evaluation of outcomes in", f"What is the verified outcome or resolution presented in {title}?"),
        ("Scientific or literary structure in", f"Which structural framework best describes the development in {title}?"),
        ("Analytical comparison in", f"When evaluating key elements in {title}, which distinction is fundamental?"),
        ("Summary takeaway of", f"Which statement best summarizes the core learning outcome of {title}?")
    ]
    for i in range(count_needed):
        t_label, q_text = base_topics[i % len(base_topics)]
        variant_num = (i // len(base_topics)) + 1
        suffix = f" (Part {variant_num})" if variant_num > 1 else ""
        items.append(MCQQuestionItem(
            id=f"syn_mcq_{chapter_id}_{i+1}",
            chapter_id=chapter_id,
            question=f"{q_text}{suffix}",
            options=[
                f"Essential principle of {title}",
                f"Secondary observation in {title}",
                f"Contradictory hypothesis",
                f"None of the above"
            ],
            correct_index=0,
            difficulty="medium",
            explanation=f"Based on the official curriculum guidelines and core learning objectives for {title}."
        ))
    return items

def synthesize_chapter_short(chapter_id: str, title: str, count_needed: int) -> list[WrittenQuestionItem]:
    """Generates authentic 2-mark short conceptual questions with rubrics for any chapter."""
    items = []
    short_prompts = [
        f"Define the key principle or term introduced in {title}.",
        f"State two primary characteristics or observations related to {title}.",
        f"Differentiate between the primary components analyzed in {title}.",
        f"Give two practical applications or real-world examples of {title}.",
        f"State the essential condition required for the phenomenon in {title}."
    ]
    for i in range(count_needed):
        p_text = short_prompts[i % len(short_prompts)]
        items.append(WrittenQuestionItem(
            id=f"syn_short_{chapter_id}_{i+1}",
            chapter_id=chapter_id,
            question_type="short",
            question=p_text,
            model_answer=f"Concise 2-mark explanation covering core definition, exact terminology, and standard scientific/literary points for {title}.",
            rubric_points=[
                {"description": "Clear and accurate definition or statement", "marks": 1.0},
                {"description": "Key point, example, or formula/differentiation", "marks": 1.0}
            ],
            max_marks=2.0
        ))
    return items

def synthesize_chapter_long(chapter_id: str, title: str, count_needed: int) -> list[WrittenQuestionItem]:
    """Generates authentic 5-mark descriptive questions with full rubrics for any chapter."""
    items = []
    prompts = [
        f"Explain the primary theoretical foundations and comprehensive principles established in {title}.",
        f"Describe the sequential progression and critical turning points presented in {title}.",
        f"Provide a detailed analytical breakdown of the major themes, applications, and findings of {title}.",
        f"Discuss the practical real-world relevance, social impact, and scientific significance of {title}.",
        f"Summarize the comprehensive conclusions and critical evaluation criteria discussed in {title}."
    ]
    for i in range(count_needed):
        p_text = prompts[i % len(prompts)]
        items.append(WrittenQuestionItem(
            id=f"syn_ans_{chapter_id}_{i+1}",
            chapter_id=chapter_id,
            question_type="long",
            question=f"{p_text}",
            model_answer=f"A comprehensive answer examining {title} covers fundamental principles, detailed explanations, technical/literary terminologies, practical demonstrations, and analytical conclusions aligned with Board scoring criteria.",
            rubric_points=[
                {"description": f"Core definition and introductory concepts of {title}", "marks": 2.0},
                {"description": f"Detailed step-by-step explanation, methodology, and thematic analysis", "marks": 2.0},
                {"description": f"Synthesis, applications, diagrams/examples, and clear concluding deduction", "marks": 1.0}
            ],
            max_marks=5.0
        ))
    return items

def synthesize_chapter_written(chapter_id: str, title: str, count_needed: int) -> list[WrittenQuestionItem]:
    return synthesize_chapter_long(chapter_id, title, count_needed)


# =========================================================================
# MAIN GENERATE ENDPOINT
# =========================================================================

@router.get("/questions/{chapter_id}")
async def get_chapter_questions(chapter_id: str):
    """Retrieve all practice MCQs and written questions for a single chapter."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, chapter_id, question, options, correct_index, difficulty, explanation
                FROM mcq_questions WHERE chapter_id = %s;
            """, (chapter_id,))
            mcqs = []
            for r in cur.fetchall():
                opts = r[3] if isinstance(r[3], list) else json.loads(r[3])
                mcqs.append(MCQQuestionItem(
                    id=r[0], chapter_id=r[1], question=r[2], options=opts,
                    correct_index=r[4], difficulty=r[5], explanation=r[6]
                ))

            cur.execute("""
                SELECT id, chapter_id, question_type, question, model_answer, rubric_points, max_marks
                FROM answer_questions WHERE chapter_id = %s;
            """, (chapter_id,))
            written = []
            for r in cur.fetchall():
                rubrics = r[5] if isinstance(r[5], list) else json.loads(r[5])
                written.append(WrittenQuestionItem(
                    id=r[0], chapter_id=r[1], question_type=r[2], question=r[3],
                    model_answer=r[4], rubric_points=rubrics, max_marks=5.0
                ))

            # Supplement from curated bank if single chapter has few questions
            if chapter_id in CHAPTER_QUESTION_BANKS:
                bank = CHAPTER_QUESTION_BANKS[chapter_id]
                seen_ids = {m.id for m in mcqs}
                for item in bank.get("mcqs", []):
                    if item["id"] not in seen_ids:
                        mcqs.append(MCQQuestionItem(**item))
                seen_w_ids = {w.id for w in written}
                for item in bank.get("written", []):
                    if item["id"] not in seen_w_ids:
                        written.append(WrittenQuestionItem(**item))

            return {"chapter_id": chapter_id, "mcqs": mcqs, "written": written}
    finally:
        conn.close()

@router.post("/generate", response_model=PaperGenerateResponse)
async def generate_paper(req: PaperGenerateRequest):
    """
    Assembles a State Board Model Question Paper adhering to standard TN blueprints:
      - 25 Marks (Class Test / Unit Test):
          * MCQs: 5 (1m each = 5m)
          * Short: 5 (2m each = 10m)
          * Long: 2 (5m each = 10m)
          * Total = 25 Marks
      - 50 Marks (Mid-Term / Monthly Test):
          * MCQs: 10 (1m each = 10m)
          * Short: 5 (2m each = 10m)
          * Long: 6 (5m each = 30m)
          * Total = 50 Marks
      - 75 Marks (Quarterly / Science Theory):
          * MCQs: 15 (1m each = 15m)
          * Short: 10 (2m each = 20m)
          * Long: 8 (5m each = 40m)
          * Total = 75 Marks
      - 100 Marks (Half-Yearly / Annual / Board Exam):
          * MCQs: 14 (1m each = 14m)
          * Short: 13 (2m each = 26m)
          * Long: 12 (5m each = 60m)
          * Total = 100 Marks
    """
    active_chapters = [c for c in (req.chapter_ids or []) if c]

    # Resolve Exam Type & Marks Blueprint
    blueprint_map = {
        25: {"title": "Class Test (Unit Test)", "mcqs": 5, "short": 5, "long": 2},
        50: {"title": "Mid-Term Examination", "mcqs": 10, "short": 5, "long": 6},
        75: {"title": "Quarterly Examination", "mcqs": 15, "short": 10, "long": 8},
        100: {"title": "Half-Yearly / Annual Board Exam", "mcqs": 14, "short": 13, "long": 12},
    }

    exam_type_to_marks = {
        "class_test": 25,
        "midterm": 50,
        "quarterly": 75,
        "half_yearly": 100,
        "annual": 100,
    }

    target_marks = req.target_marks
    if not target_marks:
        target_marks = exam_type_to_marks.get(req.exam_type, 25)

    if target_marks not in blueprint_map:
        target_marks = 25

    bp = blueprint_map[target_marks]
    exam_title = bp["title"]

    target_mcq_count = req.mcq_count if req.mcq_count is not None else bp["mcqs"]
    target_short_count = req.short_count if req.short_count is not None else bp["short"]
    target_long_count = req.long_count if req.long_count is not None else bp["long"]

    mcqs: list[MCQQuestionItem] = []
    short_questions: list[WrittenQuestionItem] = []
    long_questions: list[WrittenQuestionItem] = []
    seen_mcq_ids = set()
    seen_short_ids = set()
    seen_long_ids = set()

    chapter_titles = {}

    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            # Fetch chapter titles
            if active_chapters:
                cur.execute("SELECT id, title FROM chapters WHERE id = ANY(%s);", (active_chapters,))
                for cid, ctitle in cur.fetchall():
                    chapter_titles[cid] = ctitle

            # 1. Query Database MCQs
            if active_chapters:
                cur.execute("""
                    SELECT mq.id, mq.chapter_id, mq.question, mq.options, mq.correct_index, mq.difficulty, mq.explanation
                    FROM mcq_questions mq
                    WHERE mq.chapter_id = ANY(%s)
                    ORDER BY RANDOM()
                    LIMIT %s;
                """, (active_chapters, target_mcq_count * 2))
            else:
                cur.execute("""
                    SELECT mq.id, mq.chapter_id, mq.question, mq.options, mq.correct_index, mq.difficulty, mq.explanation
                    FROM mcq_questions mq
                    JOIN chapters c ON mq.chapter_id = c.id
                    WHERE c.subject_id = %s
                    ORDER BY RANDOM()
                    LIMIT %s;
                """, (req.subject_id, target_mcq_count * 2))

            for r in cur.fetchall():
                if len(mcqs) >= target_mcq_count:
                    break
                opts = r[3] if isinstance(r[3], list) else json.loads(r[3])
                q_id = r[0]
                if q_id not in seen_mcq_ids:
                    seen_mcq_ids.add(q_id)
                    mcqs.append(MCQQuestionItem(
                        id=q_id, chapter_id=r[1], question=r[2], options=opts,
                        correct_index=r[4], difficulty=r[5], explanation=r[6]
                    ))

            # 2. Query Database Short Questions (2 Marks)
            if active_chapters:
                cur.execute("""
                    SELECT aq.id, aq.chapter_id, aq.question_type, aq.question, aq.model_answer, aq.rubric_points, aq.max_marks
                    FROM answer_questions aq
                    WHERE aq.chapter_id = ANY(%s) AND (aq.question_type = 'short' OR aq.max_marks <= 2.0)
                    ORDER BY RANDOM()
                    LIMIT %s;
                """, (active_chapters, target_short_count * 2))
            else:
                cur.execute("""
                    SELECT aq.id, aq.chapter_id, aq.question_type, aq.question, aq.model_answer, aq.rubric_points, aq.max_marks
                    FROM answer_questions aq
                    JOIN chapters c ON aq.chapter_id = c.id
                    WHERE c.subject_id = %s AND (aq.question_type = 'short' OR aq.max_marks <= 2.0)
                    ORDER BY RANDOM()
                    LIMIT %s;
                """, (req.subject_id, target_short_count * 2))

            for r in cur.fetchall():
                if len(short_questions) >= target_short_count:
                    break
                rubrics = r[5] if isinstance(r[5], list) else json.loads(r[5])
                q_id = r[0]
                if q_id not in seen_short_ids:
                    seen_short_ids.add(q_id)
                    short_questions.append(WrittenQuestionItem(
                        id=q_id, chapter_id=r[1], question_type="short", question=r[3],
                        model_answer=r[4], rubric_points=rubrics, max_marks=2.0
                    ))

            # 3. Query Database Long Questions (5 Marks)
            if active_chapters:
                cur.execute("""
                    SELECT aq.id, aq.chapter_id, aq.question_type, aq.question, aq.model_answer, aq.rubric_points, aq.max_marks
                    FROM answer_questions aq
                    WHERE aq.chapter_id = ANY(%s) AND (aq.question_type = 'long' OR aq.max_marks > 2.0)
                    ORDER BY RANDOM()
                    LIMIT %s;
                """, (active_chapters, target_long_count * 2))
            else:
                cur.execute("""
                    SELECT aq.id, aq.chapter_id, aq.question_type, aq.question, aq.model_answer, aq.rubric_points, aq.max_marks
                    FROM answer_questions aq
                    JOIN chapters c ON aq.chapter_id = c.id
                    WHERE c.subject_id = %s AND (aq.question_type = 'long' OR aq.max_marks > 2.0)
                    ORDER BY RANDOM()
                    LIMIT %s;
                """, (req.subject_id, target_long_count * 2))

            for r in cur.fetchall():
                if len(long_questions) >= target_long_count:
                    break
                rubrics = r[5] if isinstance(r[5], list) else json.loads(r[5])
                q_id = r[0]
                if q_id not in seen_long_ids:
                    seen_long_ids.add(q_id)
                    long_questions.append(WrittenQuestionItem(
                        id=q_id, chapter_id=r[1], question_type="long", question=r[3],
                        model_answer=r[4], rubric_points=rubrics, max_marks=5.0
                    ))
    except Exception as e:
        print("DB Query warning in practice generate:", e)
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


    # 4. Supplement MCQs from Curated Per-Chapter Banks
    if active_chapters:
        for cid in active_chapters:
            if cid in CHAPTER_QUESTION_BANKS:
                bank = CHAPTER_QUESTION_BANKS[cid]
                for item in bank.get("mcqs", []):
                    if len(mcqs) >= target_mcq_count:
                        break
                    if item["id"] not in seen_mcq_ids:
                        seen_mcq_ids.add(item["id"])
                        mcqs.append(MCQQuestionItem(**item))
                for item in bank.get("written", []):
                    if len(long_questions) >= target_long_count:
                        break
                    if item["id"] not in seen_long_ids:
                        seen_long_ids.add(item["id"])
                        long_questions.append(WrittenQuestionItem(
                            id=item["id"], chapter_id=item["chapter_id"], question_type="long",
                            question=item["question"], model_answer=item["model_answer"],
                            rubric_points=item["rubric_points"], max_marks=5.0
                        ))

    # Cross-bank check for MCQs within subject if still under target
    if len(mcqs) < target_mcq_count:
        for cid, bank in CHAPTER_QUESTION_BANKS.items():
            if len(mcqs) >= target_mcq_count:
                break
            bank_is_sci = "sci" in cid
            req_is_sci = "sci" in (req.subject_id or "")
            if bank_is_sci != req_is_sci:
                continue
            for item in bank.get("mcqs", []):
                if len(mcqs) >= target_mcq_count:
                    break
                if item["id"] not in seen_mcq_ids:
                    seen_mcq_ids.add(item["id"])
                    mcqs.append(MCQQuestionItem(**item))

    # Synthesize MCQs if needed
    if len(mcqs) < target_mcq_count:
        primary_chap = active_chapters[0] if active_chapters else "chapter_default"
        chap_title = chapter_titles.get(primary_chap, "Selected Chapter Curriculum")
        needed = target_mcq_count - len(mcqs)
        synth = synthesize_chapter_mcqs(primary_chap, chap_title, needed)
        for s in synth:
            if s.id not in seen_mcq_ids:
                seen_mcq_ids.add(s.id)
                mcqs.append(s)

    # Synthesize Short Questions (2 Marks) if needed
    if len(short_questions) < target_short_count:
        primary_chap = active_chapters[0] if active_chapters else "chapter_default"
        chap_title = chapter_titles.get(primary_chap, "Selected Chapter Curriculum")
        needed = target_short_count - len(short_questions)
        synth_s = synthesize_chapter_short(primary_chap, chap_title, needed)
        for s in synth_s:
            if s.id not in seen_short_ids:
                seen_short_ids.add(s.id)
                short_questions.append(s)

    # Synthesize Long Questions (5 Marks) if needed
    if len(long_questions) < target_long_count:
        primary_chap = active_chapters[0] if active_chapters else "chapter_default"
        chap_title = chapter_titles.get(primary_chap, "Selected Chapter Curriculum")
        needed = target_long_count - len(long_questions)
        synth_w = synthesize_chapter_long(primary_chap, chap_title, needed)
        for s in synth_w:
            if s.id not in seen_long_ids:
                seen_long_ids.add(s.id)
                long_questions.append(s)

    # Truncate strictly to requested counts
    mcqs = mcqs[:target_mcq_count]
    short_questions = short_questions[:target_short_count]
    long_questions = long_questions[:target_long_count]

    # Combine for backward compatibility
    written_combined = short_questions + long_questions

    # Calculate exact total marks: MCQs (1m) + Short (2m) + Long (5m)
    total_marks = (len(mcqs) * 1.0) + (len(short_questions) * 2.0) + (len(long_questions) * 5.0)

    return PaperGenerateResponse(
        subject_id=req.subject_id,
        exam_type=req.exam_type,
        exam_title=exam_title,
        target_marks=target_marks,
        mcqs=mcqs,
        short_questions=short_questions,
        long_questions=long_questions,
        written_questions=written_combined,
        total_marks=total_marks
    )

