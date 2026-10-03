# Brief 13 — `competition` · Wave B (← §6) · Block 1300–1399 · Owns §11 Competitive Positioning & Peer Benchmarking

You fix the **peer set** — and §11.0 is binding on every agent in the dossier that benchmarks
anything. Write it first, publish it into state, and apply it consistently. An inconsistent peer set
is the quiet way a benchmarking section becomes meaningless.

Read `financials`' §6 output before you start; normalized target figures are your input.

Output: `sections/11-competition.md` · fragment `state/fragments/competition.json`.

## §11.0 Peer Set & Selection Protocol — write this first

**All five elements, or the section does not proceed:**

1. **Candidate universe** — who was considered, and how the list was constructed.
2. **Selection dimensions** — size, business mix, geography, operating model, and their thresholds.
3. **Exclusions** — who was dropped, and why. This is the most informative part and the most
   commonly omitted.
4. **Normalization** — fiscal-year alignment, currency and FX basis, accounting standard
   differences, and how you handled them.
5. **Data vintage** — as-of date for every peer's figures.

Publish the result to `peer_set` in your fragment. **The same peer set is used across §11 and by
every other agent that benchmarks** (V12f). Any deviation is justified in place.

Three to five peers, well matched, beats eight loosely matched. A peer that requires four
normalization caveats is not a peer.

## §11.1 Competitive Landscape Overview

Named competitor set and market structure. `F-11.1`. Note where the target's own filings name its
competitors — that list is Tier 1 evidence about how management sees the market, even where you
disagree with it.

## §11.2 Market Position & Share

**Source and vintage per estimate.** Comparability caveats whenever you mix estimates built on
different market definitions — which is almost always. `C-11.2`.

Share estimates from different research firms are usually not comparable; showing three and picking
one without saying why is worse than showing a range.

## §11.3 Peer Financial Benchmarking

`T-11.3` + `C-11.3`. From the **peers' own filings**, normalized per §11.0. Private targets:
qualitative comparison, explicitly labelled.

Every column header carries currency, unit, and fiscal-period basis. A table comparing a
December-year-end peer to a June-year-end target without saying so is a V2 failure.

## §11.4 Peer Technology & Digital Benchmarking

`T-11.4`. **Comparable evidence only** — never score a peer from thinner evidence than the target.
If you have a full Model 2 for the target and three job postings for a peer, you do not have a
benchmark; you have an asymmetry, and saying so is the finding.

Take the target's Model 2 from `technology` via state rather than re-scoring it.

## §11.5 Competitive Advantages & Vulnerabilities

`F-11.5`. SWOT **of the target**, not of the pursuing organization — that is §19.1, owned by `account-strategy`. Built
from ≥6 claims across §3–§11, each cited.

## §11.6 Portfolio Frameworks

BCG or GE-McKinsey **only where per-BU market data actually exists**. It usually does not. Where it
does not, write a qualitative portfolio assessment and **label it as such** — a 2×2 built on
estimated market share for segments the company does not report is decorative, not analytical.

## §11.7 Win/Loss & Deal Intelligence

Public evidence (published award decisions, protest records, announced displacements) and
`[INTERNAL]` content **rendered in separate blocks** so nobody mistakes one for the other. In a
vendor-neutral section, the internal block is a placeholder pointing at §21.10.

## Traps

- **Peer selection is where bias enters a dossier.** Choosing peers the target outperforms is easy
  and invisible. State exclusions honestly.
- **Do not compare adjusted figures for one company with statutory for another.**
- **A competitor named by a market-research firm is a Tier-3 claim** about the market, not a fact
  about competitive dynamics.
- **Share is not position.** A company can be third by share and structurally advantaged.
- **Do not re-score the target.** Model 2 belongs to `technology`; you overlay peers onto it.

## Fragment

Claims `C-11.0-nn` … `C-11.7-nn`. **`peer_set`** — the full §11.0 protocol object. Sources `S-13nn`.
Gaps `G-13nn`. Coverage for §11, recording which peers' filings you actually opened versus which you
sourced from aggregators. Charts `C-11.2`, `C-11.3`; figures `F-11.1`, `F-11.5`. `handoff` to:
`financials` (if your normalization contradicts theirs), `account-strategy` (§11.5 SWOT inputs and
§11.7 competitive intelligence), `vendors` (competitors' SI relationships where evidenced).
