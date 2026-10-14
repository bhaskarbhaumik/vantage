"""Run-directory discovery for ``vantage runs`` (and the TUI, via ``vantage runs list --json``).

A run directory lives under ``engine.output_dir`` and is recognised by any of: a
``*-vantage.md`` dossier, ``state/state.json``, ``run.jsonl``, or a ``sections/`` folder. Every
file is optional — a run that crashed in P0 still lists, with nulls where data is missing.

Layout read here::

    <run>/<slug>-vantage.md            assembled dossier
    <run>/state/state.json             run_contract (entity, tier, as_of) + verification
    <run>/qa/verification-report.json  final verification (preferred over state.verification)
    <run>/exports/manifest.json        written by ``vantage export``
    <run>/sections/*.md                per-section outputs
    <run>/run.jsonl                    event log (fallback for client/tier)
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

DOSSIER_GLOB = "*-vantage.md"
VERIFICATION_KEYS = ("result", "overall_confidence", "eqi", "blockers", "majors", "minors")
_SLUG_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def valid_slug(slug: str) -> bool:
    """A slug is one safe path component (no separators, no leading dot)."""
    return bool(_SLUG_RE.match(slug or "")) and ".." not in slug


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def is_run_dir(path: Path) -> bool:
    if not path.is_dir() or path.name.startswith("."):
        return False
    return (
        (path / "state" / "state.json").exists()
        or (path / "run.jsonl").exists()
        or (path / "sections").is_dir()
        or any(path.glob(DOSSIER_GLOB))
    )


def find_dossier(run_dir: Path) -> Path | None:
    preferred = run_dir / f"{run_dir.name}-vantage.md"
    if preferred.exists():
        return preferred
    found = sorted(run_dir.glob(DOSSIER_GLOB))
    return found[0] if found else None


def _first_run_start(run_dir: Path) -> dict:
    log = run_dir / "run.jsonl"
    try:
        with log.open(encoding="utf-8") as fh:
            for line in fh:
                try:
                    ev = json.loads(line)
                except ValueError:
                    continue
                if ev.get("type") == "run_start":
                    return ev
    except OSError:
        pass
    return {}


def _verification(run_dir: Path, state: dict | None) -> dict | None:
    report = _read_json(run_dir / "qa" / "verification-report.json")
    src = report if isinstance(report, dict) and report.get("result") else None
    if src is None and isinstance(state, dict) and isinstance(state.get("verification"), dict):
        src = state["verification"]
    if not src:
        return None
    return {k: src.get(k) for k in VERIFICATION_KEYS}


def _exports(run_dir: Path) -> list[str]:
    exp = run_dir / "exports"
    manifest = _read_json(exp / "manifest.json")
    items: list[Any] = []
    if isinstance(manifest, dict):
        items = manifest.get("artifacts") or manifest.get("files") or []
    elif isinstance(manifest, list):
        items = manifest
    out: list[str] = []
    for it in items:
        p = it.get("path") if isinstance(it, dict) else it
        if not p:
            continue
        pp = Path(str(p))
        out.append(str(pp if pp.is_absolute() else exp / pp))
    if not out and exp.is_dir():
        out = [str(p) for p in sorted(exp.iterdir())
               if p.is_file() and p.name != "manifest.json" and not p.name.startswith(".")]
    return out


def _mtime(paths: list[Path]) -> float:
    best = 0.0
    for p in paths:
        try:
            best = max(best, p.stat().st_mtime)
        except OSError:
            continue
    return best


def run_info(run_dir: Path, *, sections: bool = False) -> dict:
    """The ``vantage runs`` JSON object for one run directory."""
    run_dir = Path(run_dir)
    state = _read_json(run_dir / "state" / "state.json")
    state = state if isinstance(state, dict) else {}
    contract = state.get("run_contract") if isinstance(state.get("run_contract"), dict) else {}
    entity = contract.get("entity") if isinstance(contract.get("entity"), dict) else {}
    start = {} if (contract and contract.get("tier")) else _first_run_start(run_dir)

    client = entity.get("legal_name") or contract.get("target") or entity.get("common_name") \
        or start.get("message")
    tier = contract.get("tier") or (start.get("data") or {}).get("tier")
    dossier = find_dossier(run_dir)
    info: dict[str, Any] = {
        "slug": run_dir.name,
        "run_dir": str(run_dir),
        "dossier": str(dossier) if dossier else None,
        "client": client or None,
        "as_of": contract.get("as_of") or None,
        "tier": tier or None,
        "mtime": _mtime([run_dir, run_dir / "state" / "state.json", run_dir / "run.jsonl",
                         run_dir / "qa" / "verification-report.json"]
                        + ([dossier] if dossier else [])),
        "verification": _verification(run_dir, state),
        "exports": _exports(run_dir),
    }
    if sections:
        sec = run_dir / "sections"
        info["sections"] = sorted(p.name for p in sec.iterdir() if p.is_file()) \
            if sec.is_dir() else []
    return info


def discover(root: Path) -> list[dict]:
    """Every run under ``root``, most recently touched first."""
    root = Path(root).expanduser()
    if not root.is_dir():
        return []
    runs = [run_info(p) for p in root.iterdir() if is_run_dir(p)]
    runs.sort(key=lambda r: (r["mtime"], r["slug"]), reverse=True)
    return runs


def find_run(root: Path, slug: str) -> Path | None:
    """Resolve ``slug`` to a run directory directly under ``root`` (never outside it)."""
    if not valid_slug(slug):
        return None
    cand = Path(root).expanduser() / slug  # valid_slug() rules out separators and ".."
    return cand if is_run_dir(cand) else None


def slugs(root: Path) -> list[str]:
    root = Path(root).expanduser()
    if not root.is_dir():
        return []
    return sorted(p.name for p in root.iterdir() if is_run_dir(p))
