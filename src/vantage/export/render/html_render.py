"""Render a single, fully self-contained HTML file: a microsite or an HTML deck.

* **microsite** — the :class:`SitePlan`: the dossier's own sections as a scrolling document with a
  sticky, searchable, grouped nav.
* **deck** — the :class:`DeckPlan` on a fixed 1920×1080 stage that scales to the viewport, with
  keyboard, click and swipe navigation and deep-linkable slides.

Everything is inlined — stylesheet, script, icons and charts as inline SVG, photographs and logos
as ``data:`` URIs — so the one file opens offline, from disk, from an email attachment. It makes no
network request: there is no external ``src`` or ``href`` anywhere in it.

The classification marking appears in the ``<title>``, a ``classification`` meta tag, every slide
footer and the deck HUD, a fixed marking bar on every microsite screen, and a running footer when
printed.
"""

from __future__ import annotations

import html
import json
from pathlib import Path

from ..context import RenderContext, data_uri
from ..dossier import SECTION_ICON
from ..models import (
    Callout,
    ChartBlock,
    ChartSpec,
    Code,
    DeckPlan,
    Dossier,
    FigureBlock,
    FigureSpec,
    ListBlock,
    Rule,
    Section,
    SitePlan,
    Slide,
    SlideLayout,
    Table,
)
from ..models import Paragraph as IRParagraph
from ..richtext import plain, to_html
from ..theme import DOC_KIND, HANDLING, SCORE_DISCLAIMER
from ..visuals import figure_table, sanitize_svg

SITE_ASSETS = Path(__file__).resolve().parents[1] / "assets" / "site"


def esc(text: object) -> str:
    return html.escape(str(text), quote=True)


class SiteRenderer:
    def __init__(self, dossier: Dossier, ctx: RenderContext, *, deck: DeckPlan | None = None,
                 site: SitePlan | None = None, mode: str = "microsite",
                 meta: dict | None = None) -> None:
        self.dossier = dossier
        self.ctx = ctx
        self.deck = deck
        self.site = site
        self.mode = "deck" if mode == "deck" else "microsite"
        self.meta = meta or {}
        self._svg_no = 0
        self._figure_no = 0

    # ── public API ───────────────────────────────────────────────────────────
    def render(self, out_path: Path) -> Path:
        body = self._deck_html() if self.mode == "deck" else self._microsite_html()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(self._page(body), encoding="utf8")
        return out_path

    # ── page shell ───────────────────────────────────────────────────────────
    def _page(self, body: str) -> str:
        css = (SITE_ASSETS / "site.css").read_text(encoding="utf8")
        script = (SITE_ASSETS / ("deck.js" if self.mode == "deck" else "microsite.js")).read_text(
            encoding="utf8")
        marking = self.ctx.classification
        title = f"{plain(self.dossier.client)} — {DOC_KIND} · {marking}"
        vars_css = self.ctx.theme.css_vars().replace(
            "\n}", f"\n  --marking: {json.dumps(marking)};\n}}")
        return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(marking)} — {esc(HANDLING)}">
