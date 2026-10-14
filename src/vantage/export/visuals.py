"""Figure-spec blocks → diagrams; plus the SVG hygiene every inlined image goes through.

Engines, tried in order for ``helpers.diagrams = "auto"``:

1. ``dgm`` — writes a semantic spec, lets the tool lay it out (headless SVG/PNG preview);
2. ``drawio`` — an mxGraph file laid out here, exported by the draw.io CLI;
3. ``mmdc`` — a Mermaid flowchart rendered by mermaid-cli;
4. built-in — a layered layout drawn with matplotlib. Always available.

Positioned figures (nodes with ``x``/``y`` — quadrants, matrices) are drawn by the built-in
quadrant renderer whatever the setting, because their position *is* the data. ``"none"`` draws
nothing and the renderers print the figure's nodes and edges as a table instead — the content is
never lost.
"""

from __future__ import annotations

import hashlib
import html
import json
import re
from dataclasses import dataclass
from pathlib import Path

from .helpers import Toolbox
from .models import FigureSpec, Table
from .render.charts import _mpl, strip_prolog
from .richtext import plain
from .theme import Theme


@dataclass
class FigureArt:
    svg: str | None
    png: Path | None
    engine: str


class FigureRenderer:
    def __init__(self, theme: Theme, tools: Toolbox, cache_dir: Path, mode: str = "auto") -> None:
        self.theme = theme
        self.tools = tools
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.mode = mode
        self._memo: dict[str, FigureArt | None] = {}
        self.engines: dict[str, int] = {}

    def render(self, spec: FigureSpec) -> FigureArt | None:
        key = hashlib.sha256((spec.model_dump_json() + self.mode
                              + self.theme.palette.accent).encode()).hexdigest()[:16]
        if key in self._memo:
            return self._memo[key]
        art = self._render(spec, key)
        self._memo[key] = art
        if art:
            self.engines[art.engine] = self.engines.get(art.engine, 0) + 1
        return art

    def _render(self, spec: FigureSpec, key: str) -> FigureArt | None:
        if self.mode == "none":
            return None
        if spec.positioned:
            return self._builtin_quadrant(spec, key)
        if not spec.nodes:
            return None
        order = {"auto": ["dgm", "drawio", "mermaid", "builtin"],
                 "dgm": ["dgm", "builtin"], "drawio": ["drawio", "builtin"],
                 "mermaid": ["mermaid", "builtin"]}.get(self.mode, ["builtin"])
        for engine in order:
            if engine == "builtin":
                return self._builtin_graph(spec, key)
            binary = self.tools.which(Toolbox.BINARIES[engine])
            if not binary:
                if self.mode == engine:
                    self.tools.available(engine)   # one warning for an explicit choice
                continue
            art = getattr(self, f"_{engine}")(binary, spec, key)
            if art is not None:
                return art
        return self._builtin_graph(spec, key)

    # ── dgm ──────────────────────────────────────────────────────────────────
    def _dgm(self, binary: str, spec: FigureSpec, key: str) -> FigureArt | None:
        folder = self.cache_dir / f"fig-{key}"
        folder.mkdir(parents=True, exist_ok=True)
        ids = _safe_ids(spec)
        groups = {}
        for n in spec.nodes:
            g = str(n.get("group") or n.get("category") or "").strip()
            if g and g not in groups:
                groups[g] = f"g{len(groups)}"
        use_groups = 1 < len(groups) <= 8
        doc = {
            "apiVersion": "dgm/v1",
            "kind": "Diagram",
            "metadata": {
                "title": plain(spec.title)[:90],
                "notation": "flow",
                "theme": "corporate-blue",
                "direction": _direction(spec),
            },
            "groups": [{"id": gid, "label": label[:40], "role": "zone"}
                       for label, gid in groups.items()] if use_groups else [],
            "nodes": [
                {k: v for k, v in {
                    "id": ids[str(n["id"])], "label": _label(n), "role": "process",
                    "group": groups.get(str(n.get("group") or n.get("category") or "").strip())
                    if use_groups else None,
                }.items() if v}
                for n in spec.nodes
            ],
            "edges": [
                {k: v for k, v in {"from": ids.get(str(e["from"])), "to": ids.get(str(e["to"])),
                                   "label": plain(str(e.get("label") or ""))[:40]}.items() if v}
                for e in spec.edges if str(e["from"]) in ids and str(e["to"]) in ids
            ],
        }
        if not doc["groups"]:
            doc.pop("groups")
        spec_path = folder / "figure.yaml"
        spec_path.write_text(json.dumps(doc, indent=2), encoding="utf8")   # JSON is valid YAML
        svg_path, png_path = folder / "figure.svg", folder / "figure.png"
        done = self.tools.run([binary, "preview", str(spec_path), "-o", str(svg_path)])
        if not done or done.returncode != 0 or not svg_path.exists():
            return None
        self.tools.run([binary, "preview", str(spec_path), "-o", str(png_path), "--scale", "2"])
        png = png_path if png_path.exists() else None
        if png is None and self.tools.rasterize(svg_path, png_path, 1800):
            png = png_path
        return FigureArt(svg_path.read_text(encoding="utf8"), png, "dgm")

    # ── draw.io ──────────────────────────────────────────────────────────────
    def _drawio(self, binary: str, spec: FigureSpec, key: str) -> FigureArt | None:
        folder = self.cache_dir / f"fig-{key}"
        folder.mkdir(parents=True, exist_ok=True)
        src = folder / "figure.drawio"
        src.write_text(_mxfile(spec, self.theme), encoding="utf8")
        svg_path, png_path = folder / "figure-drawio.svg", folder / "figure-drawio.png"
        timeout = max(self.tools.timeout, 30)
        done = self.tools.run([binary, "-x", "-f", "svg", "-o", str(svg_path), str(src)],
                              timeout=timeout)
        if not done or done.returncode != 0 or not svg_path.exists():
            return None
        self.tools.run([binary, "-x", "-f", "png", "-s", "2", "-o", str(png_path), str(src)],
                       timeout=timeout)
        return FigureArt(svg_path.read_text(encoding="utf8"),
                         png_path if png_path.exists() else None, "drawio")

    # ── mermaid ──────────────────────────────────────────────────────────────
    def _mermaid(self, binary: str, spec: FigureSpec, key: str) -> FigureArt | None:
        folder = self.cache_dir / f"fig-{key}"
        folder.mkdir(parents=True, exist_ok=True)
        src = folder / "figure.mmd"
        src.write_text(mermaid_source(spec), encoding="utf8")
        svg_path, png_path = folder / "figure-mmd.svg", folder / "figure-mmd.png"
        timeout = max(self.tools.timeout, 45)
        done = self.tools.run([binary, "-i", str(src), "-o", str(svg_path), "-b", "white"],
                              timeout=timeout)
        if not done or done.returncode != 0 or not svg_path.exists():
            return None
        self.tools.run([binary, "-i", str(src), "-o", str(png_path), "-b", "white", "-s", "2"],
                       timeout=timeout)
        return FigureArt(svg_path.read_text(encoding="utf8"),
                         png_path if png_path.exists() else None, "mermaid")

    # ── built-in (matplotlib) ────────────────────────────────────────────────
    def _save(self, fig, key: str, engine: str) -> FigureArt:
        import io

        plt = _mpl()
        png = self.cache_dir / f"fig-{key}.png"
        fig.savefig(png, dpi=180, bbox_inches="tight", pad_inches=0.1)
        buffer = io.StringIO()
        with plt.rc_context({"svg.fonttype": "none"}):
            fig.savefig(buffer, format="svg", bbox_inches="tight", pad_inches=0.1)
        plt.close(fig)
        return FigureArt(strip_prolog(buffer.getvalue()), png, engine)

    def _builtin_graph(self, spec: FigureSpec, key: str) -> FigureArt:
        from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

        plt = _mpl()
        p = self.theme.palette
        positions, ranks, width = layered_layout(spec)
        cols = max(ranks) + 1 if ranks else 1
        horizontal = _direction(spec) == "right"
        box_w, box_h = 2.2, 0.8
        gap_x, gap_y = 0.9, 0.45
        if horizontal:
            fig_w = min(14.0, max(6.0, cols * (box_w + gap_x)))
            fig_h = min(10.0, max(2.5, width * (box_h + gap_y) + 0.8))
        else:
            fig_w = min(14.0, max(6.0, width * (box_w + gap_x)))
            fig_h = min(12.0, max(2.5, cols * (box_h + gap_y * 2) + 0.8))
        fig, ax = plt.subplots(figsize=(fig_w, fig_h))
        ax.set_axis_off()
        centres: dict[str, tuple[float, float]] = {}
        for nid, (rank, slot) in positions.items():
            if horizontal:
                x, y = rank * (box_w + gap_x), -slot * (box_h + gap_y)
            else:
                x, y = slot * (box_w + gap_x), -rank * (box_h + gap_y * 2)
            centres[nid] = (x, y)
        size = 8 if len(spec.nodes) <= 14 else 6.5
        for n in spec.nodes:
            nid = str(n["id"])
            if nid not in centres:
                continue
            x, y = centres[nid]
            ax.add_patch(FancyBboxPatch((x - box_w / 2, y - box_h / 2), box_w, box_h,
                                        boxstyle="round,pad=0.02,rounding_size=0.12",
                                        facecolor=f"#{p.accent_tint}",
                                        edgecolor=f"#{p.accent}", linewidth=1.1))
            ax.text(x, y, _wrap(_label(n), 26, 3), ha="center", va="center", fontsize=size,
                    color=f"#{p.ink}")
        for e in spec.edges:
            a, b = centres.get(str(e["from"])), centres.get(str(e["to"]))
            if not a or not b:
                continue
            ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=10,
                                         color=f"#{p.ink_faint}", linewidth=0.9,
                                         shrinkA=28, shrinkB=28,
                                         connectionstyle="arc3,rad=0.06"))
            label = plain(str(e.get("label") or ""))
            if label:
                ax.text((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, _wrap(label, 24, 2), ha="center",
                        va="center", fontsize=size - 1.5, color=f"#{p.ink_soft}",
                        bbox={"facecolor": "white", "edgecolor": "none", "pad": 1})
        xs = [c[0] for c in centres.values()] or [0]
        ys = [c[1] for c in centres.values()] or [0]
        ax.set_xlim(min(xs) - box_w, max(xs) + box_w)
        ax.set_ylim(min(ys) - box_h * 1.5, max(ys) + box_h * 1.5)
        ax.set_title(_wrap(plain(spec.title), 80, 2), loc="left", fontsize=11,
                     color=f"#{p.ink}")
        return self._save(fig, key, "builtin")

    def _builtin_quadrant(self, spec: FigureSpec, key: str) -> FigureArt:
        plt = _mpl()
        p = self.theme.palette
        fig, ax = plt.subplots(figsize=(7.5, 5.2))
        xs, ys = [], []
        for n in spec.nodes:
            try:
                x, y = float(n["x"]), float(n["y"])
            except (TypeError, ValueError):
                continue
            xs.append(x)
            ys.append(y)
            ax.scatter([x], [y], s=46, color=f"#{p.accent}", zorder=3)
            ax.annotate(_wrap(_label(n), 28, 2), (x, y), textcoords="offset points",
                        xytext=(6, 4), fontsize=7.5, color=f"#{p.ink_soft}")
        if xs:
            mid_x = (min(xs) + max(xs)) / 2 if max(xs) != min(xs) else xs[0]
            mid_y = (min(ys) + max(ys)) / 2 if max(ys) != min(ys) else ys[0]
            ax.axvline(mid_x, color=f"#{p.rule}", linewidth=1)
            ax.axhline(mid_y, color=f"#{p.rule}", linewidth=1)
        x_label, y_label = _axis(spec.axes, "x"), _axis(spec.axes, "y")
        if x_label:
            ax.set_xlabel(x_label, color=f"#{p.ink_soft}")
        if y_label:
            ax.set_ylabel(y_label, color=f"#{p.ink_soft}")
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        ax.set_title(_wrap(plain(spec.title), 80, 2), loc="left", fontsize=11,
                     color=f"#{p.ink}")
        return self._save(fig, key, "builtin")


# ── layout + sources ─────────────────────────────────────────────────────────


def _safe_ids(spec: FigureSpec) -> dict[str, str]:
    out: dict[str, str] = {}
    for i, n in enumerate(spec.nodes):
        base = re.sub(r"[^a-zA-Z0-9_]", "_", str(n["id"]))[:30] or f"n{i}"
        if not base[0].isalpha():
            base = f"n_{base}"
        while base in out.values():
            base = f"{base}_{i}"
        out[str(n["id"])] = base
    return out


def _label(node: dict) -> str:
    return plain(str(node.get("label") or node.get("id") or ""))[:80]


def _direction(spec: FigureSpec) -> str:
    if spec.direction:
        d = spec.direction.lower()
        if d in {"lr", "right", "horizontal", "left-right"}:
            return "right"
        if d in {"td", "tb", "down", "vertical", "top-down"}:
            return "down"
    if any(k in spec.type for k in ("org", "hierarchy", "tree", "taxonomy")):
        return "down"
    return "right" if len(spec.nodes) <= 8 else "down"


def _axis(axes: dict, name: str) -> str:
    value = axes.get(name) if isinstance(axes, dict) else None
    if isinstance(value, dict):
        value = value.get("label") or value.get("name") or ""
    return plain(str(value or ""))


def _wrap(text: str, width: int, lines: int) -> str:
    words, out, current = text.split(), [], ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) > width and current:
            out.append(current)
            current = word
        else:
            current = candidate
    if current:
        out.append(current)
    return "\n".join(out[:lines]) + ("…" if len(out) > lines else "")


