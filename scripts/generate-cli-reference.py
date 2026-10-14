"""Generate docs/reference/cli.md from the live command tree.

    uv run python scripts/generate-cli-reference.py           # write the file
    uv run python scripts/generate-cli-reference.py --check   # exit 1 if it is out of date

The reference is built from two sources and nothing else, so it cannot drift from the code:

* the Click command tree behind ``vantage.cli.app`` (every command, argument and option, with
  the global options injected exactly as the CLI injects them), and
* the flag registry in ``vantage.cli.flags`` (one ``--section-key`` flag per config leaf, with
  its type, shipped default and environment variables), via ``vantage options``' own rows.

``tests/test_docs.py`` fails when the committed file differs from what this script renders.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import typer

from vantage import TAGLINE
from vantage.cli import app
from vantage.cli import flags as F
from vantage.cli.config_cmd import all_option_rows

REPO = Path(__file__).resolve().parents[1]
TARGET = REPO / "docs" / "reference" / "cli.md"
PROG = "vantage"


# ── formatting helpers ────────────────────────────────────────────────────────────────────────
def cell(text: Any) -> str:
    """One Markdown table cell: single line, pipes escaped."""
    s = "" if text is None else str(text)
    s = re.sub(r"\s+", " ", s).strip().replace("``", "`")
    # Outside code spans: keep <placeholders> and *globs* literal.
    parts = s.split("`")
    for i in range(0, len(parts), 2):
        parts[i] = parts[i].replace("<", "&lt;").replace(">", "&gt;").replace("*", "\\*")
    s = "`".join(parts)
    return s.replace("|", "\\|") or "—"


def code(text: str) -> str:
    return f"`{text}`" if text else ""


def anchor(title: str) -> str:
    """GitHub's heading slug: lowercase, drop punctuation except '-' and ' ', spaces -> '-'."""
    s = title.strip().lower()
    s = re.sub(r"[^\w\- ]", "", s)
    return s.replace(" ", "-")


def type_label(p: Any) -> str:
    t = p.type
    name = type(t).__name__
    if getattr(p, "is_flag", False):
        return "flag"
    if hasattr(t, "choices"):
        label = "`" + "\\|".join(str(c) for c in t.choices) + "`"
    elif name in ("IntRange", "FloatRange"):
        base = "int" if name == "IntRange" else "float"
        lo, hi = getattr(t, "min", None), getattr(t, "max", None)
        if lo is not None and hi is not None:
            label = f"{base} {lo}–{hi}"
        elif lo is not None:
            label = f"{base} ≥ {lo}"
        elif hi is not None:
            label = f"{base} ≤ {hi}"
        else:
            label = base
    elif "Path" in name:
        label = "path"
    else:
        label = {"IntParamType": "int", "FloatParamType": "float"}.get(name, "text")
    if getattr(p, "multiple", False):
        label += " (repeatable)"
    return label


def default_label(p: Any) -> str:
    if getattr(p, "required", False):
        return "required"
    d = p.default
    if getattr(p, "is_flag", False):
        if p.secondary_opts:
            if d is None:
                return "—"
            return code(p.opts[0] if d else p.secondary_opts[0])
        return "off" if not d else "on"
    if d is None or d == () or d == [] or d == "":
        return "—"
    return code(str(d))


def option_names(p: Any) -> str:
    longs = [o for o in p.opts if o.startswith("--")]
    shorts = [o for o in p.opts if not o.startswith("--")]
    names = longs + list(p.secondary_opts) + shorts
    return ", ".join(code(n) for n in names)


# ── command tree ──────────────────────────────────────────────────────────────────────────────
def root_group() -> Any:
    return typer.main.get_command(app)


def walk(group: Any, prefix: tuple[str, ...] = ()) -> list[tuple[tuple[str, ...], Any]]:
    """Commands in help order (registration order), depth first, with flags injected."""
    out = []
    for name, cmd in group.commands.items():
        F.inject(cmd)
        out.append((prefix + (name,), cmd))
        if getattr(cmd, "commands", None):
            out.extend(walk(cmd, prefix + (name,)))
    return out


