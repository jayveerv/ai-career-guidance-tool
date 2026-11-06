"""AI recommendation engine.

Method: content-based filtering. Every career and the user are turned into
vectors over the same 34 features (6 interest types, 13 subjects, 15 skills).
Cosine similarity (scikit-learn) is computed block by block, combined with
weights, adjusted for the user's goal and stream, and explained by listing the
features that contributed most. No gender, caste, religion or income is used.
"""
from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass, field

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from .vocab import RIASEC, SKILLS, STREAMS, SUBJECTS

DATA = pathlib.Path(__file__).resolve().parents[1] / "data"
CAREERS_FILE = DATA / "careers.json"

R_KEYS, SUB_KEYS, SK_KEYS = list(RIASEC), list(SUBJECTS), list(SKILLS)
WEIGHTS = {"interest": 0.50, "skills": 0.30, "subjects": 0.20}
GOAL_BONUS = 0.10
STREAM_PENALTY = 0.75          # multiplier when the user's stream does not lead to the career
LETTER_WEIGHTS = (1.0, 0.7, 0.4)


def load_careers(path: pathlib.Path = CAREERS_FILE) -> list[dict]:
    careers = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    for c in careers:
        validate_career(c)
    return careers


def validate_career(c: dict) -> None:
    need = ["id", "name", "category", "streams", "riasec", "subjects", "skills", "summary", "roadmap"]
    miss = [k for k in need if not c.get(k)]
    if miss:
        raise ValueError(f"career {c.get('id', '?')} is missing {miss}")
    if any(ch not in RIASEC for ch in c["riasec"]) or not 1 <= len(c["riasec"]) <= 3:
        raise ValueError(f"career {c['id']}: riasec must be 1-3 letters from RIASEC")
    for s in c["subjects"]:
        if s not in SUBJECTS:
            raise ValueError(f"career {c['id']}: unknown subject {s}")
    for s in c["skills"]:
        if s not in SKILLS:
            raise ValueError(f"career {c['id']}: unknown skill {s}")
    for s in c["streams"]:
        if s not in STREAMS:
            raise ValueError(f"career {c['id']}: unknown stream {s}")


def career_vectors(c: dict) -> dict[str, np.ndarray]:
    interest = np.zeros(len(R_KEYS))
    for w, ch in zip(LETTER_WEIGHTS, c["riasec"]):
        interest[R_KEYS.index(ch)] = w
    subjects = np.array([1.0 if k in c["subjects"] else 0.0 for k in SUB_KEYS])
    skills = np.array([1.0 if k in c["skills"] else 0.0 for k in SK_KEYS])
    return {"interest": interest, "subjects": subjects, "skills": skills}


@dataclass
class Profile:
    interest: dict[str, float]                 # RIASEC type -> 0..1 (from the quiz)
    subjects: list[str] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)
    stream: str = "ANY"
    goal: str = ""

    def vectors(self) -> dict[str, np.ndarray]:
        return {
            "interest": np.array([float(self.interest.get(k, 0.0)) for k in R_KEYS]),
            "subjects": np.array([1.0 if k in self.subjects else 0.0 for k in SUB_KEYS]),
            "skills": np.array([1.0 if k in self.skills else 0.0 for k in SK_KEYS]),
        }


def _cos(a: np.ndarray, b: np.ndarray) -> float:
    if not a.any() or not b.any():
        return 0.0
    return float(cosine_similarity(a.reshape(1, -1), b.reshape(1, -1))[0, 0])


def goal_matches(goal: str, career: dict) -> list[str]:
    g = " " + " ".join(goal.lower().replace(",", " ").replace("/", " ").split()) + " "
    if not g.strip():
        return []
    hits = [k for k in career.get("keywords", []) if f" {k.lower()} " in g]
    if career["name"].lower() in g:
        hits.append(career["name"].lower())
    return sorted(set(hits))


def score(profile: Profile, career: dict) -> dict:
    u, v = profile.vectors(), career_vectors(career)
    parts = {k: _cos(u[k], v[k]) for k in WEIGHTS}
    base = sum(WEIGHTS[k] * parts[k] for k in WEIGHTS)
    goal_hits = goal_matches(profile.goal, career)
    total = base + (GOAL_BONUS if goal_hits else 0.0)
    eligible = profile.stream == "ANY" or profile.stream in career["streams"]
    if not eligible:
        total *= STREAM_PENALTY
    return {"career": career, "score": total, "parts": parts, "goal_hits": goal_hits,
            "eligible": eligible, "match": int(round(min(total, 0.99) * 100))}


def explain(profile: Profile, r: dict) -> list[str]:
    """Plain-language reasons for one recommendation."""
    c, reasons = r["career"], []
    strong = [ch for ch in c["riasec"] if profile.interest.get(ch, 0) >= 0.6]
    if strong:
        names = " and ".join(RIASEC[ch][0] for ch in strong[:2])
        reasons.append(f"Your quiz shows strong {names} interests, which this career needs.")
    common_sk = [SKILLS[s] for s in c["skills"] if s in profile.skills]
    if common_sk:
        reasons.append("You are good at " + ", ".join(common_sk[:3]).lower() + ".")
    common_sub = [SUBJECTS[s] for s in c["subjects"] if s in profile.subjects]
    if common_sub:
        reasons.append("You like " + ", ".join(common_sub[:3]) + ", key subjects for this path.")
    if r["goal_hits"]:
        reasons.append("It matches your goal (" + ", ".join(r["goal_hits"][:3]) + ").")
    if not r["eligible"]:
        need = ", ".join(STREAMS[s] for s in c["streams"])
        reasons.append(f"Note: usually needs {need}. Check bridge options before choosing.")
    if not reasons:
        reasons.append("A partial match to your overall profile; explore it to see if it excites you.")
    return reasons


def recommend(profile: Profile, careers: list[dict], top: int = 5, only_eligible: bool = False) -> list[dict]:
    if not careers:
        return []
    rs = [score(profile, c) for c in careers]
    if only_eligible:
        rs = [r for r in rs if r["eligible"]]
    rs.sort(key=lambda r: (-r["score"], r["career"]["name"]))
    out = rs[:top]
    for r in out:
        r["reasons"] = explain(profile, r)
    return out


def top_interests(profile: Profile, n: int = 2) -> list[str]:
    return [k for k, _ in sorted(profile.interest.items(), key=lambda kv: -kv[1])[:n]]
