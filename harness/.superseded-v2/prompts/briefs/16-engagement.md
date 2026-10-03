# Brief — `engagement` (block 16)

**Stage** 3b — runs concurrently with `account-strategy`, after `opportunity`
**Owns** §13.1–13.6 · **Block** `1600`–`1699` · **Sole owner of** `A-nn`
**Envelope** ~1,500 w · **Output** `<RUN_DIR>/sections/13-engagement.md` · **Fragment** `engagement.json`

Read `_common.md` first. **Tier 3 — the pursuing organization content permitted and expected.**

## Mission

Make the strategy operational: when to move, who to approach, in what sequence, what must be
validated first, what gets committed — and, new in v2.1, **under what conditions the pursuing organization should stop**.

You run concurrently with `account-strategy`. You own actions and timing; they own positioning and
commercial shape. Do not write positioning; they will not write actions.

## §13.1 Entry Vehicles & Timing Calendar — table · bar ≥3 dated triggers

Trigger events mapped to entry actions. Sources of dated triggers, in descending reliability:

`ecosystem`'s §9.5 contract and renewal signals — the strongest, when they exist · `risk-reg`'s
regulatory compliance deadlines and §10.7 scenario watch-signals · `strategy`'s §5.2 programme
milestones · `financials`' fiscal calendar and budget-setting cycle · `leadership`'s recent or
expected executive transitions · earnings dates and investor-day announcements.

Per row: `Trigger · Evidenced date · Source · Why it opens a window · Entry vehicle · Related O-nn`.

A trigger without a date is not a trigger. If you have fewer than three dated triggers, say so —
"pursuit timing is not externally anchored; entry will depend on relationship-led access" is an
honest and actionable finding, and it should change how §13.5 is written.

## §13.2 Stakeholder Engagement Plan — table

Per row: `P-nn · Influence/Accessibility quadrant · Message ref (§12.3) · Vehicle · Owner role ·
Target date · Objective`.

Reference `P-nn` — do not re-profile anyone (QA F5a). Sequence by quadrant: High/High engage first;
High-influence/Low-accessibility needs a routed sponsor path — **name the route**, do not just note
the problem.

Where `KNOWN_RELATIONSHIP_CONTEXT` is `NONE`, every accessibility score is structurally biased low
(see §8.3's caveat). Reflect that in the plan by leading with relationship-building actions rather
than assuming cold access will work.

## §13.3 Three-Horizon Pursuit Roadmap — table

Every `O-nn` assigned to 0–6 / 6–18 / 18+ months, with **dependencies stated**: which opportunities
require another to land first, which share a stakeholder or a budget cycle, which are gated by a
§13.4 validation.

Horizons come from §11.1; if you disagree with one, that is a `handoff` to `opportunity` and a note
— not a silent reassignment.

## §13.4 Validation Question Backlog — table

**Coverage is mandatory and mechanically checked** (QA F7e): every `HYPOTHESIS` and `VALIDATE`
opportunity, and every `materiality: high` gap in Appendix F, must appear here.

Per row: `Q-16nn · Question · Why it matters · Who can answer (P-nn or role) · How to ask ·
Blocks which O-nn · Target date`.

Write questions an account executive can actually ask in a meeting. "Confirm the client's data
platform strategy" is not a question. "In the March investor day you described consolidating onto a
single data platform by FY27 — which platform, and is the programme funded?" is.

On thin-evidence accounts this section is the **primary deliverable**, per the degradation mode.
Weight it accordingly rather than treating it as a leftover.

## §13.5 Action Plan — 7–12 `A-nn`

`A-nn · Action · Owner role · Due · Success metric · Horizon (30/90/180d) · Refs`.

Owner **role**, not a person's name — the dossier outlives the assignment. Dates relative to
`RESEARCH_AS_OF_DATE`. A success metric that is observable: "meeting held with P-02 and their
stated priority confirmed or corrected", not "build relationship".

First actions should close the highest-materiality validation questions, not launch a pursuit on
unvalidated assumptions. Feeds §1.7 directly.

## §13.6 Kill Criteria & Disengagement Triggers — `NEW v2.1` · bar ≥3 triggers

The counterweight to Tier 3's structural optimism. Tier 3 is the only the pursuing organization-positive layer in the
dossier, which makes it the only one with a built-in incentive to conclude "pursue".

Per row: `Trigger · Observable signal · Source to monitor · Decision if triggered · Review date`.

Derive from: the assumptions §12.2's thesis rests on — which, if disproved, collapses it? · §12.1's
weakness quadrant · the high-materiality gaps in Appendix F — what would a bad answer to a §13.4
question mean? · Model 7's high-risk dimensions · Model 5's suppressed win-probability scores ·
**§10.7's Bear-scenario signals — the observable markers that the client's investment capacity is
contracting are ready-made kill-criteria monitors.**

Good triggers are **observable and dated**: "the ERP consolidation RFP (§9.5) is awarded to an
incumbent SI" · "the CIO role (P-03) remains vacant past Q2, removing the sponsor the thesis
assumes" · "FY27 guidance signals a cost-reduction agenda rather than the transformation agenda
§5.1 evidences".

Bad triggers are unfalsifiable: "the client loses interest", "the market changes".

Set a **named review date** for the whole pursuit. A thesis with no review date is not a decision,
it is a commitment.

## Fragment duties

- `actions[]`: every `A-nn`.
- `open_questions[]`: every `Q-16nn` from §13.4.
- `handoff` to `exec-brief`: the 30/90/180 actions for §1.7, and the kill criteria summary.
- `handoff` to `qa-gate`: your §13.4 coverage list, so F7e can be verified mechanically.

## Traps

- Actions without metrics are intentions. Every `A-nn` gets an observable success metric.
- Do not write positioning, messaging content, or commercial constructs — `account-strategy` owns
  those and is writing them right now.
- Do not assign real names as owners.
- Do not soften §13.6 to protect the thesis. An account team that never disengages has no pursuit
  budget for the accounts that would have converted.
