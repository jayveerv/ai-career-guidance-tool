# AI based Career Guidance Tool

B.Tech 6th Semester Minor Project, Parul Institute of Technology, Parul University.
Team: Ayush Kumar, Divya Patel, Jayveerkumar Vasava · Supervisor: Dr. Bijal Talati

**Live app:** https://ai-career-guidance-tool-z69smste3d9upcvsmjrlwv.streamlit.app

A web app that helps students choose a career. The student enters their stream,
favourite subjects, skills and goal, and answers an 18-question interest quiz.
The AI engine then returns the **top 5 matching careers** with a match %, the
reasons, a step-by-step roadmap, entrance exams, an approximate Indian salary
range and free courses (SWAYAM, NPTEL, DIKSHA, Skill India Digital). A PDF
report can be downloaded.

## Features (mapped to the project modules)

| Module in the proposal | In this version |
|---|---|
| User profile | Stream, subjects, skills, goal (name only for the PDF, never stored) |
| AI recommendation engine | Content-based filtering with scikit-learn cosine similarity over 34 features, with plain-language reasons |
| User interface, mobile compatible | Streamlit app, works on phone and laptop |
| Data integration | 40 careers in 7 fields (`data/careers.json`), free course platforms |
| Admin panel | Password login, dashboard, feedback, add / edit / delete careers with automatic backups |
| Feedback and evaluation | 👍 / 👎 on each suggestion, helpful % per career |
| Reporting and analytics | Charts of most recommended careers and students by stream, CSV export |
| Data privacy and security | Only anonymous counts are stored locally in SQLite; admin password via environment variable |
| Ethics and bias | Gender, caste, religion and income are never asked or used |

Not included: live data from DIKSHA / SWAYAM (no public API, so the tool links to
the platforms) and contact details of real professionals.

## How the AI works

1. **Interest quiz (RIASEC).** 18 statements, 3 for each of Holland's six types:
   Realistic, Investigative, Artistic, Social, Enterprising, Conventional. Each
   type gets a score from 0 to 1.
2. **Vectors.** The student and every career become vectors over the same
   features: 6 interest types, 13 subjects and 15 skills. A career's code such
   as `ICR` gives weights 1.0, 0.7 and 0.4 to its three types.
3. **Similarity.** Cosine similarity is computed for each block and combined:
   interest 50%, skills 30%, subjects 20%. A goal that mentions the career
   (for example "ethical hacker") adds 10 points. If the student's stream does
   not normally lead to the career, the score is multiplied by 0.75 and a note
   is shown.
4. **Explanation.** The reasons list the interest types, skills, subjects and
   goal words that the student and the career share.

The method is deterministic: the same answers always give the same result.

## Run it

**Windows:** double-click `run_app.bat`.
**Linux / macOS:** `./run_app.sh`.
Or manually:

```bash
pip install -r requirements.txt
streamlit run app/Home.py
```

The app opens at http://localhost:8501.
Admin password: set the `CG_ADMIN_PASSWORD` environment variable before starting.
Without it the demo password is `admin123`.

## Tests

```bash
pip install -r requirements-dev.txt
python -m pytest
```

13 tests cover the dataset, quiz scoring, recommendations for technical,
medical and creative profiles, goal matching, the stream filter, explanations,
storage and the PDF report.

## Project structure

```
app/                 Streamlit pages (Home, Find My Career, Career Explorer, Admin)
careerguide/         engine.py (AI), quiz.py, report.py (PDF), storage.py (SQLite), vocab.py
data/careers.json    40 careers (regenerate with python tools/build_careers.py)
tests/               pytest tests
```

## Note on data

Salaries are rough Indian ranges in lakh per annum (LPA) for planning only.
Course entries name a free platform and a topic to search there. Students
should confirm details with teachers, counsellors and official exam websites.
