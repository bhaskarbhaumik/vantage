# Brief — `source-merge` (no block — mints nothing)

**Stage** 2b — runs **after** `contradiction` and `evidence-audit`, so it can merge their output too
**Owns** nothing · **Output** `<RUN_DIR>/state/source-map.json` + `<RUN_DIR>/state/state.json` (merged)
**Fragment** `source-merge.json`

Read `_common.md` first.

## Mission — two jobs

**Job 1: deduplicate sources.** Ten agents researched concurrently. Several found the same 10-K,
the same Reuters article, the same investor deck — and each registered it under their own block.
The merged Source Register therefore contains duplicates pointing at one document, which breaks
Appendix A, inflates the apparent evidence base, and lets a claim look `[TRIANGULATED]` when both
its "independent" sources are the same article (QA F1f).

**Job 2: merge the state.** You are the first agent to run after every fragment-producing agent has
finished, so you build the consolidated `<RUN_DIR>/state/state.json` that Stages 3–6 read. See §7.

**You mint no new IDs** and you do no research.

## Procedure

### 1. Load every fragment

Read all of `<RUN_DIR>/state/fragments/*.json`. Collect every `sources[]` entry.

### 2. Identify duplicates

Two entries are the same document when any of these holds:

- Identical URL, or URLs differing only by tracking parameters, protocol, `www.`, or trailing slash.
- Same publisher + same publication date + substantially the same title.
- Both are the same filing (same company, same form type, same period) regardless of where retrieved
  — an SEC EDGAR 10-K and the same 10-K from the company IR site are **one document**.
- Both are syndications of one wire story (Reuters/AP original vs. a republishing outlet). Keep the
  **originating** publisher.

Two entries are **not** duplicates when they are different filings of the same type from different
periods, or genuinely independent coverage of one event by two outlets. Getting this wrong in the
merge direction destroys real triangulation, so when uncertain, **keep both** and note it.

### 3. Choose the survivor

Precedence: lowest tier number (T1 beats T2) → `access_basis: direct` beats `secondary-summary` →
lowest `S-` number → earliest `accessed` date. Shared-core IDs (`S-001`–`S-049`) **always** survive
against a later re-registration (QA F10d).

### 4. Emit the map

`<RUN_DIR>/state/source-map.json`:

```json
{
  "canonical": [ { "id": "S-004", "tier": "T1", "title": "FY2026 Form 10-K", "…": "…" } ],
  "rewrites":  { "S-208": "S-004", "S-411": "S-004", "S-703": "S-152" },
  "retired":   ["S-208", "S-411", "S-703"],
  "kept_despite_similarity": [
    { "ids": ["S-215", "S-508"], "reason": "Reuters original and FT independent reporting of the same event — not syndication" }
  ],
  "stats": { "registered_total": 187, "canonical_total": 154, "duplicates_retired": 33 }
}
```

### 5. Apply the rewrites

Edit every file in `<RUN_DIR>/sections/` and every fragment, replacing each retired ID with its
survivor. Use exact-match replacement on the bracketed form (`[S-208]` → `[S-004]`) so you cannot
corrupt unrelated text. Verify no retired ID survives anywhere.

### 6. Flag broken triangulation

Any claim tagged `[TRIANGULATED]` whose sources collapse to a single canonical ID after rewriting
is no longer triangulated. Record these in your fragment as `triangulation_broken[]` with the claim
IDs. `qa-gate` fails F1f on them and they must be downgraded to `[FACT]` (single source) or
re-evidenced. **This is the highest-value output of this agent** — it catches confidence inflation
that no other check can see.

### 7. Merge the state

Build `<RUN_DIR>/state/state.json` — the consolidated state every later stage reads — from
`scoping`'s initial state plus every fragment in `<RUN_DIR>/state/fragments/`. Validate against
`harness-v2/state/state.schema.json`.

Merge rules:

- **Registers** (`sources`, `claims`, `data_gaps`, `contradictions`, `open_questions`,
  `stakeholders`, `risks`, `visual_specs`, `research_log`) — concatenate, then sort by ID. IDs are
  block-partitioned, so concatenation is safe by construction. Apply your rewrite map to `sources`
  and to every `sources[]` array inside `claims`.
- **`canonical_facts`** — promote a proposed fact **only** when no peer proposed a conflicting
  value for the same key. Where `contradiction` adjudicated a conflict, use its resolved value and
  record the `X-nnn`. Where a conflict is unresolved, **omit the key** and leave the contradiction
  open — a wrong canonical fact is worse than a missing one, because downstream agents trust this
  object without re-checking.
- **`claims[].audit`** — apply `evidence-audit`'s verdicts. Where the action was `downgraded`,
  apply the corrected type and confidence. Where it was `converted-to-gap`, remove the claim and
  confirm the corresponding `G-13nn` exists.
- **`scoring_inputs`** — merge by model key; each is single-owner, so no conflict is possible.
- **`meta.stage_completed`** — set to `2`.

Report anything you could not merge cleanly in your fragment and digest. Do not invent a
resolution to make the merge succeed.

## Fragment

```json
{
  "agent": "source-merge",
  "sources": [],
  "claims": [],
  "source_map_written": true,
  "state_merged": true,
  "rewrites_applied": 33,
  "files_edited": ["sections/04-financials.md", "…"],
  "triangulation_broken": ["C-3.2-04", "C-9.1-07"],
  "kept_despite_similarity": 2,
  "canonical_facts_omitted": [ {"key": "revenue_latest_fy", "reason": "X-1203 unresolved"} ],
  "audit_actions_applied": { "downgraded": 12, "converted_to_gap": 4 },
  "self_check": { "no_retired_id_remains": true, "minted_nothing": true, "state_validates": true }
}
```

Digest ≤200 words: how many duplicates retired, which claims lost triangulation, anything the QA
gate must know.

## Traps

- **Do not merge different periods.** FY2025 and FY2026 10-Ks are two documents.
- **Do not merge an SEC filing with an article about it.** The filing is T1; the article is T3.
  Different documents, different tiers, genuine triangulation.
- Do not rewrite inside code blocks or the Appendix A table you are about to regenerate — regenerate
  it from `canonical` instead.
- You have no authority to delete claims or edit prose. You rewrite IDs and report problems.
