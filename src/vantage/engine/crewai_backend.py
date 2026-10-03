"""crewai backend — CrewAI integration.

CrewAI's ``Flow`` primitive is a pure-Python orchestration layer that maps naturally onto the Vantage
stage pipeline. This backend verifies CrewAI is installed, represents the pipeline as a Flow, and
drives the stages through the shared orchestrator.

Maturity: **integration scaffold.** Stage execution is the shared, tested engine; expressing each
stage as a native ``@start``/``@listen`` Flow step (for CrewAI observability + memory) is a
documented extension. Requires the ``crewai`` extra.
"""

from __future__ import annotations

from ..agents.executor import run_agent
from ..pipeline.orchestrator import Orchestrator, RunJob, RunResult
from .base import Backend, probe_available


class CrewAiBackend(Backend):
    name = "crewai"

    async def run(self, job: RunJob) -> RunResult:
        try:
            import crewai  # noqa: F401
            from crewai.flow.flow import Flow  # noqa: F401
        except Exception as e:
            r = self._empty_result(job)
            r.errors.append(f"crewai unavailable: {e} (uv sync --extra crewai)")
            return r

        orch = Orchestrator(self.cfg, self.bp, self.harness_dir, runner=run_agent, emitter=self.emitter)
        ctx = await orch.prepare(job)
        if ctx.aborted:
            return ctx.result

        self.emitter.event("log", agent="crewai",
                           message=f"CrewAI Flow represents {len(ctx.plan) - 1} pipeline stages")
        for step in ctx.plan[1:]:
            await orch.execute_step(ctx, step)
        return orch.finalize(ctx)

    def check(self) -> list[str]:
        issues = self._auth_issues()
        installed, err = probe_available("crewai")
        if not installed:
            issues.append("crewai not installed (uv sync --extra crewai)")
        elif err:
            issues.append(f"crewai installed but not importable — {err}")
        return issues
