"""Vantage engine CLI (Typer).

Human mode prints concise progress to stderr; ``--json`` streams one RunEvent JSON object per line
to stdout for the Ink TUI to consume. Console script: ``vantage-engine``.
"""

from __future__ import annotations

import asyncio
import datetime as _dt
import json
import os
import sys

import typer
from rich.console import Console
from rich.table import Table

from . import TAGLINE, __version__, auth
from .blueprint import Blueprint
from .engine import BACKENDS, get_backend
from .logging import EventEmitter
from .models.config import AUTH_MODES, Config
from .models.events import RunEvent
from .pipeline.orchestrator import RunJob
from .settings import (
    REPO_DEFAULT,
    USER_CONFIG,
    ensure_user_config,
    ensure_user_schema,
    harness_dir,
    load_config,
    migrate_user_config,
    output_dir,
)

app = typer.Typer(no_args_is_help=True, add_completion=False, help=f"Vantage — {TAGLINE}.")
config_app = typer.Typer(no_args_is_help=True, help="Inspect and manage configuration.")
app.add_typer(config_app, name="config")
auth_app = typer.Typer(no_args_is_help=True, help="Inspect and switch the credential mode.")
app.add_typer(auth_app, name="auth")
err = Console(stderr=True)


def _today() -> str:
    return _dt.date.today().isoformat()


def _human_sink(ev: RunEvent) -> None:
    if ev.type == "stage_start":
        err.print(f"[bold cyan]▶ {ev.stage}[/]  {ev.data.get('agents', '')}")
    elif ev.type == "agent_start":
        err.print(f"   … {ev.agent}")
    elif ev.type == "agent_tool":
        err.print(f"      [dim]{ev.agent} → {ev.message}[/]")
    elif ev.type == "agent_done":
        u = ev.data.get("usage", {})
        err.print(f"   [green]✓ {ev.agent}[/] ({u.get('output_tokens', 0)} out tok)")
    elif ev.type == "agent_error":
        err.print(f"   [red]✗ {ev.agent}: {ev.message}[/]")
    elif ev.type == "run_warning":
        err.print(f"   [yellow]! {ev.message}[/]")
    elif ev.type == "run_error":
        err.print(f"[red]run error: {ev.message}[/]")
    elif ev.type == "run_done":
        err.print(f"[bold green]● done[/] {ev.message}")
    elif ev.type == "log":
        err.print(f"[dim]{ev.agent or ''}: {ev.message}[/]")


@app.command()
def version() -> None:
    """Print the engine version."""
    typer.echo(__version__)


