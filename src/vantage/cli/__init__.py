"""Vantage command line (Typer). Console scripts: ``vantage`` and ``vantage-engine``.

Human output is Rich on **stderr**; ``--json`` writes only JSON to **stdout** (RunEvent lines then
``{"result": …}`` for ``run``/``export``) for the Ink TUI and scripts. Every config key is also a
flag (``vantage options``), accepted before or after the command.

Exit codes: 0 ok · 1 the command ran but did not produce its result (no dossier, no artifacts,
missing run, invalid file) · 2 usage, configuration or startup error.
"""

from __future__ import annotations

import asyncio
import dataclasses
import datetime as _dt
import os
import re
import sys
import warnings

import typer
from rich.panel import Panel
from rich.table import Table
from typer.core import TyperOption

from .. import TAGLINE, __version__, auth
from ..blueprint import Blueprint
from ..engine import BACKENDS, get_backend
from ..logging import EventEmitter
from ..models.config import Config
from ..models.events import RunEvent
from ..pipeline.orchestrator import RunJob
from ..runs import valid_slug
from ..settings import (
    REPO_DEFAULT,
    REPO_ROOT,
    REPO_SCHEMA,
    USER_CONFIG,
    ensure_user_config,
    ensure_user_schema,
    harness_dir,
    load_config,
    migrate_user_config,
    output_dir,
)
from . import completion as C
from . import flags as F
from . import tui as T
from .auth_cmd import auth_app, auth_checks
from .common import configure_ui, emit_json, fail, load_cfg
from .config_cmd import config_app, options_cmd
from .export_cmd import export as export_cmd
from .runs_cmd import runs_app
from .ui import UI

__all__ = [
    "REPO_DEFAULT", "REPO_ROOT", "REPO_SCHEMA", "USER_CONFIG", "app", "ensure_user_config",
    "ensure_user_schema", "get_backend", "load_config", "main", "migrate_user_config",
]

HARNESS_VERSION = "3.0.0"
CONFIG_VERSION = str(Config.model_fields["version"].default)
_LEGAL_SUFFIX = re.compile(
    r"\b(incorporated|inc|corporation|corp|company|co|limited|ltd|llc|plc|lp|llp|sa|ag|nv|bv|"
    r"se|spa|gmbh|holdings?|group)\b\.?", re.I)


# ── root group ────────────────────────────────────────────────────────────────────────────────
def _tui_flag(ctx, param, value):  # noqa: ANN001
    if value and not ctx.resilient_parsing:
        ctx.meta[F.META_TUI] = True
    return value


def _version_flag(ctx, param, value):  # noqa: ANN001
    if value and not ctx.resilient_parsing:
        typer.echo(__version__)
        ctx.exit(0)
    return value


class VantageGroup(F.VantageSubGroup):
    """Root group: carries every global/config flag, ``--tui`` and ``--version``."""

    def __init__(self, **kw) -> None:  # noqa: ANN003
        super().__init__(**kw)
        F.inject(self, root=True)
        self.params.append(TyperOption(
            param_decls=["g__tui", "--tui"], is_flag=True, default=False, expose_value=False,
            callback=_tui_flag, rich_help_panel=F.PANEL_GLOBAL,
            help="Launch the Ink TUI, forwarding the remaining arguments."))
        self.params.append(TyperOption(
            param_decls=["g__version", "--version"], is_flag=True, default=False,
            expose_value=False, is_eager=True, callback=_version_flag,
            help="Print the version and exit."))

    def invoke(self, ctx):  # noqa: ANN001
        if ctx.meta.get(F.META_TUI):
            _launch_tui(ctx, [*getattr(ctx, "_protected_args", []), *ctx.args])
        return super().invoke(ctx)


app = typer.Typer(
    cls=VantageGroup, no_args_is_help=True, add_completion=False,
    help=f"Vantage — {TAGLINE}.\n\nEvery config key is also a flag, before or after the "
         "command: see `vantage options`.",
)
app.add_typer(config_app, name="config")
app.add_typer(auth_app, name="auth")
app.add_typer(runs_app, name="runs")
completion_app = typer.Typer(no_args_is_help=True, cls=F.VantageSubGroup,
                             help="Shell completion scripts (bash, zsh, fish).")
app.add_typer(completion_app, name="completion")


