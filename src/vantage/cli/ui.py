"""CLI presentation: one stderr console, the icon set, colour and verbosity.

Human output always goes to **stderr** so stdout stays clean for ``--json`` and for values meant
to be piped (``vantage runs path``, ``vantage config get``). The console is reconfigured once per
invocation from the effective ``ui`` config section (``--icons``, ``--ascii``, ``--no-color``,
``--theme``) plus ``--quiet`` / ``--verbose``. ``NO_COLOR`` is honoured whenever colour is
``auto``.
"""

from __future__ import annotations

import os
import sys
import unicodedata
from dataclasses import dataclass, field

from rich.console import Console
from rich.theme import Theme

from .icons import glyph

_THEMES = {
    "dark": {
        "accent": "bold cyan", "muted": "grey62", "ok": "green", "warn": "yellow",
        "fail": "red", "loud": "bold white on red", "title": "bold", "key": "cyan",
        "band.strong": "bold green", "band.adequate": "bold cyan", "band.thin": "bold yellow",
        "band.insufficient": "bold red",
    },
    "light": {
        "accent": "bold blue", "muted": "grey42", "ok": "dark_green", "warn": "dark_orange3",
        "fail": "red3", "loud": "bold white on red3", "title": "bold", "key": "blue",
        "band.strong": "bold dark_green", "band.adequate": "bold blue",
        "band.thin": "bold dark_orange3", "band.insufficient": "bold red3",
    },
}

#: Overall Confidence band -> theme style (blueprint: Strong ≥80 · Adequate 65–79 · Thin 50–64).
BAND_STYLE = {
    "Strong": "band.strong", "Adequate": "band.adequate", "Thin": "band.thin",
    "Insufficient": "band.insufficient",
}
RESULT_STYLE = {"PASS": "ok", "PASS WITH DISCLOSURES": "warn", "FAIL": "fail"}


@dataclass
class Ui:
    icons: str = "nerd"
    color: str = "auto"
    theme: str = "dark"
    animations: bool = True
    quiet: bool = False
    verbose: bool = False
    err: Console = field(default_factory=lambda: _console("auto", "dark"))

    def configure(self, *, icons: str | None = None, color: str | None = None,
                  theme: str | None = None, animations: bool | None = None,
                  quiet: bool | None = None, verbose: bool | None = None) -> Ui:
        if icons:
            self.icons = icons
        if color:
            self.color = color
        if theme:
            self.theme = theme
        if animations is not None:
            self.animations = animations
        if quiet is not None:
            self.quiet = quiet
        if verbose is not None:
            self.verbose = verbose
        self.err = _console(self.color, self.theme, ascii_only=self.icons == "ascii")
        return self

    def i(self, name: str) -> str:
        """Glyph for a semantic icon name in the active set."""
        return glyph(name, self.icons)

    # convenience printers -----------------------------------------------------------------
    def print(self, *a, **k) -> None:
        self.err.print(*a, **k)

    def info(self, msg: str) -> None:
        if not self.quiet:
            self.err.print(msg)

    def debug(self, msg: str) -> None:
        if self.verbose:
            self.err.print(f"[muted]{msg}[/]")

    def ok(self, msg: str) -> None:
        if not self.quiet:
            self.err.print(f"[ok]{self.i('ok')}[/] {msg}")

    def warn(self, msg: str) -> None:
        self.err.print(f"[warn]{self.i('warn')} {msg}[/]")

    def error(self, msg: str) -> None:
        self.err.print(f"[fail]{self.i('fail')} {msg}[/]")

    def status_cell(self, status: str) -> str:
        style = {"ok": "ok", "warn": "warn", "fail": "fail"}.get(status, "muted")
        return f"[{style}]{self.i(status if status in ('ok', 'warn', 'fail') else 'info')} {status}[/]"

    def band(self, band: str | None) -> str:
        if not band:
            return "[muted]—[/]"
        return f"[{BAND_STYLE.get(band, 'muted')}]{band}[/]"

    def result(self, result: str | None) -> str:
        if not result:
            return "[muted]—[/]"
        return f"[{RESULT_STYLE.get(result, 'muted')}]{result}[/]"


#: Punctuation the CLI prints that has a conventional 7-bit spelling.
_ASCII_MAP = str.maketrans({
    "·": ".", "•": "*", "—": "-", "–": "-", "…": "...", "→": "->", "←": "<-", "★": "*",
    "✓": "v", "✗": "x", "≥": ">=", "≤": "<=", "×": "x", "§": "S", "‘": "'", "’": "'",
    "“": '"', "”": '"', "±": "+/-",
})


class _AsciiStream:
    """A stderr wrapper that reports an ASCII encoding and writes only 7-bit text.

    Rich reads ``encoding`` to decide ``ascii_only``, which already swaps table borders, rules and
    spinners for ASCII ones; this covers the remaining text (separators, dashes, glyphs).
    """

    encoding = "ascii"

    def __init__(self, stream) -> None:
        self._stream = stream

    def write(self, text: str) -> int:
        text = unicodedata.normalize("NFKD", text.translate(_ASCII_MAP))
        out = text.encode("ascii", "ignore").decode("ascii")
        self._stream.write(out)
        return len(text)

    def flush(self) -> None:
        self._stream.flush()

    def isatty(self) -> bool:
        return self._stream.isatty()

    def fileno(self) -> int:
        return self._stream.fileno()


def _console(color: str, theme: str, ascii_only: bool = False) -> Console:
    kw: dict = {"stderr": True, "highlight": False, "soft_wrap": True, "theme": Theme(_THEMES.get(theme, _THEMES["dark"]))}
    if ascii_only:
        kw.pop("stderr")
        kw["file"] = _AsciiStream(sys.stderr)
    if color == "never" or (color == "auto" and os.environ.get("NO_COLOR")):
        kw["no_color"] = True
    elif color == "always":
        kw["force_terminal"] = True
    return Console(**kw)


#: The process-wide presenter. Commands call ``UI.configure(...)`` once config is resolved.
UI = Ui()
