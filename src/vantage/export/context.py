"""Everything a renderer needs besides the plan: theme, marking, imagery and the helpers."""

from __future__ import annotations

import base64
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from ..models.config import ExportHelpersCfg
from .helpers import BrandAssets, Toolbox
from .render.charts import ChartRenderer
from .theme import DEFAULT_THEME, Theme
from .visuals import FigureRenderer


@dataclass
class RenderContext:
    theme: Theme
    classification: str
    assets_dir: Path
    tools: Toolbox
    charts: ChartRenderer
    figures: FigureRenderer
    #: The client's logo (cover only), and the pursuing organization's (``--brand``) furniture.
    client_logo: Path | None = None
    brand: BrandAssets | None = None
    warnings: list[str] = field(default_factory=list)
    _stock: dict[str, Path | None] = field(default_factory=dict)
    _icons_png: dict[tuple[str, str], Path | None] = field(default_factory=dict)

    @classmethod
    def build(cls, *, out_dir: Path, classification: str, helpers: ExportHelpersCfg,
              theme: Theme = DEFAULT_THEME, warn: Callable[[str], None] | None = None,
              log: Callable[[str], None] | None = None) -> RenderContext:
        assets = Path(out_dir) / ".assets"
        assets.mkdir(parents=True, exist_ok=True)
        warnings: list[str] = []

        def _warn(message: str) -> None:
            warnings.append(message)
            if warn:
                warn(message)

        tools = Toolbox(helpers, assets, warn=_warn, log=log)
        charts = ChartRenderer(theme, assets / "charts", helpers.charts, warn=_warn)
        figures = FigureRenderer(theme, tools, assets / "figures", helpers.diagrams)
        return cls(theme=theme, classification=classification, assets_dir=assets, tools=tools,
                   charts=charts, figures=figures, warnings=warnings)

    def retheme(self, theme: Theme) -> None:
        self.theme = theme
        self.charts.theme = theme
        self.figures.theme = theme

    # ── imagery ──────────────────────────────────────────────────────────────
    def stock(self, query: str | None) -> Path | None:
        if not query:
            return None
        if query not in self._stock:
            self._stock[query] = self.tools.stock_image(query)
        return self._stock[query]

    def icon_png(self, name: str | None, color: str) -> Path | None:
        if not name:
            return None
        key = (name, color)
        if key not in self._icons_png:
            self._icons_png[key] = self.tools.icon_png(name, color)
        return self._icons_png[key]

    def icon_svg(self, name: str | None) -> str | None:
        return self.tools.icon_svg(name) if name else None

    @property
    def brand_logo(self) -> Path | None:
        return self.brand.logo_png if self.brand else None

    @property
    def brand_logo_dark(self) -> Path | None:
        return (self.brand.logo_png_dark or self.brand.logo_png) if self.brand else None


def data_uri(path: Path | None) -> str | None:
    """A file as a ``data:`` URI, so the HTML needs nothing beside itself."""
    if path is None or not Path(path).exists():
        return None
    suffix = Path(path).suffix.lower()
    mime = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".svg": "image/svg+xml", ".webp": "image/webp", ".gif": "image/gif"}.get(suffix)
    if mime is None:
        return None
    return f"data:{mime};base64,{base64.b64encode(Path(path).read_bytes()).decode('ascii')}"