@app.callback(invoke_without_command=True)
def _root(ctx: typer.Context) -> None:
    configure_ui(ctx)
    if ctx.invoked_subcommand is None and not ctx.meta.get(F.META_TUI):
        typer.echo(ctx.get_help(), err=True)
        raise typer.Exit(0)


def _launch_tui(ctx: typer.Context, args: list[str]) -> None:
    configure_ui(ctx)
    given = F.given_paths(ctx)
    argv, reason = T.build_command(args, given, REPO_ROOT)
    if argv is None:
        UI.error(f"cannot start the TUI: {reason}")
        UI.print(f"  build it from the repository root:  [key]{T.BUILD_HINT}[/]  "
                 "(needs Node.js 18+)")
        raise typer.Exit(1)
    specs = {s.dotted: s for s in F.config_flag_specs()}
    env = T.env_for(given, ctx.find_root().meta.get(F.META_CONFIG_PATH), specs)
    UI.debug(f"exec {' '.join(argv)}")
    try:
        T.exec_tui(argv, env)
    except OSError as e:
        fail(f"cannot start the TUI: {e}", 1)
    raise typer.Exit(0)  # only reached when exec is stubbed (tests)


# ── run / generate ────────────────────────────────────────────────────────────────────────────
def _today() -> str:
    return _dt.date.today().isoformat()


def auto_slug(name: str, as_of: str | None = None) -> str:
    """``Acme Industries, Inc.`` + 2026-10-14 -> ``acme-industries-2026-10``."""
    base = _LEGAL_SUFFIX.sub(" ", name)
    base = re.sub(r"[^a-z0-9]+", "-", base.lower()).strip("-") or \
        re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "run"
    month = (as_of or _today())[:7]
    return f"{base[:48].rstrip('-')}-{month}"


def _human_sink(ev: RunEvent) -> None:
    if ev.type == "stage_start":
        UI.info(f"[accent]{UI.i('stage')} {ev.stage}[/]  {ev.data.get('agents', '')}")
    elif ev.type == "agent_start":
        UI.info(f"   [muted]{UI.i('agent')}[/] {ev.agent}")
    elif ev.type == "agent_tool":
        if not UI.quiet:
            UI.print(f"      [muted]{ev.agent} {UI.i('tool')} {ev.message}[/]")
    elif ev.type == "agent_progress":
        UI.debug(f"      {ev.agent}: {ev.message or ''}")
    elif ev.type == "agent_done":
        u = ev.data.get("usage", {})
        UI.info(f"   [ok]{UI.i('ok')} {ev.agent}[/] ({u.get('output_tokens', 0)} out tok)")
    elif ev.type == "agent_error":
        UI.error(f"{ev.agent}: {ev.message}")
    elif ev.type == "stage_done":
        UI.debug(f"   {UI.i('ok')} {ev.stage} done")
    elif ev.type == "run_warning":
        UI.warn(ev.message or "")
    elif ev.type == "run_error":
        UI.error(f"run error: {ev.message}")
    elif ev.type == "run_done":
        UI.print(f"[ok]{UI.i('done')} done[/] {ev.message}")
    elif ev.type == "log":
        if not UI.quiet:
            UI.print(f"[muted]{ev.agent or ''}: {ev.message}[/]")


