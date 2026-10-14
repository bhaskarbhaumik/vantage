"""P7R owner remediation in the Claude Code Workflow script.

The workflow is JavaScript, so these tests run it under Node with every Workflow global stubbed
(tests/workflow_driver.mjs) and assert on the agent calls it makes. No model is called.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = ROOT / "harness" / "workflows" / "vantage-v3.workflow.mjs"
DRIVER = ROOT / "tests" / "workflow_driver.mjs"

pytestmark = pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")

FAILING = {"result": "FAIL", "blockers": 4, "majors": 5, "minors": 0, "eqi": 57.0,
           "overall_confidence": "Thin", "digest": "first pass"}
IMPROVED = {"result": "PASS WITH DISCLOSURES", "blockers": 1, "majors": 3, "minors": 0,
            "eqi": 62.0, "overall_confidence": "Thin", "digest": "second pass"}


def _finding(fid: str, loc: str) -> dict:
    return {"finding_id": fid, "check": "V5a", "severity": "BLOCKER", "locations": [loc],
            "defect": "qualifier lost", "required_outcome": "carry the audited status"}


ROUTER = {
    "orders": [
        # Deliberately out of dependency order: the workflow must sort by tier, not trust the router.
        {"owner": "exec-brief", "findings": [_finding("VR-02", "§1.2 #6")]},
        {"owner": "technology", "fetch_budget": 2, "findings": [_finding("VR-01", "§8.2")]},
        {"owner": "contradiction", "findings": [_finding("VR-03", "§21.11")]},
        {"owner": "opportunity", "findings": [_finding("VR-02", "T-18.1.3")]},
        {"owner": "vendors", "findings": [_finding("VR-01", "§16.2")]},
    ],
    "unroutable": [{"finding_id": "VR-05", "reason": "needs a document nobody retrieved"}],
    "digest": "routed",
}


def run(tmp_path: Path, scenario: dict) -> dict:
    sc = tmp_path / "scenario.json"
    sc.write_text(json.dumps(scenario))
    out = subprocess.run(["node", str(DRIVER), str(WORKFLOW), str(sc)],
                         capture_output=True, text=True, timeout=60)
    if out.returncode:
        raise RuntimeError(out.stderr)
    return json.loads(out.stdout)


def labels(res: dict) -> list[str]:
    return [c["label"] for c in res["calls"]]


def after_first_verification(res: dict) -> list[str]:
    ls = labels(res)
    return ls[ls.index("verification") + 1:]


def test_clean_verification_skips_remediation(tmp_path):
    res = run(tmp_path, {})
    assert after_first_verification(res) == ["appendices", "state-remerge-P7", "assembly"]
    assert res["result"]["remediation"] == []
    assert "Owner remediation" not in res["calls"][-1]["prompt"]


def test_blockers_are_routed_to_owners_in_dependency_order(tmp_path):
    res = run(tmp_path, {"verifications": [FAILING, IMPROVED], "router": ROUTER})
    assert after_first_verification(res) == [
        "remediation-router-r1",
        "contradiction-r1",                 # tier 0: registers, so body owners can cite new X-nnnn
        "technology-r1", "vendors-r1",      # tier 1: body, concurrent
        "state-remerge-R1a",                # once, before synthesis reads state
        "opportunity-r1",                   # tier 2: §18
        "account-strategy-r1", "playbook-r1",  # tier 3: re-sync only, no finding names them
        "exec-brief-r1", "methodology-r1",  # tier 4: §1 (order + re-sync), §2 (re-sync)
        "state-remerge-R1",
        "verification-r1",
        "appendices", "state-remerge-P7", "assembly",
    ]


def test_owner_prompt_carries_its_own_order_and_files_only(tmp_path):
    res = run(tmp_path, {"verifications": [FAILING, IMPROVED], "router": ROUTER})
    prompt = next(c["prompt"] for c in res["calls"] if c["label"] == "technology-r1")
    assert "prompts/briefs/06-technology.md" in prompt, "owner must re-read its own brief"
    assert "26b-remediation-pass.md" in prompt
    assert "sections/08-technology.md" in prompt
    assert "Fetch budget for this pass: 2" in prompt
    assert "[VR-01] V5a BLOCKER" in prompt and "§8.2" in prompt
    assert "T-18.1.3" not in prompt, "another owner's location leaked into this order"


def test_final_verification_is_the_re_verification(tmp_path):
    res = run(tmp_path, {"verifications": [FAILING, IMPROVED], "router": ROUTER})
    r = res["result"]
    assert r["verification"]["blockers"] == 1
    assert r["verification_initial"]["blockers"] == 4
    (rnd,) = r["remediation"]
    assert rnd["before"]["blockers"] == 4 and rnd["after"]["blockers"] == 1
    assert rnd["unroutable"] == ROUTER["unroutable"]

    reverify = next(c for c in res["calls"] if c["label"] == "verification-r1")
    assert reverify["has_schema"]
    assert 'phase_completed: "R1"' in reverify["prompt"]
    assert "RE-VERIFICATION, round 1" in reverify["prompt"]
    assert "Owner remediation (P7R): round 1 4B → 1B" in res["calls"][-1]["prompt"]


def test_first_verification_prompt_is_unchanged_by_the_loop(tmp_path):
    """The first pass must not know about P7R, so resumed runs replay it from cache."""
    res = run(tmp_path, {"verifications": [FAILING, IMPROVED], "router": ROUTER})
    first = next(c["prompt"] for c in res["calls"] if c["label"] == "verification")
    assert 'phase_completed: "P6"' in first
    assert "RE-VERIFICATION" not in first
    assert "26b-remediation-pass" not in first


def test_every_call_is_unique_so_resume_cannot_replay_the_wrong_one(tmp_path):
    still_failing = {**IMPROVED, "blockers": 2}
    res = run(tmp_path, {"args": {"remediation_rounds": 2},
                         "verifications": [FAILING, still_failing, IMPROVED], "router": ROUTER})
    ls = labels(res)
    assert "remediation-router-r2" in ls and "verification-r2" in ls
    assert len(ls) == len(set(ls)), [x for x in ls if ls.count(x) > 1]
    prompts = [c["prompt"] for c in res["calls"]]
    assert len(prompts) == len(set(prompts))
    assert [r["round"] for r in res["result"]["remediation"]] == [1, 2]


def test_rounds_stop_when_blockers_clear(tmp_path):
    cleared = {**IMPROVED, "blockers": 0}
    res = run(tmp_path, {"args": {"remediation_rounds": 2},
                         "verifications": [FAILING, cleared], "router": ROUTER})
    assert "remediation-router-r2" not in labels(res)


def test_zero_rounds_disables_remediation(tmp_path):
    res = run(tmp_path, {"args": {"remediation_rounds": 0},
                         "verifications": [FAILING], "router": ROUTER})
    assert after_first_verification(res) == ["appendices", "state-remerge-P7", "assembly"]


@pytest.mark.parametrize("bad", [3, -1, "two"])
def test_invalid_rounds_are_rejected(tmp_path, bad):
    with pytest.raises(RuntimeError, match="remediation_rounds"):
        run(tmp_path, {"args": {"remediation_rounds": bad}})


def test_router_failure_leaves_findings_disclosed(tmp_path):
    res = run(tmp_path, {"verifications": [FAILING], "router": None})
    assert after_first_verification(res) == [
        "remediation-router-r1", "appendices", "state-remerge-P7", "assembly"]
    assert res["result"]["verification"]["blockers"] == 4
    assert any("router returned nothing" in m for m in res["logs"])


def test_orders_for_agents_that_did_not_run_are_dropped_and_logged(tmp_path):
    """EXECUTIVE tier skips Wave B, so `vendors` has no section to revise."""
    res = run(tmp_path, {"args": {"output_tier": "EXECUTIVE"},
                         "verifications": [FAILING, IMPROVED], "router": ROUTER})
    ls = labels(res)
    assert "vendors-r1" not in ls and "technology-r1" in ls
    assert any('dropped an order for "vendors"' in m for m in res["logs"])
    router_call = next(c for c in res["calls"] if c["label"] == "remediation-router-r1")
    assert "vendors" not in router_call["schema"]["properties"]["orders"]["items"][
        "properties"]["owner"]["enum"]


def test_body_fixes_cascade_a_resync_to_every_downstream_synthesis_owner(tmp_path):
    """First proof run: §4/§8 were fixed but §18/§19/§1 kept the pre-fix values."""
    res = run(tmp_path, {"verifications": [FAILING, IMPROVED], "router": ROUTER})
    calls = {c["label"]: c["prompt"] for c in res["calls"]}

    resync_only = calls["account-strategy-r1"]
    assert "RE-SYNC" in resync_only and "YOUR WORK ORDER" not in resync_only
    assert "contradiction, technology, vendors, opportunity" in resync_only
    assert "exec-brief" not in resync_only.split("RE-SYNC")[1], "only upstream owners are listed"

    both = calls["exec-brief-r1"]
    assert "YOUR WORK ORDER (1 finding)" in both and "RE-SYNC" in both

    assert "RE-SYNC" not in calls["technology-r1"], "body owners are not re-synced"
    assert "methodology (re-sync)" in calls["verification-r1"]
    assert "methodology (re-sync)" in calls["state-remerge-R1"]
    owners = {o["owner"]: o for o in res["result"]["remediation"][0]["owners"]}
    assert owners["playbook"]["resync"] and owners["playbook"]["findings"] == []
    assert not owners["technology"]["resync"]


def test_no_cascade_when_only_the_last_tier_is_routed(tmp_path):
    router = {"orders": [{"owner": "exec-brief", "findings": [_finding("VR-02", "§1.2")]}],
              "unroutable": [], "digest": "routed"}
    res = run(tmp_path, {"verifications": [FAILING, IMPROVED], "router": router})
    assert after_first_verification(res)[:4] == [
        "remediation-router-r1", "exec-brief-r1", "state-remerge-R1", "verification-r1"]
    assert "RE-SYNC" not in next(c["prompt"] for c in res["calls"] if c["label"] == "exec-brief-r1")


def test_synthesis_order_cascades_only_to_later_synthesis_tiers(tmp_path):
    router = {"orders": [{"owner": "playbook", "findings": [_finding("VR-04", "§20.6 A-06")]}],
              "unroutable": [], "digest": "routed"}
    res = run(tmp_path, {"verifications": [FAILING, IMPROVED], "router": router})
    ls = after_first_verification(res)
    assert ls[:4] == ["remediation-router-r1", "playbook-r1", "exec-brief-r1", "methodology-r1"]
    assert "opportunity-r1" not in ls and "account-strategy-r1" not in ls
    assert "state-remerge-R1a" not in ls, "no body tier ran, so no mid-round merge"
