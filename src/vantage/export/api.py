"""The export API the CLI and the TUI code against.

    opts = options_from_config(cfg, Path("~/.cache/vantage/run/acme-2026-10"), formats=["pptx"])
    result = export(opts, emit=print)

``export`` emits :class:`~vantage.models.events.RunEvent` objects as it goes: ``stage_start`` /
``stage_done`` for ``ingest``, ``plan``, ``assets``, ``charts`` and ``render:<format>``; ``log``;
``run_warning`` (a helper missing, a plan rejected, PDF skipped); one ``artifact`` per file; and
``run_done``. Heavy dependencies (python-pptx, python-docx, matplotlib, …) load lazily; if the
``export`` extra is missing, :class:`ExportDependencyError` says how to install it.
"""

from __future__ import annotations

import importlib
import json
import shutil
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..models.config import Config, ExportHelpersCfg
from ..models.events import RunEvent

FORMATS = ("pptx", "docx", "pdf", "html")
DEPTHS = ("exec", "standard", "full")
SITE_MODES = ("microsite", "deck")
AUTHORING = ("deterministic", "agents")

#: Python modules each format needs; all ship in the ``export`` extra.
DEPENDENCIES = {
    "pptx": ["pptx", "matplotlib", "PIL"],
    "docx": ["docx", "matplotlib", "PIL"],
    "pdf": ["docx", "pypdf", "matplotlib", "PIL"],
    "html": ["matplotlib"],
}
_DIST = {"pptx": "python-pptx", "docx": "python-docx", "PIL": "pillow", "pypdf": "pypdf",
         "matplotlib": "matplotlib", "numpy": "numpy", "plotly": "plotly"}


class ExportDependencyError(RuntimeError):
    """The ``export`` extra is not installed."""


@dataclass
class ExportOptions:
    dossier: Path                     # a *-vantage.md file or a run directory containing one
    formats: list[str]                # subset of pptx docx pdf html (pdf implies docx)
    depth: str = "standard"           # exec | standard | full
    site_mode: str = "microsite"      # microsite | deck
    authoring: str = "deterministic"  # deterministic | agents
    out_dir: Path | None = None       # None -> <run dir>/exports
    classification: str = "Confidential"
    brand: str | None = None          # domain, themed via get-brand
    client_logo: bool = True
    helpers: ExportHelpersCfg = field(default_factory=ExportHelpersCfg)
    harness_dir: Path | None = None   # None -> bundled harness/export


@dataclass
class Check:
    group: str
    name: str
    status: str          # "ok" | "warn" | "fail"
    detail: str = ""

    def to_dict(self) -> dict[str, str]:
        return {"group": self.group, "name": self.name, "status": self.status,
                "detail": self.detail}


@dataclass
class ExportResult:
    out_dir: Path
    manifest: Path
    artifacts: list[dict] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    plans: dict[str, str] = field(default_factory=dict)
    verification: dict | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "out_dir": str(self.out_dir),
            "manifest": str(self.manifest),
            "artifacts": [{**a, "path": str(a["path"])} for a in self.artifacts],
            "warnings": list(self.warnings),
            "plans": dict(self.plans),
            "verification": self.verification,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Options
# ─────────────────────────────────────────────────────────────────────────────


def default_harness_dir(cfg: Config | None = None) -> Path:
    from ..settings import harness_dir

    base = harness_dir(cfg) if cfg is not None else harness_dir(Config())
    return base / "export"


def options_from_config(cfg: Config, dossier: Path, **overrides: Any) -> ExportOptions:
    """Build options from ``cfg.export``; explicit, non-``None`` ``overrides`` win.

    ``helpers`` may be an :class:`ExportHelpersCfg` or a partial dict merged over the config.
    """
    ex = cfg.export
    values: dict[str, Any] = {
        "formats": list(ex.formats), "depth": ex.depth, "site_mode": ex.site_mode,
        "authoring": ex.authoring, "out_dir": ex.out_dir, "classification": ex.classification,
        "brand": ex.brand, "client_logo": ex.client_logo,
        "helpers": ex.helpers.model_copy(deep=True), "harness_dir": None,
    }
    for key, value in overrides.items():
        if value is None:
            continue
        if key not in values:
            raise TypeError(f"unknown export option: {key}")
        if key == "helpers" and isinstance(value, dict):
            values["helpers"] = values["helpers"].model_copy(update=value)
        else:
            values[key] = value
    formats = [str(f).lower() for f in values["formats"]]
    out_dir = values["out_dir"]
    harness = values["harness_dir"] or default_harness_dir(cfg)
    return ExportOptions(
        dossier=Path(dossier).expanduser(),
        formats=formats,
        depth=values["depth"],
        site_mode=values["site_mode"],
        authoring=values["authoring"],
        out_dir=Path(out_dir).expanduser() if out_dir else None,
        classification=values["classification"],
        brand=values["brand"] or None,
        client_logo=bool(values["client_logo"]),
        helpers=values["helpers"],
        harness_dir=Path(harness).expanduser(),
    )


