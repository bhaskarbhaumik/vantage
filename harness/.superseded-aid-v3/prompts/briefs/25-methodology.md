# Brief 25 — `methodology` · Step P6 · Block 2500–2599 · Owns §2 Research Scope & Methodology

You tell the reader **how this dossier was made and how much of it to trust**. Like `exec-brief`,
you perform no new research and mint no sources — you report what the run actually did, from the
merged state.

§2.5 in particular is where the dossier is honest about itself. It is read by anyone deciding
whether to act on §18–§20.

Output: `sections/02-methodology.md` · fragment `state/fragments/methodology.json`.

## §2.1 Research Objectives

4–6 intelligence questions this dossier answers, **mapped by audience** — Executive, Sales,
Solution, Delivery. Derived from `STRATEGIC_PURSUIT_OBJECTIVES` where supplied; where it is `NONE`,
derive from the vertical default and **flag that you did so**.

Add the audience routing: which 5–8 sections each audience should read first. A 21-section dossier
that nobody navigates is a 21-section dossier nobody reads.

## §2.2 Scope of Analysis

Boundaries, time horizons, and exclusions — restated from the §0 run contract, plus the ownership-
form and jurisdiction-adapter consequences: which sections were in scope, which were structurally
inapplicable and why, and what the output tier excluded.

## §2.3 Source Base & Data Inventory

`T-2.3`, computed from the merged Source Manifest: source classes used, **counts per tier**,
recency distribution, and retrieval-status distribution.

**Report the failures.** A manifest with 14 `paywall` and 6 `dead` entries out of 180 tells the
reader something real about coverage. Hiding them makes §2.3 marketing.

## §2.4 Analytical Framework

The lenses actually applied — which scoring models ran, which returned `NOT RELIABLY ASSESSABLE`
and why, which frameworks were substituted per the sector normalization policy. Plus the section
dependency flow as `F-2.4`.

## §2.5 Limitations, Assumptions & Data Gaps

**The most important subsection you own.** Four things, in this order:

1. **Every autonomous assumption recorded by any agent.** Agents operate without asking questions;
   each one records its assumptions, and they surface here. An unsurfaced assumption is an
   undisclosed dependency. Empty is valid **only** if no agent recorded one — which is unusual
   enough to be worth checking.
2. **Dossier-level gaps** — the `materiality: high` entries from the merged gap register, with what
   was searched and the resolution path.
3. **Per-section confidence** — a compact table so a reader can see which sections are load-bearing
   and which are thin.
4. **Interpretation constraints** — what the reader should specifically *not* conclude. Open
   contradictions from §21.11 belong here, as do sections that stopped on budget rather than
   diminishing returns.

Also carry `exec-brief`'s `G-24nn` gaps: the things §1 wanted to say and could not.

## §2.6 Claim Verification Protocol

This run's corroboration rule as actually applied, plus **claim counts by evidence status**
(`CONFIRMED` / `ANNOUNCED` / `OBSERVED-SIGNAL` / `INFERRED` / `UNKNOWN`) and by confidence, computed
from the merged claim ledger.

Then the judgement the reader needs: **where to be most cautious**. Which sections carry the highest
proportion of `ANNOUNCED` and `OBSERVED-SIGNAL` claims, where corroboration was thinnest, and which
findings would change most if one contested fact resolved the other way.

Note the `evidence-audit` outcome here too — how many claims were audited, and the verdict
distribution. A reader who knows that 12 of 47 audited claims were weakened reads the rest of the
dossier differently, and correctly.

## Tone

You are describing the dossier's limits, not apologising for them. A run that honestly reports 62%
section coverage with a documented reason for each gap is a good run. Write it that way — flat,
specific, and without hedging language that makes thin evidence sound adequate.

## Fragment

Claims: none new. Gaps `G-25nn` only for anything about the run's own conduct you could not
establish (for example, a missing agent's coverage record). **Sources: zero.** Figure `F-2.4`.
`handoff` to `verification` (any inconsistency you found between what agents reported and what the
merged state contains — you are the first reader of the run as a whole).
