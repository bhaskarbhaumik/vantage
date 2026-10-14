"""Dossier Markdown → :class:`Dossier` (structure only).

Hand-rolled rather than markdown-it-based because the dossier is a *known* dialect, and what
matters is recovering its structure (numbered sections, registers, claim references) rather than
rendering arbitrary CommonMark. It tolerates the variance seen across real runs:

* section numbers written as ``## 1.``, ``## §10`` or ``## 21.11`` in the same corpus
* subsections emitted one heading level too high (``## 21.1`` under ``## 21.``)
* front matter as loose ``**Key:** value`` lines, with several keys on one line
* fenced visual blocks with hyphenated info strings (```` ```chart-data ````)

Visual blocks and the title-block metadata are lifted by :mod:`vantage.export.dossier`.
"""

from __future__ import annotations

import re
from pathlib import Path

from .models import (
    Callout,
    Code,
    Dossier,
    ListBlock,
    ListItem,
    Paragraph,
    Rule,
    Section,
    Table,
)

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
# GFM needs only one hyphen per cell, so `|:-:|` and `|-|` are valid separators.
TABLE_SEP_RE = re.compile(r"^\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)*\|?\s*$")
BULLET_RE = re.compile(r"^(\s*)[-*+]\s+(.*)$")
ORDERED_RE = re.compile(r"^(\s*)(\d+)[.)]\s+(.*)$")
RULE_RE = re.compile(r"^\s*(-{3,}|\*{3,}|_{3,})\s*$")
# CommonMark allows any run of non-backtick characters as the info string, and the dossier uses
# hyphenated ones (```chart-data, ```figure-spec). Matching only `\w*` left those opening fences
# unrecognised while their closing ``` still toggled the tracker — silently swallowing every
# heading until the next fence.
FENCE_RE = re.compile(r"^\s{0,3}(?:`{3,}|~{3,})\s*(?P<info>[^`]*)$")

# "1.", "§10", "10", "21.11", "A.1"
NUMBER_RE = re.compile(
    r"^(?:(?P<appendix>Appendix\s+(?P<aletter>[A-Z]))|§\s*(?P<sect>[\d.]+)"
    r"|(?P<plain>\d+(?:\.\d+)*)\.?|(?P<sub>[A-Z]\.\d+))"
    r"\s*(?:[—–\-:.]\s*)?(?P<rest>.*)$"
)

FRONT_MATTER_RE = re.compile(r"\*\*(?P<key>[^*:]+):\*\*\s*(?P<val>.*?)(?=\s*\*\*[^*:]+:\*\*|$)")

# Claim / source / opportunity / risk / gap / action / person identifiers used throughout.
CLAIM_REF_RE = re.compile(r"\b([COPRAGKUXSQTF]-[\d.]+(?:-\d+)?[a-z]?)\b")


def _split_heading(text: str) -> tuple[str, str, str]:
    """``"§10 Risk, Regulatory & ESG"`` → ``("10", "§10", "Risk, Regulatory & ESG")``."""
    match = NUMBER_RE.match(text)
    if not match:
        return "", "", text
    rest = match.group("rest") or ""
    if match.group("appendix"):
        return match.group("aletter"), match.group("appendix"), rest
    if match.group("sect"):
        return match.group("sect").rstrip("."), f"§{match.group('sect')}", rest
    if match.group("sub"):
        return match.group("sub"), match.group("sub"), rest
    plain = match.group("plain")
    # Bare years or figures are not section numbers; require the heading to continue.
    if plain and rest:
        return plain, plain, rest
    return "", "", text


def _tone(text: str) -> str:
    lowered = text.lower()
    head = lowered[:200]
    if "must not be presented to the client" in lowered or "decision aids" in lowered:
        return "disclaimer"
    if text.lstrip().startswith("**Verdict") or "verdict" in lowered[:40]:
        return "verdict"
    if any(w in head for w in ("read before", "read this", "erratum", "withdrawn", "suppressed",
                               "warning", "do not", "caution")):
        return "warning"
    return "note"


def _split_row(line: str) -> list[str]:
    stripped = line.strip().removeprefix("|")
    if stripped.endswith("|") and not stripped.endswith("\\|"):
        stripped = stripped[:-1]
    cells = re.split(r"(?<!\\)\|", stripped)
    return [c.strip().replace("\\|", "|") for c in cells]


def _aligns(sep_line: str) -> list[str]:
    out = []
    for cell in _split_row(sep_line):
        left, right = cell.startswith(":"), cell.endswith(":")
        out.append("center" if left and right else "right" if right else "left")
    return out


