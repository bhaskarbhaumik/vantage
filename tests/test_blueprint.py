from vantage.blueprint import AGENTS, Blueprint, build_plan
from vantage.blueprint.stages import WAVE_A, WAVE_B, id_blocks
from vantage.settings import harness_dir, load_config


def test_blueprint_loads():
    bp = Blueprint(harness_dir(load_config()))
    assert "VANTAGE-ANALYST v3" in bp.system_prompt()
    assert len(bp.brief("00-preflight.md")) > 500
    assert bp.state_schema()["properties"]["schema_version"]["const"] == "3.0"
    # The v3 reference set every agent may consult.
    assert set(bp.reference_docs()) == {
        "blueprint", "evidence_policy", "section_contracts", "id_allocation",
        "jurisdiction_adapters", "tooling_map", "scoring_rubrics",
        "vertical_modules", "verification_protocol",
    }


def test_every_agent_brief_exists():
    bp = Blueprint(harness_dir(load_config()))
    for spec in AGENTS.values():
        assert len(bp.brief(spec.brief)) > 400, f"{spec.label} brief is missing or a stub"


def test_single_owner_registers_assigned_once():
    flat = [m for spec in AGENTS.values() for m in spec.mints]
    assert sorted(flat) == sorted(set(flat)), "a register is minted by two agents"
    assert set(flat) == {"P-", "R-", "U-", "O-", "A-", "X-"}


def test_id_blocks_are_disjoint():
    blocks = sorted((b["block_start"], b["block_end"], label)
                    for label, b in id_blocks().items())
    for (_, end_a, a), (start_b, _, b) in zip(blocks, blocks[1:], strict=False):
        assert end_a < start_b, f"{a} and {b} have overlapping ID blocks"


def test_body_sections_are_vendor_neutral_except_ai_readiness():
    """§3-§17 carry no the pursuing organization content. §15.6 is the one gated exception (V7a)."""
    body = {str(n) for n in range(3, 18)}
    for spec in AGENTS.values():
        if body & set(spec.sections):
            expected_neutral = spec.label != "ai-readiness"
            assert spec.neutral is expected_neutral, spec.label


def test_synthesis_agents_do_not_research():
    """§18-§21 are synthesis over what the body established, so they get no web tools."""
    for label in ("opportunity", "account-strategy", "playbook", "exec-brief",
                  "methodology", "verification", "appendices", "assembly",
                  "source-merge", "contradiction", "evidence-audit"):
        assert AGENTS[label].researches is False, label


def test_plan_full_annex():
    plan = build_plan("FULL_ANNEX", "V-BFSI", "High")
    labels = [lbl for s in plan for lbl in s.labels]
    assert labels[0] == "preflight" and labels[1] == "backbone"
    assert labels[-1] == "assembly"
    assert set(WAVE_A) | set(WAVE_B) <= set(labels)
    assert "vertical" in labels
    # §1 is written last: exec-brief must follow every body and pursuit agent.
    assert labels.index("exec-brief") > labels.index("playbook")
    # The adversarial audit runs BEFORE §18, so a refuted claim cannot become an opportunity.
    assert labels.index("evidence-audit") < labels.index("opportunity")
    # source-merge precedes the sweep and the audit, which both read merged state.
    assert labels.index("source-merge") < labels.index("contradiction")


def test_plan_executive_tier_skips_wave_b():
    labels = [lbl for s in build_plan("EXECUTIVE", "V-BFSI", "High") for lbl in s.labels]
    assert not set(WAVE_B) & set(labels)
    assert "vertical" not in labels
    assert {"preflight", "exec-brief", "verification", "assembly"} <= set(labels)


def test_low_vertical_confidence_drops_the_module():
    labels = [lbl for s in build_plan("FULL_ANNEX", "V-BFSI", "Low") for lbl in s.labels]
    assert "vertical" not in labels
    labels = [lbl for s in build_plan("FULL_ANNEX", "NONE", "High") for lbl in s.labels]
    assert "vertical" not in labels
