"""``vantage config …`` and ``vantage options``."""

from __future__ import annotations

import datetime as _dt
import json
import os
import re
import shlex
import subprocess
from pathlib import Path
from typing import Annotated, Any

import typer
from pydantic import ValidationError
from rich.table import Table

from ..models.config import Config
from . import flags as F
from .common import config_path, emit_json, fail, load_cfg, open_path, pkg
from .ui import UI

config_app = typer.Typer(no_args_is_help=True, cls=F.VantageSubGroup,
                         help="Inspect and manage configuration.")

_SECRET_KEY = re.compile(r"(api_?key|secret|token|password|passwd)$", re.I)
_SECRET_VALUE = re.compile(r"^(sk-[A-Za-z0-9_-]{16,}|sk-ant-|AIza[0-9A-Za-z_-]{20,}|tvly-|"
                           r"ghp_|xox[abp]-)")


def _user_file(ctx: typer.Context) -> Path:
    explicit = config_path(ctx)
    if explicit:
        return Path(explicit).expanduser()
    env = os.environ.get("VANTAGE_CONFIG")
    if env:
        return Path(env).expanduser()
    return pkg().ensure_user_config()


def _read(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
    except ValueError as e:
        fail(f"{path} is not valid JSON: {e}")
    return data if isinstance(data, dict) else {}


def _get(data: Any, path: tuple[str, ...]) -> Any:
    cur = data
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            raise KeyError(".".join(path))
        cur = cur[key]
    return cur


def _validate_merged(user: dict) -> None:
    from ..settings import _deep_merge

    shipped = json.loads(pkg().REPO_DEFAULT.read_text()) if pkg().REPO_DEFAULT.exists() else {}
    Config.model_validate(_deep_merge(shipped, user))


def _print_validation(e: ValidationError) -> None:
    for err in e.errors():
        loc = ".".join(str(p) for p in err.get("loc", ()))
        UI.print(f"  [key]{loc}[/]: {err.get('msg')}")


@config_app.command("show", cls=F.VantageCommand)
def config_show(
    ctx: typer.Context,
    json_out: bool = typer.Option(False, "--json", help="Compact JSON (default: indented)."),
) -> None:
    """Print the merged effective configuration (shipped < user file < env < flags) as JSON."""
    cfg = load_cfg(ctx)
    data = cfg.model_dump(mode="json")
    if json_out:
        emit_json(data)
    else:
        typer.echo(json.dumps(data, indent=2))


@config_app.command("get", cls=F.VantageCommand)
def config_get(
    ctx: typer.Context,
    key: str = typer.Argument(..., help="Dotted key, e.g. engine.max_concurrency"),
    json_out: bool = typer.Option(False, "--json", help="Always print the value as JSON."),
) -> None:
    """Print one effective config value (strings raw, everything else as JSON)."""
    cfg = load_cfg(ctx)
    try:
        value = _get(cfg.model_dump(mode="json"), tuple(k for k in key.split(".") if k))
    except KeyError:
        fail(f"no config key '{key}'", 1)
    if isinstance(value, str) and not json_out:
        typer.echo(value)
    else:
        typer.echo(json.dumps(value, indent=None if json_out else 2))


@config_app.command("set", cls=F.VantageCommand)
def config_set(
    ctx: typer.Context,
    key: str = typer.Argument(..., help="Dotted key, e.g. export.depth"),
    value: str = typer.Argument(..., help="Value; JSON-parsed (8, true, null, [\"pptx\"]) else a "
                                          "string."),
) -> None:
    """Persist one value to the user config file (validated first; never stores secrets)."""
    try:
        path_t = F.check_key(key)
    except ValueError as e:
        fail(str(e))
    parsed = F.parse_value(value)
    last = path_t[-1]
    if (_SECRET_KEY.search(last) and not last.endswith("_env")) or (
            isinstance(parsed, str) and _SECRET_VALUE.match(parsed)):
        fail("refusing to write what looks like a credential to the config file. Keys belong in "
             "environment variables; set the *_env key to the variable's NAME instead.")
    target = _user_file(ctx)
    data = _read(target)
    F.set_path(data, path_t, parsed)
    try:
        _validate_merged(data)
    except ValidationError as e:
        UI.error(f"{key} = {value!r} would make the configuration invalid")
        _print_validation(e)
        raise typer.Exit(2) from e
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, indent=2) + "\n")
    typer.echo(f"{'.'.join(path_t)} = {json.dumps(parsed)}  ({target})")
    if path_t == ("auth", "mode") and parsed == "api-key":
        UI.warn("Runs are now billed per token. Export the provider key, or pass --ask-key to be "
                "prompted per run.")


