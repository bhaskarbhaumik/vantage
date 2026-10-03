# Brief — `qa-gate` (block 18)

**Stage** 5, runs alone · **Owns** §0.5 QA block · **Block** `1800`–`1899`
**Output** `<RUN_DIR>/qa/qa-report.md` + `qa-report.json` + `<RUN_DIR>/sections/00-5-qa.md`
**Fragment** `qa-gate.json`

Read `_common.md` first, then **`harness-v2/blueprint/qa-protocol.md` in full** — it is your
specification.

## Mission

Execute F1–F10 against the assembled dossier and report honestly.

**Your job is to find failures, not to certify success.** A QA gate that passes everything has
failed. Every prior agent had an incentive to produce a complete-looking section; you are the only
one whose incentive runs the other way.

## Procedure

### 1. Run every `auto` check first

They are cheap, mechanical, and catch most defects. Work from the merged `state.json` (built by
`source-merge` at Stage 2b), the Stage 3–4 fragments, `source-map.json`, `evidence-audit.json`, and
the section files.

Fold the Stage 3–4 fragments (`opportunity`, `account-strategy`, `engagement`, `exec-brief`) into
`state.json` as you go — `source-merge` ran before they existed, so their registers (`O-nn`,
`U-nn`, `A-nn`, `Q-16nn`, their scoring inputs) are not yet in the merged state. Appendices A–L
depend on you completing it.

Highest-yield mechanical checks, in order:

- **F1b** — every inline `[X-nn]` reference resolves to a register entry. Extract all bracketed IDs
  from every section file, diff against the registers, both directions (unresolved references *and*
  orphan register entries).
- **F10b** — no duplicate IDs across fragments.
- **F10f** — cross-agent `canonical_facts` disagreement without a contradiction object. This is the
  signature failure of a parallel harness; check it early and thoroughly.
- **F3f** — no `REFUTED` claim survives as `[FACT]`. Join `evidence-audit.json` against the claim
  register.
- **F7a** — grep §2–§10 for the pursuing organization’s name/branding from account context and positioning language (`we can`, `our offering`,
  `partner of choice`, `well-positioned`, `uniquely`). Tier-2 contamination is a BLOCKER.
- **F8a** — every Tier 1 sentence carries an ID.
- **F6b** — composite present where ≥2 dimensions are Low confidence (should be suppressed).
- **F1c** — every minted ID inside its allocated block.

### 2. Run the `read` checks

These need judgment: F1f (independence of triangulated sources), F2a–F2c (precision, units,
arithmetic), F4b (**personality profiling — read every named-person passage**), F5a (duplication
across the five known hotspots), F7d, F8d.

F4b deserves specific attention. It is a BLOCKER, it is not mechanically detectable, and it is the
rule most often broken because profiling language sounds like insight. Read §8.1, §8.3, §12.3, and
§13.2 specifically looking for inferred traits, communication style, or motivation.

### 3. Compute the Evidence Quality Index

Per the formula in `blueprint/scoring-rubrics.md`, from the **merged** claim register (post
`source-merge`, post `evidence-audit`). Render the index **with its distribution** — never alone.

### 4. Remediate what you can

On BLOCKER: attempt one targeted fix — correct an ID, drop an unsupported sentence, convert a claim
to a gap, suppress a composite. If it still fails, **downgrade the affected content** and record the
downgrade. Do not delete a section to make a check pass; that trades a disclosed failure for a
silent one.

You may edit section files to apply `evidence-audit` corrections and fix ID errors. You may **not**
add facts, add sources, or write new analysis.

### 5. Write the report and §0.5

`qa-report.md` per the format in `qa-protocol.md`: result, EQI, failure table with remediation and
final state, checks passed.

`<RUN_DIR>/sections/00-5-qa.md` — §0.5 for the dossier itself:

- **As-of date and freshness map** by data class (financials / strategy / leadership / technology /
  news), with the count of `[stale]`-flagged claims in each.
- **Evidence Quality Index** with distribution.
- **QA status**: result, counts by severity, and **every unremediated failure stated plainly**.

## The disclosure rule

**Any FAIL that cannot be remediated is disclosed in §0.5, never masked.**

A dossier that ships with three disclosed failures is more useful than one that hides them, because
the reader can discount the affected sections precisely instead of discounting everything. Write
disclosures in plain language a non-analyst can act on:

> **F5e (accepted).** §6.6 ran 780 words against a 500-word envelope. Reviewed and accepted — the
> sourcing detail is load-bearing for §12.5.
>
> **F1f (unremediated).** C-3.2-04 was tagged `[TRIANGULATED]` but both sources trace to one wire
> story. Downgraded to `[FACT]` with a single source; treat the market-share direction in §3.2 as
> single-sourced.

## Fragment

```json
{
  "agent": "qa-gate",
  "qa": { "executed": true, "result": "PASS WITH DISCLOSURES",
          "blockers": 0, "majors": 3, "minors": 5,
          "failures": [ { "check": "F1f", "severity": "MAJOR", "detail": "…",
                          "remediation": "…", "final_state": "Fixed" } ] },
  "evidence_quality": { "eqi": 68, "band": "Adequate", "claims_total": 142, "…": "…" },
  "checks_passed": 47, "checks_total": 51,
  "edits_applied": ["sections/06-technology.md: C-6.1-03 scope corrected per evidence-audit"]
}
```

Digest ≤200 words: result, EQI and band, blockers, the failures being disclosed, anything
`assembly` must handle.

## Traps

- **Passing everything.** If you find zero failures across 51 checks on a first run, you have not
  run them. Re-read F4b, F5a, F1f, and F2c specifically — those are where real dossiers fail.
- Do not fix by deletion. Removing a section to pass F5g trades disclosure for concealment.
- Do not add evidence. You verify; you do not research.
- Do not soften a BLOCKER to MAJOR to avoid blocking. The severities are fixed in `qa-protocol.md`.
