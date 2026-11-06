"""Local SQLite storage for anonymous usage statistics and feedback.

No names, phone numbers or e-mails are stored: only the stream, the top
recommendations and whether the user found a suggestion helpful.
"""
from __future__ import annotations

import datetime as dt
import json
import pathlib
import sqlite3

DB_FILE = pathlib.Path(__file__).resolve().parents[1] / "data" / "app.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    stream TEXT NOT NULL,
    top_interests TEXT NOT NULL,
    recommended TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    career_id TEXT NOT NULL,
    helpful INTEGER NOT NULL CHECK (helpful IN (0, 1)),
    comment TEXT
);
"""


def connect(path: pathlib.Path | str = DB_FILE) -> sqlite3.Connection:
    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.executescript(SCHEMA)
    return con


def _now() -> str:
    return dt.datetime.now().isoformat(timespec="seconds")


def log_session(con, stream: str, top_interests: list[str], career_ids: list[str]) -> int:
    cur = con.execute(
        "INSERT INTO sessions (ts, stream, top_interests, recommended) VALUES (?, ?, ?, ?)",
        (_now(), stream, "".join(top_interests), json.dumps(career_ids)))
    con.commit()
    return cur.lastrowid


def add_feedback(con, career_id: str, helpful: bool, comment: str = "") -> None:
    con.execute("INSERT INTO feedback (ts, career_id, helpful, comment) VALUES (?, ?, ?, ?)",
                (_now(), career_id, 1 if helpful else 0, (comment or "").strip()[:500]))
    con.commit()


def stats(con) -> dict:
    n_sessions = con.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
    n_fb, n_help = con.execute("SELECT COUNT(*), COALESCE(SUM(helpful), 0) FROM feedback").fetchone()
    counts: dict[str, int] = {}
    for (rec,) in con.execute("SELECT recommended FROM sessions"):
        for cid in json.loads(rec):
            counts[cid] = counts.get(cid, 0) + 1
    streams = dict(con.execute("SELECT stream, COUNT(*) FROM sessions GROUP BY stream").fetchall())
    per_career = {cid: (tot, helpful) for cid, tot, helpful in con.execute(
        "SELECT career_id, COUNT(*), SUM(helpful) FROM feedback GROUP BY career_id")}
    return {"sessions": n_sessions, "feedback": n_fb, "helpful": n_help,
            "helpful_pct": round(100 * n_help / n_fb) if n_fb else None,
            "recommended_counts": counts, "streams": streams, "per_career_feedback": per_career}


def feedback_rows(con, limit: int = 200) -> list[tuple]:
    return con.execute("SELECT ts, career_id, helpful, comment FROM feedback ORDER BY id DESC LIMIT ?",
                       (limit,)).fetchall()
