"""End-to-end drive of the P0→P8 DAG with a mock runner.

Exercises the orchestrator's real sequencing, step notes, merge, and assembly without any LLM.
"""

import asyncio
import json
from pathlib import Path

import pytest

from vantage.agents.executor import AgentResult
from vantage.blueprint.loader import Blueprint
from vantage.blueprint.stages import AGENTS
from vantage.pipeline.orchestrator import Orchestrator, RunJob
from vantage.settings import harness_dir, load_config


def _mock_runner(calls, notes):
    async def runner(spec, *, run_dir, extra_text="", **kw):
        calls.append(spec.label)
        notes[spec.label] = extra_text
        (run_dir / "sections").mkdir(parents=True, exist_ok=True)
        (run_dir / "state" / "fragments").mkdir(parents=True, exist_ok=True)
        if spec.out:
            (run_dir / "sections" / spec.out).write_text(f"## {spec.label}\n\n> Verdict.")
        frag = {"agent": spec.label}
        if spec.block:
            frag["source_manifest"] = [{"id": f"S-{spec.block[0]:04d}",
                                        "url": f"https://x/{spec.label}",
                                        "minted_by": spec.label}]
        (run_dir / "state" / "fragments" / f"{spec.label}.json").write_text(json.dumps(frag))
        structured = None
        if spec.label == "preflight":
            structured = {"legal_name": "Acme Corp", "ownership_form": "public",
                          "jurisdictions": ["us-sec"], "vertical_primary": "V-MFG",
                          "vertical_confidence": "High", "cik": "0000123"}
        elif spec.label == "verification":
            structured = {"result": "PASS WITH DISCLOSURES", "overall_confidence": "Adequate",
                          "eqi": 71.4, "blockers": 0, "majors": 2, "minors": 1,
                          "budget_limited_topics": ["12.4", "17.1"]}
        return AgentResult(label=spec.label, digest=f"{spec.label} done", structured=structured,
                           fragment=frag)
    return runner


@pytest.fixture
def orch(tmp_path):
    cfg = load_config(overrides={"engine": {"output_dir": str(tmp_path)}})
    hd = harness_dir(cfg)
    calls, notes = [], {}
    o = Orchestrator(cfg, Blueprint(hd), hd, runner=_mock_runner(calls, notes))
    return o, calls, notes, tmp_path


def test_full_dag_runs_and_assembles(orch):
    o, calls, notes, tmp = orch
    result = asyncio.run(o.run(RunJob(client_legal_name="Acme Corp", slug="acme",
                                      research_as_of="2026-08-29", tier="FULL_ANNEX")))

    # Every LLM agent ran; source-merge and assembly are deterministic Python.
    assert set(calls) == set(AGENTS) - {"source-merge", "assembly"}
    assert calls[0] == "preflight" and calls[1] == "backbone"

    # Ordering invariants the design depends on.
    assert calls.index("evidence-audit") < calls.index("opportunity")   # audit before §18
    assert calls.index("playbook") < calls.index("exec-brief")          # §1 written last
    assert calls.index("verification") < calls.index("appendices")

    # The dossier name follows whichever harness is installed, so read it off the result
    # rather than hard-coding the brand.
    assert result.dossier and Path(result.dossier).exists()
    assert Path(result.dossier).name.startswith("acme-")
    text = Path(result.dossier).read_text()
    assert "**Overall Confidence:** Adequate (EQI 71.4)" in text
    assert "Acme Corp" in text and "CIK 0000123" in text
    assert result.agents_ok == result.agents_total == len(AGENTS) - 2


def test_step_notes_carry_the_binding_constraints(orch):
    o, calls, notes, _ = orch
    asyncio.run(o.run(RunJob(client_legal_name="Acme", slug="acme",
                             research_as_of="2026-08-29")))

    # Body agents are told the tier rule; ai-readiness is the §15.6 exception.
    assert "VENDOR-NEUTRAL" in notes["financials"]
    assert "VENDOR-NEUTRAL" not in notes["ai-readiness"]
    # Wave B agents are pointed at their dependency rather than left to re-research it.
    assert "§6 (financials)" in notes["competition"]
    # The refuted list is surfaced to §18 as binding.
    assert "BINDING" in notes["opportunity"] and "V3f" in notes["opportunity"]
    # Gated fields are surfaced where the Input Sheet is absent.
    assert "renormalize" in notes["exec-brief"].lower()
    # The verifier is told it did not write the dossier.
    assert "FRESH CONTEXT" in notes["verification"]
    # Sole minters are told so.
    assert "SOLE minter of P-" in notes["leadership"]


def test_preflight_failure_aborts_the_run(tmp_path):
    cfg = load_config(overrides={"engine": {"output_dir": str(tmp_path)}})
    hd = harness_dir(cfg)

    async def failing(spec, **kw):
        return AgentResult(label=spec.label, error="entity could not be resolved")

    o = Orchestrator(cfg, Blueprint(hd), hd, runner=failing)
    r = asyncio.run(o.run(RunJob(client_legal_name="Ambiguous Co", slug="amb",
                                 research_as_of="2026-08-29")))
    assert r.dossier is None
    assert r.errors and "preflight" in r.errors[0]
    assert r.agents_total == 1  # nothing downstream ran


def test_executive_tier_skips_wave_b(orch):
    o, calls, _, _ = orch
    asyncio.run(o.run(RunJob(client_legal_name="Acme", slug="acme",
                             research_as_of="2026-08-29", tier="EXECUTIVE")))
    assert "competition" not in calls and "vertical" not in calls
    assert {"preflight", "exec-brief", "verification"} <= set(calls)
