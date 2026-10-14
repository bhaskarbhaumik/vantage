# HTML blueprint — microsite and deck

One stylesheet, two modes, **one file**. The HTML export is a single self-contained `.html`: CSS,
script, icons, charts (inline SVG), diagrams (inline SVG) and photographs/logos (`data:` URIs) are
all inside it. It makes no network request and has no external `src` or `href` — it opens offline,
from disk or an email attachment.

## Mode: `microsite` (default)

The `SitePlan`: the dossier's own sections as a scrolling document with a sticky, grouped,
searchable nav. Content is rendered **from the dossier**, not from authored text: the plan chooses
grouping, order, page summaries, page icons and page images.

Default grouping:

| Slug | Title | Sections |
|---|---|---|
| `brief` | Executive summary | §1 |
| `company` | Company and market | §3, §4, §5 |
| `financials` | Financial performance | §6 |
| `operations` | Operations and technology | §7, §8, §15, §16 |
| `strategy` | Strategy, leadership and competition | §9–§13 |
| `risk` | Risk and ESG | §14, §17 |
| `pursuit` | Opportunity and pursuit | §18, §19, §20 |
| `method` | Run contract and method | §0, §2 |
| `reference` | Registers and verification | §21.1, §21.8, §21.11 (`full`: §21) |

Regroup when the dossier's weight suggests it. Every page needs at least one section that exists.
`section_ids` may name subsections (`21.11`).

## Mode: `deck`

The `DeckPlan` on a fixed 1920×1080 stage that scales to the viewport: arrow keys, space, `j`/`k`,
Home/End, click, swipe, `f` for fullscreen; deep links (`#14`). Same layouts and limits as the
`.pptx` — the two renderers consume the identical plan.

## Both modes

- The classification marking in the `<title>`, a `classification` meta tag, every slide footer /
  a fixed marking bar on every microsite screen, and a running footer when printed.
- The banner carries as-of, tier, Overall Confidence (EQI) and the verification result.
- `<meta name="robots" content="noindex, nofollow, noarchive">`.
- Wide tables scroll inside their own container; the page never scrolls horizontally.
