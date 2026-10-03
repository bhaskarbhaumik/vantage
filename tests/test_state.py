import json

from vantage.models.state import VantageState
from vantage.pipeline.merge import dedupe_sources, merge_fragments


def test_merge_dedupes_by_id():
    st = VantageState()
    st.merge_fragment({"claim_ledger": [{"id": "C-6.1-01", "claim": "a"}]})
    st.merge_fragment({"claim_ledger": [{"id": "C-6.1-01", "confidence": "HIGH"}]})
    assert len(st.claim_ledger) == 1
    assert st.claim_ledger[0]["claim"] == "a"
    assert st.claim_ledger[0]["confidence"] == "HIGH"


def test_legacy_key_aliases_are_accepted():
    """Agents are LLMs; the looser key names still land in the canonical registers."""
    st = VantageState()
    st.merge_fragment({"sources": [{"id": "S-0100"}], "claims": [{"id": "C-3.1-01"}],
                       "gaps": [{"id": "G-0100"}]})
    assert st.source_manifest and st.claim_ledger and st.data_gaps


def test_dedupe_sources_keeps_lowest_id():
    """The backbone S-0001..S-0049 wins, which makes citing it the cheap path."""
    st = VantageState(source_manifest=[
        {"id": "S-0300", "url": "https://www.sec.gov/x/?utm_source=news"},
        {"id": "S-0001", "url": "https://sec.gov/x", "sections": ["6.1"]},
    ])
    rewrite = dedupe_sources(st)
    assert [s["id"] for s in st.source_manifest] == ["S-0001"]
    assert rewrite == {"S-0300": "S-0001"}


def test_dedupe_matches_on_doc_id_when_urls_differ():
    st = VantageState(source_manifest=[
        {"id": "S-0002", "doc_id": "0000320193-25-000073"},
        {"id": "S-0500", "doc_id": "0000320193-25-000073", "sections": ["6.2"]},
    ])
    rewrite = dedupe_sources(st)
    assert rewrite == {"S-0500": "S-0002"}
    assert st.source_manifest[0]["sections"] == ["6.2"]


def test_conflicting_canonical_facts_are_contested_not_averaged():
    """V10f: two agents disagreeing on a canonical fact is the signature parallel failure.

    The contested fact is omitted from downstream use rather than reconciled by guess.
    """
    st = VantageState()
    st.merge_fragment({"agent": "financials", "carry_forward_facts": {
        "revenue_fy0": {"value": 40.2, "currency": "USD", "unit": "B", "as_of": "FY2025"}}})
    st.merge_fragment({"agent": "corporate", "carry_forward_facts": {
        "revenue_fy0": {"value": 39.9, "currency": "USD", "unit": "B", "as_of": "FY2025"}}})
    assert st.contested_facts() == ["revenue_fy0"]
    assert st.carry_forward_facts["revenue_fy0"]["competing_values"] == [40.2, 39.9]


def test_same_value_different_period_is_not_a_conflict():
    """Different period, entity, basis, or unit means different facts — not a contradiction."""
    st = VantageState()
    st.merge_fragment({"agent": "financials", "carry_forward_facts": {
        "revenue": {"value": 40.2, "as_of": "FY2025"}}})
    st.merge_fragment({"agent": "corporate", "carry_forward_facts": {
        "revenue": {"value": 40.2, "as_of": "FY2025", "source": "S-0004"}}})
    assert st.contested_facts() == []
    assert st.carry_forward_facts["revenue"]["source"] == "S-0004"


def test_single_owner_register_from_wrong_agent_is_a_defect():
    st = VantageState()
    st.merge_fragment({"agent": "corporate", "risks": [{"id": "R-01"}]}, agent="corporate")
    assert st.risks == []
    assert st.merge_defects[0]["kind"] == "single_owner_violation"
    st.merge_fragment({"agent": "risk", "risks": [{"id": "R-01"}]}, agent="risk")
    assert len(st.risks) == 1


def test_refuted_claims_are_readable_from_either_shape():
    st = VantageState(evidence_audit={
        "refuted": ["C-9.2-03"],
        "verdicts": [{"claim_id": "C-8.3-01", "verdict": "REFUTED"},
                     {"claim_id": "C-8.3-02", "verdict": "WEAKENED"}]})
    assert st.refuted_claim_ids() == {"C-9.2-03", "C-8.3-01"}


def test_merge_fragments_from_disk(tmp_path):
    fdir = tmp_path / "state" / "fragments"
    fdir.mkdir(parents=True)
    (fdir / "preflight.json").write_text(json.dumps({
        "agent": "preflight",
        "source_manifest": [{"id": "S-0001", "url": "u1", "minted_by": "preflight"}],
        "carry_forward_facts": {"ceo": {"value": "Jane", "source": "S-0001"}},
    }))
    (fdir / "financials.json").write_text(json.dumps({
        "agent": "financials",
        "claim_ledger": [{"id": "C-6.2-01", "materiality": "high"}],
        "data_gaps": [{"id": "G-0500", "materiality": "medium", "minted_by": "financials"}],
        "coverage": [{"section": "6", "stop_reason": "budget"}],
    }))
    st = merge_fragments(tmp_path)
    assert (tmp_path / "state" / "state.json").exists()
    assert st.carry_forward_facts["ceo"]["value"] == "Jane"
    assert len(st.claim_ledger) == 1 and len(st.data_gaps) == 1
    assert st.coverage[0]["stop_reason"] == "budget"


def test_out_of_block_id_is_recorded_not_repaired(tmp_path):
    """V1c. source-merge is a collator; a silent fix would hide the defect from verification."""
    fdir = tmp_path / "state" / "fragments"
    fdir.mkdir(parents=True)
    (fdir / "financials.json").write_text(json.dumps({
        "agent": "financials",
        "source_manifest": [{"id": "S-0900", "url": "u", "minted_by": "financials"}],
    }))
    st = merge_fragments(tmp_path)
    kinds = [d["kind"] for d in st.merge_defects]
    assert "out_of_block_id" in kinds
    assert st.source_manifest[0]["id"] == "S-0900"  # recorded, not renumbered


def test_false_triangulation_is_downgraded_and_reported(tmp_path):
    """V10h. A HIGH claim whose two sources collapse to one is confidence inflation."""
    fdir = tmp_path / "state" / "fragments"
    fdir.mkdir(parents=True)
    (fdir / "market.json").write_text(json.dumps({
        "agent": "market",
        "source_manifest": [
            {"id": "S-0300", "url": "https://ir.example.com/pr", "minted_by": "market"},
            {"id": "S-0301", "url": "https://ir.example.com/pr/", "minted_by": "market"},
        ],
        "claim_ledger": [{"id": "C-4.2-01", "sources": ["S-0300", "S-0301"],
                          "confidence": "HIGH", "dimensions": {"corroboration": 2}}],
    }))
    st = merge_fragments(tmp_path)
    assert st.claim_ledger[0]["confidence"] == "MEDIUM"
    assert st.claim_ledger[0]["dimensions"]["corroboration"] == 1
    assert st.merge_report["false_triangulation"][0]["claim_id"] == "C-4.2-01"


def test_missing_agent_is_named_not_absorbed(tmp_path):
    """V10e: silent data loss is the failure mode a parallel harness must not have."""
    (tmp_path / "state" / "fragments").mkdir(parents=True)
    st = merge_fragments(tmp_path, expected_labels=["financials", "risk"])
    missing = {d["agent"] for d in st.merge_defects if d["kind"] == "missing_fragment"}
    assert missing == {"financials", "risk"}
