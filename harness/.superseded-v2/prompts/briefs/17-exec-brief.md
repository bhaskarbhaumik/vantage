# Brief — `exec-brief` (block 17)

**Stage** 4, runs alone · **Owns** §1.1–1.8, §0.4 (final), §0.6 · **Block** `1700`–`1799`
**Envelope** ~1,800 w (≤3 pages) · **Output** `<RUN_DIR>/sections/01-exec-brief.md`
**Fragment** `exec-brief.json`

Read `_common.md` first.

## Mission

Write the only part many executives will read — **last**, derived strictly from the body.

This ordering is the single most important structural decision in the whole design. v1.2 wrote the
executive summary first, which meant the brief invented conclusions the body then had to justify.
Reversing it removes the incentive to fabricate, because you cannot write a conclusion the body
does not already prove.

## The hard rule

**You perform no new research. You mint no new sources** (QA F8g).

Every Tier 1 statement carries a `C-`, `O-`, `R-`, `A-`, `P-`, or `G-` reference. A Tier 1 sentence
with no ID is a BLOCKER failure (F8a). Nothing appears in Tier 1 that is not in the body (F8b).

If you find yourself wanting to say something the body does not support, that is a signal the body
is incomplete. Record it as a `G-17nn` gap — it belongs in §1.8, which is exactly what §1.8 is for.

## Read before writing

Every file in `<RUN_DIR>/sections/` · the merged `state.json` · `<RUN_DIR>/qa/evidence-audit.json` ·
`<RUN_DIR>/state/source-map.json` · every Stage-3 handoff.

## §1.1 Account Thesis — ≤150 w

A verdict: **pursue / develop / nurture / monitor**, the 2–3 load-bearing reasons each with claim
IDs, and the single biggest uncertainty.

Must be consistent with §1.6's readiness band (QA F8d, BLOCKER). A *Monitor* band under a
"pursue aggressively" thesis is a contradiction the reader will catch immediately, and it destroys
trust in everything else. If the band and your reading of the evidence genuinely diverge, say so
explicitly and explain why — do not paper over it.

## §1.2 Company Snapshot Card — table

From `canonical_facts` only. Gap-tolerant: unknown fields render `[DATA GAP] G-nnn`, not blank and
not guessed. Private variant drops market-cap and valuation fields.

## §1.3 Top Findings & Implications — 7–10 rows

`# · Finding · Evidence (claim IDs) · Implication for pursuit · Confidence`.

Select for **decision-changing**, not for interesting. The test: would an account executive who
already knows this client learn something that changes what they do? A finding that restates the
client's public narrative fails the test, however well-sourced.

Confidence labels must match the underlying claims (F8c). Findings resting on `WEAKENED` claims
carry the downgraded confidence.

## §1.4 Opportunity Themes — top 5

From `opportunity`'s handoff, referencing `O-nn` with scores and status. Where a Model 5 composite
was suppressed, show the qualitative assessment — **do not substitute a number** to make the table
look complete.

## §1.5 Risks & Watchpoints — top 5–7

From `R-nn` and §10.5, with mitigation stance. Include the pursuit-facing risks, not only the
client's enterprise risks — the reader is deciding whether to invest pursuit budget.

## §1.6 Engagement Readiness — Model 1

Composite scorecard, or the qualitative fallback where suppression triggered. Interpretation band.
The mandatory "decision aid, not a measurement" framing.

Model 1 consumes Models 2, 3, and 6 plus §4 financials. Where those were suppressed, Model 1 will
likely suppress too — that is correct behaviour and the render should present the qualitative
assessment confidently rather than apologetically.

## §1.7 30/90/180-Day Actions

From `engagement`'s `A-nn`. Specific, sequenced, owner-role-assigned, dated, metric-bearing (F8e).

## §1.8 Material Unknowns — `NEW v2.1`

The top 3 `materiality: high` gaps from Appendix F: `G-nnn · What's missing · Why it matters ·
Resolution path · Owner · Related Q-nnn`.

**This section is the point of the whole architecture.** Everything else in this design exists to
prevent fabrication; §1.8 is where that discipline becomes visible to the person making the
decision. It also pre-empts the "why doesn't this cover X" question by answering it first.

If there are genuinely no high-materiality gaps, **say so explicitly** — "no high-materiality gaps
remain; all core sections rendered from evidence" — rather than omitting the section. Silence reads
as an oversight; the explicit statement reads as a result.

## §0.4 final · §0.6 Reader's Map

**§0.4** — take `contradiction`'s draft and finalise: add any assumption or contradiction arising
from Tier 3, and confirm every open contradiction is present with its effect on the dossier stated.

**§0.6 Reader's Map** — `NEW v2.1`. Per audience (Executive / Sales / Solution / Delivery): the
5–8 sections that matter to them and the §0.2 intelligence questions they answer. Derive from
`scoping`'s §0.2 audience tagging — it was tagged for exactly this purpose.

## Fragment duties

- `claims[]`: **empty**. `sources[]`: **empty** (F8g).
- `data_gaps[]`: `G-17nn` only where you wanted to say something the body could not support — a
  useful signal about body completeness.
- `handoff` to `qa-gate`: your ID-reference list, so F8a can be checked mechanically.

## Traps

- **Writing the brief you wish the research supported.** The commonest failure here, and the one
  the ordering was designed to prevent. If the evidence says *nurture*, write *nurture*.
- Hedging everything into uselessness. Confidence labels carry the uncertainty; the prose can then
  be direct. "Pursue, on the strength of two dated priorities [C-5.1-02, C-5.1-04] — Medium
  confidence" is better than a paragraph of qualifications.
- Exceeding three pages. This brief competes with the reader's calendar, not with the body.
- Introducing a fact, a number, or a framing that appears nowhere below.
