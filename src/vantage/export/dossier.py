"""The v3 dossier adapter: visual blocks, title-block metadata, and integrity policies.

The v3.0.0 dossier is numbered §0–§21 and carries its visuals inline as fenced JSON blocks::

    ```chart-data     {"schema": "vantage-chart/v1",  "id": "C-6.2.1", "x": [...], "series": [...]}
    ```figure-spec    {"schema": "vantage-figure/v1", "id": "F-4.4", "nodes": [...], "edges": [...]}

This module turns those into renderable :class:`ChartBlock`/:class:`FigureBlock` objects in place,
reads the title block (as-of date, tier, Overall Confidence / EQI, verification result), and
applies the citation and cross-reference policies an export may ask for.

Nothing here invents content. A block that fails to parse is left in place as a visible code
block rather than dropped — a reader must never be shown a document that quietly lost a figure.
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any

from .models import (
    Callout,
    ChartBlock,
    ChartSpec,
    Code,
    Dossier,
    FigureBlock,
    FigureSpec,
    ListBlock,
    Paragraph,
    Section,
    Table,
)
from .parse import parse_dossier
from .richtext import plain

# ── v3 structure ─────────────────────────────────────────────────────────────

#: §3–§17 are the organization-neutral body; §18–§20 the pursuit sections.
BODY = [str(n) for n in range(3, 21)]
#: §0 run contract, §1 executive summary (written last, placed first), §2 methodology.
FRONT = ["0", "1", "2"]
APPENDIX = "21"

SECTION_TAKEAWAY = {
    "0": "What was asked, which entity it resolved to, and what the run could and could not reach",
    "1": "The verdict, the evidence behind it, and what to do next",
    "2": "How the research was done, and how far its evidence can be pushed",
    "3": "Who the company is, and which legal entity each fact attaches to",
    "4": "The market it sits in, and the rules that bind it",
    "5": "How it makes money",
    "6": "Whether it can fund a transformation, and under what pressure",
    "7": "How the work gets done, and where it hurts",
    "8": "What it actually runs, and how mature that estate is",
    "9": "What it has said it will do — and what it has delivered",
    "10": "Who decides, on what authority, and what constrains delivery",
    "11": "How it compares to the peers it is measured against",
    "12": "Who it sells to, and what they think",
    "13": "What is happening right now, and what it implies",
    "14": "What could go wrong, for them and for a delivery partner",
    "15": "How ready it is for AI, and where the use cases are",
    "16": "Who is already inside the account",
    "17": "Its licence to operate, and its responsible-AI posture",
    "18": "Where the opportunity is, and what it is worth",
    "19": "How to position, and how to engage",
    "20": "What to do next, owned and dated",
    "21": "The registers behind every claim: sources, scoring, verification and gaps",
}

#: A semantic icon per section (get-icon queries, lucide family first).
SECTION_ICON = {
    "0": "file-check", "1": "file-text", "2": "microscope", "3": "building-2", "4": "globe",
    "5": "coins", "6": "chart-line", "7": "factory", "8": "cpu", "9": "target", "10": "users",
    "11": "swords", "12": "handshake", "13": "radar", "14": "shield-alert",
    "15": "brain-circuit", "16": "network", "17": "leaf", "18": "lightbulb", "19": "compass",
    "20": "list-checks", "21": "book-open",
}

#: Vertical-module codes the run contract uses, in words a stock-image search understands.
VERTICAL_WORDS = {
    "V-ENR": "energy and natural resources", "V-MFG": "manufacturing and industrial operations",
    "V-FS": "financial services", "V-BFS": "banking and financial services",
    "V-INS": "insurance", "V-CM": "capital markets", "V-HLS": "healthcare and life sciences",
    "V-LS": "life sciences laboratory", "V-HC": "healthcare", "V-RCG": "retail and consumer goods",
    "V-RTL": "retail stores", "V-CPG": "consumer goods", "V-TEL": "telecommunications network",
    "V-MED": "media and entertainment", "V-TTH": "travel transportation and hospitality",
    "V-PUB": "public sector government", "V-UTL": "utilities power grid",
    "V-HT": "high technology", "V-AUTO": "automotive", "V-AERO": "aerospace",
    "V-EDU": "education", "V-PRO": "professional services", "V-LOG": "logistics",
}


def is_v3(dossier: Dossier) -> bool:
    """True when the dossier carries the v3 section structure."""
    version = (dossier.version or dossier.front_matter.get("Version") or "").strip()
    if version.startswith("3."):
        return True
    ids = {s.id for s in dossier.sections}
    return APPENDIX in ids and {"18", "19", "20"} <= ids


# ── visual blocks ────────────────────────────────────────────────────────────

CHART_LANGS = {"chart-data", "chart"}
FIGURE_LANGS = {"figure-spec", "figure"}
#: Any ``<namespace>-chart/vN`` / ``<namespace>-figure/vN`` id; the fence decides the kind.
SCHEMA_RE = re.compile(r"^[a-z][a-z0-9-]*-(?P<kind>chart|figure)/v(?P<ver>\d+)$")
CHART_SCHEMA = "vantage-chart/v1"
FIGURE_SCHEMA = "vantage-figure/v1"

_FORM_MAP = {
    "bar": "bar", "column": "bar", "grouped-bar": "grouped-bar", "clustered-bar": "grouped-bar",
    "stacked-bar": "stacked-bar", "stacked": "stacked-bar", "hbar": "hbar",
    "horizontal-bar": "hbar", "bar-horizontal": "hbar", "line": "line", "area": "line",
    "scatter": "scatter", "bubble": "scatter", "donut": "donut", "pie": "donut",
    "radar": "hbar", "waterfall": "waterfall", "bar+line": "combo", "combo": "combo",
}


def _num(value: Any) -> float | None:
    """A chart value as a float, or ``None`` for "not available" (never zero)."""
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return None if math.isnan(float(value)) else float(value)
    text = str(value).strip().replace(",", "").replace("−", "-")
    try:
        return float(text)
    except ValueError:
        return None


def chart_from_spec(data: dict) -> ChartSpec | None:
    """A ``chart-data`` object → :class:`ChartSpec`. ``None`` when there is nothing to draw."""
    nested = data.get("data") if isinstance(data.get("data"), dict) else {}
    categories = [str(x) for x in (data.get("x") or nested.get("categories")
                                   or nested.get("x") or [])]
    raw_series = data.get("series") or nested.get("series") or []
    if not categories or not isinstance(raw_series, list) or not raw_series:
        return None

    declared = str(data.get("type") or "bar").lower().strip()
    kinds = [str(s.get("type") or "").lower() for s in raw_series if isinstance(s, dict)]
    if "+" in declared or {"bar", "line"} <= {k for k in kinds if k}:
        form = "combo"
    else:
        form = _FORM_MAP.get(declared, "bar")

    series = []
    for index, s in enumerate(raw_series):
        if not isinstance(s, dict):
            continue
        values = [_num(v) for v in (s.get("values") or [])]
        kind = str(s.get("type") or "").lower()
        series.append({
            "name": str(s.get("name") or f"Series {index + 1}"),
            "values": values,
            "kind": "line" if kind == "line" or (form == "line" and not kind) else "bar",
        })
    if not series or not any(v is not None for s in series for v in s["values"]):
        return None

    secondary = None
    if form == "combo":
        line_names = [s["name"] for s in series if s["kind"] == "line"]
        secondary = line_names[0] if line_names else None

    note_bits = []
    if data.get("note"):
        note_bits.append(str(data["note"]))
    if data.get("as_of"):
        note_bits.append(f"as of {data['as_of']}")
    if data.get("confidence"):
        note_bits.append(f"confidence {data['confidence']}")
    if data.get("sources"):
        note_bits.append("sources " + ", ".join(str(x) for x in data["sources"][:8]))
    if any(v is None for s in series for v in s["values"]) or any(
            len(s["values"]) < len(categories) for s in series):
        note_bits.append("missing values are shown as gaps, not zero")
    if declared == "radar":
        note_bits.append("dimension scores drawn as bars")

    return ChartSpec(
        form=form,
        title=str(data.get("title") or data.get("id") or "Chart"),
        categories=categories,
        series=series,
        unit=(str(data["unit"]) if data.get("unit") else None),
        secondary_unit=secondary,
        note="; ".join(note_bits) or None,
        id=str(data.get("id") or "") or None,
    )


def figure_from_spec(data: dict) -> FigureSpec | None:
    nested = data.get("data") if isinstance(data.get("data"), dict) else {}
    nodes = data.get("nodes") or nested.get("nodes") or []
    edges = data.get("edges") or nested.get("edges") or []
    items = data.get("items") or nested.get("items") or []
    nodes = [n for n in nodes if isinstance(n, dict) and (n.get("id") or n.get("label"))]
    for index, n in enumerate(nodes):
        n.setdefault("id", f"n{index}")
        n.setdefault("label", str(n["id"]))
    edges = [e for e in edges if isinstance(e, dict) and e.get("from") and e.get("to")]
    items = [i for i in items if isinstance(i, dict)]
    if not (nodes or items):
        return None
    return FigureSpec(
        id=str(data.get("id") or ""),
        title=str(data.get("title") or "Figure"),
        type=str(data.get("type") or ""),
        nodes=nodes, edges=edges, items=items,
        axes=data.get("axes") if isinstance(data.get("axes"), dict) else {},
        sources=[str(x) for x in (data.get("sources") or [])],
        direction=str(data["direction"]) if data.get("direction") else None,
    )


def _parse_block(block: Code) -> tuple[str, object] | None:
    lang = (block.lang or "").strip().lower()
    if lang not in CHART_LANGS | FIGURE_LANGS:
        return None
    try:
        data = json.loads(block.text)
    except (json.JSONDecodeError, TypeError):
        return None
    if not isinstance(data, dict):
        return None
    want = "chart" if lang in CHART_LANGS else "figure"
    schema = str(data.get("schema") or "")
    match = SCHEMA_RE.match(schema) if schema else None
    if schema and (match is None or match.group("kind") != want):
        return None
    if want == "chart":
        spec = chart_from_spec(data)
        if spec is not None:
            return ("chart", spec)
        # Valid but with nothing to draw (every value null): say so, with its markers, rather
        # than print raw JSON or drop it.
        names = ", ".join(str(s.get("name")) for s in data.get("series") or []
                          if isinstance(s, dict) and s.get("name"))
        label = f"Chart {data.get('id')}" if data.get("id") else "Chart"
        text = (f"*{label} — {data.get('title') or 'untitled'}: the dossier records no values "
                f"to plot{f' ({names})' if names else ''}.*")
        return ("empty", Callout(text=text, tone="note"))
    fig = figure_from_spec(data)
    return ("figure", fig) if fig else None


def extract_visuals(dossier: Dossier) -> tuple[int, int, int]:
    """Replace chart/figure code blocks in place with renderable blocks.

    Returns ``(charts, figures, unparsed)``. A block that will not parse stays a code block, so
    a malformed spec is visible rather than lost.
    """
    charts = figures = unparsed = 0
    for section in dossier.walk():
        blocks: list = []
        for block in section.blocks:
            lang = (block.lang or "").strip().lower() if isinstance(block, Code) else ""
            if not lang or lang not in CHART_LANGS | FIGURE_LANGS:
                blocks.append(block)
                continue
            parsed = _parse_block(block)
            if parsed is None:
                unparsed += 1
                blocks.append(block)
                continue
            kind, obj = parsed
            if kind == "empty":
                blocks.append(obj)
            elif kind == "chart":
                blocks.append(ChartBlock(spec=obj))     # type: ignore[arg-type]
                charts += 1
            else:
                blocks.append(FigureBlock(spec=obj))    # type: ignore[arg-type]
                figures += 1
        section.blocks = blocks
    return charts, figures, unparsed


# ── title block ──────────────────────────────────────────────────────────────

_RESULT_RE = re.compile(r"\b(PASS WITH DISCLOSURES|CONDITIONAL PASS|PASS|FAIL)\b")
_EQI_RE = re.compile(r"EQI\s*[:=]?\s*(?P<eqi>\d+(?:\.\d+)?)", re.I)


def _count(text: str, word: str) -> int | None:
    m = re.search(rf"(\d+)\s+{word}", text, re.I)
    return int(m.group(1)) if m else None


def parse_verification(dossier: Dossier) -> dict[str, Any] | None:
    """Verification result from the title block, falling back to the §21.8 verdict."""
    fm = dossier.front_matter
    raw = plain(fm.get("Verification") or "")
    if not raw:
        for banner in dossier.banners:
            text = plain(banner.text)
            if "verification" in text.lower()[:80] and _RESULT_RE.search(text):
                raw = text[:600]
                break
    if not raw:
        node = dossier.find("21.8")
        for block in (node.blocks if node else []):
            if isinstance(block, Callout | Paragraph) and _RESULT_RE.search(plain(block.text)):
                raw = plain(block.text)[:600]
                break
    if not raw:
        return None
    result = _RESULT_RE.search(raw)
    checks = re.search(r"(\d+)\s+of\s+(\d+)\s+checks", raw, re.I)
    out: dict[str, Any] = {
        "result": result.group(1) if result else raw.split("(")[0].strip()[:60],
        "overall_confidence": dossier.overall_confidence,
        "eqi": dossier.eqi,
        "blockers": _count(raw, "blocker"),
        "majors": _count(raw, "major"),
        "minors": _count(raw, "minor"),
        "checks_passed": int(checks.group(1)) if checks else None,
        "checks_executed": int(checks.group(2)) if checks else None,
        "detail": raw[:400],
        "source": "title block",
    }
    return out


def merge_verification_report(verification: dict | None, run_dir: Path) -> dict | None:
    """Fill gaps from ``<run>/qa/verification-report.json`` without overriding the dossier."""
    path = run_dir / "qa" / "verification-report.json"
    if not path.exists():
        return verification
    try:
        report = json.loads(path.read_text(encoding="utf8"))
    except (OSError, json.JSONDecodeError):
        return verification
    if not isinstance(report, dict):
        return verification
    out = dict(verification or {"source": "qa/verification-report.json"})
    for key in ("result", "overall_confidence", "eqi", "blockers", "majors", "minors",
                "checks_passed", "checks_executed"):
        if out.get(key) is None and report.get(key) is not None:
            out[key] = report[key]
    return out


def _hydrate(dossier: Dossier) -> None:
    fm = {k.lower(): v for k, v in dossier.front_matter.items()}
    dossier.version = plain(fm.get("version", "")) or None
    dossier.tier = plain(fm.get("output tier", "")) or None
    dossier.as_of = plain(fm.get("as-of date") or fm.get("research as of")
                          or fm.get("as of") or "") or None
    confidence = plain(fm.get("overall confidence", ""))
    if confidence:
        dossier.overall_confidence = confidence.split("(")[0].strip().strip("*") or None
        m = _EQI_RE.search(confidence)
        dossier.eqi = float(m.group("eqi")) if m else None
    dossier.verification = parse_verification(dossier)
    dossier.client_domain = resolve_client_domain(dossier)
    dossier.vertical = _vertical(dossier)


_URL_RE = re.compile(r"https?://(?:www\.)?(?P<host>[a-z0-9][a-z0-9.-]+\.[a-z]{2,})", re.I)
_DOMAIN_RE = re.compile(r"\b(?:www\.)?(?P<host>[a-z0-9][a-z0-9-]*\.(?:com|net|org|co|io|ai|"
                        r"com\.au|co\.uk|de|fr|jp|in|ca|ch|nl|se|no|es|it|com\.br))\b", re.I)


def resolve_client_domain(dossier: Dossier) -> str | None:
    """The client's web domain, from the title block or the §0 run contract, if stated."""
    fm = {k.lower(): plain(v) for k, v in dossier.front_matter.items()}
    for key in ("website", "domain", "web", "url"):
        if fm.get(key):
            m = _URL_RE.search(fm[key]) or _DOMAIN_RE.search(fm[key])
            if m:
                return m.group("host").lower()
    contract = dossier.find("0.1") or dossier.find("0")
    if contract is not None:
        for block in contract.blocks:
            if not isinstance(block, Table):
                continue
            for row in block.rows:
                label = plain(row[0]).lower() if row else ""
                if any(k in label for k in ("target", "website", "domain", "entity")):
                    m = _URL_RE.search(" ".join(row))
                    if m:
                        return m.group("host").lower()
    return None


