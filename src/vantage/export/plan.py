"""Baseline plans, derived deterministically from the v3 IR.

The export agents author the *good* plan — they read the dossier and make editorial judgements a
rule cannot. This module produces the plan you get without them: a defensible, complete mapping
of dossier → collateral. It has two jobs:

1. **Fallback.** ``vantage export`` must produce every collateral with no model in the loop, so the
   CLI works headless and the renderers stay testable.
2. **Scaffold.** The agents receive this plan as their starting point, so they spend attention on
   narrative and emphasis rather than restating structure.

Every plan validates against the same pydantic models the agents must emit. Nothing here adds a
fact: every string is lifted from the dossier (and trimmed for display only), and a composite the
dossier marks ``SUPPRESSED`` is never turned into a number.
"""

from __future__ import annotations

import re

from .dossier import SECTION_ICON, SECTION_TAKEAWAY, first_callout, vertical_words
from .models import (
    KPI,
    Callout,
    ChartSpec,
    DeckPlan,
    DocPlan,
    DocSectionPlan,
    DocTreatment,
    Dossier,
    ListBlock,
    Paragraph,
    Section,
    SitePage,
    SitePlan,
    Slide,
    SlideLayout,
    Table,
    TimelineStep,
)
from .parse import claim_refs
from .richtext import plain, truncate
from .theme import SCORE_DISCLAIMER

DEPTHS = ("exec", "standard", "full")

#: How the body groups for the standard deck and for the microsite.
GROUPS: list[tuple[str, str, list[str], str]] = [
    ("brief", "Executive summary", ["1"], "file-text"),
    ("company", "Company and market", ["3", "4", "5"], "building-2"),
    ("financials", "Financial performance", ["6"], "chart-line"),
    ("operations", "Operations and technology", ["7", "8", "15", "16"], "cpu"),
    ("strategy", "Strategy, leadership and competition", ["9", "10", "11", "12", "13"], "target"),
    ("risk", "Risk and ESG", ["14", "17"], "shield-alert"),
    ("pursuit", "Opportunity and pursuit", ["18", "19", "20"], "lightbulb"),
    ("method", "Run contract and method", ["0", "2"], "microscope"),
]

APPENDICES_BY_DEPTH = {
    "exec": ["21.11"],
    "standard": ["21.1", "21.8", "21.11"],
    "full": [],   # full carries §21 whole, through the body plan
}

SUPPRESSED_RE = re.compile(r"\bSUPPRESSED\b|\bsuppressed\b")


# ── table helpers ────────────────────────────────────────────────────────────


def tables(section: Section | None, deep: bool = False) -> list[Table]:
    if section is None:
        return []
    nodes = list(section.walk()) if deep else [section]
    return [b for node in nodes for b in node.blocks if isinstance(b, Table)]


def first_table(section: Section | None, min_rows: int = 1, deep: bool = False) -> Table | None:
    for table in tables(section, deep):
        if len(table.rows) >= min_rows:
            return table
    return None


def column(table: Table, *names: str) -> int | None:
    lowered = [plain(h).lower().strip() for h in table.header]
    for name in names:
        for index, head in enumerate(lowered):
            if name in head:
                return index
    return None


def cell(row: list[str], index: int | None) -> str:
    return row[index] if index is not None and index < len(row) else ""


def lead_paragraph(section: Section | None, limit: int = 320) -> str:
    if section is None:
        return ""
    for block in section.blocks:
        if isinstance(block, Paragraph) and len(plain(block.text)) > 60:
            return truncate(block.text.split("\n\n")[0], limit)
    return ""


def verdict(section: Section | None) -> str:
    """A section's own opening verdict, with the "Verdict." label removed."""
    text = first_callout(section, ("verdict",))
    return re.sub(r"^\*\*Verdict[^*]*\*\*\s*", "", text).strip()