def run(
    ctx: typer.Context,
    client: str = typer.Option(..., "--client", "-c", help="Client legal name"),
    slug: str | None = typer.Option(None, "--slug", "-s", help="Run directory name (default: "
                                    "from the client name + YYYY-MM)"),
    as_of: str | None = typer.Option(None, "--as-of", help="YYYY-MM-DD (default: today)"),
    common_name: str = typer.Option("", "--common-name", help="Name the client is known by"),
    ticker: str | None = typer.Option(None, "--ticker", help="Ticker, or PRIVATE "
                                      "(default run_defaults.ticker_or_private)"),
    vertical: str | None = typer.Option(None, "--vertical", help="Target vertical "
                                        "(default run_defaults.target_vertical)"),
    geography: str | None = typer.Option(None, "--geography", help="Primary geography "
                                         "(default run_defaults.primary_geography)"),
    account_context: str | None = typer.Option(None, "--account-context"),
    relationship: str | None = typer.Option(None, "--relationship",
                                            help="Known relationship context"),
    objectives: str | None = typer.Option(None, "--objectives",
                                          help="Strategic pursuit objectives"),
    capability_pack: str | None = typer.Option(
        None, "--capability-pack",
        help="ATTACHED|NOT_ATTACHED. Without it every organization capability claim renders "
             "[INTERNAL: validate with practice]."),
    input_sheet: str | None = typer.Option(
        None, "--input-sheet",
        help="ATTACHED|NOT_ATTACHED (§21.10). Without it win probability, account revenue, "
             "relationship strength, and stakeholder access render [INTERNAL REQUIRED]."),
    remediation_rounds: int | None = typer.Option(
        None, "--remediation-rounds", min=0, max=2,
        help="Owner-remediation rounds after verification (P7R), 0-2; default 1. Workflow "
             "backend."),
    ask_key: bool = typer.Option(
        False, "--ask-key", help="With --auth api-key: prompt on this terminal for any key that is "
                                 "not already in the environment. The key is never stored."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print the resolved job and config as "
                                                          "JSON; run nothing."),
    json_out: bool = typer.Option(False, "--json", help="Stream RunEvent JSON to stdout (for the "
                                                        "TUI)"),
) -> None:
    """Run a dossier end to end with the selected backend."""
    if ask_key:
        F.record(ctx, ("auth", "prompt_for_key"), True)
    cfg = load_cfg(ctx)
    if ask_key and cfg.auth.subscription:
        UI.warn("--ask-key ignored: subscription mode reads no API key "
                "(add --auth api-key to change that)")

    as_of = as_of or _today()
    try:
        _dt.date.fromisoformat(as_of)
    except ValueError:
        fail(f"--as-of must be YYYY-MM-DD, got {as_of!r}")
    slug = slug or auto_slug(common_name or client, as_of)
    if not valid_slug(slug):
        fail(f"--slug must be one path component of letters, digits, '.', '_' or '-', "
             f"got {slug!r}")
    gates = {}
    for flag, value, default in (("--capability-pack", capability_pack,
                                  cfg.run_defaults.capability_pack),
                                 ("--input-sheet", input_sheet,
                                  cfg.run_defaults.account_team_input_sheet)):
        v = (value or default).upper()
        if v not in ("ATTACHED", "NOT_ATTACHED"):
            fail(f"{flag} must be ATTACHED or NOT_ATTACHED, got {value!r}")
        gates[flag] = v

    backend_name = cfg.engine.backend
    d = cfg.run_defaults

    def pick(value: str | None, default: str) -> str:
        return value if value is not None else default

    job = RunJob(
        client_legal_name=client, slug=slug, research_as_of=as_of,
        client_common_name=common_name,
        ticker_or_private=pick(ticker, d.ticker_or_private),
        primary_geography=pick(geography, d.primary_geography),
        target_vertical=pick(vertical, d.target_vertical),
        tier=cfg.engine.tier,
        account_context=pick(account_context, d.account_context),
        known_relationship_context=pick(relationship, d.known_relationship_context),
        strategic_pursuit_objectives=pick(objectives, d.strategic_pursuit_objectives),
        capability_pack=gates["--capability-pack"],
        account_team_input_sheet=gates["--input-sheet"],
    )
    if remediation_rounds is not None:
        job.remediation_rounds = remediation_rounds
        if backend_name != "workflow":
            UI.warn(f"--remediation-rounds applies to the workflow backend only; {backend_name} "
                    "does not run P7R yet")
    run_dir = output_dir(cfg) / slug

    if dry_run:
        job_dict = dataclasses.asdict(job)
        emit_json({"job": job_dict, "backend": backend_name, "run_dir": str(run_dir),
                   "harness_dir": str(harness_dir(cfg)), "config": cfg.model_dump(mode="json")})
        UI.info(f"[muted]{UI.i('info')} dry run — nothing was executed[/]")
        return

    hd = harness_dir(cfg)
    emitter = EventEmitter(jsonl_path=run_dir / "run.jsonl", stdout_json=json_out,
                           callback=None if json_out else _human_sink)
    try:
        bp = Blueprint(hd)
        be = get_backend(backend_name, cfg, bp, hd, emitter)
    except Exception as e:
        emitter.close()
        fail(f"cannot start: {e}")

    try:
        for provider in auth.prompt_missing(cfg):
            UI.print(f"[muted]{provider} key accepted for this run only (not stored)[/]")
    except auth.AuthError as e:
        emitter.close()
        fail(f"auth: {e}")

    if not json_out and not cfg.auth.subscription:
        UI.warn(f"auth {cfg.auth.mode}: this run is billed per token")
    for issue in be.check():
        UI.warn(f"readiness: {issue}")
    if warning := auth.model_pin_warning(cfg):
        UI.warn(f"auth: {warning}")
    if not json_out:
        UI.info(f"[title]{UI.i('run')} {client}[/] [muted]{slug} · {backend_name} · "
                f"{cfg.engine.tier} · as of {as_of}[/]")

    result = asyncio.run(be.run(job))
    emitter.close()

    if json_out:
        emit_json({"result": _result_dict(result)})
    else:
        _print_result(result, backend_name)
    raise typer.Exit(0 if result.dossier else 1)