def find_dossier(path: Path) -> Path:
    """Resolve a run directory (or a dossier path) to its ``*-vantage.md``."""
    path = Path(path).expanduser()
    if path.is_file():
        return path.resolve()
    if path.is_dir():
        hits = sorted(path.glob("*-vantage.md"))
        if hits:
            preferred = [h for h in hits if h.stem == f"{path.name}-vantage"]
            return (preferred or hits)[0].resolve()
        raise FileNotFoundError(f"no *-vantage.md dossier in {path}")
    raise FileNotFoundError(f"dossier not found: {path}")


def _validate(opts: ExportOptions) -> list[str]:
    formats = list(dict.fromkeys(f.lower() for f in opts.formats))
    unknown = [f for f in formats if f not in FORMATS]
    if unknown or not formats:
        raise ValueError(f"unknown format(s): {', '.join(unknown) or '(none)'}. "
                         f"Known: {', '.join(FORMATS)}")
    if opts.depth not in DEPTHS:
        raise ValueError(f"depth must be one of {', '.join(DEPTHS)}, got {opts.depth!r}")
    if opts.site_mode not in SITE_MODES:
        raise ValueError(f"site_mode must be one of {', '.join(SITE_MODES)}")
    if opts.authoring not in AUTHORING:
        raise ValueError(f"authoring must be one of {', '.join(AUTHORING)}")
    if not str(opts.classification).strip():
        raise ValueError("classification must not be empty")
    return formats


def check_dependencies(formats: list[str]) -> None:
    missing = []
    for module in dict.fromkeys(m for f in formats for m in DEPENDENCIES.get(f, [])):
        try:
            importlib.import_module(module)
        except ImportError:
            missing.append(_DIST.get(module, module))
    if missing:
        raise ExportDependencyError(
            f"vantage export needs {', '.join(missing)} — install the export extra: "
            f"uv sync --extra export")


# ─────────────────────────────────────────────────────────────────────────────
# Export
# ─────────────────────────────────────────────────────────────────────────────


class _Emitter:
    def __init__(self, emit: Callable[[RunEvent], None] | None) -> None:
        self._emit = emit
        self.warnings: list[str] = []

    def event(self, type_: str, *, stage: str | None = None, message: str | None = None,
              data: dict | None = None, agent: str | None = None) -> None:
        if self._emit is None:
            return
        self._emit(RunEvent(type=type_, ts=time.time(), stage=stage, message=message,
                            agent=agent, data=data or {}))

    def warn(self, message: str) -> None:
        if message not in self.warnings:
            self.warnings.append(message)
            self.event("run_warning", message=message)

    def log(self, message: str, agent: str | None = None) -> None:
        self.event("log", message=message, agent=agent)


