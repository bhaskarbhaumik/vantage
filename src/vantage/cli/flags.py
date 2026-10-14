"""Every configuration key is a CLI flag — generated, not hand-written.

The pydantic :class:`~vantage.models.config.Config` model is walked once; every leaf becomes a
kebab-case option (``engine.max_concurrency`` -> ``--engine-max-concurrency``). Open-ended map
sections (``providers.<name>``, ``cloud.<target>``) are expanded from the shipped
``config/default.json`` so each shipped key gets a flag too. ``role_model_map`` has its own
repeatable ``--role-model agent=tier`` and anything else can be reached with
``--set dotted.key=value``.

Type mapping: ``Literal`` -> choice, ``bool`` -> ``--x/--no-x`` pair, ``list`` -> repeatable,
optional fields accept the literal value ``null`` to clear them.

The options are injected into the root command *and* into every subcommand (lazily, as the
command is resolved), so ``vantage --tier STANDARD run …`` and ``vantage run --tier STANDARD …``
are equivalent. Values are recorded on the root context in parse order and become the
``overrides`` passed to :func:`vantage.settings.load_config` (highest precedence). On the root
command each flag also reads ``VANTAGE_<DOTTED_KEY>`` from the environment (lower than a flag).
"""

from __future__ import annotations

import inspect
import json
import re
import types as _pytypes
import typing
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import Any, Literal, get_args, get_origin

from pydantic import BaseModel
from typer.core import TyperCommand, TyperGroup, TyperOption

try:  # Typer >= 0.20 vendors Click
    from typer._click import types as click_types
    from typer._click.core import ParameterSource
    from typer._click.shell_completion import CompletionItem
except ImportError:  # pragma: no cover - older Typer on real Click
    import click.types as click_types  # type: ignore[no-redef]
    from click.core import ParameterSource  # type: ignore[no-redef]
    from click.shell_completion import CompletionItem  # type: ignore[no-redef]
try:
    from typer._types import TyperChoice as _Choice
except ImportError:  # pragma: no cover
    from click import Choice as _Choice  # type: ignore[no-redef]

from ..models.config import AUTH_MODES, DEFAULT_BACKENDS, Config, EngineCfg
from ..settings import REPO_DEFAULT

#: Top-level fields that are not options (schema version) or have a bespoke flag (role map).
SKIP_TOP = frozenset({"version", "role_model_map"})
#: Env vars ``settings.load_config`` already understands — listed alongside the generated ones.
LEGACY_ENV = {
    "engine.backend": "VANTAGE_BACKEND",
    "engine.tier": "VANTAGE_TIER",
    "engine.output_dir": "VANTAGE_OUTPUT_DIR",
    "engine.harness_dir": "VANTAGE_HARNESS_DIR",
    "auth.mode": "VANTAGE_AUTH_MODE",
}
ROLE_TIERS = ("synthesis", "research", "cheap")
NULL = "null"

_META_OVERRIDES = "vantage.cli.overrides"
_META_SEQ = "vantage.cli.seq"
META_CONFIG_PATH = "vantage.cli.config_path"
META_QUIET = "vantage.cli.quiet"
META_VERBOSE = "vantage.cli.verbose"
META_TUI = "vantage.cli.tui"

PANEL_GLOBAL = "Global options"


