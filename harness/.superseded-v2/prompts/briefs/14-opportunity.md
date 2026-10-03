# Brief — `opportunity` (block 14)

**Stage** 3a — runs alone, before `account-strategy` and `engagement`
**Owns** §11.1–11.3 · **Block** `1400`–`1499` · **Sole owner of** `O-nn`, `U-nn`
**Envelope** ~1,800 w · **Output** `<RUN_DIR>/sections/11-opportunity.md` · **Fragment** `opportunity.json`

Read `_common.md` first. **Tier 3 begins here — the pursuing organization content is now permitted and expected.**
You score **Models 4 and 5**. Read `blueprint/scoring-rubrics.md`.

## Mission

Convert evidenced client reality into a scored, single-source-of-truth opportunity register. Every
downstream Tier-3 section references your `O-nn` IDs — §12.2, §12.3, §13.1, §13.3, and §1.4 all
depend on this register being right, and none of them may create opportunities of their own.

You run alone precisely so that §12 and §13 have stable IDs to reference.

## Read before writing

- Every file in `<RUN_DIR>/sections/` — the full Tier 2 body.
- `<RUN_DIR>/qa/evidence-audit.json` — **the refuted-claim list is binding**.
- All Stage-1 `handoff` entries, especially: `financials` (programme budgets, discretionary
  capacity, cost pools), `strategy` (priorities, programmes, R&D/innovation posture), `technology`
  (§6.6 sourcing posture, legacy constraints, **§6.7 operational pain-point register — a prime
  source of `CONFIRMED` need evidence**), `ai-posture` (initiatives and capability gaps), `risk-reg`
  (regulatory deadlines), `leadership` (**§8.4 talent/skills gaps and reskilling programmes**),
  `vertical` (filtered use-case seeds), `ecosystem` (whitespace domains).
- `ACCOUNT_CONTEXT` and `STRATEGIC_PURSUIT_OBJECTIVES`.

## §11.1 Opportunity Register — 8–15 `O-nn`

The canonical register. Per row:

`O-nn · Opportunity · Status · Need evidence (claim IDs) · Attractiveness (conf) · Win prob (conf) ·
Sizing basis + range · Horizon · Lead practice · Next action`

### Need evidence is the load-bearing field

Every `O-nn` cites ≥1 claim ID **that survived `evidence-audit`**. A claim marked `REFUTED` may not
be cited as need evidence (QA F3f, BLOCKER). A claim marked `WEAKENED` may be cited only at its
corrected strength — which usually means the opportunity is `HYPOTHESIS`, not `CONFIRMED`.

An opportunity with no claim ID is not an opportunity. It is a capability you would like to sell,
and it does not belong in this register.

### Status discipline

| Status | Meaning | Bar |
|--------|---------|-----|
| `CONFIRMED` | The client has publicly stated this need or programme | T1–T2 claim, dated |
| `HYPOTHESIS` | Evidence-backed inference — the need follows from what is evidenced | ≥1 surviving claim + stated reasoning |
| `VALIDATE` | Plausible, but the account team must confirm before investment | Named validation question in §13.4 |

Skew honestly. On most accounts, three `CONFIRMED` and nine `HYPOTHESIS` is the real distribution.
A register where everything is `CONFIRMED` has redefined the word.

### Sizing

`ESTIMATE` with a **range**, a stated method, and the key assumption. A client-disclosed programme
budget (from `financials`/`strategy` handoff) is the only evidence that lets Model 4's value
dimension score `5`; benchmark-derived sizing caps at `3`. Never a point value.

### Scoring

Model 4 (attractiveness) and Model 5 (win probability) per `O-nn`, each dimension with anchor,
claim IDs, and confidence. Suppress composites at ≥2 Low-confidence dimensions and give the
qualitative assessment instead. Expect suppression to be common on Model 5, because incumbency and
timing usually rest on absent contract evidence — **that is the design working**, and the render
should say so once rather than apologise for it repeatedly.

## §11.2 AI & Agentic Use-Case Backlog — 8–12 `U-nn`

`U-nn · Use case · Paradigm · Domain · Impact (1–5) · Feasibility (1–5) · Evidence (claim IDs) ·
Accelerator fit · HITL · Status`

Every `U-nn` cites ≥1 claim from §6 or §7. Seed from `vertical`'s handoff and `ai-posture`'s gap
findings — then **filter to this client's evidenced situation**. A generic sector use-case list
with no client-specific evidence is exactly the filler this blueprint exists to eliminate.

Feasibility must reflect the constraints Tier 2 established: `technology`'s §6.3 data-maturity
finding, `risk-reg`'s §10.5 delivery constraints, the OT/IT boundary in `V-ENR`/`V-MFG`, the
authorisation boundary in `V-GOV`, model-risk governance in `V-BFSI`. A use case rated highly
feasible against a client whose data foundation scored 2 is not credible.

`Accelerator fit` renders only from `ACCOUNT_CONTEXT`. If that input is `NONE`, the column
reads "input not provided" — never a fabricated accelerator name (QA F4e, BLOCKER).

## §11.3 Prioritization View — ~400 w

Impact × feasibility × timing, with the **trade-offs stated explicitly**. Which opportunities
compete for the same budget, the same stakeholder, or the same delivery capacity? What sequencing
dependency exists between them?

A prioritised list with no stated trade-off is a sorted list. The trade-offs are the analysis.

A `VZ-14nn` spec for a 2×2 is warranted here if the register is large enough that the pattern is
hard to see in a table.

## Fragment duties

- `opportunities[]`, `use_cases[]`: fully populated.
- `scoring_inputs.opportunity_attractiveness`, `scoring_inputs.win_probability`: per `O-nn`.
- `handoff` to `account-strategy`: the `O-nn` set with scores, for §12.2 and §12.4.
- `handoff` to `engagement`: `O-nn` with horizons, plus every `HYPOTHESIS`/`VALIDATE` item for
  §13.4.
- `handoff` to `exec-brief`: the top 5 by combined score, for §1.4.

## Traps

- **Do not create opportunities from the pursuing organization capability.** Start from the evidenced client need and map
  capability to it. A capability with no evidenced need is not an opportunity — at best it is a
  `VALIDATE` item with a named validation question.
- Do not re-analyse Tier 2. Cite claim IDs. If you find yourself explaining the client's financial
  position, you are rewriting §4.
- Do not inflate scores to make the account look attractive. §1.6 rolls up from these, and §13.6
  will name kill criteria against them. An honest weak register is a usable result.
- `O-nn` and `U-nn` are yours alone. No other agent mints them, and you mint nothing else outside
  block 14.
