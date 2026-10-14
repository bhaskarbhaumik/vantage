"""Export: parsing the v3 dossier, lifting visual blocks, plans, and the integrity rules."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from vantage.export import dossier as dz
from vantage.export.models import (
    Callout,
    ChartBlock,
    Code,
    DeckPlan,
    DocPlan,
    FigureBlock,
    SitePlan,
    SlideLayout,
    Table,
)
from vantage.export.parse import claim_refs, parse_markdown
from vantage.export.plan import build_deck_plan, build_doc_plan, build_site_plan, headline_number
from vantage.export.richtext import markers, parse_runs, plain, to_html, truncate

FIXTURE = Path(__file__).parent / "fixtures" / "export" / "northwind-2026-10"
DOSSIER = FIXTURE / "northwind-2026-10-vantage.md"


@pytest.fixture(scope="module")
def d():
    return dz.load_dossier(DOSSIER)


# ── parsing ──────────────────────────────────────────────────────────────────


def test_title_block(d):
    assert d.client == "Northwind Ceramics Corporation"
    assert d.version == "3.0.0"
    assert d.tier == "STANDARD"
    assert d.as_of == "2026-10-01"
    assert d.overall_confidence == "Adequate"
    assert d.eqi == 66.2
    assert d.client_domain == "northwind-ceramics.example"
    assert d.vertical == "V-MFG"
    assert dz.is_v3(d)


def test_verification_parsed_from_title_block(d):
    v = d.verification
    assert v["result"] == "PASS WITH DISCLOSURES"
    assert (v["blockers"], v["majors"], v["minors"]) == (2, 5, 1)
    assert (v["checks_passed"], v["checks_executed"]) == (61, 70)


def test_banners_keep_their_tone(d):
    assert [b.tone for b in d.banners] == ["disclaimer", "warning"]


def test_sections_nest_and_number(d):
    ids = [s.id for s in d.sections]
    assert ids[:4] == ["0", "1", "2", "3"] and ids[-1] == "21"
    assert [c.id for c in d.find("1").children] == ["1.1", "1.2", "1.3", "1.4", "1.5", "1.6",
                                                   "1.7"]
    assert d.find("21.11") is not None


def test_visual_blocks_lifted_in_place(d):
    stats = d.stats()
    assert stats["charts"] == 4 and stats["figures"] == 2
    six = d.find("6.1")
    kinds = [b.kind for b in six.blocks]
    assert "code" not in kinds
    combo = next(b.spec for b in six.blocks if isinstance(b, ChartBlock) and b.spec.id == "C-6.1")
    assert combo.form == "combo"
    assert combo.series[1]["values"] == [1.2, None, -4.9]       # null stays a gap, never zero
    assert "gaps" in combo.note
    waterfall = next(b.spec for b in six.blocks
                     if isinstance(b, ChartBlock) and b.spec.form == "waterfall")
    assert waterfall.categories[0] == "Opening"
    # An all-null chart becomes a visible note that keeps its marker.
    empty = [b for b in six.blocks if isinstance(b, Callout) and "C-6.6" in b.text]
    assert empty and "[DATA UNAVAILABLE]" in empty[0].text


def test_figures_parse_nodes_edges_and_positions(d):
    org = d.find("3").figures[0]
    assert org.id == "F-3.3" and len(org.nodes) == 4 and len(org.edges) == 3
    assert not org.positioned
    risk = d.find("14").figures[0]
    assert risk.positioned and risk.axes["x"] == "Likelihood"


def test_hyphenated_fences_do_not_swallow_headings():
    md = textwrap.dedent("""\
        # Vantage — Acme

        ## 1. One
        ```chart-data
        {"schema": "vantage-chart/v1", "x": ["a"], "series": [{"name": "s", "values": [1]}]}
        ```
        ## 2. Two
        text
        """)
    doc = parse_markdown(md, "acme-vantage.md")
    assert [s.id for s in doc.sections] == ["1", "2"]


def test_foreign_schema_kind_is_kept_as_code():
    md = ("# Vantage — Acme\n\n## 1. S\n\n```chart-data\n"
          '{"schema": "vantage-figure/v1", "x": ["a"], "series": [{"values": [1]}]}\n```\n')
    doc = parse_markdown(md, "x.md")
    charts, figures, unparsed = dz.extract_visuals(doc)
    assert (charts, figures, unparsed) == (0, 0, 1)
    assert any(isinstance(b, Code) for b in doc.find("1").blocks)


def test_unparseable_block_is_kept_not_dropped():
    doc = parse_markdown("# T\n\n## 1. S\n\n```figure-spec\n{not json\n```\n", "x.md")
    assert dz.extract_visuals(doc) == (0, 0, 1)


def test_data_style_chart_is_accepted():
    spec = dz.chart_from_spec({"type": "bar", "title": "t", "data": {
        "categories": ["A", "B"], "series": [{"name": "s", "values": [1, -2]}]}})
    assert spec is not None and spec.categories == ["A", "B"]


# ── richtext + markers ───────────────────────────────────────────────────────


def test_truncate_reappends_a_marker_it_would_cut():
    text = "A long claim about sizing that runs on and on and on and on [ESTIMATED] for sure"
    out = truncate(text, 30)
    assert out.endswith("[ESTIMATED]")
    assert len(truncate("short", 30)) == 5


def test_markers_and_minus_survive_plain():
    assert markers("x `[INTERNAL REQUIRED]` and SUPPRESSED [DATA GAP]") == [
        "[INTERNAL REQUIRED]", "SUPPRESSED", "[DATA GAP]"]
    assert plain("**−$56.9B** FY2025") == "−$56.9B FY2025"


def test_html_never_emits_an_external_href():
    out = to_html("see [the filing](https://example.com/10k)")
    assert "href=" not in out and "https://example.com/10k" in out
    assert [r.href for r in parse_runs("[a](#x)")] == ["#x"]


def test_claim_refs_extraction():
    assert claim_refs("led by `O-04`, [`C-4.2-05`, `G-0504`] and S-0013") == [
        "O-04", "C-4.2-05", "G-0504", "S-0013"]


def test_headline_number_keeps_sign_and_ignores_suppressed():
    assert headline_number("−118 (FY2024 42)") == "−118"
    assert headline_number("About USD 1.9B at close") == "USD 1.9B"
    assert headline_number("**SUPPRESSED** — two dimensions LOW") == ""
    assert headline_number("[DATA UNAVAILABLE]. No release") == ""


# ── text policy ──────────────────────────────────────────────────────────────


def test_strip_citations_keeps_the_caveat():
    assert dz.strip_citations("Revenue rose [S-0004].") == "Revenue rose."
    assert dz.strip_citations("Colocated [S-0408 — SNIPPET-ONLY].") == "Colocated [SNIPPET-ONLY]."
    assert "[DATA GAP]" in dz.strip_citations("Value is [DATA GAP] [S-0700].")


def test_strip_xrefs_repairs_the_phrase():
    assert dz.strip_xrefs("Detail in §6.2.") == "Detail elsewhere in this report."


# ── plans ────────────────────────────────────────────────────────────────────


def test_deck_plan_shape(d):
    plan = build_deck_plan(d, "standard")
    DeckPlan.model_validate(plan.model_dump())
    layouts = [s.layout for s in plan.slides]
    assert layouts[0] is SlideLayout.TITLE and layouts[-1] is SlideLayout.CLOSING
    titles = [s.title for s in plan.slides]
    assert "Material unknowns" in titles and "Verification and disclosures" in titles
    for slide in plan.slides:
        assert len(slide.bullets) <= 7 and len(slide.kpis) <= 4 and len(slide.timeline) <= 5
        if slide.table is not None:
            assert len(slide.table.rows) <= 8


def test_depth_changes_deck_length(d):
    lengths = {k: len(build_deck_plan(d, k).slides) for k in ("exec", "standard", "full")}
    assert lengths["exec"] < lengths["standard"] <= lengths["full"]


def test_suppressed_composite_is_never_a_number(d):
    plan = build_deck_plan(d, "full")
    chart = next(s.chart for s in plan.slides if s.title == "Attractiveness by opportunity")
    assert [c.split()[0] for c in chart.categories] == ["O-01", "O-02"]   # O-03 is suppressed
    readiness = next(s for s in plan.slides if s.title == "Engagement readiness")
    cells = [c for row in readiness.table.rows for c in row]
    assert any("SUPPRESSED" in c for c in cells)
    kpis = [k for s in plan.slides for k in s.kpis]
    assert all("SUPPRESSED" not in k.value for k in kpis)


def test_negative_kpi_keeps_its_sign(d):
    kpis = [k for s in build_deck_plan(d, "exec").slides for k in s.kpis]
    net = next(k for k in kpis if "net income" in k.label.lower())
    assert net.value == "−118" and net.tone == "risk"


def test_reliability_slide_carries_eqi_and_verification(d):
    slide = build_deck_plan(d, "exec").slides[1]
    values = {k.label: k.value for k in slide.kpis}
    assert values["Evidence Quality Index (0–100)"] == "66.2"
    assert values["Verification result"] == "PASS"


def test_unknowns_come_from_the_gap_register_cited_in_section_1(d):
    slide = next(s for s in build_deck_plan(d, "exec").slides if s.title == "Material unknowns")
    assert slide.bullets[0].startswith("**G-0101**")


def test_doc_and_site_plans(d):
    doc = build_doc_plan(d, "standard")
    DocPlan.model_validate(doc.model_dump())
    assert [s.section_id for s in doc.sections][:2] == ["0", "1"]
    assert "21" not in [s.section_id for s in doc.sections]
    assert doc.appendices == ["21.1", "21.8", "21.11"]
    assert build_doc_plan(d, "full").sections[-1].section_id == "21"
    site = build_site_plan(d, "microsite", "standard")
    SitePlan.model_validate(site.model_dump())
    for page in site.pages:
        assert page.section_ids and all(d.find(s) is not None for s in page.section_ids)


def test_tables_are_parsed_with_alignment(d):
    table = next(b for b in d.find("6.1").blocks if isinstance(b, Table))
    assert table.aligns == ["left", "right", "right"]
    assert table.rows[1][2] == "−118"


def test_figure_blocks_render_in_section_order(d):
    kinds = [b.kind for b in d.find("3").blocks]
    assert kinds.index("figure") > kinds.index("paragraph")
    assert any(isinstance(b, FigureBlock) for b in d.find("14").blocks)