<meta name="robots" content="noindex, nofollow, noarchive">
<meta name="classification" content="{esc(marking)}">
<meta name="generator" content="Vantage export">
<style>
{vars_css}
{css}
</style>
</head>
<body class="{self.mode}-body">
{body}
<script>
{script}
</script>
</body>
</html>
"""

    # ── inline visuals ───────────────────────────────────────────────────────
    def _icon(self, name: str | None, klass: str = "icon") -> str:
        svg = self.ctx.icon_svg(name) if name else None
        if not svg:
            return ""
        self._svg_no += 1
        return f'<span class="{klass}" aria-hidden="true">{sanitize_svg(svg, f"i{self._svg_no}")}</span>'

    def _chart(self, spec: ChartSpec, width_in: float = 7.5,
               height_in: float | None = None) -> str:
        markup = self.ctx.charts.html(spec, width_in=width_in, height_in=height_in)
        if not markup:
            return ""
        self._svg_no += 1
        if markup.lstrip().startswith("<svg"):
            markup = sanitize_svg(markup, f"c{self._svg_no}")
        title = esc(plain(spec.title))
        return f'<div class="art" role="img" aria-label="{title}">{markup}</div>'

    def _figure_art(self, spec: FigureSpec) -> str:
        art = self.ctx.figures.render(spec)
        if art is None:
            return ""
        self._svg_no += 1
        if art.svg:
            return f'<div class="art">{sanitize_svg(art.svg, f"f{self._svg_no}")}</div>'
        uri = data_uri(art.png)
        return f'<div class="art"><img src="{uri}" alt="{esc(spec.title)}"></div>' if uri else ""

    def _figure(self, spec: FigureSpec) -> str:
        art = self._figure_art(spec)
        if not art:
            table = figure_table(spec)
            art = f'<div class="table-wrap">{self._table_html(table)}</div>' if table else ""
        return f"<figure>{art}<figcaption>{esc(spec.caption())}</figcaption></figure>"

    def _reliability_chips(self) -> str:
        d, m = self.dossier, self.meta
        chips = []
        if d.as_of:
            chips.append(f"As of <strong>{esc(d.as_of)}</strong>")
        if d.tier:
            chips.append(esc(d.tier.replace("_", " ").title()))
        if d.overall_confidence or d.eqi is not None:
            eqi = f" (EQI {d.eqi:g})" if d.eqi is not None else ""
            chips.append(f"Overall confidence <strong>{esc(d.overall_confidence or '—')}"
                         f"{esc(eqi)}</strong>")
        if m.get("result"):
            counts = " · ".join(f"{m[k]} {k}" for k in ("blockers", "majors", "minors")
                                if m.get(k) is not None)
            risk = " chip--risk" if "FAIL" in str(m["result"]) else ""
            chips.append((f"Verification <strong>{esc(m['result'])}</strong>"
                          + (f" · {esc(counts)}" if counts else ""), risk))
        out = []
        for chip in chips:
            text, extra = chip if isinstance(chip, tuple) else (chip, "")
            out.append(f'<span class="chip{extra}">{text}</span>')
        return f'<div class="chips">{"".join(out)}</div>'

    # ═══════════════════════════════════════════════════════════════════════
    # Deck
    # ═══════════════════════════════════════════════════════════════════════
    def _deck_html(self) -> str:
        if self.deck is None:
            raise ValueError("deck mode needs a DeckPlan")
        slides = "\n".join(self._slide(s, i) for i, s in enumerate(self.deck.slides, start=1))
        marking = esc(self.ctx.classification)
        return f"""<div class="deck__progress"></div>
<div class="deck">
  <div class="stage">
{slides}
  </div>
</div>
<div class="deck__hud">
  <span class="classification">{marking}</span>
  <button data-prev aria-label="Previous slide">&larr;</button>
  <span data-counter>1 / {len(self.deck.slides)}</span>
  <button data-next aria-label="Next slide">&rarr;</button>