# ── leaf model ────────────────────────────────────────────────────────────────────────────────
@dataclass(frozen=True)
class FlagSpec:
    """One config leaf exposed as a CLI flag."""

    path: tuple[str, ...]
    kind: str  # "bool" | "int" | "float" | "str" | "choice"
    choices: tuple[str, ...] = ()
    multiple: bool = False
    nullable: bool = False
    negatable: bool = True  # bool only: False for Literal[True]
    default: Any = None
    help: str = ""

    @property
    def dotted(self) -> str:
        return ".".join(self.path)

    @property
    def flag(self) -> str:
        return "--" + "-".join(p.replace("_", "-") for p in self.path)

    @property
    def negative(self) -> str | None:
        if self.kind == "bool" and self.negatable and not self.multiple:
            return "--no-" + self.flag[2:]
        return None

    @property
    def param_name(self) -> str:
        return "cfg__" + "__".join(re.sub(r"\W", "_", p) for p in self.path)

    @property
    def envvar(self) -> str:
        return "VANTAGE_" + "_".join(re.sub(r"\W", "_", p).upper() for p in self.path)

    @property
    def env_vars(self) -> list[str]:
        legacy = LEGACY_ENV.get(self.dotted)
        return [self.envvar] + ([legacy] if legacy and legacy != self.envvar else [])

    @property
    def type_label(self) -> str:
        base = f"choice[{'|'.join(self.choices)}]" if self.kind == "choice" else self.kind
        if self.nullable:
            base += "|null"
        return f"list[{base}]" if self.multiple else base

    @property
    def flags_label(self) -> str:
        return f"{self.flag}/{self.negative}" if self.negative else self.flag

    def as_dict(self) -> dict:
        return {
            "flag": self.flag, "negative": self.negative, "key": self.dotted,
            "type": self.type_label, "choices": list(self.choices) or None,
            "multiple": self.multiple, "nullable": self.nullable, "default": self.default,
            "env": self.env_vars, "description": self.help,
        }


#: Descriptions for leaves the model does not document (fnmatch patterns, first match wins).
_HELP: tuple[tuple[str, str], ...] = (
    ("engine.backend", "Execution backend. workflow runs on the Claude subscription."),
    ("engine.available_backends", "Backends offered by the TUI picker."),
    ("engine.output_dir", "Root of the run tree; each run is <output_dir>/<slug>."),
    ("engine.harness_dir", "Prompt/blueprint library. null = the bundled harness."),
    ("engine.tool_result_max_chars", "Truncate each tool result to this many characters."),
    ("engine.tool_timeout_seconds", "Seconds before one tool call is abandoned."),
    ("auth.mode", "subscription (Claude plan, reads no key) | api-key (billed per token)."),
    ("auth.model_env", "Env var that pins every anthropic-routed agent to one model "
                       "(api-key mode)."),
    ("models.*.provider", "Provider serving this model tier."),
    ("models.*.model", "Model id for this tier."),
    ("models.*.max_tokens", "Output-token cap for this tier. null = models.max_tokens."),
    ("models.*.temperature", "Sampling temperature for this tier. null = models.temperature."),
    ("models.*.effort", "Reasoning effort for this tier. null = provider default."),
    ("models.temperature", "Default sampling temperature."),
    ("models.max_tokens", "Default output-token cap per agent turn."),
    ("models.thinking.enabled", "Extended thinking on supported models."),
    ("models.thinking.mode", "auto picks adaptive or budgeted thinking per model."),
    ("models.thinking.budget_tokens", "Thinking budget when mode is enabled."),
    ("models.thinking.effort", "Thinking effort when mode is adaptive."),
    ("providers.*.enabled", "Allow routing agents to this provider."),
    ("providers.*.api_key_env", "Env var holding this provider's key (the name, never the key)."),
    ("providers.*.default_model", "Model used when a role names this provider without a model."),
    ("providers.*.timeout_seconds", "Per-request timeout."),
    ("providers.*.max_attempts", "Attempts per request, including the first."),
    ("providers.*.retry_min_seconds", "Minimum back-off between retries."),
    ("providers.*.retry_max_seconds", "Maximum back-off between retries."),
    ("tools.web_search.enabled", "Web search tool for research agents."),
    ("tools.web_search.provider", "Search provider."),
    ("tools.web_search.api_key_env", "Env var holding the search key (the name, never the key)."),
    ("tools.web_search.max_results", "Results per query."),
    ("tools.web_search.search_depth", "Provider search depth."),
    ("tools.web_search.timeout_seconds", "Seconds before a search is abandoned."),
    ("tools.web_search.snippet_max_chars", "Truncate each result snippet."),
    ("tools.edgar.enabled", "SEC EDGAR filings tool."),
    ("tools.edgar.identity_env", "Env var holding the SEC User-Agent identity."),
    ("tools.edgar.filings_limit", "Filings listed per lookup."),
    ("tools.edgar.statement_max_chars", "Truncate each financial statement."),
    ("tools.market_data.enabled", "Market-data tool (quotes, multiples)."),
    ("cloud.target", "Default target for `vantage deploy`."),
    ("cloud.image", "Container image name."),
    ("cloud.*.*", "Cloud deploy setting."),
    ("run_defaults.primary_geography", "Default for run --geography."),
    ("run_defaults.target_vertical", "Default for run --vertical."),
    ("run_defaults.ticker_or_private", "Default for run --ticker."),
    ("run_defaults.capability_pack", "Default for run --capability-pack."),
    ("run_defaults.account_team_input_sheet", "Default for run --input-sheet."),
    ("run_defaults.account_context", "Default for run --account-context."),
    ("run_defaults.known_relationship_context", "Default for run --relationship."),
    ("run_defaults.strategic_pursuit_objectives", "Default for run --objectives."),
    ("output.formats", "Dossier formats the engine writes (Markdown only)."),
    ("output.keep_state", "Keep state/ and qa/ next to the dossier (always on)."),
    ("export.formats", "Default `vantage export` formats (pdf implies docx)."),
    ("ui.theme", "Colour theme for the CLI and TUI."),
)


