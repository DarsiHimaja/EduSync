import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER

# ── Colour palette ─────────────────────────────────────────────────────────
PRIMARY = colors.HexColor("#6c63ff")
ACCENT  = colors.HexColor("#00d4aa")
DARK    = colors.HexColor("#1a1a2e")
MUTED   = colors.HexColor("#9090b0")
WHITE   = colors.white
LIGHT   = colors.HexColor("#f4f4fb")
BORDER  = colors.HexColor("#ddddf0")


def _styles():
    base = getSampleStyleSheet()
    def s(name, **kw):
        return ParagraphStyle(name, parent=base["Normal"], **kw)

    return {
        "title":    s("T",  fontSize=22, textColor=WHITE,   fontName="Helvetica-Bold",  spaceAfter=4,  alignment=TA_LEFT),
        "subtitle": s("ST", fontSize=11, textColor=ACCENT,  fontName="Helvetica",        spaceAfter=2),
        "meta":     s("M",  fontSize=9,  textColor=MUTED,   fontName="Helvetica",        spaceAfter=2),
        "h2":       s("H2", fontSize=13, textColor=PRIMARY, fontName="Helvetica-Bold",   spaceBefore=14, spaceAfter=5),
        "h3":       s("H3", fontSize=10, textColor=ACCENT,  fontName="Helvetica-Bold",   spaceBefore=8,  spaceAfter=3),
        "body":     s("B",  fontSize=9,  textColor=colors.HexColor("#333344"), fontName="Helvetica", leading=14, spaceAfter=2),
        "bullet":   s("BL", fontSize=9,  textColor=colors.HexColor("#333344"), fontName="Helvetica", leading=14, leftIndent=12, bulletIndent=0, spaceAfter=1),
        "link":     s("LK", fontSize=8,  textColor=PRIMARY, fontName="Helvetica", leading=12, spaceAfter=1),
        "footer":   s("F",  fontSize=8,  textColor=MUTED,   fontName="Helvetica", alignment=TA_CENTER),
    }


