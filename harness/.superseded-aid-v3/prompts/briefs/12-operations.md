# Brief 12 — `operations` · Wave B (← §5) · Block 1200–1299 · Owns §7 Operations & Value Chain

You describe **how the work actually gets done, and where it hurts**. §7.5 is the origin of most
§18 opportunities and §15.3 use cases: a use case with no §7.5 anchor is filler and gets deleted
downstream, so the quality of your pain-point register determines the quality of the pursuit
sections.

Read `business-model`'s §5 output before you start — cost pools (§5.6) and supply chain (§5.8) are
your inputs, not your subject.

Output: `sections/07-operations.md` · fragment `state/fragments/operations.json`.

## §7.1 Operating Model Overview

How inputs become delivered value: the operating structure, the make-versus-buy posture, the
degree of centralization. `F-7.1`.

## §7.2 Core Business Processes

5–7 **end-to-end** processes, named the way this industry names them — order-to-cash,
procure-to-pay, hire-to-retire, record-to-report, plan-to-produce, claims, servicing,
quote-to-cash. `T-7.2` + `F-7.2`.

Per process: pain level and automation potential, **each evidence-tagged**. An automation-potential
score with no evidence behind it is a guess dressed as an assessment — mark it `INFERRED` with the
trail, or `n/e`.

## §7.3 Supply Chain & Fulfillment

Physical and logical flow, supplier and facility evidence from trade and open-supply data where
available. Facility-level data (Open Supply Hub, trade records) is `OBSERVED-SIGNAL` unless the
company confirms it.

## §7.4 Shared Services & Back Office — the deal-shape predictor

Outsourcing status, **named providers where evidenced**, GCC and captive-centre footprint, prior
SI transitions, insourcing moves, managed-service posture, procurement's stated
vendor-consolidation stance.

> **This is the strongest single predictor of deal shape in the dossier.** §19.8's commercial
> construct derives from it. A company with three mature GCCs and a stated insourcing agenda buys
> very differently from one that has never run a captive. Do not thin this section — and where
> evidence is absent, say precisely what you searched, because the absence changes §19.8's
> confidence, not just its content.

`corporate` mapped the GCC footprint geographically in §3.4; take it via `handoff` and add the
functional and sourcing read.

## §7.5 Operational Pain Points & Bottlenecks — the opportunity origin

Top 7, **ranked**, each tied to a cited claim with an evidence status. `T-7.5` + `C-7.5`.

Per pain point: process · function · severity · evidence · automation/AI relevance
(**neutral flag, no the pursuing organization**).

Where does the evidence come from? Executive statements about operational difficulty ·
earnings-call operational commentary · incident and quality disclosures · regulator complaint data ·
analyst and trade-press observation · hiring for explicitly remedial roles.

**Rank honestly.** Three well-evidenced pain points beat seven where four are inferred from
industry-typical friction. `ai-readiness` and `opportunity` both cite this register by claim ID; a
weak entry here becomes a weak opportunity, then a weak action, then a weak line in the executive
brief.

## §7.6 Product Quality, Service Reliability & Complaint Signals

Outage history from public status pages · recalls · regulator complaint databases (CFPB, openFDA,
NHTSA and equivalents) · app and service incidents · remediation.

**Sample sizes and windows stated** for every signal. "1,240 CFPB complaints in the 12 months to
2026-06, of which 61% concern account servicing" is evidence; "customers complain about servicing"
is not. **Empty is a valid render.**

## Traps

- **Do not describe a generic industry process model.** If you cannot evidence how *this* company
  runs order-to-cash, the honest output is the process list with a gap on the specifics.
- **A vendor's case study describing a process improvement is self-reported by both parties.**
- **Status-page history is real evidence and is under-used** — it is one of the few places where
  operational reliability is publicly observable over time.
- **Do not convert a pain point into a solution.** §7.5 is vendor-neutral; the automation relevance
  flag names the capability class, not a provider.
- **Complaint volume scales with customer count.** Normalize or state that you did not.

## Fragment

Claims `C-7.1-nn` … `C-7.6-nn`. Sources `S-12nn`. Gaps `G-12nn`. Coverage for §7 including which
complaint and reliability databases you reached. Figures `F-7.1`, `F-7.2`; chart `C-7.5`.
`handoff` to: `ai-readiness` (the ranked §7.5 register — it is their anchor set for §15.3),
`opportunity` (same, for §18.3), `account-strategy` (the §7.4 sourcing posture for §19.8),
`vendors` (named incumbent providers you evidenced).