def _default_help(dotted: str) -> str:
    from fnmatch import fnmatchcase

    for pattern, text in _HELP:
        if fnmatchcase(dotted, pattern):
            return text
    return ""


def _unwrap_optional(tp: Any) -> tuple[Any, bool]:
    if get_origin(tp) in (typing.Union, _pytypes.UnionType):
        args = get_args(tp)
        rest = [a for a in args if a is not type(None)]
        if len(rest) == 1:
            return rest[0], len(rest) < len(args)
    return tp, False


def _is_model(tp: Any) -> bool:
    return inspect.isclass(tp) and issubclass(tp, BaseModel)


@cache
def _field_comments(cls: type) -> dict[str, str]:
    """``#:`` comments and docstring-less field docs, keyed by field name, from the class source."""
    out: dict[str, str] = {}
    try:
        src = inspect.getsource(cls)
    except (OSError, TypeError):
        return out
    pending: list[str] = []
    for line in src.splitlines():
        s = line.strip()
        if s.startswith("#:"):
            pending.append(s[2:].strip())
            continue
        m = re.match(r"(\w+)\s*:", s)
        if m and pending:
            out[m.group(1)] = " ".join(pending)
        pending = []
    return out


def _leaf(path: tuple[str, ...], tp: Any, default: Any, help_: str) -> FlagSpec:
    tp, nullable = _unwrap_optional(tp)
    multiple = False
    if get_origin(tp) is list or tp is list:
        multiple = True
        args = get_args(tp)
        tp = args[0] if args else str
        tp, inner_null = _unwrap_optional(tp)
        nullable = nullable or inner_null
    if get_origin(tp) is Literal:
        values = get_args(tp)
        if all(isinstance(v, bool) for v in values):
            return FlagSpec(path, "bool", negatable=len(set(values)) > 1, default=default,
                            help=help_)
        return FlagSpec(path, "choice", tuple(str(v) for v in values), multiple, nullable,
                        default=default, help=help_)
    kind = {bool: "bool", int: "int", float: "float"}.get(tp, "str")
    if tp is Any or tp is object:
        kind = _kind_of(default)
    return FlagSpec(path, kind, (), multiple, nullable, default=default, help=help_)


def _kind_of(value: Any) -> str:
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "float"
    return "str"


