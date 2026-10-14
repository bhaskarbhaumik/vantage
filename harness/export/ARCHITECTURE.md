# Vantage export harness — architecture

## The one rule

**Agents write plans. Code writes files.**

An agent never emits `.pptx`, `.docx` or HTML. It emits a JSON *plan* validated against the
pydantic models in `src/vantage/export/models.py` (schemas in `state/`). The renderers own every
pixel. This buys three things:

- **Reproducibility.** The same plan renders identically. Re-render after a theme change without
  re-running a single agent.
- **Inspectability.** A plan is a small JSON file a person can read, diff and hand-edit.
- **A hard safety boundary.** A plan cannot drop the classification marking, the verification
  result on the cover, or the scoring disclaimer: it has no vocabulary for them.

## Pipeline

```
<slug>-vantage.md
   │
   ├─ P0  ingest       deterministic — python -m vantage.export inspect / plan
   │                   parses the dossier, writes the derived plans as a scaffold
   ├─ P1  narrative    one agent reads §0–§2, §1, §18–§20, §21.8, §21.11 and decides the story
   ├─ P2  authoring    three concurrent agents, one per collateral
   │      ├─ deck-plan       plan/deck.json
   │      ├─ doc-plan        plan/doc.json
   │      └─ site-plan       plan/site.json
   ├─ P3  qa-gate      one adversarial agent: every number traced, nothing invented, no
   │                   SUPPRESSED score resurrected, markers intact; empowered to fix
   └─ P4  render       deterministic — python -m vantage.export render (or `vantage export`)
                       → .pptx · .docx · .pdf · one self-contained .html
```

P0 and P4 are Python. P1–P3 are Claude Code agents reading Markdown briefs from
`prompts/briefs/`. The workflow script (`workflows/vantage-export.workflow.mjs`) holds no prompt
text — it passes *paths*, and each agent reads its own brief, so the prompt library stays
editable as plain Markdown.

`vantage export --authoring agents` runs P0–P3 through the Claude Code CLI (headless, on the
subscription — the same mechanism as the `workflow` research backend) with `render: false`, then
renders P4 itself. `--authoring deterministic` skips P1–P3 and renders the scaffold.

## Visual helpers

Plans name *what* to show; helpers fetch it. Every helper is optional and cached under
`<out>/.assets/`; a missing helper degrades to a built-in fallback and a `run_warning`.

| Plan field / block | Helper (Claude Code skill) | Fallback |
|---|---|---|
| `Slide.icon`, `KPI.icon`, `SitePage.icon` | `get-icon` (`/icon`), lucide family | accent marker |
| `Slide.image_query`, `SitePage.image_query` | `get-stock` (`/stock`) | plain layout |
| `--brand <domain>`, client cover logo | `get-brand` (`/get-brand`) | neutral Vantage theme |
| ```` ```figure-spec ```` blocks, `Slide.figure` | `dgm` (`/diagram`) → `drawio` (`/drawio`) → `mmdc` | built-in matplotlib diagram |
| ```` ```chart-data ```` blocks, `Slide.chart` | matplotlib (or plotly) | — |
| concept illustration (opt-in) | `napkin` (`/napkin`) | none |

## Contracts

| Stage | Reads | Writes | Validated against |
|---|---|---|---|
| ingest | dossier | `plan/*.json` + `plan/.scaffold.json` | `DeckPlan` / `DocPlan` / `SitePlan` |
| narrative | dossier | `plan/story.md` | prose |
| deck-plan | dossier + story | `plan/deck.json` | `state/deck.plan.schema.json` |
| doc-plan | dossier + story | `plan/doc.json` | `state/doc.plan.schema.json` |
| site-plan | dossier + story | `plan/site.json` | `state/site.plan.schema.json` |
| qa-gate | plans + dossier | `plan/qa.json` | prose + verdict |
| render | plans + dossier | the collateral + `manifest.json` | — |

A malformed plan degrades *that* collateral to its derived plan and records a warning; it never
fails the run. `manifest.json` records each plan as `authored`, `scaffold` or `derived`.

## Classification

Not a plan field and not an agent's decision: `export.classification` (default `Confidential`) is
stamped by the renderers on every slide, page and screen. See `blueprint/classification.md`.