def layered_layout(spec: FigureSpec) -> tuple[dict[str, tuple[int, int]], list[int], int]:
    """Longest-path layering (cycles broken by DFS order). Returns (id → (rank, slot))."""
    ids = [str(n["id"]) for n in spec.nodes]
    known = set(ids)
    succ: dict[str, list[str]] = {i: [] for i in ids}
    for e in spec.edges:
        a, b = str(e["from"]), str(e["to"])
        if a in known and b in known and a != b:
            succ[a].append(b)
    # Break cycles: keep only edges that point forward in a DFS finishing order.
    state: dict[str, int] = {}
    order: list[str] = []

    def dfs(node: str) -> None:
        state[node] = 1
        for nxt in succ[node]:
            if state.get(nxt, 0) == 0:
                dfs(nxt)
        state[node] = 2
        order.append(node)

    for node in ids:
        if state.get(node, 0) == 0:
            dfs(node)
    position = {node: i for i, node in enumerate(reversed(order))}
    rank = dict.fromkeys(ids, 0)
    for node in sorted(ids, key=lambda n: position[n]):
        for nxt in succ[node]:
            if position[nxt] > position[node]:
                rank[nxt] = max(rank[nxt], rank[node] + 1)
    # Cap the depth so a long chain wraps rather than producing a 40-column strip.
    max_rank = max(rank.values(), default=0)
    if max_rank > 7:
        rank = {k: v % 8 for k, v in rank.items()}
    slots: dict[int, int] = {}
    positions: dict[str, tuple[int, int]] = {}
    for node in ids:
        r = rank[node]
        positions[node] = (r, slots.get(r, 0))
        slots[r] = slots.get(r, 0) + 1
    return positions, list(rank.values()), max(slots.values(), default=1)


