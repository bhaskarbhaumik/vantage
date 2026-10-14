"""Charts from the dossier's chart-data blocks, drawn to the export theme.

Follows the dataviz rules: pick the form from the question, not the data type; the accent carries
the series that matters and secondaries only differentiate; label directly instead of forcing a
legend round-trip; never encode meaning in colour alone; never invent a point — a ``null`` in the
dossier is a gap in the line, not a zero.

Every chart renders to PNG (for .pptx/.docx) and to SVG text (inlined into the HTML), cached by
content hash so a spec shared by the deck, the whitepaper and the microsite is drawn once.
``helpers.charts = "plotly"`` swaps the HTML rendering for an interactive Plotly figure (with
plotly.js inlined once, so the file still works offline); the Office formats keep matplotlib unless
Kaleido is installed.
"""

from __future__ import annotations

import hashlib
import io
import json
import math
import re
from collections.abc import Callable
from pathlib import Path

from ..models import ChartSpec
from ..theme import Theme

DPI = 200


def _mpl():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    return plt


class ChartRenderer:
    def __init__(self, theme: Theme, cache_dir: Path, engine: str = "matplotlib",
                 warn: Callable[[str], None] | None = None) -> None:
        self.theme = theme
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.engine = engine
        self._warn = warn or (lambda _m: None)
        self._plotly_js_emitted = False
        self.drawn = 0

    # ── public ───────────────────────────────────────────────────────────────
    def png(self, spec: ChartSpec, width_in: float = 6.0,
            height_in: float | None = None) -> Path | None:
        if not _drawable(spec):
            return None
        out = self.cache_dir / f"chart-{self._key(spec, width_in, height_in)}.png"
        if out.exists():
            return out
        if self.engine == "plotly" and self._plotly_png(spec, out, width_in, height_in):
            return out
        fig = self._figure(spec, width_in, height_in)
        if fig is None:
            return None
        fig.savefig(out, dpi=DPI, bbox_inches="tight", pad_inches=0.08)
        _mpl().close(fig)
        self.drawn += 1
        return out

    def svg(self, spec: ChartSpec, width_in: float = 7.5,
            height_in: float | None = None) -> str | None:
        """Inline SVG markup (no XML prolog), or ``None`` when there is nothing to draw."""
        if not _drawable(spec):
            return None
        out = self.cache_dir / f"chart-{self._key(spec, width_in, height_in)}.svg"
        if out.exists():
            return out.read_text(encoding="utf8")
        fig = self._figure(spec, width_in, height_in)
        if fig is None:
            return None
        buffer = io.StringIO()
        plt = _mpl()
        with plt.rc_context({"svg.fonttype": "none"}):
            fig.savefig(buffer, format="svg", bbox_inches="tight", pad_inches=0.08)
        plt.close(fig)
        text = strip_prolog(buffer.getvalue())
        out.write_text(text, encoding="utf8")
        self.drawn += 1
        return text

    def html(self, spec: ChartSpec, width_in: float = 7.5,
             height_in: float | None = None) -> str | None:
        """What the HTML embeds: inline SVG, or an interactive Plotly div."""
        if self.engine == "plotly":
            fragment = self._plotly_html(spec)
            if fragment:
                return fragment
        return self.svg(spec, width_in, height_in)

    # ── matplotlib ───────────────────────────────────────────────────────────
    def _key(self, spec: ChartSpec, width_in: float, height_in: float | None) -> str:
        payload = json.dumps([spec.model_dump(), round(width_in, 3), height_in,
                              self.theme.chart_series, self.theme.type.chart],
                             sort_keys=True, default=str)
        return hashlib.sha256(payload.encode()).hexdigest()[:16]

    def _style(self) -> dict:
        p = self.theme.palette
        return {
            "font.family": "sans-serif",
            "font.sans-serif": list(self.theme.type.chart),
            "font.size": 9,
            "axes.edgecolor": f"#{p.rule}",
            "axes.labelcolor": f"#{p.ink_soft}",
            "axes.titlecolor": f"#{p.ink}",
            "axes.titlesize": 11,
            "axes.titleweight": "normal",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "text.color": f"#{p.ink}",
            "xtick.color": f"#{p.ink_faint}",
            "ytick.color": f"#{p.ink_faint}",
            "xtick.labelsize": 8.5,
            "ytick.labelsize": 8.5,
            "grid.color": f"#{p.rule}",
            "grid.linewidth": 0.6,
            "figure.facecolor": "white",
            "savefig.facecolor": "white",
            "legend.frameon": False,
            "legend.fontsize": 8.5,
            "axes.unicode_minus": True,
        }

    def _figure(self, spec: ChartSpec, width_in: float, height_in: float | None):
        plt = _mpl()
        from matplotlib.ticker import FuncFormatter

        series = _series_values(spec)
        height_in = height_in or max(2.4, min(width_in * 0.55, 4.4))
        colours = self.theme.chart_series
        categories = [str(c) for c in spec.categories]
        form = spec.form
        # Long category names belong on a horizontal axis; rotated labels collide and clip.
        long_labels = max((len(c) for c in categories), default=0) > 14
        if form in {"bar", "grouped-bar"} and long_labels:
            form = "hbar"
        if form == "hbar":
            height_in = max(height_in, min(0.42 * len(categories) + 1.0, 6.5))

        with plt.rc_context(self._style()):
            fig, ax = plt.subplots(figsize=(width_in, height_in))
            if form == "combo":
                self._combo(ax, categories, series, colours, spec)
            elif form in {"bar", "grouped-bar", "stacked-bar"}:
                _bars(ax, categories, series, colours, stacked=form == "stacked-bar")
            elif form == "hbar":
                self._hbars(ax, categories, series, colours)
            elif form == "line":
                _lines(ax, categories, series, colours)
            elif form == "scatter":
                self._scatter(ax, categories, series, colours)
            elif form == "donut":
                _donut(ax, categories, series, colours)
            elif form == "waterfall":
                self._waterfall(ax, categories, series, colours)
            else:
                _bars(ax, categories, series, colours)

            if form not in {"donut", "combo"}:
                value_axis = ax.xaxis if form == "hbar" else ax.yaxis
                value_axis.set_major_formatter(FuncFormatter(_fmt(spec.unit)))
                ax.grid(axis="x" if form == "hbar" else "y", alpha=0.7)
                ax.set_axisbelow(True)
                if spec.y_label or (spec.unit and form != "hbar"):
                    ax.set_ylabel(spec.y_label or spec.unit or "")
                elif spec.unit and form == "hbar":
                    ax.set_xlabel(spec.unit)

            ax.set_title(_wrap(spec.title, 70, lines=2), loc="left", pad=12)
            if len(series) > 1 and form not in {"donut", "scatter", "combo", "waterfall"}:
                ax.legend(loc="upper left", bbox_to_anchor=(0, -0.14),
                          ncol=min(len(series), 4))
            fig.tight_layout()
        return fig

    def _combo(self, ax, categories, series, colours, spec) -> None:
        """Bar series on the left axis, line series on a right axis (absolute vs rate)."""
        import numpy as np
        from matplotlib.ticker import FuncFormatter

        kinds = {s["name"]: (s.get("kind") or "bar") for s in spec.series}
        bars = [(n, v) for n, v in series if kinds.get(n, "bar") != "line"]
        lines = [(n, v) for n, v in series if kinds.get(n, "bar") == "line"]
        if not bars:
            _lines(ax, categories, series, colours)
            return
        x = np.arange(len(categories))
        width = min(0.8 / max(len(bars), 1), 0.5)
        offset = -width * (len(bars) - 1) / 2
        handles, labels = [], []
        for i, (name, values) in enumerate(bars):
            h = ax.bar(x + offset + i * width, _pad(values, len(categories)), width, label=name,
                       color=f"#{colours[i % len(colours)]}")
            handles.append(h)
            labels.append(name)
        ax.set_xticks(x)
        ax.set_xticklabels([_wrap(c, 14) for c in categories])
        ax.yaxis.set_major_formatter(FuncFormatter(_fmt(spec.unit)))
        if spec.unit:
            ax.set_ylabel(spec.unit)
        ax.grid(axis="y", alpha=0.7)
        ax.set_axisbelow(True)
        if lines:
            right = ax.twinx()
            right.grid(False)
            right.spines["right"].set_visible(True)
            for j, (name, values) in enumerate(lines):
                vals = np.array(_pad(values, len(categories)), dtype=float)
                (h,) = right.plot(x, vals, marker="o", linewidth=2,
                                  color=f"#{colours[(len(bars) + j) % len(colours)]}", label=name)
                handles.append(h)
                labels.append(name)
            unit = "%" if spec.secondary_unit and "%" in spec.secondary_unit else None
            right.yaxis.set_major_formatter(FuncFormatter(_fmt(unit)))
            if spec.secondary_unit:
                right.set_ylabel(spec.secondary_unit)
        ax.legend(handles, labels, loc="upper left", bbox_to_anchor=(0, -0.14),
                  ncol=min(len(labels), 4))

    def _hbars(self, ax, categories, series, colours) -> None:
        """Horizontal bars, ranked, labelled at the bar end; a missing value says so."""
        p = self.theme.palette
        count = len(series)
        padded = [_pad(values, len(categories)) for _n, values in series]
        lead = padded[0]
        order = sorted(range(len(categories)),
                       key=lambda i: float("-inf") if math.isnan(lead[i]) else lead[i])
        labels = [_wrap(categories[i], 34) for i in order]
        positions = list(range(len(order)))
        height = 0.72 / count
        for index, (name, _v) in enumerate(series):
            values = [padded[index][i] for i in order]
            offset = ([p_ - 0.36 + height * (index + 0.5) for p_ in positions]
                      if count > 1 else positions)
            ax.barh(offset, [0 if math.isnan(v) else v for v in values],
                    height if count > 1 else 0.6,
                    color=f"#{colours[index % len(colours)]}", label=name)
            if count <= 2:
                for pos, value in zip(offset, values, strict=False):
                    text = " n/a" if math.isnan(value) else f" {_minus(f'{value:,.6g}')}"
                    ax.text(0 if math.isnan(value) else value, pos, text, va="center",
                            ha="left", fontsize=7.5, color=f"#{p.ink_soft}")
        ax.set_yticks(positions)
        ax.set_yticklabels(labels, fontsize=8)
        ax.set_ylim(-0.6, len(positions) - 0.4)

    def _scatter(self, ax, categories, series, colours) -> None:
        p = self.theme.palette
        if len(series) >= 2:
            (x_name, xs), (y_name, ys) = series[0], series[1]
            ax.scatter(_pad(xs, len(categories)), _pad(ys, len(categories)), s=48,
                       color=f"#{colours[0]}")
            ax.set_xlabel(x_name)
            ax.set_ylabel(y_name)
            for label, x, y in zip(categories, xs, ys, strict=False):
                if x is not None and y is not None and not (math.isnan(x) or math.isnan(y)):
                    ax.annotate(str(label), (x, y), textcoords="offset points", xytext=(6, 4),
                                fontsize=7.5, color=f"#{p.ink_soft}")
        else:
            _bars(ax, categories, series, colours)

    def _waterfall(self, ax, categories, series, colours) -> None:
        """First and last bars are totals; the ones between float as deltas."""
        p = self.theme.palette
        values = _pad(series[0][1], len(categories))
        running = 0.0
        for i, value in enumerate(values):
            if math.isnan(value):
                continue
            total = i in (0, len(values) - 1)
            if total:
                bottom, height, colour = 0.0, value, p.accent
                running = value
            else:
                bottom = running if value >= 0 else running + value
                height = abs(value)
                colour = p.green if value >= 0 else p.red
                running += value
            ax.bar(i, height, 0.6, bottom=bottom, color=f"#{colour}")
            label = _minus(f"{value:,.6g}") if total else (
                ("+" if value >= 0 else "−") + f"{abs(value):,.6g}")
            ax.text(i, bottom + height, label, ha="center", va="bottom", fontsize=7.5,
                    color=f"#{p.ink_soft}")
        ax.set_xticks(range(len(categories)))
        ax.set_xticklabels([_wrap(c, 12) for c in categories], fontsize=7.5)

    # ── plotly (optional) ────────────────────────────────────────────────────
    def _plotly_figure(self, spec: ChartSpec):
        try:
            import plotly.graph_objects as go
        except ImportError:
            self._warn("helpers.charts is 'plotly' but plotly is not installed — "
                       "using matplotlib (uv sync --extra export)")
            self.engine = "matplotlib"
            return None
        colours = [f"#{c}" for c in self.theme.chart_series]
        fig = go.Figure()
        kinds = {s["name"]: (s.get("kind") or "bar") for s in spec.series}
        for i, (name, values) in enumerate(_series_values(spec)):
            vals = [None if math.isnan(v) else v for v in _pad(values, len(spec.categories))]
            colour = colours[i % len(colours)]
            if spec.form == "line" or (spec.form == "combo" and kinds.get(name) == "line"):
                fig.add_trace(go.Scatter(x=spec.categories, y=vals, name=name,
                                         mode="lines+markers", line={"color": colour},
                                         yaxis="y2" if spec.form == "combo" else "y"))
            elif spec.form == "hbar":
                fig.add_trace(go.Bar(y=spec.categories, x=vals, name=name, orientation="h",
                                     marker_color=colour))
            elif spec.form == "donut":
                fig.add_trace(go.Pie(labels=spec.categories, values=vals, hole=0.45,
                                     marker={"colors": colours}))
            else:
                fig.add_trace(go.Bar(x=spec.categories, y=vals, name=name, marker_color=colour))
        layout: dict = {
            "title": {"text": spec.title, "x": 0},
            "barmode": "stack" if spec.form == "stacked-bar" else "group",
            "font": {"family": self.theme.type.body_css, "size": 12},
            "paper_bgcolor": "white", "plot_bgcolor": "white",
            "margin": {"l": 40, "r": 20, "t": 50, "b": 40},
        }
        if spec.form == "combo":
            layout["yaxis2"] = {"overlaying": "y", "side": "right",
                                "title": spec.secondary_unit or ""}
        fig.update_layout(**layout)
        return fig

    def _plotly_html(self, spec: ChartSpec) -> str | None:
        if not _drawable(spec):
            return None
        fig = self._plotly_figure(spec)
        if fig is None:
            return None
        include = "inline" if not self._plotly_js_emitted else False
        self._plotly_js_emitted = True
        return fig.to_html(full_html=False, include_plotlyjs=include,
                           config={"displaylogo": False, "responsive": True})

    def _plotly_png(self, spec: ChartSpec, out: Path, width_in: float,
                    height_in: float | None) -> bool:
        try:
            import kaleido  # noqa: F401
        except ImportError:
            return False
        fig = self._plotly_figure(spec)
        if fig is None:
            return False
        try:
            fig.write_image(str(out), width=int(width_in * 120),
                            height=int((height_in or width_in * 0.55) * 120), scale=2)
            return out.exists()
        except Exception:
            return False


