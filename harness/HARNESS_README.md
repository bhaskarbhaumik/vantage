# Vantage v3.0.0 Harness

The prompt library and execution graph that produce a Vantage dossier — *Verified Account Navigator: Targeting, Analysis & GTM Engine*. Implements
`aid-20260829.md` (AID Prompt Package v3.0.0, Vantage contributors).

**Architecture and design rationale:** `ARCHITECTURE.md`.

**Reverting the report format:** `.superseded-aid-v3/` holds the pre-rename AID v3.0.0
harness. `scripts/backout-vantage-v1-to-aid.sh apply|restore|status` swaps the two. The
engine follows whichever is installed — filenames resolve through `Blueprint._resolve()`
and the dossier is named `<slug>-vantage.md` or `<slug>-aid.md` accordingly — so no engine
source changes. `.superseded-v2/` is the older v2.1/v2.2 harness; nothing reads from it.

---

## Layout

```
harness/
  ARCHITECTURE.md                     design decisions, the DAG, phase mapping
  prompts/
    system-vantage-analyst.md             the constitution — byte-stable, caches across every agent
    id-allocation.md                  per-agent ID blocks; collision avoidance under parallelism
    briefs/_common.md                 shared preamble every brief inherits
    briefs/00-preflight.md … 28-assembly.md   one brief per agent
  blueprint/
    vantage-blueprint-v3.md               what each of the 22 sections contains
    section-contracts.md              who writes it · envelope · evidence bar · dependencies
    evidence-policy.md                status enum · confidence dimensions · corroboration · gaps
    verification-protocol.md          V1–V12, the six spec-mandated Pass checks, Overall Confidence
    scoring-rubrics.md                the eight models, anchored
    jurisdiction-adapters.md          disclosure backbone per jurisdiction + ownership-form branching
    vertical-modules.md               eleven modules, six blocks each
    tooling-map.md                    section → where its evidence actually lives
  state/state.schema.json             schema 3.0 — the v3 handoff contract, extended
  workflows/vantage-v3.workflow.mjs       the Claude Code Workflow runner
  .superseded-v2/                     the frozen v2 generation; nothing reads from it
```

The Markdown **is** the harness. The workflow script passes paths, never content — so you can edit
any brief, rubric, or contract without touching the runner.

## Running it

### Through the CLI (recommended)

```bash
vantage run --client "Acme Industries, Inc." --slug acme-2026-08
vantage run -c "Acme" -s acme --tier EXECUTIVE
vantage run -c "Acme" -s acme --capability-pack ATTACHED --input-sheet ATTACHED
```

### Through Claude Code directly

> Use a workflow (this is an explicit opt-in). Run the workflow at
> `harness/workflows/vantage-v3.workflow.mjs` with these args as JSON, and execute it to completion
> without asking questions:
>
> ```json
> {"client_legal_name":"Acme Industries, Inc.","slug":"acme-2026-08",
>  "research_as_of":"2026-08-29","output_tier":"FULL_ANNEX"}
> ```

### Args contract

| Arg | Required | Default | Notes |
|---|---|---|---|
| `client_legal_name` | ✅ | — | The target as given; `preflight` resolves the legal entity |
| `research_as_of` | ✅ | — | Workflow scripts cannot call `Date.now()` — supply it |
| `slug` | ✅ | — | Run directory name |
| `output_tier` | | `FULL_ANNEX` | `EXECUTIVE` \| `STANDARD` \| `FULL_ANNEX` |
| `client_common_name` | | = legal name | |
| `ticker_or_private` | | `AUTO-DETECT` | |
| `primary_geography` | | `AUTO-DETECT` | |
| `target_vertical` | | `AUTO-DETECT` | Detected from revenue mix, not codes alone |
| `capability_pack` | | `NOT_ATTACHED` | Gates every organization capability claim |
| `account_team_input_sheet` | | `NOT_ATTACHED` | Gates win probability, revenue, access |
| `account_context` | | `NONE` | |
| `known_relationship_context` | | `NONE` | |
| `strategic_pursuit_objectives` | | `NONE` | Drives §2.1 intelligence questions |
| `harness_dir` | | `harness` | |
| `run_dir` | | `runs/<slug>` | |