def build_curriculum_pdf(data: dict, req: dict) -> bytes:
    buf    = io.BytesIO()
    margin = 18 * mm
    doc    = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=margin, rightMargin=margin,
        topMargin=10 * mm, bottomMargin=18 * mm
    )

    st    = _styles()
    story = []
    W     = A4[0] - 2 * margin   # usable width

    # ── Header banner ──────────────────────────────────────────────────────
    header_data = [[
        Paragraph("EduSync", ParagraphStyle("brand", fontSize=14, textColor=ACCENT, fontName="Helvetica-Bold")),
        Paragraph("AI-Generated Curriculum", ParagraphStyle("tag", fontSize=9, textColor=MUTED, fontName="Helvetica", alignment=1)),
    ]]
    header_tbl = Table(header_data, colWidths=[W * 0.5, W * 0.5])
    header_tbl.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, -1), DARK),
        ("ROWPADDING",  (0, 0), (-1, -1), 10),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN",       (1, 0), (1, 0),   "RIGHT"),
        ("ROUNDEDCORNERS", [6]),
    ]))
    story.append(header_tbl)
    story.append(Spacer(1, 8))

    # ── Course title block ─────────────────────────────────────────────────
    title_data = [[Paragraph(data.get("course_title", ""), ParagraphStyle(
        "ct", fontSize=18, textColor=DARK, fontName="Helvetica-Bold", leading=22
    ))]]
    title_tbl = Table(title_data, colWidths=[W])
    title_tbl.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, -1), LIGHT),
        ("ROWPADDING",  (0, 0), (-1, -1), 12),
        ("ROUNDEDCORNERS", [8]),
        ("BOX",         (0, 0), (-1, -1), 1, BORDER),
    ]))
    story.append(title_tbl)
    story.append(Spacer(1, 6))

    # Meta pills row
    meta = [
        ("Level",     req.get("level", "")),
        ("Duration",  f"{req.get('duration','')} weeks"),
        ("Topics",    str(sum(len(c["topics"]) for c in data.get("all_topics", [])))),
        ("Resources", str(len(data.get("resources", [])))),
    ]
    meta_cells = [[Paragraph(f"<b>{k}:</b> {v}", ParagraphStyle(
        "mp", fontSize=8, textColor=DARK, fontName="Helvetica", leading=12
    )) for k, v in meta]]
    meta_tbl = Table(meta_cells, colWidths=[W / 4] * 4)
    meta_tbl.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, -1), colors.HexColor("#ebebff")),
        ("ROWPADDING",  (0, 0), (-1, -1), 6),
        ("ALIGN",       (0, 0), (-1, -1), "CENTER"),
        ("ROUNDEDCORNERS", [6]),
        ("GRID",        (0, 0), (-1, -1), 0.5, BORDER),
    ]))
    story.append(meta_tbl)
    story.append(Spacer(1, 6))

    # Description
    story.append(Paragraph(data.get("description", ""), st["body"]))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=6))

    # ── Learning Outcomes ──────────────────────────────────────────────────
    story.append(Paragraph("🎯  Learning Outcomes", st["h2"]))
    for o in data.get("learning_outcomes", []):
        story.append(Paragraph(f"✓  {o}", st["bullet"]))
    story.append(Spacer(1, 6))

    # ── All Topics ─────────────────────────────────────────────────────────
    if data.get("all_topics"):
        story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=4))
        story.append(Paragraph("📚  All Topics", st["h2"]))
        for cat in data["all_topics"]:
            story.append(Paragraph(cat["category"], st["h3"]))
            rows = []
            for t in cat["topics"]:
                rows.append([
                    Paragraph(f"<b>{t['name']}</b>", ParagraphStyle("tn", fontSize=8, fontName="Helvetica-Bold", textColor=DARK, leading=12)),
                    Paragraph(t.get("description", ""), ParagraphStyle("td", fontSize=8, fontName="Helvetica", textColor=MUTED, leading=12)),
                ])
            tbl = Table(rows, colWidths=[W * 0.32, W * 0.68])
            tbl.setStyle(TableStyle([
                ("BACKGROUND",  (0, 0), (-1, -1), LIGHT),
                ("BACKGROUND",  (0, 0), (0, -1),  colors.HexColor("#eeeeff")),
                ("ROWPADDING",  (0, 0), (-1, -1), 5),
                ("GRID",        (0, 0), (-1, -1), 0.4, BORDER),
                ("VALIGN",      (0, 0), (-1, -1), "TOP"),
            ]))
            story.append(tbl)
            story.append(Spacer(1, 4))

    # ── Weekly Study Plan ──────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=4))
    story.append(Paragraph("🗓  Weekly Study Plan", st["h2"]))
    for w in data.get("weekly_plan", []):
        week_rows = [
            [
                Paragraph(f"<b>Week {w['week']}</b>", ParagraphStyle("wn", fontSize=9, fontName="Helvetica-Bold", textColor=WHITE, leading=13)),
                Paragraph(w["title"], ParagraphStyle("wt", fontSize=9, fontName="Helvetica-Bold", textColor=WHITE, leading=13)),
            ],
            [
                Paragraph("<b>Topics</b>", ParagraphStyle("wlh", fontSize=8, fontName="Helvetica-Bold", textColor=PRIMARY, leading=12)),
                Paragraph(",  ".join(w.get("topics", [])), ParagraphStyle("wl", fontSize=8, fontName="Helvetica", textColor=DARK, leading=12)),
            ],
            [
                Paragraph("<b>Activities</b>", ParagraphStyle("wah", fontSize=8, fontName="Helvetica-Bold", textColor=ACCENT, leading=12)),
                Paragraph(",  ".join(w.get("activities", [])), ParagraphStyle("wa", fontSize=8, fontName="Helvetica", textColor=DARK, leading=12)),
            ],
        ]
        week_tbl = Table(week_rows, colWidths=[W * 0.2, W * 0.8])
        week_tbl.setStyle(TableStyle([
            ("BACKGROUND",  (0, 0), (-1, 0), PRIMARY),
            ("BACKGROUND",  (0, 1), (-1, 1), LIGHT),
            ("BACKGROUND",  (0, 2), (-1, 2), colors.HexColor("#f0fff8")),
            ("ROWPADDING",  (0, 0), (-1, -1), 6),
            ("GRID",        (0, 0), (-1, -1), 0.4, BORDER),
            ("VALIGN",      (0, 0), (-1, -1), "TOP"),
            ("SPAN",        (0, 0), (0, 0)),
        ]))
        story.append(KeepTogether([week_tbl, Spacer(1, 5)]))

    # ── Resources ─────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=4))
    story.append(Paragraph("🔗  Resources", st["h2"]))
    res_rows = [[
        Paragraph("<b>Title</b>", ParagraphStyle("rh", fontSize=8, fontName="Helvetica-Bold", textColor=WHITE)),
        Paragraph("<b>Type</b>",  ParagraphStyle("rh", fontSize=8, fontName="Helvetica-Bold", textColor=WHITE)),
        Paragraph("<b>Platform</b>", ParagraphStyle("rh", fontSize=8, fontName="Helvetica-Bold", textColor=WHITE)),
        Paragraph("<b>Free?</b>", ParagraphStyle("rh", fontSize=8, fontName="Helvetica-Bold", textColor=WHITE)),
        Paragraph("<b>URL</b>",   ParagraphStyle("rh", fontSize=8, fontName="Helvetica-Bold", textColor=WHITE)),
    ]]
    for r in data.get("resources", []):
        res_rows.append([
            Paragraph(r.get("title", ""),    ParagraphStyle("rb", fontSize=7, fontName="Helvetica-Bold", textColor=DARK,    leading=11)),
            Paragraph(r.get("type", ""),     ParagraphStyle("rb", fontSize=7, fontName="Helvetica",      textColor=PRIMARY,  leading=11)),
            Paragraph(r.get("platform", ""), ParagraphStyle("rb", fontSize=7, fontName="Helvetica",      textColor=MUTED,    leading=11)),
            Paragraph("✓ Free" if r.get("free") else "Paid", ParagraphStyle("rb", fontSize=7, fontName="Helvetica", textColor=ACCENT if r.get("free") else colors.HexColor("#f0a500"), leading=11)),
            Paragraph(f'<link href="{r.get("url","")}">{r.get("url","")[:55]}…</link>' if len(r.get("url","")) > 55 else f'<link href="{r.get("url","")}">{r.get("url","")}</link>',
                      ParagraphStyle("rl", fontSize=7, fontName="Helvetica", textColor=PRIMARY, leading=11)),
        ])
    res_tbl = Table(res_rows, colWidths=[W*0.24, W*0.09, W*0.13, W*0.08, W*0.46])
    res_tbl.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0),  PRIMARY),
        ("BACKGROUND",   (0, 1), (-1, -1), LIGHT),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT, WHITE]),
        ("ROWPADDING",   (0, 0), (-1, -1), 5),
        ("GRID",         (0, 0), (-1, -1), 0.4, BORDER),
        ("VALIGN",       (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(res_tbl)
    story.append(Spacer(1, 8))

    # ── Assessment Ideas ───────────────────────────────────────────────────
    if data.get("assessment_ideas"):
        story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=4))
        story.append(Paragraph("📝  Assessment Ideas", st["h2"]))
        for i, a in enumerate(data["assessment_ideas"], 1):
            story.append(Paragraph(f"{i}.  {a}", st["bullet"]))
        story.append(Spacer(1, 6))

    # ── Footer ─────────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=4))
    from datetime import datetime
    story.append(Paragraph(
        f"Generated by EduSync  ·  {datetime.now().strftime('%B %d, %Y  %H:%M')}",
        st["footer"]
    ))

    doc.build(story)
    return buf.getvalue()
