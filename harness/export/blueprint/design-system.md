# Design system — the neutral Vantage theme

The single source of truth in code is `src/vantage/export/theme.py`. This file explains the intent
so an agent planning a collateral knows what the renderer will do with its plan.

## The governing idea

**Ink and paper first, one accent second.** The accent (`#2F5D8A` by default) is the *single*
highlight. Secondary hues (amber, teal, red, green) differentiate series and status only and never
carry meaning on their own — a `risk` KPI gets a red rule *and* a minus sign in its value.

Do not ask for "a colourful comparison". Ask for the one series that matters; the renderer gives
it the accent.

## Tokens

| Token | Hex | Use |
|---|---|---|
| ink | `1B1F24` | body text, dark surfaces |
| ink-soft | `3D4650` | secondary prose |
| ink-faint | `6B7480` | captions, metadata |
| surface | `F4F6F8` | tiles, zebra rows, callouts |
| **accent** | `2F5D8A` | the highlight — one per view |
| accent-deep | `1F3F5F` | whitepaper headings |
| accent-tint | `E7EEF5` | verdict callouts |
| amber / teal / red / green | `D9922E` / `2A8C82` / `C0473A` / `3C8D5A` | differentiation, status |

Type: a serif display face (Georgia in Office; Iowan/Palatino/Georgia stack in HTML) for titles
and KPI values; a humanist sans (Arial / system UI) for body; monospace for claim identifiers.
Sentence case everywhere. Never ALL CAPS headlines.

## `--brand <domain>`

Themes everything to the *pursuing organization*: `get-brand` supplies the palette (its `brand`
colour becomes the accent, darkened until it reads on white at ≥ 4.5:1), real typeface names when
it has them, and a logo placed on every slide header, the whitepaper cover and the microsite nav.
The client's own logo (from the dossier's stated web domain) appears on covers only.

## Emphasis

`dark` for the cover, dividers, statements and the closing card; `light` for anything with a
table, chart, figure or KPI tiles. Never alternate for variety.

## Charts

Pick the form from the question, not the data type. Long category names → horizontal bars (the
renderer flips them). Label directly. Never invent a point to complete a series: a dossier `null`
is drawn as a gap and the caption says so. Combined absolute + rate series get two axes.
Charts render with matplotlib (PNG in Office, inline SVG in HTML) or, with
`helpers.charts = "plotly"`, as interactive Plotly in the HTML.

## Icons and imagery

| Need | Plan field | Helper (skill) |
|---|---|---|
| Icons | `icon` — a lucide name: `gauge`, `shield-alert`, `chart-line`, `lightbulb`, `list-checks`, `building-2`, `users`, `cpu`, `leaf`, `compass`, `target`, `network`, `badge-check`, `triangle-alert`, `circle-help`… | `get-icon` (`/icon`) |
| Photography | `image_query` — a plain description ("aluminium smelter operations") | `get-stock` (`/stock`) |
| Diagrams | dossier figure-spec blocks / `Slide.figure` | `dgm` (`/diagram`), `drawio` (`/drawio`), Mermaid |
| Concept graphics | opt-in, `helpers.illustrations = "napkin"` | `napkin` (`/napkin`) |
| Logos and palette | `--brand` | `get-brand` (`/get-brand`) |

Imagery is an enhancement, never a dependency: if a helper is missing the collateral still builds.
Use one icon family (lucide) so every glyph shares a grid and stroke. Use images on covers and
dividers only — never behind dense content.