def export(opts: ExportOptions, emit: Callable[[RunEvent], None] | None = None) -> ExportResult:
    formats = _validate(opts)
    check_dependencies(formats)

    from .context import RenderContext
    from .dossier import load_dossier, merge_verification_report
    from .pipeline import load_or_build_plans, write_plans
    from .theme import DEFAULT_THEME

    ev = _Emitter(emit)
    source = find_dossier(opts.dossier)
    run_dir = source.parent
    out_dir = (opts.out_dir or run_dir / "exports").expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = source.stem.removesuffix("-vantage")
    ev.event("run_start", message=str(source),
             data={"dossier": str(source), "out_dir": str(out_dir), "formats": formats})

    # ── ingest ───────────────────────────────────────────────────────────────
    ev.event("stage_start", stage="ingest", message=source.name)
    dossier = load_dossier(source)
    verification = merge_verification_report(dossier.verification, run_dir)
    dossier.verification = verification
    stats = dossier.stats()
    unparsed = sum(1 for s in dossier.walk() for b in s.blocks
                   if getattr(b, "kind", "") == "code"
                   and (getattr(b, "lang", "") or "").lower() in {"chart-data", "figure-spec"})
    if unparsed:
        ev.warn(f"{unparsed} chart/figure block(s) did not parse and are shown as code")
    ev.event("stage_done", stage="ingest", message=dossier.client,
             data={**stats, "client": dossier.client, "as_of": dossier.as_of,
                   "version": dossier.version, "verification": verification})

    # ── plan ─────────────────────────────────────────────────────────────────
    ev.event("stage_start", stage="plan", message=opts.authoring)
    if opts.authoring == "agents":
        from .agents import run_workflow

        write_plans(dossier, out_dir, opts.depth, opts.site_mode, keep_authored=True)
        ok, reason = run_workflow(
            dossier=source, out_dir=out_dir,
            harness_dir=opts.harness_dir or default_harness_dir(), depth=opts.depth,
            formats=formats, site_mode=opts.site_mode, classification=opts.classification,
            brand=opts.brand, log=lambda line: ev.log(line, agent="export-workflow"))
        if not ok:
            ev.warn(f"agent authoring unavailable — {reason}")
    plan_warnings: list[str] = []
    deck, doc, site, plans = load_or_build_plans(dossier, out_dir, opts.depth, opts.site_mode,
                                                 plan_warnings)
    for message in plan_warnings:
        ev.warn(message)
    site = site.model_copy(update={"mode": opts.site_mode})
    ev.event("stage_done", stage="plan", data={"plans": plans, "slides": len(deck.slides),
                                               "sections": len(doc.sections),
                                               "pages": len(site.pages)})

    # ── assets ───────────────────────────────────────────────────────────────
    ev.event("stage_start", stage="assets")
    ctx = RenderContext.build(out_dir=out_dir, classification=opts.classification,
                              helpers=opts.helpers, theme=DEFAULT_THEME, warn=ev.warn,
                              log=ev.log)
    if opts.brand:
        brand = ctx.tools.brand(opts.brand)
        if brand is None:
            ev.warn(f"could not theme with --brand {opts.brand}; using the neutral theme")
        else:
            ctx.brand = brand
            ctx.retheme(DEFAULT_THEME.with_brand(brand.colors, brand.fonts, name=brand.name,
                                                 domain=opts.brand))
    if opts.client_logo:
        if not dossier.client_domain:
            ev.warn("client_logo: no web domain stated in the dossier — cover logo skipped")
        elif opts.helpers.brand:
            client = ctx.tools.brand(dossier.client_domain)
            ctx.client_logo = client.logo_png if client else None
            if ctx.client_logo is None:
                ev.warn(f"client_logo: no logo found for {dossier.client_domain}")
    _prefetch(ctx, deck, site)
    ev.event("stage_done", stage="assets", data={
        "brand": ctx.theme.brand_name, "client_logo": bool(ctx.client_logo),
        "icons": len(list((ctx.assets_dir / "icons").glob("*.svg")))
        if (ctx.assets_dir / "icons").exists() else 0,
        "images": len(list((ctx.assets_dir / "stock").glob("*.jpg")))
        if (ctx.assets_dir / "stock").exists() else 0})

    # ── charts + figures ─────────────────────────────────────────────────────
    ev.event("stage_start", stage="charts")
    _prerender(ctx, dossier, deck, formats)
    ev.event("stage_done", stage="charts",
             data={"charts": ctx.charts.drawn, "figures": dict(ctx.figures.engines)})

    meta = {**(verification or {}), "overall_confidence": dossier.overall_confidence,
            "eqi": dossier.eqi}
    artifacts: list[dict] = []

    def artifact(fmt: str, path: Path, pages: int | None = None,
                 slides: int | None = None) -> None:
        item = {"format": fmt, "path": path, "bytes": path.stat().st_size, "pages": pages,
                "slides": slides}
        artifacts.append(item)
        ev.event("artifact", stage=f"render:{fmt}", message=str(path),
                 data={**item, "path": str(path)})

    # ── render ───────────────────────────────────────────────────────────────
    if "pptx" in formats:
        from .render.pptx_render import render_pptx

        ev.event("stage_start", stage="render:pptx")
        path = render_pptx(deck, out_dir / f"{slug}-deck.pptx", ctx, meta)
        artifact("pptx", path, slides=len(deck.slides))
        ev.event("stage_done", stage="render:pptx", data={"slides": len(deck.slides)})

    if "docx" in formats or "pdf" in formats:
        from .render.whitepaper import build_whitepaper

        want_pdf = "pdf" in formats
        ev.event("stage_start", stage="render:docx")
        if want_pdf:
            ev.event("stage_start", stage="render:pdf")
        built = build_whitepaper(
            dossier, doc, out_dir / f"{slug}-whitepaper.docx", ctx, want_pdf=want_pdf,
            meta=meta, soffice=opts.helpers.libreoffice_bin,
            timeout=max(600.0, opts.helpers.timeout_seconds * 10))
        for message in built.warnings:
            ev.warn(message)
        if "docx" in formats:
            artifact("docx", built.docx, pages=built.pages)
        ev.event("stage_done", stage="render:docx",
                 data={"contents_entries": built.toc_total, "pages": built.pages})
        if want_pdf:
            if built.pdf is not None:
                artifact("pdf", built.pdf, pages=built.pages)
            else:
                ev.warn("PDF was requested but not produced — see the warning above")
            ev.event("stage_done", stage="render:pdf", data={"pages": built.pages})

    if "html" in formats:
        from .render.html_render import render_site

        ev.event("stage_start", stage="render:html", message=opts.site_mode)
        name = f"{slug}-{'deck' if opts.site_mode == 'deck' else 'microsite'}.html"
        path = render_site(dossier, out_dir / name, ctx, deck=deck, site=site,
                           mode=opts.site_mode, meta=meta)
        artifact("html", path, slides=len(deck.slides) if opts.site_mode == "deck" else None)
        ev.event("stage_done", stage="render:html", data={"mode": opts.site_mode})

    # ── manifest ─────────────────────────────────────────────────────────────
    warnings = list(dict.fromkeys(ev.warnings + ctx.warnings))
    manifest = out_dir / "manifest.json"
    result = ExportResult(out_dir=out_dir, manifest=manifest, artifacts=artifacts,
                          warnings=warnings, plans=plans, verification=verification)
    _write_manifest(result, dossier, opts, formats, ctx)
    ev.event("run_done", message=str(out_dir), data={"result": result.to_dict()})
    return result


