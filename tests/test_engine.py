import pytest

from careerguide import engine, storage
from careerguide.quiz import QUESTIONS, riasec_scores
from careerguide.report import build_pdf

CAREERS = engine.load_careers()


def prof(answers, **kw):
    return engine.Profile(interest=riasec_scores(answers), **kw)


TECH = [2, 2, 3, 5, 5, 4, 2, 3, 2, 3, 2, 3, 2, 2, 3, 4, 4, 4]
CARE = [1, 1, 1, 3, 3, 3, 2, 2, 2, 5, 5, 5, 2, 2, 2, 3, 3, 3]
ART = [1, 1, 1, 2, 2, 2, 5, 5, 5, 2, 2, 2, 4, 4, 4, 1, 1, 1]


def test_dataset_is_valid_and_complete():
    assert len(CAREERS) == 40
    assert len({c["id"] for c in CAREERS}) == 40
    assert len({c["category"] for c in CAREERS}) == 7


def test_quiz_scoring_range_and_errors():
    s = riasec_scores([5] * len(QUESTIONS))
    assert all(v == 1.0 for v in s.values())
    assert all(v == 0.0 for v in riasec_scores([1] * 18).values())
    with pytest.raises(ValueError):
        riasec_scores([3] * 5)
    with pytest.raises(ValueError):
        riasec_scores([6] * 18)


def test_tech_profile_gets_tech_careers():
    r = engine.recommend(prof(TECH, subjects=["computers", "maths"], skills=["coding", "logic"], stream="PCM"), CAREERS)
    assert all(x["career"]["category"] == "Engineering and Technology" for x in r[:3])


def test_goal_keyword_moves_career_to_top():
    p = prof(TECH, subjects=["computers"], skills=["coding"], stream="PCM", goal="I want to be an ethical hacker")
    assert engine.recommend(p, CAREERS)[0]["career"]["id"] == "cyber_security_analyst"


def test_care_profile_gets_medical_careers():
    r = engine.recommend(prof(CARE, subjects=["biology", "chemistry"], skills=["empathy", "detail"], stream="PCB"), CAREERS)
    assert r[0]["career"]["category"] == "Medical and Health"


def test_art_profile_gets_creative_careers():
    r = engine.recommend(prof(ART, subjects=["art_design"], skills=["creativity", "visual"], stream="ARTS"), CAREERS)
    assert r[0]["career"]["category"] == "Arts, Design and Media"


def test_stream_filter_and_penalty():
    p = prof(CARE, subjects=["biology"], skills=["empathy"], stream="COM")
    only = engine.recommend(p, CAREERS, top=40, only_eligible=True)
    assert all("COM" in x["career"]["streams"] for x in only)
    doc = next(x for x in engine.recommend(p, CAREERS, top=40) if x["career"]["id"] == "doctor")
    assert not doc["eligible"] and any("usually needs" in r for r in doc["reasons"])


def test_every_result_has_reasons_and_match_in_range():
    for x in engine.recommend(prof([3] * 18), CAREERS, top=40):
        assert x["reasons"] and 0 <= x["match"] <= 99


def test_deterministic():
    p = prof(TECH, subjects=["maths"], skills=["logic"], stream="PCM")
    a = [x["career"]["id"] for x in engine.recommend(p, CAREERS)]
    assert a == [x["career"]["id"] for x in engine.recommend(p, CAREERS)]


def test_validation_rejects_bad_career():
    bad = dict(CAREERS[0], riasec="XYZ")
    with pytest.raises(ValueError):
        engine.validate_career(bad)


def test_no_sensitive_attributes_in_profile():
    fields = set(engine.Profile.__dataclass_fields__)
    assert not fields & {"gender", "caste", "religion", "income"}


def test_storage_roundtrip(tmp_path):
    con = storage.connect(tmp_path / "t.db")
    storage.log_session(con, "PCM", ["I", "C"], ["software_developer", "data_scientist"])
    storage.add_feedback(con, "software_developer", True)
    storage.add_feedback(con, "data_scientist", False, "not for me")
    s = storage.stats(con)
    assert s["sessions"] == 1 and s["feedback"] == 2 and s["helpful_pct"] == 50
    assert s["recommended_counts"]["software_developer"] == 1


def test_pdf_report_builds():
    p = prof(TECH, subjects=["computers"], skills=["coding"], stream="PCM", goal="hacker")
    pdf = build_pdf(p, engine.recommend(p, CAREERS), "Test Student")
    assert pdf[:4] == b"%PDF" and len(pdf) > 3000