</div>"""

    def _slide(self, plan: Slide, index: int) -> str:
        dark = plan.emphasis == "dark"
        klass = "slide slide--dark" if dark else "slide"
        builder = {
            SlideLayout.TITLE: self._s_title, SlideLayout.SECTION: self._s_section,
            SlideLayout.STATEMENT: self._s_statement, SlideLayout.BULLETS: self._s_bullets,
            SlideLayout.TWO_COLUMN: self._s_two_column, SlideLayout.KPI: self._s_kpi,
            SlideLayout.TABLE: self._s_table, SlideLayout.CHART: self._s_chart,
            SlideLayout.FIGURE: self._s_figure, SlideLayout.QUOTE: self._s_quote,
            SlideLayout.TIMELINE: self._s_timeline, SlideLayout.MATRIX: self._s_table,
            SlideLayout.CLOSING: self._s_closing,
        }.get(plan.layout, self._s_bullets)
        refs = " · ".join(f"§{s}" for s in plan.source_sections[:4])
        claims = (f'<div class="slide__claims">{esc(" · ".join(plan.claim_refs[:8]))}</div>'
                  if plan.claim_refs and plan.layout not in {SlideLayout.TITLE,
                                                             SlideLayout.SECTION} else "")
        score = SCORE_DISCLAIMER in (plan.notes or "") or (
            plan.chart is not None and SCORE_DISCLAIMER in (plan.chart.note or ""))
        disclaimer = (f'<div class="slide__disclaimer">{esc(SCORE_DISCLAIMER)}</div>'
                      if score else "")
        logo = self.ctx.brand_logo_dark if dark else self.ctx.brand_logo
        brand = (f'<div class="slide__brand"><img src="{data_uri(logo)}" alt=""></div>'
                 if logo is not None and plan.layout != SlideLayout.TITLE else "")
        return f"""    <section class="{klass}" data-index="{index}">
      {brand}
      {builder(plan)}
      {disclaimer}
      {claims}
      <div class="slide__foot">
        <span class="classification">{esc(self.ctx.classification)}</span>
        <span class="slide__num">{index}</span>
        <span class="slide__refs">{esc(refs)}</span>
      </div>
    </section>"""

    def _s_title(self, plan: Slide) -> str:
        image = data_uri(self.ctx.stock(plan.image_query))
        logo = data_uri(self.ctx.client_logo)
        brand = data_uri(self.ctx.brand_logo_dark)
        meta = f'<div class="meta anim">{esc(plain(plan.body))}</div>' if plan.body else ""
        reliability = self._reliability_text()
        return f"""<div class="cover{'' if image else ' cover--plain'}">
        <div class="cover__text">
          {f'<div class="logo"><img src="{logo}" alt="{esc(plain(plan.title))} logo"></div>' if logo else ''}
          <div class="band"></div>
          <h1 class="anim">{esc(plain(plan.title))}</h1>
          <div class="sub anim">{esc(plain(plan.subtitle))}</div>
          {meta}
          {f'<div class="reliability anim">{reliability}</div>' if reliability else ''}
          {f'<img class="brandmark" src="{brand}" alt="">' if brand else ''}
        </div>
        {f'<div class="cover__image" style="background-image:url({image})"></div>' if image else ''}
      </div>"""

    def _reliability_text(self) -> str:
        d, m = self.dossier, self.meta
        parts = []
        if d.overall_confidence or d.eqi is not None:
            eqi = f" (EQI {d.eqi:g})" if d.eqi is not None else ""
            parts.append(f"<strong>Overall confidence:</strong> "
                         f"{esc(d.overall_confidence or '—')}{esc(eqi)}")
        if m.get("result"):
            counts = " · ".join(f"{m[k]} {k}" for k in ("blockers", "majors", "minors")
                                if m.get(k) is not None)
            parts.append(f"<strong>Verification:</strong> {esc(m['result'])}"
                         + (f" ({esc(counts)})" if counts else ""))
        return "<br>".join(parts)

    def _s_section(self, plan: Slide) -> str:
        image = data_uri(self.ctx.stock(plan.image_query))
        sub = f'<h3 class="anim">{esc(plain(plan.subtitle))}</h3>' if plan.subtitle else ""
        return f"""<div class="section-divider{'' if image else ' section-divider--plain'}">
        <div class="section-divider__text">
          {self._icon(plan.icon)}
          <div class="rule-accent"><h2 class="anim">{esc(plain(plan.title))}</h2>{sub}</div>
        </div>
        {f'<div class="section-divider__image" style="background-image:url({image})"></div>' if image else ''}
      </div>"""

    def _s_statement(self, plan: Slide) -> str:
        qual = f'<div class="qual">{esc(plain(plan.subtitle))}</div>' if plan.subtitle else ""
        support = f'<p class="support anim">{to_html(plan.body)}</p>' if plan.body else ""
        return f"""<div class="statement">
        {self._icon(plan.icon)}
        <div class="rule-accent"><div class="lead anim">{to_html(plan.title)}</div>{qual}</div>
        {support}
      </div>"""

    def _head(self, plan: Slide) -> str:
        sub = f'<h3 class="anim">{esc(plain(plan.subtitle))}</h3>' if plan.subtitle else ""
        return (f'<div class="slide__title">{self._icon(plan.icon)}<div>'
                f'<h2 class="anim">{esc(plain(plan.title))}</h2>{sub}</div></div>')

    def _s_bullets(self, plan: Slide) -> str:
        lead = f'<p class="anim">{to_html(plan.body)}</p>' if plan.body else ""
        items = "".join(f"<li>{to_html(b)}</li>" for b in plan.bullets[:7])
        dense = " dense" if len(plan.bullets) >= 5 else ""
        bullets = f'<ul class="bullets anim{dense}">{items}</ul>' if items else ""
        return f'<div class="slide__head">{self._head(plan)}{lead}{bullets}</div>'

    def _s_two_column(self, plan: Slide) -> str:
        cols = []
        for heading, bullets in zip(plan.column_headings or ["", ""],
                                    [plan.bullets, plan.bullets_right], strict=False):
            head = f"<h4>{esc(plain(heading))}</h4>" if heading else ""
            items = "".join(f"<li>{to_html(b)}</li>" for b in bullets[:7])
            cols.append(f'<div>{head}<ul class="bullets">{items}</ul></div>')
        return (f'<div class="slide__head">{self._head(plan)}'
                f'<div class="columns anim">{"".join(cols)}</div></div>')

    def _s_kpi(self, plan: Slide) -> str:
        tiles = []
        for kpi in plan.kpis[:4]:
            delta = f'<div class="kpi__delta">{esc(plain(kpi.delta))}</div>' if kpi.delta else ""
            tiles.append(
                f'<div class="kpi kpi--{esc(kpi.tone)}">{self._icon(kpi.icon)}'
                f'<div class="kpi__value">{esc(plain(kpi.value))}</div>'
                f'<div class="kpi__label">{esc(plain(kpi.label))}</div>{delta}</div>')
        return (f'<div class="slide__head">{self._head(plan)}'
                f'<div class="kpis anim">{"".join(tiles)}</div></div>')

    def _s_table(self, plan: Slide) -> str:
        if plan.table is None:
            return f'<div class="slide__head">{self._head(plan)}</div>'
        note = (f'<div class="table-note">{esc(plain(plan.table.caption))}</div>'
                if plan.table.caption else "")
        return (f'<div class="slide__head">{self._head(plan)}'
                f'<div class="anim">{self._table_html(plan.table)}{note}</div></div>')

    def _s_chart(self, plan: Slide) -> str:
        if plan.chart is None:
            return f'<div class="slide__head">{self._head(plan)}</div>'
        art = self._chart(plan.chart, width_in=8.6, height_in=4.6)
        aside = f'<div class="rule-accent"><p>{to_html(plan.body)}</p></div>' if plan.body else ""
        note = (f'<div class="table-note">{esc(plain(plan.chart.note))}</div>'
                if plan.chart.note and SCORE_DISCLAIMER not in plan.chart.note else "")
        return (f'<div class="slide__head">{self._head(plan)}<div class="chart-row anim">'
                f"<div>{art}{note}</div>{aside}</div></div>")

    def _s_figure(self, plan: Slide) -> str:
        if plan.figure is None:
            return f'<div class="slide__head">{self._head(plan)}</div>'
        art = self._figure_art(plan.figure)
        if not art:
            table = figure_table(plan.figure)
            art = self._table_html(table) if table else ""
        aside = f'<div class="rule-accent"><p>{to_html(plan.body)}</p></div>' if plan.body else ""
        return (f'<div class="slide__head">{self._head(plan)}<div class="chart-row anim">'
                f'<div>{art}<div class="table-note">{esc(plan.figure.caption())}</div></div>'
                f"{aside}</div></div>")

    def _s_quote(self, plan: Slide) -> str:
        attrib = (f'<div class="attrib anim">{esc(plain(plan.attribution))}</div>'
                  if plan.attribution else "")
        return (f'<div class="statement quote rule-accent"><div class="mark anim">'
                f"&ldquo;{esc(plain(plan.title))}&rdquo;</div>{attrib}</div>")

    def _s_timeline(self, plan: Slide) -> str:
        steps = "".join(
            f'<div class="step"><div class="when">{to_html(s.when)}</div>'
            f'<div class="what">{to_html(s.what)}</div>'
            + (f'<div class="detail">{to_html(s.detail)}</div>' if s.detail else "") + "</div>"
            for s in plan.timeline[:5])
        return (f'<div class="slide__head">{self._head(plan)}'
                f'<div class="timeline anim">{steps}</div></div>')

    def _s_closing(self, plan: Slide) -> str:
        return f"""<div class="closing">
        <h1 class="anim">{esc(plan.title or "Vantage")}</h1>
        <div class="disclaimer anim">{esc(plan.subtitle or SCORE_DISCLAIMER)}</div>
        <div class="handling anim">{esc(self.ctx.classification)} · {esc(HANDLING)}</div>
      </div>"""

    # ═══════════════════════════════════════════════════════════════════════
    # Microsite
    # ═══════════════════════════════════════════════════════════════════════
    def _microsite_html(self) -> str:
        if self.site is None:
            raise ValueError("microsite mode needs a SitePlan")
        nav: list[str] = []
        body: list[str] = []
        for page in self.site.pages:
            live = [s for s in page.section_ids if self.dossier.find(s) is not None]
            if not live:
                continue
            nav.append(f'<div class="nav-group">{self._icon(page.icon)}{esc(plain(page.title))}'
                       f"</div>")
            image = data_uri(self.ctx.stock(page.image_query))
            summary = (f'<p class="group-summary">{to_html(page.summary)}</p>'
                       if page.summary else "")
            body.append(
                f'<div class="site__group{" has-image" if image else ""}" id="grp-{esc(page.slug)}">'
                f'<div class="text"><div class="group-title">{self._icon(page.icon)}'
                f"{esc(plain(page.title))}</div>{summary}</div>"
                + (f'<div class="image" style="background-image:url({image})"></div>'
                   if image else "") + "</div>")
            for section_id in live:
                section = self.dossier.find(section_id)
                anchor = f"sec-{section_id.replace('.', '-')}"
                label = f"§{section.id} {plain(section.title)}".strip()
                words = esc(plain(section.text(600)).lower()[:600])
                nav.append(f'<a href="#{anchor}" data-text="{words}">{esc(label)}</a>')
                body.append(self._section_html(section, anchor, level=2))
        d = self.dossier
        cover = data_uri(self.ctx.stock(self._cover_query()))
        logo = data_uri(self.ctx.client_logo)
        brand = data_uri(self.ctx.brand_logo_dark)
        brand_name = self.ctx.theme.brand_name
        marking = esc(self.ctx.classification)
        brand_block = (f'<img src="{brand}" alt="{esc(brand_name or "")}">' if brand
                       else '<span class="name">Vantage</span>')
        banner_style = f' style="background-image:url({cover})"' if cover else ""
        return f"""<div class="site">
  <nav class="site__nav" aria-label="Sections">
    <div class="brand">{brand_block}</div>
    <div class="brand-sub">{esc(DOC_KIND)} · {esc(plain(d.client))}</div>
    <input type="search" placeholder="Filter sections" aria-label="Filter sections">
    {"".join(nav)}
    <div class="foot"><span class="classification">{marking}</span><br>{esc(HANDLING)}</div>
  </nav>
  <main class="site__main">
    <header class="site__banner{' has-image' if cover else ''}"{banner_style}>
      {f'<div class="logo"><img src="{logo}" alt="{esc(plain(d.client))} logo"></div>' if logo else ''}
      <h1>{esc(plain(d.client))}</h1>
      <div class="sub">{esc(DOC_KIND)}</div>
      {self._reliability_chips()}
    </header>
    <div class="site__body">
      {"".join(self._callout_html(b, banner=True) for b in d.banners)}
      {"".join(body)}
    </div>
    <footer class="site__foot">
      <span class="classification">{marking}</span>
      <span>{esc(HANDLING)} {esc(SCORE_DISCLAIMER)}</span>
    </footer>
  </main>