def trim_table(table: Table, max_rows: int, max_cols: int,
               keep_cols: list[int] | None = None) -> Table:
    """Fit a dossier table onto a slide without silently dropping the point.

    A trimmed table gains a caption saying so, because a reader must never think they are
    seeing the whole register.
    """
    cols = keep_cols or list(range(min(len(table.header), max_cols)))
    cols = cols[:max_cols]
    rows = [[row[i] if i < len(row) else "" for i in cols] for row in table.rows[:max_rows]]
    caption = None
    if len(table.rows) > len(rows) or len(table.header) > len(cols):
        caption = f"Showing {len(rows)} of {len(table.rows)} rows"
        if len(table.header) > len(cols):
            caption += f" and {len(cols)} of {len(table.header)} columns"
        caption += " — full register in the dossier."
    return Table(
        header=[table.header[i] for i in cols if i < len(table.header)],
        rows=rows,
        aligns=[table.aligns[i] if i < len(table.aligns) else "left" for i in cols],
        caption=caption,
    )


# The dossier writes negatives with U+2212 MINUS SIGN. Losing it turns "−651" into "651".
MINUS = "-−–‐"
NUMBER_RE = re.compile(
    rf"(?P<sign>[{MINUS}]?)\s*(?P<body>(?:USD\s?|US\$|A\$|[$€£])?\s?"
    rf"(?:\d{{1,3}}(?:,\d{{3}})+|\d+)(?:\.\d+)?"
    rf"\s?(?:%|bps|bn\b|[BMK]\b|billion|million|trillion)?)"
)


def headline_number(value: str) -> str:
    """Pull the leading quantity out of a dense snapshot cell, sign intact."""
    text = plain(value)
    if SUPPRESSED_RE.search(text) or text.strip().startswith("["):
        return ""
    match = NUMBER_RE.search(text)
    if not match:
        return ""
    sign = "−" if match.group("sign") else ""
    return f"{sign}{match.group('body').strip()}"


def kpi_tone(value: str) -> str:
    stripped = plain(value).strip()
    if stripped[:1] in MINUS or "decline" in stripped.lower() or "outflow" in stripped.lower():
        return "risk"
    return "neutral"


def score(text: str) -> float | None:
    """The leading score in a scored cell (``**3.5**. Need 5 …``) — never from a suppressed one."""
    flat = plain(text)
    if SUPPRESSED_RE.search(flat[:80]) or "n/e" in flat[:12]:
        return None
    m = re.match(r"\s*(\d+(?:\.\d+)?)", flat)
    return float(m.group(1)) if m else None


def refs(*texts: str) -> list[str]:
    return claim_refs(" ".join(texts))[:8]


# ── deck ─────────────────────────────────────────────────────────────────────


def build_deck_plan(dossier: Dossier, depth: str = "standard") -> DeckPlan:
    depth = depth if depth in DEPTHS else "standard"
    vertical = vertical_words(dossier)
    slides: list[Slide] = [_cover(dossier, vertical)]
    slides.extend(_reliability(dossier))

    thesis = verdict(dossier.find("1"))
    if thesis:
        slides.append(Slide(
            layout=SlideLayout.STATEMENT, title=truncate(thesis, 230), subtitle="The verdict",
            source_sections=["1"], claim_refs=refs(thesis),
            emphasis="dark", icon="file-text",
            notes="The single sentence the room should leave with. Say the confidence out loud.",
        ))

    slides.extend(_snapshot(dossier))
    slides.extend(_findings(dossier, 4 if depth == "exec" else 6))
    relevance = verdict(dossier.find("1.3"))
    if relevance and depth != "exec":
        slides.append(Slide(
            layout=SlideLayout.STATEMENT, title=truncate(relevance, 230),
            subtitle="Strategic relevance for the pursuing organization",
            source_sections=["1.3"], claim_refs=refs(relevance),
            icon="compass",
        ))
    slides.extend(_opportunities(dossier, vertical))
    slides.extend(_risks(dossier))
    slides.extend(_readiness(dossier))
    slides.extend(_actions(dossier))

    if depth in {"standard", "full"}:
        slides.append(Slide(
            layout=SlideLayout.SECTION, title="The evidence",
            subtitle="What the body of the dossier establishes", emphasis="dark",
            icon="book-open", image_query=f"research analysis {vertical}".strip(),
        ))
        if depth == "standard":
            slides.extend(_evidence_groups(dossier))
        else:
            for section in dossier.body_sections:
                if section.id.isdigit() and 3 <= int(section.id) <= 20:
                    slides.extend(_section_slides(section))

    slides.extend(_unknowns(dossier))
    slides.extend(_verification(dossier))
    slides.append(Slide(
        layout=SlideLayout.CLOSING, title="Evidence first. Decisions second.",
        subtitle=SCORE_DISCLAIMER, emphasis="dark",
    ))

    return DeckPlan(
        client=dossier.client, title=dossier.client, as_of=dossier.as_of or "",
        thesis=plain(thesis)[:400], audience="Account and pursuit leadership",
        slides=slides,
    )


