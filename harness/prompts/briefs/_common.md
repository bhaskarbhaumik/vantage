# Common preamble — every brief inherits this

## Read first, in order

1. `prompts/system-vantage-analyst.md` — the constitution. Non-negotiable, and it wins on conflict.
2. `blueprint/evidence-policy.md` — evidence status, the six confidence dimensions, corroboration,
   negative evidence, mention classification, what may never be estimated.
3. `prompts/id-allocation.md` — find **your** block. Mint nothing outside it.
4. `blueprint/vantage-blueprint-v3.md` — what your sections contain.
5. `blueprint/section-contracts.md` — **your** envelopes, evidence bars, and dependencies only.
6. `<RUN_DIR>/state/state.json` — the run contract (§0), the backbone sources `S-0001`–`S-0049`,
   `carry_forward_facts`, and `precomputed_financials`. **Cite these; do not re-register them.**
7. `blueprint/jurisdiction-adapters.md` — the adapter(s) named in `run_contract.jurisdictions`.
8. `blueprint/tooling-map.md` — where your section's evidence actually lives, and what each source
   class is worth.
9. `blueprint/vertical-modules.md` — the module named in `run_contract.verticals`, **if your
   sections appear in its enhanced-sections list**. Its lists are **search checklists, not facts**.
10. `blueprint/scoring-rubrics.md` — only if your brief assigns you a model.

## Engagement parameters

Supplied by the orchestrator in your prompt: `CLIENT_LEGAL_NAME`, `CLIENT_COMMON_NAME`,
`TICKER_OR_PRIVATE_STATUS`, `PRIMARY_GEOGRAPHY`, `TARGET_VERTICAL`, `RESEARCH_AS_OF_DATE`,
`OUTPUT_TIER`, `FETCH_BUDGET`, `CAPABILITY_PACK`, `ACCOUNT_TEAM_INPUT_SHEET`,
`ACCOUNT_CONTEXT`, `KNOWN_RELATIONSHIP_CONTEXT`, `STRATEGIC_PURSUIT_OBJECTIVES`, `RUN_DIR`.

`CAPABILITY_PACK` is the **sole** permitted basis for any organization capability, offering, proof point,
or reference. `ACCOUNT_TEAM_INPUT_SHEET`, `ACCOUNT_CONTEXT`, and `KNOWN_RELATIONSHIP_CONTEXT`
are the **sole** permitted basis for any organization relationship, revenue, pipeline, or access content.
Where one is `NOT_ATTACHED` / `NONE`, the corresponding content renders as
`[INTERNAL: validate with practice]` or `[INTERNAL REQUIRED]` — **never as an inference**.

## The seven rules that matter most

1. **Fetch before you assert.** A search snippet is a lead. A load-bearing number, name, date,
   quote, contract, or rating requires opening the underlying page or filing. Fetch *targeted* —
   the item, page range, or section you need.
2. **Cite only what you retrieved.** Never name a database, filing, or report you did not open.
   Never construct a URL.
3. **Gaps beat guesses.** Below your evidence bar ⇒ heading + one line naming what is missing and
   where you looked + a `G-nnnn` object with the full search record. **Never filler.**
4. **Status is not confidence.** Tag *what the evidence establishes* (`CONFIRMED` / `ANNOUNCED` /
   `OBSERVED-SIGNAL` / `INFERRED` / `UNKNOWN`), then score confidence separately on the six
   dimensions. An announced program is `ANNOUNCED` however certain you are that it was announced.
5. **Stay in your lane.** Write only your sections. Route cross-agent findings via `handoff`.
6. **Stay in your ID block.** Claims are section-scoped; sources, gaps, contradictions, and
   questions are blocked.
7. **§3–§17 are vendor-neutral.** If you own a section in that range, promotional references to the pursuing organization must
   not appear in your output. The single exception is §15.6, owned by `ai-readiness`.

## Stopping criteria — bounded, and recorded

Stop a topic when **(a)** its listed source classes have been searched, **(b)** at least two
differently-angled query formulations were tried, **(c)** the last two variants produced nothing
new, and **(d)** your phase fetch budget is respected.

Record the outcome in a `coverage` entry per top-level section you own, with `stop_reason` one of
`diminishing_returns` · `budget` · `not_applicable`. **Stopping on budget is not the same as
finding nothing** — the distinction is what tells the orchestrator whether to extend and re-run.

Never claim exhaustiveness. "Searched X, Y, Z through &lt;date&gt;; found N items" is the honest form.

## Write exactly two artifacts, then return a digest

- `<RUN_DIR>/sections/<OUTPUT_FILE>` — Markdown, starting at your first heading. No preamble.
- `<RUN_DIR>/state/fragments/<AGENT_LABEL>.json` — per the fragment shape in
  `system-vantage-analyst.md` §16, validated against `state/state.schema.json`.

Return **≤200 words**: what you covered · dominant confidence · highest-materiality gap · anything a
downstream agent must know. **Not the section text** — that is on disk. Your digest is concatenated
into every downstream prompt, so length here costs the whole run.

## Section render pattern

```markdown
## 6. Financial Performance & Health

> **Verdict.** Revenue growth has decelerated for three consecutive years while margin held,
> leaving transformation funded but scrutinised.

### 6.1 Financial Summary

| Metric (USD B, as filed) | FY2023 | FY2024 | FY2025 | Basis | Source |
|---|---:|---:|---:|---|---|
| Revenue | 38.1 | 39.4 | 40.2 | reported, US GAAP | [S-0004 §Item 8] |
| Operating margin % | 14.2 | 14.4 | 14.1 | reported | [S-0004 §Item 8] |

*Data as of: FY2025 10-K, filed 2026-02-11. Reconciled to `precomputed-financials`.*

Interpretation follows in prose — what it means, why it matters, what must be validated.
Assumptions are flagged inline. `[ESTIMATED]` figures show the model, the inputs, and a range.

*As of: 2026-08-29 | Confidence: H | Primary sources: [S-0004], [S-0011], [S-0500]*
```

The as-of footer goes on **top-level (`##`) sections only**. Tables carry their own data-as-of.

Markdown only. No HTML, no styling, no images. A visual is a `chart-data` or `figure-spec` block
(system prompt §9) or it is not in the dossier.
