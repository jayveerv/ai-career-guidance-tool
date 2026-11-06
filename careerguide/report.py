"""PDF career report (ReportLab)."""
from __future__ import annotations

import datetime as dt
import io

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

from .vocab import PLATFORMS, RIASEC, SKILLS, STREAMS, SUBJECTS

INK = colors.HexColor("#1B2A4A")
ACCENT = colors.HexColor("#0F766E")
MUTED = colors.HexColor("#5B6475")
LIGHT = colors.HexColor("#EEF2F7")


def _styles():
    ss = getSampleStyleSheet()
    return {
        "h1": ParagraphStyle("h1", parent=ss["Title"], fontName="Helvetica-Bold", fontSize=20,
                             textColor=INK, alignment=TA_LEFT, spaceAfter=2),
        "sub": ParagraphStyle("sub", parent=ss["Normal"], fontSize=9.5, textColor=MUTED, spaceAfter=10),
        "h2": ParagraphStyle("h2", parent=ss["Heading2"], fontName="Helvetica-Bold", fontSize=13,
                             textColor=INK, spaceBefore=10, spaceAfter=4),
        "h3": ParagraphStyle("h3", parent=ss["Heading3"], fontName="Helvetica-Bold", fontSize=11.5,
                             textColor=ACCENT, spaceBefore=6, spaceAfter=2),
        "body": ParagraphStyle("body", parent=ss["Normal"], fontSize=9.5, leading=13),
        "small": ParagraphStyle("small", parent=ss["Normal"], fontSize=8, leading=10.5, textColor=MUTED),
    }


def _bar(value: float, width: int = 30) -> str:
    n = int(round(value * width))
    return "<font color='#0F766E'>" + "|" * n + "</font><font color='#C9D1DC'>" + "|" * (width - n) + "</font>"


def build_pdf(profile, results, name: str = "") -> bytes:
    """profile: engine.Profile; results: list from engine.recommend."""
    st, buf = _styles(), io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                            topMargin=16 * mm, bottomMargin=16 * mm,
                            title="AI Career Guidance Report", author="AI Career Guidance Tool")
    E = []
    who = f" for {name}" if name.strip() else ""
    E.append(Paragraph(f"Career Guidance Report{who}", st["h1"]))
    E.append(Paragraph(f"AI based Career Guidance Tool &middot; {dt.date.today():%d %B %Y}", st["sub"]))

    E.append(Paragraph("1. Your profile", st["h2"]))
    rows = [["Stream", STREAMS.get(profile.stream, profile.stream)],
            ["Favourite subjects", ", ".join(SUBJECTS[s] for s in profile.subjects) or "-"],
            ["Strong skills", ", ".join(SKILLS[s] for s in profile.skills) or "-"],
            ["Goal / dream", profile.goal or "-"]]
    t = Table([[Paragraph(f"<b>{a}</b>", st["body"]), Paragraph(b, st["body"])] for a, b in rows],
              colWidths=[38 * mm, 136 * mm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, -1), LIGHT), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D5DCE6")),
                           ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    E.append(t)

    E.append(Paragraph("2. Your interest profile (RIASEC)", st["h2"]))
    irows = [[Paragraph(f"<b>{RIASEC[k][0]}</b>", st["body"]),
              Paragraph(_bar(profile.interest.get(k, 0)), st["body"]),
              Paragraph(f"{round(profile.interest.get(k, 0) * 100)}%", st["body"]),
              Paragraph(RIASEC[k][1], st["small"])] for k in RIASEC]
    it = Table(irows, colWidths=[28 * mm, 52 * mm, 14 * mm, 80 * mm])
    it.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                            ("LINEBELOW", (0, 0), (-1, -2), 0.3, colors.HexColor("#E3E8EF"))]))
    E.append(it)

    E.append(Paragraph("3. Your top career matches", st["h2"]))
    for i, r in enumerate(results, 1):
        c = r["career"]
        block = [Paragraph(f"{i}. {c['name']} &nbsp;<font color='#5B6475' size='9'>"
                           f"{r['match']}% match &middot; {c['category']}</font>", st["h3"]),
                 Paragraph(c["summary"], st["body"]),
                 Paragraph("<b>Why it fits you:</b> " + " ".join(r["reasons"]), st["body"]),
                 Paragraph(f"<b>A typical day:</b> {c.get('day', '')}", st["body"]),
                 Paragraph(f"<b>Education:</b> {c.get('education', '')}"
                           + (f" &middot; <b>Exams:</b> {', '.join(c.get('exams', []))}" if c.get('exams') else ""),
                           st["body"])]
        if c.get("salary_entry") and c["salary_entry"] != "variable":
            block.append(Paragraph(f"<b>Approx. salary in India:</b> {c['salary_entry']} LPA at start, "
                                   f"{c['salary_mid']} LPA after 5-8 years", st["body"]))
        block.append(Paragraph("<b>Roadmap:</b> " + " &rarr; ".join(
            f"({n}) {s}" for n, s in enumerate(c["roadmap"], 1)), st["body"]))
        if c.get("courses"):
            block.append(Paragraph("<b>Free courses:</b> " + "; ".join(
                f"{x['platform']}: search '{x['topic']}'" for x in c["courses"]), st["body"]))
        block.append(Spacer(1, 4))
        E.append(KeepTogether(block))

    E.append(Paragraph("4. Free learning platforms", st["h2"]))
    E.append(Paragraph(" &middot; ".join(f"{k}: {v}" for k, v in PLATFORMS.items()), st["body"]))
    E.append(Spacer(1, 8))
    E.append(Paragraph("This report is guidance, not a final decision. Talk to teachers, parents and people "
                       "working in these careers. Salaries are rough Indian ranges in lakh per annum and vary "
                       "by city, employer and year. The tool does not use gender, caste, religion or income.",
                       st["small"]))
    doc.build(E)
    return buf.getvalue()