def _cover(dossier: Dossier, vertical: str) -> Slide:
    meta = [x for x in (
        dossier.as_of and f"As of {dossier.as_of}",
        dossier.tier and dossier.tier.replace("_", " ").title(),
        dossier.vertical,
    ) if x]
    return Slide(
        layout=SlideLayout.TITLE, title=dossier.client, subtitle="Vantage dossier",
        body=" · ".join(meta), emphasis="dark",
        image_query=f"{vertical or 'corporate'} {plain(dossier.client)} operations".strip(),
        notes="Opening frame. State the decision this dossier supports before moving on.",
    )


def _reliability(dossier: Dossier) -> list[Slide]:
    """Overall Confidence / EQI and the verification result travel with the collateral."""
    v = dossier.verification or {}
    kpis: list[KPI] = []
    if dossier.eqi is not None:
        kpis.append(KPI(value=f"{dossier.eqi:g}", label="Evidence Quality Index (0–100)",
                        delta=dossier.overall_confidence or None, icon="gauge",
                        tone="risk" if dossier.eqi < 60 else "neutral"))
    elif dossier.overall_confidence:
        kpis.append(KPI(value=dossier.overall_confidence[:12], label="Overall confidence",
                        icon="gauge"))
    if v.get("result"):
        result = str(v["result"])
        kpis.append(KPI(value="PASS" if result.startswith("PASS") else result[:12],
                        label="Verification result", delta=result if result != "PASS" else None,
                        icon="badge-check", tone="risk" if "FAIL" in result else "neutral"))
    counts = [f"{v[k]} {k}" for k in ("blockers", "majors", "minors") if v.get(k) is not None]
    if counts:
        kpis.append(KPI(value=str(v.get("blockers", "—")), label="Open blockers (disclosed)",
                        delta=" · ".join(counts), icon="triangle-alert",
                        tone="risk" if v.get("blockers") else "good"))
    if v.get("checks_passed") is not None and v.get("checks_executed"):
        kpis.append(KPI(value=f"{v['checks_passed']}/{v['checks_executed']}",
                        label="Verification checks passed", icon="list-checks"))
    slides: list[Slide] = []
    if kpis:
        slides.append(Slide(
            layout=SlideLayout.KPI, title="How far this dossier can be trusted",
            subtitle=" · ".join(x for x in (
                dossier.overall_confidence and f"Overall confidence: {dossier.overall_confidence}",
                v.get("result") and f"Verification: {v['result']}") if x),
            kpis=kpis[:4], source_sections=["21.8"], icon="gauge",
            notes=str(v.get("detail") or ""),
        ))
    for banner in dossier.banners:
        if banner.tone == "warning":
            slides.append(Slide(
                layout=SlideLayout.STATEMENT, title="Read before use",
                body=truncate(re.sub(r"^\*\*Read before use\.?\*\*\s*", "", banner.text), 300),
                claim_refs=refs(banner.text), icon="triangle-alert",
                notes=plain(banner.text),
            ))
            break
    return slides


SNAPSHOT_KEYS = ("revenue", "net income", "ebitda", "employees", "market cap", "free cash",
                 "aum", "net debt")


