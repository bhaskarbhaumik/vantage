# Common preamble — every agent reads this

## Inputs you are given

| Variable | Meaning |
|---|---|
| `DOSSIER` | absolute path to `<slug>-vantage.md` |
| `RUN_DIR` | where exports land (default `<dossier-dir>/exports`) |
| `PLAN_DIR` | `$RUN_DIR/plan` — derived plans are already there |
| `HARNESS_DIR` | this harness (`harness/export`) |
| `DEPTH` | `exec` \| `standard` \| `full` |
| `ENGINE` | `uv run --project <repo> python -m vantage.export` |

## Read the dossier, do not skim it

The dossier is long (often 7,000+ lines). Read what your brief tells you to read, in full. The most
consequential sentences sit in the middle of tables, inside errata blockquotes and in table notes.

```bash
$ENGINE inspect "$DOSSIER"                 # structure, title block, stats
$ENGINE inspect "$DOSSIER" --section 1.4   # one section's blocks
$ENGINE inspect "$DOSSIER" --json          # machine-readable summary incl. verification
```

Or `Read` the Markdown with an offset. The parser view is faster for orientation; the raw Markdown
is authoritative.

## The derived plan is your scaffold

`$PLAN_DIR/deck.json`, `doc.json` and `site.json` already exist, generated deterministically.
They are structurally valid and editorially flat. **Start from them**; spend your effort on
judgement — what leads, what is cut, where the tension is.

> **Never run `$ENGINE plan`.** It regenerates the scaffold. You only ever need `render`, which
> reads plans and never writes them.

## Visual helpers you may use

The renderers fetch visuals through the same CLIs the Claude Code skills wrap. You choose; they draw.

| Skill | CLI | How a plan uses it |
|---|---|---|
| `/icon` | `get-icon iconify search <term> -p lucide` | `icon` on slides, KPIs and site pages — a **lucide** icon name (verify it exists with the search) |
| `/stock` | `get-stock --json "<description>"` | `image_query` on cover/divider slides and site pages — a plain description of the scene |
| `/get-brand` | `get-brand <domain> --json` | not in plans — `--brand` is a run option; you may check what palette it returns |
| `/diagram`, `/drawio` | `dgm`, `drawio` | figure-spec blocks render automatically; feature one with a `figure` slide (copy the spec verbatim) |
| `/napkin` | `napkin` | only when the run enables illustrations; it spends credits — never call it yourself |
| charts | matplotlib / plotly (via `uv`), d3/vega (via `npm`) for previews only | `chart` specs — every value copied from the dossier |

You may run these CLIs to *check* an icon name or preview an image query. Do not download assets
into the plan; the renderer caches its own under `$RUN_DIR/.assets/`. Never invent an image URL.

## Output

Write exactly one file, to the path your brief names: JSON that validates against the schema in
`$HARNESS_DIR/state/`. Overwrite the derived file.

Validate before you finish:

```bash
$ENGINE render "$DOSSIER" --out "$RUN_DIR" --format pptx      # exercises deck.json
```

and read `$RUN_DIR/manifest.json`: your collateral's entry under `plans` must read `authored`.
`scaffold` means you never wrote it; `derived` means it failed validation and was discarded (the
warning says why).

## Rules you inherit

`$HARNESS_DIR/prompts/system-vantage-editor.md` is your constitution, and
`$HARNESS_DIR/blueprint/classification.md` is enforced by the renderers — you do not add the
marking, and you must not remove a disclaimer, an erratum or a marker the dossier carries.
