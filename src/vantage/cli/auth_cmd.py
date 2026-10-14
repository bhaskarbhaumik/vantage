"""``vantage auth status|use`` — the subscription-first credential posture."""

from __future__ import annotations

import json
import os

import typer

from .. import auth
from ..models.config import AUTH_MODES, Config
from . import flags as F
from .common import emit_json, fail, load_cfg, pkg
from .ui import UI

auth_app = typer.Typer(no_args_is_help=True, cls=F.VantageSubGroup,
                       help="Inspect and switch the credential mode.")


def profile_rows(cfg: Config) -> list[dict]:
    """One row per credential class: which provider, model and key env it would use."""
    from ..blueprint.stages import ORCHESTRATOR_AGENTS, SECTION_RESEARCH_AGENTS

    rows = []
    for name, roles, profile in (
        ("orchestrator", ORCHESTRATOR_AGENTS, cfg.auth.orchestrator),
        ("research", SECTION_RESEARCH_AGENTS, cfg.auth.research),
    ):
        sample = roles[0] if roles else ""
        provider = profile.provider or (cfg.model_for_role(sample).provider if sample else "anthropic")
        env = auth.key_env(cfg, provider, profile)
        rows.append({
            "class": name, "agents": len(roles), "provider": provider,
            "model": profile.model or None, "key_env": env,
            "key_set": None if cfg.auth.subscription else bool(os.environ.get(env)),
        })
    return rows


def auth_checks(cfg: Config) -> list[dict]:
    """Doctor checks for the auth group. Never includes a key value — only whether it is set."""
    out = []
    if cfg.auth.subscription:
        out.append({"group": "auth", "name": "mode", "status": "ok",
                    "detail": "subscription — runs on your Claude plan; no API key is read, even "
                              "if one is exported"})
    else:
        out.append({"group": "auth", "name": "mode", "status": "warn",
                    "detail": f"{cfg.auth.mode} — billed per token against the keys below"})
    for r in profile_rows(cfg):
        model = r["model"] or "(per role_model_map tier)"
        detail = f"{r['agents']} agents · provider {r['provider']} · model {model} · key {r['key_env']}"
        if r["key_set"] is None:
            status, detail = "ok", detail + " (n/a in subscription mode)"
        elif r["key_set"]:
            status, detail = "ok", detail + " set"
        else:
            status, detail = "warn", detail + " unset"
        out.append({"group": "auth", "name": r["class"], "status": status, "detail": detail})
    if warning := auth.model_pin_warning(cfg):
        out.append({"group": "auth", "name": "model pin", "status": "warn", "detail": warning})
    return out


def print_auth(cfg: Config) -> None:
    if cfg.auth.subscription:
        UI.print("  mode           [ok]subscription[/] — runs on your Claude plan; no API key is "
                 "read, even if one is exported")
    else:
        UI.print(f"  mode           [warn]{cfg.auth.mode}[/] — billed per token against the keys "
                 "below")
    for r in profile_rows(cfg):
        model = r["model"] or "(per role_model_map tier)"
        if r["key_set"] is None:
            state = "[muted]n/a in subscription mode[/]"
        else:
            state = "[ok]set[/]" if r["key_set"] else "[warn]unset[/]"
        UI.print(f"  {r['class']:14s} {r['agents']:2d} agents · provider {r['provider']} · "
                 f"model {model}")
        UI.print(f"                 {UI.i('key')} {r['key_env']} {state}")
    if warning := auth.model_pin_warning(cfg):
        UI.warn(warning)


@auth_app.command("status", cls=F.VantageCommand)
def auth_status(
    ctx: typer.Context,
    json_out: bool = typer.Option(False, "--json", help="Machine-readable output on stdout."),
) -> None:
    """Show which credentials this configuration would use, and whether they are present."""
    cfg = load_cfg(ctx)
    if json_out:
        emit_json({"mode": cfg.auth.mode, "subscription": cfg.auth.subscription,
                   "profiles": profile_rows(cfg),
                   "model_pin_warning": auth.model_pin_warning(cfg)})
        return
    UI.print(f"[title]{UI.i('auth')} auth[/]")
    print_auth(cfg)
    UI.print(f"\n[muted]Keys are read from the environment only. Vantage never writes one to "
             f"{pkg().USER_CONFIG}.[/]")


@auth_app.command("use", cls=F.VantageCommand)
def auth_use(
    mode: str = typer.Argument(..., help="subscription | api-key"),
) -> None:
    """Persist the default credential mode to the user config."""
    if mode not in AUTH_MODES:
        fail(f"mode must be one of {' | '.join(AUTH_MODES)}")
    path = pkg().ensure_user_config()
    data = json.loads(path.read_text())
    data.setdefault("auth", {})["mode"] = mode
    path.write_text(json.dumps(data, indent=2) + "\n")
    typer.echo(f"auth.mode = {mode}  ({path})")
    if mode == "api-key":
        UI.warn("Runs are now billed per token. Export the provider key, or pass --ask-key to be "
                "prompted per run.")
