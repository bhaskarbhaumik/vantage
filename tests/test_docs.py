"""Documentation stays true to the code.

* ``docs/reference/cli.md`` is exactly what ``scripts/generate-cli-reference.py`` renders.
* Relative links in the README and ``docs/`` resolve to files, and anchors to headings.
* Every ``vantage …`` command line shown in the docs names real commands and real options, and
  every ``vantage-tui`` flag shown is one the TUI accepts.
* The docs use the current names (no retired paths or identifiers).
"""

from __future__ import annotations

import importlib.util
import re
import shlex
from functools import cache
from pathlib import Path

import pytest
import typer

from vantage.cli import app
from vantage.cli import flags as F

REPO = Path(__file__).resolve().parents[1]
DOCS = REPO / "docs"


def _doc_files() -> list[Path]:
    files = [REPO / "README.md", REPO / "AGENTS.md", REPO / "harness" / "HARNESS_README.md"]
    files += sorted(p for p in DOCS.rglob("*.md") if "prompts" not in p.relative_to(DOCS).parts)
    return files


DOC_FILES = _doc_files()
# The generated reference is checked by the freshness test; its option tables are the code itself.
PROSE_FILES = [p for p in DOC_FILES if p != DOCS / "reference" / "cli.md"]


def _rel(p: Path) -> str:
    return str(p.relative_to(REPO))


# ── generated reference ───────────────────────────────────────────────────────────────────────
def _generator():
    path = REPO / "scripts" / "generate-cli-reference.py"
    spec = importlib.util.spec_from_file_location("generate_cli_reference", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_cli_reference_is_up_to_date():
    gen = _generator()
    current = (DOCS / "reference" / "cli.md").read_text()
    assert current == gen.render(), (
        "docs/reference/cli.md is stale: run `uv run python scripts/generate-cli-reference.py`")


def test_cli_reference_covers_every_command_and_config_flag():
    text = (DOCS / "reference" / "cli.md").read_text()
    root = typer.main.get_command(app)
    for path, _cmd in F.iter_commands(root):
        assert f"## vantage {' '.join(path)}\n" in text, path
    for spec in F.config_flag_specs():
        assert f"`{spec.flag}`" in text, spec.flag


# ── markdown parsing ──────────────────────────────────────────────────────────────────────────
_FENCE = re.compile(r"^(\s*)(`{3,}|~{3,})(.*)$")


def _split_fences(text: str) -> tuple[list[str], list[tuple[str, list[str]]]]:
    """Return (prose lines with fenced blocks blanked, [(info string, block lines)])."""
    prose: list[str] = []
    blocks: list[tuple[str, list[str]]] = []
    fence: str | None = None
    info = ""
    body: list[str] = []
    for line in text.splitlines():
        m = _FENCE.match(line)
        if fence is None and m:
            fence, info, body = m.group(2), m.group(3).strip(), []
            prose.append("")
        elif fence is not None and m and m.group(2).startswith(fence[0]) \
                and len(m.group(2)) >= len(fence) and not m.group(3).strip():
            blocks.append((info, body))
            fence = None
            prose.append("")
        elif fence is not None:
            body.append(line)
            prose.append("")
        else:
            prose.append(line)
    return prose, blocks


def _slug(heading: str) -> str:
    s = re.sub(r"<[^>]+>", "", heading)
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)
    s = s.replace("`", "").strip().lower()
    s = re.sub(r"[^\w\- ]", "", s)
    return s.replace(" ", "-")


@cache
def _anchors(path: Path) -> frozenset[str]:
    prose, _ = _split_fences(path.read_text())
    seen: dict[str, int] = {}
    out = set()
    for line in prose:
        m = re.match(r"^#{1,6}\s+(.*?)\s*#*\s*$", line)
        if not m:
            continue
        base = _slug(m.group(1))
        n = seen.get(base, 0)
        seen[base] = n + 1
        out.add(base if n == 0 else f"{base}-{n}")
    return frozenset(out)


_LINK = re.compile(r"!?\[(?:[^\]\[]|\[[^\]]*\])*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")


def _links(path: Path) -> list[str]:
    prose, _ = _split_fences(path.read_text())
    text = re.sub(r"`[^`\n]*`", "", "\n".join(prose))
    return _LINK.findall(text)


@pytest.mark.parametrize("doc", DOC_FILES, ids=_rel)
def test_relative_links_resolve(doc: Path):
    problems = []
    for target in _links(doc):
        if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I):  # http:, https:, mailto: …
            continue
        file_part, _, frag = target.partition("#")
        dest = (doc.parent / file_part).resolve() if file_part else doc
        if not dest.exists():
            problems.append(f"{target}: {dest} does not exist")
            continue
        if frag and dest.suffix == ".md" and frag not in _anchors(dest):
            problems.append(f"{target}: no heading '#{frag}' in {_rel(dest)}")
    assert not problems, "\n".join(problems)


# ── command lines shown in the docs ───────────────────────────────────────────────────────────
@cache
def _root():
    root = typer.main.get_command(app)
    for _path, _cmd in F.iter_commands(root):  # inject the global/config options everywhere
        pass
    return root


def _options(cmd) -> dict[str, bool]:
    """Option spelling -> whether it takes a value."""
    out: dict[str, bool] = {}
    for p in cmd.params:
        if getattr(p, "param_type_name", "") != "option":
            continue
        takes = not (getattr(p, "is_flag", False) or getattr(p, "count", False))
        for o in (*p.opts, *p.secondary_opts):
            out[o] = takes
    out["--help"] = False
    return out


