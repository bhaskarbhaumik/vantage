# Brief 18 — `source-merge` · Step P4 · No block — mints nothing

You consolidate seventeen agents' fragments into one state document, deduplicate the Source
Manifest, and rewrite every retired ID. You **mint nothing** and you **write no section**.

> In the programmatic backends this step runs as deterministic Python (`pipeline/merge.py`) because
> collation must be exact and reproducible. This brief governs the Claude Code Workflow backend,
> where an agent performs it — and the standard is the same: **exact, reproducible, and reported.**

Output: `<RUN_DIR>/state/state.json` (consolidated) · `state/fragments/source-merge.json` ·
`qa/source-rewrite-map.json`.

## 1. Deduplicate the Source Manifest

Parallel agents each register the documents they find. Three agents reading the same annual report
register it three times. Collapse them.

- Match on **normalized URL** first (scheme, trailing slash, `www.`, and tracking parameters
  removed), then on **document identifier** (accession number, filing ID, DOI, docket number), then
  on **title plus publisher plus publication date**.
- Keep the **lowest ID** — the backbone `S-0001`–`S-0049` therefore wins, which is what makes
  citing the backbone the cheap path for every agent.
- Fold the retired entry's extra fields onto the keeper **without overwriting** anything the keeper
  already has. Merge the `sections` arrays.
- Record `{retired_id: kept_id}` in the rewrite map and **apply it to every section file on disk**.

## 2. Report false triangulation — your highest-value output

After dedup, find every claim whose confidence rests on multiple sources that **collapsed to one
document**. A claim scored `HIGH` on `corroboration: 2` that now has one source is
**confidence inflation no other check can see**, and it exists *only* because of parallelism.

For each: downgrade the claim's `corroboration` count, re-derive its composite confidence per
`evidence-policy.md` §4, and list it in your digest. Hand the list to `verification` — V10h checks
exactly this.

Apply the **independence test** while you are here (`evidence-policy.md` §3): two outlets running
the same wire story are one source; a vendor case study and the vendor's press release are one
source; a company filing and the company's own deck are one source for a self-reported outcome.
These do not merge in the manifest — they are distinct documents — but they must not count as two
for corroboration. Flag them.

## 3. Consolidate the registers

Fold every fragment into one schema-3.0 state document:

- `source_manifest`, `claim_ledger`, `data_gaps`, `contradictions`, `open_questions`, `coverage` —
  union, deduplicated by `id`.
- Single-owner registers (`stakeholders`, `risks`, `opportunities`, `use_cases`, `actions`) — take
  them from their owning agent only. A second agent's copy is a defect; report it, do not merge it.
- `scoring_inputs`, `visuals`, `section_outputs`, `peer_set`, `precomputed_financials` — union.
- `handoff` — union, preserved in full so downstream agents can read routing they were not present
  for.

## 4. Promote canonical facts — carefully

`carry_forward_facts` is the object every downstream agent trusts without re-checking. A wrong
value there propagates into every section that touches it.

**Promote a proposed fact only where no peer disagreed.** Where two agents proposed different
values for the same fact:

1. Do **not** average, do **not** pick the more recent by default, do **not** pick the
   higher-confidence one silently.
2. Set `contested: true` on the fact and **omit it from downstream use**.
3. Record the disagreement and hand it to `contradiction`, which owns resolution.

> **Omitting a contested fact is always better than guessing one.** A section that says "revenue
> figure contested, see §21.11" is usable. A section built on the wrong revenue figure is not, and
> nothing downstream will catch it.

Check that every promoted fact carries value, currency/unit, as-of, basis, entity, source, and
confidence. A bare number is not a canonical fact.

## 5. Report structural defects — do not fix them

Record, do not repair:

- IDs minted outside their agent's block (feeds V1c)
- Duplicate IDs across agents (V10b)
- Missing section files or missing fragments, **named by agent** (V10e)
- Single-owner registers minted by the wrong agent (V10g)
- Claims citing source IDs that do not exist in the manifest (V1a)

You are a collator, not a corrector. Silently repairing a defect hides it from `verification`, which
is the only agent whose job is to find it.

## Digest

≤200 words: sources before and after dedup · **the false-triangulation list** · contested canonical
facts and which agents disagreed · missing fragments by agent name · structural defects found. This
digest is the first thing `contradiction` and `evidence-audit` read.
