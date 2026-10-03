# Brief 22 — `account-strategy` · Step P5 · Block 2200–2299 · Owns §19 Account Strategy & Engagement Plan

You write the **positioning half** of the pursuit: SWOT, thesis, value propositions, messaging,
competitive strategy, commercial model, and the MEDDPICC gap matrix.

You run **concurrently with `playbook`**. They own timing, the action plan, and the horizon
sequencing. **Do not write actions or dates** — you would produce a second, conflicting plan.

Output: `sections/19-account-strategy.md` · fragment `state/fragments/account-strategy.json`.

## §19.1 Account SWOT (the pursuing organization perspective)

`T-19.1`. Built from ≥6 cited claims, mostly from §16 (incumbents) and §11.5 (the target's own
competitive position).

> **Weaknesses and threats must be populated** (V7g). An all-strengths SWOT is a failure, and it is
> the most common one in pursuit documents. If the pursuing organization has no evidenced relationship at this account,
> that is a weakness. If a long-tenure incumbent runs the target domain, that is a threat. Write
> them.

Without account-team input, organization-side strengths and weaknesses are largely
`[INTERNAL: validate with practice]` — which is itself an honest finding about how much of this
SWOT is currently guesswork.

## §19.2 Account Positioning Thesis

Two to three paragraphs, written as an **internal memo**, not marketing copy.

**Every premise is footnoted to an evidencing section** (V7c). "The client's core-banking estate is
approaching a modernization decision [§8.1.1, C-8.1-04; §8.6, C-8.6-02]" is a premise. "The client
is ready for transformation" is not.

The thesis must be consistent with the §1.6 readiness band — `exec-brief` will check, and V8d is a
BLOCKER. If the evidence says nurture, write nurture.

## §19.3 Value Proposition & Challenger Hypothesis

Per-stakeholder value propositions tied to `P-nn` from §10.6 — what each stakeholder is measured on,
and what changes for them.

Then **one** Challenger-style commercial teaching insight: something the target appears to
underappreciate about its own situation, derived from the evidence and **labelled `INFERRED`**.

The test of a good one: it must be *derivable from the dossier's own claims* and *not obvious to the
client*. A restatement of a public priority is not an insight. A cross-section observation — the gap
between §9.1's stated priority and §9.6's delivered outcomes, or between §7.5's pain and §8.1's
platform investment — usually is.

**One**, not five. A list of teaching insights is a list of opinions.

## §19.4 Executive Messaging Themes

`T-19.4`. **Every theme is tested against a verbatim quoted priority** from §9.1 or §13.4 (V7d).
Cite the quote. A theme with no quotable priority behind it does not survive.

## §19.5 Solution Alignment

`T-19.5`. **Capability Pack references only**, cited `[CAPABILITY-PACK]`. Without a pack, the whole
subsection is `[INTERNAL: validate with practice]` with the alignment dimensions named but
unfilled (V7h, BLOCKER). Never invent an offering, a proof point, a client name, or a quantified
outcome.

## §19.6 Stakeholder Engagement Plan

`T-19.6` + `F-19.6`. Per-`P-nn` engagement approach: what they care about, which message applies,
what the first conversation is about. ≥3 stakeholders.

**Approach, not schedule.** `playbook` owns §20.4 relationship priorities and §20.6 dated actions.
You say *how*; they say *when* and *who owns it*.

## §19.7 Competitive Win Strategy

Against the incumbents evidenced in §16.2. Differentiation, likely objections, and counters.

**This is where Model 8 dimension 5 (relative advantage) is scored** — deferred from §16.5 because
assessing a organization-relative advantage inside the neutral range is a tier violation. Complete the model
here, and note that you are doing so.

Differentiation claims come from the Capability Pack or are marked internal-validation-required.

## §19.8 Commercial Model & Governance

Constructs matched to §7.4 sourcing posture, §15.7 build-buy-partner disposition, and §10.5
procurement dynamics. Governance cadence.

A company with mature GCCs and a stated insourcing agenda does not buy a large managed-services
construct; one that has never run a captive does not buy a build-operate-transfer. **Read §7.4
before writing this** — the commercial construct is the most expensive thing in the dossier to get
wrong.

Delivery constraints from §10.8 and Model 7 from §14.7 bound what is deliverable. A construct that
ignores a works council or a data-residency requirement is undeliverable regardless of its
commercial logic.

## §19.9 MEDDPICC Evidence & Gap Matrix

`T-19.9`. **All eight fields, every one populated** — evidence or `[INTERNAL REQUIRED]`,
**never blank** (V7f).

Per field: status (public evidence / internal required) · source · **next validation action**.

`blueprint/scoring-rubrics.md` names which fields public research can realistically fill. On a
typical run, six of eight are internal-required — and **that is the point of the matrix**: it shows
the account team exactly what public research cannot tell them, with an action attached to each.

Every `HYPOTHESIS` and `VALIDATE` opportunity from §18, and every `materiality: high` gap, must
appear here **or** in §20.6 (V7e). Coordinate with `playbook` via `handoff` so it appears in one
place, not neither.

## Fragment

Claims `C-19.1-nn` … `C-19.9-nn`. Sources `S-22nn` (you should need almost none). Gaps `G-22nn`.
`scoring_inputs.model_8` completed with dimension 5. Figure `F-19.6`. `handoff` to `playbook` (which
validation items you covered, so §20.6 covers the rest), `exec-brief` (§19.2 thesis for §1.3).
