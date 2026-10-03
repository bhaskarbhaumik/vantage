"""The step orchestrator — runs the P0→P8 DAG with per-step concurrency.

Exposes a step-level lifecycle (``prepare`` → ``execute_step`` → ``finalize``) so the framework
backends (LangGraph/ADK/CrewAI) can drive the identical pipeline node-by-node, and a convenience
``run`` that executes the whole plan. The per-agent *runner* is injectable, so the agent-sdk
backend swaps only how one agent is executed.

Two steps are deterministic Python rather than LLM agents, because collation must be exact and
reproducible: ``source-merge`` (P4a) and ``assembly`` (P8b).
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from pathlib import Path

from ..agents.executor import AgentResult, run_agent
from ..blueprint.loader import Blueprint
from ..blueprint.stages import (
    AGENTS,
    DEFAULT_TIER,
    TIERS,
    WAVE_B_DEPENDS,
    Step,
    build_plan,
    id_blocks,
)
from ..logging import EventEmitter, get_logger
from ..models.config import Config
from ..providers.router import ProviderRouter
from ..render.assembly import assemble
from .merge import merge_fragments

log = get_logger()

Runner = Callable[..., Awaitable[AgentResult]]

_NEUTRAL_NOTE = (
    "§3-§17 ARE VENDOR-NEUTRAL. Promotional references to the pursuing organization must not appear in your output. "
    "V7a is a BLOCKER. The single exception in the whole range is §15.6, owned by ai-readiness."
)


@dataclass
class RunJob:
    client_legal_name: str
    slug: str
    research_as_of: str
    client_common_name: str = ""
    ticker_or_private: str = "AUTO-DETECT"
    primary_geography: str = "AUTO-DETECT"
    target_vertical: str = "AUTO-DETECT"
    #: EXECUTIVE | STANDARD | FULL_ANNEX (blueprint §4)
    tier: str = DEFAULT_TIER
    #: Gated inputs. Without these, every organization capability/relationship field renders its marker.
    capability_pack: str = "NOT_ATTACHED"
    account_team_input_sheet: str = "NOT_ATTACHED"
    account_context: str = "NONE"
    known_relationship_context: str = "NONE"
    strategic_pursuit_objectives: str = "NONE"


@dataclass
class RunResult:
    slug: str
    run_dir: str
    dossier: str | None = None
    entity: dict = field(default_factory=dict)
    ownership_form: str = ""
    jurisdictions: list[str] = field(default_factory=list)
    vertical_module: str = "NONE"
    vertical_confidence: str = ""
    entity_ambiguity: str | None = None
    agents_ok: int = 0
    agents_total: int = 0
    verification: dict | None = None
    usage: dict = field(default_factory=lambda: {"input_tokens": 0, "output_tokens": 0})
    errors: list[str] = field(default_factory=list)


@dataclass
class RunContext:
    job: RunJob
    run_dir: Path
    params: str
    base_state: dict
    digests: dict[str, str]
    upstream: str
    result: RunResult
    plan: list[Step]
    aborted: bool = False


class Orchestrator:
    def __init__(
        self,
        cfg: Config,
        blueprint: Blueprint,
        harness_dir: Path,
        *,
        runner: Runner = run_agent,
        emitter: EventEmitter | None = None,
    ) -> None:
        self.cfg = cfg
        self.bp = blueprint
        self.harness_dir = harness_dir
        self.runner = runner
        self.emitter = emitter or EventEmitter()
        self.router = ProviderRouter(cfg)
        self._sem = asyncio.Semaphore(cfg.engine.max_concurrency)

    # -- helpers ---------------------------------------------------------------
    def _params(self, job: RunJob, run_dir: Path) -> str:
        return "\n".join([
            "== ENGAGEMENT PARAMETERS ==",
            f"CLIENT_LEGAL_NAME:        {job.client_legal_name}",
            f"CLIENT_COMMON_NAME:       {job.client_common_name or job.client_legal_name}",
            f"TICKER_OR_PRIVATE_STATUS: {job.ticker_or_private}",
            f"PRIMARY_GEOGRAPHY:        {job.primary_geography}",
            f"TARGET_VERTICAL:          {job.target_vertical}",
            f"RESEARCH_AS_OF_DATE:      {job.research_as_of}",
            f"OUTPUT_TIER:              {job.tier}",
            f"RUN_DIR:                  {run_dir}",
            f"HARNESS_DIR:              {self.harness_dir}",
            "",
            "== GATED INPUTS (sole permitted basis for any organization content) ==",
            f"CAPABILITY_PACK:          {job.capability_pack}",
            f"ACCOUNT_TEAM_INPUT_SHEET:     {job.account_team_input_sheet}",
            f"ACCOUNT_CONTEXT:          {job.account_context}",
            f"KNOWN_RELATIONSHIP_CONTEXT:   {job.known_relationship_context}",
            f"STRATEGIC_PURSUIT_OBJECTIVES: {job.strategic_pursuit_objectives}",
        ])

    def _step_notes(self, label: str, ctx: RunContext) -> str:
        """Per-agent notes that mirror the Workflow backend's step notes."""
        spec = AGENTS[label]
        notes: list[str] = []
        if spec.out:
            notes.append(f"Your section file is sections/{spec.out}; your fragment is "
                         f"state/fragments/{label}.json. The engine writes both from your submit call.")
        if dep := WAVE_B_DEPENDS.get(label):
            notes.append(f"You depend on {dep} — READ IT FROM DISK under {ctx.run_dir}/sections/ "
                         "before you start. Do not re-research what it established; cite its claim IDs.")
        if spec.neutral:
            notes.append(_NEUTRAL_NOTE)
        if spec.mints:
            notes.append(f"You are the SOLE minter of {', '.join(spec.mints)}. No other agent may "
                         "create these IDs, and you may not create any other agent's.")
        if label == "opportunity":
            notes.append(
                "The refuted-claim list in qa/evidence-audit.json is BINDING: no O-nn may cite a "
                "refuted claim as need evidence (V3f, BLOCKER). "
                f"Capability Pack is {ctx.job.capability_pack} and Account-Team Input Sheet is "
                f"{ctx.job.account_team_input_sheet} — without them, every capability claim reads "
                "[INTERNAL: validate with practice] and every win-probability field reads "
                "[INTERNAL REQUIRED].")
        if label == "exec-brief":
            notes.append(
                "NO NEW RESEARCH, NO NEW SOURCES (V8c). Every §1 statement carries a "
                "C-/O-/R-/A-/P-/G- reference (V8a, BLOCKER). §1.3 must be consistent with the §1.6 "
                "readiness band (V8d, BLOCKER). A carry_forward_fact marked contested is NOT stated "
                "in §1.1 — write \"contested, see §21.11\".")
            if ctx.job.account_team_input_sheet == "NOT_ATTACHED":
                notes.append("§1.6 Stakeholder Access is NOT ASSESSED and the remaining five weights "
                             "renormalize from 90% to 100% — SHOW THE RENORMALIZATION (V5c, BLOCKER).")
        if label == "verification":
            notes.append(
                "You are running with FRESH CONTEXT and did not write this dossier. The digests above "
                "are context only — verify against the ARTEFACTS on disk, not against these claims "
                "about them. Execute blueprint/verification-protocol.md V1-V12 in full.")
        if ctx.job.tier == "EXECUTIVE" and spec.neutral:
            notes.append("EXECUTIVE tier: research only what §1 consumes. Envelopes are ~0.4x. "
                         "Skip Opt subsections entirely.")
        return "\n\n".join(notes)

    async def _run_one(self, label: str, ctx: RunContext, upstream: str) -> AgentResult:
        spec = AGENTS[label]
        self.emitter.event("agent_start", stage=spec.step, agent=label)
        async with self._sem:
            res = await self.runner(
                spec, cfg=self.cfg, router=self.router, blueprint=self.bp, run_dir=ctx.run_dir,
                harness_dir=self.harness_dir, params_text=ctx.params, upstream_text=upstream,
                extra_text=self._step_notes(label, ctx), emitter=self.emitter,
            )
        if res.error:
            self.emitter.event("agent_error", stage=spec.step, agent=label, message=res.error)
        else:
            self.emitter.event("agent_done", stage=spec.step, agent=label,
                               data={"iters": res.iters, "usage": res.usage})
        return res

    # -- lifecycle -------------------------------------------------------------
    async def prepare(self, job: RunJob) -> RunContext:
        tier = (job.tier or DEFAULT_TIER).upper()
        if tier not in TIERS:
            tier = DEFAULT_TIER
        job.tier = tier

        run_dir = Path(self.cfg.engine.output_dir).expanduser() / job.slug
        for sub in ("sections", "state/fragments", "qa"):
            (run_dir / sub).mkdir(parents=True, exist_ok=True)
        result = RunResult(slug=job.slug, run_dir=str(run_dir))
        params = self._params(job, run_dir)

        # Seed state with the run contract and the id-allocation table (so V1c is checkable).
        base_state = {
            "schema_version": "3.0",
            "id_blocks": id_blocks(),
            "run_contract": {
                "target": job.client_legal_name,
                "entity": {"legal_name": job.client_legal_name,
                           "common_name": job.client_common_name or job.client_legal_name},
                "tier": tier,
                "as_of": job.research_as_of,
                "capability_pack": job.capability_pack,
                "account_team_input_sheet": job.account_team_input_sheet,
            },
        }
        ctx = RunContext(job, run_dir, params, base_state, {}, "", result, plan=[])

        self.emitter.event("run_start", message=job.client_legal_name,
                           data={"slug": job.slug, "backend": self.cfg.engine.backend, "tier": tier})

        # P0 — preflight is a hard gate. Nothing downstream can run without §0.
        self.emitter.event("stage_start", stage="P0 Preflight")
        pre = await self._run_one("preflight", ctx, "")
        result.agents_total += 1
        _acc_usage(result, pre)
        if pre.error:
            result.errors.append(f"preflight: {pre.error}")
            self.emitter.event("run_error", message=f"preflight failed: {pre.error}")
            ctx.aborted = True
            return ctx

        result.agents_ok += 1
        st = pre.structured or {}
        result.entity = {
            "legal_name": st.get("legal_name") or job.client_legal_name,
            "ticker": st.get("ticker"), "lei": st.get("lei"), "cik": st.get("cik"),
        }
        result.ownership_form = st.get("ownership_form", "public")
        result.jurisdictions = st.get("jurisdictions") or ["generic"]
        result.vertical_module = st.get("vertical_primary", "NONE")
        result.vertical_confidence = st.get("vertical_confidence", "Low")
        result.entity_ambiguity = st.get("entity_ambiguity")

        base_state["run_contract"].update({
            "entity": {**base_state["run_contract"]["entity"], **{
                k: v for k, v in {
                    "legal_name": st.get("legal_name"), "ticker": st.get("ticker"),
                    "lei": st.get("lei"), "cik": st.get("cik"), "fy_end": st.get("fy_end"),
                    "latest_fy_label": st.get("latest_fy_label"),
                    "ambiguity": st.get("entity_ambiguity"),
                }.items() if v}},
            "ownership_form": result.ownership_form,
            "jurisdictions": result.jurisdictions,
            "reporting_standard": st.get("reporting_standard"),
            "languages": st.get("languages") or ["en"],
            "verticals": {"primary": result.vertical_module,
                          "secondary": st.get("vertical_secondary") or [],
                          "confidence": result.vertical_confidence},
        })

        if result.entity_ambiguity:
            self.emitter.event("run_warning", stage="P0 Preflight",
                               message=f"entity ambiguity: {result.entity_ambiguity}")

        ctx.upstream = (
            f"From P0 (preflight): {result.entity['legal_name']}"
            f"{f' ({result.entity['ticker']})' if result.entity.get('ticker') else ''} · "
            f"ownership_form {result.ownership_form} · adapters "
            f"{', '.join(result.jurisdictions)} · vertical {result.vertical_module} "
            f"({result.vertical_confidence}) · tier {tier}. "
            f"Capability Pack {job.capability_pack} · Input Sheet {job.account_team_input_sheet}. "
            f"Run contract and backbone sources are in state/state.json — cite them, do not "
            f"re-register.\n\n{pre.digest}"
        )
        ctx.digests["preflight"] = pre.digest
        self.emitter.event("stage_done", stage="P0 Preflight")
        ctx.plan = build_plan(tier, result.vertical_module, result.vertical_confidence)
        return ctx

    async def execute_step(self, ctx: RunContext, step: Step) -> None:
        self.emitter.event("stage_start", stage=step.title, data={"agents": step.labels})

        # P4a — deterministic collation.
        if step.labels == ["source-merge"]:
            state = merge_fragments(ctx.run_dir, ctx.base_state,
                                    expected_labels=self._expected_labels(ctx))
            rep = state.merge_report
            msg = (f"{rep.get('sources_after_dedup', 0)} sources after dedup "
                   f"({rep.get('sources_retired', 0)} retired) · "
                   f"{len(rep.get('false_triangulation') or [])} false-triangulation downgrades · "
                   f"{len(rep.get('defects') or [])} defects recorded")
            ctx.digests["source-merge"] = msg
            if contested := state.contested_facts():
                self.emitter.event("run_warning", stage=step.title,
                                   message=f"contested canonical facts (omitted downstream): "
                                           f"{', '.join(contested)}")
            self.emitter.event("stage_done", stage=step.title, message=msg)
            return

        # P8b — deterministic assembly.
        if step.labels == ["assembly"]:
            state = merge_fragments(ctx.run_dir, ctx.base_state,
                                    expected_labels=self._expected_labels(ctx))
            # The verifier's structured return is authoritative for the title metadata; fold it in
            # so Overall Confidence is present even when its fragment omitted the block.
            if ctx.result.verification:
                state.verification = {**state.verification, **ctx.result.verification}
                state.save(ctx.run_dir / "state" / "state.json")
            dossier = assemble(
                ctx.run_dir, state, ctx.job.slug,
                client=ctx.job.client_legal_name, research_as_of=ctx.job.research_as_of,
                tier=ctx.job.tier, dossier_suffix=self.bp.dossier_suffix,
            )
            ctx.result.dossier = str(dossier)
            self.emitter.event("stage_done", stage=step.title, message=str(dossier))
            return

        upstream = ctx.upstream + _digest_block(ctx.digests, exclude={"preflight"})
        results = await asyncio.gather(*[self._run_one(lbl, ctx, upstream) for lbl in step.labels])

        missing: list[str] = []
        for lbl, res in zip(step.labels, results, strict=True):
            ctx.result.agents_total += 1
            _acc_usage(ctx.result, res)
            if res.error:
                ctx.result.errors.append(f"{lbl}: {res.error}")
                missing.append(lbl)
            else:
                ctx.result.agents_ok += 1
                ctx.digests[lbl] = res.digest
                if lbl == "verification" and res.structured:
                    ctx.result.verification = res.structured

        # A non-returning agent is named, never absorbed — V10e depends on knowing which.
        if missing:
            self.emitter.event("run_warning", stage=step.title,
                               message=f"no return from: {', '.join(missing)} "
                                       "(V10e will flag the missing fragments)")
        self.emitter.event("stage_done", stage=step.title)

    def _expected_labels(self, ctx: RunContext) -> list[str]:
        """Every agent the plan intended to run — the basis for the missing-fragment check."""
        return ["preflight"] + [lbl for s in ctx.plan[1:] for lbl in s.labels
                                if lbl not in ("source-merge", "assembly")]

    def finalize(self, ctx: RunContext) -> RunResult:
        ver = ctx.result.verification or {}
        self.emitter.event("run_done", message=ctx.result.dossier or "(no dossier)",
                           data={"agents_ok": ctx.result.agents_ok,
                                 "agents_total": ctx.result.agents_total,
                                 "usage": ctx.result.usage,
                                 "verification": ver})
        if ver.get("overall_confidence") == "Insufficient":
            self.emitter.event("run_warning",
                               message="Overall Confidence Insufficient — do not present. "
                                       "Re-run with better sources or reduce scope.")
        if topics := (ver.get("budget_limited_topics") or []):
            self.emitter.event("run_warning",
                               message="stopped on budget (not diminishing returns): "
                                       + ", ".join(topics)
                                       + " — extending the budget and re-running these would "
                                         "materially improve coverage")
        return ctx.result

    async def run(self, job: RunJob) -> RunResult:
        ctx = await self.prepare(job)
        if ctx.aborted:
            return ctx.result
        for step in ctx.plan[1:]:  # plan[0] is P0, already run in prepare()
            await self.execute_step(ctx, step)
        return self.finalize(ctx)


def _acc_usage(result: RunResult, res: AgentResult) -> None:
    result.usage["input_tokens"] += res.usage.get("input_tokens", 0)
    result.usage["output_tokens"] += res.usage.get("output_tokens", 0)


def _digest_block(digests: dict[str, str], exclude: set[str]) -> str:
    items = [f"--- {k} ---\n{v}" for k, v in digests.items() if k not in exclude and v]
    return ("\n\n== UPSTREAM AGENT DIGESTS ==\n" + "\n\n".join(items)) if items else ""