@config_app.command("unset", cls=F.VantageCommand)
def config_unset(
    ctx: typer.Context,
    key: str = typer.Argument(..., help="Dotted key to remove from the user config file"),
) -> None:
    """Remove one key from the user config file (the shipped default applies again)."""
    target = _user_file(ctx)
    data = _read(target)
    path_t = tuple(k for k in key.split(".") if k)
    try:
        parent = _get(data, path_t[:-1]) if len(path_t) > 1 else data
        if not isinstance(parent, dict) or path_t[-1] not in parent:
            raise KeyError(key)
    except KeyError:
        fail(f"'{key}' is not set in {target}", 1)
    del parent[path_t[-1]]
    try:
        _validate_merged(data)
    except ValidationError as e:
        UI.error(f"removing {key} would make the configuration invalid")
        _print_validation(e)
        raise typer.Exit(2) from e
    target.write_text(json.dumps(data, indent=2) + "\n")
    typer.echo(f"unset {key}  ({target})")


@config_app.command("path", cls=F.VantageCommand)
def config_path_cmd() -> None:
    """Print the user config path (creating it from the template if missing)."""
    typer.echo(str(pkg().ensure_user_config()))


@config_app.command("init", cls=F.VantageCommand)
def config_init(
    force: bool = typer.Option(False, "--force", help="Replace an existing file (kept as .bak)."),
) -> None:
    """Create ~/.config/vantage/default.json from the template."""
    p = pkg()
    if force and p.USER_CONFIG.exists():
        stamp = _dt.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        backup = p.USER_CONFIG.with_name(f"default.json.{stamp}.bak")
        backup.write_text(p.USER_CONFIG.read_text())
        p.USER_CONFIG.unlink()
        UI.info(f"previous file kept at {backup}")
    path = p.ensure_user_config()
    typer.echo(f"user config at {path}")


@config_app.command("migrate", cls=F.VantageCommand)
def config_migrate(
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would change, write nothing"),
) -> None:
    """Bring ~/.config/vantage/default.json up to the current schema.

    Reconciles role_model_map against the live agent roster, and fills in keys the shipped template
    has gained. The previous file is kept alongside as `.bak`.
    """
    p = pkg()
    path = p.USER_CONFIG
    user = json.loads(path.read_text()) if path.exists() else {}
    template = json.loads(p.REPO_DEFAULT.read_text())
    merged, changes = p.migrate_user_config(user, template)
    Config.model_validate(merged)

    if not changes:
        if not dry_run:
            p.ensure_user_schema()
        typer.echo(f"{path} is already current — nothing to do.")
        return
    for line in changes:
        UI.print(f"  [accent]{UI.i('bullet')}[/] {line}")
    if dry_run:
        UI.print("[muted]--dry-run: nothing written[/]")
        return

    path.parent.mkdir(parents=True, exist_ok=True)
    stamp = _dt.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    backup = path.with_name(f"default.json.{stamp}.bak")
    if path.exists():
        backup.write_text(path.read_text())
    path.write_text(json.dumps(merged, indent=2) + "\n")
    p.ensure_user_schema()
    typer.echo(f"migrated {path}  (previous file kept at {backup})")


@config_app.command("edit", cls=F.VantageCommand)
def config_edit(ctx: typer.Context) -> None:
    """Open the user config in $VISUAL / $EDITOR (else the system handler), then validate it."""
    target = _user_file(ctx)
    editor = os.environ.get("VISUAL") or os.environ.get("EDITOR")
    if editor:
        subprocess.call([*shlex.split(editor), str(target)])
        _validate_file(target)
    else:
        open_path(target)
        UI.info(f"opened {target} — run `vantage config validate` when done")