app.command("run", cls=F.VantageCommand)(run)
app.command("generate", cls=F.VantageCommand,
            help="Alias of `run`: produce a dossier end to end.")(run)


def _result_dict(r) -> dict:  # noqa: ANN001
    return {
        "slug": r.slug, "run_dir": r.run_dir, "dossier": r.dossier,
        "entity": r.entity, "ownership_form": r.ownership_form,
        "jurisdictions": r.jurisdictions, "vertical_module": r.vertical_module,
        "vertical_confidence": r.vertical_confidence,
        "entity_ambiguity": r.entity_ambiguity,
        "agents_ok": r.agents_ok, "agents_total": r.agents_total,
        "verification": r.verification, "usage": r.usage, "errors": r.errors,
    }


def _print_result(r, backend_name: str) -> None:  # noqa: ANN001
    grid = Table.grid(padding=(0, 2))
    grid.add_column(style="muted")
    grid.add_column()
    grid.add_row("backend", backend_name)
    grid.add_row("agents", f"{r.agents_ok}/{r.agents_total} ok")
    grid.add_row("tokens", f"{r.usage.get('input_tokens', 0)} in / "
                           f"{r.usage.get('output_tokens', 0)} out")
    if r.entity_ambiguity:
        grid.add_row("entity", f"[warn]ambiguity recorded: {r.entity_ambiguity}[/]")
    v = r.verification or {}
    if v:
        grid.add_row("verify", f"{UI.result(v.get('result'))} · Overall Confidence "
                     f"{UI.band(v.get('overall_confidence'))} (EQI {v.get('eqi')}) · "
                     f"{v.get('blockers', 0)}B/{v.get('majors', 0)}M/{v.get('minors', 0)}m")
        if topics := (v.get("budget_limited_topics") or []):
            grid.add_row("", f"[warn]stopped on budget (not diminishing returns): "
                             f"{', '.join(topics)}[/]")
    if r.errors:
        grid.add_row("issues", f"[warn]{len(r.errors)}[/]")
        for e in r.errors[:8]:
            grid.add_row("", f"[warn]- {e}[/]")
    grid.add_row("dossier", f"[title]{r.dossier or '(none)'}[/]")
    UI.err.rule(f"[title]{UI.i('done')} run complete[/]")
    UI.print(grid)
    if v.get("overall_confidence") == "Insufficient":
        UI.print(Panel(
            f"[loud] {UI.i('stop')} DO NOT PRESENT [/]\n"
            "Overall Confidence is Insufficient — do not present. Re-run with better sources or "
            "reduce scope.", border_style="fail", expand=False))


# ── backends / doctor ─────────────────────────────────────────────────────────────────────────
def _backend_rows(cfg: Config) -> list[dict]:
    hd = harness_dir(cfg)
    bp = Blueprint(hd)
    rows = []
    for name in BACKENDS:
        try:
            issues = list(get_backend(name, cfg, bp, hd).check())
        except Exception as e:  # a broken optional backend must not hide the others
            issues = [f"{type(e).__name__}: {e}"]
        rows.append({"name": name, "ready": not issues, "issues": issues})
    return rows


