"""Whitepaper build: DOCX, then PDF with a real table of contents.

LibreOffice recalculates ordinary fields on headless conversion but **not** indexes, so a ``TOC``
field converts to the "update this field" placeholder. A Word user never sees that; a PDF reader
always would. So when a PDF is asked for, the whitepaper is built twice:

1. render → convert → read back which printed page each heading landed on
2. render again with those page numbers written into the contents → convert

The second pass is safe because the body restarts page numbering at 1 in its own section: growing
the contents from one page to several shifts where the body *sits* in the PDF, but not the page
numbers **printed** on it — which is what the contents cites.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from ..context import RenderContext
from ..models import DocPlan, Dossier
from .docx_render import DocxRenderer
from .pdf_render import PdfConversionError, docx_to_pdf, page_count, soffice_binary


@dataclass
class WhitepaperResult:
    docx: Path
    pdf: Path | None = None
    pages: int | None = None
    toc_resolved: int = 0
    toc_total: int = 0
    warnings: list[str] = field(default_factory=list)


#: The body footer prints "Page N" (numbering restarts at 1 in the body section).
PAGE_FOOTER_RE = re.compile(r"\bPage\s+(\d+)\b")

_LIGATURES = str.maketrans({
    "ﬀ": "ff", "ﬁ": "fi", "ﬂ": "fl", "ﬃ": "ffi", "ﬄ": "ffl",
    "ﬅ": "st", "ﬆ": "st", "œ": "oe", "æ": "ae",
})


def _normalise(text: str) -> str:
    """Letters and digits only, ligatures expanded — robust to PDF text extraction."""
    flat = re.sub(r"[^a-z0-9]+", "", text.casefold().translate(_LIGATURES))
    # Some extractors decode the fi/fl ligature glyphs with a stray letter ("Prefliight"), so
    # the letters those ligatures touch are ignored on both sides of the comparison.
    return re.sub(r"[fil]", "", flat)


def _contains(page: str, needle: str) -> bool:
    """Exact containment, else a close match (extractors insert stray letters at ligatures)."""
    if needle in page:
        return True
    if len(needle) < 10:
        return False
    from difflib import SequenceMatcher

    hit = SequenceMatcher(None, needle, page, autojunk=False).find_longest_match(
        0, len(needle), 0, len(page))
    if hit.size < len(needle) // 3:
        return False
    start = max(0, hit.b - hit.a - 2)
    window = page[start:start + len(needle) + 6]
    return SequenceMatcher(None, needle, window, autojunk=False).ratio() >= 0.88


def measure_toc_pages(pdf_path: Path, entries: list[tuple[int, str, str, str]]) -> dict[str, int]:
    """Map each heading anchor to the page number *printed* on its page.

    Headings are matched in document order and never move backwards, so a phrase that also
    appears in the contents or a cross-reference cannot pull an entry to the wrong page.
    """
    try:
        from pypdf import PdfReader
    except ImportError:
        return {}
    reader = PdfReader(str(pdf_path))
    pages: list[str] = []
    printed: list[int | None] = []
    for page in reader.pages:
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        pages.append(_normalise(text))
        match = PAGE_FOOTER_RE.search(text)
        printed.append(int(match.group(1)) if match else None)

    resolved: dict[str, int] = {}
    cursor = 0
    max_jump = max(8, len(pages) // 3)
    for _level, number, title, anchor in entries:
        needle = _normalise(f"{number} {title}" if number else title)
        if not needle:
            continue
        for candidate in (needle, _normalise(title)):
            for index in range(cursor, min(len(pages), cursor + max_jump + 1)):
                # Only body pages print a number; the cover, front matter and contents never
                # hold the heading itself, and matching them strands the cursor there.
                if printed[index] is None:
                    continue
                if candidate and _contains(pages[index], candidate):
                    if printed[index] is not None:
                        resolved[anchor] = printed[index]
                    cursor = index
                    break
            if anchor in resolved:
                break
    return resolved


def build_whitepaper(dossier: Dossier, plan: DocPlan, out_docx: Path, ctx: RenderContext, *,
                     want_pdf: bool = True, template: Path | None = None, links: bool = True,
                     meta: dict | None = None, soffice: str = "soffice",
                     timeout: float = 600) -> WhitepaperResult:
    renderer = DocxRenderer(dossier, plan, ctx, template, links=links, meta=meta)
    renderer.render(out_docx)
    total = len([e for e in renderer.toc_entries if e[0] <= 2])
    if not want_pdf:
        return WhitepaperResult(docx=out_docx, toc_total=total)

    binary = soffice_binary(soffice)
    try:
        pdf_path = docx_to_pdf(out_docx, binary=binary, timeout=timeout)
    except PdfConversionError as exc:
        return WhitepaperResult(docx=out_docx, toc_total=total,
                                warnings=[f"PDF not produced: {exc}"])

    entries = [e for e in renderer.toc_entries if e[0] <= 2]
    pages = measure_toc_pages(pdf_path, entries)
    warnings: list[str] = []
    if not pages:
        warnings.append("Could not read page numbers back from the first-pass PDF; the contents "
                        "page is left as a field for Word to populate.")
        return WhitepaperResult(docx=out_docx, pdf=pdf_path, pages=page_count(pdf_path),
                                toc_total=total, warnings=warnings)

    final = DocxRenderer(dossier, plan, ctx, template, toc_pages=pages, links=links, meta=meta)
    final.render(out_docx)
    try:
        pdf_path = docx_to_pdf(out_docx, binary=binary, timeout=timeout)
    except PdfConversionError as exc:
        return WhitepaperResult(docx=out_docx, pdf=pdf_path, pages=page_count(pdf_path),
                                toc_total=total, warnings=[f"second PDF pass failed: {exc}"])
    missing = len(entries) - len(pages)
    if missing > 0:
        warnings.append(f"{missing} of {len(entries)} contents entries could not be page-matched.")
    return WhitepaperResult(docx=out_docx, pdf=pdf_path, pages=page_count(pdf_path),
                            toc_resolved=len(pages), toc_total=len(entries), warnings=warnings)