# ── helpers ──────────────────────────────────────────────────────────────────


def _drawable(spec: ChartSpec) -> bool:
    return bool(spec.categories) and any(
        v is not None for s in spec.series for v in (s.get("values") or []))


def strip_prolog(svg: str) -> str:
    svg = re.sub(r"<\?xml[^>]*\?>", "", svg)
    svg = re.sub(r"<!DOCTYPE[^>]*>", "", svg, flags=re.S)
    svg = re.sub(r"<metadata>.*?</metadata>", "", svg, flags=re.S)
    return svg.strip()


def _minus(text: str) -> str:
    """ASCII hyphen-minus → U+2212, so an axis matches the prose that cites it."""
    return "−" + text[1:] if text.startswith("-") else text


def _fmt(unit: str | None):
    unit_l = (unit or "").lower().strip()
    # Only a unit that *is* a percentage formats ticks as one; "USD M (net margin %)" is not.
    pct = unit_l.startswith("%") or unit_l in {"percent", "pct", "% of total"}

    def inner(value, _pos):
        if pct:
            return _minus(f"{value:,.6g}%")
        if abs(value) >= 1_000_000_000:
            text = f"{value / 1_000_000_000:,.1f}B"
        elif abs(value) >= 1_000_000:
            text = f"{value / 1_000_000:,.1f}M"
        elif abs(value) >= 10_000:
            text = f"{value / 1_000:,.1f}k"
        else:
            text = f"{value:,.6g}"
        return _minus(text)

    return inner


