"""Inline Markdown → styled runs.

The dossier leans on inline emphasis: **bold** for the load-bearing claim, `code` for claim and
source identifiers and for markers such as ``[INTERNAL REQUIRED]``, *italic* for asides. Dropping
that formatting would flatten the document's signalling system, so every renderer converts
through here — one tokenizer, three consumers (docx runs, pptx runs, HTML spans).
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass

# Ordered: the first pattern to match at a position wins. Code is checked before emphasis so
# `**not bold**` inside backticks survives intact.
TOKEN_RE = re.compile(
    r"(?P<code>`[^`]+`)"
    r"|(?P<bolditalic>\*\*\*[^*]+\*\*\*)"
    r"|(?P<bold>\*\*(?:[^*]|\*(?!\*))+\*\*)"
    r"|(?P<italic>(?<![*\w])\*(?!\s)[^*]+(?<!\s)\*(?!\*))"
    r"|(?P<link>\[[^\]]+\]\([^)]+\))"
    r"|(?P<strike>~~[^~]+~~)"
)

LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

#: Integrity markers that carry meaning and must survive every trim, policy and layout.
MARKER_RE = re.compile(
    r"\[(?:DATA GAP|DATA UNAVAILABLE|ESTIMATED?|INFERRED|SNIPPET-ONLY|STALE[^\]]*"
    r"|INTERNAL(?: REQUIRED)?(?:[:\s][^\]]*)?)\]"
    r"|\bNOT ASSESSED\b|\bSUPPRESSED\b|\bNOT RELIABLY ASSESSABLE\b"
)


@dataclass
class Run:
    text: str
    bold: bool = False
    italic: bool = False
    code: bool = False
    strike: bool = False
    href: str | None = None


def parse_runs(text: str) -> list[Run]:
    """Split a fragment of inline Markdown into styled runs."""
    runs: list[Run] = []
    pos = 0

    for match in TOKEN_RE.finditer(text):
        if match.start() > pos:
            runs.append(Run(text[pos : match.start()]))

        kind = match.lastgroup
        raw = match.group()

        if kind == "code":
            runs.append(Run(raw[1:-1], code=True))
        elif kind == "bolditalic":
            runs.append(Run(raw[3:-3], bold=True, italic=True))
        elif kind == "bold":
            for inner in parse_runs(raw[2:-2]):
                inner.bold = True
                runs.append(inner)
        elif kind == "italic":
            for inner in parse_runs(raw[1:-1]):
                inner.italic = True
                runs.append(inner)
        elif kind == "strike":
            runs.append(Run(raw[2:-2], strike=True))
        elif kind == "link":
            m = LINK_RE.match(raw)
            label, href = (m.groups() if m else (raw, ""))
            for inner in parse_runs(label):
                inner.href = href
                runs.append(inner)

        pos = match.end()

    if pos < len(text):
        runs.append(Run(text[pos:]))

    return [r for r in runs if r.text]


def plain(text: str) -> str:
    """Strip inline markup — for slide titles, alt text, TOC entries, metadata."""
    return "".join(run.text for run in parse_runs(text or ""))


def to_html(text: str) -> str:
    """Render inline Markdown as safe HTML.

    Links are never emitted as ``href``: the export is a self-contained, offline file and must
    not reach the network when opened. The target is kept visible as text instead, so the
    provenance a link carried is not lost.
    """
    out: list[str] = []
    for run in parse_runs(text or ""):
        body = html.escape(run.text)
        if run.code:
            klass = ' class="marker"' if MARKER_RE.search(run.text) else ""
            out.append(f"<code{klass}>{body}</code>")
            continue
        if run.bold:
            body = f"<strong>{body}</strong>"
        if run.italic:
            body = f"<em>{body}</em>"
        if run.strike:
            body = f"<s>{body}</s>"
        if run.href:
            target = html.escape(run.href, quote=True)
            if run.href.startswith("#"):
                body = f'<a href="{target}">{body}</a>'
            elif run.href != run.text:
                body = f'{body} <span class="link-target">({target})</span>'
        out.append(body)
    return "".join(out)


def markers(text: str) -> list[str]:
    """Every integrity marker in a fragment, in order, de-duplicated."""
    return list(dict.fromkeys(m.group(0) for m in MARKER_RE.finditer(plain(text or ""))))


def truncate(text: str, limit: int, ellipsis: str = "…") -> str:
    """Trim to ``limit`` characters on a word boundary, markup-aware.

    Used where a layout has a hard ceiling (a slide bullet, a table cell). The caller is trimming
    *display*, never the dossier — and an integrity marker the cut would remove (``[DATA GAP]``,
    ``[ESTIMATE]``, ``[INTERNAL REQUIRED]``, ``SUPPRESSED``…) is re-appended, because a claim
    shown without its caveat reads stronger than its evidence supports.
    """
    flat = plain(text)
    if len(flat) <= limit:
        return text
    cut = flat[: max(1, limit - len(ellipsis))]
    if " " in cut[limit // 2 :]:
        cut = cut.rsplit(" ", 1)[0]
    out = cut.rstrip(" ,;:—–-") + ellipsis
    lost = [m for m in markers(flat) if m not in out]
    if lost:
        out += " " + " ".join(lost)
    return out
