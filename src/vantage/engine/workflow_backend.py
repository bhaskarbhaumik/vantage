"""workflow backend (DEFAULT) — wraps the Claude Code Workflow harness.

Runs the bundled ``harness/workflows/vantage-v3.workflow.mjs`` through the Claude Code CLI in headless
print mode. This is the subscription path: no API key, agents research with Claude Code's built-in
web_search. It requires the ``claude`` CLI and a Claude subscription with the Workflow tool.
"""

from __future__ import annotations

import asyncio
import json
import os
import shutil

from ..settings import REPO_ROOT
from .base import Backend, RunJob, RunResult


class WorkflowBackend(Backend):
    name = "workflow"

    def _claude_cli(self) -> str:
        return os.environ.get("CLAUDE_CLI", "claude")

    async def run(self, job: RunJob) -> RunResult:
        run_dir = self._run_dir(job)
        result = RunResult(slug=job.slug, run_dir=str(run_dir))
        cli = self._claude_cli()
        if not shutil.which(cli):
            result.errors.append(f"Claude Code CLI '{cli}' not found on PATH (set CLAUDE_CLI or use --backend api)")
            return result

        wf = self.bp.workflow_path()
        args = {
            "client_legal_name": job.client_legal_name,
            "client_common_name": job.client_common_name or job.client_legal_name,
            "ticker_or_private": job.ticker_or_private,
            "primary_geography": job.primary_geography,
            "target_vertical": job.target_vertical,
            "research_as_of": job.research_as_of,
            "output_tier": job.tier,
            "slug": job.slug,
            "run_dir": str(run_dir),
            "harness_dir": str(self.harness_dir),
            "capability_pack": job.capability_pack,
            "account_team_input_sheet": job.account_team_input_sheet,
            "account_context": job.account_context,
            "known_relationship_context": job.known_relationship_context,
            "strategic_pursuit_objectives": job.strategic_pursuit_objectives,
            "remediation_rounds": job.remediation_rounds,
        }
        prompt = (
            "Use a workflow (this is an explicit opt-in). Run the workflow at "
            f"{wf} with these args as JSON:\n{json.dumps(args)}\n"
            "Execute it to completion without asking questions."
        )
        self.emitter.event("run_start", message=job.client_legal_name,
                           data={"slug": job.slug, "backend": "workflow"})
        proc = await asyncio.create_subprocess_exec(
            cli, "-p", prompt,
            cwd=str(REPO_ROOT),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            env=os.environ.copy(),
        )
        assert proc.stdout is not None
        async for raw in proc.stdout:
            line = raw.decode(errors="replace").rstrip()
            if line:
                self.emitter.event("log", agent="workflow", message=line[:500])
        await proc.wait()

        dossier = run_dir / f"{job.slug}-{self.bp.dossier_suffix}.md"
        if dossier.exists():
            result.dossier = str(dossier)
        else:
            result.errors.append(
                "workflow finished but no dossier was produced — check the Claude Code output above; "
                "the Workflow tool may need to be enabled/opted-in in your Claude Code session."
            )
        self.emitter.event("run_done", message=result.dossier or "(no dossier)")
        return result

    def check(self) -> list[str]:
        cli = self._claude_cli()
        issues: list[str] = []
        if not self.cfg.auth.subscription:
            # The Claude Code CLI authenticates itself; an --auth api-key run would still be
            # billed to the subscription here, so say so rather than let the user assume metering.
            issues.append(
                "auth mode is 'api-key' but the workflow backend always runs on the Claude Code "
                "CLI's own credentials — use --backend api to actually spend the API key"
            )
        if not shutil.which(cli):
            issues.append(f"Claude Code CLI '{cli}' not found (needed for the default workflow backend)")
        wf = self.bp.workflow_path()
        if not wf.exists():
            issues.append(f"bundled workflow missing: {wf}")
        return issues