@app.command()
def run(
    client: str = typer.Option(..., "--client", "-c", help="Client legal name"),
    slug: str = typer.Option(..., "--slug", "-s", help="Run directory name"),
    backend: str | None = typer.Option(None, "--backend", "-b", help=f"{'|'.join(BACKENDS)}"),
    tier: str | None = typer.Option(None, "--tier", "-t", help="EXECUTIVE|STANDARD|FULL_ANNEX"),
    as_of: str | None = typer.Option(None, "--as-of", help="YYYY-MM-DD (default: today)"),
    common_name: str = typer.Option("", "--common-name"),
    ticker: str | None = typer.Option(None, "--ticker"),
    vertical: str | None = typer.Option(None, "--vertical"),
    geography: str | None = typer.Option(None, "--geography"),
    account_context: str | None = typer.Option(None, "--account-context"),
    relationship: str | None = typer.Option(None, "--relationship"),
    objectives: str | None = typer.Option(None, "--objectives"),
    capability_pack: str | None = typer.Option(
        None, "--capability-pack",
        help="ATTACHED|NOT_ATTACHED. Without it every organization capability claim renders "
             "[INTERNAL: validate with practice]."),
    input_sheet: str | None = typer.Option(
        None, "--input-sheet",
        help="ATTACHED|NOT_ATTACHED (§21.10). Without it win probability, account revenue, "
             "relationship strength, and stakeholder access render [INTERNAL REQUIRED]."),
    auth_mode: str | None = typer.Option(
        None, "--auth", "-a", help="subscription|api-key. Default subscription: runs on your Claude "
                                   "plan and reads no API key. api-key is billed per token."),
    ask_key: bool = typer.Option(
        False, "--ask-key", help="With --auth api-key: prompt on this terminal for any key that is "
                                 "not already in the environment. The key is never stored."),
    config_path: str | None = typer.Option(None, "--config"),
    json_out: bool = typer.Option(False, "--json", help="Stream RunEvent JSON to stdout (for the TUI)"),
) -> None:
    """Run a dossier end to end with the selected backend."""
    overrides: dict = {"engine": {}, "auth": {}}
    if backend:
        overrides["engine"]["backend"] = backend
    if tier:
        overrides["engine"]["tier"] = tier.upper()
    if auth_mode:
        if auth_mode not in AUTH_MODES:
            err.print(f"[red]--auth must be one of {' | '.join(AUTH_MODES)}[/]")
            raise typer.Exit(2)
        overrides["auth"]["mode"] = auth_mode
    if ask_key:
        overrides["auth"]["prompt_for_key"] = True
    cfg = load_config(config_path, overrides=overrides or None)
    if ask_key and cfg.auth.subscription:
        err.print("[yellow]--ask-key ignored: subscription mode reads no API key "
                  "(add --auth api-key to change that)[/]")
    backend_name = cfg.engine.backend
    hd = harness_dir(cfg)

    run_dir = output_dir(cfg) / slug
    emitter = EventEmitter(
        jsonl_path=run_dir / "run.jsonl",
        stdout_json=json_out,
        callback=None if json_out else _human_sink,
    )

    try:
        bp = Blueprint(hd)
        be = get_backend(backend_name, cfg, bp, hd, emitter)
    except Exception as e:
        err.print(f"[red]cannot start: {e}[/]")
        raise typer.Exit(2) from e

    try:
        for provider in auth.prompt_missing(cfg):
            err.print(f"[dim]{provider} key accepted for this run only (not stored)[/]")
    except auth.AuthError as e:
        err.print(f"[red]auth: {e}[/]")
        raise typer.Exit(2) from e

    issues = be.check()
    if issues:
        for i in issues:
            err.print(f"[yellow]readiness: {i}[/]")
    if warning := auth.model_pin_warning(cfg):
        err.print(f"[yellow]auth: {warning}[/]")

    defaults = cfg.run_defaults
    job = RunJob(
        client_legal_name=client, slug=slug, research_as_of=as_of or _today(),
        client_common_name=common_name, ticker_or_private=ticker if ticker is not None else defaults.ticker_or_private, primary_geography=geography if geography is not None else defaults.primary_geography,
        target_vertical=vertical if vertical is not None else defaults.target_vertical, tier=cfg.engine.tier, account_context=account_context if account_context is not None else defaults.account_context,
        known_relationship_context=relationship if relationship is not None else defaults.known_relationship_context, strategic_pursuit_objectives=objectives if objectives is not None else defaults.strategic_pursuit_objectives,
        capability_pack=(capability_pack or defaults.capability_pack).upper(),
        account_team_input_sheet=(input_sheet or defaults.account_team_input_sheet).upper(),
    )
    result = asyncio.run(be.run(job))
    emitter.close()

    if json_out:
        sys.stdout.write(json.dumps({"result": _result_dict(result)}) + "\n")
    else:
        _print_result(result, backend_name)
    raise typer.Exit(0 if result.dossier else 1)


@app.command()
def backends() -> None:
    """List execution backends and their readiness."""
    cfg = load_config()
    hd = harness_dir(cfg)
    bp = Blueprint(hd)
    t = Table("backend", "default", "ready", "notes")
    for name in BACKENDS:
        be = get_backend(name, cfg, bp, hd)
        issues = be.check()
        t.add_row(name, "★" if name == cfg.engine.backend else "", "yes" if not issues else "no", "; ".join(issues))
    Console().print(t)


@app.command()
def doctor() -> None:
    """Environment + configuration diagnostics."""
    cfg = load_config()
    hd = harness_dir(cfg)
    c = Console()
    c.print(f"[bold]Vantage {__version__}[/]")
    c.print(f"python           {sys.version.split()[0]}")
    c.print(f"config (user)    {USER_CONFIG}  {'(exists)' if USER_CONFIG.exists() else '(will be created)'}")
    c.print(f"harness          {hd}  {'ok' if hd.exists() else 'MISSING'}")
    c.print(f"output dir       {output_dir(cfg)}")
    c.print(f"default backend  {cfg.engine.backend} · tier {cfg.engine.tier}")
    c.print(f"concurrency      {cfg.engine.max_concurrency}")
    c.print("\n[bold]harness[/]")
    for issue in _config_drift(cfg):
        c.print(f"  [yellow]{issue}[/]")
    c.print("\n[bold]auth[/]")
    _print_auth(c, cfg)
    c.print("\n[bold]tool keys[/]")
    for label, env in [("Tavily", "TAVILY_API_KEY"), ("SEC EDGAR id", "SEC_EDGAR_IDENTITY")]:
        c.print(f"  {label:14s} {'set' if os.environ.get(env) else '[dim]unset[/]'}  ({env})")
    c.print("\n[bold]backends[/]")
    bp = Blueprint(hd)
    for name in BACKENDS:
        issues = get_backend(name, cfg, bp, hd).check()
        c.print(f"  {name:10s} {'[green]ready[/]' if not issues else '[yellow]' + '; '.join(issues) + '[/]'}")


