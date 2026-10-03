"""Config loading + path resolution.

Precedence, low → high:
  1. repo ``config/default.json``
  2. ``~/.config/vantage/default.json`` (created from the repo default on first run)
  3. environment variables (``VANTAGE_*``)
  4. explicit ``overrides`` (CLI flags)
"""

from __future__ import annotations

import json
import os
import re
from copy import deepcopy
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from .models.config import Config

APP = "vantage"
# src/vantage/settings.py → parents[2] == repo root
REPO_ROOT = Path(__file__).resolve().parents[2]
REPO_DEFAULT = REPO_ROOT / "config" / "default.json"
if not REPO_DEFAULT.exists():
    REPO_DEFAULT = Path(__file__).resolve().parent / "_config" / "default.json"
REPO_SCHEMA = REPO_DEFAULT.with_name("default.schema.json")
# Honour the user's explicit request: ~/.config/vantage (XDG), not the macOS default.
USER_CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))) / APP
USER_CONFIG = USER_CONFIG_DIR / "default.json"

_ENV_LOADED = False


def _load_env_once() -> None:
    global _ENV_LOADED
    if not _ENV_LOADED:
        load_dotenv(REPO_ROOT / ".env")
        load_dotenv()  # also a .env in cwd, if any
        _ENV_LOADED = True


def _deep_merge(base: dict, over: dict) -> dict:
    out = deepcopy(base)
    for k, v in over.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def _neutral_run_defaults(data: dict) -> dict:
    """Accept legacy organization-prefixed input names; explicit neutral names win."""
    out = deepcopy(data)
    defaults = out.get("run_defaults", {})
    for key in list(defaults):
        for canonical in ("capability_pack", "account_context"):
            if key.endswith(f"_{canonical}"):
                defaults.setdefault(canonical, defaults.pop(key))
    return out


def ensure_user_config() -> Path:
    """Create ``~/.config/vantage/default.json`` from the repo template on first run."""
    if not USER_CONFIG.exists():
        USER_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        if REPO_DEFAULT.exists():
            USER_CONFIG.write_text(REPO_DEFAULT.read_text())
    ensure_user_schema()
    return USER_CONFIG


def ensure_user_schema() -> None:
    """Keep the deployed relative $schema reference resolvable after upgrades."""
    if REPO_SCHEMA.exists():
        USER_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        dest = USER_CONFIG_DIR / REPO_SCHEMA.name
        text = REPO_SCHEMA.read_text()
        if not dest.exists() or dest.read_text() != text:
            dest.write_text(text)


def _env_overrides() -> dict[str, Any]:
    over: dict[str, Any] = {}
    eng: dict[str, Any] = {}
    if os.environ.get("VANTAGE_BACKEND"):
        eng["backend"] = os.environ["VANTAGE_BACKEND"]
    if os.environ.get("VANTAGE_TIER"):
        eng["tier"] = os.environ["VANTAGE_TIER"].upper()
    if os.environ.get("VANTAGE_OUTPUT_DIR"):
        eng["output_dir"] = os.environ["VANTAGE_OUTPUT_DIR"]
    if os.environ.get("VANTAGE_HARNESS_DIR"):
        eng["harness_dir"] = os.environ["VANTAGE_HARNESS_DIR"]
    if eng:
        over["engine"] = eng
    if os.environ.get("VANTAGE_AUTH_MODE"):
        over["auth"] = {"mode": os.environ["VANTAGE_AUTH_MODE"]}
    return over


def load_config(path: str | None = None, overrides: dict | None = None) -> Config:
    _load_env_once()
    data: dict[str, Any] = {}
    if REPO_DEFAULT.exists():
        data = json.loads(REPO_DEFAULT.read_text())

    if path:
        ucfg: Path | None = Path(path).expanduser()
    elif os.environ.get("VANTAGE_CONFIG"):
        ucfg = Path(os.environ["VANTAGE_CONFIG"]).expanduser()
    else:
        ucfg = ensure_user_config()
    if ucfg and ucfg.exists():
        data = _deep_merge(data, _neutral_run_defaults(json.loads(ucfg.read_text())))

    data = _deep_merge(data, _env_overrides())
    if overrides:
        data = _deep_merge(data, overrides)
    # v1 advertised an XBRL toggle that was never consumed. Accept old files until migration.
    data.get("tools", {}).get("edgar", {}).pop("xbrl", None)
    return Config.model_validate(data)


# Pre-rename tokens that may survive in a user config copied over from the company-aid era.
# Longest first: "Account Intelligence Dossier" must match before the bare "AID" inside it.
_LEGACY_STRINGS: tuple[tuple[str, str], ...] = (
    ("Account Intelligence Dossier", "Vantage"),
    ("Company AID", "Vantage"),
    ("company-aid", "vantage"),
    ("company_aid", "vantage"),
    ("COMPANY_AID", "VANTAGE"),
)
_LEGACY_AID = re.compile(r"\bAID\b")


