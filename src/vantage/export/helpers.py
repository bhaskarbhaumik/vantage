"""Optional helper CLIs: icons, brand, stock imagery, diagrams, illustrations, rasterizing.

Every helper is optional. A missing binary, a non-zero exit or a timeout degrades to the built-in
fallback and records one ``run_warning`` per helper — never a failed export. Results are cached
under ``<out_dir>/.assets/`` so a re-render is fast and offline.

| config (``export.helpers``) | binary                     | used for                                 |
|-----------------------------|----------------------------|------------------------------------------|
| ``icons``                   | ``get-icon``               | slide headers, KPI tiles, dividers, nav  |
| ``brand``                   | ``get-brand``              | ``--brand`` theming, client cover logo   |
| ``stock_images``            | ``get-stock``              | cover and section-opener imagery         |
| ``diagrams``                | ``dgm`` / ``drawio`` / ``mmdc`` | figure-spec blocks                  |
| ``illustrations``           | ``napkin``                 | one concept illustration (spends credits)|
| —                           | ``rsvg-convert`` / ``magick`` | SVG → PNG for the Office formats      |
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..models.config import ExportHelpersCfg

#: The icon family tried first, so every icon in one export shares a stroke and grid.
ICON_FAMILY = "lucide"
_SAFE = re.compile(r"[^a-z0-9._-]+")


def _slug(text: str, limit: int = 60) -> str:
    return _SAFE.sub("-", text.lower()).strip("-")[:limit] or "x"


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf8")).hexdigest()[:16]


@dataclass
class BrandAssets:
    domain: str
    name: str | None
    colors: list[dict]
    fonts: list[dict]
    logo_png: Path | None = None       # for light backgrounds
    logo_png_dark: Path | None = None  # for dark backgrounds (falls back to logo_png)
    logo_svg: str | None = None


class Toolbox:
    """Thin, injectable wrapper over the helper binaries (tests replace ``which``/``run``)."""

    BINARIES = {
        "icons": "get-icon", "brand": "get-brand", "stock": "get-stock", "dgm": "dgm",
        "drawio": "drawio", "mermaid": "mmdc", "napkin": "napkin", "rsvg": "rsvg-convert",
        "magick": "magick",
    }

    def __init__(self, cfg: ExportHelpersCfg, assets_dir: Path,
                 warn: Callable[[str], None] | None = None,
                 log: Callable[[str], None] | None = None) -> None:
        self.cfg = cfg
        self.assets_dir = Path(assets_dir)
        self.timeout = float(cfg.timeout_seconds)
        self._warn = warn or (lambda _m: None)
        self._log = log or (lambda _m: None)
        self._warned: set[str] = set()
        self._failed: set[str] = set()

    # ── plumbing ─────────────────────────────────────────────────────────────
    def which(self, name: str) -> str | None:
        return shutil.which(name)

    def run(self, args: list[str], timeout: float | None = None,
            cwd: Path | None = None) -> subprocess.CompletedProcess | None:
        try:
            return subprocess.run(args, capture_output=True, text=True, check=False,
                                  timeout=timeout or self.timeout,
                                  cwd=str(cwd) if cwd else None)
        except (OSError, subprocess.SubprocessError) as exc:
            self._log(f"{args[0]} failed: {exc}")
            return None

    def fetch(self, url: str, dest: Path) -> bool:
        """Download an http(s) asset into the cache. Never raises."""
        if not url.startswith(("https://", "http://")):
            return False
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            req = urllib.request.Request(url, headers={"User-Agent": "vantage-export"})
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:  # noqa: S310
                data = resp.read(25_000_000)
            if not data:
                return False
            dest.write_bytes(data)
            return True
        except Exception as exc:  # network errors are never fatal
            self._log(f"download failed for {url}: {exc}")
            return False

    def warn_once(self, key: str, message: str) -> None:
        if key not in self._warned:
            self._warned.add(key)
            self._warn(message)

    def available(self, key: str) -> str | None:
        """The binary for a helper, or ``None`` (with one warning) when it is absent."""
        binary = self.BINARIES[key]
        found = self.which(binary)
        if not found:
            self.warn_once(f"missing:{key}",
                           f"{binary} not found on PATH — using the built-in fallback")
        return found

    def _dir(self, *parts: str) -> Path:
        path = self.assets_dir.joinpath(*parts)
        path.mkdir(parents=True, exist_ok=True)
        return path

    # ── SVG → PNG ────────────────────────────────────────────────────────────
    def rasterize(self, svg: Path, png: Path, width: int = 512) -> bool:
        if png.exists() and png.stat().st_size:
            return True
        rsvg = self.which("rsvg-convert")
        if rsvg:
            done = self.run([rsvg, "-w", str(width), "-f", "png", "-o", str(png), str(svg)])
            if done and done.returncode == 0 and png.exists():
                return True
        magick = self.which("magick")
        if magick:
            done = self.run([magick, "-background", "none", "-density", "300", str(svg),
                             "-resize", f"{width}x", str(png)])
            if done and done.returncode == 0 and png.exists():
                return True
        self.warn_once("missing:rasterizer",
                       "no SVG rasterizer (rsvg-convert or ImageMagick) — icons and logos in "
                       "the .pptx/.docx use built-in shapes")
        return False

    # ── icons ────────────────────────────────────────────────────────────────
    def icon_svg(self, name: str) -> str | None:
        """An icon as SVG text drawn in ``currentColor``, or ``None``."""
        if not self.cfg.icons or not name:
            return None
        cache = self._dir("icons") / f"{_slug(name)}.svg"
        if cache.exists():
            text = cache.read_text(encoding="utf8")
            return text or None
        if f"icon:{name}" in self._failed:
            return None
        binary = self.available("icons")
        if not binary:
            return None
        text = self._iconify(binary, name, cache) or self._nerd(binary, name, cache)
        if not text:
            self._failed.add(f"icon:{name}")
            cache.write_text("", encoding="utf8")   # remember the miss; avoid re-querying
            return None
        cache.write_text(text, encoding="utf8")
        return text

    def _iconify(self, binary: str, name: str, cache: Path) -> str | None:
        tmp = self._dir("icons", ".tmp")
        done = self.run([binary, "iconify", "download", f"{ICON_FAMILY}:{name}", "-o", str(tmp)])
        if not done or done.returncode != 0:
            return None
        produced = sorted(tmp.glob(f"*{_slug(name)}*.svg"), key=lambda p: p.stat().st_mtime)
        if not produced:
            return None
        text = produced[-1].read_text(encoding="utf8")
        return text if "<svg" in text else None

    def _nerd(self, binary: str, name: str, cache: Path) -> str | None:
        done = self.run([binary, "nerd", "search", name.replace("-", " "), "--json", "-l", "8"])
        if not done or done.returncode != 0:
            return None
        try:
            hits = json.loads(done.stdout or "[]")
        except json.JSONDecodeError:
            return None
        hits = sorted((h for h in hits if isinstance(h, dict) and h.get("class")),
                      key=lambda h: h.get("set") != "md")
        if not hits:
            return None
        tmp = self._dir("icons", ".tmp")
        out = tmp / f"nerd-{_slug(name)}.svg"
        done = self.run([binary, "nerd", "download", str(hits[0]["class"]), "-o", str(out)])
        if not done or done.returncode != 0 or not out.exists():
            return None
        text = out.read_text(encoding="utf8")
        return text if "<svg" in text else None

    def icon_png(self, name: str, color: str, size: int = 256) -> Path | None:
        svg = self.icon_svg(name)
        if not svg:
            return None
        color = "#" + color.lstrip("#")
        tinted = recolor_svg(svg, color)
        base = self._dir("icons") / f"{_slug(name)}-{color.lstrip('#').lower()}"
        svg_path = base.with_suffix(".svg")
        svg_path.write_text(tinted, encoding="utf8")
        png = base.with_suffix(".png")
        return png if self.rasterize(svg_path, png, size) else None

    # ── stock imagery ────────────────────────────────────────────────────────
    def stock_image(self, query: str, max_width: int = 1920) -> Path | None:
        if not self.cfg.stock_images or not query.strip():
            return None
        folder = self._dir("stock")
        cache = folder / f"{_digest(query)}.jpg"
        if cache.exists() and cache.stat().st_size:
            return cache
        if f"stock:{query}" in self._failed:
            return None
        binary = self.available("stock")
        if not binary:
            return None
        done = self.run([binary, "--json", "-n", "1", query])
        url = None
        if done and done.returncode == 0:
            try:
                hits = json.loads(done.stdout or "[]")
                if isinstance(hits, dict):          # `-n 1` prints one object, not a list
                    hits = [hits]
                if isinstance(hits, list) and hits and isinstance(hits[0], dict):
                    url = hits[0].get("cdn_url") or hits[0].get("url")
            except json.JSONDecodeError:
                url = None
        raw = folder / f"{_digest(query)}.raw"
        if not url or not self.fetch(str(url), raw):
            self._failed.add(f"stock:{query}")
            self.warn_once("stock:fetch", "get-stock returned no usable image for at least one "
                                          "query — those slides use the plain layout")
            return None
        if not _downscale(raw, cache, max_width):
            shutil.move(str(raw), str(cache))
        raw.unlink(missing_ok=True)
        return cache

    # ── brand ────────────────────────────────────────────────────────────────
    def brand(self, domain: str) -> BrandAssets | None:
        if not self.cfg.brand or not domain:
            return None
        folder = self._dir("brand", _slug(domain))
        record = folder / "brand.json"
        data: dict[str, Any] | None = None
        if record.exists():
            try:
                data = json.loads(record.read_text(encoding="utf8"))
            except json.JSONDecodeError:
                data = None
        if data is None:
            binary = self.available("brand")
            if not binary:
                return None
            # --no-llm keeps the call bounded and cheap; providers alone give logo + palette.
            done = self.run([binary, domain, "--json", "--quiet", "--no-llm"])
            if not done or done.returncode != 0:
                self.warn_once(f"brand:{domain}", f"get-brand could not resolve {domain}")
                return None
            try:
                data = json.loads(done.stdout or "{}")
            except json.JSONDecodeError:
                self.warn_once(f"brand:{domain}", f"get-brand returned invalid JSON for {domain}")
                return None
            record.write_text(json.dumps(data, indent=2), encoding="utf8")
        brand = data.get("brand", data) if isinstance(data, dict) else {}
        assets = BrandAssets(
            domain=domain,
            name=brand.get("name"),
            colors=[c for c in brand.get("colors") or [] if isinstance(c, dict)],
            fonts=[f for f in brand.get("fonts") or [] if isinstance(f, dict)],
        )
        assets.logo_png = self._logo(folder, brand, "light")
        assets.logo_png_dark = self._logo(folder, brand, "dark") or assets.logo_png
        svg = folder / "logo-light.svg"
        assets.logo_svg = svg.read_text(encoding="utf8") if svg.exists() else None
        return assets

    def _logo(self, folder: Path, brand: dict, theme: str) -> Path | None:
        """A PNG logo suitable for a ``theme`` ("light"/"dark") background."""
        png = folder / f"logo-{theme}.png"
        if png.exists() and png.stat().st_size:
            return png
        candidates: list[tuple[int, str, str]] = []
        for logo in brand.get("logos") or []:
            if not isinstance(logo, dict):
                continue
            kind = str(logo.get("type") or "")
            rank = {"logo": 0, "symbol": 2, "icon": 3}.get(kind, 4)
            # get-brand (Brandfetch) names a logo by its *own* tone: a "light" logo is light
            # artwork for dark backgrounds. So a light background wants the "dark" variant.
            wanted = "dark" if theme == "light" else "light"
            if logo.get("theme") and logo.get("theme") != wanted:
                rank += 5
            for fmt in logo.get("formats") or []:
                if isinstance(fmt, dict) and fmt.get("src"):
                    candidates.append((rank, str(fmt.get("format") or ""), str(fmt["src"])))
        if not candidates and brand.get("logo"):
            candidates.append((5, "svg" if ".svg" in str(brand["logo"]) else "png",
                               str(brand["logo"])))
        for _rank, fmt, src in sorted(candidates, key=lambda c: (c[0], c[1] != "png")):
            if fmt == "svg":
                svg = folder / f"logo-{theme}.svg"
                if self.fetch(src, svg) and self.rasterize(svg, png, 800):
                    return png
            elif fmt in {"png", "jpeg", "jpg", "webp"}:
                raw = folder / f"logo-{theme}.{fmt}"
                if self.fetch(src, raw):
                    if fmt == "png":
                        return raw if raw == png else _copy(raw, png)
                    if _to_png(raw, png):
                        return png
        return None

    # ── illustrations (Napkin; spends credits — opt-in) ──────────────────────
    def illustration(self, text: str, name: str) -> Path | None:
        if self.cfg.illustrations != "napkin" or not text.strip():
            return None
        folder = self._dir("illustrations")
        cache = folder / f"{_slug(name)}-{_digest(text)}.png"
        if cache.exists():
            return cache
        binary = self.available("napkin")
        if not binary:
            return None
        content = folder / f"{_slug(name)}.txt"
        content.write_text(text, encoding="utf8")
        done = self.run([binary, "generate", "-f", str(content), "--format", "png", "-n", "1",
                         "-o", str(folder), "--filename-prefix", cache.stem, "--json",
                         "--max-wait", str(int(self.timeout))], timeout=self.timeout + 15)
        if not done or done.returncode != 0:
            self.warn_once("napkin", "napkin did not produce an illustration")
            return None
        produced = sorted(folder.glob(f"{cache.stem}*.png"))
        if not produced:
            return None
        if produced[0] != cache:
            produced[0].replace(cache)
        return cache


def recolor_svg(svg: str, color: str) -> str:
    """Bind ``currentColor`` (and a missing fill) to a concrete colour for rasterizing."""
    out = svg.replace("currentColor", color)
    if "fill=" not in out and "stroke=" not in out:
        out = out.replace("<svg", f'<svg fill="{color}"', 1)
    return out


def _downscale(src: Path, dest: Path, max_width: int) -> bool:
    try:
        from PIL import Image
    except ImportError:
        return False
    try:
        with Image.open(src) as img:
            img = img.convert("RGB")
            if img.width > max_width:
                img = img.resize((max_width, round(img.height * max_width / img.width)))
            img.save(dest, "JPEG", quality=80, optimize=True, progressive=True)
        return True
    except Exception:
        return False


def _to_png(src: Path, dest: Path) -> bool:
    try:
        from PIL import Image

        with Image.open(src) as img:
            img.save(dest, "PNG")
        return True
    except Exception:
        return False


def _copy(src: Path, dest: Path) -> Path:
    shutil.copyfile(src, dest)
    return dest
