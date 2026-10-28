"""
seed_bulk_mcqs.py
-----------------
Populates comprehensive, board-accurate MCQ question banks directly into PostgreSQL (mcq_questions table)
for all chapters across TN State Board (Classes 10 & 12) and CBSE (Classes 10 & 12).
"""
import json
import psycopg2
from ingestion.db import get_connection

BULK_MCQS = [
    # =========================================================================
    # TN Class 10 English - Unit 1: His First Flight
    # =========================================================================
    {
        "id": "mcq_tn10_eng_u1_1",
        "chapter_id": "tn_10_eng_ch1",
        "question": "Who is the author of the story 'His First Flight'?",
        "options": ["Liam O'Flaherty", "Alphonse Daudet", "Satyajit Ray", "Arthur Conan Doyle"],
        "correct_index": 0,
        "difficulty": "easy",
        "explanation": "Liam O'Flaherty, an Irish novelist and short story writer, wrote 'His First Flight'."
    },
    {
        "id": "mcq_tn10_eng_u1_2",
        "chapter_id": "tn_10_eng_ch1",
        "question": "Why was the young seagull afraid to fly?",
        "options": ["He had hurt wings", "He felt his wings would never support him over the vast sea", "His parents told him not to fly", "He preferred walking on the ledge"],
        "correct_index": 1,
        "difficulty": "easy",
        "explanation": "He looked at the expansive sea beneath and feared his wings would give way."
    },
    {
        "id": "mcq_tn10_eng_u1_3",
        "chapter_id": "tn_10_eng_ch1",
        "question": "What bait did the mother seagull use to compel the young seagull to dive?",
        "options": ["A crab", "A piece of fish", "An insect", "Seaweed"],
        "correct_index": 1,
        "difficulty": "easy",
        "explanation": "The mother flew close with a piece of fish in her beak, halting just out of reach to provoke his dive."
    },
    {
        "id": "mcq_tn10_eng_u1_4",
        "chapter_id": "tn_10_eng_ch1",
        "question": "How long had the young seagull been left alone without food on the ledge?",
        "options": ["12 hours", "24 hours", "36 hours", "48 hours"],
        "correct_index": 1,
        "difficulty": "medium",
        "explanation": "Since the previous day, twenty-four hours had passed with no one approaching him with food."
    },
    {
        "id": "mcq_tn10_eng_u1_5",
        "chapter_id": "tn_10_eng_ch1",
        "question": "What did the young seagull feel when he finally opened his wings and soared?",
        "options": ["He felt dizzy and sank", "Wind rushed against his breast feathers and his fear vanished", "His wings snapped", "He fell straight into the water"],
        "correct_index": 1,
        "difficulty": "medium",
        "explanation": "The wind rushed against his breast feathers, stomach, and wingtips as he mastered soaring."
    },

    # =========================================================================
    # TN Class 10 English - Unit 2: Empowered Women Navigating The World
    # =========================================================================
    {
        "id": "mcq_tn10_eng_u2_1",
        "chapter_id": "tn_10_eng_ch2",
        "question": "What was the official name of the circumnavigation voyage conducted by the Indian Navy women officers?",
        "options": ["Samudra Manthan", "Navika Sagar Parikrama", "Sagar Kanya", "Nari Shakti Jal Marg"],
        "correct_index": 1,
        "difficulty": "easy",
        "explanation": "The historic circumnavigation expedition was titled 'Navika Sagar Parikrama'."
    },
    {
        "id": "mcq_tn10_eng_u2_2",
        "chapter_id": "tn_10_eng_ch2",
        "question": "Who served as the skipper of the INSV Tarini all-woman crew?",
        "options": ["Lt. Pratibha Jamwal", "Lt. Cdr. Vartika Joshi", "Lt. P. Swathi", "Lt. S. Vijaya Devi"],
        "correct_index": 1,
        "difficulty": "easy",
        "explanation": "Lieutenant Commander Vartika Joshi was the skipper leading the six-member crew."
    },
    {
        "id": "mcq_tn10_eng_u2_3",
        "chapter_id": "tn_10_eng_ch2",
        "question": "How many total days did the INSV Tarini take to circumnavigate the globe?",
        "options": ["200 days", "254 days", "300 days", "365 days"],
        "correct_index": 1,
        "difficulty": "medium",
        "explanation": "The crew completed the global journey in 254 days, returning to Goa on 21 May 2018."
    },
    {
        "id": "mcq_tn10_eng_u2_4",
        "chapter_id": "tn_10_eng_ch2",
        "question": "What was the primary motive behind using INSV Tarini instead of an engine-driven warship?",
        "options": ["Cost cutting", "Harnessing environment-friendly wind energy and promoting indigenous manufacturing", "Testing engine spares", "Conducting deep-sea mining"],
        "correct_index": 1,
        "difficulty": "medium",
        "explanation": "Tarini is an indigenously built sailboat that utilizes eco-friendly wind energy, promoting 'Make in India'."
    },

    # =========================================================================
    # TN Class 10 English - Unit 3: The Attic (Satyajit Ray)
    # =========================================================================
    {
        "id": "mcq_tn10_eng_u3_1",
        "chapter_id": "tn_10_eng_ch3",
        "question": "Who wrote the nostalgic short story 'The Attic'?",
        "options": ["Rabindranath Tagore", "Satyajit Ray", "R.K. Narayan", "Mulk Raj Anand"],
        "correct_index": 1,
        "difficulty": "easy",
        "explanation": "'The Attic' was originally written in Bengali by the legendary filmmaker and writer Satyajit Ray."
    },
    {
        "id": "mcq_tn10_eng_u3_2",
        "chapter_id": "tn_10_eng_ch3",
        "question": "What was the ancestral village that Aditya and the narrator visited?",
        "options": ["Bramhapur", "Deoprayag", "Santiniketan", "Malguci"],
        "correct_index": 0,
        "difficulty": "medium",
        "explanation": "Aditya and the narrator detoured to visit Bramhapur, Aditya's ancestral birthplace."
    },
    {
        "id": "mcq_tn10_eng_u3_3",
        "chapter_id": "tn_10_eng_ch3",
        "question": "What article had Aditya kept in the attic twenty-nine years ago?",
        "options": ["An old wristwatch", "A silver medal won by Sasanka Sanyal", "A diary", "A gold coin"],
        "correct_index": 1,
        "difficulty": "easy",
        "explanation": "Aditya retrieved the silver medal awarded to Sasanka Sanyal for reciting Tagore's poem."
    },
    {
        "id": "mcq_tn10_eng_u3_4",
        "chapter_id": "tn_10_eng_ch3",
        "question": "Why did Sasanka Sanyal refuse to accept the money Aditya offered him at the end?",
        "options": ["He had plenty of wealth", "He wanted his lost medal and his self-respect back, not cash", "He was frightened of Aditya", "The money was counterfeit"],
        "correct_index": 1,
        "difficulty": "medium",
        "explanation": "Sanyal valued his dignity and the cherished medal higher than monetary compensation."
    },

    # =========================================================================
    # TN Class 10 English - Unit 4: Tech Bloomers
    # =========================================================================
    {
        "id": "mcq_tn10_eng_u4_1",
        "chapter_id": "tn_10_eng_ch4",
        "question": "In 'Tech Bloomers', which assistive technology allowed Alisha to type despite cerebral palsy?",
        "options": ["Dragon Dictate (Speech Recognition)", "Braille keyboard", "Touch Stylus", "Pencil grip"],
        "correct_index": 0,
        "difficulty": "easy",
        "explanation": "Dragon Dictate speech-recognition software enabled Alisha to speak words that appeared directly on screen."
    },
    {
        "id": "mcq_tn10_eng_u4_2",
        "chapter_id": "tn_10_eng_ch4",
        "question": "What device did David use to control his wheelchair and communication device using eye movements?",
        "options": ["Eye Gaze tracker / ECO2 system", "Laser pointer", "Headphone switch", "Bluetooth joystick"],
        "correct_index": 0,
        "difficulty": "medium",
        "explanation": "David utilized the ECO2 with an Eye Gaze camera system operated entirely through eye blinks and gaze."
    },
    {
        "id": "mcq_tn10_eng_u4_3",
        "chapter_id": "tn_10_eng_ch4",
        "question": "According to the lesson, technology is the greatest equalizer especially for:",
        "options": ["Corporate workers", "Specially abled (differently-abled) people", "Astronauts", "Politicians"],
        "correct_index": 1,
        "difficulty": "easy",
        "explanation": "Technology empowers differently-abled individuals to live independently and communicate with confidence."
    },

    # =========================================================================
    # TN Class 10 English - Unit 5: The Last Lesson
    # =========================================================================
    {
        "id": "mcq_tn10_eng_u5_1",
        "chapter_id": "tn_10_eng_ch5",
        "question": "What final phrase did M. Hamel write in huge letters on the blackboard before ending class?",
        "options": ["Vive la République!", "Vive La France!", "Liberté, Égalité, Fraternité", "Adieu Alsace"],
        "correct_index": 1,
        "difficulty": "easy",
        "explanation": "Taking a piece of chalk, M. Hamel wrote as large as he could: 'Vive La France!' (Long Live France!)."
    },
    {
        "id": "mcq_tn10_eng_u5_2",
        "chapter_id": "tn_10_eng_ch5",
        "question": "Which two French districts were annexed by Prussia requiring German to be taught?",
        "options": ["Alsace and Lorraine", "Normandy and Brittany", "Provence and Aquitaine", "Corsica and Savoy"],
        "correct_index": 0,
        "difficulty": "easy",
        "explanation": "Berlin issued an order that only German would be taught in the schools of Alsace and Lorraine."
    },
    {
        "id": "mcq_tn10_eng_u5_3",
        "chapter_id": "tn_10_eng_ch5",
        "question": "How did M. Hamel describe holding fast to one's mother language?",
        "options": ["Like carrying a useless load", "As holding the key to their prison", "As a temporary shield", "As a barrier to progress"],
        "correct_index": 1,
        "difficulty": "medium",
        "explanation": "He declared that as long as an enslaved people held fast to their language, it was as if they had the key to their prison."
    },

    # =========================================================================
    # TN Class 10 English - Unit 6: The Dying Detective
    # =========================================================================
    {
        "id": "mcq_tn10_eng_u6_1",
        "chapter_id": "tn_10_eng_ch6",
        "question": "Who created the famous character Sherlock Holmes in 'The Dying Detective'?",
        "options": ["Agatha Christie", "Sir Arthur Conan Doyle", "Edgar Allan Poe", "G.K. Chesterton"],
        "correct_index": 1,
        "difficulty": "easy",
        "explanation": "Sir Arthur Conan Doyle wrote the Sherlock Holmes detective series."
    },
    {
        "id": "mcq_tn10_eng_u6_2",
        "chapter_id": "tn_10_eng_ch6",
        "question": "Who was the culprit summoned by Watson who had supposedly infected Victor Savage?",
        "options": ["Professor Moriarty", "Culverton Smith", "Dr. Roylott", "John Clay"],
        "correct_index": 1,
        "difficulty": "medium",
        "explanation": "Culverton Smith was the plantation owner from Sumatra who possessed knowledge of the deadly infectious disease."
    },
    {
        "id": "mcq_tn10_eng_u6_3",
        "chapter_id": "tn_10_eng_ch6",
        "question": "How did Culverton Smith attempt to assassinate Sherlock Holmes?",
        "options": ["By poisoning his tea", "Through an infected ivory box with a hidden spring needle", "By shooting him", "With chloroform"],
        "correct_index": 1,
        "difficulty": "medium",
        "explanation": "Smith posted an ivory box containing an infected spring-loaded needle designed to prick the opener."
    },
    {
        "id": "mcq_tn10_eng_u6_4",
        "chapter_id": "tn_10_eng_ch6",
        "question": "Who was concealed behind the head of Holmes's bed as a witness to Culverton Smith's confession?",
        "options": ["Inspector Morton", "Dr. Watson", "Mrs. Hudson", "Mycroft Holmes"],
        "correct_index": 1,
        "difficulty": "medium",
        "explanation": "Dr. Watson was instructed to hide behind the bed headboard to witness the entire conversation."
    },

    # =========================================================================
    # TN Class 10 English - Unit 7: A Dilemma
    # =========================================================================
    {
        "id": "mcq_tn10_eng_u7_1",
        "chapter_id": "tn_10_eng_ch7",
        "question": "Who is the author of the story 'A Dilemma'?",
        "options": ["Silas Weir Mitchell", "O. Henry", "Guy de Maupassant", "H.G. Wells"],
        "correct_index": 0,
        "difficulty": "easy",
        "explanation": "Silas Weir Mitchell, an American physician and writer, authored 'A Dilemma'."
    },
    {
        "id": "mcq_tn10_eng_u7_2",
        "chapter_id": "tn_10_eng_ch7",
        "question": "What booby-trap did Uncle Philip place inside the iron box containing precious gems?",
        "options": ["Poisonous gas", "Dynamite rigged to detonate upon opening the lid", "A cobra", "Corrosive acid"],
        "correct_index": 1,
        "difficulty": "easy",
        "explanation": "Uncle Philip placed dynamite with a trigger spring that would blow anyone to pieces upon opening the box."
    },
    {
        "id": "mcq_tn10_eng_u7_3",
        "chapter_id": "tn_10_eng_ch7",
        "question": "What did the nephew finally decide to do with the perilous iron box in his will?",
        "options": ["Drop it in the ocean", "Bequeath it to the Society for the Preservation of Human Vivisection", "Open it with a rifle from afar", "Bury it under a tree"],
        "correct_index": 1,
        "difficulty": "medium",
        "explanation": "Out of sheer frustration and sleeplessness, Tom willed the lethal treasure box to the Society."
    },

    # =========================================================================
    # CBSE Class 10 Science - Chapter 1: Chemical Reactions and Equations
    # =========================================================================
    {
        "id": "mcq_cbse10_sci_c1_1",
        "chapter_id": "cbse_10_sci_ch1",
        "question": "Which of the following observations confirms a chemical reaction has taken place?",
        "options": ["Change in state and color", "Evolution of gas", "Change in temperature", "All of the above"],
        "correct_index": 3,
        "difficulty": "easy",
        "explanation": "Chemical reactions are typically accompanied by state change, color change, gas evolution, or temperature change."
    },
    {
        "id": "mcq_cbse10_sci_c1_2",
        "chapter_id": "cbse_10_sci_ch1",
        "question": "What happens when magnesium ribbon is burned in air?",
        "options": ["Burns with a dazzling white flame forming white powder (MgO)", "Produces black residue", "Forms liquid magnesium", "Releases pungent chlorine gas"],
        "correct_index": 0,
        "difficulty": "easy",
        "explanation": "Magnesium reacts vigorously with oxygen: 2Mg + O2 -> 2MgO (dazzling white flame and white powder)."
    },
    {
        "id": "mcq_cbse10_sci_c1_3",
        "chapter_id": "cbse_10_sci_ch1",
        "question": "In the reaction: Fe2O3 + 2Al -> Al2O3 + 2Fe, what type of reaction is this?",
        "options": ["Combination reaction", "Displacement and redox reaction (Thermite)", "Decomposition reaction", "Precipitation reaction"],
        "correct_index": 1,
        "difficulty": "medium",
        "explanation": "Aluminum displaces iron from ferric oxide; it is a highly exothermic displacement/redox reaction."
    },
    {
        "id": "mcq_cbse10_sci_c1_4",
        "chapter_id": "cbse_10_sci_ch1",
        "question": "Why is respiration considered an exothermic reaction?",
        "options": ["Heat is absorbed during breathing", "Glucose combines with oxygen in cells to release energy", "It requires external light", "Lactic acid cools muscles"],
        "correct_index": 1,
        "difficulty": "medium",
        "explanation": "C6H12O6 + 6O2 -> 6CO2 + 6H2O + Energy (releases energy, hence exothermic)."
    },
    {
        "id": "mcq_cbse10_sci_c1_5",
        "chapter_id": "cbse_10_sci_ch1",
        "question": "What gas is flushed into potato chip packets to prevent rancidity?",
        "options": ["Oxygen", "Carbon dioxide", "Nitrogen", "Argon"],
        "correct_index": 2,
        "difficulty": "easy",
        "explanation": "Nitrogen is an unreactive antioxidant gas that prevents oil and fat oxidation."
    },
    {
        "id": "mcq_cbse10_sci_c1_6",
        "chapter_id": "cbse_10_sci_ch1",
        "question": "Which compound is quick lime?",
        "options": ["CaCO3", "Ca(OH)2", "CaO", "CaCl2"],
        "correct_index": 2,
        "difficulty": "easy",
        "explanation": "Calcium oxide (CaO) is known as quick lime; reacting with water gives slaked lime Ca(OH)2."
    },

    # =========================================================================
    # CBSE Class 10 Science - Chapter 2: Acids, Bases and Salts
    # =========================================================================
    {
        "id": "mcq_cbse10_sci_c2_1",
        "chapter_id": "cbse_10_sci_ch2",
        "question": "What is the pH range of human blood under healthy conditions?",
        "options": ["2.0 - 3.5", "5.5 - 6.5", "7.35 - 7.45", "9.0 - 10.5"],
        "correct_index": 2,
        "difficulty": "medium",
        "explanation": "Human blood pH is tightly regulated within the slightly alkaline range of 7.35 to 7.45."
    },
    {
        "id": "mcq_cbse10_sci_c2_2",
        "chapter_id": "cbse_10_sci_ch2",
        "question": "What is the chemical formula of Plaster of Paris?",
        "options": ["CaSO4 · 2H2O", "CaSO4 · 1/2 H2O", "CaSO4 · 5H2O", "2CaSO4 · 4H2O"],
        "correct_index": 1,
        "difficulty": "easy",
        "explanation": "Plaster of Paris is calcium sulphate hemihydrate: CaSO4 · 1/2 H2O."
    },
    {
        "id": "mcq_cbse10_sci_c2_3",
        "chapter_id": "cbse_10_sci_ch2",
        "question": "Tooth enamel begins to decay when the pH of the mouth drops below:",
        "options": ["7.0", "6.5", "5.5", "4.0"],
        "correct_index": 2,
        "difficulty": "medium",
        "explanation": "At pH below 5.5, calcium hydroxyapatite in tooth enamel corrodes due to bacterial acids."
    },
    {
        "id": "mcq_cbse10_sci_c2_4",
        "chapter_id": "cbse_10_sci_ch2",
        "question": "Which gas is liberated when an acid reacts with a metal?",
        "options": ["Oxygen gas", "Hydrogen gas (H2)", "Carbon dioxide", "Nitrogen dioxide"],
        "correct_index": 1,
        "difficulty": "easy",
        "explanation": "Acid + Metal -> Salt + Hydrogen gas (testable by burning with a pop sound)."
    },
    {
        "id": "mcq_cbse10_sci_c2_5",
        "chapter_id": "cbse_10_sci_ch2",
        "question": "Which acid is present in stinging nettle leaves and ant stings?",
        "options": ["Acetic acid", "Methanoic acid (Formic acid)", "Citric acid", "Oxalic acid"],
        "correct_index": 1,
        "difficulty": "easy",
        "explanation": "Ant bites and nettle stings inject methanoic acid (HCOOH), causing acute burning."
    },

    # =========================================================================
    # CBSE Class 10 Science - Chapter 3: Metals and Non-Metals
    # =========================================================================
    {
        "id": "mcq_cbse10_sci_c3_1",
        "chapter_id": "cbse_10_sci_ch3",
        "question": "Which metal exists in liquid state at room temperature?",
        "options": ["Sodium", "Mercury", "Gallium", "Bromine"],
        "correct_index": 1,
        "difficulty": "easy",
        "explanation": "Mercury (Hg) is the only metal that is liquid at standard room temperature."
    },
    {
        "id": "mcq_cbse10_sci_c3_2",
        "chapter_id": "cbse_10_sci_ch3",
        "question": "Which non-metal is lustrous and has a shiny appearance?",
        "options": ["Carbon", "Iodine", "Sulphur", "Phosphorus"],
        "correct_index": 1,
        "difficulty": "easy",
        "explanation": "Iodine crystals have a characteristic metallic luster despite being a non-metal."
    },
    {
        "id": "mcq_cbse10_sci_c3_3",
        "chapter_id": "cbse_10_sci_ch3",
        "question": "What is an amphoteric oxide?",
        "options": ["An oxide that dissolves in water", "An oxide that reacts with both acids and bases to yield salt and water", "An oxide of non-metals only", "A neutral gas"],
        "correct_index": 1,
        "difficulty": "medium",
        "explanation": "Oxides like Al2O3 and ZnO react with both acids and bases, demonstrating amphoteric character."
    },
    {
        "id": "mcq_cbse10_sci_c3_4",
        "chapter_id": "cbse_10_sci_ch3",
        "question": "Which metal does NOT corrode easily and is widely used for electroplating iron?",
        "options": ["Sodium", "Zinc (Galvanization)", "Magnesium", "Potassium"],
        "correct_index": 1,
        "difficulty": "easy",
        "explanation": "Zinc coating shields iron galvanically from air and moisture to avert rusting."
    },
    {
        "id": "mcq_cbse10_sci_c3_5",
        "chapter_id": "cbse_10_sci_ch3",
        "question": "What is Aqua Regia composed of?",
        "options": ["3:1 concentrated HCl to concentrated HNO3", "1:3 concentrated HCl to concentrated HNO3", "Equal parts H2SO4 and HNO3", "Pure concentrated acetic acid"],
        "correct_index": 0,
        "difficulty": "medium",
        "explanation": "Aqua Regia ('Royal Water') is 3 parts concentrated HCl and 1 part concentrated HNO3, dissolving noble metals."
    },

    # =========================================================================
    # CBSE Class 10 Science - Chapter 4: Life Processes
    # =========================================================================
    {
        "id": "mcq_cbse10_sci_c4_1",
        "chapter_id": "cbse_10_sci_ch4",
        "question": "Where does the light-dependent phase of photosynthesis primarily occur?",
        "options": ["Stroma of chloroplast", "Thylakoid / Grana membranes", "Mitochondrial matrix", "Cytoplasm"],
        "correct_index": 1,
        "difficulty": "medium",
        "explanation": "Chlorophyll pigments within grana/thylakoids absorb light energy to photolyse water and form ATP/NADPH."
    },
    {
        "id": "mcq_cbse10_sci_c4_2",
        "chapter_id": "cbse_10_sci_ch4",
        "question": "What is the structural and functional filtration unit of the human kidney?",
        "options": ["Neuron", "Nephron", "Alveolus", "Villus"],
        "correct_index": 1,
        "difficulty": "easy",
        "explanation": "Nephrons filter blood, reabsorb essential nutrients, and produce urine in the kidneys."
    },
    {
        "id": "mcq_cbse10_sci_c4_3",
        "chapter_id": "cbse_10_sci_ch4",
        "question": "Which enzyme initiates starch digestion in the human buccal cavity?",
        "options": ["Pepsin", "Salivary Amylase (Ptyalin)", "Trypsin", "Lipase"],
        "correct_index": 1,
        "difficulty": "easy",
        "explanation": "Salivary amylase breaks down complex starch polysaccharides into maltose."
    },
    {
        "id": "mcq_cbse10_sci_c4_4",
        "chapter_id": "cbse_10_sci_ch4",
        "question": "In humans, deoxygenated blood from body tissues enters which cardiac chamber first?",
        "options": ["Left Atrium", "Right Atrium", "Left Ventricle", "Right Ventricle"],
        "correct_index": 1,
        "difficulty": "easy",
        "explanation": "Superior and inferior vena cava return deoxygenated venous blood directly to the right atrium."
    },
    {
        "id": "mcq_cbse10_sci_c4_5",
        "chapter_id": "cbse_10_sci_ch4",
        "question": "Which vascular tissue transports photosynthesized sugars bidirectionally in plants?",
        "options": ["Xylem", "Phloem", "Cambium", "Pith"],
        "correct_index": 1,
        "difficulty": "easy",
        "explanation": "Phloem sieve tubes and companion cells translocate sucrose and amino acids bidirectionally."
    },

    # =========================================================================
    # TN Class 12 Physics - Unit 1: Electrostatics & CBSE Class 12 Physics Ch 1
    # =========================================================================
    {
        "id": "mcq_tn12_phy_u1_1",
        "chapter_id": "tn_12_phy_ch1",
        "question": "What is the electrostatic force between two point charges inversely proportional to, according to Coulomb's Law?",
        "options": ["Distance r", "Square of distance r²", "Cube of distance r³", "Square root of r"],
        "correct_index": 1,
        "difficulty": "easy",
        "explanation": "F = (1 / 4πε₀) * (|q1 * q2| / r²), obeying the inverse-square law."
    },
    {
        "id": "mcq_tn12_phy_u1_2",
        "chapter_id": "tn_12_phy_ch1",
        "question": "What is the electric field inside a hollow charged spherical conducting shell in electrostatic equilibrium?",
        "options": ["Uniform and maximum", "Zero", "Proportional to radius", "Infinite"],
        "correct_index": 1,
        "difficulty": "easy",
        "explanation": "By Gauss's Law, enclosing zero internal net charge results in an electric field of zero everywhere inside."
    },
    {
        "id": "mcq_tn12_phy_u1_3",
        "chapter_id": "tn_12_phy_ch1",
        "question": "What is the SI unit of electric flux (Φ_E)?",
        "options": ["N / C", "N·m² / C", "C / m²", "Volt / meter"],
        "correct_index": 1,
        "difficulty": "medium",
        "explanation": "Flux Φ = E · A = (N/C) * m² = N·m²/C (or Volt·meter)."
    },
    {
        "id": "mcq_tn12_phy_u1_4",
        "chapter_id": "tn_12_phy_ch1",
        "question": "When a dielectric slab of dielectric constant K is inserted between parallel capacitor plates connected to a battery, what happens to capacitance C?",
        "options": ["Decreases by factor K", "Increases by factor K (C = K·C₀)", "Remains unchanged", "Becomes zero"],
        "correct_index": 1,
        "difficulty": "medium",
        "explanation": "A dielectric polarizes and enhances charge storage capacity, scaling capacitance to K·C₀."
    },

    # CBSE 12 Physics Ch 1
    {
        "id": "mcq_cbse12_phy_c1_1",
        "chapter_id": "cbse_12_phy_ch1",
        "question": "Which physical quantity has the unit Coulomb per square meter (C/m²)?",
        "options": ["Linear charge density (λ)", "Surface charge density (σ)", "Volume charge density (ρ)", "Electric dipole moment"],
        "correct_index": 1,
        "difficulty": "easy",
        "explanation": "Surface charge density σ = Q / Area, with SI unit C/m²."
    },
    {
        "id": "mcq_cbse12_phy_c1_2",
        "chapter_id": "cbse_12_phy_ch1",
        "question": "What torque acts on an electric dipole p placed at angle θ in a uniform electric field E?",
        "options": ["τ = p · E", "τ = p × E (magnitude pE sin θ)", "τ = p / E", "τ = 0 always"],
        "correct_index": 1,
        "difficulty": "medium",
        "explanation": "Torque vector τ = p × E, aligning the dipole with the field."
    },

    # =========================================================================
    # TN Class 12 Physics - Unit 2: Current Electricity
    # =========================================================================
    {
        "id": "mcq_tn12_phy_u2_1",
        "chapter_id": "tn_12_phy_ch2",
        "question": "Kirchhoff's first law (Junction Rule) is a consequence of which conservation law?",
        "options": ["Conservation of Energy", "Conservation of Electric Charge", "Conservation of Momentum", "Conservation of Mass"],
        "correct_index": 1,
        "difficulty": "easy",
        "explanation": "Total current entering a junction equals current exiting, conserving electric charge."
    },
    {
        "id": "mcq_tn12_phy_u2_2",
        "chapter_id": "tn_12_phy_ch2",
        "question": "In a balanced Wheatstone bridge with resistors P, Q, R, and S, what is the balancing condition?",
        "options": ["P / Q = R / S", "P + Q = R + S", "P · Q = R · S", "P / R = S / Q"],
        "correct_index": 0,
        "difficulty": "easy",
        "explanation": "When zero galvanometer current flows, the bridge ratio holds: P / Q = R / S."
    },
    {
        "id": "mcq_tn12_phy_u2_3",
        "chapter_id": "tn_12_phy_ch2",
        "question": "How does the electrical resistance of a metallic conductor vary with temperature?",
        "options": ["Decreases linearly", "Increases as temperature increases due to higher lattice vibrations", "Remains constant", "Drops to zero at 100°C"],
        "correct_index": 1,
        "difficulty": "medium",
        "explanation": "Heating increases ionic collisions, shortening relaxation time τ and increasing resistance."
    },
    {
        "id": "mcq_tn12_phy_u2_4",
        "chapter_id": "tn_12_phy_ch2",
        "question": "What is the drift velocity of free electrons in a copper wire on the order of?",
        "options": ["Speed of light (~10^8 m/s)", "Speed of sound (~340 m/s)", "Fractions of a millimeter per second (~10^-4 m/s)", "Zero"],
        "correct_index": 2,
        "difficulty": "hard",
        "explanation": "Drift velocity is very slow (~10^-4 m/s), though electromagnetic signals travel near light speed."
    },

    # =========================================================================
    # TN Class 12 Commerce - Chapter 1: Principles of Management
    # =========================================================================
    {
        "id": "mcq_tn12_com_u1_1",
        "chapter_id": "tn_12_com_ch1",
        "question": "Who is globally celebrated as the 'Father of Scientific Management'?",
        "options": ["Henri Fayol", "Frederick Winslow Taylor (F.W. Taylor)", "Peter Drucker", "Elton Mayo"],
        "correct_index": 1,
        "difficulty": "easy",
        "explanation": "F.W. Taylor pioneered time-motion studies and scientific management principles."
    },
    {
        "id": "mcq_tn12_com_u1_2",
        "chapter_id": "tn_12_com_ch1",
        "question": "How many administrative management principles were propounded by Henri Fayol?",
        "options": ["10", "12", "14", "16"],
        "correct_index": 2,
        "difficulty": "easy",
        "explanation": "Henri Fayol authored the famous 14 General Principles of Management."
    },
    {
        "id": "mcq_tn12_com_u1_3",
        "chapter_id": "tn_12_com_ch1",
        "question": "What does Henri Fayol's principle 'Espirit de Corps' emphasize?",
        "options": ["Strict military discipline", "Team spirit and harmony among staff", "Hierarchical reporting chain", "Individual remuneration"],
        "correct_index": 1,
        "difficulty": "easy",
        "explanation": "'Esprit de Corps' emphasizes fostering team unity, morale, and collective strength."
    },
    {
        "id": "mcq_tn12_com_u1_4",
        "chapter_id": "tn_12_com_ch1",
        "question": "According to the principle of 'Unity of Command':",
        "options": ["An employee should receive orders from only one superior", "Managers should issue only written orders", "Employees can report to multiple directors", "All staff must dress uniformly"],
        "correct_index": 0,
        "difficulty": "easy",
        "explanation": "Unity of Command avoids confusion and conflicts by ensuring each employee reports to exactly one boss."
    }
]


def seed_mcqs():
    conn = get_connection()
    inserted = 0
    updated = 0
    try:
        with conn.cursor() as cur:
            for item in BULK_MCQS:
                cur.execute("""
                    INSERT INTO mcq_questions (id, chapter_id, question, options, correct_index, difficulty, explanation)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        chapter_id = EXCLUDED.chapter_id,
                        question = EXCLUDED.question,
                        options = EXCLUDED.options,
                        correct_index = EXCLUDED.correct_index,
                        difficulty = EXCLUDED.difficulty,
                        explanation = EXCLUDED.explanation;
                """, (
                    item["id"],
                    item["chapter_id"],
                    item["question"],
                    json.dumps(item["options"]),
                    item["correct_index"],
                    item["difficulty"],
                    item["explanation"]
                ))
                inserted += 1
            conn.commit()
            print(f"[x] Successfully seeded/updated {inserted} MCQs across all chapters.")
    finally:
        conn.close()


if __name__ == "__main__":
    seed_mcqs()