def _rebrand(value: Any) -> Any:
    """Rewrite pre-rename brand tokens anywhere in a config value, recursively."""
    if isinstance(value, str):
        for old, new in _LEGACY_STRINGS:
            value = value.replace(old, new)
        return _LEGACY_AID.sub("Vantage", value)
    if isinstance(value, dict):
        return {k: _rebrand(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_rebrand(v) for v in value]
    return value


def migrate_user_config(user: dict, template: dict) -> tuple[dict, list[str]]:
    """Bring a user config up to the current schema. Returns ``(config, change log)``.

    Deliberately conservative: it rebrands strings, reconciles ``role_model_map`` against the live
    agent roster, and fills in keys the template has gained — but it does not prune unrecognised
    keys generally, because ``cloud`` and ``providers`` are open-ended and a deliberate extra there
    is indistinguishable from a leftover.
    """
    from .blueprint.stages import AGENTS

    changes: list[str] = []
    normalized = _neutral_run_defaults(user)
    if normalized != user:
        changes.append("renamed organization-prefixed run defaults to neutral input names")
        user = normalized
    out = _deep_merge(template, user)
    if out != user:
        changes.append("filled missing settings from the shipped template")

    rebranded = _rebrand(out)
    if rebranded != out:
        changes.append("rewrote pre-rename brand tokens (company-aid / Company AID / AID / "
                       "Account Intelligence Dossier) to Vantage")
        out = rebranded

    old_output = out["engine"]["output_dir"]
    legacy_paths = {Path(p).expanduser() for p in ("~/vantage/runs", "~/.cache/vantage/runs")}
    if Path(old_output).expanduser() in legacy_paths:
        out["engine"]["output_dir"] = template["engine"]["output_dir"]
        changes.append(f"migrated engine.output_dir {old_output} -> {out['engine']['output_dir']}")

    # Upgrade only known shipped defaults. Deliberately pinned/custom models survive.
    for tier, old in (("synthesis", "claude-opus-4-8"), ("research", "claude-sonnet-5")):
        ref = out["models"][tier]
        if ref.get("provider") == "anthropic" and ref.get("model") == old:
            ref["model"] = template["models"][tier]["model"]
            changes.append(f"updated models.{tier}.model to {ref['model']}")
    for provider, old in (("openai", "gpt-5"), ("gemini", "gemini-2.5-pro")):
        pc = out.get("providers", {}).get(provider, {})
        if pc.get("default_model") == old:
            pc["default_model"] = template["providers"][provider]["default_model"]
            changes.append(f"updated providers.{provider}.default_model")
    if "xbrl" in out.get("tools", {}).get("edgar", {}):
        out["tools"]["edgar"].pop("xbrl")
        changes.append("removed tools.edgar.xbrl (never consumed by the engine)")
    if out.get("version") != template["version"]:
        out["version"] = template["version"]
        changes.append(f"updated config version to {template['version']}")

    # v3 renamed engine.depth -> engine.tier. A stale `depth` is inert but misleading.
    if "depth" in out.get("engine", {}):
        out["engine"].pop("depth")
        changes.append("dropped engine.depth (v3 uses engine.tier)")

    rmm = out.get("role_model_map") or {}
    stale = sorted(set(rmm) - set(AGENTS))
    for role in stale:
        rmm.pop(role)
    if stale:
        changes.append(f"dropped role_model_map entries for agents that no longer exist: "
                       f"{', '.join(stale)}")
    added = sorted(set(template.get("role_model_map", {})) - set(rmm))
    for role in added:
        rmm[role] = template["role_model_map"][role]
    if added:
        changes.append(f"added role_model_map entries for: {', '.join(added)}")
    if rmm:
        out["role_model_map"] = rmm

    # Wave A launches len(WAVE_A) agents; a lower cap silently serialises the research phase.
    from .blueprint.stages import WAVE_A

    if user.get("version", "1.0") == "1.0" and out.get("engine", {}).get("max_concurrency", 0) < len(WAVE_A):
        was = out["engine"].get("max_concurrency")
        out["engine"]["max_concurrency"] = len(WAVE_A)
        changes.append(f"raised engine.max_concurrency {was} -> {len(WAVE_A)} (Wave A size)")

    # The _note is documentation, not configuration — always take the current one.
    if template.get("_note") and out.get("_note") != template["_note"]:
        out["_note"] = template["_note"]
        changes.append("refreshed _note from the shipped template")

    return out, changes


def harness_dir(cfg: Config) -> Path:
    """Resolve the bundled prompt/blueprint library directory."""
    if cfg.engine.harness_dir:
        return Path(cfg.engine.harness_dir).expanduser()
    env = os.environ.get("VANTAGE_HARNESS_DIR")
    if env:
        return Path(env).expanduser()
    repo = REPO_ROOT / "harness"
    if repo.exists():
        return repo
    return Path(__file__).resolve().parent / "_harness"  # wheel-installed location


def output_dir(cfg: Config) -> Path:
    return Path(cfg.engine.output_dir).expanduser()


def run_dir(cfg: Config, slug: str) -> Path:
    return output_dir(cfg) / slug