def _snapshot(dossier: Dossier) -> list[Slide]:
    section = dossier.find("1.1")
    table = first_table(section, min_rows=3)
    if table is None:
        return []
    kpis: list[KPI] = []
    for row in table.rows:
        label = plain(cell(row, 0))
        value = cell(row, 1)
        if not label or not value:
            continue
        if any(key in label.lower() for key in SNAPSHOT_KEYS):
            number = headline_number(value)
            if number:
                kpis.append(KPI(value=number, label=truncate(label, 40), tone=kpi_tone(value),
                                icon="chart-line"))
        if len(kpis) == 4:
            break
    slides: list[Slide] = []
    if kpis:
        unit = ""
        caption = next((b.text for b in section.blocks if isinstance(b, Paragraph)), "")
        if "millions" in caption.lower():
            unit = "USD millions unless stated"
        slides.append(Slide(
            layout=SlideLayout.KPI, title="Company at a glance", subtitle=unit or dossier.client,
            kpis=kpis, source_sections=["1.1"], claim_refs=refs(*[" ".join(r) for r in table.rows]),
            icon="building-2", notes="Anchor the room in scale before opinion.",
        ))
    slides.append(Slide(
        layout=SlideLayout.TABLE, title="Snapshot card",
        table=trim_table(table, max_rows=8, max_cols=2), source_sections=["1.1"],
        icon="building-2",
    ))
    return slides


def _findings(dossier: Dossier, limit: int) -> list[Slide]:
    section = dossier.find("1.2")
    table = first_table(section, min_rows=2)
    if section is None:
        return []
    slides = [Slide(layout=SlideLayout.SECTION, title="What we found",
                    subtitle="Key findings and what they mean", emphasis="dark", icon="microscope")]
    if table is None:
        bullets = bullets_from_section(section, limit=6)
        if bullets:
            slides.append(Slide(layout=SlideLayout.BULLETS, title="Key findings",
                                bullets=bullets, source_sections=["1.2"]))
        return slides
    finding_col = column(table, "finding") or 1
    implication_col = column(table, "implication", "so what")
    status_col = column(table, "status")
    confidence_col = column(table, "confidence", "conf")
    for row in table.rows[:limit]:
        finding = cell(row, finding_col)
        if not finding:
            continue
        implication = cell(row, implication_col)
        qualifiers = " · ".join(plain(x) for x in (cell(row, status_col),
                                                   cell(row, confidence_col)) if x)
        slides.append(Slide(
            layout=SlideLayout.STATEMENT,
            title=truncate(_first_sentence(finding), 150),
            body=truncate(implication or finding, 300),
            subtitle=qualifiers and f"Status / confidence: {truncate(qualifiers, 80)}",
            source_sections=["1.2"], claim_refs=refs(*row), notes=plain(finding),
        ))
    return slides


def _first_sentence(text: str) -> str:
    flat = text.strip()
    m = re.match(r"(.{40,}?[.;])\s", flat)
    return m.group(1).rstrip(".;") if m else flat


