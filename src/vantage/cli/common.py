"""Helpers shared by the command modules.

Config loading goes through the package attribute ``vantage.cli.load_config`` (looked up at call
time) so tests — and embedders — can substitute it in one place.
"""

from __future__ import annotations

import importlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, NoReturn

import typer
from pydantic import ValidationError

from ..models.config import Config, UiCfg
from . import flags as F
from .ui import UI

_META_CFG = "vantage.cli.cfg"


def pkg():
    """The ``vantage.cli`` package module (for patchable names such as ``load_config``)."""
    return importlib.import_module("vantage.cli")


def fail(msg: str, code: int = 2) -> NoReturn:
    UI.error(msg)
    raise typer.Exit(code)


def config_path(ctx: typer.Context | None) -> str | None:
    return ctx.find_root().meta.get(F.META_CONFIG_PATH) if ctx is not None else None


def configure_ui(ctx: typer.Context | None, cfg: Config | None = None) -> None:
    """Apply ``ui.*`` (config + flags) and ``--quiet``/``--verbose`` to the stderr console."""
    meta = ctx.find_root().meta if ctx is not None else {}
    if cfg is not None:
        ui = cfg.ui
    else:
        try:
            ui = UiCfg.model_validate(F.overrides_from(ctx).get("ui", {}) if ctx else {})
        except ValidationError:
            ui = UiCfg()
    UI.configure(icons=ui.icons, color=ui.color, theme=ui.theme, animations=ui.animations,
                 quiet=bool(meta.get(F.META_QUIET)), verbose=bool(meta.get(F.META_VERBOSE)))


def load_cfg(ctx: typer.Context | None) -> Config:
    """Effective config: shipped < user file < VANTAGE_* env < every CLI flag. Cached per run."""
    root = ctx.find_root() if ctx is not None else None
    if root is not None and _META_CFG in root.meta:
        return root.meta[_META_CFG]
    overrides = F.overrides_from(ctx) if ctx is not None else {}
    try:
        cfg = pkg().load_config(config_path(ctx), overrides=overrides or None)
    except ValidationError as e:
        UI.error("invalid configuration")
        for err in e.errors():
            loc = ".".join(str(p) for p in err.get("loc", ()))
            UI.print(f"  [key]{loc}[/]: {err.get('msg')}")
        raise typer.Exit(2) from e
    except (OSError, ValueError) as e:
        fail(f"cannot read configuration: {e}")
    configure_ui(ctx, cfg)
    if root is not None:
        root.meta[_META_CFG] = cfg
    return cfg


def emit_json(obj: Any) -> None:
    sys.stdout.write(json.dumps(obj, default=str) + "\n")
    sys.stdout.flush()


def open_path(path: Path) -> None:
    """Open a file or folder with the platform's default handler (non-blocking)."""
    if sys.platform == "darwin":
        subprocess.Popen(["open", str(path)])
    elif os.name == "nt":  # pragma: no cover
        os.startfile(str(path))  # type: ignore[attr-defined]
    else:
        subprocess.Popen(["xdg-open", str(path)], stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)


def complete_slugs(incomplete: str) -> list[str]:
    """Run slugs under the configured output dir (shell completion; never raises)."""
    try:
        from ..runs import slugs
        from ..settings import output_dir

        cfg = pkg().load_config()
        return [s for s in slugs(output_dir(cfg)) if s.startswith(incomplete)]
    except Exception:
        return []
