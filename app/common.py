"""Helpers shared by all pages."""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st  # noqa: E402

from careerguide import engine, storage  # noqa: E402

CSS = """
<style>
.block-container {padding-top: 2rem; max-width: 1100px;}
.cg-card {border: 1px solid rgba(128,128,128,.25); border-radius: 12px; padding: 1rem 1.2rem;
          margin-bottom: .8rem; background: rgba(15,118,110,.04);}
.cg-match {font-size: 1.6rem; font-weight: 700; color: #0F766E;}
.cg-tag {display: inline-block; padding: 2px 10px; margin: 2px 4px 2px 0; border-radius: 999px;
         font-size: .8rem; background: rgba(15,118,110,.12);}
.cg-muted {opacity: .75; font-size: .9rem;}
</style>
"""


def setup(title: str, icon: str = "🧭"):
    st.set_page_config(page_title=f"{title} | AI Career Guidance", page_icon=icon, layout="wide")
    st.markdown(CSS, unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def careers(_mtime: float):
    return engine.load_careers()


def get_careers():
    return careers(engine.CAREERS_FILE.stat().st_mtime)


def db():
    # A fresh connection per call: Streamlit reruns can run on different threads,
    # and SQLite connections must stay on the thread that created them.
    return storage.connect()


def tags(items):
    return " ".join(f"<span class='cg-tag'>{i}</span>" for i in items)


def salary_text(c):
    if not c.get("salary_entry") or c["salary_entry"] == "variable":
        return "Varies a lot (depends on the business)"
    return f"₹{c['salary_entry']} LPA at start · ₹{c['salary_mid']} LPA after 5-8 years (approx.)"
