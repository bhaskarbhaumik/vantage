"""``vantage runs list|show|path|open|rm`` — the run tree under ``engine.output_dir``."""

from __future__ import annotations

import shutil
import time
from pathlib import Path

import typer
from rich.table import Table

from .. import runs as R
from ..settings import output_dir
from . import flags as F
from .common import complete_slugs, emit_json, fail, load_cfg, open_path
from .ui import UI

runs_app = typer.Typer(no_args_is_help=True, cls=F.VantageSubGroup,
                       help="List, inspect, open and delete runs in the output dir.")

_SLUG_ARG = typer.Argument(..., help="Run slug (directory name under the output dir)",
                           autocompletion=complete_slugs)


def _age(mtime: float) -> str:
    if not mtime:
        return "—"
    d = max(0.0, time.time() - mtime)
    for unit, sec in (("d", 86400), ("h", 3600), ("m", 60)):
        if d >= sec:
            return f"{int(d // sec)}{unit} ago"
    return "just now"


def _resolve(ctx: typer.Context, slug: str) -> Path:
    cfg = load_cfg(ctx)
    root = output_dir(cfg)
    run = R.find_run(root, slug)
    if run is None:
        fail(f"no run '{slug}' under {root}", 1)
    return run


def _vcell(v: dict | None) -> tuple[str, str, str]:
    if not v:
        return "[muted]—[/]", "", ""
    eqi = "" if v.get("eqi") is None else f"{v['eqi']}"
    counts = f"{v.get('blockers') or 0}B/{v.get('majors') or 0}M/{v.get('minors') or 0}m"
    return UI.band(v.get("overall_confidence")), eqi, counts


@runs_app.command("list", cls=F.VantageCommand)
def runs_list(
    ctx: typer.Context,
    limit: int = typer.Option(0, "--limit", "-n", min=0, help="Show at most N runs (0 = all)."),
    json_out: bool = typer.Option(False, "--json", help="Machine-readable output on stdout."),
) -> None:
    """List runs, most recent first."""
    cfg = load_cfg(ctx)
    root = output_dir(cfg)
    found = R.discover(root)
    if limit:
        found = found[:limit]
    if json_out:
        emit_json({"runs": found})
        return
    if not found:
        UI.info(f"no runs under {root}")
        return
    t = Table(title=f"{UI.i('folder')} {root}", title_justify="left")
    t.add_column("slug", no_wrap=True)
    t.add_column("client", overflow="ellipsis", max_width=28, no_wrap=True)
    for col in ("as of", "tier", "confidence", "EQI", "B/M/m", "exports", "updated"):
        t.add_column(col, no_wrap=True)
    for r in found:
        band, eqi, counts = _vcell(r["verification"])
        dossier = UI.i("dossier") + " " if r["dossier"] else ""
        t.add_row(f"{dossier}[key]{r['slug']}[/]", r["client"] or "", r["as_of"] or "",
                  r["tier"] or "", band, eqi, counts, str(len(r["exports"])) if r["exports"] else "",
                  _age(r["mtime"]))
    UI.print(t)


@runs_app.command("show", cls=F.VantageCommand)
def runs_show(
    ctx: typer.Context,
    slug: str = _SLUG_ARG,
    json_out: bool = typer.Option(False, "--json", help="Machine-readable output on stdout."),
) -> None:
    """Show one run: dossier, verification, sections and exports."""
    info = R.run_info(_resolve(ctx, slug), sections=True)
    if json_out:
        emit_json(info)
        return
    v = info["verification"] or {}
    grid = Table.grid(padding=(0, 2))
    grid.add_column(style="muted")
    grid.add_column()
    grid.add_row("client", info["client"] or "—")
    grid.add_row("as of", info["as_of"] or "—")
    grid.add_row("tier", info["tier"] or "—")
    grid.add_row("run dir", info["run_dir"])
    grid.add_row("dossier", info["dossier"] or "[warn](none)[/]")
    if v:
        grid.add_row("verification", f"{UI.result(v.get('result'))} · Overall Confidence "
                     f"{UI.band(v.get('overall_confidence'))} (EQI {v.get('eqi')}) · "
                     f"{v.get('blockers') or 0}B/{v.get('majors') or 0}M/{v.get('minors') or 0}m")
    else:
        grid.add_row("verification", "[muted]not run[/]")
    grid.add_row("sections", f"{len(info['sections'])}")
    grid.add_row("exports", "\n".join(info["exports"]) or "[muted]none[/]")
    grid.add_row("updated", _age(info["mtime"]))
    UI.print(f"[title]{UI.i('dossier')} {info['slug']}[/]")
    UI.print(grid)
    if v.get("overall_confidence") == "Insufficient":
        UI.print(f"[loud] {UI.i('stop')} DO NOT PRESENT — Overall Confidence Insufficient [/]")


@runs_app.command("path", cls=F.VantageCommand)
def runs_path(
    ctx: typer.Context,
    slug: str = _SLUG_ARG,
    dossier: bool = typer.Option(False, "--dossier", help="Print the dossier file instead."),
) -> None:
    """Print a run's directory (or dossier) path on stdout."""
    run = _resolve(ctx, slug)
    if dossier:
        d = R.find_dossier(run)
        if d is None:
            fail(f"run '{slug}' has no dossier yet", 1)
        typer.echo(str(d))
    else:
        typer.echo(str(run))


@runs_app.command("open", cls=F.VantageCommand)
def runs_open(
    ctx: typer.Context,
    slug: str = _SLUG_ARG,
    folder: bool = typer.Option(False, "--dir", help="Open the run folder, not the dossier."),
) -> None:
    """Open a run's dossier (or folder) with the system handler."""
    run = _resolve(ctx, slug)
    target = run if folder else (R.find_dossier(run) or run)
    open_path(target)
    UI.ok(f"opened {target}")


@runs_app.command("rm", cls=F.VantageCommand)
def runs_rm(
    ctx: typer.Context,
    slug: str = _SLUG_ARG,
    yes: bool = typer.Option(False, "--yes", "-y", help="Do not ask for confirmation."),
) -> None:
    """Delete a run directory (asks first unless --yes)."""
    run = _resolve(ctx, slug)
    if run.is_symlink():
        fail(f"{run} is a symlink — remove it by hand", 1)
    if not yes and not typer.confirm(f"Delete {run} and everything in it?", default=False,
                                     err=True):
        UI.info("kept")
        raise typer.Exit(1)
    shutil.rmtree(run)
    UI.ok(f"{UI.i('trash')} removed {run}")
