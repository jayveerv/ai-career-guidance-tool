import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import db, get_careers, salary_text, setup, tags  # noqa: E402

import streamlit as st  # noqa: E402

from careerguide import engine, storage  # noqa: E402
from careerguide.quiz import LIKERT, QUESTIONS, riasec_scores  # noqa: E402
from careerguide.report import build_pdf  # noqa: E402
from careerguide.vocab import PLATFORMS, RIASEC, SKILLS, STREAMS, SUBJECTS  # noqa: E402

setup("Find my career", "🚀")
ss = st.session_state
ss.setdefault("step", 1)

st.title("🚀 Find my career")
st.progress({1: 0.15, 2: 0.55, 3: 1.0}[ss.step],
            text={1: "Step 1 of 3: About you", 2: "Step 2 of 3: Interest quiz", 3: "Step 3 of 3: Your results"}[ss.step])

# ---------------- Step 1: profile ----------------
if ss.step == 1:
    with st.form("profile"):
        name = st.text_input("Your name (optional, only printed on your PDF report)", value=ss.get("name", ""))
        stream = st.selectbox("Your stream (after Class 10)", list(STREAMS), format_func=STREAMS.get,
                              index=list(STREAMS).index(ss.get("stream", "ANY")))
        subjects = st.multiselect("Subjects you enjoy (pick 1-4)", list(SUBJECTS), format_func=SUBJECTS.get,
                                  default=ss.get("subjects", []))
        skills = st.multiselect("Things you are good at (pick 2-5)", list(SKILLS), format_func=SKILLS.get,
                                default=ss.get("skills", []))
        goal = st.text_input("Your dream or goal, in your own words (optional)",
                             value=ss.get("goal", ""), placeholder="e.g. I want to become an ethical hacker")
        if st.form_submit_button("Next: Interest quiz →", type="primary"):
            if not subjects or not skills:
                st.error("Please pick at least one subject and one skill.")
            else:
                ss.update(name=name, stream=stream, subjects=subjects, skills=skills, goal=goal, step=2)
                st.rerun()

# ---------------- Step 2: quiz ----------------
elif ss.step == 2:
    st.write("Rate each statement honestly. There are no right or wrong answers.")
    with st.form("quiz"):
        answers = []
        for i, (_, q) in enumerate(QUESTIONS):
            answers.append(st.select_slider(f"**{i + 1}.** {q}", options=list(LIKERT),
                                            value=ss.get("answers", [3] * len(QUESTIONS))[i],
                                            format_func=LIKERT.get, key=f"q{i}"))
        back, nxt = st.columns([1, 3])
        go_back = back.form_submit_button("← Back")
        done = nxt.form_submit_button("See my careers →", type="primary")
    if go_back:
        ss.update(answers=answers, step=1)
        st.rerun()
    if done:
        ss.update(answers=answers, step=3, logged=False)
        st.rerun()

# ---------------- Step 3: results ----------------
else:
    profile = engine.Profile(interest=riasec_scores(ss.answers), subjects=ss.subjects,
                             skills=ss.skills, stream=ss.stream, goal=ss.goal)
    careers = get_careers()
    only = st.toggle("Show only careers open to my stream", value=False)
    results = engine.recommend(profile, careers, top=5, only_eligible=only)
    if not ss.get("logged"):
        storage.log_session(db(), ss.stream, engine.top_interests(profile),
                            [r["career"]["id"] for r in results])
        ss.logged = True

    left, right = st.columns([3, 2])
    with left:
        st.subheader("Your interest profile")
        for k in sorted(RIASEC, key=lambda t: -profile.interest[t]):
            pct = round(profile.interest[k] * 100)
            st.progress(pct / 100, text=f"**{RIASEC[k][0]}**: {pct}%")
    with right:
        st.subheader("What it means")
        for k in engine.top_interests(profile):
            st.markdown(f"**{RIASEC[k][0]}**: {RIASEC[k][1]}.")
        st.caption("RIASEC (Holland codes) is a standard interest model used in career counselling.")

    st.subheader("Your top 5 career matches")
    for i, r in enumerate(results, 1):
        c = r["career"]
        with st.container(border=True):
            a, b = st.columns([5, 1])
            a.markdown(f"### {i}. {c['name']}")
            a.markdown(f"<span class='cg-muted'>{c['category']}</span>", unsafe_allow_html=True)
            b.markdown(f"<div class='cg-match'>{r['match']}%</div><div class='cg-muted'>match</div>",
                       unsafe_allow_html=True)
            st.write(c["summary"])
            st.markdown("**Why it fits you**")
            for reason in r["reasons"]:
                st.markdown(f"- {reason}")
            with st.expander("Roadmap, exams, salary and free courses"):
                st.markdown(f"**A typical day:** {c.get('day', '')}")
                st.markdown(f"**Education:** {c.get('education', '')}")
                if c.get("exams"):
                    st.markdown("**Entrance / qualifying exams:** " + tags(c["exams"]), unsafe_allow_html=True)
                st.markdown(f"**Salary in India:** {salary_text(c)}")
                st.markdown("**Step-by-step roadmap**")
                for n, step in enumerate(c["roadmap"], 1):
                    st.markdown(f"{n}. {step}")
                if c.get("courses"):
                    st.markdown("**Free courses to start with**")
                    for x in c["courses"]:
                        st.markdown(f"- [{x['platform']}]({PLATFORMS.get(x['platform'], '#')}): search *{x['topic']}*")
            f1, f2, _ = st.columns([1, 1, 4])
            key = f"fb_{c['id']}"
            if ss.get(key):
                st.caption("Thanks for your feedback!")
            else:
                if f1.button("👍 Helpful", key=key + "_y"):
                    storage.add_feedback(db(), c["id"], True)
                    ss[key] = True
                    st.rerun()
                if f2.button("👎 Not for me", key=key + "_n"):
                    storage.add_feedback(db(), c["id"], False)
                    ss[key] = True
                    st.rerun()

    st.divider()
    pdf = build_pdf(profile, results, ss.get("name", ""))
    d1, d2 = st.columns(2)
    d1.download_button("📄 Download my career report (PDF)", data=pdf, file_name="My_Career_Report.pdf",
                       mime="application/pdf", type="primary")
    if d2.button("↺ Start again"):
        for k in ["step", "answers", "logged"] + [k for k in ss if str(k).startswith("fb_")]:
            ss.pop(k, None)
        st.rerun()
    st.caption("This is guidance, not a final decision. Discuss your options with teachers, parents and "
               "people working in these careers.")