class _BlockParser:
    """Consumes the lines belonging to one section into typed blocks."""

    def __init__(self, lines: list[str]) -> None:
        self.lines = lines
        self.i = 0
        self.blocks: list = []

    def parse(self) -> list:
        while self.i < len(self.lines):
            line = self.lines[self.i]
            if not line.strip():
                self.i += 1
            elif RULE_RE.match(line):
                self.blocks.append(Rule())
                self.i += 1
            elif FENCE_RE.match(line):
                self._code()
            elif line.lstrip().startswith(">"):
                self._callout()
            elif self._looks_like_table():
                self._table()
            elif BULLET_RE.match(line) or ORDERED_RE.match(line):
                self._list()
            else:
                self._paragraph()
        return self.blocks

    def _code(self) -> None:
        match = FENCE_RE.match(self.lines[self.i])
        lang = (match.group("info") or "").strip() or None if match else None
        self.i += 1
        body: list[str] = []
        while self.i < len(self.lines) and not FENCE_RE.match(self.lines[self.i]):
            body.append(self.lines[self.i])
            self.i += 1
        self.i += 1  # closing fence
        self.blocks.append(Code(text="\n".join(body), lang=lang))

    def _callout(self) -> None:
        body: list[str] = []
        while self.i < len(self.lines) and self.lines[self.i].lstrip().startswith(">"):
            body.append(re.sub(r"^\s*>\s?", "", self.lines[self.i]))
            self.i += 1
        text = _join_wrapped(body)
        # A heading inside a blockquote ("> ### Verification result") reads as the callout label.
        text = re.sub(r"^#{1,6}\s+", "", text)
        self.blocks.append(Callout(text=text, tone=_tone(text)))

    def _looks_like_table(self) -> bool:
        line = self.lines[self.i]
        if not line.lstrip().startswith("|"):
            return False
        nxt = self.lines[self.i + 1] if self.i + 1 < len(self.lines) else ""
        return bool(TABLE_SEP_RE.match(nxt))

    def _table(self) -> None:
        header = _split_row(self.lines[self.i])
        aligns = _aligns(self.lines[self.i + 1])
        self.i += 2
        rows: list[list[str]] = []
        while self.i < len(self.lines) and self.lines[self.i].lstrip().startswith("|"):
            cells = _split_row(self.lines[self.i])
            # Pad or trim ragged rows so downstream renderers can assume a grid.
            cells = (cells + [""] * len(header))[: len(header)]
            rows.append(cells)
            self.i += 1
        aligns = (aligns + ["left"] * len(header))[: len(header)]
        self.blocks.append(Table(header=header, rows=rows, aligns=aligns))

    def _list(self) -> None:
        items: list[ListItem] = []
        ordered = bool(ORDERED_RE.match(self.lines[self.i]))
        indents: list[int] = []      # open nesting levels, by indent width (2- or 4-space lists)
        while self.i < len(self.lines):
            line = self.lines[self.i]
            match = ORDERED_RE.match(line) or BULLET_RE.match(line)
            if not match:
                # A wrapped continuation line belongs to the previous item.
                if (items and line.strip() and line.startswith((" ", "\t"))
                        and not self._looks_like_table()):
                    items[-1].text += " " + line.strip()
                    self.i += 1
                    continue
                break
            indent = len(match.group(1).expandtabs(4))
            text = match.group(3) if match.re is ORDERED_RE else match.group(2)
            while indents and indents[-1] > indent:
                indents.pop()
            if not indents or indents[-1] < indent:
                indents.append(indent)
            items.append(ListItem(text=text.strip(), level=min(len(indents) - 1, 3)))
            self.i += 1
        self.blocks.append(ListBlock(ordered=ordered, items=items))

    def _paragraph(self) -> None:
        body: list[str] = []
        while self.i < len(self.lines):
            line = self.lines[self.i]
            if (
                not line.strip()
                or RULE_RE.match(line)
                or line.lstrip().startswith(">")
                or FENCE_RE.match(line)
                or BULLET_RE.match(line)
                or ORDERED_RE.match(line)
                or self._looks_like_table()
            ):
                break
            body.append(line)
            self.i += 1
        text = _join_wrapped(body)
        if text:
            self.blocks.append(Paragraph(text=text))


