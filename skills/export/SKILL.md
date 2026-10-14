---
name: export
description: >-
  Export, format or design a finished Vantage dossier (<slug>-vantage.md) as a PowerPoint deck
  (.pptx), a Word whitepaper (.docx), a PDF, and/or a single self-contained HTML microsite or HTML
  deck. Use whenever the user asks to "export the dossier", "turn the Vantage run into a deck",
  "make a whitepaper / PDF from the dossier", "build a microsite for the account", "theme the
  collateral with our brand", or names a Vantage run to format and share. Formats an existing
  dossier only — to research and produce one, use /vantage:generate.
---

# Vantage export — turn a dossier into collateral

Drives `vantage export` from the Vantage repo. Input is a finished `<slug>-vantage.md` (or its run
directory); output is a deck, a whitepaper (+ PDF) and one offline HTML file, every page marked
with the configured classification (default **Confidential**).

> This skill **formats an existing dossier**. It performs no research and adds no facts.

## 0. Resolve the repo

```bash
VANTAGE_REPO="${CLAUDE_PLUGIN_ROOT:-${VANTAGE_REPO:-$(cd -P "$HOME/.claude/skills/vantage/../../.." && pwd -P)}}"
[ -d "$VANTAGE_REPO/harness/export" ] || echo "set VANTAGE_REPO to your vantage clone"
```

Use `$VANTAGE_REPO` in every command; where a literal path is needed (Workflow args), substitute
the resolved absolute path.

## 1. Find the dossier

A run directory works directly — the engine finds `*-vantage.md` inside it. Default output root:

```bash
ls -t ~/.cache/vantage/run/            # newest runs first (engine.output_dir)
```

Ask only if you cannot resolve one. Read the title block to learn the client, as-of date,
**Overall Confidence (EQI)** and **Verification** result:

```bash
uv run --project "$VANTAGE_REPO" python -m vantage.export inspect "<run dir>" --json
```

## 2. Gather parameters (infer; ask only when ambiguous)

| Param | Flag | Default (`export.*` in `~/.config/vantage/default.json`) |
|---|---|---|
| Formats | `--format` (repeatable) | `pptx docx pdf html` — pdf implies docx |
| Depth | `--depth` | `standard` (`exec` ≈ 18 slides · `standard` ≈ 31 · `full` = everything) |
| HTML shape | `--site-mode` | `microsite` (or `deck`) |
| Authoring | `--authoring` | `deterministic` (or `agents`) |
| Output | `--out` | `<run dir>/exports` |
| Marking | `--classification` | `Confidential` |
| Brand | `--brand <domain>` | none — neutral Vantage theme |

"Just the deck" → `--format pptx`; "a Word doc" → `--format docx`; "something to email" → `html`.

## 3. Run

### Agent-authored (preferred inside Claude Code)

Run the bundled Workflow natively with the Workflow tool — Claude authors the plans, code renders:

> Run the workflow at `$VANTAGE_REPO/harness/export/workflows/vantage-export.workflow.mjs` with args:
> ```json
> {"dossier": "<abs path to *-vantage.md>", "repo": "<abs $VANTAGE_REPO>",
>  "depth": "standard", "formats": ["pptx","docx","pdf","html"], "site_mode": "microsite",
>  "classification": "Confidential", "brand": null}
> ```

Five phases: ingest → narrative → three concurrent plan authors → adversarial QA → render.

### Deterministic (fast, no agents)

```bash
uv run --project "$VANTAGE_REPO" vantage export "<run dir or dossier>" \
  --format pptx --format docx --format pdf --format html \
  --depth standard --site-mode microsite
```

Add `--json` for machine-readable events plus a final `{"result": …}`.

### Richer collateral — use the helper skills

The renderer calls these CLIs itself when they are on PATH, but you can direct them for better
results (and check names before putting them in a plan):

- **/icon** (`get-icon`) — pick lucide icons for slide headers, KPI tiles, dividers and nav.
- **/get-brand** (`get-brand`) — `--brand <pursuing-org domain>` themes every output; the client's
  own logo goes on the covers.
- **/stock** (`get-stock`) — choose specific splash images for the cover and section openers
  (`image_query` in the plans).
- **/diagram** (`dgm`) and **/drawio** (`drawio`) — figure-spec blocks become real diagrams;
  feature one on a `figure` slide, or refine a `.drawio` for the whitepaper.
- **/napkin** (`napkin`) — concept illustrations, only when the user opts in
  (`export.helpers.illustrations = "napkin"`); it spends credits.
- Charts come from the dossier's chart-data blocks (matplotlib, or plotly for interactive HTML).

### Re-render after editing a plan

Plans live in `<out>/plan/{deck,doc,site}.json`. Edit one, re-run the deterministic command — it
picks the edited plan up (`manifest.json` then reports it as `authored`).

## 4. Report

Give the user:

- The output directory and each artifact with its size; the slide count (pptx / HTML deck) and the
  PDF page count.
- The `plans` map from `manifest.json` — `authored` (an agent or person wrote it), `scaffold`
  (generated, unedited) or `derived` (missing or failed validation) — and the QA verdict if the
  harness ran.
- The dossier's **Overall Confidence (EQI)** and **verification result** — collateral inherits the
  dossier's reliability.
- Every warning (missing helper, PDF skipped, unmatched contents entries).

Then state the marking plainly, e.g. **Confidential — internal use only, not for client
distribution.**

## Rules

- **Never publish an export to a public URL.** If a share link is wanted it must be
  access-controlled and explicitly requested.
- Never add a fact, never print a score the dossier marks `SUPPRESSED`, never drop `[DATA GAP]`,
  `[ESTIMATED]` or `[INTERNAL REQUIRED]` markers, and honour verification errata.
- `vantage doctor` diagnoses the environment (export extra, LibreOffice for PDF, helper CLIs). If
  the export extra is missing: `uv sync --project "$VANTAGE_REPO" --extra export`.
