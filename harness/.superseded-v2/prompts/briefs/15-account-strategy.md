# Brief — `account-strategy` (block 15)

**Stage** 3b — runs concurrently with `engagement`, after `opportunity`
**Owns** §12.1–12.5 · **Block** `1500`–`1599` · **Envelope** ~1,700 w
**Output** `<RUN_DIR>/sections/12-strategy.md` · **Fragment** `account-strategy.json`

Read `_common.md` first. **Tier 3 — the pursuing organization content permitted and expected.**

## Mission

Turn the opportunity register into a position: why the pursuing organization, why now, against whom, on what proof, and
in what commercial shape. This is an **internal memo**, not a client-facing pitch. Its readers are
an account team deciding where to spend pursuit budget, and they are better served by honesty about
weakness than by confidence.

## Read before writing

Every Tier 2 section · `opportunity`'s §11 and its handoff · `ecosystem`'s incumbent set and
Model 8 partials · `technology`'s §6.6 sourcing posture · `risk-reg`'s §10.5 delivery constraints ·
`leadership`'s stakeholder register · `ACCOUNT_CONTEXT` and `KNOWN_RELATIONSHIP_CONTEXT`.

## §12.1 Account SWOT (the pursuing organization lens) — ~300 w · 2×2 with IDs

the pursuing organization's position **at this account** — not the client's SWOT (that is §3.4, and duplicating it fails
QA F5a).

Strengths and weaknesses are organization-side and derive **only** from `ACCOUNT_CONTEXT` and
`KNOWN_RELATIONSHIP_CONTEXT`. If both are `NONE`, those two quadrants read "input not provided" —
do not infer the pursuing organization's capability or relationship from anything else (QA F4e, BLOCKER).

Opportunities and threats derive from Tier 2 and are always renderable: threats include evidenced
incumbents from §9.2, the client's procurement posture from §6.6, and the delivery constraints
from §10.5.

An honest weakness quadrant is the most valuable part of this section. "No evidenced relationship
above the director level" is worth more to a pursuit than three strengths.

## §12.2 Positioning Thesis — ≤300 w

The narrative, as an internal memo: why the pursuing organization, why now, on what proof.

Structure it as an argument that could fail: the client's evidenced situation → the specific need
that creates → why a partner is required at all → why the pursuing organization specifically, against the evidenced
alternatives → what proof the pursuing organization would need to show.

Reference ≥3 `O-nn`. Every load-bearing sentence carries an ID. If you cannot write this in 300
words with IDs, the thesis is not yet clear enough to act on — say that instead of padding.

## §12.3 Stakeholder Messaging Framework — table

Per persona: `P-nn · Their evidenced priority (C-5.1-nn) · Message · Proof point · Related O-nn ·
Likely objection`.

**Every message must trace to a `C-5.1-nn` priority claim and a `P-nn`.** A message not anchored to
something the stakeholder has publicly said they care about is a guess about a named individual,
and it is the kind of guess that gets a meeting wasted.

Use the client's own vocabulary from §5.1 — `strategy` was instructed to preserve it for exactly
this purpose. If they call it "Simplify, Focus, Grow", the message uses those words.

Do not re-profile stakeholders. Reference `P-nn` and move on (QA F5a).

## §12.4 Competitive Win Strategy — ~400 w

Differentiation against the **evidenced** incumbents in §9.2 — named, specific, and honest.

This is where **Model 8 dimension 5 (differentiation)** is computed, deferred from §9.4 because it
is the pursuing organization-specific (QA F6g). Complete the model here: take `ecosystem`'s four-dimension partial per
incumbent, add differentiation from `ACCOUNT_CONTEXT`, and report the full composite.

Per incumbent: their evidenced position · where they are strong · where evidence suggests they are
vulnerable · the pursuing organization's differentiator **tied to a client-specific constraint**, not a generic
capability · the likely objection and a specific counter.

"Global delivery scale" is not a differentiator — every major SI has it. "Existing GCC in Hyderabad
adjacent to the client's own captive (§6.6), enabling a hybrid captive-managed model the incumbent
has no precedent for" is one, if the input supports it.

Where `ACCOUNT_CONTEXT` is `NONE`, say so and render the incumbent analysis without the
differentiation column rather than inventing capabilities.

## §12.5 Commercial & Governance Model — ~400 w · bar §6.6 written

**Derives directly from §6.6.** This is the reason §6.6 was added in v2.1.

Recommended commercial construct — outcome-based, managed service, T&M, fixed-price, capacity,
build-operate-transfer — matched to: the client's procurement style (§8.2) · their sourcing posture
and captive footprint (§6.6) · the delivery constraints from §10.5 · the opportunity shapes in
§11.1.

A client with a large captive and a stated consolidation drive wants a different construct from one
that outsources wholesale to two incumbents. Say which case this is and why, citing §6.6.

Then: governance model and cadence · the commercial risks from Model 7 and how the construct
mitigates them · pricing considerations grounded in evidence, not aspiration.

Where §8.2's procurement style rests on `[INFERENCE]` — usual outside `V-GOV` — flag that this
recommendation is correspondingly provisional and put it in §13.4 as a validation question.

## Fragment duties

- `scoring_inputs.displacement_full`: completed Model 8 per incumbent, including dimension 5.
- `handoff` to `engagement`: entry vehicles implied by §12.5, and per-persona message IDs for §13.2.
- `handoff` to `exec-brief`: the thesis in one sentence, for §1.1.
- `data_gaps[]`: `G-15nn` wherever the pursuing organization input was absent and a section could not render fully.

## Traps

- **Generic capability lists.** Every organization capability named must map to a documented client need.
  A paragraph that would read identically for any client in this vertical fails the section.
- Do not fabricate the pursuing organization references, credentials, partnerships, or delivery history. Only what
  `ACCOUNT_CONTEXT` provides (QA F4e, BLOCKER).
- Do not restate Tier 2 analysis. Cite it.
- Do not write actions or dates — that is §13.5, and `engagement` is writing it concurrently.
  Duplicating it produces two conflicting action plans.