def _vertical(dossier: Dossier) -> str | None:
    contract = dossier.find("0.1") or dossier.find("0")
    if contract is None:
        return None
    for block in contract.blocks:
        if isinstance(block, Table):
            for row in block.rows:
                if row and "vertical" in plain(row[0]).lower() and len(row) > 1:
                    codes = re.findall(r"V-[A-Z]{2,4}", plain(row[1]))
                    if codes:
                        return codes[0]
    return None


def vertical_words(dossier: Dossier) -> str:
    return VERTICAL_WORDS.get(dossier.vertical or "", "")


def load_dossier(path: str | Path) -> Dossier:
    """Parse, lift visual blocks and read the title block — the IR every exporter uses."""
    dossier = parse_dossier(path)
    extract_visuals(dossier)
    _hydrate(dossier)
    return dossier


# ── citation and cross-reference policy ──────────────────────────────────────

#: `[S-021 §Item 3.B]`, `[S-0101; S-0301]`, `[S-0101, calculated]`
CITATION_RE = re.compile(r"\[\s*S-\d+[^\]]*\]")
XREF_RE = re.compile(r"§\s*\d+(?:\.\d+)*")
SOURCE_HEADER_RE = re.compile(r"^\s*(sources?|source ?ids?|evidence|citation|\[s-ids?\])\s*$",
                              re.I)