def _config_drift(cfg) -> list[str]:
    """Report a user config that predates the v3 harness rather than letting it degrade a run."""
    from .blueprint.stages import AGENTS, WAVE_A

    issues: list[str] = []
    if cfg.engine.max_concurrency < len(WAVE_A):
        issues.append(
            f"max_concurrency is {cfg.engine.max_concurrency} but Wave A launches {len(WAVE_A)} "
            f"agents — the research phase will serialise. Raise it in {USER_CONFIG}."
        )
    # An output_dir from an older layout silently splits the user's runs across two trees.
    if cfg.engine.output_dir in ("~/vantage/runs", "~/.cache/vantage/runs"):
        issues.append(
            f"output_dir still points at a legacy run tree ({cfg.engine.output_dir}) — "
            f"update it to ~/.cache/vantage/run in {USER_CONFIG}, or move the existing runs across."
        )
    unknown = sorted(set(cfg.role_model_map) - set(AGENTS))
    missing = sorted(set(AGENTS) - set(cfg.role_model_map))
    if unknown:
        issues.append(f"role_model_map names agents that no longer exist: {', '.join(unknown)} "
                      "(v2 roster). They are ignored.")
    if missing:
        issues.append(f"role_model_map has no entry for: {', '.join(missing)} — these fall back "
                      "to the research tier.")
    if not issues:
        issues.append("config matches the v3.0.0 agent roster")
    else:
        issues.append("run `vantage-engine config migrate` to fix the above")
    return issues


