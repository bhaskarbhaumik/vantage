"""api backend — direct multi-provider API fan-out. The full headless engine."""

from __future__ import annotations

from ..agents.executor import run_agent
from ..pipeline.orchestrator import Orchestrator, RunJob, RunResult
from .base import Backend


class ApiBackend(Backend):
    name = "api"

    async def run(self, job: RunJob) -> RunResult:
        orch = Orchestrator(self.cfg, self.bp, self.harness_dir, runner=run_agent, emitter=self.emitter)
        return await orch.run(job)

    def check(self) -> list[str]:
        # auth.readiness already walks every provider the role map can route to, including the
        # per-class overrides in auth.orchestrator / auth.research.
        return sorted(set(self._auth_issues()))
