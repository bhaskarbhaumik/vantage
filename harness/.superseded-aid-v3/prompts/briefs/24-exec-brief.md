# Brief 24 — `exec-brief` · Step P6 · Block 2400–2499 · Owns §1 Executive Summary & Company Snapshot

**§1 is written last and placed first.** This is the single most important structural decision in
the design: an executive summary written first invents conclusions that the body then has to
justify — the exact mechanism that produces confident fabrication in long structured generation.

You perform **no new research** and **mint no sources**.

Output: `sections/01-exec-brief.md` · fragment `state/fragments/exec-brief.json`.

## The two hard rules

**1. Every §1 statement carries an ID.** A `C-` claim, an `O-` opportunity, an `R-` risk, an `A-`
action, a `P-` stakeholder, or a `G-` gap. **A §1 sentence with no ID is a BLOCKER** (V8a).

**2. Nothing appears in §1 that is not in the body** (V8b). If you want to say something the body
does not support, that is not a finding — it is a gap. Record it as `G-24nn` and surface it in §2.5
via `handoff` to `methodology`.

Minting a source is the clearest signal that you are researching rather than synthesising (V8c). If
you find yourself needing one, the body is incomplete and that is the finding.

## §1.1 Company-at-a-Glance

`T-1.1`. **Every field populated, cited `[S-id]`, or explicitly gapped** (V8e):

legal name · trade name · founded · HQ · ticker / exchange / registry IDs / LEI · CEO (since) ·
employees (as-of) · revenue (FY0, currency) · EBITDA and margin (**basis labelled**) · market cap
(date) *or* last-round valuation (private) · **credit ratings — rated entity and instrument per
rating** · industry (primary + secondary) · FY end · vertical(s) · website / IR URL.

Vertical add-ons from the module's E block: regulator (regulated industries), backlog (EPC and
A&D), AUM (asset managers), same-store sales (retail), FFO and occupancy (real estate), utilisation
(professional services).

Take every value from `carry_forward_facts`. **A fact marked `contested` is not stated** — write
"contested, see §21.11" rather than picking a side. This is the one table a reader will quote from,
so a wrong cell here travels furthest.

## §1.2 Key Findings & Strategic Highlights

`T-1.2` — # · Finding · Evidence `[S-ids]` · **Status** · **Confidence** · Implication for the pursuing organization.

7–10 findings. Selection criteria, in order: **highest materiality**, **survived
`evidence-audit`**, and **changes a decision**. A true fact that changes nothing is not a finding.

**Status and confidence are mandatory per row** (V8g), and they must match what the body says. This
is where V5a is most often failed: an `ANNOUNCED` programme, restated in a summary table, quietly
becomes a fact. Carry the status forward verbatim.

## §1.3 Strategic Relevance for the pursuing organization

The engagement thesis, from §19.2. Capabilities cited `[CAPABILITY-PACK]` or marked
`[INTERNAL: validate with practice]`. **Every target-side premise anchored to a later section.**

**§1.3 must be consistent with the §1.6 readiness band** (V8d, BLOCKER). If Model 1 lands at
"nurture", §1.3 says nurture. Writing an enthusiastic thesis over a 52/100 readiness score is the
failure this check exists to catch.

## §1.4 Top Opportunities

`T-1.4` — # · Opportunity · Evidence Basis · **Attractiveness (1–5)** · **Win Prob** · Horizon ·
Lead Practice. Top 5–8 by public attractiveness from the `O-nn` register.

**The win-probability column is Input-Sheet-derived or `[INTERNAL REQUIRED]` throughout**
(V8f, BLOCKER). Not "TBD", not blank, not an estimate.

Ranges and reasoning, never bare authoritative-looking scores.

## §1.5 Top Risks & Watchpoints

5–7 from the `R-nn` register: type, severity, likelihood, mitigation stance. Include risks to the
**pursuit** and to **delivery**, not only risks to the client — §14.7 supplies both.

## §1.6 Engagement Readiness Score

`T-1.6`. Model 1: Financial Health 20% · Digital Maturity 20% · AI Readiness 20% · Strategic
Alignment 15% · Stated Priorities Fit 15% · **Stakeholder Access 10%**.

> **Without the Account-Team Input Sheet, Stakeholder Access is `NOT ASSESSED`, the remaining five
> weights renormalize from 90% to 100%, and the renormalization is shown in-section** (V5c,
> BLOCKER). Not scored as 0. Not silently dropped.

Per-dimension evidence, and the band (Pursue / Develop / Nurture / Monitor).

## §1.7 Recommended Next Actions

5–7 from the `A-nn` register: Action · Owner Role · Deadline · Success Metric. Select for
decision-relevance, not comprehensiveness — §20.6 has the full register.

## What to do with what you cannot say

The most valuable thing you produce is often the thing the body could not establish. Where a
high-materiality gap or an open contradiction means a reader should **not** draw an obvious
conclusion, say so in §1.2 as a finding with its `G-` or `X-` reference. An executive summary that
marks its own boundaries is worth more than one that reads smoothly past them.

## Fragment

Claims: none new — you cite. Gaps `G-24nn` for anything you wanted to say and could not.
`scoring_inputs.model_1`. **Sources: zero** (V8c). `handoff` to `methodology` (your gaps belong in
§2.5) and `verification` (anything you could not reconcile between §1.6 and §1.3).
