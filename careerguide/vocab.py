"""Shared vocabulary: interest types, school subjects, skills and streams.

Every career and every user profile is described with these same keys, so the
recommendation engine can compare them as vectors.
"""

# Holland's RIASEC interest types, a standard model used in career counselling.
RIASEC = {
    "R": ("Realistic", "Doer: likes hands-on work with tools, machines, the outdoors"),
    "I": ("Investigative", "Thinker: likes solving problems, science, research"),
    "A": ("Artistic", "Creator: likes art, design, writing, new ideas"),
    "S": ("Social", "Helper: likes teaching, caring for and guiding people"),
    "E": ("Enterprising", "Persuader: likes leading, selling, starting things"),
    "C": ("Conventional", "Organiser: likes order, data, rules, accuracy"),
}

SUBJECTS = {
    "maths": "Mathematics",
    "physics": "Physics",
    "chemistry": "Chemistry",
    "biology": "Biology",
    "computers": "Computer Science",
    "accounts": "Accountancy",
    "economics": "Economics",
    "business": "Business Studies",
    "languages": "Languages and Literature",
    "history_civics": "History, Political Science, Civics",
    "art_design": "Art and Design",
    "geography": "Geography and Environment",
    "sports": "Physical Education and Sports",
}

SKILLS = {
    "logic": "Logical thinking",
    "coding": "Coding",
    "numbers": "Working with numbers",
    "research": "Research and curiosity",
    "communication": "Communication",
    "public_speaking": "Public speaking",
    "writing": "Writing",
    "creativity": "Creativity",
    "visual": "Drawing and visual sense",
    "leadership": "Leadership",
    "teamwork": "Teamwork",
    "empathy": "Empathy and patience with people",
    "detail": "Attention to detail",
    "hands_on": "Hands-on and technical work",
    "discipline": "Discipline and fitness",
}

# Stream after Class 10. A career lists the streams that can lead to it.
STREAMS = {
    "PCM": "Science with Maths (PCM)",
    "PCB": "Science with Biology (PCB)",
    "COM": "Commerce",
    "ARTS": "Arts / Humanities",
    "ANY": "Not decided yet / Other",
}

CATEGORIES = [
    "Engineering and Technology",
    "Medical and Health",
    "Commerce, Finance and Business",
    "Arts, Design and Media",
    "Government, Law and Defence",
    "Science and Research",
    "Other Professional Careers",
]

# Platforms named in the B.Tech proposal, plus other free government platforms.
PLATFORMS = {
    "SWAYAM": "https://swayam.gov.in",
    "NPTEL": "https://nptel.ac.in",
    "DIKSHA": "https://diksha.gov.in",
    "Skill India Digital": "https://www.skillindiadigital.gov.in",
    "e-PG Pathshala": "https://epgp.inflibnet.ac.in",
}
