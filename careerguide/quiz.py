"""Interest quiz: 18 statements, three for each RIASEC type.

The user rates each statement from 1 (not like me) to 5 (very much like me).
"""

QUESTIONS = [
    ("R", "I like fixing or building things with my hands (bikes, gadgets, furniture)."),
    ("R", "I would rather work outdoors or in a workshop than sit at a desk all day."),
    ("R", "I enjoy understanding how machines and tools work."),
    ("I", "I enjoy solving puzzles, maths problems or riddles."),
    ("I", "I often ask 'why?' and like to find out how things really work."),
    ("I", "I like doing experiments or reading about science and technology."),
    ("A", "I enjoy drawing, designing, music, writing stories or making videos."),
    ("A", "I like to do things in my own new way rather than follow fixed steps."),
    ("A", "I notice colours, styles and how things look."),
    ("S", "I like helping friends with their problems or studies."),
    ("S", "I would enjoy teaching, caring for or guiding people."),
    ("S", "I am patient and good at understanding how others feel."),
    ("E", "I like leading a group or taking charge of a project."),
    ("E", "I enjoy convincing people, selling an idea or debating."),
    ("E", "I would like to start my own business one day."),
    ("C", "I like keeping things organised: notes, files, schedules."),
    ("C", "I am careful with details and like rules to be clear."),
    ("C", "I am comfortable working with numbers, records and data."),
]

LIKERT = {1: "Not like me", 2: "A little", 3: "Somewhat", 4: "Mostly", 5: "Very much like me"}


def riasec_scores(answers):
    """answers: list of 18 ints (1-5) in QUESTIONS order -> dict type -> 0..1."""
    if len(answers) != len(QUESTIONS):
        raise ValueError(f"expected {len(QUESTIONS)} answers, got {len(answers)}")
    sums = {k: [] for k in "RIASEC"}
    for (t, _), a in zip(QUESTIONS, answers):
        if not 1 <= int(a) <= 5:
            raise ValueError("answers must be between 1 and 5")
        sums[t].append(int(a))
    return {t: (sum(v) / len(v) - 1) / 4 for t, v in sums.items()}
