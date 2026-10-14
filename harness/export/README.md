# Vantage export harness

The agentic layer over `vantage export`. Read `ARCHITECTURE.md` first — it explains the one rule
(**agents write plans, code writes files**).

## Layout

```
blueprint/
  classification.md      the marking, the scoring disclaimer, suppressed scores, sharing
  design-system.md       the neutral Vantage theme, --brand theming, charts, icons, imagery
  deck-blueprint.md      the deck's spine, its layouts and their limits
  document-blueprint.md  whitepaper treatments, appendix policy, section numbering
  microsite-blueprint.md the single-file microsite and HTML deck
prompts/
  system-vantage-editor.md the constitution every agent reads first
  briefs/                _common, 01-narrative, 02-deck-plan, 03-doc-plan, 04-microsite-plan, 05-qa-gate
state/                   JSON Schemas generated from the plan models
                         (python -m vantage.export schemas — rerun after editing models.py)
workflows/
  vantage-export.workflow.mjs  the Claude Code Workflow (P0–P4)
```

## Running it

Inside Claude Code: `/vantage:export <run dir or dossier>` (the plugin skill), or run the
workflow directly with the Workflow tool:

```json
{"dossier": "/abs/path/acme-2026-10-vantage.md", "repo": "/abs/path/to/vantage",
 "depth": "standard", "formats": ["pptx", "docx", "pdf", "html"], "site_mode": "microsite"}
```

Headless, from a terminal: `vantage export <run dir> --authoring agents` (Claude Code CLI on PATH)
or `--authoring deterministic` (no model at all).

## Args

| Arg | Default | Meaning |
|---|---|---|
| `dossier` | *(required)* | absolute path to `<slug>-vantage.md` |
| `repo` | *(required when not run from the repo)* | the vantage checkout (`uv run --project`) |
| `run_dir` | `<dossier-dir>/exports` | where collateral and `plan/` land |
| `harness_dir` | `<repo>/harness/export` | this directory |
| `depth` | `standard` | `exec` \| `standard` \| `full` |
| `formats` | `["pptx","docx","pdf","html"]` | any subset (pdf implies docx) |
| `site_mode` | `microsite` | `microsite` \| `deck` — the shape of the HTML |
| `classification` | `Confidential` | marking stamped on every page/slide/screen |
| `brand` | none | pursuing organization's domain, themed via get-brand |
| `render` | `true` | `false` stops after QA (used by `vantage export --authoring agents`) |