def _opportunities(dossier: Dossier, vertical: str) -> list[Slide]:
    section = dossier.find("1.4")
    if section is None:
        return []
    table = first_table(section, min_rows=2)
    slides: list[Slide] = [Slide(
        layout=SlideLayout.SECTION, title="Where the work is", subtitle="Top opportunities",
        emphasis="dark", icon="lightbulb",
        image_query=f"innovation opportunity {vertical}".strip(),
    )]
    if table is None:
        slides.append(Slide(layout=SlideLayout.BULLETS, title="Top opportunities",
                            bullets=bullets_from_section(section, 6), source_sections=["1.4"]))
        return slides
    keep = [i for i in (column(table, "#", "o-nn"), column(table, "opportunity", "theme"),
                        column(table, "attractiveness", "m4"), column(table, "win"),
                        column(table, "horizon")) if i is not None]
    slides.append(Slide(
        layout=SlideLayout.TABLE, title="Top opportunities",
        subtitle="Ranked by public attractiveness (Model 4, 1–5)",
        table=trim_table(table, max_rows=7, max_cols=6, keep_cols=sorted(set(keep)) or None),
        source_sections=["1.4"], claim_refs=refs(*[" ".join(r) for r in table.rows]),
        notes=SCORE_DISCLAIMER, icon="lightbulb",
    ))
    id_col = column(table, "#", "o-nn")
    attr_col = column(table, "attractiveness", "m4")
    if attr_col is not None:
        cats, vals = [], []
        for row in table.rows[:8]:
            value = score(cell(row, attr_col))
            if value is None:
                continue
            name = plain(cell(row, id_col)) or ""
            title = plain(cell(row, column(table, "opportunity", "theme")))
            cats.append(truncate(f"{name} {title}".strip(), 48))
            vals.append(value)
        if len(cats) >= 2:
            slides.append(Slide(
                layout=SlideLayout.CHART, title="Attractiveness by opportunity",
                body="Composite scores as the dossier states them; suppressed composites are "
                     "left out rather than estimated.",
                chart=ChartSpec(form="hbar", title="Model 4 attractiveness (1–5)",
                                categories=cats, series=[{"name": "Attractiveness",
                                                          "values": vals}],
                                unit="score", note=SCORE_DISCLAIMER),
                source_sections=["1.4", "18.1"], icon="chart-line",
            ))
    return slides


def _risks(dossier: Dossier) -> list[Slide]:
    section = dossier.find("1.5")
    if section is None:
        return []
    table = first_table(section, min_rows=2)
    if table is None:
        return [Slide(layout=SlideLayout.BULLETS, title="Risks and watchpoints",
                      bullets=bullets_from_section(section, 6), source_sections=["1.5"],
                      icon="shield-alert")]
    id_col = column(table, "#", "r-")
    risk_col = column(table, "risk") or 1
    stance_col = column(table, "mitigation", "stance", "response")
    left, right = [], []
    for row in table.rows[:6]:
        head = plain(cell(row, id_col))
        left.append(truncate(f"**{head}** {cell(row, risk_col)}".strip(), 150))
        if stance_col is not None:
            right.append(truncate(cell(row, stance_col), 150))
    slides = [Slide(
        layout=SlideLayout.TWO_COLUMN, title="Risks and watchpoints",
        subtitle="Client risk and pursuit risk, together",
        column_headings=["Risk", "Mitigation stance"], bullets=left, bullets_right=right,
        source_sections=["1.5"], claim_refs=refs(*[" ".join(r) for r in table.rows[:6]]),
        icon="shield-alert",
    )]
    sev, lik = column(table, "severity", "sev"), column(table, "likelihood", "lik")
    if sev is not None and lik is not None:
        cats, s_vals, l_vals = [], [], []
        for row in table.rows[:8]:
            s, li = score(cell(row, sev)), score(cell(row, lik))
            if s is None or li is None:
                continue
            cats.append(plain(cell(row, id_col)) or truncate(plain(cell(row, risk_col)), 20))
            s_vals.append(s)
            l_vals.append(li)
        if len(cats) >= 2:
            slides.append(Slide(
                layout=SlideLayout.CHART, title="Severity and likelihood",
                body="Both on the dossier's 1–5 register scale; the pairing, not either score "
                     "alone, sets the watch order.",
                chart=ChartSpec(form="grouped-bar", title="Top risks — severity vs likelihood",
                                categories=cats, unit="score",
                                series=[{"name": "Severity", "values": s_vals},
                                        {"name": "Likelihood", "values": l_vals}],
                                note="1–5 scales from the §14 risk register"),
                source_sections=["1.5", "14"], icon="shield-alert",
            ))
    return slides


