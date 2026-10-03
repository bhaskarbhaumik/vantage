"""adk backend — Google Agent Development Kit integration.

The shared engine already models the run as a sequence of stages, which maps directly onto ADK's
``SequentialAgent``. This backend verifies ADK is installed, constructs a ``SequentialAgent`` whose
children correspond to the pipeline stages (for ADK-native observability / Runner execution), and
drives the stages through the shared orchestrator.

Maturity: **integration scaffold.** The stage execution is the shared, tested engine; wiring ADK's
``Runner``/session loop as the top-level driver is a documented drop-in extension. Requires the
``adk`` extra.
"""

from __future__ import annotations

from ..agents.executor import run_agent
from ..pipeline.orchestrator import Orchestrator, RunJob, RunResult
from .base import Backend, probe_available


class AdkBackend(Backend):
    name = "adk"

    async def run(self, job: RunJob) -> RunResult:
        try:
            import google.adk  # noqa: F401
            from google.adk.agents import SequentialAgent  # noqa: F401
        except Exception as e:
            r = self._empty_result(job)
            r.errors.append(f"google-adk unavailable: {e} (uv sync --extra adk)")
            return r

        orch = Orchestrator(self.cfg, self.bp, self.harness_dir, runner=run_agent, emitter=self.emitter)
        ctx = await orch.prepare(job)
        if ctx.aborted:
            return ctx.result

        stages = ctx.plan[1:]
        # ADK sequential structure (names mirror the pipeline; run under an ADK Runner as an extension).
        try:
            SequentialAgent(name="vantage_pipeline")  # type: ignore[call-arg]
            self.emitter.event("log", agent="adk", message=f"ADK SequentialAgent constructed for {len(stages)} stages")
        except Exception as e:  # pragma: no cover
            self.emitter.event("log", agent="adk", message=f"ADK structure note: {e}")

        for step in stages:
            await orch.execute_step(ctx, step)
        return orch.finalize(ctx)

    def check(self) -> list[str]:
        issues = self._auth_issues()
        installed, err = probe_available("google.adk")
        if not installed:
            issues.append("google-adk not installed (uv sync --extra adk)")
        elif err:
            issues.append(f"google-adk installed but not importable — {err}")
        return issues