def _walk(model: type[BaseModel], prefix: tuple[str, ...], shipped: dict) -> Iterator[FlagSpec]:
    comments = _field_comments(model)
    for name, field in model.model_fields.items():
        if not prefix and name in SKIP_TOP:
            continue
        path = prefix + (name,)
        tp, _ = _unwrap_optional(field.annotation)
        sub = shipped.get(name) if isinstance(shipped, dict) else None
        help_ = field.description or comments.get(name, "") or _default_help(".".join(path))
        if _is_model(tp):
            yield from _walk(tp, path, sub if isinstance(sub, dict) else {})
        elif tp is dict or get_origin(tp) is dict:
            args = get_args(tp)
            value_tp = args[1] if len(args) == 2 else Any
            for key, val in (sub or {}).items():
                if _is_model(value_tp):
                    yield from _walk(value_tp, path + (key,), val if isinstance(val, dict) else {})
                elif not isinstance(val, dict):
                    yield FlagSpec(path + (key,), _kind_of(val), nullable=val is None,
                                   default=val,
                                   help=_default_help(".".join(path + (key,)))
                                   or f"{'.'.join(path)} setting '{key}'.")
        else:
            if isinstance(shipped, dict) and name in shipped:
                default = shipped[name]
            elif field.default_factory is not None:
                default = field.default_factory()  # type: ignore[call-arg]
            else:
                default = field.default
            if isinstance(default, BaseModel):
                default = default.model_dump(mode="json")
            yield _leaf(path, field.annotation, default, help_)


def shipped_defaults() -> dict:
    try:
        return json.loads(Path(REPO_DEFAULT).read_text())
    except (OSError, ValueError):
        return {}


@cache
def config_flag_specs() -> tuple[FlagSpec, ...]:
    """Every config leaf as a :class:`FlagSpec` (cached; the model does not change at runtime)."""
    return tuple(_walk(Config, (), shipped_defaults()))


@cache
def _spec_by_param() -> dict[str, FlagSpec]:
    return {s.param_name: s for s in config_flag_specs()}


def config_leaf_paths() -> set[str]:
    return {s.dotted for s in config_flag_specs()}


# ── parameter types ───────────────────────────────────────────────────────────────────────────
class _Nullable(click_types.ParamType):
    """Wrap a type so the literal ``null`` clears an optional config value."""

    def __init__(self, inner: click_types.ParamType) -> None:
        self.inner = inner
        self.name = getattr(inner, "name", "text")

    def convert(self, value, param, ctx):  # noqa: ANN001
        if value is None or (isinstance(value, str) and value.strip().lower() == NULL):
            return None
        return self.inner.convert(value, param, ctx)

    def shell_complete(self, ctx, param, incomplete):  # noqa: ANN001
        items = list(self.inner.shell_complete(ctx, param, incomplete))
        if NULL.startswith(incomplete):
            items.append(CompletionItem(NULL))
        return items


def _param_type(spec: FlagSpec) -> click_types.ParamType:
    if spec.kind == "choice":
        choices = spec.choices + ((NULL,) if spec.nullable else ())
        t: click_types.ParamType = _Choice(choices)
        return _Nullable(t) if spec.nullable else t
    base = {"int": click_types.IntParamType(), "float": click_types.FloatParamType()}.get(
        spec.kind, click_types.StringParamType())
    return _Nullable(base) if spec.nullable else base


# ── override recording ────────────────────────────────────────────────────────────────────────
def _root_meta(ctx) -> dict:  # noqa: ANN001
    return ctx.find_root().meta


def record(ctx, path: tuple[str, ...], value: Any, *, rank: int = 1) -> None:  # noqa: ANN001
    """Remember one override. ``rank`` 0 = environment, 1 = command line (always wins)."""
    meta = _root_meta(ctx)
    seq = meta.get(_META_SEQ, 0)
    meta[_META_SEQ] = seq + 1
    meta.setdefault(_META_OVERRIDES, []).append((rank, seq, tuple(path), value))


def recorded(ctx) -> list[tuple[tuple[str, ...], Any]]:  # noqa: ANN001
    """Overrides in application order (env first, then flags in the order they were given)."""
    if ctx is None:
        return []
    items = sorted(_root_meta(ctx).get(_META_OVERRIDES, []), key=lambda r: (r[0], r[1]))
    return [(path, value) for _, _, path, value in items]


def set_path(data: dict, path: tuple[str, ...] | list[str], value: Any) -> dict:
    cur = data
    for key in path[:-1]:
        nxt = cur.get(key)
        if not isinstance(nxt, dict):
            nxt = {}
            cur[key] = nxt
        cur = nxt
    cur[path[-1]] = value
    return data


def overrides_from(ctx) -> dict:  # noqa: ANN001
    out: dict = {}
    for path, value in recorded(ctx):
        set_path(out, path, value)
    return out