def _is_placeholder(tok: str) -> bool:
    return tok.startswith(("<", "[", "$", "{")) or tok in ("…", "...") or "…" in tok


def _check_vantage_args(args: list[str]) -> list[str]:
    """Walk args through the command tree; return the problems found."""
    root = _root()
    cmd = root
    path: list[str] = []
    allowed = _options(root)
    i = 0
    while i < len(args):
        tok = args[i]
        if tok in ("--tui",):
            return []  # the rest belongs to the TUI
        if tok.startswith("-") and tok not in ("-", "--"):
            name = tok.split("=", 1)[0]
            if name not in allowed:
                return [f"unknown option {name} for `vantage {' '.join(path)}`"]
            if allowed[name] and "=" not in tok:
                i += 1  # skip its value
            i += 1
            continue
        commands = getattr(cmd, "commands", None)
        if commands:
            if tok in commands:
                cmd = commands[tok]
                path.append(tok)
                F.inject(cmd)
                allowed = {**_options(root), **_options(cmd)}
                if tok == "tui" and len(path) == 1:
                    return []
            elif _is_placeholder(tok):
                return []
            else:
                return [f"unknown command `vantage {' '.join([*path, tok])}`"]
        i += 1
    return []


@cache
def _tui_flags() -> frozenset[str]:
    src = (REPO / "tui" / "src" / "lib" / "args.ts").read_text()
    help_text = src[src.index("export const HELP_TEXT"):]
    return frozenset(re.findall(r"--[a-z][a-z-]*", help_text)) | {"-h", "-v"}


_PROGS = ("vantage", "vantage-engine", "vantage-tui")


def _invocation(segment: str) -> tuple[str, list[str]] | None:
    """``(program, args)`` when a shell segment runs vantage, vantage-engine or vantage-tui.

    Accepts leading ``VAR=value`` assignments and a ``uv run [--quiet] [--project DIR]`` prefix;
    anything else (``for p in vantage …``, ``docker build -t vantage``) is not an invocation.
    """
    try:
        tokens = shlex.split(segment)
    except ValueError:
        return None
    tokens = [t.rstrip(")") for t in tokens]
    while tokens and re.match(r"^[A-Z_][A-Z0-9_]*=", tokens[0]):
        tokens.pop(0)
    if tokens[:2] == ["uv", "run"]:
        tokens = tokens[2:]
        while tokens and tokens[0].startswith("--"):
            tokens = tokens[2:] if tokens[0] == "--project" else tokens[1:]
    if tokens and tokens[0] in _PROGS:
        return tokens[0], tokens[1:]
    return None


def _command_lines(path: Path) -> list[tuple[str, list[str]]]:
    """Shell-ish lines that invoke vantage / vantage-tui, from code blocks and inline code."""
    prose, blocks = _split_fences(path.read_text())
    lines: list[str] = []
    for info, body in blocks:
        if info and info.split()[0] not in ("bash", "sh", "shell", "zsh", "console", "text"):
            continue
        joined: list[str] = []
        buf = ""
        for raw in body:
            line = raw.rstrip()
            if line.endswith("\\"):
                buf += line[:-1] + " "
                continue
            joined.append(buf + line)
            buf = ""
        lines += joined
    for span in re.findall(r"`([^`\n]+)`", "\n".join(prose)):
        lines.append(span)
    out = []
    for line in lines:
        line = line.split(" #", 1)[0].strip()
        if line.startswith(("$ ", "> ")):
            line = line[2:]
        for seg in re.split(r"\s(?:\||&&|;)\s|\$\(|<\(|\|\s*$", line):
            found = _invocation(seg.strip())
            if found:
                out.append(found)
    return out


@pytest.mark.parametrize("doc", PROSE_FILES, ids=_rel)
def test_documented_commands_and_flags_exist(doc: Path):
    problems = []
    for prog, args in _command_lines(doc):
        line = " ".join([prog, *args])
        if prog == "vantage-tui":
            bad = [t.split("=", 1)[0] for t in args
                   if t.startswith("-") and t.split("=", 1)[0] not in _tui_flags()]
            problems += [f"{line!r}: vantage-tui has no {b}" for b in bad]
        else:
            problems += [f"{line!r}: {p}" for p in _check_vantage_args(args)]
    assert not problems, "\n".join(problems)


def test_command_checker_catches_mistakes():
    assert _check_vantage_args(["run", "--client", "X", "--tier", "EXECUTIVE"]) == []
    assert _check_vantage_args(["--set", "engine.tier=STANDARD", "config", "get", "engine.tier"]) == []
    assert _check_vantage_args(["export", "slug", "--export-helpers-charts", "plotly"]) == []
    assert _check_vantage_args(["runz", "list"])
    assert _check_vantage_args(["run", "--no-such-flag"])
    assert _check_vantage_args(["config", "frobnicate"])


# ── names ─────────────────────────────────────────────────────────────────────────────────────
_RETIRED = re.compile(
    r"\bAID\b|\baid[-_]|Account Intelligence Dossier|company-aid|\bTCS\b|Tata Consultancy"
    r"|scripts/vantage(?![-_\w])|\bcli/src\b|\bcli/dist\b|vantage-engine run|vantage-engine config"
)


@pytest.mark.parametrize("doc", DOC_FILES, ids=_rel)
def test_docs_use_current_names(doc: Path):
    hits = [f"{n}: {line.strip()}" for n, line in enumerate(doc.read_text().splitlines(), 1)
            if _RETIRED.search(line)]
    assert not hits, "\n".join(hits)