def _series_values(spec: ChartSpec) -> list[tuple[str, list[float]]]:
    out: list[tuple[str, list[float]]] = []
    for index, series in enumerate(spec.series):
        name = str(series.get("name") or f"Series {index + 1}")
        values: list[float] = []
        for item in series.get("values") or []:
            try:
                values.append(float("nan") if item is None else float(item))
            except (TypeError, ValueError):
                values.append(float("nan"))
        out.append((name, values))
    return out


def _bars(ax, categories, series, colours, stacked: bool = False) -> None:
    count = len(series)
    positions = list(range(len(categories)))
    if stacked or count == 1:
        bottom = [0.0] * len(categories)
        for index, (name, values) in enumerate(series):
            padded = _pad(values, len(categories))
            ax.bar(positions, [0 if math.isnan(v) else v for v in padded] if stacked else padded,
                   0.62, bottom=bottom if stacked else None, label=name,
                   color=f"#{colours[index % len(colours)]}")
            if stacked:
                bottom = [b + (0 if math.isnan(v) else v)
                          for b, v in zip(bottom, padded, strict=False)]
    else:
        width = 0.8 / count
        for index, (name, values) in enumerate(series):
            offset = [p - 0.4 + width * (index + 0.5) for p in positions]
            ax.bar(offset, _pad(values, len(categories)), width, label=name,
                   color=f"#{colours[index % len(colours)]}")
    ax.set_xticks(positions)
    labels = [_wrap(c, 16) for c in categories]
    longest = max((len(part) for label in labels for part in label.split("\n")), default=0)
    rotate = longest > 12 and len(categories) > 4
    ax.set_xticklabels(labels, rotation=25 if rotate else 0, ha="right" if rotate else "center",
                       fontsize=8 if longest > 10 else 8.5)


def _wrap(text: str, width: int, lines: int = 2) -> str:
    words, out, current = str(text).split(), [], ""
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


def _lines(ax, categories, series, colours) -> None:
    for index, (name, values) in enumerate(series):
        ax.plot(categories, _pad(values, len(categories)), marker="o", markersize=4,
                linewidth=2.0 if index == 0 else 1.6, label=name,
                color=f"#{colours[index % len(colours)]}")


def _donut(ax, categories, series, colours) -> None:
    values = [0 if math.isnan(v) else v for v in _pad(series[0][1], len(categories))]
    wedges, *_ = ax.pie(values, startangle=90, counterclock=False,
                        colors=[f"#{colours[i % len(colours)]}" for i in range(len(values))],
                        wedgeprops={"width": 0.42, "edgecolor": "white", "linewidth": 1.5})
    total = sum(values) or 1
    ax.legend(wedges, [f"{c} — {v / total:.0%}" for c, v in zip(categories, values, strict=False)],
              loc="center left", bbox_to_anchor=(1.0, 0.5))
    ax.set_aspect("equal")


def _pad(values: list[float], length: int) -> list[float]:
    return (list(values) + [float("nan")] * length)[:length]
