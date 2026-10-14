"""``vantage export`` — turn a finished dossier into PPTX / DOCX / PDF / HTML collateral.

The work is done by :mod:`vantage.export.api`, imported lazily so the CLI starts (and every other
command works) without the ``export`` extra installed. Each flag here is also recorded as an
``export.*`` config override, so ``cfg.export`` and the :class:`ExportOptions` agree.
"""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Annotated, Literal

import typer
from rich.table import Table

from ..logging import EventEmitter
from ..models.events import RunEvent
from ..settings import output_dir
from . import flags as F
from .common import complete_slugs, emit_json, fail, load_cfg, open_path
from .ui import UI

try:
    from typer._types import TyperChoice as _Choice
except ImportError:  # pragma: no cover
    from click import Choice as _Choice  # type: ignore[no-redef]

FORMATS = ("pptx", "docx", "pdf", "html")
_FORMAT_CHOICE = _Choice(FORMATS, case_sensitive=False)
_HELP_PANEL = "Export helpers"


def _complete_target(incomplete: str) -> list[str]:
    return complete_slugs(incomplete)


def _resolve_target(target: str, out_root: Path) -> Path:
    p = Path(target).expanduser()
    if p.exists():
        return p
    cand = out_root / target
    if "/" not in target and cand.exists():
        return cand
    fail(f"no dossier, run directory or run slug '{target}' (looked in {out_root})")


def _sink(ev: RunEvent) -> None:
    if ev.type == "stage_start":
        UI.info(f"[accent]{UI.i('stage')} {ev.stage}[/]")
    elif ev.type == "stage_done":
        UI.debug(f"   {UI.i('ok')} {ev.stage}")
    elif ev.type == "artifact":
        d = ev.data
        extra = ", ".join(f"{d[k]} {k}" for k in ("slides", "pages") if d.get(k))
        UI.info(f"   [ok]{UI.i('file')} {d.get('format')}[/] {d.get('path')}"
                + (f" [muted]({extra})[/]" if extra else ""))
    elif ev.type == "run_warning":
        UI.warn(ev.message or "")
    elif ev.type in ("run_error", "agent_error"):
        UI.error(ev.message or "")
    elif ev.type == "log":
        UI.debug(f"{ev.agent or ''}: {ev.message}")


def _human_bytes(n: int | None) -> str:
    if not n:
        return ""
    size = float(n)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return str(n)