def _readiness(dossier: Dossier) -> list[Slide]:
    section = dossier.find("1.6")
    table = first_table(section, min_rows=3)
    if table is None:
        return []
    keep = [i for i in (column(table, "dimension"), column(table, "score"),
                        column(table, "confidence")) if i is not None]
    band = ""
    for row in table.rows:
        if "band" in plain(cell(row, 0)).lower():
            band = plain(cell(row, column(table, "score") or 1))
    subtitle = verdict(section)
    return [Slide(
        layout=SlideLayout.MATRIX, title="Engagement readiness",
        subtitle=truncate(f"Band: {band}" if band else subtitle, 110),
        table=trim_table(table, max_rows=8, max_cols=4, keep_cols=keep or None),
        body=truncate(subtitle, 240), source_sections=["1.6"],
        claim_refs=refs(subtitle), notes=SCORE_DISCLAIMER, icon="gauge",
    )]


def _actions(dossier: Dossier) -> list[Slide]:
    section = dossier.find("1.7")
    table = first_table(section, min_rows=2)
    steps: list[TimelineStep] = []
    if table is not None:
        id_col = column(table, "a-nn", "#")
        when_col = column(table, "deadline", "due", "horizon", "when")
        what_col = column(table, "action", "what")
        owner_col = column(table, "owner")
        for row in table.rows[:5]:
            what = cell(row, what_col if what_col is not None else 1)
            when = plain(cell(row, when_col)) or plain(cell(row, id_col))
            ident = plain(cell(row, id_col))
            steps.append(TimelineStep(
                when=truncate(f"{when} · {ident}" if ident and ident not in when else when, 34),
                what=truncate(what, 120),
                detail=truncate(cell(row, owner_col), 60) or None,
            ))
    if steps:
        return [Slide(layout=SlideLayout.TIMELINE, title="Recommended next actions",
                      subtitle="Owned and dated", timeline=steps, source_sections=["1.7", "20.6"],
                      claim_refs=refs(*[" ".join(r) for r in (table.rows if table else [])][:5]),
                      icon="list-checks")]
    bullets = bullets_from_section(section, 6)
    return [Slide(layout=SlideLayout.BULLETS, title="Recommended next actions",
                  bullets=bullets, source_sections=["1.7"], icon="list-checks")] if bullets else []


def _evidence_groups(dossier: Dossier) -> list[Slide]:
    slides: list[Slide] = []
    for slug, title, ids, icon in GROUPS:
        if slug in {"brief", "method"}:
            continue
        bullets, used = [], []
        for section_id in ids:
            section = dossier.find(section_id)
            if section is None:
                continue
            text = verdict(section) or lead_paragraph(section, 180)
            if text:
                bullets.append(f"**§{section.id} {plain(section.title)}** — {truncate(text, 170)}")
                used.append(section_id)
        if 0 < len(bullets) < 3:
            # A thin group (one or two sections) earns its slide with the subsection verdicts.
            for section_id in used:
                for child in (dossier.find(section_id) or Section(
                        id="", number="", title="", heading="", level=2)).children:
                    text = verdict(child)
                    if text and len(bullets) < 6:
                        bullets.append(f"**§{child.id} {plain(child.title)}** — "
                                       f"{truncate(text, 150)}")
        if bullets:
            slides.append(Slide(
                layout=SlideLayout.BULLETS, title=title, bullets=bullets[:7],
                source_sections=used, icon=icon,
                claim_refs=refs(*bullets),
            ))
        # One chart per group where the dossier states the comparison numerically.
        if slug not in {"financials", "pursuit", "strategy"}:
            continue
        for section_id in used:
            section = dossier.find(section_id)
            chart = next((c for node in section.walk() for c in node.charts), None) \
                if section else None
            if chart is not None:
                slides.append(_chart_slide(section, chart))
                break
    return slides


def _chart_slide(section: Section | None, chart: ChartSpec) -> Slide:
    sid = section.id if section else ""
    return Slide(
        layout=SlideLayout.CHART, title=truncate(plain(chart.title), 90),
        body=truncate(verdict(section), 240) if section else "",
        chart=chart, source_sections=[sid] if sid else [], icon=SECTION_ICON.get(sid),
        notes=chart.note or "",
    )


