import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

PRIMARY = colors.HexColor("#6c63ff")
ACCENT  = colors.HexColor("#00d4aa")
DARK    = colors.HexColor("#1a1a2e")
MUTED   = colors.HexColor("#6b6b8a")
LIGHT   = colors.HexColor("#f4f4fb")
WHITE   = colors.white
BORDER  = colors.HexColor("#ddddf0")
WARN    = colors.HexColor("#f0a500")
SEM_CLR = [colors.HexColor("#6c63ff"), colors.HexColor("#00967a"),
           colors.HexColor("#e05d44"), colors.HexColor("#3a86ff"),
           colors.HexColor("#8338ec"), colors.HexColor("#fb5607"),
           colors.HexColor("#06d6a0"), colors.HexColor("#ef476f")]


def _s(name, **kw):
    base = {"fontName": "Helvetica", "fontSize": 9, "leading": 13, "textColor": DARK}
    base.update(kw)
    return ParagraphStyle(name, **base)


def _cell(text, bold=False, color=DARK, size=8, align=TA_LEFT):
    fn = "Helvetica-Bold" if bold else "Helvetica"
    return Paragraph(str(text), ParagraphStyle("c", fontName=fn, fontSize=size,
                                                textColor=color, leading=12, alignment=align))


def _tbl(rows, col_widths, header_color=PRIMARY):
    t = Table(rows, colWidths=col_widths)
    t.setStyle(TableStyle([
        ("BACKGROUND",      (0, 0), (-1, 0),  header_color),
        ("TEXTCOLOR",       (0, 0), (-1, 0),  WHITE),
        ("FONTNAME",        (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",        (0, 0), (-1, 0),  8),
        ("ROWPADDING",      (0, 0), (-1, -1), 5),
        ("GRID",            (0, 0), (-1, -1), 0.4, BORDER),
        ("VALIGN",          (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS",  (0, 1), (-1, -1), [LIGHT, WHITE]),
    ]))
    return t


def build_educator_pdf(data: dict, req: dict) -> bytes:
    buf    = io.BytesIO()
    margin = 15 * mm
    W      = A4[0] - 2 * margin
    doc    = SimpleDocTemplate(buf, pagesize=A4,
                               leftMargin=margin, rightMargin=margin,
                               topMargin=10*mm, bottomMargin=15*mm)
    story = []

    # ── Cover ─────────────────────────────────────────────────────────────
    cover = Table([[
        Paragraph("EduSync", _s("br", fontSize=15, fontName="Helvetica-Bold", textColor=ACCENT)),
        Paragraph("Educator Curriculum Plan", _s("t", fontSize=9, textColor=MUTED, alignment=TA_CENTER)),
    ]], colWidths=[W*0.5, W*0.5])
    cover.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(-1,-1), DARK),
        ("ROWPADDING", (0,0),(-1,-1), 10),
        ("VALIGN",     (0,0),(-1,-1), "MIDDLE"),
        ("ALIGN",      (1,0),(1,0),   "RIGHT"),
    ]))
    story.append(cover)
    story.append(Spacer(1, 8))

    # Title block
    tt = Table([[Paragraph(data.get("course_title",""), _s("ct", fontSize=17, fontName="Helvetica-Bold", leading=22))]], colWidths=[W])
    tt.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),LIGHT),("ROWPADDING",(0,0),(-1,-1),12),("BOX",(0,0),(-1,-1),1,BORDER)]))
    story.append(tt)
    story.append(Spacer(1, 5))

    # Meta strip
    meta = [
        ("Level",        req.get("level","")),
        ("Semesters",    str(req.get("semesters",""))),
        ("Weekly Hours", f"{req.get('weekly_hours','')} hrs"),
        ("Industry",     req.get("industry_focus","")),
        ("Code",         data.get("course_code","—")),
    ]
    mt = Table([[_cell(f"<b>{k}:</b> {v}", size=8) for k,v in meta]], colWidths=[W/5]*5)
    mt.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#eeeeff")),
                             ("ROWPADDING",(0,0),(-1,-1),6),("GRID",(0,0),(-1,-1),0.5,BORDER),
                             ("ALIGN",(0,0),(-1,-1),"CENTER")]))
    story.append(mt)
    story.append(Spacer(1,5))
    story.append(Paragraph(data.get("description",""), _s("desc", textColor=MUTED, spaceAfter=4)))
    if data.get("industry_relevance"):
        story.append(Paragraph(f"🏭  {data['industry_relevance']}", _s("ir", textColor=ACCENT, fontName="Helvetica-Bold", spaceAfter=4)))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=4))

    # Prerequisites
    prereqs = data.get("prerequisites",[])
    if prereqs:
        story.append(Paragraph("Prerequisites", _s("h3", fontSize=10, fontName="Helvetica-Bold", textColor=ACCENT, spaceBefore=6, spaceAfter=4)))
        for p in prereqs:
            story.append(Paragraph(f"•  {p}", _s("bl", leftIndent=10, textColor=DARK, spaceAfter=1)))
        story.append(Spacer(1,4))

    # ── Learning Outcomes ──────────────────────────────────────────────────
    story.append(Paragraph("🎯  Learning Outcomes", _s("h2", fontSize=13, fontName="Helvetica-Bold", textColor=PRIMARY, spaceBefore=10, spaceAfter=5)))
    lo_rows = [[_cell(h, bold=True, color=WHITE) for h in ["ID","Outcome","Bloom's Level"]]]
    for lo in data.get("learning_outcomes",[]):
        lo_rows.append([_cell(lo.get("id",""),bold=True,color=PRIMARY), _cell(lo.get("outcome","")), _cell(lo.get("bloom_level",""),color=ACCENT)])
    story.append(_tbl(lo_rows, [W*0.1, W*0.7, W*0.2]))
    story.append(Spacer(1,8))

    # ── Semester Plans ─────────────────────────────────────────────────────
    for sem in data.get("semesters",[]):
        story.append(PageBreak())
        si     = sem.get("semester",1) - 1
        clr    = SEM_CLR[si % len(SEM_CLR)]

        # Semester header
        sh = Table([[
            Paragraph(f"Semester {sem['semester']}", _s("sn", fontSize=14, fontName="Helvetica-Bold", textColor=WHITE)),
            Paragraph(sem.get("title",""), _s("st", fontSize=11, fontName="Helvetica-Bold", textColor=WHITE)),
        ]], colWidths=[W*0.25, W*0.75])
        sh.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),clr),("ROWPADDING",(0,0),(-1,-1),10),("VALIGN",(0,0),(-1,-1),"MIDDLE")]))
        story.append(sh)
        story.append(Spacer(1,5))

        # Semester focus + LOs
        story.append(Paragraph(f"Focus: {sem.get('focus','')}", _s("sf", textColor=MUTED, spaceAfter=3)))
        lo_tags = "  ".join(sem.get("learning_outcomes",[]))
        story.append(Paragraph(f"Outcomes: {lo_tags}", _s("slo", textColor=PRIMARY, fontName="Helvetica-Bold", spaceAfter=6)))

        # Weekly plan table
        story.append(Paragraph("Weekly Study Plan", _s("wph", fontSize=10, fontName="Helvetica-Bold", textColor=clr, spaceAfter=4)))
        wp_rows = [[_cell(h, bold=True, color=WHITE) for h in ["Wk","Topic","Subtopics","Method","Hrs","Assessment"]]]
        for w in sem.get("weekly_plan",[]):
            subs = ", ".join(w.get("subtopics",[]))
            asmnt = w.get("assessment","None")
            wp_rows.append([
                _cell(str(w.get("week","")), bold=True, color=clr),
                _cell(w.get("topic",""), bold=True),
                _cell(subs),
                _cell(w.get("teaching_method",""), color=ACCENT),
                _cell(str(w.get("hours",""))+"h", align=TA_CENTER),
                _cell("—" if asmnt=="None" else asmnt, color=WARN if asmnt!="None" else MUTED),
            ])
        wp_tbl = Table(wp_rows, colWidths=[W*0.07, W*0.22, W*0.36, W*0.13, W*0.07, W*0.15])
        wp_tbl.setStyle(TableStyle([
            ("BACKGROUND",     (0,0),(-1,0),   clr),
            ("TEXTCOLOR",      (0,0),(-1,0),   WHITE),
            ("FONTNAME",       (0,0),(-1,0),   "Helvetica-Bold"),
            ("FONTSIZE",       (0,0),(-1,-1),  7),
            ("ROWPADDING",     (0,0),(-1,-1),  4),
            ("GRID",           (0,0),(-1,-1),  0.4, BORDER),
            ("VALIGN",         (0,0),(-1,-1),  "TOP"),
            ("ROWBACKGROUNDS", (0,1),(-1,-1),  [LIGHT, WHITE]),
        ]))
        story.append(wp_tbl)
        story.append(Spacer(1,8))

        # Semester assessments
        ass = sem.get("semester_assessments",{})

        def _mini_tbl(items, headers, mapper, hclr):
            if not items: return None
            rows = [[_cell(h,bold=True,color=WHITE) for h in headers]]
            for item in items:
                rows.append(mapper(item))
            return _tbl(rows, [W/len(headers)]*len(headers), hclr)

        story.append(Paragraph("Assessments", _s("ah", fontSize=10, fontName="Helvetica-Bold", textColor=clr, spaceAfter=4)))

        asgn = _mini_tbl(ass.get("assignments",[]),
            ["Assignment","Due Week","Marks"],
            lambda a:[_cell(a.get("title",""),bold=True),_cell(f"Week {a.get('week_due','')}"),_cell(f"{a.get('marks','')}m",color=WARN,bold=True)],
            DARK)
        if asgn: story.append(KeepTogether([Paragraph("Assignments", _s("mh", fontSize=8, fontName="Helvetica-Bold", textColor=MUTED, spaceAfter=2)), asgn, Spacer(1,4)]))

        qz = _mini_tbl(ass.get("quizzes",[]),
            ["Quiz","Week","Marks"],
            lambda q:[_cell(q.get("title",""),bold=True),_cell(f"Week {q.get('week','')}"),_cell(f"{q.get('marks','')}m",color=WARN,bold=True)],
            colors.HexColor("#574fd6"))
        if qz: story.append(KeepTogether([Paragraph("Quizzes", _s("mh", fontSize=8, fontName="Helvetica-Bold", textColor=MUTED, spaceAfter=2)), qz, Spacer(1,4)]))

        pr = _mini_tbl(ass.get("projects",[]),
            ["Project","Type","Marks"],
            lambda p:[_cell(p.get("title",""),bold=True),_cell(p.get("type",""),color=ACCENT),_cell(f"{p.get('marks','')}m",color=WARN,bold=True)],
            ACCENT)
        if pr: story.append(KeepTogether([Paragraph("Projects", _s("mh", fontSize=8, fontName="Helvetica-Bold", textColor=MUTED, spaceAfter=2)), pr, Spacer(1,4)]))

        lb = _mini_tbl(ass.get("lab_exercises",[]),
            ["Lab Exercise","Week","Tools"],
            lambda l:[_cell(l.get("title",""),bold=True),_cell(f"Week {l.get('week','')}"),_cell(", ".join(l.get("tools",[])))],
            colors.HexColor("#00967a"))
        if lb: story.append(KeepTogether([Paragraph("Lab Exercises", _s("mh", fontSize=8, fontName="Helvetica-Bold", textColor=MUTED, spaceAfter=2)), lb, Spacer(1,4)]))

        # Mark distribution
        md = sem.get("mark_distribution",{})
        if md:
            story.append(Spacer(1,4))
            story.append(Paragraph("Mark Distribution", _s("mdh", fontSize=9, fontName="Helvetica-Bold", textColor=clr, spaceAfter=3)))
            md_rows = [[_cell(k.replace("_"," ").title(), bold=True), _cell(f"{v} marks", color=PRIMARY, bold=True)] for k,v in md.items()]
            total   = sum(md.values())
            md_rows.append([_cell("TOTAL",bold=True,color=WHITE), _cell(f"{total} marks",bold=True,color=WHITE)])
            md_tbl  = Table(md_rows, colWidths=[W*0.4, W*0.6])
            md_tbl.setStyle(TableStyle([
                ("ROWBACKGROUNDS",(0,0),(-1,-2),[LIGHT,WHITE]),
                ("BACKGROUND",   (0,-1),(-1,-1),clr),
                ("GRID",         (0,0),(-1,-1),0.4,BORDER),
                ("ROWPADDING",   (0,0),(-1,-1),5),
            ]))
            story.append(md_tbl)

    # ── Outcome–Topic Mapping ──────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("🗺  Outcome — Topic Mapping", _s("h2", fontSize=13, fontName="Helvetica-Bold", textColor=PRIMARY, spaceAfter=5)))
    om_rows = [[_cell(h,bold=True,color=WHITE) for h in ["LO","Outcome","Bloom's","Semesters","Topics","Assessments"]]]
    for m in data.get("outcome_topic_mapping",[]):
        sems = ", ".join(f"S{s}" for s in m.get("mapped_semesters",[]))
        om_rows.append([
            _cell(m.get("outcome_id",""),bold=True,color=PRIMARY),
            _cell(m.get("outcome_text","")),
            _cell(m.get("bloom_level",""),color=ACCENT),
            _cell(sems, color=PRIMARY),
            _cell(", ".join(m.get("mapped_topics",[]))),
            _cell(", ".join(m.get("assessment_types",[])),color=WARN),
        ])
    story.append(_tbl(om_rows, [W*0.07, W*0.3, W*0.12, W*0.1, W*0.25, W*0.16]))
    story.append(Spacer(1,8))

    # ── Industry Projects ──────────────────────────────────────────────────
    industry_projects = data.get("industry_projects",[])
    if industry_projects:
        story.append(HRFlowable(width="100%",thickness=1,color=BORDER,spaceAfter=4))
        story.append(Paragraph("🏭  Industry Projects", _s("h2", fontSize=13, fontName="Helvetica-Bold", textColor=PRIMARY, spaceAfter=5)))
        ip_rows = [[_cell(h,bold=True,color=WHITE) for h in ["Title","Semester","Description","Skills Covered"]]]
        for p in industry_projects:
            ip_rows.append([
                _cell(p.get("title",""),bold=True),
                _cell(f"Semester {p.get('semester','')}", color=PRIMARY),
                _cell(p.get("description","")),
                _cell(", ".join(p.get("skills_covered",[])),color=ACCENT),
            ])
        story.append(_tbl(ip_rows, [W*0.22, W*0.1, W*0.38, W*0.3]))
        story.append(Spacer(1,8))

    # ── Resources ─────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%",thickness=1,color=BORDER,spaceAfter=4))
    story.append(Paragraph("🔗  Learning Resources", _s("h2", fontSize=13, fontName="Helvetica-Bold", textColor=PRIMARY, spaceAfter=5)))
    res_rows = [[_cell(h,bold=True,color=WHITE) for h in ["Title","Type","Platform","Free?","URL"]]]
    for r in data.get("resources",[]):
        url   = r.get("url","")
        short = (url[:55]+"…") if len(url)>55 else url
        res_rows.append([
            _cell(r.get("title",""),bold=True),
            _cell(r.get("type",""),color=PRIMARY),
            _cell(r.get("platform",""),color=MUTED),
            _cell("✓ Free" if r.get("free") else "Paid", color=ACCENT if r.get("free") else WARN),
            Paragraph(f'<link href="{url}">{short}</link>', _s("rl", textColor=PRIMARY, fontSize=7, leading=11)),
        ])
    story.append(_tbl(res_rows, [W*0.24, W*0.1, W*0.13, W*0.08, W*0.45]))
    story.append(Spacer(1,6))

    tools = data.get("recommended_tools",[])
    if tools:
        story.append(Paragraph("🛠  Recommended Tools:  " + "   ·   ".join(tools),
                                _s("tools", textColor=ACCENT, fontName="Helvetica-Bold", spaceAfter=4)))

    # Footer
    story.append(HRFlowable(width="100%",thickness=1,color=BORDER,spaceAfter=4))
    story.append(Paragraph(
        f"Generated by EduSync (Educator Mode)  ·  {datetime.now().strftime('%B %d, %Y  %H:%M')}",
        _s("ft", fontSize=8, textColor=MUTED, alignment=TA_CENTER)
    ))

    doc.build(story)
    return buf.getvalue()