def given_paths(ctx) -> dict[str, Any]:  # noqa: ANN001
    """Dotted key -> final value for everything set on the command line or via VANTAGE_* env."""
    return {".".join(p): v for p, v in recorded(ctx)}


def _source_rank(ctx, param) -> int | None:  # noqa: ANN001
    src = ctx.get_parameter_source(param.name)
    if src == ParameterSource.COMMANDLINE:
        return 1
    if src == ParameterSource.ENVIRONMENT:
        return 0
    return None


def _config_callback(ctx, param, value):  # noqa: ANN001
    rank = _source_rank(ctx, param)
    if rank is None or ctx.resilient_parsing:
        return value
    spec = _spec_by_param()[param.name]
    record(ctx, spec.path, list(value) if spec.multiple else value, rank=rank)
    return value


def parse_value(raw: str) -> Any:
    """JSON-parse ``raw`` (so ``8``, ``true``, ``null``, ``["a"]`` work); fall back to the string."""
    try:
        return json.loads(raw)
    except ValueError:
        return raw


def check_key(dotted: str) -> tuple[str, ...]:
    """Validate a dotted config key against the model. Raises ``ValueError`` with a hint."""
    path = tuple(p for p in dotted.strip().split(".") if p)
    if not path:
        raise ValueError("empty key")
    if path[0] not in Config.model_fields or path[0] == "version":
        raise ValueError(f"unknown config section '{path[0]}' "
                         f"(sections: {', '.join(k for k in Config.model_fields if k != 'version')})")
    if path[0] in ("providers", "cloud", "role_model_map"):
        return path  # open-ended maps; pydantic validates the value shape
    leaves = config_leaf_paths()
    joined = ".".join(path)
    if joined in leaves or any(leaf.startswith(joined + ".") for leaf in leaves):
        return path
    close = sorted(leaf for leaf in leaves if leaf.split(".")[-1] == path[-1])
    hint = f" — did you mean {', '.join(close[:3])}?" if close else ""
    raise ValueError(f"unknown config key '{joined}'{hint}")


def _set_callback(ctx, param, value):  # noqa: ANN001
    if _source_rank(ctx, param) != 1 or ctx.resilient_parsing:
        return value
    for item in value:
        key, sep, raw = item.partition("=")
        if not sep:
            raise _bad(f"--set expects dotted.key=value, got {item!r}", ctx, param)
        try:
            path = check_key(key)
        except ValueError as e:
            raise _bad(str(e), ctx, param) from None
        record(ctx, path, parse_value(raw))
    return value


def _role_callback(ctx, param, value):  # noqa: ANN001
    if _source_rank(ctx, param) != 1 or ctx.resilient_parsing:
        return value
    for item in value:
        agent, sep, tier = item.partition("=")
        tier = tier.strip().lower()
        if not sep or not agent.strip():
            raise _bad(f"--role-model expects agent=tier, got {item!r}", ctx, param)
        if tier not in ROLE_TIERS:
            raise _bad(f"tier must be one of {' | '.join(ROLE_TIERS)}, got {tier!r}", ctx, param)
        record(ctx, ("role_model_map", agent.strip()), tier)
    return value


def _bad(msg: str, ctx, param):  # noqa: ANN001
    try:
        from typer._click.exceptions import BadParameter
    except ImportError:  # pragma: no cover
        from click.exceptions import BadParameter  # type: ignore[no-redef]
    return BadParameter(msg, ctx=ctx, param=param)


# ── friendly global options ───────────────────────────────────────────────────────────────────
@dataclass(frozen=True)
class GlobalOpt:
    """A hand-named option accepted on every command."""

    decls: tuple[str, ...]
    name: str
    help: str
    apply: Callable[[Any, Any], None]  # (ctx, value) -> None
    type: Any = None
    is_flag: bool = False
    multiple: bool = False
    metavar: str | None = None
    root_only: bool = False
    is_eager: bool = False
    key: str | None = None  # config key it sets, for `vantage options`

    def make(self, taken: set[str], *, root: bool) -> TyperOption | None:
        decls = [d for d in self.decls if d not in taken]
        if not any(d.startswith("--") for d in decls):
            return None

        def cb(ctx, param, value):  # noqa: ANN001
            if _source_rank(ctx, param) != 1 or ctx.resilient_parsing:
                return value
            self.apply(ctx, value)
            return value

        return TyperOption(
            param_decls=[f"g__{self.name}", *decls], type=self.type, is_flag=self.is_flag or None,
            multiple=self.multiple, default=None if not self.is_flag else False,
            expose_value=False, callback=cb, help=self.help, metavar=self.metavar,
            is_eager=self.is_eager, rich_help_panel=PANEL_GLOBAL,
        )