#: Caveats written *inside* a citation bracket, re-emitted on their own when it is removed.
_CAVEAT_RE = re.compile(r"\b(SNIPPET-ONLY|INFERRED|ESTIMATED|ESTIMATE|STALE)\b")


def _tidy(text: str) -> str:
    text = re.sub(r"[ \t]*\(\s*[;,]?\s*\)", "", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"\s+([,.;:)])", r"\1", text)
    text = re.sub(r"\(\s+", "(", text)
    text = re.sub(r"(^|\s)[,;]\s*([.;,])", r"\1\2", text)
    text = re.sub(r"\.\s*\.", ".", text)
    text = re.sub(r"\s+\b(and|or)\s*([.;,:)])", r"\2", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def strip_citations(text: str) -> str:
    """Remove `[S-nnn …]` citations, keeping any evidence caveat they carried."""
    if not text:
        return text

    def replace(match: re.Match) -> str:
        caveats = list(dict.fromkeys(_CAVEAT_RE.findall(match.group(0))))
        return " ".join(f"[{c}]" for c in caveats) if caveats else ""

    return _tidy(CITATION_RE.sub(replace, text))


def strip_xrefs(text: str) -> str:
    """Remove `§x.y` cross-references, repairing the phrases that lean on them."""
    if not text or "§" not in text:
        return text
    text = re.sub(r"\((?:see|per|cf\.?|from|via|detailed in|full (?:detail|register) in)\s+"
                  r"§\s*\d+(?:\.\d+)*(?:\s*(?:,|and|;)\s*§\s*\d+(?:\.\d+)*)*\s*\)",
                  "", text, flags=re.I)
    text = re.sub(r"\b(see|per|cf\.?|detailed in|set out in|described in|covered in|listed in)\s+"
                  r"§\s*\d+(?:\.\d+)*(?:\s*(?:,|and|;)\s*§\s*\d+(?:\.\d+)*)*",
                  r"\1 elsewhere in this report", text, flags=re.I)
    text = re.sub(r"\bin\s+§\s*\d+(?:\.\d+)*", "elsewhere in this report", text, flags=re.I)
    text = XREF_RE.sub("", text)
    return _tidy(text)


def apply_text_policy(dossier: Dossier, *, citations: str = "keep", xrefs: str = "keep") -> int:
    """Rewrite every text-bearing block under the given policies. Returns blocks changed."""
    if citations == "keep" and xrefs == "keep":
        return 0

    def rewrite(text: str) -> str:
        out = text
        if citations == "strip":
            out = strip_citations(out)
        if xrefs == "strip":
            out = strip_xrefs(out)
        return out

    changed = 0
    for section in dossier.walk():
        section.title = rewrite(section.title)
        for block in section.blocks:
            if isinstance(block, Paragraph | Callout):
                new = rewrite(block.text)
                changed += new != block.text
                block.text = new
            elif isinstance(block, ListBlock):
                for item in block.items:
                    new = rewrite(item.text)
                    changed += new != item.text
                    item.text = new
            elif isinstance(block, Table):
                changed += _rewrite_table(block, rewrite, drop_source_cols=citations == "strip")
    return changed


def _rewrite_table(table: Table, rewrite, *, drop_source_cols: bool) -> int:
    changed = 0
    header = list(table.header or [])
    if drop_source_cols and header:
        keep = [i for i, h in enumerate(header) if not SOURCE_HEADER_RE.match(str(h))]
        if len(keep) < len(header) and keep:
            table.header = [header[i] for i in keep]
            table.rows = [[r[i] if i < len(r) else "" for i in keep] for r in table.rows]
            table.aligns = [table.aligns[i] for i in keep if i < len(table.aligns)]
            changed += 1
            header = table.header
    table.header = [rewrite(str(h)) for h in header]
    new_rows = []
    for row in table.rows:
        new = [rewrite(str(c)) for c in row]
        changed += new != row
        new_rows.append(new)
    table.rows = new_rows
    return changed


def first_callout(section: Section | None, tones: tuple[str, ...] = ("verdict",)) -> str:
    """The opening verdict a section leads with, if it has one."""
    if section is None:
        return ""
    for block in section.blocks:
        if isinstance(block, Callout) and block.tone in tones:
            return block.text.split("\n\n")[0]
    return ""
