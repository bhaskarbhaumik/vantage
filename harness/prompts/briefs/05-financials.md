# Brief 05 — `financials` · Wave A · Block 0500–0599 · Owns §6 Financial Performance & Health

You answer one question the rest of the dossier assumes: **can this company fund a transformation,
and under what pressure?** Every number you write is checked against the `precomputed-financials`
block, and every derived number is recomputed by the Verification Pass.

Output: `sections/06-financials.md` · fragment `state/fragments/financials.json`.

## Rule zero — reconcile, do not re-derive

Read `state/precomputed-financials.json` first.

- **Attached** → it is the numeric source of truth. Reconcile the filing against it. A discrepancy
  is **reported in place and handed off to `contradiction`** — never silently corrected, never
  averaged (V2a, BLOCKER).
- **`unavailable_reason` set** → XBRL was not available. You recompute from the stated filing
  figures **with the inputs shown**, and you say in your section that the deterministic block was
  unavailable, so the reader knows the arithmetic is yours.

Apply the **normalization policy** throughout (`system-vantage-analyst.md` §3.8): accounting basis,
restatements (use latest restated, note the restatement), continuing versus discontinued
operations, adjusted versus statutory labelling, 53-week years, ADR ratios, share-class
aggregation, splits, material pension and lease effects.

## §6.1 Financial Summary — 3–5 year trend

`T-6.1` + `C-6.1`. Currency and unit in the header; basis per column.

## §6.2 Income Statement Analysis

**6.2.1** Revenue growth: YoY, CAGR, and the **organic/inorganic split** — which requires the
acquisition contribution the company discloses, or it is `INFERRED` with the method shown.
**6.2.2** Profitability and margins versus peers — using the **§11.0 peer set only**. If
`competition` has not published §11.0 yet (it runs in Wave B), compare against the target's own
history and hand the peer comparison to them via `handoff` rather than inventing a peer set.
**6.2.3** OpEx breakdown.

## §6.3 Balance Sheet, Leverage & Obligations

Debt structure **by issuing entity** — read §3.6 from `corporate`'s section, and attach each
instrument to its issuer (V4e). Covenants where disclosed, maturity wall, pensions, leases,
off-balance-sheet items and non-consolidated JVs.

## §6.4 Cash Flow

`C-6.4` as a waterfall. Operating, investing, financing, and the free-cash-flow definition you used.

## §6.5 Capital Allocation

**Stated framework (quoted) versus revealed behaviour.** Both, or say which is missing. The gap
between what management says it prioritises and where the cash actually went is one of the most
decision-relevant findings this dossier can produce.

## §6.6 IT & Technology Spending

Reported where disclosed. Otherwise `[ESTIMATED]` with **the model, the inputs, and a range**
(V2h) — for example, sector IT-spend-to-revenue benchmarks applied to disclosed revenue, with the
benchmark source named and the range stated. **Gap-tolerant by design**: most companies do not
disclose this, and an honest gap here is more useful than a confident number, because §18 sizing
will lean on it.

## §6.7 Market Valuation & Investor Signals

Multiples versus peers, **date-stamped**, short interest, ownership shifts.
**Private branch**: substitute funding and debt history, last-round terms and date, and any
disclosed valuation — with the confidence ceiling at `MEDIUM` on anything unverifiable.

## §6.8 Credit Ratings & Analyst Consensus

Per rating: **rated entity · instrument · seniority · agency · outlook · action date** (V4d). A
rating attaches to a specific obligor and instrument; "the company is BBB+" is usually wrong.
Consensus distribution plus the bull and bear theses, attributed.

## §6.9 DuPont & Quality of Earnings

Where applicable. For banks, insurers, and REITs, **use sector metrics** — NIM, combined ratio, FFO,
book value per share — and mark the general framework `NOT RELIABLY ASSESSABLE` with the reason
rather than forcing it (V2g). Flag one-offs, restatements, auditor changes, and revenue-recognition
matters.

## §6.10 Guidance Credibility & Earnings-Surprise History

Guidance versus actuals across recent periods, estimate revisions, and what that implies about
management credibility. **Empty is a valid render** for a company that does not guide.

## Traps

- **Every derived number will be recomputed (V2b).** Show your inputs.
- **No silent FX conversion.** Show the rate and the date.
- **Do not blend vendor-normalized and as-filed data in one table** (V2e).
- **Do not attribute the parent's financials to a subsidiary target** (V4f, BLOCKER).
- **A restatement is not an error to hide.** Use the latest restated figures and note it.
- **Trailing-twelve-month is not a fiscal year.** Label the period.

## Fragment

Claims `C-6.1-nn` … `C-6.10-nn` with dimensions and entity attribution. Sources `S-05nn`. Gaps
`G-05nn`. Coverage for §6. Charts `C-6.1`, `C-6.2.1`, `C-6.2.2`, `C-6.3`, `C-6.4`, `C-6.5`, `C-6.6`.
Propose `carry_forward_facts` for revenue FY0, margin, net debt, FCF, market cap — **each with
currency, unit, as-of, basis, and entity**. `handoff` to `contradiction` (every discrepancy against
`precomputed-financials`), `competition` (your normalized figures for peer work), `opportunity`
(the IT-spend estimate and its range).
