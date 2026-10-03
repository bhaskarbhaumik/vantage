import json

from vantage.models.state import VantageState
from vantage.pipeline.merge import merge_fragments
from vantage.render.assembly import assemble, unresolved_references


def _run(tmp_path):
    run = tmp_path / "acme"
    (run / "sections").mkdir(parents=True)
    (run / "state" / "fragments").mkdir(parents=True)
    return run


def test_assembly_end_to_end(tmp_path):
    run = _run(tmp_path)
    (run / "sections" / "03-company.md").write_text("## 3. Company Overview\n\n> Industrial.")
    (run / "sections" / "06-financials.md").write_text(
        "## 6. Financial Performance\n\n> FY2025 revenue $41B [C-6.2-01].")
    (run / "sections" / "01-exec-brief.md").write_text(
        "## 1. Executive Summary\n\nGrowth decelerated [C-6.2-01]; see [O-01] and gap [G-0500].")
    (run / "state" / "fragments" / "financials.json").write_text(json.dumps({
        "agent": "financials",
        "source_manifest": [
            {"id": "S-0500", "url": "u", "title": "FY2025 10-K", "retrieval_status": "ok",
             "tier": 1, "minted_by": "financials", "sections": ["6.1"]},
            {"id": "S-0501", "url": "p", "title": "Analyst note", "retrieval_status": "paywall",
             "retrieval_note": "used the IR deck instead", "minted_by": "financials"},
        ],
        "claim_ledger": [{"id": "C-6.2-01", "claim": "revenue grew", "section": "6.2",
                          "materiality": "high", "confidence": "HIGH", "status": "CONFIRMED",
                          "sources": ["S-0500"]}],
        "data_gaps": [{"id": "G-0500", "item": "IT spend", "section": "6.6",
                       "searched": ["10-K Item 7", "investor day"], "materiality": "high",
                       "resolution_path": "account-team-validation", "minted_by": "financials"}],
        "coverage": [{"section": "6", "expected": ["10-K", "XBRL", "transcripts"],
                      "retrieved": ["10-K", "XBRL"], "stop_reason": "budget",
                      "residual_risk": "guidance history unverified"}],
    }))
    (run / "state" / "fragments" / "opportunity.json").write_text(json.dumps({
        "agent": "opportunity", "opportunities": [{"id": "O-01", "title": "Core modernization"}]}))
    (run / "state" / "fragments" / "verification.json").write_text(json.dumps({
        "agent": "verification",
        "verification": {"result": "PASS WITH DISCLOSURES", "overall_confidence": "Adequate",
                         "eqi": 71.4, "blockers": 0}}))

    state = merge_fragments(run)
    out = assemble(run, state, "acme", client="Acme Industries, Inc.",
                   research_as_of="2026-08-29", tier="FULL_ANNEX")
    text = out.read_text()

    for marker in [
        "# Vantage — Acme Industries, Inc.",
        "**Vantage:** Verified Account Navigator: Targeting, Analysis & GTM Engine",
        "**Overall Confidence:** Adequate (EQI 71.4)",
        "21.1 Source Manifest", "21.9 Claim Ledger",
        "21.10 Account-Team Input Sheet", "21.11 Contradiction & Data-Gap Register",
        "21.12 Source-Completeness Scorecard",
        "## 6. Financial Performance", "C-6.2-01", "G-0500",
    ]:
        assert marker in text, f"missing {marker!r}"


def test_failed_retrievals_survive_into_the_manifest(tmp_path):
    """V1h. A manifest showing only successes misrepresents coverage."""
    run = _run(tmp_path)
    (run / "state" / "fragments" / "f.json").write_text(json.dumps({
        "agent": "market",
        "source_manifest": [{"id": "S-0300", "title": "Paywalled report", "url": "p",
                             "retrieval_status": "paywall", "retrieval_note": "tried the abstract",
                             "minted_by": "market"}]}))
    state = merge_fragments(run)
    text = assemble(run, state, "acme", client="Acme", research_as_of="2026-08-29").read_text()
    assert "Failed retrievals" in text
    assert "tried the abstract" in text


def test_budget_limited_topics_are_visibly_distinguished(tmp_path):
    """The difference between 'nothing is there' and 'we did not look far enough'."""
    run = _run(tmp_path)
    (run / "state" / "fragments" / "f.json").write_text(json.dumps({
        "agent": "esg",
        "coverage": [{"section": "17", "stop_reason": "budget"},
                     {"section": "14", "stop_reason": "diminishing_returns"}]}))
    state = merge_fragments(run)
    text = assemble(run, state, "acme", client="Acme", research_as_of="2026-08-29").read_text()
    assert "Stopped on budget, not on diminishing returns:" in text
    assert "§17" in text


def test_input_sheet_template_is_emitted_when_absent(tmp_path):
    """§21.10 blank template is the deliverable — it unlocks the gated fields on a re-run."""
    run = _run(tmp_path)
    state = merge_fragments(run)
    text = assemble(run, state, "acme", client="Acme", research_as_of="2026-08-29").read_text()
    assert "[INTERNAL]" in text
    assert "[INTERNAL REQUIRED]" in text


