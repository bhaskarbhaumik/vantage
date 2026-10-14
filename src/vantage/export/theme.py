"""Design tokens for every export renderer — the one place colour and type are defined.

The default is the neutral **Vantage** theme: near-black ink, one restrained accent, generous
white space, a serif display face over a humanist sans body. ``--brand <domain>`` swaps the accent
family (and, when the brand names real typefaces, the faces) for the pursuing organization's own,
via :func:`Theme.with_brand`. Nothing else in the package hard-codes a colour or a font.

The governing rule is *ink and paper first, one accent second*: secondary hues differentiate
series and status only, and never carry meaning on their own.
"""

from __future__ import annotations

import colorsys
from dataclasses import dataclass, field, replace

#: Wherever a score appears, this sentence travels with it, verbatim.
SCORE_DISCLAIMER = (
    "Scores are evidence-based internal decision aids derived from outside-in public evidence. "
    "They are not measurements of the client and must not be presented to the client."
)

#: Handling statement written into document properties and the export manifest.
HANDLING = "Internal use only. Not for client distribution."

PRODUCT = "Vantage"
DOC_KIND = "Vantage dossier"


def _hex(value: str) -> str:
    return value.lstrip("#").upper()


def _rgb(value: str) -> tuple[float, float, float]:
    h = _hex(value)
    return int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255


def _to_hex(r: float, g: float, b: float) -> str:
    return "".join(f"{max(0, min(255, round(c * 255))):02X}" for c in (r, g, b))


def luminance(value: str) -> float:
    """WCAG relative luminance, 0 (black) to 1 (white)."""

    def chan(c: float) -> float:
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (chan(c) for c in _rgb(value))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: str, b: str) -> float:
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def shade(value: str, lightness: float) -> str:
    """Same hue and saturation, new HLS lightness (0–1)."""
    h, _l, s = colorsys.rgb_to_hls(*_rgb(value))
    return _to_hex(*colorsys.hls_to_rgb(h, max(0.0, min(1.0, lightness)), s))


def mix(a: str, b: str, t: float) -> str:
    ra, rb = _rgb(a), _rgb(b)
    return _to_hex(*(x + (y - x) * t for x, y in zip(ra, rb, strict=True)))


@dataclass(frozen=True)
class Palette:
    """Hex tokens without the leading ``#`` (python-pptx/-docx take them that way)."""

    ink: str = "1B1F24"          # body text, dark surfaces
    ink_soft: str = "3D4650"     # secondary prose
    ink_faint: str = "6B7480"    # captions, metadata (AA on white)
    paper: str = "FFFFFF"
    surface: str = "F4F6F8"      # tiles, zebra rows, callout fills
    rule: str = "D9DEE5"
    dark_surface: str = "262C33"  # tiles on dark slides
    on_dark_soft: str = "B9C2CC"  # secondary text on dark
    on_dark_faint: str = "8C96A1"

    accent: str = "2F5D8A"       # the single highlight
    accent_deep: str = "1F3F5F"  # headings in the whitepaper
    accent_tint: str = "E7EEF5"  # verdict callouts
    accent_on_dark: str = "9DBCDD"

    teal: str = "2A8C82"
    amber: str = "D9922E"
    red: str = "C0473A"
    green: str = "3C8D5A"
    violet: str = "6A5A9E"


@dataclass(frozen=True)
class Typography:
    """Faces per medium. Office files name installed faces; HTML gets a full fallback stack."""

    display: str = "Georgia"               # headlines, KPI values (Office)
    body: str = "Arial"                    # prose, tables (Office)
    mono: str = "Courier New"              # claim identifiers (Office)
    display_css: str = "'Iowan Old Style', 'Palatino Linotype', Georgia, 'Times New Roman', serif"
    body_css: str = ("system-ui, -apple-system, 'Segoe UI', 'Helvetica Neue', Arial, "
                     "'Noto Sans', sans-serif")
    mono_css: str = "ui-monospace, 'SF Mono', 'Cascadia Code', Menlo, Consolas, monospace"
    chart: tuple[str, ...] = ("Helvetica Neue", "Arial", "DejaVu Sans")