def _join_wrapped(lines: list[str]) -> str:
    """Re-flow hard-wrapped Markdown: a blank line is the only real paragraph break."""
    out: list[str] = []
    buf: list[str] = []
    for line in lines:
        if line.strip():
            buf.append(line.strip())
        elif buf:
            out.append(" ".join(buf))
            buf = []
    if buf:
        out.append(" ".join(buf))
    return "\n\n".join(out).strip()


def parse_front_matter(lines: list[str]) -> dict[str, str]:
    """``**Version:** 3.0.0 · **Output tier:** FULL_ANNEX`` → two entries."""
    found: dict[str, str] = {}
    for line in lines:
        if "**" not in line or line.lstrip().startswith(">"):
            continue
        for match in FRONT_MATTER_RE.finditer(line):
            key = match.group("key").strip()
            value = match.group("val").strip().rstrip("·").strip()
            if key and value:
                found.setdefault(key, value)
    return found


def parse_markdown(raw: str, source_path: str = "") -> Dossier:
    """Parse dossier Markdown text into the structural IR."""
    lines = raw.split("\n")

    # ── title + front matter: everything before the first H2 ────────────────
    title = ""
    first_h2 = len(lines)
    in_fence = False
    for idx, line in enumerate(lines):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = HEADING_RE.match(line)
        if match and len(match.group(1)) == 1 and not title:
            title = match.group(2).strip()
        if match and len(match.group(1)) == 2:
            first_h2 = idx
            break

    preamble_lines = lines[:first_h2]
    front_matter = parse_front_matter(preamble_lines)
    preamble_blocks = _BlockParser(
        [ln for ln in preamble_lines if not HEADING_RE.match(ln)]).parse()
    banners = [b for b in preamble_blocks if isinstance(b, Callout)]
    preamble = [b for b in preamble_blocks if isinstance(b, Paragraph)
                and not FRONT_MATTER_RE.match(b.text)]

    # ── sections ─────────────────────────────────────────────────────────────
    # Collect headings first, then slice the body between them. Fences are tracked so a `#`
    # inside a code block never registers as a heading.
    heads: list[tuple[int, int, str]] = []   # (line_no, level, text)
    in_fence = False
    for idx, line in enumerate(lines):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = HEADING_RE.match(line)
        if match and len(match.group(1)) >= 2:
            heads.append((idx, len(match.group(1)), match.group(2).strip()))

    flat: list[Section] = []
    for pos, (line_no, level, text) in enumerate(heads):
        end = heads[pos + 1][0] if pos + 1 < len(heads) else len(lines)
        section_id, number, clean_title = _split_heading(text)
        if not section_id:
            slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
            section_id = "toc" if "table of contents" in text.lower() else slug[:40] or f"h{pos}"
        flat.append(
            Section(
                id=section_id,
                number=number,
                title=clean_title or text,
                heading=text,
                level=level,
                blocks=_BlockParser(lines[line_no + 1 : end]).parse(),
            )
        )

    return Dossier(
        title=title or Path(source_path).stem,
        client=client_from_title(title) if title else Path(source_path).stem,
        source_path=source_path,
        front_matter=front_matter,
        banners=banners,
        preamble=preamble,
        sections=_nest(flat),
    )


def parse_dossier(path: str | Path) -> Dossier:
    """Parse a ``<slug>-vantage.md`` file into the structural IR."""
    path = Path(path).expanduser()
    return parse_markdown(path.read_text(encoding="utf8"), str(path))


def _nest(flat: list[Section]) -> list[Section]:
    """Turn the flat heading list into a tree using heading level.

    A same-level heading whose id extends the previous section's id (``## 21.1`` after
    ``## 21.``) is adopted as a child instead of a sibling.
    """
    roots: list[Section] = []
    stack: list[Section] = []

    for section in flat:
        while stack and stack[-1].level >= section.level:
            top = stack[-1]
            if (top.level == section.level and section.id and top.id
                    and section.id.startswith(f"{top.id}.")):
                break
            stack.pop()
        if stack:
            stack[-1].children.append(section)
        else:
            roots.append(section)
        stack.append(section)
    return roots


def client_from_title(title: str) -> str:
    """``"Vantage — Northwind Ceramics plc"`` → ``"Northwind Ceramics plc"``."""
    for dash in ("—", "–", " - ", ": "):
        if dash in title:
            return title.split(dash, 1)[1].strip()
    return title.strip()


def claim_refs(text: str) -> list[str]:
    """Every claim/source/opportunity identifier cited in a fragment, in order."""
    return list(dict.fromkeys(CLAIM_REF_RE.findall(text or "")))
