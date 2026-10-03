"""Cloud deploy — build the image and deploy the engine as a batch job / task.

Deployment is done by shelling out to the cloud CLI (``gcloud`` / ``az`` / ``aws``), which is the
most reliable and auditable path. ``--dry-run`` prints the exact command sequence without executing.
Reference manifests live under ``deploy/``.
"""

from __future__ import annotations

import os

from rich.console import Console

from ..models.config import Config
from .aws import aws_cmds
from .azure import azure_cmds
from .base import run_cmds
from .gcp import gcp_cmds

_BUILDERS = {"gcp": gcp_cmds, "azure": azure_cmds, "aws": aws_cmds}


def deploy(cfg: Config, target: str, *, build: bool = True, dry_run: bool = False,
           console: Console | None = None) -> int:
    console = console or Console()
    target = (target or cfg.cloud.target).lower()
    builder = _BUILDERS.get(target)
    if builder is None:
        console.print(f"[red]unknown cloud target {target!r}; choose gcp | azure | aws[/]")
        return 2
    cmds, notes = builder(cfg, build)
    console.print(f"[bold]deploy → {target}[/]  ({'dry-run' if dry_run else 'LIVE'})")
    for n in notes:
        console.print(f"[yellow]• {n}[/]")
    return run_cmds(cmds, dry_run=dry_run, console=console)


def env_or(name: str, default: str) -> str:
    return os.environ.get(name) or default