@app.command(cls=F.VantageCommand)
def backends(
    ctx: typer.Context,
    json_out: bool = typer.Option(False, "--json", help="Machine-readable output on stdout."),
) -> None:
    """List execution backends and their readiness."""
    cfg = load_cfg(ctx)
    rows = _backend_rows(cfg)
    if json_out:
        emit_json({"default": cfg.engine.backend, "backends": rows})
        return
    t = Table(title=f"{UI.i('backend')} backends", title_justify="left")
    for col in ("backend", "default", "ready", "notes"):
        t.add_column(col, overflow="fold")
    for r in rows:
        t.add_row(f"[key]{r['name']}[/]", UI.i("star") if r["name"] == cfg.engine.backend else "",
                  UI.status_cell("ok" if r["ready"] else "warn"), "; ".join(r["issues"]))
    UI.print(t)


def _config_drift(cfg) -> list[str]:  # noqa: ANN001
    """Report a user config that predates the v3 harness rather than letting it degrade a run."""
    from ..blueprint.stages import AGENTS, WAVE_A

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
    return issues


def _check(group: str, name: str, status: str, detail: str) -> dict:
    return {"group": group, "name": name, "status": status, "detail": detail}


def doctor_checks(cfg: Config) -> list[dict]:
    """Every doctor check as ``{group, name, status: ok|warn|fail, detail}``."""
    import shutil

    hd = harness_dir(cfg)
    out_root = output_dir(cfg)
    checks = [
        _check("engine", "version", "ok", f"Vantage {__version__} · harness {HARNESS_VERSION} · "
                                          f"config {CONFIG_VERSION}"),
        _check("engine", "python", "ok", sys.version.split()[0]),
        _check("engine", "user config", "ok" if USER_CONFIG.exists() else "warn",
               f"{USER_CONFIG}" + ("" if USER_CONFIG.exists() else " (will be created)")),
        _check("engine", "harness", "ok" if hd.exists() else "fail",
               f"{hd}" + ("" if hd.exists() else " MISSING")),
        _check("engine", "output dir", "ok" if out_root.exists() else "warn",
               f"{out_root}" + ("" if out_root.exists() else " (will be created)")),
        _check("engine", "defaults", "ok", f"backend {cfg.engine.backend} · tier "
                                           f"{cfg.engine.tier} · concurrency "
                                           f"{cfg.engine.max_concurrency}"),
    ]
    drift = _config_drift(cfg)
    for issue in drift:
        checks.append(_check("harness", "config drift", "warn", issue))
    if drift:
        checks.append(_check("harness", "fix", "warn",
                             "run `vantage config migrate` to fix the above"))
    else:
        checks.append(_check("harness", "roster", "ok", "config matches the v3.0.0 agent roster"))
    checks += auth_checks(cfg)
    for label, env in (("Tavily", "TAVILY_API_KEY"), ("SEC EDGAR id", "SEC_EDGAR_IDENTITY")):
        checks.append(_check("tools", label, "ok" if os.environ.get(env) else "warn",
                             f"{env} {'set' if os.environ.get(env) else 'unset'}"))
    for r in _backend_rows(cfg):
        checks.append(_check("backends", r["name"], "ok" if r["ready"] else "warn",
                             "ready" if r["ready"] else "; ".join(r["issues"])))
    checks += _export_checks(cfg)
    prefix, reason = T.resolve_tui(REPO_ROOT)
    checks.append(_check("tui", "launcher", "ok" if prefix else "warn",
                         " ".join(prefix) if prefix else f"{reason} Build: {T.BUILD_HINT}"))
    checks.append(_check("tui", "node", "ok" if shutil.which("node") else "warn",
                         shutil.which("node") or "node not on PATH (Node.js 18+ needed for the TUI)"))
    return checks


def _export_checks(cfg: Config) -> list[dict]:
    try:
        import importlib

        api = importlib.import_module("vantage.export.api")
    except ImportError as e:
        return [_check("export", "module", "warn",
                       f"export unavailable ({e}); install with: uv sync --extra export")]
    try:
        out = []
        for c in api.doctor(cfg):
            get = c.get if isinstance(c, dict) else (lambda k, _c=c: getattr(_c, k, None))
            out.append(_check(str(get("group") or "export"), str(get("name") or ""),
                              str(get("status") or "warn"), str(get("detail") or "")))
        return out
    except Exception as e:
        return [_check("export", "doctor", "fail", f"{type(e).__name__}: {e}")]