## Output tiers

| Tier | Body | Appendices | Agents |
|---|---|---|---|
| `EXECUTIVE` | §0–§2 + §1 synthesis + top tables | 21.1, 21.9, 21.12 | 19 — Wave A reduced, Wave B skipped |
| `STANDARD` | §0–§20, Opt subsections only where evidenced | 21.1–21.4, 21.8–21.12 | 29 |
| `FULL_ANNEX` | All 22 sections | 21.1–21.12 | 29 — the default |

## Run output layout

```
runs/<slug>/
  <slug>-vantage.md                     the dossier
  sections/                         one file per owning agent, in blueprint order
  state/
    state.json                      merged schema-3.0 state
    precomputed-financials.json     the numeric source of truth for §6 (V2a)
    fragments/<agent>.json          per-agent contributions before merge
  qa/
    evidence-audit.json             adversarial verdicts; the refuted list is BINDING
    verification-report.md/.json    V1–V12 outcomes, Overall Confidence, disclosures
    source-rewrite-map.json         retired → kept source IDs after dedup
  run.jsonl                         structured event stream
```

## Reading the result

Three things tell you how much to trust the dossier, and they are all in the title block or §21:

1. **Overall Confidence** (title block) — `Strong` ≥80 · `Adequate` 65–79 · `Thin` 50–64 ·
   `Insufficient` <50. **Insufficient means do not present it.**
2. **§21.12 Source-Completeness Scorecard** — and specifically, which topics stopped on **budget**
   rather than on diminishing returns. Those are worth re-running with an extended budget; the rest
   genuinely found nothing.
3. **§2.5 Limitations** and **§21.11** — every autonomous assumption, every high-materiality gap,
   and every open contradiction the run could not resolve.

A run that renders 60% of sections honestly is worth more than one that renders 100% with a quarter
invented. The Verification Pass exists to tell the two apart.

## Gated content

Four things cannot be derived from public evidence: **win probability · account revenue ·
relationship strength · stakeholder access.**

Without the §21.10 Account-Team Input Sheet those fields render `[INTERNAL REQUIRED]`, §1.6
scores Stakeholder Access as `NOT ASSESSED` and shows the weight renormalization, and §16.4 renders
a completion marker. Without the Capability Pack, every capability, offering, proof point, and
reference renders `[INTERNAL: validate with practice]`.

§21.10 is emitted as a **blank template** — filling it in and re-running is what unlocks those
fields.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Run stops at P0 with an entity ambiguity | Two candidates were both plausible and no retrieved record separated them | Supply `ticker_or_private` or a fuller legal name. Researching the wrong company thoroughly is the worst outcome this harness can produce. |
| §6 numbers do not reconcile | `precomputed-financials` was unavailable (no XBRL for this jurisdiction/ownership form) | Expected for most private targets. §6 recomputes from filings with inputs shown, and says so. |
| Many sections read "no evidence found" | Thin disclosure, or a jurisdiction with a light regime | Check §21.12: `not_applicable` means the adapter does not provide it; `budget` means re-run with more. |
| Overall Confidence `Insufficient` | Evidence base too thin for the tier | Reduce scope to `EXECUTIVE`, or extend budgets and re-run the topics §21.12 flags. |
| §18 is thin after a full run | The adversarial audit refuted the claims the opportunities rested on | Working as intended. Read `qa/evidence-audit.json` — the refutations are the finding. |
| Every organization field says `[INTERNAL…]` | No Capability Pack / Input Sheet attached | Expected. Attach them and re-run. |
| `doctor` reports role_model_map drift | A user config predating v3 at `~/.config/vantage/default.json` | Update it, or delete it to fall back to the shipped template. |