def _section_slides(section: Section) -> list[Slide]:
    lead = verdict(section) or lead_paragraph(section, 260)
    bullets: list[str] = []
    for child in section.children[:6]:
        text = verdict(child) or lead_paragraph(child, 150)
        if text:
            bullets.append(f"**{plain(child.title)}** — {truncate(text, 150)}")
    slides = [Slide(
        layout=SlideLayout.BULLETS,
        title=f"§{section.id} {plain(section.title)}".strip(),
        subtitle=SECTION_TAKEAWAY.get(section.id, ""),
        body=truncate(lead, 240) if lead and not bullets else "",
        bullets=bullets, source_sections=[section.id], icon=SECTION_ICON.get(section.id),
        claim_refs=refs(lead, *bullets),
    )]
    chart = next((c for node in section.walk() for c in node.charts), None)
    if chart is not None:
        slides.append(_chart_slide(section, chart))
    figure = next((f for node in section.walk() for f in node.figures), None)
    if figure is not None:
        slides.append(Slide(
            layout=SlideLayout.FIGURE, title=truncate(figure.title, 90), figure=figure,
            body=truncate(lead, 200), source_sections=[section.id],
            icon=SECTION_ICON.get(section.id), notes=figure.caption(),
        ))
    table = first_table(section, min_rows=3, deep=True)
    if table is not None:
        slides.append(Slide(
            layout=SlideLayout.TABLE, title=f"{plain(section.title)} — detail",
            table=trim_table(table, max_rows=8, max_cols=6), source_sections=[section.id],
            icon=SECTION_ICON.get(section.id),
        ))
    return slides


def _gap_register(dossier: Dossier) -> dict[str, str]:
    """``G-nnnn`` → what is missing, from the §21.11 register."""
    out: dict[str, str] = {}
    for table in tables(dossier.find("21.11"), deep=True):
        id_col = column(table, "id")
        what_col = column(table, "missing", "gap", "question")
        if id_col is None or what_col is None:
            continue
        for row in table.rows:
            ident = plain(cell(row, id_col)).strip()
            if ident.startswith("G-"):
                out.setdefault(ident, cell(row, what_col))
    return out


def _unknowns(dossier: Dossier) -> list[Slide]:
    register = _gap_register(dossier)
    brief = dossier.find("1")
    cited = [r for r in claim_refs(" ".join(
        plain(b.text) if isinstance(b, Paragraph | Callout) else " ".join(
            " ".join(row) for row in b.rows) if isinstance(b, Table) else ""
        for node in (brief.walk() if brief else []) for b in node.blocks)) if r.startswith("G-")]
    bullets = [f"**{g}** — {truncate(register[g], 150)}" for g in cited if g in register][:6]
    if not bullets:
        bullets = [f"**{g}** — {truncate(text, 150)}" for g, text in list(register.items())[:6]]
    if not bullets:
        return []
    return [Slide(
        layout=SlideLayout.BULLETS, title="Material unknowns",
        subtitle="What this dossier could not establish", bullets=bullets,
        source_sections=["21.11"], icon="circle-help",
        notes="Name the gaps before someone else does. Each one is a qualification question.",
    )]


def _verification(dossier: Dossier) -> list[Slide]:
    v = dossier.verification
    if not v:
        return []
    bullets = [f"**Result:** {v.get('result')}"]
    if v.get("detail"):
        bullets.append(truncate(str(v["detail"]), 200))
    if dossier.overall_confidence:
        bullets.append(f"**Overall confidence:** {dossier.overall_confidence}"
                       + (f" (EQI {dossier.eqi:g})" if dossier.eqi is not None else ""))
    for banner in dossier.banners:
        if banner.tone == "warning":
            bullets.append(truncate(banner.text, 200))
            break
    errata = [b for node in (dossier.find("1").walk() if dossier.find("1") else [])
              for b in node.blocks if isinstance(b, Callout) and "erratum" in b.text.lower()[:60]]
    if errata:
        bullets.append(f"{len(errata)} verification errata are printed in the executive summary; "
                       "where a sentence and its erratum disagree, the erratum governs.")
    return [Slide(
        layout=SlideLayout.BULLETS, title="Verification and disclosures",
        subtitle="What the verifier found, and what remains disclosed", bullets=bullets[:7],
        source_sections=["21.8"], icon="badge-check",
    )]


