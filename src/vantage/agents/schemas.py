"""The terminal ``submit_section`` tool schema — how every agent returns its work."""

from __future__ import annotations

from ..providers.base import ToolSpec

SUBMIT_NAME = "submit_section"


def submit_spec(writes_section: bool) -> ToolSpec:
    props: dict = {
        "digest": {
            "type": "string",
            "description": "<=200 words: what you covered, dominant confidence, highest-materiality gap, "
            "anything a downstream agent must know. Concatenated into every downstream prompt.",
        },
        "fragment": {
            "type": "object",
            "description": (
                "Your state fragment per state/state.schema.json and your id-allocation block: "
                "source_manifest[] (eleven fields each, INCLUDING failed retrievals with their "
                "reason), claim_ledger[] (with the six confidence dimensions recorded so the "
                "Verification Pass can re-derive the composite), data_gaps[] (with the full "
                "negative-evidence record: searched, queries_tried, languages, date_range), "
                "coverage[] (one per top-level section you own, with stop_reason "
                "diminishing_returns|budget|not_applicable), visuals[], any single-owner register "
                "you alone mint (stakeholders/risks/opportunities/use_cases/actions/contradictions), "
                "carry_forward_facts, scoring_inputs, and handoff[]. Omit empty arrays."
            ),
        },
        "files": {
            "type": "array",
            "description": "Extra files to write, relative to the run dir (e.g. qa/qa-report.json). "
            "Most agents leave this empty.",
            "items": {
                "type": "object",
                "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
                "required": ["path", "content"],
            },
        },
        "structured": {
            "type": "object",
            "description": (
                "Typed return, only if your brief defines one. preflight: legal_name, "
                "ownership_form, jurisdictions[], reporting_standard, ticker, lei, cik, fy_end, "
                "latest_fy_label, languages[], vertical_primary, vertical_secondary[], "
                "vertical_confidence, tier, backbone_sources_registered, entity_ambiguity, "
                "anticipated_gaps[]. verification: result, overall_confidence, eqi, "
                "eqi_components, blockers, majors, minors, checks_executed, checks_passed, "
                "spec_checks, disclosed_failures[], budget_limited_topics[], "
                "eqi_attainment, attainment_confidence, eqi_attainment_components, "
                "eqi_attainment_suppressed, attainability_exclusions[] (per-claim "
                "structural justification, required by V13a/V13b)."
            ),
        },
    }
    required = ["digest"]
    if writes_section:
        props["section_markdown"] = {
            "type": "string",
            "description": "Your section(s) as Markdown, starting at your first heading. No preamble.",
        }
        required = ["section_markdown", "digest"]
    return ToolSpec(
        name=SUBMIT_NAME,
        description="Submit your finished work. Call EXACTLY ONCE, at the end. The engine writes the files.",
        input_schema={"type": "object", "properties": props, "required": required},
    )