def mermaid_source(spec: FigureSpec) -> str:
    ids = _safe_ids(spec)
    direction = "LR" if _direction(spec) == "right" else "TD"
    lines = [f"flowchart {direction}"]
    for n in spec.nodes:
        label = _label(n).replace('"', "'")
        lines.append(f'  {ids[str(n["id"])]}["{label}"]')
    for e in spec.edges:
        a, b = ids.get(str(e["from"])), ids.get(str(e["to"]))
        if not a or not b:
            continue
        label = plain(str(e.get("label") or "")).replace('"', "'").replace("|", "/")[:40]
        lines.append(f'  {a} -->|"{label}"| {b}' if label else f"  {a} --> {b}")
    return "\n".join(lines) + "\n"


def _mxfile(spec: FigureSpec, theme: Theme) -> str:
    positions, _ranks, _w = layered_layout(spec)
    horizontal = _direction(spec) == "right"
    p = theme.palette
    cells = ['<mxCell id="0"/>', '<mxCell id="1" parent="0"/>']
    ids = _safe_ids(spec)
    for n in spec.nodes:
        nid = str(n["id"])
        rank, slot = positions[nid]
        x, y = (rank * 240, slot * 110) if horizontal else (slot * 240, rank * 130)
        style = (f"rounded=1;whiteSpace=wrap;html=1;fillColor=#{p.accent_tint};"
                 f"strokeColor=#{p.accent};fontColor=#{p.ink};fontSize=12;")
        cells.append(
            f'<mxCell id="{ids[nid]}" value="{html.escape(_label(n), quote=True)}" '
            f'style="{style}" vertex="1" parent="1">'
            f'<mxGeometry x="{x}" y="{y}" width="190" height="70" as="geometry"/></mxCell>')
    for i, e in enumerate(spec.edges):
        a, b = ids.get(str(e["from"])), ids.get(str(e["to"]))
        if not a or not b:
            continue
        label = html.escape(plain(str(e.get("label") or ""))[:40], quote=True)
        cells.append(
            f'<mxCell id="e{i}" value="{label}" style="edgeStyle=orthogonalEdgeStyle;'
            f'rounded=1;html=1;strokeColor=#{p.ink_faint};fontSize=10;" edge="1" parent="1" '
            f'source="{a}" target="{b}"><mxGeometry relative="1" as="geometry"/></mxCell>')
    body = "".join(cells)
    return (f'<mxfile><diagram name="{html.escape(plain(spec.title)[:60], quote=True)}">'
            f"<mxGraphModel><root>{body}</root></mxGraphModel></diagram></mxfile>")


