"""The generic, brief-driven agent executor.

One code path runs *every* LLM agent. It composes the system prompt + the agent's brief + shared
preamble + engagement params + upstream digests, exposes the right tool set, runs the tool-use
loop, and writes the agent's section + fragment from its terminal ``submit_section`` call. This is
what makes "port all Tier-0..Tier-4 agents" tractable: the agents differ only by their brief.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from ..blueprint.loader import Blueprint
from ..blueprint.stages import AgentSpec
from ..logging import EventEmitter, get_logger
from ..models.config import Config
from ..providers.router import ProviderRouter
from ..tools.registry import RECONCILE_TOOLS, RESEARCH_TOOLS, ToolRegistry
from .schemas import SUBMIT_NAME, submit_spec

log = get_logger()

_USER_TEMPLATE = """You are agent "{label}" in the Vantage engine (dossier blueprint v3.0.0).

Your BRIEF below is authoritative for your scope. You may read shared contracts on demand with the
read_file tool (paths resolve against the harness): blueprint/vantage-blueprint-v3.md,
blueprint/evidence-policy.md, blueprint/section-contracts.md, blueprint/jurisdiction-adapters.md,
blueprint/tooling-map.md, blueprint/scoring-rubrics.md, blueprint/vertical-modules.md,
blueprint/verification-protocol.md, prompts/id-allocation.md, state/state.schema.json.
Run artifacts from earlier steps (when they exist): sections/*.md, state/state.json,
state/precomputed-financials.json, state/fragments/*.json, qa/evidence-audit.json.

=== EVIDENCE POLICY (status, confidence, corroboration, negative evidence) ===
{evidence_policy}

=== COMMON PREAMBLE ===
{common}

=== YOUR BRIEF ({brief_file}) ===
{brief}

=== ENGAGEMENT PARAMETERS ===
{params}
{upstream}{extra}
When finished, call {submit} EXACTLY ONCE. Research with the provided tools first; cite only what
you retrieve. Do not write files yourself — the engine writes them from your {submit} call.
Stay inside your id-allocation block; if you write no section, omit section_markdown.
"""


@dataclass
class AgentResult:
    label: str
    digest: str = ""
    structured: dict | None = None
    usage: dict = field(default_factory=lambda: {"input_tokens": 0, "output_tokens": 0})
    section_path: str | None = None
    fragment: dict = field(default_factory=dict)
    error: str | None = None
    iters: int = 0


def _tool_names(spec: AgentSpec) -> list[str]:
    """Research agents get the full toolset; reconcile and synthesis agents read artifacts only.

    §18-§21 are synthesis over what the body established. Handing them web search invites the
    exact behaviour ``exec-brief`` and ``methodology`` are forbidden from: researching past a gap
    instead of reporting it.
    """
    return list(RESEARCH_TOOLS if spec.researches else RECONCILE_TOOLS)


def build_agent_prompt(
    spec: AgentSpec,
    blueprint: Blueprint,
    params_text: str,
    upstream_text: str = "",
    extra_text: str = "",
) -> tuple[str, str]:
    """Compose the (system, user) prompt for an agent. Shared by the api and agent-sdk backends."""
    system = blueprint.system_prompt()
    user = _USER_TEMPLATE.format(
        label=spec.label,
        common=blueprint.common(),
        evidence_policy=blueprint.evidence_policy(),
        brief_file=spec.brief,
        brief=blueprint.brief(spec.brief),
        params=params_text,
        upstream=f"\n=== UPSTREAM CONTEXT ===\n{upstream_text}\n" if upstream_text else "",
        extra=f"\n=== STAGE NOTES ===\n{extra_text}\n" if extra_text else "",
        submit=SUBMIT_NAME,
    )
    return system, user


async def run_agent(
    spec: AgentSpec,
    *,
    cfg: Config,
    router: ProviderRouter,
    blueprint: Blueprint,
    run_dir: Path,
    harness_dir: Path,
    params_text: str,
    upstream_text: str = "",
    extra_text: str = "",
    emitter: EventEmitter | None = None,
) -> AgentResult:
    result = AgentResult(label=spec.label)
    try:
        provider, model = router.for_role(spec.label)
    except Exception as e:
        result.error = f"provider unavailable: {e}"
        return result

    registry = ToolRegistry(cfg, run_dir, harness_dir)
    tool_names = [n for n in _tool_names(spec) if registry.has(n)]
    writes_section = spec.out is not None
    tool_specs = registry.specs(tool_names) + [submit_spec(writes_section)]

    system, user = build_agent_prompt(spec, blueprint, params_text, upstream_text, extra_text)
    messages: list[dict] = [{"role": "user", "content": [{"type": "text", "text": user}]}]

    ref = cfg.model_for_role(spec.label)
    thinking = cfg.models.thinking.model_dump()
    if ref.effort:
        thinking["effort"] = ref.effort
    submitted: dict | None = None
    for i in range(cfg.engine.max_iterations):
        result.iters = i + 1
        try:
            turn = await provider.complete(
                system=system,
                messages=messages,
                tools=tool_specs,
                model=model,
                temperature=ref.temperature if ref.temperature is not None else cfg.models.temperature,
                max_tokens=ref.max_tokens or cfg.models.max_tokens,
                thinking=thinking,
            )
        except Exception as e:
            result.error = f"llm error: {e}"
            return result

        result.usage["input_tokens"] += turn.usage.get("input_tokens", 0)
        result.usage["output_tokens"] += turn.usage.get("output_tokens", 0)

        assistant_content: list[dict] = []
        if turn.text:
            assistant_content.append({"type": "text", "text": turn.text})
        for tc in turn.tool_calls:
            assistant_content.append({"type": "tool_use", "id": tc.id, "name": tc.name, "input": tc.input})
        assistant = {"role": "assistant", "content": turn.content or assistant_content}
        if turn.provider_content is not None:
            assistant["provider_content"] = turn.provider_content
        messages.append(assistant)

        submit_call = next((tc for tc in turn.tool_calls if tc.name == SUBMIT_NAME), None)
        if submit_call is not None:
            submitted = submit_call.input
            break

        if not turn.tool_calls:
            # finished without submitting — nudge once, then give up gracefully
            if i < cfg.engine.max_iterations - 1:
                messages.append({"role": "user", "content": [{"type": "text",
                    "text": f"Call {SUBMIT_NAME} now with your section, fragment, and digest."}]})
                continue
            submitted = {"section_markdown": turn.text, "digest": turn.text[:1200]}
            break

        # execute non-submit tool calls
        results_blocks = []
        for tc in turn.tool_calls:
            if emitter:
                emitter.event("agent_tool", stage=spec.step, agent=spec.label,
                              message=tc.name, data={"args": _short(tc.input)})
            out = await registry.run(tc.name, tc.input)
            results_blocks.append({
                "type": "tool_result",
                "tool_use_id": tc.id,
                "content": out[:cfg.engine.tool_result_max_chars],
            })
        messages.append({"role": "user", "content": results_blocks})

    if submitted is None:
        result.error = "agent did not submit within iteration budget"
        return result

    _write_outputs(spec, submitted, run_dir)
    result.digest = (submitted.get("digest") or "").strip()
    result.structured = submitted.get("structured")
    result.fragment = submitted.get("fragment") or {}
    if writes_section and spec.out:
        result.section_path = f"sections/{spec.out}"
    return result


def _write_outputs(spec: AgentSpec, submitted: dict, run_dir: Path) -> None:
    (run_dir / "sections").mkdir(parents=True, exist_ok=True)
    (run_dir / "state" / "fragments").mkdir(parents=True, exist_ok=True)

    if spec.out and submitted.get("section_markdown"):
        (run_dir / "sections" / spec.out).write_text(submitted["section_markdown"], encoding="utf-8")

    for f in submitted.get("files", []) or []:
        try:
            rel = f["path"].lstrip("/")
            dest = (run_dir / rel).resolve()
            if not str(dest).startswith(str(run_dir.resolve())):
                continue  # never escape the run dir
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(f["content"], encoding="utf-8")
        except Exception:  # pragma: no cover
            continue

    fragment = submitted.get("fragment") or {}
    if not isinstance(fragment, dict):
        fragment = {}
    fragment.setdefault("agent", spec.label)
    (run_dir / "state" / "fragments" / f"{spec.label}.json").write_text(
        json.dumps(fragment, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def _short(obj: dict) -> dict:
    out = {}
    for k, v in list(obj.items())[:4]:
        s = str(v)
        out[k] = s[:80]
    return out
