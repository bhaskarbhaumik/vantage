# Common preamble — every brief inherits this

## Read first, in order

1. `harness-v2/prompts/system-aid-analyst.md` — the constitution. Non-negotiable.
2. `harness-v2/prompts/id-allocation.md` — find **your** block. Mint nothing outside it.
3. `harness-v2/blueprint/aid-blueprint-v2.1.md` — the section spec.
4. `harness-v2/blueprint/section-contracts.md` — envelopes, **evidence bars**, dependencies for
   your sections only.
5. `<RUN_DIR>/state/state.json` — canonical facts and the shared source register
   (`S-001`–`S-049`). **Cite these; do not re-register them.**
6. `harness-v2/blueprint/vertical-modules.md` — the module named in `meta.vertical_module`, if any.
   Remember: its lists are **search checklists, not facts**.
7. `harness-v2/blueprint/scoring-rubrics.md` — only if your brief assigns you a model.

## Engagement parameters

Supplied by the orchestrator in your prompt: `CLIENT_LEGAL_NAME`, `CLIENT_COMMON_NAME`,
`TICKER_OR_PRIVATE_STATUS`, `PRIMARY_GEOGRAPHY`, `TARGET_VERTICAL`, `RESEARCH_AS_OF_DATE`,
`REQUIRED_DEPTH`, `ACCOUNT_CONTEXT`, `KNOWN_RELATIONSHIP_CONTEXT`,
`STRATEGIC_PURSUIT_OBJECTIVES`, `RUN_DIR`.

`ACCOUNT_CONTEXT` and `KNOWN_RELATIONSHIP_CONTEXT` are the **sole** permitted basis for any
the pursuing organization-history content anywhere in the dossier. If either is `NONE`, the corresponding content
renders as "input not provided" — never as an inference.

## The five rules that matter most

1. **Cite only what you retrieved.** Never a database by name unless you actually opened it.
2. **Gaps beat guesses.** Below the evidence bar ⇒ heading + one-line gap + `G-nnn`. Never filler.
3. **Stay in your lane.** Write only your sections. Route cross-agent findings via `handoff`.
4. **Stay in your ID block.** Claims are section-scoped; everything else is blocked.
5. **Tier 2 is vendor-neutral.** If you own §2–§10, promotional references to the pursuing organization must not appear in your
   output except in a single-line neutral relevance flag.

## Stop rules

Stop a line of research when a T1–T2 source answers it, two credible sources triangulate, or
3–4 well-formed queries fail. On failure: mint a gap, log the failed queries (with
`best_source: null`), move on. Do not polish low-materiality sections.

## Write exactly two files, then return a digest

- `<RUN_DIR>/sections/<OUTPUT_FILE>` — Markdown, starting at your first heading. No preamble.
- `<RUN_DIR>/state/fragments/<AGENT_LABEL>.json` — per the fragment shape in
  `system-aid-analyst.md` §16, validated against `harness-v2/state/state.schema.json`.

Return **≤200 words**: what you covered · dominant confidence · highest-materiality gap · anything
a downstream agent must know. Not the section text — that is on disk. Your digest is concatenated
into every downstream prompt, so length here costs everyone.

## Section render pattern

```markdown
### 4.2 Financial Performance & Health

> **Verdict [Confidence: High].** Revenue growth has decelerated for three consecutive years
> while margin held, leaving transformation funded but scrutinised.

| Metric | FY2024 | FY2025 | FY2026 | Basis | Source |
|--------|-------:|-------:|-------:|-------|--------|
| Revenue (USD B) | 38.1 | 39.4 | 40.2 | reported | S-004 |

Interpretation follows in prose — what it means, why it matters, what must be validated.
Assumptions are flagged inline.
```

Markdown only. No HTML, no styling, no images. A visual goes in as a `VZ-nnn` spec or not at all.
