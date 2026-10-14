"""Agent authoring — run the export Workflow through the Claude Code CLI.

Mirrors :mod:`vantage.engine.workflow_backend`: the bundled
``harness/export/workflows/vantage-export.workflow.mjs`` runs in headless print mode on the
user's Claude subscription (no API key). The workflow ingests the dossier, writes the narrative,
runs three concurrent plan authors and an adversarial QA gate, and leaves authored plans in
``<out>/plan/``. Rendering stays deterministic: :func:`vantage.export.api.export` renders from
those plans afterwards (``render: false`` tells the workflow not to render itself).
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from collections.abc import Callable
from pathlib import Path

from ..settings import REPO_ROOT

WORKFLOW = "workflows/vantage-export.workflow.mjs"


def claude_cli() -> str:
    return os.environ.get("CLAUDE_CLI", "claude")


def workflow_path(harness_dir: Path) -> Path:
    return Path(harness_dir) / WORKFLOW


def run_workflow(*, dossier: Path, out_dir: Path, harness_dir: Path, depth: str,
                 formats: list[str], site_mode: str, classification: str, brand: str | None,
                 log: Callable[[str], None]) -> tuple[bool, str]:
    """Run the export Workflow to completion. Returns ``(ok, reason)``; never raises."""
    cli = claude_cli()
    if not shutil.which(cli):
        return False, (f"Claude Code CLI '{cli}' not found on PATH (set CLAUDE_CLI); "
                       "falling back to deterministic plans")
    wf = workflow_path(harness_dir)
    if not wf.exists():
        return False, f"export workflow missing: {wf}"
    args = {
        "dossier": str(dossier),
        "run_dir": str(out_dir),
        "harness_dir": str(harness_dir),
        "repo": str(REPO_ROOT),
        "depth": depth,
        "formats": formats,
        "site_mode": site_mode,
        "classification": classification,
        "brand": brand,
        "render": False,
    }
    prompt = ("Use a workflow (this is an explicit opt-in). Run the workflow at "
              f"{wf} with these args as JSON:\n{json.dumps(args)}\n"
              "Execute it to completion without asking questions.")
    try:
        proc = subprocess.Popen([cli, "-p", prompt], cwd=str(REPO_ROOT), stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, text=True, env=os.environ.copy())
    except OSError as exc:
        return False, f"could not start the Claude Code CLI: {exc}"
    assert proc.stdout is not None
    for line in proc.stdout:
        line = line.rstrip()
        if line:
            log(line[:500])
    code = proc.wait()
    if code != 0:
        return False, f"the export workflow exited with status {code}"
    return True, ""