def is_global(p: Any) -> bool:
    return (p.name or "").startswith("g__")


def is_config(p: Any) -> bool:
    return (p.name or "").startswith("cfg__")


def own_params(cmd: Any) -> list[Any]:
    return [p for p in cmd.params
            if not getattr(p, "hidden", False) and not is_global(p) and not is_config(p)]


def short_help(cmd: Any) -> str:
    text = cmd.short_help or (cmd.help or "").strip().split("\n\n")[0]
    return re.sub(r"\s+", " ", text).strip()


def full_help(cmd: Any) -> str:
    paras = [re.sub(r"\s+", " ", p).strip() for p in (cmd.help or "").strip().split("\n\n")]
    return "\n\n".join(p for p in paras if p)


def usage(path: tuple[str, ...], cmd: Any) -> str:
    parts = [PROG, *path, "[OPTIONS]"]
    for p in cmd.params:
        if getattr(p, "param_type_name", "") == "argument" or type(p).__name__.endswith("Argument"):
            name = p.name.upper()
            parts.append(name if p.required else f"[{name}]")
    if getattr(cmd, "commands", None):
        parts.append("COMMAND [ARGS]...")
    if (cmd.context_settings or {}).get("allow_extra_args"):
        parts.append("[ARGS]...")
    return " ".join(parts)


def lost_globals(cmd: Any) -> list[str]:
    """Global option spellings a command's own option took over (e.g. deploy -t = --target)."""
    present = set()
    for p in cmd.params:
        if is_global(p):
            present.update(p.opts)
    notes = []
    for opt in F.GLOBAL_OPTS:
        if not any(d in present for d in opt.decls):
            continue
        for d in opt.decls:
            if d not in present:
                owner = next((q for q in own_params(cmd) if d in q.opts), None)
                if owner is not None:
                    notes.append(f"`{d}` means `{owner.opts[0]}` on this command; spell the "
                                 f"global option `{opt.decls[0]}` in full.")
    return notes


def param_table(params: list[Any]) -> list[str]:
    args = [p for p in params if type(p).__name__.endswith("Argument")]
    opts = [p for p in params if p not in args]
    lines: list[str] = []
    if args:
        lines += ["**Arguments**", "", "| Argument | Type | Default | Description |",
                  "|---|---|---|---|"]
        for p in args:
            lines.append(f"| {code(p.name.upper())} | {type_label(p)} | {default_label(p)} | "
                         f"{cell(getattr(p, 'help', ''))} |")
        lines.append("")
    panels: dict[str | None, list[Any]] = {}
    for p in opts:
        panels.setdefault(getattr(p, "rich_help_panel", None), []).append(p)
    for panel, items in panels.items():
        lines += [f"**{panel or 'Options'}**", "", "| Option | Type | Default | Description |",
                  "|---|---|---|---|"]
        for p in items:
            lines.append(f"| {option_names(p)} | {type_label(p)} | {default_label(p)} | "
                         f"{cell(p.help)} |")
        lines.append("")
    return lines