def export(
    ctx: typer.Context,
    target: str = typer.Argument(..., metavar="DOSSIER", help="A *-vantage.md dossier, a run directory, or a run "
                                           "slug under the output dir.",
                                 autocompletion=_complete_target),
    formats: Annotated[list[str] | None, typer.Option(
        "--format", "-f", click_type=_FORMAT_CHOICE,
        help="Output format; repeat for several (pdf implies docx). Default: export.formats.",
    )] = None,
    depth: Literal["exec", "standard", "full"] | None = typer.Option(
        None, "--depth", help="exec ≈ 18 slides · standard ≈ 31 · full = every section."),
    site_mode: Literal["microsite", "deck"] | None = typer.Option(
        None, "--site-mode", help="Shape of the HTML output."),
    authoring: Literal["deterministic", "agents"] | None = typer.Option(
        None, "--authoring", help="deterministic maps sections to plans; agents lets Claude "
                                  "author them."),
    out: Annotated[Path | None, typer.Option(
        "--out", "-o", help="Output dir (default <run dir>/exports).")] = None,
    classification: str | None = typer.Option(None, "--classification",
                                              help="Marking on every page, slide and screen."),
    brand: str | None = typer.Option(None, "--brand", help="Domain whose brand themes the "
                                                           "collateral (via get-brand)."),
    client_logo: bool | None = typer.Option(None, "--client-logo/--no-client-logo",
                                            help="Client logo on the cover."),
    helper_icons: bool | None = typer.Option(None, "--helper-icons/--no-helper-icons",
                                             help="get-icon glyphs.", rich_help_panel=_HELP_PANEL),
    helper_brand: bool | None = typer.Option(None, "--helper-brand/--no-helper-brand",
                                             help="get-brand theming.", rich_help_panel=_HELP_PANEL),
    stock_images: bool | None = typer.Option(None, "--stock-images/--no-stock-images",
                                             help="get-stock splash images.",
                                             rich_help_panel=_HELP_PANEL),
    diagrams: Literal["auto", "dgm", "drawio", "mermaid", "none"] | None = typer.Option(
        None, "--diagrams", help="Diagram renderer.", rich_help_panel=_HELP_PANEL),
    illustrations: Literal["none", "napkin"] | None = typer.Option(
        None, "--illustrations", help="napkin spends Napkin credits (opt-in).",
        rich_help_panel=_HELP_PANEL),
    charts: Literal["matplotlib", "plotly"] | None = typer.Option(
        None, "--charts", help="Chart renderer.", rich_help_panel=_HELP_PANEL),
    libreoffice_bin: str | None = typer.Option(None, "--libreoffice-bin",
                                               help="LibreOffice binary for PDF conversion.",
                                               rich_help_panel=_HELP_PANEL),
    helper_timeout: float | None = typer.Option(None, "--helper-timeout", min=0.001,
                                                help="Seconds before a helper call is abandoned.",
                                                rich_help_panel=_HELP_PANEL),
    open_out: bool = typer.Option(False, "--open", help="Open the output folder when done."),
    json_out: bool = typer.Option(False, "--json", help="Stream RunEvent JSON to stdout, then "
                                                        "{\"result\": …}."),
) -> None:
    """Export a dossier to PPTX, DOCX, PDF and/or self-contained HTML."""
    given = {
        "formats": [f.lower() for f in formats] if formats else None,
        "depth": depth, "site_mode": site_mode, "authoring": authoring,
        "out_dir": str(out.expanduser()) if out else None,
        "classification": classification, "brand": brand, "client_logo": client_logo,
    }
    helpers = {
        "icons": helper_icons, "brand": helper_brand, "stock_images": stock_images,
        "diagrams": diagrams, "illustrations": illustrations, "charts": charts,
        "libreoffice_bin": libreoffice_bin, "timeout_seconds": helper_timeout,
    }
    for key, value in given.items():
        if value is not None:
            F.record(ctx, ("export", key), value)
    for key, value in helpers.items():
        if value is not None:
            F.record(ctx, ("export", "helpers", key), value)
    cfg = load_cfg(ctx)
    dossier = _resolve_target(target, output_dir(cfg))

    try:
        api = importlib.import_module("vantage.export.api")
    except ImportError as e:
        fail(f"export support is unavailable ({e}). Install it with: uv sync --extra export")

    kwargs = {k: v for k, v in given.items() if v is not None}
    if "out_dir" in kwargs:
        kwargs["out_dir"] = Path(kwargs["out_dir"])
    if any(v is not None for v in helpers.values()):
        kwargs["helpers"] = cfg.export.helpers
    try:
        opts = api.options_from_config(cfg, dossier, **kwargs)
    except FileNotFoundError as e:
        fail(str(e))
    except (ValueError, TypeError) as e:
        fail(f"invalid export options: {e}")

    emitter = EventEmitter(stdout_json=json_out, callback=None if json_out else _sink)
    if not json_out:
        UI.info(f"[title]{UI.i('export')} export[/] {dossier} "
                f"[muted]→ {', '.join(opts.formats)} · {opts.depth}[/]")
    try:
        result = api.export(opts, emit=emitter.emit)
    except FileNotFoundError as e:
        fail(str(e))
    except Exception as e:  # surface, do not traceback, in human mode
        if json_out:
            emitter.emit(RunEvent(type="run_error", message=str(e)))
        fail(f"export failed: {e}", 1)
    finally:
        emitter.close()

    if json_out:
        emit_json({"result": result.to_dict()})
    else:
        _print_result(result)
    if open_out:
        open_path(Path(result.out_dir))
    raise typer.Exit(0 if result.artifacts else 1)


def _print_result(result) -> None:  # noqa: ANN001
    t = Table(title=f"{UI.i('folder')} {result.out_dir}", title_justify="left")
    for col in ("format", "file", "size", "slides/pages"):
        t.add_column(col, overflow="fold")
    for a in result.artifacts:
        sp = a.get("slides") or a.get("pages") or ""
        t.add_row(f"[ok]{UI.i('file')} {a.get('format')}[/]", Path(str(a.get("path"))).name,
                  _human_bytes(a.get("bytes")), str(sp))
    UI.print(t)
    for w in result.warnings or []:
        UI.warn(w)
    if result.plans:
        UI.info("[muted]plans: " + ", ".join(f"{k} {v}" for k, v in result.plans.items()) + "[/]")
    v = result.verification or {}
    if v.get("overall_confidence"):
        UI.print(f"verification  {UI.result(v.get('result'))} · Overall Confidence "
                 f"{UI.band(v.get('overall_confidence'))}")
        if v.get("overall_confidence") == "Insufficient":
            UI.print(f"[loud] {UI.i('stop')} DO NOT PRESENT — Overall Confidence Insufficient [/]")
    if not result.artifacts:
        UI.error("no artifacts were written")
