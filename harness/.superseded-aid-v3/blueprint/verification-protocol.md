# Verification Protocol v3.0.0 — the executable gate

> Implements the **Verification Pass** of `aid-20260829.md` ("Verify as a skeptical reviewer who
> did not write the dossier") as twelve executable check families. The spec's six mandatory checks
> map to **V2** (numeric), **V3** (claim-ledger audit), **V10d** (contradiction sweep), **V4**
> (entity), **V5** (status honesty), and **V11** (coverage). The remaining families exist because
> this is a *parallel* harness: a single-session run cannot produce an ID collision, a duplicated
> source, or a silently missing section, and this one can.
>
> Executed by the `verification` agent **with fresh context** — it did not write the dossier and
> must not read the writing agents' digests as authority. Its outcome is recorded in the
> Verification Summary at the top of §21.8 and in the title metadata.

## Operating rules

1. **Your job is to find failures, not to certify success.** Every prior agent had an incentive to
   produce a complete-looking section; you are the only one whose incentive runs the other way.
   Zero failures across ~60 checks on a first run means you did not run them.
2. **Verify against artifacts, not digests.** Read `sections/*.md`, `state/state.json`, and
   `qa/evidence-audit.json`. A digest is a claim about the work, not the work.
3. **Severity**: `BLOCKER` — the dossier must not be used until fixed or disclosed ·
   `MAJOR` — materially degrades trust · `MINOR` — cosmetic or envelope.
4. **Any failure that cannot be remediated is DISCLOSED** in the Verification Summary and in §2.5.
   **Never masked.**
5. **Sample rule**: full census where the check is mechanical (IDs, headings, blocks); **≥3
   additional claims per major section** where it is judgemental.

---

## V1 — Traceability & citation integrity

| ID | Check | Sev |
|---|---|---|
| V1a | Every inline `[S-…]` resolves to a §21.1 Source Manifest entry | BLOCKER |
| V1b | Every manifest entry carries all eleven fields: id · title · publisher · doc/accession id (where applicable) · pub date · access date · URL · language · retrieval status · reliability tier · sections fed | MAJOR |
| V1c | Every minted ID falls inside the minting agent's `id-allocation.md` block | BLOCKER |
| V1d | No constructed or guessed URL — every URL was fetched or returned verbatim by a search tool | BLOCKER |
| V1e | Long sources carry a **pinpoint locator** (`§Item 1A`, `p.34`, heading, timestamp) wherever a specific fact is drawn | MAJOR |
| V1f | No claim is `HIGH` on two sources that fail the independence test (same wire story, vendor PR + vendor case study, company filing + company deck) | MAJOR |
| V1g | Every `C-` claim in the body appears in the merged claim ledger, and vice versa for `materiality: high` | MAJOR |
| V1h | Failed retrievals (`paywall`/`blocked`/`dead`/`parse_error`) are **present** in the manifest with the alternative attempted, not dropped | MAJOR |

## V2 — Numeric integrity *(spec check 1)*

| ID | Check | Sev |
|---|---|---|
| V2a | Where `precomputed-financials` is attached, **every** §6 and §21.3 figure reconciles to it; discrepancies are **reported, not silently corrected** | BLOCKER |
| V2b | Every derived number (sum, YoY %, margin, CAGR, weighted score) recomputes from its stated inputs | BLOCKER |
| V2c | Segment and geography tables **foot to the reported total** (± rounding, noted) | MAJOR |
| V2d | Currency and unit in every table header; no silent FX conversion — rates and FY mapping shown | MAJOR |
| V2e | Adjusted vs statutory labelled per column; vendor-normalized and as-filed never share an unlabelled table | MAJOR |
| V2f | Accounting basis stated; restatements, continuing/discontinued split, 53-week years, ADR ratios, share-class aggregation noted where they affect a number | MAJOR |
| V2g | Sector-appropriate metrics used for banks/insurers/REITs; forced DuPont/EBITDA is `NOT RELIABLY ASSESSABLE` instead | MAJOR |
| V2h | Every `[ESTIMATED]` figure shows model **and** inputs **and** a range | BLOCKER |

## V3 — Evidence integrity & claim-ledger audit *(spec check 2)*

| ID | Check | Sev |
|---|---|---|
| V3a | Every §21.9 ledger entry has a manifest ID pointing at a source with `retrieval_status` `ok` or `partial` | BLOCKER |
| V3b | Every ledger entry's evidence status is correct for its evidence — re-derive it, do not trust it | BLOCKER |
| V3c | Every ledger entry's composite confidence re-derives from its six recorded dimensions | MAJOR |
| V3d | Consequential non-financial claims at `HIGH` have `ind×2` after the independence test; else downgraded to `MEDIUM` | MAJOR |
| V3e | Sample **≥3 additional claims per major section** beyond the ledger; failures downgrade or gap-mark | MAJOR |
| V3f | **No `O-nn` cites a claim that `evidence-audit` marked REFUTED as its need evidence** | BLOCKER |
| V3g | Every `[SNIPPET-ONLY]` claim is `LOW` and anchors no recommendation alone | MAJOR |
| V3h | Every gap object carries the full negative-evidence record: searched · queries tried · languages · date range · best available · resolution path | MAJOR |
| V3i | `structurally-inapplicable` fields are marked as such, not as gaps, and match the §0 ownership form | MINOR |

## V4 — Entity discipline *(spec check 4)*

| ID | Check | Sev |
|---|---|---|
| V4a | No fact from a similarly-named or affiliate entity is misattributed to the target | BLOCKER |
| V4b | Every entity named in the dossier resolves against the §3.6 Entity & Securities Map | MAJOR |
| V4c | Ownership instruments used correctly: proxy tables and 13D/G for beneficial ownership, Forms 3/4/5 for insiders, **13F labelled as holdings OF an institutional manager** | BLOCKER |
| V4d | Every credit rating carries rated entity + instrument + seniority | MAJOR |
| V4e | Debt, litigation, and regulatory obligations attributed to the **issuing/obligated** entity, not the group by default | MAJOR |
| V4f | For controlled subsidiaries, parent financials are not presented as the target's | BLOCKER |

## V5 — Status honesty *(spec check 5)*

| ID | Check | Sev |
|---|---|---|
| V5a | **No `ANNOUNCED`, `OBSERVED-SIGNAL`, or `INFERRED` item reads as `CONFIRMED` anywhere downstream** — trace each one from its origin section to §1 | BLOCKER |
| V5b | No internal-gate field is silently scored: win probability, account revenue, relationship strength, stakeholder access | BLOCKER |
| V5c | §1.6 "Stakeholder Access" is `NOT ASSESSED` **with the renormalization shown** whenever the Input Sheet is absent | BLOCKER |
| V5d | Company outcome claims (savings, share, success, implementation status) are `ANNOUNCED` or `MEDIUM` unless independently corroborated | MAJOR |
| V5e | Every technology entry carries a mention classification; nothing is `CURRENTLY-USED` on a job posting alone | MAJOR |
| V5f | Every `[INFERRED]` / `[ESTIMATED]` label survives into every downstream restatement | BLOCKER |
| V5g | No "compliant" assertion without regulator or company evidence | MAJOR |

## V6 — Structure, format & visual schema

| ID | Check | Sev |
|---|---|---|
| V6a | Heading hierarchy exactly matches the blueprint numbering; no section silently merged or dropped | BLOCKER |
| V6b | Every section opens with a **one-sentence analytical verdict** | MAJOR |
| V6c | Every `##` section carries the as-of footer; every material table carries its own data-as-of | MAJOR |
| V6d | No bullet-only section — consultative prose plus tables | MINOR |
| V6e | Every `chart-data` / `figure-spec` block parses as JSON and validates against schema v1 (required keys, id matching its section, `null` for unavailable points) | MAJOR |
| V6f | No table omitted for lack of data — `[DATA UNAVAILABLE]` per cell instead | MAJOR |
| V6g | Markdown only: no HTML, no styling, no embedded images | MINOR |
| V6h | Section envelopes within +50% of `section-contracts.md`, or the overrun is disclosed | MINOR |

## V7 — Strategy, tier & gating discipline

| ID | Check | Sev |
|---|---|---|
| V7a | **Promotional references to the pursuing organization do not appear in §3–§17** other than §15.6 | BLOCKER |
| V7b | Every organization capability, offering, proof point, or reference is `[CAPABILITY-PACK]`-cited or `[INTERNAL: validate with practice]` — **no invented references, client names, or quantified outcomes** | BLOCKER |
| V7c | Every §19 premise footnotes to an evidencing body section | MAJOR |
| V7d | Every §19.4 messaging theme maps to a **quoted** §9.1 or §13.4 priority | MAJOR |
| V7e | **Coverage**: every `HYPOTHESIS`/`VALIDATE` opportunity and every `materiality: high` gap appears as a §20.6 action or a §19.9 validation item | MAJOR |
| V7f | §19.9 MEDDPICC has all eight fields populated — evidence or `[INTERNAL REQUIRED]`, **never blank** | MAJOR |
| V7g | §19.1 SWOT weaknesses and threats are populated — an all-strengths SWOT is a failure | MAJOR |
| V7h | §16.4 and §19.5 render only from supplied inputs, else the `[INTERNAL…]` marker | BLOCKER |

## V8 — Executive summary

| ID | Check | Sev |
|---|---|---|
| V8a | **Every §1 statement carries a `C-`/`O-`/`R-`/`A-`/`P-`/`G-` reference.** A §1 sentence with no ID is a failure | BLOCKER |
| V8b | Nothing appears in §1 that is not in the body | BLOCKER |
| V8c | `exec-brief` minted **zero** sources | MAJOR |
| V8d | §1.3 engagement thesis is consistent with the §1.6 readiness band — if the evidence says nurture, §1.3 says nurture | BLOCKER |
| V8e | §1.1 every field populated, cited, or explicitly gapped | MAJOR |
| V8f | §1.4 win-probability column is Input-Sheet-derived or `[INTERNAL REQUIRED]` throughout | BLOCKER |
| V8g | §1.2 findings each carry evidence status **and** confidence **and** an organization implication | MAJOR |

## V9 — People, vendors, contracts

| ID | Check | Sev |
|---|---|---|
| V9a | No sensitive personal data; no speculation about loyalties, motives, or working style | BLOCKER |
| V9b | Prior-vendor employment appears only as a weak `OBSERVED-SIGNAL` hypothesis, never as a predisposition | BLOCKER |
| V9c | §10.7 workforce data is aggregate only | MAJOR |
| V9d | **No estimated contract value, expiry, or renewal date anywhere** | BLOCKER |
| V9e | No undisclosed litigation exposure figure | BLOCKER |
| V9f | Quotes are verbatim with speaker, event, date, and **provenance class**; machine translations marked | MAJOR |
| V9g | Non-English sources record their original language; consequential claims keep the original excerpt | MAJOR |
| V9h | Review/sentiment signals state sample size, window, method, and known biases | MAJOR |

## V10 — Parallel-execution integrity

> These four failure modes exist only because agents run concurrently. A sequential run cannot
> produce them, so `aid-20260829.md` does not check for them — and this harness must.

| ID | Check | Sev |
|---|---|---|
| V10a | Every planned section file exists on disk | BLOCKER |
| V10b | No ID minted twice by two agents | BLOCKER |
| V10c | No duplicate source: two manifest entries for the same URL/document after `source-merge` | MAJOR |
| V10d | **Contradiction sweep** — the same fact carries the same value everywhere; conflicts reconciled to the governing source and logged in §21.11 | BLOCKER |
| V10e | **Silent data loss** — every agent in the plan produced both a section (where it owns one) and a fragment. A non-returning agent is named, not absorbed | BLOCKER |
| V10f | **Canonical-fact agreement** — no two agents report different values for a `canonical_facts` entry. *The signature failure of a parallel harness: everything built on the wrong value is wrong* | BLOCKER |
| V10g | No agent wrote outside its owned sections | MAJOR |
| V10h | No claim's `[TRIANGULATED]`-equivalent `HIGH` collapsed to a single document after source dedup | MAJOR |

## V11 — Coverage & source-completeness *(spec check 6)*

| ID | Check | Sev |
|---|---|---|
| V11a | §21.12 scorecard is populated for **every** in-scope section | MAJOR |
| V11b | Every section records `expected` source classes vs `retrieved`, and they are consistent with the §0 jurisdiction adapter | MAJOR |
| V11c | Every `stop_reason` is one of `diminishing_returns` / `budget` / `not_applicable` — and **topics that stopped on budget are called out separately** so the orchestrator can extend | MAJOR |
| V11d | The stopping criteria were actually met where `diminishing_returns` is claimed: ≥2 differently-angled query formulations, last two variants yielding nothing new | MAJOR |
| V11e | No section claims exhaustiveness ("all", "every", "complete list") without the search record supporting it | MAJOR |
| V11f | Residual risk stated for every section whose retrieved classes fall short of expected | MINOR |

## V12 — Scoring integrity

| ID | Check | Sev |
|---|---|---|
| V12a | Every scored dimension cites the evidence behind its score | MAJOR |
| V12b | Every score uses the anchored 1–5 rubric from `scoring-rubrics.md`; no unanchored judgement | MAJOR |
| V12c | Weights sum to 100%; renormalizations are shown | BLOCKER |
| V12d | Composite suppressed where ≥2 dimensions are `LOW` confidence, and the suppression is stated | MAJOR |
| V12e | `NOT RELIABLY ASSESSABLE` carries a reason, and is used rather than a forced score | MAJOR |
| V12f | Peer overlays use only comparable evidence and the §11.0 peer set | MAJOR |

---

## Overall Confidence (title metadata)

The dossier's title block carries **Overall Confidence**, computed after the pass. It is a decision
aid about the *document*, not a measurement of the *company*.

```
EQI = 100 × ( 0.30·S_evidence + 0.25·S_coverage + 0.20·S_corroboration
            + 0.15·S_recency  + 0.10·S_verification )
```

| Component | Definition |
|---|---|
| `S_evidence` | Share of material claims at `CONFIRMED` **and** `HIGH` |
| `S_coverage` | Share of in-scope sections rendered above their evidence bar |
| `S_corroboration` | Share of consequential non-financial claims meeting `ind×2` |
| `S_recency` | Share of current-state claims inside their staleness window |
| `S_verification` | Checks passed ÷ checks executed |

| Band | EQI | Meaning |
|---|---|---|
| **Strong** | ≥ 80 | Decision-grade. Use as-is. |
| **Adequate** | 65–79 | Use with the disclosed gaps in view. |
| **Thin** | 50–64 | Directional only. §18 sizing must be treated as hypothesis. |
| **Insufficient** | < 50 | **Do not present.** Re-run with better sources or reduce scope. |

`Overall Confidence` on the title page is the band; the numeric EQI and the component breakdown go
in §21.8.

---

## Report format

`verification` writes `qa/verification-report.md`, `qa/verification-report.json`, and
`sections/21-8-verification.md`.

```markdown
# Verification Summary — {{CLIENT}} AID, as of {{RESEARCH_AS_OF}}

**Result:** PASS WITH DISCLOSURES · **Overall Confidence:** Adequate (EQI 71.4)
**Checks:** 58 executed · 53 passed · 2 BLOCKER · 3 MAJOR · 0 MINOR
**Verifier context:** fresh — this agent did not write the dossier.

## Spec-mandated checks
| Pass check | Family | Outcome |
|---|---|---|
| 1 Numeric | V2 | PASS — 4 discrepancies vs precomputed-financials reported in §6.2 |
| 2 Claim-ledger audit | V3 | 2 downgrades, 1 gap-marked |
| 3 Contradiction sweep | V10d | 3 resolved, 1 open → §21.11 |
| 4 Entity check | V4 | PASS |
| 5 Status honesty | V5 | **FAIL V5a** — §1.2 finding #4 presents an ANNOUNCED program as delivered |
| 6 Coverage | V11 | 3 sections stopped on budget — listed below |

## Failures
| ID | Sev | Where | What | Remediation |
|---|---|---|---|---|
| V5a | BLOCKER | §1.2 #4 | ANNOUNCED program reads as delivered | Downgraded in place; §9.6 cross-ref added |
| V3f | BLOCKER | §18.1 O-04 | Cites C-9.2-03, REFUTED by evidence-audit | O-04 restated as HYPOTHESIS; need evidence replaced |
| V11c | MAJOR | §12.4, §17.1, §21.7 | Stopped on budget, not diminishing returns | **Disclosed** — orchestrator may extend and re-run those topics |

## Stopped on budget (not on diminishing returns)
§12.4 customer satisfaction · §17.1 ESG ratings · §21.7 digital presence

## Disclosed in §2.5
V11c (budget-limited coverage on three topics)
```

The JSON mirror carries `result`, `overall_confidence`, `eqi`, per-family counts,
`disclosed_failures[]`, and `budget_limited_topics[]` so the orchestrator can decide whether to
extend budgets and re-run.