def _prefetch(ctx, deck, site) -> None:
    """Warm the icon and image caches so render stages are pure layout."""
    from .dossier import SECTION_ICON

    icons = {s.icon for s in deck.slides if s.icon}
    icons |= {k.icon for s in deck.slides for k in s.kpis if k.icon}
    icons |= {p.icon for p in site.pages if p.icon} | set(SECTION_ICON.values())
    for name in sorted(i for i in icons if i):
        ctx.icon_svg(name)
    queries = [s.image_query for s in deck.slides if s.image_query]
    queries += [p.image_query for p in site.pages if p.image_query]
    for query in dict.fromkeys(q for q in queries if q):
        ctx.stock(query)


def _prerender(ctx, dossier, deck, formats: list[str]) -> None:
    from .models import ChartBlock, FigureBlock

    office = any(f in formats for f in ("pptx", "docx", "pdf"))
    html = "html" in formats
    for section in dossier.walk():
        for block in section.blocks:
            if isinstance(block, FigureBlock):
                ctx.figures.render(block.spec)
            elif isinstance(block, ChartBlock) and html and ctx.charts.engine != "plotly":
                ctx.charts.svg(block.spec, width_in=7.5)
    if office:
        for slide in deck.slides:
            if slide.figure is not None:
                ctx.figures.render(slide.figure)


