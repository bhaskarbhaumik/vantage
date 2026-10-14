"""The execution plan — agents, ID blocks, and the step DAG.

Mirrors ``harness/workflows/vantage-v3.workflow.mjs`` and ``prompts/id-allocation.md`` so the
programmatic backends (api/agent-sdk/langgraph/adk/crewai) run the identical pipeline the Claude
Code Workflow backend runs.

Phase mapping. ``aid-20260829.md`` specifies eight sequential phases. Phases 2-6 there are a
*dependency* ordering, not a concurrency constraint, so the harness collapses them into two
research waves: Wave A holds every body section with no intra-body dependency (ten agents), Wave B
holds the five that block on a Wave A output. Every phase-boundary persistence obligation is still
honoured at each wave end. Reconciliation runs before synthesis rather than at phase 8, because a
claim refuted after §18-§20 are written costs a rebuild of all three. See ``ARCHITECTURE.md``.

One known divergence: the workflow's P7R step (owner remediation after verification, briefs 26a
and 26b) is not mirrored here. ``remediation-router`` is deliberately absent from ``AGENTS``
because this roster is what the programmatic orchestrator runs, and it does not run P7R yet.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Output tiers, per blueprint §4.
TIERS = ("EXECUTIVE", "STANDARD", "FULL_ANNEX")
DEFAULT_TIER = "FULL_ANNEX"

VERTICAL_CODES = (
    "V-HLS", "V-BFSI", "V-RCG", "V-ENR", "V-MFG",
    "V-TMT", "V-TTH", "V-GOV", "V-AND", "V-REC", "V-PSE",
)


@dataclass(frozen=True)
class AgentSpec:
    label: str
    brief: str                       # filename under prompts/briefs/
    step: str                        # P0..P8
    out: str | None = None           # section markdown file under sections/
    block: tuple[int, int] | None = None
    sections: tuple[str, ...] = ()   # top-level sections owned
    neutral: bool = False            # §3-§17: promotional language about the pursuing organization is forbidden
    mints: tuple[str, ...] = ()      # single-owner registers this agent alone may mint
    researches: bool = True          # False -> reconcile/synthesis toolset, no web research


AGENTS: dict[str, AgentSpec] = {
    # --- P0/P1: gate and evidence layer -------------------------------------
    "preflight": AgentSpec(
        "preflight", "00-preflight.md", "P0", "00-run-contract.md", (0, 99), ("0",)),
    "backbone": AgentSpec(
        "backbone", "01-backbone.md", "P1", None, (100, 199)),

    # --- P2 Wave A: vendor-neutral body, no intra-body dependency --------------
    "corporate": AgentSpec(
        "corporate", "02-corporate.md", "P2", "03-company.md", (200, 299), ("3",), True),
    "market": AgentSpec(
        "market", "03-market.md", "P2", "04-market.md", (300, 399), ("4",), True),
    "business-model": AgentSpec(
        "business-model", "04-business-model.md", "P2", "05-business-model.md", (400, 499), ("5",), True),
    "financials": AgentSpec(
        "financials", "05-financials.md", "P2", "06-financials.md", (500, 599), ("6",), True),
    "technology": AgentSpec(
        "technology", "06-technology.md", "P2", "08-technology.md", (600, 699), ("8",), True),
    "strategy": AgentSpec(
        "strategy", "07-strategy.md", "P2", "09-strategy.md", (700, 799), ("9",), True),
    "leadership": AgentSpec(
        "leadership", "08-leadership.md", "P2", "10-leadership.md", (800, 899), ("10",), True, ("P-",)),
    "signals": AgentSpec(
        "signals", "09-signals.md", "P2", "13-signals.md", (900, 999), ("13",), True),
    "risk": AgentSpec(
        "risk", "10-risk.md", "P2", "14-risk.md", (1000, 1099), ("14",), True, ("R-",)),
    "esg": AgentSpec(
        "esg", "11-esg.md", "P2", "17-esg.md", (1100, 1199), ("17",), True),

    # --- P3 Wave B: body sections that block on a Wave A output -------------
    "operations": AgentSpec(
        "operations", "12-operations.md", "P3", "07-operations.md", (1200, 1299), ("7",), True),
    "competition": AgentSpec(
        "competition", "13-competition.md", "P3", "11-competition.md", (1300, 1399), ("11",), True),
    "customers": AgentSpec(
        "customers", "14-customers.md", "P3", "12-customers.md", (1400, 1499), ("12",), True),
    "ai-readiness": AgentSpec(
        # §15.6 the pursuing organization Engagement Fit is the one gated exception inside §3-§17, so not neutral.
        "ai-readiness", "15-ai-readiness.md", "P3", "15-ai-readiness.md", (1500, 1599), ("15",), False, ("U-",)),
    "vendors": AgentSpec(
        "vendors", "16-vendors.md", "P3", "16-vendors.md", (1600, 1699), ("16",), True),
    "vertical": AgentSpec(
        "vertical", "17-vertical.md", "P3", "21-vertical-annex.md", (1700, 1799), (), True),

    # --- P4 Reconcile -------------------------------------------------------
    "source-merge": AgentSpec(
        "source-merge", "18-source-merge.md", "P4", None, None, (), False, (), False),
    "contradiction": AgentSpec(
        "contradiction", "19-contradiction.md", "P4", "21-11-contradictions.md",
        (1900, 1999), (), False, ("X-",), False),
    "evidence-audit": AgentSpec(
        "evidence-audit", "20-evidence-audit.md", "P4", None, (2000, 2099), (), False, (), False),

    # --- P5 Synthesis (Tier 3) ---------------------------------------------
    "opportunity": AgentSpec(
        "opportunity", "21-opportunity.md", "P5", "18-opportunity.md",
        (2100, 2199), ("18",), False, ("O-",), False),
    "account-strategy": AgentSpec(
        "account-strategy", "22-account-strategy.md", "P5", "19-account-strategy.md",
        (2200, 2299), ("19",), False, (), False),
    "playbook": AgentSpec(
        "playbook", "23-playbook.md", "P5", "20-playbook.md",
        (2300, 2399), ("20",), False, ("A-",), False),

    # --- P6 Brief (written last, placed first) ------------------------------
    "exec-brief": AgentSpec(
        "exec-brief", "24-exec-brief.md", "P6", "01-exec-brief.md", (2400, 2499), ("1",), False, (), False),
    "methodology": AgentSpec(
        "methodology", "25-methodology.md", "P6", "02-methodology.md", (2500, 2599), ("2",), False, (), False),

    # --- P7/P8 Verification and assembly ------------------------------------
    "verification": AgentSpec(
        "verification", "26-verification.md", "P7", "21-8-verification.md",
        (2600, 2699), (), False, (), False),
    "appendices": AgentSpec(
        "appendices", "27-appendices.md", "P8", "21-appendices.md", (2700, 2799), (), False, (), False),
    "assembly": AgentSpec(
        "assembly", "28-assembly.md", "P8", None, None, (), False, (), False),
}

# Wave A — fully concurrent, no intra-body dependency.
WAVE_A = [
    "corporate", "market", "business-model", "financials", "technology",
    "strategy", "leadership", "signals", "risk", "esg",
]
# EXECUTIVE tier researches only what §1's synthesis consumes.
WAVE_A_EXECUTIVE = ["corporate", "financials", "technology", "strategy", "leadership", "risk"]

# Wave B — each blocks on a Wave A section.
WAVE_B = ["operations", "competition", "customers", "ai-readiness", "vendors"]

#: The section-wise deep-research agents — the ones that own a body section and go to the open web
#: for it. Everything else orchestrates, reconciles, or synthesises what these produced. The auth
#: layer keys its two credential profiles off this split (``config.auth.research`` vs
#: ``config.auth.orchestrator``), so the expensive research fan-out can run on a different
#: provider or key than the orchestrator.
SECTION_RESEARCH_AGENTS: tuple[str, ...] = tuple(WAVE_A + WAVE_B + ["vertical"])
ORCHESTRATOR_AGENTS: tuple[str, ...] = tuple(
    label for label in AGENTS if label not in SECTION_RESEARCH_AGENTS
)

# Wave B dependencies, surfaced to the agent so it reads rather than re-researches.
WAVE_B_DEPENDS: dict[str, str] = {
    "operations": "§5 (business-model)",
    "competition": "§6 (financials)",
    "customers": "§5 (business-model)",
    "ai-readiness": "§8 (technology), §7.5 (operations)",
    "vendors": "§8 (technology)",
}


@dataclass
class Step:
    id: str
    title: str
    labels: list[str] = field(default_factory=list)
    concurrent: bool = True


def build_plan(tier: str, vertical_module: str | None, vertical_confidence: str | None) -> list[Step]:
    """The P0..P8 DAG for one run. ``plan[0]`` is P0, already executed by ``Orchestrator.prepare``."""
    tier = (tier or DEFAULT_TIER).upper()
    if tier not in TIERS:
        tier = DEFAULT_TIER
    executive = tier == "EXECUTIVE"

    wave_a = WAVE_A_EXECUTIVE if executive else list(WAVE_A)

    # Vertical packets only help when a module was actually selected with usable confidence.
    run_vertical = (
        not executive
        and vertical_module not in (None, "NONE", "")
        and vertical_confidence != "Low"
    )
    wave_b = ([] if executive else list(WAVE_B) + (["vertical"] if run_vertical else []))

    steps = [
        Step("P0", "P0 Preflight", ["preflight"], concurrent=False),
        Step("P1", "P1 Backbone", ["backbone"], concurrent=False),
        Step("P2", "P2 Wave A", wave_a),
    ]
    if wave_b:
        steps.append(Step("P3", "P3 Wave B", wave_b))
    steps += [
        # source-merge runs alone first: the sweep and the audit both read merged state.
        Step("P4a", "P4 Merge", ["source-merge"], concurrent=False),
        Step("P4b", "P4 Reconcile", ["contradiction", "evidence-audit"]),
        # opportunity runs alone so §19/§20 have stable O-nn IDs to reference.
        Step("P5a", "P5 Opportunity", ["opportunity"], concurrent=False),
        Step("P5b", "P5 Pursuit", ["account-strategy", "playbook"]),
        Step("P6", "P6 Brief", ["exec-brief", "methodology"]),
        Step("P7", "P7 Verification", ["verification"], concurrent=False),
        Step("P8a", "P8 Appendices", ["appendices"], concurrent=False),
        Step("P8b", "P8 Assemble", ["assembly"], concurrent=False),
    ]
    return steps


def all_labels_in_plan(plan: list[Step]) -> list[str]:
    return [lbl for step in plan for lbl in step.labels]


def id_blocks() -> dict[str, dict]:
    """The id-allocation table as data, so the merged state can carry it for check V1c."""
    return {
        spec.label: {
            "block_start": spec.block[0],
            "block_end": spec.block[1],
            "sections": list(spec.sections),
            "mints": list(spec.mints),
        }
        for spec in AGENTS.values()
        if spec.block is not None
    }
