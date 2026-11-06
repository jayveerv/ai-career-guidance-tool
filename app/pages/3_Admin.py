import hmac
import json
import os
import shutil
import sys
import datetime as dt
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import db, get_careers, setup  # noqa: E402

import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402

from careerguide import engine, storage  # noqa: E402
from careerguide.vocab import CATEGORIES, PLATFORMS, SKILLS, STREAMS, SUBJECTS  # noqa: E402

setup("Admin", "🔐")
st.title("🔐 Admin panel")

# Password: set CG_ADMIN_PASSWORD before starting the app. The default is only for local demos.
PASSWORD = os.environ.get("CG_ADMIN_PASSWORD", "admin123")
if not st.session_state.get("admin_ok"):
    with st.form("login"):
        pw = st.text_input("Admin password", type="password")
        if st.form_submit_button("Log in"):
            if hmac.compare_digest(pw, PASSWORD):
                st.session_state.admin_ok = True
                st.rerun()
            st.error("Wrong password.")
    if PASSWORD == "admin123":
        st.caption("Demo password is admin123. Set CG_ADMIN_PASSWORD to change it.")
    st.stop()

careers = get_careers()
names = {c["id"]: c["name"] for c in careers}
s = storage.stats(db())

tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "💬 Feedback", "🛠 Manage careers"])

with tab1:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Students guided", s["sessions"])
    m2.metric("Feedback received", s["feedback"])
    m3.metric("Found helpful", f"{s['helpful_pct']}%" if s["helpful_pct"] is not None else "-")
    m4.metric("Careers in database", len(careers))
    if s["recommended_counts"]:
        st.subheader("Most recommended careers")
        top = sorted(s["recommended_counts"].items(), key=lambda kv: -kv[1])[:10]
        st.bar_chart(pd.DataFrame({"Career": [names.get(k, k) for k, _ in top],
                                   "Times recommended": [v for _, v in top]}).set_index("Career"),
                     horizontal=True, color="#0F766E")
        st.subheader("Students by stream")
        st.bar_chart(pd.DataFrame({"Stream": [STREAMS.get(k, k) for k in s["streams"]],
                                   "Students": list(s["streams"].values())}).set_index("Stream"),
                     horizontal=True, color="#1B2A4A", height=60 + 40 * len(s["streams"]))
    else:
        st.info("No sessions yet. Statistics appear after students use 'Find my career'.")

with tab2:
    rows = storage.feedback_rows(db())
    if rows:
        df = pd.DataFrame(rows, columns=["Time", "Career", "Helpful", "Comment"])
        df["Career"] = df["Career"].map(lambda k: names.get(k, k))
        df["Helpful"] = df["Helpful"].map({1: "Yes", 0: "No"})
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button("Download feedback (CSV)", df.to_csv(index=False).encode(), "feedback.csv", "text/csv")
        st.subheader("Helpfulness by career")
        pc = s["per_career_feedback"]
        st.dataframe(pd.DataFrame([{"Career": names.get(k, k), "Ratings": t, "Helpful %": round(100 * h / t)}
                                   for k, (t, h) in pc.items()]).sort_values("Ratings", ascending=False),
                     use_container_width=True, hide_index=True)
    else:
        st.info("No feedback yet.")


def save_careers(new_list):
    for c in new_list:
        engine.validate_career(c)
    backup_dir = engine.DATA / "backups"
    backup_dir.mkdir(exist_ok=True)
    shutil.copy(engine.CAREERS_FILE, backup_dir / f"careers_{dt.datetime.now():%Y%m%d_%H%M%S}.json")
    engine.CAREERS_FILE.write_text(json.dumps(new_list, indent=2, ensure_ascii=False), encoding="utf-8")


with tab3:
    mode = st.radio("Action", ["Edit a career", "Add a new career", "Delete a career"], horizontal=True)
    base = None
    if mode == "Edit a career":
        cid = st.selectbox("Career", list(names), format_func=names.get)
        base = next(c for c in careers if c["id"] == cid)
    if mode in ("Edit a career", "Add a new career"):
        b = base or {}
        with st.form("career_form"):
            name = st.text_input("Name", b.get("name", ""))
            cid_new = st.text_input("ID (lowercase, no spaces)", b.get("id", ""), disabled=base is not None)
            cat = st.selectbox("Field", CATEGORIES, index=CATEGORIES.index(b["category"]) if b else 0)
            streams = st.multiselect("Streams", [k for k in STREAMS if k != "ANY"], b.get("streams", []),
                                     format_func=STREAMS.get)
            riasec = st.text_input("RIASEC code (1-3 letters, strongest first, e.g. ICR)", b.get("riasec", ""))
            subjects = st.multiselect("Key subjects", list(SUBJECTS), b.get("subjects", []), format_func=SUBJECTS.get)
            skills = st.multiselect("Key skills", list(SKILLS), b.get("skills", []), format_func=SKILLS.get)
            summary = st.text_area("Summary", b.get("summary", ""))
            day = st.text_area("A typical day", b.get("day", ""))
            education = st.text_input("Education", b.get("education", ""))
            exams = st.text_input("Exams (comma separated)", ", ".join(b.get("exams", [])))
            s1, s2 = st.columns(2)
            sal_e = s1.text_input("Starting salary (LPA, e.g. 4-8)", b.get("salary_entry", ""))
            sal_m = s2.text_input("Salary after 5-8 years (LPA)", b.get("salary_mid", ""))
            roadmap = st.text_area("Roadmap (one step per line)", "\n".join(b.get("roadmap", [])))
            courses = st.text_area("Free courses (one per line: Platform | topic)",
                                   "\n".join(f"{x['platform']} | {x['topic']}" for x in b.get("courses", [])),
                                   help="Platforms: " + ", ".join(PLATFORMS))
            keywords = st.text_input("Search keywords (comma separated)", ", ".join(b.get("keywords", [])))
            if st.form_submit_button("Save", type="primary"):
                new = dict(id=(base["id"] if base else cid_new.strip().lower().replace(" ", "_")),
                           name=name.strip(), category=cat, streams=streams, riasec=riasec.strip().upper(),
                           subjects=subjects, skills=skills, summary=summary.strip(), day=day.strip(),
                           education=education.strip(),
                           exams=[e.strip() for e in exams.split(",") if e.strip()],
                           salary_entry=sal_e.strip(), salary_mid=sal_m.strip(),
                           roadmap=[r.strip() for r in roadmap.splitlines() if r.strip()],
                           courses=[{"platform": p.split("|")[0].strip(), "topic": p.split("|", 1)[1].strip()}
                                    for p in courses.splitlines() if "|" in p],
                           keywords=[k.strip().lower() for k in keywords.split(",") if k.strip()])
                try:
                    if not base and new["id"] in names:
                        raise ValueError(f"ID '{new['id']}' already exists")
                    updated = [new if c["id"] == new["id"] else c for c in careers] if base else careers + [new]
                    save_careers(updated)
                    st.cache_data.clear()
                    st.success(f"Saved '{new['name']}'. A backup of the old list was kept in data/backups.")
                except ValueError as e:
                    st.error(f"Not saved: {e}")
    else:
        cid = st.selectbox("Career to delete", list(names), format_func=names.get)
        if st.button("Delete permanently", type="primary"):
            save_careers([c for c in careers if c["id"] != cid])
            st.cache_data.clear()
            st.success(f"Deleted '{names[cid]}'. A backup was kept in data/backups.")

    st.caption("Every save keeps a dated backup of the career list in data/backups.")

if st.button("Log out"):
    st.session_state.admin_ok = False
    st.rerun()
