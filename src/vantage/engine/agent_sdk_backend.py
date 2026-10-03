"""agent-sdk backend — runs each agent through the Claude Agent SDK, over the shared DAG.

Swaps only the per-agent *runner*: the orchestrator sequences stages exactly as the api backend
does, but each agent is executed by the Claude Agent SDK (its own tool loop) instead of the
engine's direct-API loop. Requires the ``agent-sdk`` extra.
"""

from __future__ import annotations

import json
import re

from ..agents.executor import AgentResult, build_agent_prompt
from ..agents.executor import _write_outputs as write_outputs
from ..pipeline.orchestrator import Orchestrator, RunJob, RunResult
from .base import Backend, probe_available

_JSON_OBJ = re.compile(r"\{.*\}", re.DOTALL)


def _extract_json(text: str) -> dict:
    m = _JSON_OBJ.search(text or "")
    if not m:
        return {"digest": (text or "")[:600]}
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return {"digest": (text or "")[:600]}


class AgentSdkBackend(Backend):
    name = "agent-sdk"

    async def run(self, job: RunJob) -> RunResult:
        orch = Orchestrator(self.cfg, self.bp, self.harness_dir, runner=self._runner, emitter=self.emitter)
        return await orch.run(job)

    async def _runner(self, spec, *, cfg, router, blueprint, run_dir, harness_dir,
                      params_text, upstream_text="", extra_text="", emitter=None) -> AgentResult:
        result = AgentResult(label=spec.label)
        try:
            from claude_agent_sdk import ClaudeAgentOptions, query
        except Exception as e:  # ImportError or version drift
            result.error = f"claude-agent-sdk unavailable: {e} (uv sync --extra agent-sdk)"
            return result

        system, user = build_agent_prompt(spec, blueprint, params_text, upstream_text, extra_text)
        user += (
            "\n\nIMPORTANT: instead of calling submit_section, end your turn by printing ONE JSON "
            "object with keys: section_markdown (string, omit if you write no section), fragment "
            "(object), digest (string <=200 words), structured (object, only if your brief defines "
            "one). Output only that JSON as your final message."
        )
        _, model = router.for_role(spec.label)
        try:
            options = ClaudeAgentOptions(system_prompt=system, model=model)
        except Exception:
            options = None

        text_parts: list[str] = []
        try:
            async for message in query(prompt=user, options=options):
                # SDK message objects expose text via .content blocks or .result; be tolerant
                for attr in ("result", "text"):
                    val = getattr(message, attr, None)
                    if isinstance(val, str):
                        text_parts.append(val)
                content = getattr(message, "content", None)
                if isinstance(content, list):
                    for block in content:
                        t = getattr(block, "text", None)
                        if isinstance(t, str):
                            text_parts.append(t)
        except Exception as e:
            result.error = f"agent-sdk run error: {e}"
            return result

        submitted = _extract_json("\n".join(text_parts))
        write_outputs(spec, submitted, run_dir)
        result.digest = (submitted.get("digest") or "").strip()
        result.structured = submitted.get("structured")
        result.fragment = submitted.get("fragment") or {}
        if spec.out:
            result.section_path = f"sections/{spec.out}"
        return result

    def check(self) -> list[str]:
        issues = self._auth_issues()
        installed, err = probe_available("claude_agent_sdk")
        if not installed:
            issues.append("claude-agent-sdk not installed (uv sync --extra agent-sdk)")
        elif err:
            issues.append(f"claude-agent-sdk installed but not importable — {err}")
        return issues
