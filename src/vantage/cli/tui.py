"""Launch the Ink TUI (``vantage --tui`` / ``vantage tui``).

Resolution order: ``<repo>/tui/dist/index.js`` run with ``node``, else ``vantage-tui`` on PATH.
The process is *replaced* (``os.execvp``), so the TUI owns the terminal and its exit code.

Presentation flags given to the Python CLI (``--ascii``, ``--icons``, ``--no-color``,
``--theme``, ``--no-animations``) are forwarded as flags. Every other config override given on
the command line is exported as its ``VANTAGE_*`` variable, so the engine processes the TUI
spawns (``vantage-engine run … --json``) see the same configuration.
"""

from __future__ import annotations

import os
import shutil
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from ..settings import REPO_ROOT

BUILD_HINT = "npm ci && npm run build"


def tui_entry(repo_root: Path = REPO_ROOT) -> Path:
    return repo_root / "tui" / "dist" / "index.js"


def resolve_tui(repo_root: Path = REPO_ROOT) -> tuple[list[str] | None, str | None]:
    """Return ``(argv prefix, None)`` or ``(None, reason)`` when the TUI cannot be started."""
    entry = tui_entry(repo_root)
    node = shutil.which("node")
    if entry.exists() and node:
        return [node, str(entry)], None
    exe = shutil.which("vantage-tui")
    if exe:
        return [exe], None
    if not node:
        return None, "Node.js 18+ is not on PATH and no `vantage-tui` executable was found."
    return None, f"the TUI is not built ({entry} is missing) and `vantage-tui` is not on PATH."


def ui_flags(given: Mapping[str, Any]) -> list[str]:
    """Translate explicitly-given ``ui.*`` overrides into the TUI's own flags."""
    out: list[str] = []
    icons = given.get("ui.icons")
    if icons == "ascii":
        out.append("--ascii")
    elif icons:
        out += ["--icons", str(icons)]
    if given.get("ui.color") == "never":
        out.append("--no-color")
    if given.get("ui.theme"):
        out += ["--theme", str(given["ui.theme"])]
    if given.get("ui.animations") is False:
        out.append("--no-animations")
    return out


def env_for(given: Mapping[str, Any], config_path: str | None,
            specs_by_key: Mapping[str, Any]) -> dict[str, str]:
    """``VANTAGE_*`` variables carrying the non-ui overrides into the TUI's engine children."""
    env: dict[str, str] = {}
    if config_path:
        env["VANTAGE_CONFIG"] = str(config_path)
    for key, value in given.items():
        spec = specs_by_key.get(key)
        if spec is None or key.startswith("ui."):
            continue
        if value is None:
            text = "null"
        elif isinstance(value, bool):
            text = "true" if value else "false"
        elif isinstance(value, list | tuple):
            text = " ".join(str(v) for v in value)
        else:
            text = str(value)
        env[spec.envvar] = text
    return env


def build_command(args: list[str], given: Mapping[str, Any],
                  repo_root: Path = REPO_ROOT) -> tuple[list[str] | None, str | None]:
    prefix, reason = resolve_tui(repo_root)
    if prefix is None:
        return None, reason
    return [*prefix, *ui_flags(given), *args], None


def exec_tui(argv: list[str], extra_env: Mapping[str, str]) -> None:
    """Replace this process with the TUI. Only returns if exec itself fails (raises OSError)."""
    os.environ.update(extra_env)
    os.execvp(argv[0], argv)
