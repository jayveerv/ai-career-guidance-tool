import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import get_careers, salary_text, setup, tags  # noqa: E402

import streamlit as st  # noqa: E402

from careerguide.vocab import CATEGORIES, PLATFORMS, RIASEC, SKILLS, STREAMS, SUBJECTS  # noqa: E402

setup("Career Explorer", "📚")
st.title("📚 Career Explorer")
st.write("Browse every career in the tool. Filter by field or stream, or search by keyword.")

careers = get_careers()
a, b, c = st.columns([2, 2, 3])
cat = a.selectbox("Field", ["All fields"] + CATEGORIES)
stream = b.selectbox("Open to stream", ["Any stream"] + [k for k in STREAMS if k != "ANY"],
                     format_func=lambda k: STREAMS.get(k, k))
q = c.text_input("Search", placeholder="e.g. design, bank, hacker, doctor").strip().lower()


def hit(cr):
    if cat != "All fields" and cr["category"] != cat:
        return False
    if stream != "Any stream" and stream not in cr["streams"]:
        return False
    if q:
        text = " ".join([cr["name"], cr["summary"], " ".join(cr.get("keywords", []))]).lower()
        return q in text
    return True


shown = [cr for cr in careers if hit(cr)]
st.caption(f"{len(shown)} of {len(careers)} careers")
if not shown:
    st.info("No career matches these filters. Try a different word or field.")

for cr in shown:
    with st.expander(f"**{cr['name']}** · {cr['category']}"):
        st.write(cr["summary"])
        st.markdown(f"**A typical day:** {cr.get('day', '')}")
        st.markdown("**Interest types:** " + tags(RIASEC[ch][0] for ch in cr["riasec"]), unsafe_allow_html=True)
        st.markdown("**Key subjects:** " + tags(SUBJECTS[s] for s in cr["subjects"]), unsafe_allow_html=True)
        st.markdown("**Key skills:** " + tags(SKILLS[s] for s in cr["skills"]), unsafe_allow_html=True)
        st.markdown("**Streams:** " + tags(STREAMS[s] for s in cr["streams"]), unsafe_allow_html=True)
        st.markdown(f"**Education:** {cr.get('education', '')}")
        if cr.get("exams"):
            st.markdown("**Exams:** " + tags(cr["exams"]), unsafe_allow_html=True)
        st.markdown(f"**Salary in India:** {salary_text(cr)}")
        st.markdown("**Roadmap:** " + " → ".join(cr["roadmap"]))
        if cr.get("courses"):
            st.markdown("**Free courses:** " + "; ".join(
                f"[{x['platform']}]({PLATFORMS.get(x['platform'], '#')}): *{x['topic']}*" for x in cr["courses"]))