def _setter(path: tuple[str, ...], transform: Callable[[Any], Any] = lambda v: v):
    return lambda ctx, v: record(ctx, path, transform(v))


def _meta_setter(key: str, value: Any = None):
    def apply(ctx, v):  # noqa: ANN001
        _root_meta(ctx)[key] = v if value is None else value
    return apply


GLOBAL_OPTS: tuple[GlobalOpt, ...] = (
    GlobalOpt(("--config",), "config", "Config file to merge over the shipped defaults "
              "(default ~/.config/vantage/default.json; env VANTAGE_CONFIG).",
              _meta_setter(META_CONFIG_PATH), metavar="PATH"),
    GlobalOpt(("--backend", "-b"), "backend", "Execution backend (engine.backend).",
              _setter(("engine", "backend")), type=_Choice(DEFAULT_BACKENDS), key="engine.backend"),
    GlobalOpt(("--tier", "-t"), "tier", "Output tier (engine.tier).",
              _setter(("engine", "tier"), str.upper),
              type=_Choice(typing.get_args(EngineCfg.model_fields["tier"].annotation),
                           case_sensitive=False), key="engine.tier"),
    GlobalOpt(("--auth", "-a"), "auth", "subscription (default: runs on your Claude plan, reads "
              "no API key) | api-key (billed per token, explicit opt-in).",
              _setter(("auth", "mode")), type=_Choice(AUTH_MODES), key="auth.mode"),
    GlobalOpt(("--output-dir",), "output_dir", "Run tree root (engine.output_dir).",
              _setter(("engine", "output_dir")), metavar="DIR", key="engine.output_dir"),
    GlobalOpt(("--max-concurrency",), "max_concurrency", "Concurrent agents "
              "(engine.max_concurrency).", _setter(("engine", "max_concurrency")),
              type=click_types.IntRange(1, 32), key="engine.max_concurrency"),
    GlobalOpt(("--set",), "set", "Set any config key: dotted.key=value (value JSON-parsed; "
              "repeatable).", lambda ctx, v: None, multiple=True, metavar="KEY=VALUE"),
    GlobalOpt(("--role-model",), "role_model", "Route an agent to a model tier: agent=tier "
              "(synthesis|research|cheap; repeatable).", lambda ctx, v: None, multiple=True,
              metavar="AGENT=TIER", key="role_model_map.<agent>"),
    GlobalOpt(("--icons",), "icons", "Icon set: nerd (Nerd Font, default) | unicode | ascii.",
              _setter(("ui", "icons")), type=_Choice(("nerd", "unicode", "ascii")), key="ui.icons"),
    GlobalOpt(("--ascii",), "ascii", "7-bit output (= --icons ascii).",
              lambda ctx, v: record(ctx, ("ui", "icons"), "ascii") if v else None, is_flag=True,
              key="ui.icons"),
    GlobalOpt(("--no-color",), "no_color", "Disable colour (also honours NO_COLOR).",
              lambda ctx, v: record(ctx, ("ui", "color"), "never") if v else None, is_flag=True,
              key="ui.color"),
    GlobalOpt(("--theme",), "theme", "Colour theme: dark | light.", _setter(("ui", "theme")),
              type=_Choice(("dark", "light")), key="ui.theme"),
    GlobalOpt(("--no-animations",), "no_animations", "No spinners or live redraws.",
              lambda ctx, v: record(ctx, ("ui", "animations"), False) if v else None,
              is_flag=True, key="ui.animations"),
    GlobalOpt(("--quiet", "-q"), "quiet", "Only warnings, errors and the final result.",
              _meta_setter(META_QUIET), is_flag=True),
    GlobalOpt(("--verbose", "-v"), "verbose", "Extra detail (tool calls, resolved paths).",
              _meta_setter(META_VERBOSE), is_flag=True),
)


