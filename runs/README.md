# runs/

Each dossier run writes a directory here (git-ignored):

```
runs/<slug>/
  <slug>-vantage.md                     ← the deliverable
  sections/                         per-agent Markdown, in blueprint order
  state/
    state.json                      merged canonical state (schema 3.0)
    precomputed-financials.json     the numeric source of truth for §6 and §21.3
    fragments/<agent>.json          per-agent contributions before merge
  qa/
    verification-report.md / .json  V1–V12 results, Overall Confidence, disclosures
    evidence-audit.json             adversarial verdicts; the `refuted` list is BINDING on §18
    source-rewrite-map.json         retired → kept source IDs after dedup
  run.jsonl                         structured event log (consumed by the Ink TUI)
```

The default output root is `~/.cache/vantage/run` (see `config/default.json` →
`engine.output_dir`); this in-repo `runs/` is used when you point the engine here.

## Reading a finished run

Three things say how much to trust the dossier:

- **Overall Confidence** in the title block — `Strong` ≥80 · `Adequate` 65–79 · `Thin` 50–64 ·
  `Insufficient` <50. **Insufficient means do not present it.**
- **§21.12 Source-Completeness Scorecard** — and specifically which topics stopped on *budget*
  rather than on *diminishing returns*. Those are worth re-running with an extended budget; the
  rest genuinely found nothing.
- **§2.5** and **§21.11** — every autonomous assumption, high-materiality gap, and open
  contradiction the run could not resolve.