</div>
<div class="marking-bar" role="note">{marking}</div>"""

    def _cover_query(self) -> str:
        from ..dossier import vertical_words

        words = vertical_words(self.dossier)
        return f"{words or 'corporate'} {plain(self.dossier.client)} operations".strip()

    def _section_html(self, section: Section, anchor: str, level: int) -> str:
        tag = f"h{min(level, 4)}"
        label = f"§{section.id} {plain(section.title)}" if section.number else plain(section.title)
        icon = self._icon(SECTION_ICON.get(section.id)) if level == 2 else ""
        parts = [f'<{tag} id="{esc(anchor)}">{icon}{esc(label)}</{tag}>']
        parts.extend(self._block_html(b) for b in section.blocks)
        for child in section.children:
            parts.append(self._section_html(child, f"sec-{child.id.replace('.', '-')}", level + 1))
        return "\n".join(parts)

    def _block_html(self, block) -> str:
        if isinstance(block, IRParagraph):
            return "".join(f"<p>{to_html(c)}</p>" for c in block.text.split("\n\n") if c.strip())
        if isinstance(block, Table):
            return f'<div class="table-wrap">{self._table_html(block)}</div>'
        if isinstance(block, ListBlock):
            tag = "ol" if block.ordered else "ul"
            items = "".join(
                f'<li style="margin-left:{i.level * 1.2}em">{to_html(i.text)}</li>'
                if i.level else f"<li>{to_html(i.text)}</li>" for i in block.items)
            return f"<{tag}>{items}</{tag}>"
        if isinstance(block, Callout):
            return self._callout_html(block)
        if isinstance(block, ChartBlock):
            self._figure_no += 1
            label = f"{block.spec.id} — {block.spec.title}" if block.spec.id else block.spec.title
            note = f" ({block.spec.note})" if block.spec.note else ""
            return (f"<figure>{self._chart(block.spec)}<figcaption>{esc(label)}{esc(note)}"
                    f"</figcaption></figure>")
        if isinstance(block, FigureBlock):
            return self._figure(block.spec)
        if isinstance(block, Code):
            return f"<pre><code>{esc(block.text)}</code></pre>"
        if isinstance(block, Rule):
            return ""
        return ""

    def _callout_html(self, callout: Callout, banner: bool = False) -> str:
        labels = {"verdict": "", "warning": "Read this first", "disclaimer": "", "note": ""}
        label = labels.get(callout.tone, "")
        if banner and callout.tone == "warning":
            label = "Read before use"
        head = f'<div class="label">{esc(label)}</div>' if label else ""
        body = "".join(f"<p>{to_html(c)}</p>" for c in callout.text.split("\n\n") if c.strip())
        return f'<div class="callout callout--{esc(callout.tone)}">{head}{body}</div>'

    # ── shared ───────────────────────────────────────────────────────────────
    def _table_html(self, table: Table | None) -> str:
        if table is None:
            return ""
        head = "".join(f"<th>{to_html(h)}</th>" for h in table.header)
        rows = []
        for row in table.rows:
            cells = "".join(f"<td{self._align(table, i)}>{to_html(c)}</td>"
                            for i, c in enumerate(row))
            rows.append(f"<tr>{cells}</tr>")
        thead = f"<thead><tr>{head}</tr></thead>" if head else ""
        return f'<table class="grid">{thead}<tbody>{"".join(rows)}</tbody></table>'

    @staticmethod
    def _align(table: Table, index: int) -> str:
        if index < len(table.aligns) and table.aligns[index] != "left":
            return f' style="text-align:{table.aligns[index]}"'
        return ""


def render_site(dossier: Dossier, out_path: Path, ctx: RenderContext, *,
                deck: DeckPlan | None = None, site: SitePlan | None = None,
                mode: str = "microsite", meta: dict | None = None) -> Path:
    return SiteRenderer(dossier, ctx, deck=deck, site=site, mode=mode, meta=meta).render(out_path)