def figure_table(spec: FigureSpec) -> Table | None:
    """The figure's content as a table — used when no drawing is produced, and for item lists."""
    if spec.items:
        keys: list[str] = []
        for item in spec.items:
            for k in item:
                if k not in keys and not isinstance(item[k], dict | list):
                    keys.append(k)
        keys = keys[:6]
        return Table(header=[k.replace("_", " ").capitalize() for k in keys],
                     rows=[[str(item.get(k, "")) for k in keys] for item in spec.items],
                     caption=spec.caption())
    if spec.nodes:
        labels = {str(n["id"]): _label(n) for n in spec.nodes}
        if spec.edges:
            rows = [[labels.get(str(e["from"]), str(e["from"])),
                     plain(str(e.get("label") or "")), labels.get(str(e["to"]), str(e["to"]))]
                    for e in spec.edges]
            return Table(header=["From", "Relationship", "To"], rows=rows,
                         caption=spec.caption())
        extra = [k for k in ("group", "category", "x", "y", "status") if
                 any(k in n for n in spec.nodes)][:3]
        return Table(header=["Element", *[k.capitalize() for k in extra]],
                     rows=[[_label(n), *[str(n.get(k, "")) for k in extra]] for n in spec.nodes],
                     caption=spec.caption())
    return None