def test_contested_facts_reach_the_appendix(tmp_path):
    run = _run(tmp_path)
    for agent, val in (("financials", 40.2), ("corporate", 39.9)):
        (run / "state" / "fragments" / f"{agent}.json").write_text(json.dumps({
            "agent": agent,
            "carry_forward_facts": {"revenue_fy0": {"value": val, "as_of": "FY2025"}}}))
    state = merge_fragments(run)
    text = assemble(run, state, "acme", client="Acme", research_as_of="2026-08-29").read_text()
    assert "Contested canonical facts" in text
    assert "omitted from downstream use" in text


def test_unresolved_references_are_recorded_never_invented(tmp_path):
    state = VantageState(source_manifest=[{"id": "S-0001"}], claim_ledger=[{"id": "C-3.1-01"}])
    body = "Fact one [C-3.1-01] from [S-0001], plus a dangling [S-9999] and [O-07]."
    assert unresolved_references(body, state) == ["O-07", "S-9999"]

    run = _run(tmp_path)
    (run / "sections" / "01-exec-brief.md").write_text("## 1. Summary\n\n" + body)
    merged = merge_fragments(run)
    merged.source_manifest = [{"id": "S-0001"}]
    merged.claim_ledger = [{"id": "C-3.1-01"}]
    text = assemble(run, merged, "acme", client="Acme", research_as_of="2026-08-29").read_text()
    assert "Unresolved references (recorded, not invented)" in text
    assert "S-9999" in text
    # ...and no manifest row was fabricated to make it resolve.
    assert text.count("| S-9999 |") == 0


def test_entity_ambiguity_surfaces_in_the_title_block(tmp_path):
    run = _run(tmp_path)
    state = merge_fragments(run)
    state.run_contract.entity.legal_name = "Acme Corp"
    state.run_contract.entity.ambiguity = "Acme Corp (DE) vs Acme Corporation plc (UK)."
    text = assemble(run, state, "acme", client="Acme Corp", research_as_of="2026-08-29").read_text()
    assert "Entity ambiguity recorded during preflight" in text


def test_section_one_is_placed_first(tmp_path):
    """§1 is written last and placed first — the numbering is the contract (V6a)."""
    run = _run(tmp_path)
    (run / "sections" / "01-exec-brief.md").write_text("## 1. Executive Summary\n\nX.")
    (run / "sections" / "06-financials.md").write_text("## 6. Financial Performance\n\nY.")
    state = merge_fragments(run)
    text = assemble(run, state, "acme", client="Acme", research_as_of="2026-08-29").read_text()
    assert text.index("## 1. Executive Summary") < text.index("## 6. Financial Performance")


# --- ownership-form adjustment (verification-protocol.md § Ownership-form adjustment) -------

from vantage.render.assembly import (  # noqa: E402
    _adjustment_is_live,
    _attainment_suffix,
    _eqi_label,
)


def test_adjustment_is_inert_for_a_public_filer():
    """Attainment == raw means every attainable maximum was CONFIRMED+HIGH.

    The protocol calls the adjustment inert there; the title block must be byte-identical
    to a run that never computed an attainment score at all.
    """
    assert _adjustment_is_live(71.4, 71.4, None) is False
    assert _eqi_label(71.4, 71.4, None) == " (EQI 71.4)"
    assert _attainment_suffix(71.4, "Adequate", None, "public", 71.4) == ""

    # ...and identical to the no-attainment case.
    assert _eqi_label(71.4, None, None) == " (EQI 71.4)"
    assert _attainment_suffix(None, None, None, "public", 71.4) == ""


def test_ceiling_bound_target_publishes_both_numbers():
    """A family-group non-filer shows raw and attainment, raw first, attainment named."""
    assert _adjustment_is_live(51.2, 68.9, None) is True
    assert _eqi_label(51.2, 68.9, None) == " (EQI_raw 51.2)"

    suffix = _attainment_suffix(68.9, "Adequate", None, "family-group", 51.2)
    assert "attainment" in suffix
    assert "EQI_att 68.9" in suffix
    assert "family-group" in suffix
    assert "ceiling-bound" in suffix


def test_attainment_can_never_masquerade_as_the_headline_band():
    """V13d: the raw band leads and the qualifier is always labelled.

    A reader must not be able to mistake the attainment band for the document's confidence.
    """
    band_raw, eqi_raw, eqi_att = "Thin", 51.2, 68.9
    line = f"**Overall Confidence:** {band_raw}" + _eqi_label(eqi_raw, eqi_att, None) + \
        _attainment_suffix(eqi_att, "Adequate", None, "family-group", eqi_raw)

    assert line.index("Thin") < line.index("Adequate"), "raw band must lead"
    assert "Adequate" not in line.split("·")[0], "attainment must not sit in the headline clause"
    assert line.count("attainment") == 1


def test_suppressed_attainment_reports_the_finding_not_a_number():
    """V13c: >50% of a denominator excluded means the score is noise — report that instead."""
    assert _adjustment_is_live(48.0, None, True) is True
    assert _eqi_label(48.0, None, True) == " (EQI_raw 48.0)"

    suffix = _attainment_suffix(72.0, "Adequate", True, "family-group", 48.0)
    assert "SUPPRESSED" in suffix
    assert "72.0" not in suffix, "a suppressed score must not leak its number"
    assert "Adequate" not in suffix, "a suppressed score must not leak its band"