def bullets_from_section(section: Section | None, limit: int = 6) -> list[str]:
    if section is None:
        return []
    out: list[str] = []
    for block in section.blocks:
        if isinstance(block, ListBlock):
            out.extend(truncate(item.text, 160) for item in block.items)
        elif isinstance(block, Table) and block.rows:
            col = 1 if len(block.header) > 1 else 0
            out.extend(truncate(row[col], 160) for row in block.rows if col < len(row))
        elif isinstance(block, Paragraph) and len(plain(block.text)) > 40:
            out.append(truncate(block.text.split("\n\n")[0], 160))
        if len(out) >= limit:
            break
    return out[:limit]


# ── whitepaper ───────────────────────────────────────────────────────────────


def build_doc_plan(dossier: Dossier, depth: str = "standard") -> DocPlan:
    depth = depth if depth in DEPTHS else "standard"
    body_treatment = {"exec": DocTreatment.SUMMARY, "standard": DocTreatment.CONDENSE,
                      "full": DocTreatment.VERBATIM}[depth]
    sections: list[DocSectionPlan] = []
    for root in dossier.sections:
        sid = root.id
        if not sid.isdigit():
            continue
        if sid == "21" and depth != "full":
            continue
        treatment = DocTreatment.VERBATIM if sid == "1" else body_treatment
        if sid in {"0", "2"} and depth != "full":
            treatment = DocTreatment.CONDENSE if depth == "standard" else DocTreatment.SUMMARY
        summary = ""
        if treatment == DocTreatment.SUMMARY:
            summary = "\n\n".join(x for x in (verdict(root), lead_paragraph(root, 900)) if x)
        callouts = []
        if sid == "1":
            callouts.append(Callout(text=SCORE_DISCLAIMER, tone="disclaimer"))
        sections.append(DocSectionPlan(
            section_id=sid, treatment=treatment, summary=summary,
            lead=SECTION_TAKEAWAY.get(sid, ""), callouts=callouts,
            page_break_before=sid in {"1", "2", "3", "18", "21"},
        ))
    return DocPlan(
        client=dossier.client, title=dossier.client, subtitle="Vantage dossier",
        as_of=dossier.as_of or "", abstract=truncate(verdict(dossier.find("1")), 700),
        author="Prepared with Vantage", sections=sections,
        appendix_policy="none" if depth == "full" else "selected",
        appendices=[a for a in APPENDICES_BY_DEPTH[depth] if dossier.find(a) is not None],
    )


# ── microsite ────────────────────────────────────────────────────────────────


def build_site_plan(dossier: Dossier, mode: str = "microsite", depth: str = "standard") -> SitePlan:
    depth = depth if depth in DEPTHS else "standard"
    vertical = vertical_words(dossier)
    groups = GROUPS if depth != "exec" else [g for g in GROUPS if g[0] in {"brief", "method"}]
    pages: list[SitePage] = []
    for slug, title, ids, icon in groups:
        present = [s for s in ids if dossier.find(s) is not None]
        if not present:
            continue
        lead = dossier.find(present[0])
        pages.append(SitePage(
            slug=slug, title=title, section_ids=present,
            summary=truncate(verdict(lead) or lead_paragraph(lead, 220), 260),
            icon=icon, image_query=f"{title} {vertical}".strip(),
        ))
    reference = ["21"] if depth == "full" else APPENDICES_BY_DEPTH[depth]
    reference = [r for r in reference if dossier.find(r) is not None]
    if reference:
        pages.append(SitePage(
            slug="reference", title="Registers and verification", section_ids=reference,
            summary=SECTION_TAKEAWAY["21"], icon="book-open",
        ))
    return SitePlan(
        client=dossier.client, title=dossier.client, as_of=dossier.as_of or "",
        mode="deck" if mode == "deck" else "microsite", pages=pages,
    )
