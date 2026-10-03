# Brief 15 — `ai-readiness` · Wave B (← §8) · Block 1500–1599 · Owns §15 · Mints `U-nn`

You produce the AI readiness assessment and the **use-case backlog `U-nn`** that §18 builds on. You
also own **§15.6, the single organization-specific subsection inside the neutral body** — which means you
must switch registers mid-section and be explicit about where the boundary is.

Read `technology`'s §8 output first. Model 3 dimension 6 comes **from §8.3.4 alone**; you may not
re-research it or infer it from general AI activity.

Output: `sections/15-ai-readiness.md` · fragment `state/fragments/ai-readiness.json`.

## §15.1 AI Maturity Assessment

Model 3 in `blueprint/scoring-rubrics.md`. Six dimensions, 1–5, against the universal anchors,
**evidence and confidence per cell**. `T-15.1` + `C-15.1` radar.

| Dim | Source |
|---|---|
| 1 Data foundation | §8.1.3, §15.2 |
| 2 AI initiative depth | §8.3.1 — pilots vs production, named platforms, disclosed outcomes |
| 3 Talent & organization | §13.3 role density, §10.2.2 named AI leadership |
| 4 Governance & responsible AI | §17.6 |
| 5 Partner & vendor ecosystem | §16.1, §9.5 |
| 6 **Agentic posture** | **§8.3.4 only** |

`NOT RELIABLY ASSESSABLE` is allowed and preferred over a forced score. **Deployment maturity is
systematically under-observed** — companies announce pilots loudly and ship production quietly, so
a 2 that "should" be a 3 is the expected error direction. Say that in the evidence column; do not
compensate with an unevidenced bump.

## §15.2 Data Readiness & Quality

The foundations the AI agenda depends on: platform, governance, lineage, quality practice,
residency posture. Built on §8.1.3, extended with anything you can evidence about data operations.

## §15.3 AI Use-Case Opportunity Map — the anchor rule

10–15 use cases (`U-nn`). `T-15.3` + `F-15.3`. Per use case: impact × feasibility × paradigm
(analytical / generative / agentic / automation) × accelerator fit × HITL requirement.

> **Every use case is anchored to a cited §7.5 pain point or §9.1 stated priority.** A use case
> with no anchor claim is **generic filler and is deleted, not softened**. This is the difference
> between a backlog the account team can use and a list of industry AI ideas they could have got
> anywhere.

The vertical module's **U block** is a seed list, not a backlog. Each seed still needs an anchor
claim from this target to survive.

Record `anchor_claims` on every `U-nn` in the fragment. `opportunity` and `verification` both check
it.

## §15.4 Agentic AI Opportunity Assessment

5–8 opportunities, **each tied to §8.3.4 evidence**. `T-15.4`.

If §8.3.4 found no agentic posture, this section says so and stops: *"No agentic AI signals were
evidenced (see §8.3.4). Agentic opportunities below are therefore greenfield rather than
extensions, and carry correspondingly lower feasibility confidence."* — and then you may present a
short greenfield set, clearly labelled `INFERRED`. What you may not do is infer an agentic posture
that §8.3.4 did not find.

## §15.5 Innovation Ecosystem & Culture

Labs, OSS posture, publication and patent activity, external innovation partnerships. Built on
§9.4. **Empty is a valid render.**

## §15.6 the pursuing organization Engagement Fit — the gated subsection

**This is the one place in §3–§17 where the pursuing organization may be named.** Mark the boundary explicitly with a
subsection note so a reader knows the register changed.

Capability (from the **Capability Pack only**, cited `[CAPABILITY-PACK]`) × opportunity fit scores.
`T-15.6` + `F-15.6`.

**Without a Capability Pack, the entire subsection renders as
`[INTERNAL: validate with practice]`** with the fit dimensions named but unscored. Never
invent an organization capability, offering, proof point, reference, client name, or quantified outcome
(V7b, BLOCKER).

## §15.7 Build–Buy–Partner Disposition

Sourcing history (§7.4, §9.3) → what it implies about how this company will acquire the capability.
`account-strategy` uses this directly in §19.8.

## Traps

- **Do not re-research §8.3.4.** Dimension 6 is `technology`'s finding; you score it.
- **Do not let the vertical use-case library become the backlog.** Anchor or delete.
- **An accelerator fit claim is an organization claim** — it belongs in §15.6, not §15.3, unless it is
  written as a neutral capability class.
- **Feasibility is not optimism.** Score it against evidenced data readiness and delivery
  constraints (§10.8), not against how good the use case sounds.
- **HITL requirement is a governance judgement**, and for regulated use cases it is `Required` —
  check §4.6 and §17.6 before scoring it `Optional`.

## Fragment

Claims `C-15.1-nn` … `C-15.7-nn`. **`use_cases[]` — the full `U-nn` backlog with `anchor_claims`.**
Sources `S-15nn`. Gaps `G-15nn`. Coverage for §15. `scoring_inputs.model_3`. Charts `C-15.1`;
figures `F-15.3`, `F-15.6`. `handoff` to: `opportunity` (the `U-nn` backlog and the Model 3 band),
`account-strategy` (§15.7 disposition), `exec-brief` (Model 3 composite for the §1.6 AI Readiness
dimension).