@app.command()
def deploy(
    target: str | None = typer.Option(None, "--target", "-t", help="gcp|azure|aws"),
    build: bool = typer.Option(True, "--build/--no-build", help="Build+push the image first"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print the commands without running"),
) -> None:
    """Build the container and deploy the engine to a cloud target."""
    from .cloud import deploy as _deploy

    cfg = load_config()
    tgt = target or cfg.cloud.target
    code = _deploy(cfg, tgt, build=build, dry_run=dry_run, console=Console())
    raise typer.Exit(code)


@app.command()
def serve(
    host: str = typer.Option("0.0.0.0", "--host"),
    port: int = typer.Option(0, "--port", help="0 = $PORT or 8080"),
) -> None:
    """Run the engine as an HTTP service (GET /healthz, POST /run) — for cloud service deploys."""
    from .server import serve as _serve

    _serve(host=host, port=port or None)


def _print_auth(c: Console, cfg) -> None:
    """Render the credential posture: mode, what each agent class routes to, key presence."""
    from .blueprint.stages import ORCHESTRATOR_AGENTS, SECTION_RESEARCH_AGENTS

    mode = cfg.auth.mode
    if cfg.auth.subscription:
        c.print("  mode           [green]subscription[/] — runs on your Claude plan; no API key is "
                "read, even if one is exported")
    else:
        c.print(f"  mode           [yellow]{mode}[/] — billed per token against the keys below")

    for name, roles, profile in (
        ("orchestrator", ORCHESTRATOR_AGENTS, cfg.auth.orchestrator),
        ("research", SECTION_RESEARCH_AGENTS, cfg.auth.research),
    ):
        sample = roles[0] if roles else ""
        provider = profile.provider or (cfg.model_for_role(sample).provider if sample else "anthropic")
        env = auth.key_env(cfg, provider, profile)
        model = profile.model or "(per role_model_map tier)"
        state = "[dim]n/a in subscription mode[/]" if cfg.auth.subscription else (
            "[green]set[/]" if os.environ.get(env) else "[yellow]unset[/]")
        c.print(f"  {name:14s} {len(roles):2d} agents · provider {provider} · model {model}")
        c.print(f"                 key {env} {state}")

    if warning := auth.model_pin_warning(cfg):
        c.print(f"  [yellow]{warning}[/]")


@auth_app.command("status")
def auth_status() -> None:
    """Show which credentials this configuration would use, and whether they are present."""
    cfg = load_config()
    c = Console()
    _print_auth(c, cfg)
    c.print("\n[dim]Keys are read from the environment only. Vantage never writes one to "
            f"{USER_CONFIG}.[/]")


@auth_app.command("use")
def auth_use(
    mode: str = typer.Argument(..., help="subscription | api-key"),
) -> None:
    """Persist the default credential mode to the user config."""
    if mode not in AUTH_MODES:
        err.print(f"[red]mode must be one of {' | '.join(AUTH_MODES)}[/]")
        raise typer.Exit(2)
    path = ensure_user_config()
    data = json.loads(path.read_text())
    data.setdefault("auth", {})["mode"] = mode
    path.write_text(json.dumps(data, indent=2) + "\n")
    typer.echo(f"auth.mode = {mode}  ({path})")
    if mode == "api-key":
        err.print("[yellow]Runs are now billed per token. Export the provider key, or pass "
                  "--ask-key to be prompted per run.[/]")


@config_app.command("show")
def config_show() -> None:
    """Print the merged effective configuration."""
    cfg = load_config()
    typer.echo(json.dumps(cfg.model_dump(), indent=2))


@config_app.command("path")
def config_path_cmd() -> None:
    """Print the user config path (creating it from the template if missing)."""
    typer.echo(str(ensure_user_config()))


@config_app.command("migrate")
def config_migrate(
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would change, write nothing"),
) -> None:
    """Bring ~/.config/vantage/default.json up to the current schema.

    Reconciles role_model_map against the live agent roster, and fills in keys the shipped template
    has gained. The previous file is kept alongside as `.bak`.
    """
    path = USER_CONFIG
    user = json.loads(path.read_text()) if path.exists() else {}
    template = json.loads(REPO_DEFAULT.read_text())
    merged, changes = migrate_user_config(user, template)
    Config.model_validate(merged)

    if not changes:
        if not dry_run:
            ensure_user_schema()
        typer.echo(f"{path} is already current — nothing to do.")
        return
    for line in changes:
        err.print(f"  [cyan]·[/] {line}")
    if dry_run:
        err.print("[dim]--dry-run: nothing written[/]")
        return

    path.parent.mkdir(parents=True, exist_ok=True)
    stamp = _dt.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    backup = path.with_name(f"default.json.{stamp}.bak")
    if path.exists():
        backup.write_text(path.read_text())
    path.write_text(json.dumps(merged, indent=2) + "\n")
    ensure_user_schema()
    typer.echo(f"migrated {path}  (previous file kept at {backup})")


@config_app.command("init")
def config_init() -> None:
    """Create ~/.config/vantage/default.json from the template."""
    p = ensure_user_config()
    typer.echo(f"user config at {p}")


def _result_dict(r) -> dict:
    return {
        "slug": r.slug, "run_dir": r.run_dir, "dossier": r.dossier,
        "entity": r.entity, "ownership_form": r.ownership_form,
        "jurisdictions": r.jurisdictions, "vertical_module": r.vertical_module,
        "vertical_confidence": r.vertical_confidence,
        "entity_ambiguity": r.entity_ambiguity,
        "agents_ok": r.agents_ok, "agents_total": r.agents_total,
        "verification": r.verification, "usage": r.usage, "errors": r.errors,
    }


def _print_result(r, backend_name: str) -> None:
    c = Console(stderr=True)
    c.rule("[bold]run complete[/]")
    c.print(f"backend     {backend_name}")
    c.print(f"agents      {r.agents_ok}/{r.agents_total} ok")
    c.print(f"tokens      {r.usage.get('input_tokens', 0)} in / {r.usage.get('output_tokens', 0)} out")
    if r.entity_ambiguity:
        c.print(f"[yellow]entity      ambiguity recorded: {r.entity_ambiguity}[/]")
    if r.verification:
        v = r.verification
        c.print(f"verify      {v.get('result')} · Overall Confidence {v.get('overall_confidence')} "
                f"(EQI {v.get('eqi')}) · {v.get('blockers', 0)}B/{v.get('majors', 0)}M/{v.get('minors', 0)}m")
        if v.get("overall_confidence") == "Insufficient":
            c.print("[red]            do not present — re-run with better sources or reduce scope[/]")
        if topics := (v.get("budget_limited_topics") or []):
            c.print(f"[yellow]            stopped on budget (not diminishing returns): {', '.join(topics)}[/]")
    if r.errors:
        c.print(f"[yellow]issues      {len(r.errors)}[/]")
        for e in r.errors[:8]:
            c.print(f"  [yellow]- {e}[/]")
    c.print(f"dossier     [bold]{r.dossier or '(none)'}[/]")


def main() -> None:
    import warnings

    # Some optional framework deps (crewai → chromadb) still import pydantic.v1 and warn on
    # Python 3.14+. The warning is benign and must not pollute CLI output.
    warnings.filterwarnings("ignore", message=r"Core Pydantic V1", category=UserWarning)
    app()


if __name__ == "__main__":
    main()
