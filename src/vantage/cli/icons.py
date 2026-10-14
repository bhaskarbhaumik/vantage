"""The one icon table for the CLI.

Every glyph the CLI prints is looked up here by a semantic name, in one of three sets:

* ``nerd``    — Nerd Font glyphs (Font Awesome range, present in every patched Nerd Font). Default.
* ``unicode`` — plain Unicode symbols that render in any modern terminal font.
* ``ascii``   — 7-bit only, for CI logs, serial consoles and screen readers.

The TUI keeps its own table with the same semantic names so the two surfaces look alike.
"""

from __future__ import annotations

from typing import Literal

IconSet = Literal["nerd", "unicode", "ascii"]
ICON_SETS: tuple[IconSet, ...] = ("nerd", "unicode", "ascii")

#: semantic name -> (nerd, unicode, ascii)
ICONS: dict[str, tuple[str, str, str]] = {
    "ok": ("\uf00c", "✓", "+"),
    "fail": ("\uf00d", "✗", "x"),
    "warn": ("\uf071", "▲", "!"),
    "info": ("\uf05a", "•", "i"),
    "skip": ("\uf05e", "∅", "-"),
    "run": ("\uf04b", "▶", ">"),
    "stage": ("\uf0da", "▸", ">"),
    "agent": ("\uf007", "◦", "-"),
    "tool": ("\uf0ad", "→", "->"),
    "done": ("\uf11e", "●", "*"),
    "error": ("\uf057", "✗", "x"),
    "dossier": ("\uf02d", "§", "#"),
    "folder": ("\uf07b", "▣", "/"),
    "file": ("\uf15c", "▢", "-"),
    "export": ("\uf045", "⇪", "^"),
    "backend": ("\uf1b2", "◆", "*"),
    "config": ("\uf013", "≡", "="),
    "auth": ("\uf132", "◈", "@"),
    "key": ("\uf084", "◇", "k"),
    "lock": ("\uf023", "◇", "L"),
    "cloud": ("\uf0c2", "◌", "c"),
    "chart": ("\uf080", "▤", "#"),
    "search": ("\uf002", "⌕", "?"),
    "trash": ("\uf1f8", "⌫", "x"),
    "clock": ("\uf017", "◷", "t"),
    "arrow": ("\uf061", "→", "->"),
    "bullet": ("\uf111", "•", "*"),
    "star": ("\uf005", "★", "*"),
    "terminal": ("\uf120", "❯", ">"),
    "doctor": ("\uf0f1", "✚", "+"),
    "shield": ("\uf132", "◈", "#"),
    "server": ("\uf233", "▦", "#"),
    "python": ("\ue73c", "λ", "py"),
    "node": ("\ue718", "⬢", "js"),
    "question": ("\uf128", "?", "?"),
    "stop": ("\uf05e", "‼", "!!"),
}

#: doctor/runs status -> semantic icon
STATUS_ICON = {"ok": "ok", "warn": "warn", "fail": "fail", "info": "info", "skip": "skip"}


def glyph(name: str, icon_set: str = "nerd") -> str:
    """Return the glyph for ``name`` in ``icon_set`` (unknown names render as the bullet)."""
    row = ICONS.get(name) or ICONS["bullet"]
    try:
        idx = ICON_SETS.index(icon_set)  # type: ignore[arg-type]
    except ValueError:
        idx = 0
    return row[idx]
