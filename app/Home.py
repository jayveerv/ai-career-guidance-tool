from common import db, get_careers, setup

import streamlit as st

from careerguide import storage
from careerguide.vocab import CATEGORIES, PLATFORMS

setup("Home")

st.title("🧭 AI based Career Guidance Tool")
st.markdown("##### Find careers that fit **your** interests, subjects and skills, and the path to reach them.")

careers = get_careers()
s = storage.stats(db())
c1, c2, c3, c4 = st.columns(4)
c1.metric("Careers in the tool", len(careers))
c2.metric("Career fields", len(CATEGORIES))
c3.metric("Quiz questions", 18)
c4.metric("Students guided", s["sessions"])

st.divider()
st.subheader("How it works")
a, b, c = st.columns(3)
with a:
    st.markdown("#### 1. Tell us about you")
    st.write("Your stream, favourite subjects, skills and your dream goal.")
with b:
    st.markdown("#### 2. Take an 18-question quiz")
    st.write("It measures six interest types (RIASEC) used by career counsellors worldwide.")
with c:
    st.markdown("#### 3. Get your top 5 careers")
    st.write("With match %, the reasons, a roadmap, entrance exams, salary range and free courses.")

st.page_link("pages/1_Find_My_Career.py", label="Start now: Find my career →", icon="🚀")
st.page_link("pages/2_Career_Explorer.py", label="Or browse all careers", icon="📚")

st.divider()
st.subheader("Career fields covered")
st.write(" · ".join(CATEGORIES))
st.subheader("Free learning platforms used for course suggestions")
st.write(" · ".join(f"[{k}]({v})" for k, v in PLATFORMS.items()))
st.caption("Fair by design: the tool never asks for gender, caste, religion or family income. "
           "Your answers stay on this computer; only anonymous counts are saved for the admin dashboard.")