def _make_global(opt: GlobalOpt, taken: set[str], root: bool) -> TyperOption | None:
    o = opt.make(taken, root=root)
    if o is None:
        return None
    if opt.name == "set":
        o.callback = _set_callback
    elif opt.name == "role_model":
        o.callback = _role_callback
    return o


def make_config_option(spec: FlagSpec, *, root: bool) -> TyperOption:
    decl = f"{spec.flag}/{spec.negative}" if spec.negative else spec.flag
    is_flag = spec.kind == "bool" and not spec.multiple
    default_txt = json.dumps(spec.default) if spec.default is not None else "null"
    return TyperOption(
        param_decls=[spec.param_name, decl],
        type=None if is_flag else _param_type(spec),
        is_flag=is_flag or None,
        multiple=spec.multiple,
        default=None,
        expose_value=False,
        callback=_config_callback,
        envvar=spec.envvar if root else None,
        hidden=True,
        help=f"{spec.help} [config {spec.dotted}; shipped {default_txt}]".strip(),
    )


# ── injection into the command tree ───────────────────────────────────────────────────────────
_INJECTED = "_vantage_flags_injected"


def _taken(cmd) -> set[str]:  # noqa: ANN001
    out: set[str] = set()
    for p in cmd.params:
        out.update(getattr(p, "opts", []) or [])
        out.update(getattr(p, "secondary_opts", []) or [])
    return out


def inject(cmd, *, root: bool = False) -> None:  # noqa: ANN001
    """Add the global options and every config flag to ``cmd`` (idempotent)."""
    if getattr(cmd, _INJECTED, False):
        return
    taken = _taken(cmd)
    added = []
    for opt in GLOBAL_OPTS:
        if opt.root_only and not root:
            continue
        o = _make_global(opt, taken, root)
        if o is not None:
            added.append(o)
            taken.update(o.opts)
            taken.update(o.secondary_opts)
    for spec in config_flag_specs():
        if spec.flag in taken:
            continue
        added.append(make_config_option(spec, root=root))
    cmd.params.extend(added)
    setattr(cmd, _INJECTED, True)


def _complete_hidden(cmd, ctx, incomplete: str) -> list:  # noqa: ANN001
    """Offer the hidden generated config flags when completing an option name."""
    if not incomplete.startswith("--"):
        return []
    out = []
    for p in cmd.params:
        if getattr(p, "hidden", False) and p.name and p.name.startswith("cfg__"):
            for o in (*p.opts, *p.secondary_opts):
                if o.startswith(incomplete):
                    out.append(CompletionItem(o, help=getattr(p, "help", None)))
    return out


class VantageCommand(TyperCommand):
    """Leaf command: completes the hidden config flags too."""

    def shell_complete(self, ctx, incomplete):  # noqa: ANN001
        return super().shell_complete(ctx, incomplete) + _complete_hidden(self, ctx, incomplete)


class VantageSubGroup(TyperGroup):
    """Nested group: injects the flags into each subcommand as it is resolved."""

    def get_command(self, ctx, cmd_name):  # noqa: ANN001
        cmd = super().get_command(ctx, cmd_name)
        if cmd is not None:
            inject(cmd)
        return cmd

    def shell_complete(self, ctx, incomplete):  # noqa: ANN001
        return super().shell_complete(ctx, incomplete) + _complete_hidden(self, ctx, incomplete)


def iter_commands(group, prefix: tuple[str, ...] = ()) -> Iterator[tuple[tuple[str, ...], Any]]:  # noqa: ANN001
    """Yield ``(path, command)`` for every command below ``group`` (flags injected)."""
    for name in sorted(getattr(group, "commands", {})):
        cmd = group.commands[name]
        inject(cmd)
        yield prefix + (name,), cmd
        if getattr(cmd, "commands", None):
            yield from iter_commands(cmd, prefix + (name,))
