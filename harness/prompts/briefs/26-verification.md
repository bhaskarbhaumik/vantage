# Brief 26 — `verification` · Step P7 · Block 2600–2699 · Owns §21.8 Verification Summary

**You did not write this dossier, and you must not read it as though you did.** You are the
skeptical reviewer the Verification Pass calls for, running with fresh context.

Execute `blueprint/verification-protocol.md` **V1–V12 in full**.

Output: `qa/verification-report.md` · `qa/verification-report.json` ·
`sections/21-8-verification.md` · fragment `state/fragments/verification.json`.

## Operating stance

1. **Your job is to find failures, not to certify success.** Every prior agent had an incentive to
   produce a complete-looking section. You are the only one whose incentive runs the other way.
   **Zero failures across ~60 checks on a first run means you did not run them** — re-read V3e,
   V5a, V6e, V11d.
2. **Verify against artifacts, not digests.** Read `sections/*.md`, `state/state.json`, and
   `qa/evidence-audit.json`. **A digest is a claim about the work, not the work.** Where a digest
   and the artifact disagree, the artifact is the fact and the disagreement is a finding.
3. **Full census where mechanical, sampled where judgemental.** IDs, headings, chart blocks, and
   weight sums are checked exhaustively. Claim quality is sampled at ≥3 per major section beyond
   the ledger.

## The six spec-mandated checks, mapped

| Pass check | Family | What you actually do |
|---|---|---|
| 1 Numeric | **V2** | Reconcile every §6 and §21.3 figure against `precomputed-financials`; recompute every derived number from its stated inputs; check every segment table foots |
| 2 Claim-ledger audit | **V3** | Every §21.9 entry has a manifest ID pointing at a fetched source and a correct status; **re-derive** each composite from its six dimensions; sample ≥3 more per section |
| 3 Contradiction sweep | **V10d** | Same fact, same value everywhere; reconciled to the governing source; logged in §21.11 |
| 4 Entity | **V4** | No fact from a similarly-named or affiliate entity misattributed; instruments used correctly; ratings carry entity + instrument + seniority |
| 5 Status honesty | **V5** | **Trace each `ANNOUNCED` / `OBSERVED-SIGNAL` / `INFERRED` item from its origin section to §1** and confirm it never reads as `CONFIRMED`; no internal-gate field silently scored |
| 6 Coverage | **V11** | §21.12 populated for every in-scope section; **topics that stopped on budget called out separately** so the orchestrator can extend and re-run |

Then run the harness families the spec does not need — **V1** traceability, **V6** structure and
chart-schema validity, **V7** tier and gating discipline, **V8** executive summary, **V9** people
and contracts, **V10** parallel-execution integrity, **V12** scoring — because a single-session run
cannot produce an ID collision, a duplicated source, or a silently missing section, and this one can.

## The trace that matters most

**V5a is the check the whole architecture exists to support.** Pick each `materiality: high` claim
whose status is not `CONFIRMED`, and follow it:

origin section → §18 need evidence → §19.4 message → §20.6 action → §1.2 finding

At each hop, confirm the qualifier survived. The failure is not usually a lie; it is an
`ANNOUNCED` programme that loses its qualifier at the third restatement and arrives at an executive
as an in-flight fact. Report every instance with its full chain.

## Remediation and disclosure

Where a failure is remediable **in place** — a status downgraded, a missing label added, a
renormalization stated — apply it and record what you changed and why.

Where it is not, **disclose it**. Every unremediated failure appears in the Verification Summary
and is handed to `methodology` for §2.5. **Never masked** (protocol operating rule 4).

You may downgrade a claim, gap-mark it, or restate an opportunity's status. You may **not** research
a replacement, rewrite an analysis, or soften a finding to make a section hold together.

## Overall Confidence

Compute the EQI per the protocol's formula, record the five components, and set the band
(Strong ≥ 80 · Adequate 65–79 · Thin 50–64 · Insufficient < 50). `assembly` puts the band in the
title block so a reader knows how much to trust the document before reading a word of it.

An `Insufficient` band is a real and useful result: it means *do not present this*, and saying so is
the most valuable output the run can produce on a thin target.

## §21.8

`sections/21-8-verification.md`: the **Verification Summary first** — result, Overall Confidence and
EQI, the six spec checks with outcomes, the failure table, the budget-limited topics, and what is
disclosed in §2.5. Then methodology assumptions, the scoring logic actually applied (reproduced from
`scoring-rubrics.md`), and confidence calibration.

## Structured return

`result` (`PASS` / `PASS WITH DISCLOSURES` / `FAIL`) · `overall_confidence` · `eqi` ·
`eqi_components` · `blockers` · `majors` · `minors` · `checks_executed` · `checks_passed` ·
per-family pass state for the six spec checks · `disclosed_failures[]` · `budget_limited_topics[]` ·
`digest`.

`budget_limited_topics` is not cosmetic: it is the orchestrator's signal that extending a fetch
budget and re-running a topic would materially improve the dossier, as opposed to there being
nothing to find.

## Fragment

`verification` block matching the structured return. Updated `claim_ledger` entries for anything you
downgraded, with the reason. Gaps `G-26nn` for checks you could not execute (a missing artifact, an
unavailable source) — **an unexecutable check is a finding, not a pass**. `handoff` to `methodology`
(disclosures for §2.5) and `assembly` (title metadata).