def _write_manifest(result: ExportResult, dossier, opts: ExportOptions, formats: list[str],
                    ctx) -> None:
    from .theme import HANDLING

    data = {
        "client": dossier.client,
        "classification": opts.classification,
        "handling": HANDLING,
        "source_dossier": dossier.source_path,
        "version": dossier.version,
        "tier": dossier.tier,
        "as_of": dossier.as_of,
        "overall_confidence": dossier.overall_confidence,
        "eqi": dossier.eqi,
        "verification": result.verification,
        "formats": formats,
        "depth": opts.depth,
        "site_mode": opts.site_mode,
        "authoring": opts.authoring,
        "brand": opts.brand,
        "theme": ctx.theme.brand_name or ctx.theme.name,
        "plans": result.plans,
        "artifacts": [{**a, "path": str(Path(a["path"]).relative_to(result.out_dir))}
                      for a in result.artifacts],
        "warnings": result.warnings,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
    result.manifest.write_text(json.dumps(data, indent=2), encoding="utf8")


# ─────────────────────────────────────────────────────────────────────────────
# Doctor
# ─────────────────────────────────────────────────────────────────────────────


def doctor(cfg: Config) -> list[Check]:
    """Readiness of every export dependency and helper. Never raises."""
    from .helpers import Toolbox
    from .render.pdf_render import soffice_binary

    checks: list[Check] = []
    pkg = Path(__file__).resolve().parent
    for module in ("pptx", "docx", "matplotlib", "PIL", "pypdf", "numpy", "plotly"):
        name = _DIST.get(module, module)
        try:
            importlib.import_module(module)
            checks.append(Check("export", f"python: {name}", "ok"))
        except ImportError:
            status = "warn" if module == "plotly" else "fail"
            checks.append(Check("export", f"python: {name}", status,
                                "missing — uv sync --extra export"))
    template = pkg / "assets" / "templates" / "vantage-whitepaper.docx"
    checks.append(Check("export", "whitepaper template",
                        "ok" if template.exists() else "fail",
                        str(template) if template.exists()
                        else "missing — uv run python scripts/build-export-template.py"))
    site = pkg / "assets" / "site"
    have = all((site / n).exists() for n in ("site.css", "deck.js", "microsite.js"))
    checks.append(Check("export", "site assets", "ok" if have else "fail", str(site)))
    harness = default_harness_dir(cfg)
    checks.append(Check("export", "export harness",
                        "ok" if (harness / "workflows" / "vantage-export.workflow.mjs").exists()
                        else "warn", str(harness)))
    helpers = cfg.export.helpers
    soffice = soffice_binary(helpers.libreoffice_bin)
    checks.append(Check("export", "LibreOffice (PDF)", "ok" if soffice else "warn",
                        soffice or "not found — PDF export unavailable; .docx still builds "
                                   "(macOS: brew install --cask libreoffice)"))

    def tool(name: str, binary: str, enabled: bool, purpose: str) -> None:
        if not enabled:
            checks.append(Check("export helpers", name, "ok", f"disabled in config ({purpose})"))
            return
        found = shutil.which(binary)
        checks.append(Check("export helpers", name, "ok" if found else "warn",
                            found or f"{binary} not on PATH — built-in fallback for {purpose}"))

    tool("icons", Toolbox.BINARIES["icons"], helpers.icons, "icons")
    tool("brand", Toolbox.BINARIES["brand"], helpers.brand, "--brand theming and client logos")
    tool("stock images", Toolbox.BINARIES["stock"], helpers.stock_images, "cover imagery")
    diagram_bins = {"dgm": "dgm", "drawio": "drawio", "mermaid": "mmdc"}
    if helpers.diagrams == "none":
        checks.append(Check("export helpers", "diagrams", "ok", "disabled (figures as tables)"))
    elif helpers.diagrams == "auto":
        found = [f"{k}={shutil.which(v)}" for k, v in diagram_bins.items() if shutil.which(v)]
        checks.append(Check("export helpers", "diagrams", "ok",
                            ", ".join(found) if found else "no dgm/drawio/mmdc — built-in "
                                                            "matplotlib diagrams"))
    else:
        tool("diagrams", diagram_bins[helpers.diagrams], True, "figure-spec diagrams")
    if helpers.illustrations == "napkin":
        tool("illustrations", "napkin", True, "concept illustrations (spends Napkin credits)")
    else:
        checks.append(Check("export helpers", "illustrations", "ok", "none (opt-in: napkin)"))
    raster = shutil.which("rsvg-convert") or shutil.which("magick")
    checks.append(Check("export helpers", "SVG rasterizer", "ok" if raster else "warn",
                        raster or "no rsvg-convert/ImageMagick — Office files use built-in "
                                  "icon shapes"))
    if helpers.charts == "plotly":
        try:
            importlib.import_module("kaleido")
            checks.append(Check("export helpers", "plotly static export", "ok", "kaleido"))
        except ImportError:
            checks.append(Check("export helpers", "plotly static export", "warn",
                                "kaleido missing — Office charts use matplotlib; HTML stays "
                                "interactive"))
    if cfg.export.authoring == "agents":
        from .agents import claude_cli

        cli = claude_cli()
        checks.append(Check("export", "agent authoring", "ok" if shutil.which(cli) else "warn",
                            shutil.which(cli) or f"{cli} not on PATH — deterministic plans only"))
    return checks