# ── SVG hygiene for the single-file HTML ─────────────────────────────────────

_ID_RE = re.compile(r'\bid="([^"]+)"')
_EXTERNAL_RE = re.compile(r'\s(?:xlink:)?href="(?!#|data:)[^"]*"')


def sanitize_svg(svg: str, prefix: str) -> str:
    """Make an SVG safe to inline next to others: prefixed ids, no scripts, nothing external."""
    svg = strip_prolog(svg)
    svg = re.sub(r"<script\b.*?</script>", "", svg, flags=re.S | re.I)
    svg = re.sub(r"\son[a-z]+=\"[^\"]*\"", "", svg, flags=re.I)
    svg = re.sub(r"@import[^;]+;", "", svg)
    svg = re.sub(r"url\((['\"]?)https?://[^)]*\)", "none", svg)
    svg = _EXTERNAL_RE.sub("", svg)
    ids = set(_ID_RE.findall(svg))
    if ids:
        def fix_id(m: re.Match) -> str:
            return f'id="{prefix}-{m.group(1)}"'

        svg = _ID_RE.sub(fix_id, svg)
        for ident in sorted(ids, key=len, reverse=True):
            esc = re.escape(ident)
            svg = re.sub(rf"url\(#{esc}\)", f"url(#{prefix}-{ident})", svg)
            svg = re.sub(rf'href="#{esc}"', f'href="#{prefix}-{ident}"', svg)
    # Let the SVG scale with its container (only safe when it declares a viewBox).
    head = re.match(r"<svg\b[^>]*>", svg)
    if head and "viewBox" in head.group(0):
        tag = re.sub(r'\s(?:width|height)="[^"]*"', "", head.group(0))
        svg = tag + svg[head.end():]
    return svg