def _validate_file(path: Path) -> bool:
    try:
        data = json.loads(path.read_text())
    except OSError as e:
        UI.error(f"cannot read {path}: {e}")
        return False
    except ValueError as e:
        UI.error(f"{path} is not valid JSON: {e}")
        return False
    ok = True
    try:
        _validate_merged(data if isinstance(data, dict) else {})
    except ValidationError as e:
        UI.error(f"{path} does not validate against the config model")
        _print_validation(e)
        ok = False
    schema_file = pkg().REPO_SCHEMA
    if ok and schema_file.exists():
        try:
            import jsonschema
        except ImportError:
            jsonschema = None
        if jsonschema is not None:
            try:
                jsonschema.validate(data, json.loads(schema_file.read_text()))
            except jsonschema.ValidationError as e:
                UI.error(f"{path}: {e.message} (at {'/'.join(str(p) for p in e.absolute_path)})")
                ok = False
    if ok:
        UI.ok(f"{path} is valid")
    return ok


@config_app.command("validate", cls=F.VantageCommand)
def config_validate(
    ctx: typer.Context,
    path: Annotated[Path | None, typer.Argument(
        help="Config file (default: the user config)")] = None,
) -> None:
    """Validate a config file against the model (and the JSON schema when jsonschema is installed)."""
    target = path or _user_file(ctx)
    raise typer.Exit(0 if _validate_file(Path(target).expanduser()) else 1)


@config_app.command("schema", cls=F.VantageCommand)
def config_schema() -> None:
    """Print the config JSON schema."""
    schema_file = pkg().REPO_SCHEMA
    if schema_file.exists():
        typer.echo(schema_file.read_text().rstrip())
    else:
        typer.echo(json.dumps(Config.model_json_schema(), indent=2))


# ── options listing ───────────────────────────────────────────────────────────────────────────
def _global_rows() -> list[dict]:
    rows = []
    for opt in F.GLOBAL_OPTS:
        t = opt.type
        if opt.is_flag:
            typ = "flag"
        elif t is not None and hasattr(t, "choices"):
            typ = f"choice[{'|'.join(map(str, t.choices))}]"
        elif t is not None:
            typ = getattr(t, "name", "text")
        else:
            typ = "list[text]" if opt.multiple else "text"
        rows.append({
            "flag": ", ".join(opt.decls), "negative": None, "key": opt.key, "type": typ,
            "choices": list(map(str, t.choices)) if t is not None and hasattr(t, "choices") else None,
            "multiple": opt.multiple, "nullable": False, "default": None,
            "env": ["VANTAGE_CONFIG"] if opt.name == "config" else [],
            "description": opt.help, "group": "global",
        })
    rows.append({"flag": "--tui", "negative": None, "key": None, "type": "flag", "choices": None,
                 "multiple": False, "nullable": False, "default": None, "env": [],
                 "description": "Launch the Ink TUI, forwarding the remaining arguments "
                                "(root only).", "group": "global"})
    return rows


def all_option_rows() -> list[dict]:
    return _global_rows() + [dict(s.as_dict(), group="config") for s in F.config_flag_specs()]


def options_cmd(
    json_out: bool = typer.Option(False, "--json", help="Machine-readable list on stdout."),
    grep: str | None = typer.Option(None, "--filter", help="Only flags/keys containing TEXT."),
) -> None:
    """List every CLI option — the friendly globals and one flag per config key."""
    rows = all_option_rows()
    if grep:
        g = grep.lower()
        rows = [r for r in rows if g in (r["flag"] or "").lower() or g in (r["key"] or "").lower()
                or g in (r["description"] or "").lower()]
    if json_out:
        emit_json({"options": rows})
        return
    t = Table(title="vantage options — accepted before or after any command",
              title_justify="left", show_lines=False, expand=False)
    for col in ("flag", "type", "default", "env", "description"):
        t.add_column(col, overflow="fold")
    group = None
    for r in rows:
        if r["group"] != group:
            group = r["group"]
            t.add_row(f"[title]{'global' if group == 'global' else 'config keys'}[/]", "", "", "", "")
        flag = r["flag"] + (f" / {r['negative']}" if r.get("negative") else "")
        default = "" if r["group"] == "global" else json.dumps(r["default"])
        t.add_row(f"[key]{flag}[/]", r["type"], default, " ".join(r["env"]), r["description"] or "")
    UI.print(t)
    UI.print("[muted]Also: --set dotted.key=value for any key (JSON-parsed), "
             "--role-model agent=tier, and `null` clears an optional value.[/]")


config_app.command("options", cls=F.VantageCommand)(options_cmd)
