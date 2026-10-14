"""The intermediate representation (IR) and the plan contracts.

Two layers, deliberately separated:

**IR** (:class:`Dossier`) — a faithful parse of the ``<slug>-vantage.md`` Markdown. Deterministic:
same input, same IR. Nothing in it is an editorial judgement.

**Plans** (:class:`DeckPlan`, :class:`DocPlan`, :class:`SitePlan`) — what the export agents author.
A plan says *what to say and where*, never *how to draw it*; the renderers own every pixel. Plans
are JSON on disk, so a human can inspect and hand-edit one before rendering.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field

# ─────────────────────────────────────────────────────────────────────────────
# IR — parsed dossier
# ─────────────────────────────────────────────────────────────────────────────


class BlockKind(StrEnum):
    PARAGRAPH = "paragraph"
    TABLE = "table"
    LIST = "list"
    CALLOUT = "callout"
    CODE = "code"
    RULE = "rule"
    CHART = "chart"
    FIGURE = "figure"


class Paragraph(BaseModel):
    kind: Literal[BlockKind.PARAGRAPH] = BlockKind.PARAGRAPH
    text: str


class Table(BaseModel):
    kind: Literal[BlockKind.TABLE] = BlockKind.TABLE
    header: list[str] = Field(default_factory=list)
    rows: list[list[str]] = Field(default_factory=list)
    aligns: list[Literal["left", "center", "right"]] = Field(default_factory=list)
    caption: str | None = None

    @property
    def shape(self) -> tuple[int, int]:
        return len(self.rows), len(self.header)


class ListItem(BaseModel):
    text: str
    level: int = 0


class ListBlock(BaseModel):
    kind: Literal[BlockKind.LIST] = BlockKind.LIST
    ordered: bool = False
    items: list[ListItem] = Field(default_factory=list)


class Callout(BaseModel):
    """A Markdown blockquote: verdicts, errata, warnings and disclaimers."""

    kind: Literal[BlockKind.CALLOUT] = BlockKind.CALLOUT
    text: str
    tone: Literal["note", "verdict", "warning", "disclaimer"] = "note"


class Code(BaseModel):
    kind: Literal[BlockKind.CODE] = BlockKind.CODE
    text: str
    lang: str | None = None


class Rule(BaseModel):
    kind: Literal[BlockKind.RULE] = BlockKind.RULE


class ChartSpec(BaseModel):
    """A chart the renderer generates. Data is supplied by the dossier, never invented."""

    form: Literal["bar", "hbar", "line", "grouped-bar", "stacked-bar", "scatter", "donut",
                  "combo", "waterfall"]
    title: str
    categories: list[str]
    # {"name": str, "values": [float|None], "kind": "bar"|"line"}. ``kind`` is read only by the
    # ``combo`` form, where an absolute series and a rate series need separate axes.
    series: list[dict[str, Any]] = Field(default_factory=list)
    unit: str | None = None
    note: str | None = None
    y_label: str | None = None
    secondary_unit: str | None = None
    id: str | None = None


class FigureSpec(BaseModel):
    """A ``figure-spec`` block: a node/edge diagram, a positioned grid, or an item list."""

    id: str = ""
    title: str = "Figure"
    type: str = ""
    nodes: list[dict[str, Any]] = Field(default_factory=list)
    edges: list[dict[str, Any]] = Field(default_factory=list)
    items: list[dict[str, Any]] = Field(default_factory=list)
    axes: dict[str, Any] = Field(default_factory=dict)
    sources: list[str] = Field(default_factory=list)
    direction: str | None = None

    def caption(self) -> str:
        head = f"Figure {self.id} — {self.title}" if self.id else f"Figure — {self.title}"
        bits = []
        if self.type:
            bits.append(self.type.replace("-", " "))
        if self.sources:
            bits.append("sources " + ", ".join(self.sources[:6]))
        return f"{head} ({'; '.join(bits)})" if bits else head

    @property
    def positioned(self) -> bool:
        """Nodes carry x/y (a quadrant or matrix), so position is the data."""
        return bool(self.nodes) and all("x" in n and "y" in n for n in self.nodes)


class ChartBlock(BaseModel):
    kind: Literal[BlockKind.CHART] = BlockKind.CHART
    spec: ChartSpec


class FigureBlock(BaseModel):
    kind: Literal[BlockKind.FIGURE] = BlockKind.FIGURE
    spec: FigureSpec


Block = Annotated[
    Paragraph | Table | ListBlock | Callout | Code | Rule | ChartBlock | FigureBlock,
    Field(discriminator="kind"),
]


class Section(BaseModel):
    """One heading and everything under it, up to the next heading of <= level."""

    id: str                     # normalised: "1", "1.2", "21.11"
    number: str                 # as written: "1.", "§10"
    title: str                  # heading text with the number stripped
    heading: str                # the full heading line, verbatim
    level: int                  # markdown heading level (2 = ##)
    blocks: list[Block] = Field(default_factory=list)
    children: list[Section] = Field(default_factory=list)

    def walk(self):
        yield self
        for child in self.children:
            yield from child.walk()

    def find(self, section_id: str) -> Section | None:
        for node in self.walk():
            if node.id == section_id:
                return node
        return None

    @property
    def charts(self) -> list[ChartSpec]:
        return [b.spec for b in self.blocks if isinstance(b, ChartBlock)]

    @property
    def figures(self) -> list[FigureSpec]:
        return [b.spec for b in self.blocks if isinstance(b, FigureBlock)]

    def text(self, limit: int | None = None) -> str:
        """Flattened prose, for agents that want the gist of a section."""
        out: list[str] = []
        for block in self.blocks:
            if isinstance(block, Paragraph | Callout):
                out.append(block.text)
            elif isinstance(block, ListBlock):
                out.extend(f"- {i.text}" for i in block.items)
        joined = "\n".join(out)
        return joined[:limit] if limit else joined


class Dossier(BaseModel):
    """A parsed ``<slug>-vantage.md``."""

    title: str
    client: str
    source_path: str
    front_matter: dict[str, str] = Field(default_factory=dict)
    banners: list[Callout] = Field(default_factory=list)
    preamble: list[Paragraph] = Field(default_factory=list)
    sections: list[Section] = Field(default_factory=list)

    # Derived at parse time; cheap for agents and renderers to read.
    version: str | None = None
    tier: str | None = None
    as_of: str | None = None
    overall_confidence: str | None = None
    eqi: float | None = None
    verification: dict[str, Any] | None = None
    client_domain: str | None = None
    vertical: str | None = None

    def walk(self):
        for section in self.sections:
            yield from section.walk()

    def find(self, section_id: str) -> Section | None:
        for section in self.sections:
            hit = section.find(section_id)
            if hit:
                return hit
        return None

    @property
    def body_sections(self) -> list[Section]:
        return [s for s in self.sections if s.id.isdigit() and s.id != "21"]

    def stats(self) -> dict[str, int]:
        sections = list(self.walk())

        def count(kind: type) -> int:
            return sum(1 for s in sections for b in s.blocks if isinstance(b, kind))

        return {
            "sections": len(sections),
            "tables": count(Table),
            "callouts": count(Callout),
            "paragraphs": count(Paragraph),
            "charts": count(ChartBlock),
            "figures": count(FigureBlock),
        }


# ─────────────────────────────────────────────────────────────────────────────
# Plans — authored by the export agents, consumed by the renderers
# ─────────────────────────────────────────────────────────────────────────────


class SlideLayout(StrEnum):
    """Every layout the PPTX and HTML renderers know how to draw.

    A plan may only name one of these. Adding a layout means adding it in both renderers — see
    ``harness/export/blueprint/deck-blueprint.md``.
    """

    TITLE = "title"                  # cover
    SECTION = "section"              # divider
    STATEMENT = "statement"          # one big idea
    BULLETS = "bullets"              # heading + up to 7 bullets
    TWO_COLUMN = "two-column"        # left/right bullet columns
    KPI = "kpi"                      # 2-4 stat tiles
    TABLE = "table"                  # a table, <= 8 rows
    CHART = "chart"                  # a generated chart + takeaway
    FIGURE = "figure"                # a dossier figure (diagram) + takeaway
    QUOTE = "quote"                  # a pull quote with attribution
    TIMELINE = "timeline"            # ordered horizon/phase steps
    MATRIX = "matrix"                # scored grid (renders as a table)
    CLOSING = "closing"              # end card


class KPI(BaseModel):
    value: str
    label: str
    delta: str | None = None
    tone: Literal["neutral", "good", "risk"] = "neutral"
    icon: str | None = None          # semantic icon name, e.g. "gauge"


class TimelineStep(BaseModel):
    when: str
    what: str
    detail: str | None = None


class Slide(BaseModel):
    layout: SlideLayout
    title: str = ""
    subtitle: str = ""
    body: str = ""
    bullets: list[str] = Field(default_factory=list)
    bullets_right: list[str] = Field(default_factory=list)
    column_headings: list[str] = Field(default_factory=list)
    kpis: list[KPI] = Field(default_factory=list)
    table: Table | None = None
    chart: ChartSpec | None = None
    figure: FigureSpec | None = None
    timeline: list[TimelineStep] = Field(default_factory=list)
    attribution: str = ""
    #: Semantic icon for the slide header (a get-icon query such as "shield-alert").
    icon: str | None = None
    #: Natural-language query for a splash image (covers and dividers only).
    image_query: str | None = None

    # Provenance. Every substantive slide points back into the dossier so a reader can audit
    # it, and so QA can prove nothing was invented.
    source_sections: list[str] = Field(default_factory=list)
    claim_refs: list[str] = Field(default_factory=list)

    notes: str = ""              # speaker notes
    emphasis: Literal["light", "dark"] = "light"


class DeckPlan(BaseModel):
    client: str
    title: str
    subtitle: str = "Vantage dossier"
    as_of: str = ""
    audience: str = ""
    thesis: str = ""
    slides: list[Slide] = Field(default_factory=list)


class DocTreatment(StrEnum):
    VERBATIM = "verbatim"      # carry the dossier content through as-is
    CONDENSE = "condense"      # keep tables/callouts/visuals, trim the prose
    SUMMARY = "summary"        # replace with the plan's own summary text
    OMIT = "omit"


class DocSectionPlan(BaseModel):
    section_id: str
    treatment: DocTreatment = DocTreatment.VERBATIM
    heading_override: str | None = None
    summary: str = ""                              # used when treatment=summary
    lead: str = ""                                 # optional standfirst paragraph
    callouts: list[Callout] = Field(default_factory=list)
    charts: list[ChartSpec] = Field(default_factory=list)
    page_break_before: bool = False


class DocPlan(BaseModel):
    client: str
    title: str
    subtitle: str = "Vantage dossier"
    as_of: str = ""
    abstract: str = ""
    author: str = ""
    author_org: str = ""
    author_address: str = ""
    sections: list[DocSectionPlan] = Field(default_factory=list)
    #: ``selected`` renders the subsection ids in ``appendices`` (e.g. "21.1", "21.11").
    appendix_policy: Literal["all", "selected", "none"] = "selected"
    appendices: list[str] = Field(default_factory=list)


class SitePage(BaseModel):
    slug: str
    title: str
    section_ids: list[str] = Field(default_factory=list)
    summary: str = ""
    icon: str | None = None
    image_query: str | None = None


class SitePlan(BaseModel):
    client: str
    title: str
    subtitle: str = "Vantage dossier"
    as_of: str = ""
    mode: Literal["deck", "microsite"] = "microsite"
    pages: list[SitePage] = Field(default_factory=list)


class ExportPlan(BaseModel):
    """What the harness writes to ``<out>/plan/`` — one file per collateral."""

    deck: DeckPlan | None = None
    doc: DocPlan | None = None
    site: SitePlan | None = None


Section.model_rebuild()