@app.command(cls=F.VantageCommand)
def doctor(
    ctx: typer.Context,
    json_out: bool = typer.Option(False, "--json", help="Machine-readable output on stdout."),
) -> None:
    """Environment, configuration, auth, backend, export and TUI diagnostics."""
    cfg = load_cfg(ctx)
    checks = doctor_checks(cfg)
    if json_out:
        emit_json({"version": __version__, "checks": checks})
        return
    UI.print(f"[title]{UI.i('doctor')} Vantage {__version__}[/] [muted]{TAGLINE}[/]")
    t = Table(show_header=True, title_justify="left")
    for col in ("group", "check", "status", "detail"):
        t.add_column(col, overflow="fold")
    group = None
    for c in checks:
        if UI.quiet and c["status"] == "ok":
            continue
        g = c["group"] if c["group"] != group else ""
        group = c["group"]
        t.add_row(f"[title]{g}[/]", c["name"], UI.status_cell(c["status"]), c["detail"])
    UI.print(t)
    fails = sum(c["status"] == "fail" for c in checks)
    warns = sum(c["status"] == "warn" for c in checks)
    UI.print(f"[muted]{len(checks)} checks · {warns} warn · {fails} fail[/]")


# ── deploy / serve / version / options / tui / export ─────────────────────────────────────────
@app.command(cls=F.VantageCommand)
def deploy(
    ctx: typer.Context,
    target: str | None = typer.Option(None, "--target", "-t", help="gcp|azure|aws"),
    build: bool = typer.Option(True, "--build/--no-build", help="Build+push the image first"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print the commands without running"),
) -> None:
    """Build the container and deploy the engine to a cloud target."""
    from ..cloud import deploy as _deploy

    cfg = load_cfg(ctx)
    tgt = target or cfg.cloud.target
    code = _deploy(cfg, tgt, build=build, dry_run=dry_run, console=UI.err)
    raise typer.Exit(code)


@app.command(cls=F.VantageCommand)
def serve(
    host: str = typer.Option("0.0.0.0", "--host"),
    port: int = typer.Option(0, "--port", help="0 = $PORT or 8080"),
) -> None:
    """Run the engine as an HTTP service (GET /healthz, POST /run) — for cloud service deploys."""
    from ..server import serve as _serve

    _serve(host=host, port=port or None)


@app.command(cls=F.VantageCommand)
def version(
    json_out: bool = typer.Option(False, "--json", help="Machine-readable output on stdout."),
) -> None:
    """Print the engine version."""
    if json_out:
        emit_json({"version": __version__, "harness": HARNESS_VERSION, "config": CONFIG_VERSION,
                   "python": sys.version.split()[0]})
    else:
        typer.echo(__version__)


app.command("options", cls=F.VantageCommand)(options_cmd)
app.command("export", cls=F.VantageCommand)(export_cmd)


@app.command("tui", cls=F.VantageCommand,
             context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def tui_cmd(ctx: typer.Context) -> None:
    """Launch the Ink TUI (same as `vantage --tui`); extra arguments are forwarded."""
    _launch_tui(ctx, list(ctx.args))


# ── completion ────────────────────────────────────────────────────────────────────────────────
def _completion(shell: str, install: bool, prog: str) -> None:
    if install:
        path, notes = C.install(shell, prog)
        UI.ok(f"wrote {shell} completion for {prog} to {path}")
        for n in notes:
            UI.info(f"  [muted]{UI.i('arrow')} {n}[/]")
    else:
        sys.stdout.write(C.script(shell, prog))


def _make_completion_cmd(shell: str):  # noqa: ANN202
    def cmd(
        install: bool = typer.Option(False, "--install", help="Write it to the user completion "
                                                              "dir and say where."),
        prog: str = typer.Option("vantage", "--prog-name", help="vantage | vantage-engine"),
    ) -> None:
        _completion(shell, install, prog)

    cmd.__doc__ = f"Print (or --install) the {shell} completion script."
    return cmd


for _shell in C.SHELLS:
    completion_app.command(_shell, cls=F.VantageCommand)(_make_completion_cmd(_shell))


def main() -> None:
    # Some optional framework deps (crewai → chromadb) still import pydantic.v1 and warn on
    # Python 3.14+. The warning is benign and must not pollute CLI output.
    warnings.filterwarnings("ignore", message=r"Core Pydantic V1", category=UserWarning)
    prog = os.path.basename(sys.argv[0]) if sys.argv and sys.argv[0] else "vantage"
    if prog not in C.PROGS:
        prog = "vantage"
    app(prog_name=prog)


if __name__ == "__main__":
    main()
