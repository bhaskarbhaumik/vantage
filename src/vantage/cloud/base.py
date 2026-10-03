"""Shared deploy helpers."""

from __future__ import annotations

import shutil
import subprocess

from rich.console import Console


def run_cmds(cmds: list[list[str]], *, dry_run: bool, console: Console) -> int:
    for cmd in cmds:
        console.print(f"[dim]$ {' '.join(cmd)}[/]")
        if dry_run:
            continue
        if shutil.which(cmd[0]) is None:
            console.print(f"[red]{cmd[0]} not found on PATH[/]")
            return 127
        proc = subprocess.run(cmd)
        if proc.returncode != 0:
            console.print(f"[red]command failed ({proc.returncode})[/]")
            return proc.returncode
    return 0
