"""langgraph backend — a LangGraph StateGraph drives the shared stage pipeline.

Genuine framework wiring: one graph node per stage, linear edges, executed by LangGraph's async
runtime. Each node delegates to the orchestrator's ``execute_step`` (which uses the direct-API
agent runner). Requires the ``langgraph`` extra.
"""

from __future__ import annotations

from ..agents.executor import run_agent
from ..pipeline.orchestrator import Orchestrator, RunJob, RunResult
from .base import Backend, probe_available


class LangGraphBackend(Backend):
    name = "langgraph"

    async def run(self, job: RunJob) -> RunResult:
        try:
            from langgraph.graph import END, START, StateGraph
        except Exception as e:
            r = self._empty_result(job)
            r.errors.append(f"langgraph unavailable: {e} (uv sync --extra langgraph)")
            return r

        orch = Orchestrator(self.cfg, self.bp, self.harness_dir, runner=run_agent, emitter=self.emitter)
        ctx = await orch.prepare(job)
        if ctx.aborted:
            return ctx.result

        stages = ctx.plan[1:]

        def make_node(step):
            async def node(state: dict) -> dict:
                await orch.execute_step(ctx, step)
                return {"done": state.get("done", 0) + 1}

            return node

        graph = StateGraph(dict)
        prev = START
        for step in stages:
            node_name = step.id
            graph.add_node(node_name, make_node(step))
            graph.add_edge(prev, node_name)
            prev = node_name
        graph.add_edge(prev, END)

        app = graph.compile()
        await app.ainvoke({"done": 0})
        return orch.finalize(ctx)

    def check(self) -> list[str]:
        issues = self._auth_issues()
        installed, err = probe_available("langgraph")
        if not installed:
            issues.append("langgraph not installed (uv sync --extra langgraph)")
        elif err:
            issues.append(f"langgraph installed but not importable — {err}")
        return issues