# ── document ──────────────────────────────────────────────────────────────────────────────────
def render() -> str:
    root = root_group()
    commands = walk(root)
    rows = all_option_rows()
    global_rows = [r for r in rows if r["group"] == "global"]
    config_rows = [r for r in rows if r["group"] == "config"]

    out: list[str] = [
        "<!-- GENERATED by scripts/generate-cli-reference.py from the live command tree. -->",
        "<!-- Do not edit by hand: run `uv run python scripts/generate-cli-reference.py`. -->",
        "",
        "# CLI reference",
        "",
        f"`{PROG}` — Vantage, {TAGLINE}. `vantage-engine` is an alias of the same program.",
        "",
        "This page is generated from the code. For concepts (global vs command options, "
        "precedence, `--set`, JSON mode, exit codes) read the [CLI guide](../cli.md).",
        "",
        "- [Commands](#commands)",
        "- [Global options](#global-options)",
    ]
    for path, _ in commands:
        title = " ".join((PROG, *path))
        out.append(f"{'  ' * (len(path) - 1)}- [{title}](#{anchor(title)})")
    out += [
        "- [Config flags](#config-flags)",
        "",
        "## Commands",
        "",
        "| Command | Description |",
        "|---|---|",
    ]
    for path, cmd in commands:
        title = " ".join((PROG, *path))
        out.append(f"| [`{title}`](#{anchor(title)}) | {cell(short_help(cmd))} |")
    out += [
        "",
        "## Global options",
        "",
        "Accepted by `vantage` itself and by every command, before or after the command name "
        "(`vantage --tier STANDARD run …` equals `vantage run --tier STANDARD …`). `--tui` and "
        "`--version` are accepted on the root command only.",
        "",
        "| Option | Type | Sets | Env | Description |",
        "|---|---|---|---|---|",
    ]
    for r in global_rows:
        names = ", ".join(code(n.strip()) for n in r["flag"].split(","))
        out.append(f"| {names} | {cell(r['type'])} | {code(r['key'] or '') or '—'} | "
                   f"{', '.join(code(e) for e in r['env']) or '—'} | {cell(r['description'])} |")
    out.append("| `--version` | flag | — | — | Print the version and exit (root only). |")
    out.append("")

    for path, cmd in commands:
        title = " ".join((PROG, *path))
        out += [f"## {title}", ""]
        text = full_help(cmd)
        if text:
            out += [text, ""]
        out += ["```text", usage(path, cmd), "```", ""]
        if getattr(cmd, "commands", None):
            out += ["| Subcommand | Description |", "|---|---|"]
            for name, sub in cmd.commands.items():
                sub_title = f"{title} {name}"
                out.append(f"| [`{name}`](#{anchor(sub_title)}) | {cell(short_help(sub))} |")
            out.append("")
        out += param_table(own_params(cmd))
        for note in lost_globals(cmd):
            out += [f"> {note}", ""]
        if not getattr(cmd, "commands", None):
            out += ["Also accepts the [global options](#global-options) and every "
                    "[config flag](#config-flags).", ""]

    out += [
        "## Config flags",
        "",
        "Every leaf of the configuration model is also a flag, accepted by every command, and "
        "hidden from `--help` to keep it readable (`vantage options` lists them; shell completion "
        "offers them). Booleans come as `--x/--no-x` pairs, list options are repeatable, and the "
        "literal value `null` clears an optional value. On the root command each flag also reads "
        "the first environment variable listed (lower precedence than the flag). "
        "`role_model_map` has its own `--role-model agent=tier`; `--set dotted.key=value` reaches "
        "any key, including ones without a flag.",
        "",
        "| Flag | Key | Type | Shipped default | Env | Description |",
        "|---|---|---|---|---|---|",
    ]
    for r in config_rows:
        flag = code(r["flag"]) + (f" / {code(r['negative'])}" if r.get("negative") else "")
        env = ", ".join(code(e) for e in dict.fromkeys(r["env"])) or "—"
        default = code(json.dumps(r["default"])).replace("|", "\\|")
        out.append(f"| {flag} | {code(r['key'])} | {cell(r['type'])} | {default} | {env} | "
                   f"{cell(r['description'])} |")
    out.append("")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="exit 1 if the file is out of date")
    ap.add_argument("--out", type=Path, default=TARGET, help="output file")
    args = ap.parse_args(argv)
    text = render()
    if args.check:
        current = args.out.read_text() if args.out.exists() else ""
        if current != text:
            print(f"{args.out} is out of date; run scripts/generate-cli-reference.py",
                  file=sys.stderr)
            return 1
        print(f"{args.out} is up to date")
        return 0
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text)
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