@dataclass(frozen=True)
class Theme:
    palette: Palette = field(default_factory=Palette)
    type: Typography = field(default_factory=Typography)
    name: str = PRODUCT
    #: Set when ``--brand`` themed the export: the organization's display name and domain.
    brand_name: str | None = None
    brand_domain: str | None = None

    # Categorical series — the accent leads, secondaries differentiate. Ordered so the first
    # three stay distinguishable in greyscale and for the common colour-vision deficiencies.
    @property
    def chart_series(self) -> list[str]:
        p = self.palette
        return [p.accent, p.amber, p.teal, p.accent_deep, p.red, p.ink_faint, p.violet, p.green]

    @property
    def chart_sequential(self) -> list[str]:
        p = self.palette
        return [p.accent_tint, shade(p.accent, 0.78), shade(p.accent, 0.62), p.accent,
                p.accent_deep, shade(p.accent_deep, 0.15)]

    def css_vars(self) -> str:
        """The palette and faces as CSS custom properties, for the single-file HTML."""
        p, t = self.palette, self.type
        pairs = {
            "ink": p.ink, "ink-soft": p.ink_soft, "ink-faint": p.ink_faint, "paper": p.paper,
            "surface": p.surface, "rule": p.rule, "dark-surface": p.dark_surface,
            "on-dark-soft": p.on_dark_soft, "on-dark-faint": p.on_dark_faint,
            "accent": p.accent, "accent-deep": p.accent_deep, "accent-tint": p.accent_tint,
            "accent-on-dark": p.accent_on_dark, "teal": p.teal, "amber": p.amber, "red": p.red,
            "green": p.green,
        }
        lines = [f"  --{k}: #{v.lower()};" for k, v in pairs.items()]
        lines += [f"  --font-display: {t.display_css};", f"  --font-body: {t.body_css};",
                  f"  --font-mono: {t.mono_css};"]
        return ":root {\n" + "\n".join(lines) + "\n}"

    def with_brand(self, colors: list[dict], fonts: list[dict] | None = None, *,
                   name: str | None = None, domain: str | None = None) -> Theme:
        """Return a theme whose accent family comes from a get-brand palette.

        Picks the ``brand`` colour (else ``accent``, else the most saturated mid-tone), then
        derives deep/tint/on-dark variants and darkens it until it reads on white (≥ 4.5:1), so a
        pale brand colour never produces illegible headings.
        """
        accent = _pick_accent(colors)
        if accent is None:
            return replace(self, brand_name=name, brand_domain=domain)
        h, light, s = colorsys.rgb_to_hls(*_rgb(accent))
        while contrast(accent, "FFFFFF") < 4.5 and light > 0.05:
            light -= 0.04
            accent = _to_hex(*colorsys.hls_to_rgb(h, light, s))
        secondary = _pick_secondary(colors, accent)
        palette = replace(
            self.palette,
            accent=accent,
            accent_deep=shade(accent, max(0.12, light * 0.7)),
            accent_tint=mix(accent, "FFFFFF", 0.9),
            accent_on_dark=mix(accent, "FFFFFF", 0.55),
            teal=secondary or self.palette.teal,
        )
        typography = self.type
        display, body = _pick_fonts(fonts or [])
        if display:
            typography = replace(typography, display=display,
                                 display_css=f"'{display}', {self.type.display_css}")
        if body:
            typography = replace(typography, body=body,
                                 body_css=f"'{body}', {self.type.body_css}")
        return replace(self, palette=palette, type=typography, brand_name=name, brand_domain=domain)


def _clean(color: dict) -> str | None:
    raw = str(color.get("hex") or "").strip().lstrip("#")
    if len(raw) == 3:
        raw = "".join(c * 2 for c in raw)
    if len(raw) != 6:
        return None
    try:
        int(raw, 16)
    except ValueError:
        return None
    return raw.upper()


def _saturation(value: str) -> float:
    return colorsys.rgb_to_hls(*_rgb(value))[2]


def _pick_accent(colors: list[dict]) -> str | None:
    usable = [(c, h) for c in colors if (h := _clean(c))]
    for wanted in ("brand", "accent", "primary"):
        for c, h in usable:
            if str(c.get("type") or "").lower() == wanted and 0.04 < luminance(h) < 0.85:
                return h
    mids = [h for _c, h in usable if 0.03 < luminance(h) < 0.8]
    return max(mids, key=_saturation) if mids else None


def _pick_secondary(colors: list[dict], accent: str) -> str | None:
    for c in colors:
        h = _clean(c)
        if not h or h == accent:
            continue
        if str(c.get("type") or "").lower() == "accent" and contrast(h, "FFFFFF") >= 3:
            return h
    return None


#: get-brand sometimes reports a placeholder rather than a face ("Font Black").
_GENERIC_FONT_PREFIXES = ("font ", "custom", "unknown", "default")


def _pick_fonts(fonts: list[dict]) -> tuple[str | None, str | None]:
    display = body = None
    for f in fonts:
        name = str(f.get("name") or "").strip()
        if not name or name.lower().startswith(_GENERIC_FONT_PREFIXES) or len(name) > 40:
            continue
        kind = str(f.get("type") or "").lower()
        if kind in {"title", "heading", "display"} and not display:
            display = name
        elif kind in {"body", "text"} and not body:
            body = name
    return display, body


DEFAULT_THEME = Theme()
