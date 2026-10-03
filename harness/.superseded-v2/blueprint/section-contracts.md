# Section Contracts — ownership, envelopes, evidence bars, dependencies

> The blueprint says *what* each section contains. This file says *who writes it*, *how long it
> may be*, *what evidence it needs before it may be written at all*, and *what it depends on*.
> Under parallel execution these must be declared, not inferred.

## How to read a row

- **Owner** — the single agent that may write this section. See `prompts/id-allocation.md`.
- **Envelope** — target words for `STANDARD` depth. `BRIEF` ≈ 0.5×, `DEEP` ≈ 1.6×. A guide, not
  a target to pad toward.
- **Evidence bar** — the minimum that must be in hand before the section may be *written*.
  Below the bar, emit the heading plus a one-line gap statement and a `G-nnn` object. This is a
  decidable test, so ten agents deciding independently still produce a consistent dossier.
- **Depends on** — what must exist before this section can be correct. Within a stage, `—` means
  no dependency (safe to run concurrently).
- **Emits** — registers this section is the sole source of.

Notation for evidence bars: `T1×n` = n distinct Tier-1 sources; `T1–2×n` = n sources at Tier 1
or 2; `any×n` = n sources at any tier.

---

## Tier 0

| § | Owner | Envelope | Evidence bar | Depends on | Emits |
|---|-------|---------:|--------------|------------|-------|
| 0.1 | `scoping` | 200 | Entity confirmed from `T1×1` (filing or registry) **or** `T2×2` if private | — | `S-001`–`S-049` |
| 0.2 | `scoping` | 300 | `STRATEGIC_PURSUIT_OBJECTIVES` input present; else derive from vertical defaults and flag | 0.1 | — |
| 0.3 | `scoping` | 400 | none — this is a plan | 0.1, 0.2 | — |
| 0.4 | `contradiction` drafts → `exec-brief` finalises | 400 | none — may be legitimately empty | all Stage 1 | — |
| 0.5 | `qa-gate` (sole author) | 500 | QA gate executed | all stages | Evidence Quality Index |
| 0.6 | `exec-brief` | 200 | §0.2 exists | 0.2, all sections rendered | — |

## Tier 1 — written last, derives nothing new

| § | Owner | Envelope | Evidence bar | Depends on | Emits |
|---|-------|---------:|--------------|------------|-------|
| 1.1 | `exec-brief` | 150 | §11.1 non-empty **and** §12.2 written | 11, 12, 13 | — |
| 1.2 | `exec-brief` | table | canonical facts in state | 2, 4 | — |
| 1.3 | `exec-brief` | 500 | ≥7 claims with `materiality: high` | all Tier 2 | — |
| 1.4 | `exec-brief` | table | ≥3 `O-nn` | 11.1 | — |
| 1.5 | `exec-brief` | table | ≥3 `R-nn` | 10.1, 10.5 | — |
| 1.6 | `exec-brief` | 300 | Model 1 scored, or documented qualitative fallback | 4, 6.4, 7.2, 8.3 | — |
| 1.7 | `exec-brief` | table | ≥5 `A-nn` | 13.5 | — |
| 1.8 | `exec-brief` | table | none — empty means "no high-materiality gaps", which must be stated explicitly | Appendix F | — |

**Hard rule.** `exec-brief` performs **no new research**. Every Tier 1 statement must carry a
`C-`, `O-`, `R-`, `A-`, or `G-` reference. A Tier 1 sentence with no ID is a QA failure (F8a).

## Tier 2 — Stage 1, ten concurrent agents

| § | Owner | Envelope | Evidence bar | Depends on | Emits |
|---|-------|---------:|--------------|------------|-------|
| 2.1 | `corporate` | 400 | `T1–2×1` | — | — |
| 2.2 | `corporate` | 500 | `T1×1` segment disclosure; Priv: `T2×2` | — | — |
| 2.3 | `corporate` | 400 | `T1×1` (DEF 14A / statutory) — **Pub only** | — | — |
| 2.4 | `corporate` | 300 | `T1–2×1` | — | — |
| 3.1 | `market` | 800 | `any×2`, at least one `T3` for market sizing (value-chain + macro elements: `any×1` each) | — | — |
| 3.2 | `market` | 600 | ≥3 named competitors, each `any×1` | — | — |
| 3.3 | `market` | 400 | `T1×3` peer filings — **Pub only**; else qualitative | — | — |
| 3.4 | `market` | 300 | ≥6 claims across §2–3 | 2.x (via state), 3.1–3.3 | — |
| 3.5 | `market` | 1 line | — | — | — |
| 3.6 | `market` | 550 | `T1–2×1` on customer segments; portfolio + brand elements gap-tolerant (brand: no invented NPS/CSAT) | 3.1 | — |
| 4.1 | `financials` | 700 | `T1×1` (cost-structure element: `T1×1` from income-statement/segment notes, else `[DATA GAP]`) | — | — |
| 4.2 | `financials` | 700 | `T1×2` (two reporting periods); Priv: statutory or gap | — | — |
| 4.3 | `financials` | 400 | `T1×1` cash-flow statement — **Pub only** | 4.2 | — |
| 4.4 | `financials` | 400 | none — gap-tolerant by design; `[ESTIMATE]` must state method | 4.1–4.3 | — |
| 4.5 | `financials` | 400 | `T3×1` retrieved market data — **Pub only** | — | — |
| 5.1 | `strategy` | 500 | `T1–2×2`, each dated | — | — |
| 5.2 | `strategy` | 600 | `T2×1` per program named | — | — |
| 5.3 | `strategy` | 400 | `T1–2×1` per deal named; empty is valid | — | — |
| 5.4 | `strategy` | 400 | `T2×2` transcripts/interviews within 12 mo | — | — |
| 5.5 | `strategy` | 400 | `T5×5` postings min. — **hypothesis-grade, never `[FACT]`** | — | — |
| 5.6 | `strategy` | 350 | `T1–2×1` (R&D line **or** innovation-lab/CVC evidence); empty is valid | — | — |
| 6.1 | `technology` | 600 | ≥5 evidenced rows, each `any×1`; per-row confidence mandatory | — | — |
| 6.2 | `technology` | 400 | `any×2` | 6.1 | — |
| 6.3 | `technology` | 400 | `any×2` | 6.1 | — |
| 6.4 | `technology` | 500 | Model 2: ≥1 claim per dimension, or dimension scored `n/e` | 6.1–6.3 | Model 2 inputs |
| 6.5 | `technology` | 400 | `T2×1` exec statement or `T5×3` hiring signal | 6.1–6.3 | — |
| 6.6 | `technology` | 500 | `T1–2×1` on locations/headcount **or** `T4×2` on prior SI/GCC activity | 2.4 (via state), 6.1 | — |
| 6.7 | `technology` | 500 | ≥3 evidenced pain points, each `any×1`; below bar ⇒ gap. **Neutral flag only — no the pursuing organization, no O-nn** | 6.5, 5.2 (via state) | — |
| 7.1 | `ai-posture` | 500 | `any×1` per initiative; empty register is a valid render | — | — |
| 7.2 | `ai-posture` | 500 | Model 3: ≥1 claim per dimension, or `n/e` | 7.1, 6.3 | Model 3 inputs |
| 7.3 | `ai-posture` | 300 | `any×2` — **Opt**, omit entirely if unmet | 7.1 | — |
| 7.4 | `ai-posture` | 400 | none — explicitly inference-heavy; every statement `[INFERENCE]` with basis | 6.x, 7.1–7.3 | — |
| 8.1 | `leadership` | 700 | `T1–2×1` per named person — **no exceptions, no unsourced names** | — | `P-nn` |
| 8.2 | `leadership` | 500 | `T1–2×1` **or** clearly labelled `[INFERENCE]` block | 8.1 | — |
| 8.3 | `leadership` | table | Model 6: every `P-nn` scored with stated basis | 8.1, 8.2 | Model 6 inputs |
| 8.4 | `leadership` | 400 | `T1–2×1` (human-capital disclosure); **aggregate only — F4b still binds, no individual profiling** | — | — |
| 9.1 | `ecosystem` | 500 | ≥4 evidenced rows with signal recency | — | — |
| 9.2 | `ecosystem` | 400 | `any×1` per SI named; `[UNVERIFIED]` tolerated **with flag** | — | — |
| 9.3 | `ecosystem` | 400 | `T2×1` per alliance, within 18 mo | — | — |
| 9.4 | `ecosystem` | 400 | Model 8: ≥1 claim per incumbent assessed | 9.1–9.3 | Model 8 inputs |
| 9.5 | `ecosystem` | 300 | none — **empty is the expected render for most private-sector accounts.** Never estimate an expiry date | 9.1–9.2 | — |
| 10.1 | `risk-reg` | 600 | `T1×1` risk-factor section; Priv: `T2×1` or gap | — | `R-nn` |
| 10.2 | `risk-reg` | 500 | `any×1` per regime named; `V-*` supplies the candidate list | — | — |
| 10.3 | `risk-reg` | 300 | `T1–2×1` per incident; empty is valid and common | — | — |
| 10.4 | `risk-reg` | 400 | `T2×1` sustainability report — **Opt** (Core for `V-ENR`) | — | — |
| 10.5 | `risk-reg` | 400 | Model 7: ≥4 `R-nn` translated | 10.1–10.4, 10.6, 10.7 | Model 7 inputs |
| 10.6 | `risk-reg` | 350 | `T1×1` legal-proceedings/8-K per matter; **empty is valid; never estimate exposure ($)** | — | `R-nn` (litigation risks) |
| 10.7 | `risk-reg` | 400 | none — analytical synthesis; every scenario cites ≥1 driver claim from §4/§10.1; label `[INFERENCE]`/`[ESTIMATE]` | 4.2, 10.1 (via state) | — |
| App. J | `vertical` | varies | vertical confirmed in §0.1 with confidence ≥ Medium | 0.1 | `V-<CODE>` content |

### Stage-1 concurrency note

All ten Stage-1 agents start simultaneously. The `Depends on` entries that reference other
agents' sections (e.g. 3.4 → §2.x, 6.6 → §2.4) resolve through **`state.json` canonical facts
written by `scoping`**, not through peer output. Where a genuine cross-agent dependency exists,
the dependent agent writes `see §2.4` and the `assembly` agent verifies the reference resolves.
No Stage-1 agent ever blocks on a peer.

## Stage 2 — reconciliation

**2a runs concurrently; 2b runs after both**, because `source-merge` also builds the consolidated
state and therefore must see 2a's fragments.

| Stage | Agent | Output | Depends on |
|-------|-------|--------|------------|
| 2a | `contradiction` | `<RUN_DIR>/sections/00-4-contradictions.md` + `X-nnn` objects | all Stage 1 fragments |
| 2a | `evidence-audit` | `<RUN_DIR>/qa/evidence-audit.json` — adversarial pass over every `materiality: high` claim | all Stage 1 sections + fragments |
| 2b | `source-merge` | `<RUN_DIR>/state/source-map.json` (canonical `S-nnn` + rewrite map) **and** `<RUN_DIR>/state/state.json` (merged state read by Stages 3–6) | all Stage 1 + 2a fragments |

`evidence-audit` is **adversarial by mandate**: for each high-materiality claim it attempts to
*refute* the claim, and defaults to `refuted: true` when the cited source does not clearly
support the statement. Refuted claims are downgraded to `[UNVERIFIED]` or converted to gaps
before Tier 3 consumes them — which is the point of running it before, not after, the strategy
layer.

## Tier 3 — Stage 3

§11 must complete before §12 and §13, because both reference `O-nn`. §12 and §13 then run
concurrently.

| § | Owner | Envelope | Evidence bar | Depends on | Emits |
|---|-------|---------:|--------------|------------|-------|
| 11.1 | `opportunity` | table | Every `O-nn` cites ≥1 need-evidence claim ID **that survived `evidence-audit`** | all Tier 2, evidence-audit | `O-nn` |
| 11.2 | `opportunity` | table | Every `U-nn` cites ≥1 claim from §6 or §7 | 6, 7, 11.1 | `U-nn` |
| 11.3 | `opportunity` | 400 | Models 4–5 scored per `O-nn` | 11.1–11.2 | Models 4–5 inputs |
| 12.1 | `account-strategy` | 300 | the pursuing organization input present, else render "input not provided" for organization-side quadrants | 9, 3.4, the pursuing organization input | — |
| 12.2 | `account-strategy` | 300 | ≥3 `O-nn` | 11.1 | — |
| 12.3 | `account-strategy` | table | Every message cites a `C-5.1-nn` priority claim + a `P-nn` | 5.1, 8.3, 11.1 | — |
| 12.4 | `account-strategy` | 400 | ≥1 evidenced incumbent in §9.2 | 9.2, 9.4 | — |
| 12.5 | `account-strategy` | 400 | §6.6 written (sourcing posture drives deal shape) | 6.6, 8.2, 11.1 | — |
| 13.1 | `engagement` | table | ≥3 dated trigger events from §4, §5, or §9.5 | 4, 5, 9.5, 11.1 | — |
| 13.2 | `engagement` | table | Every row references a `P-nn` | 8.3, 12.3 | — |
| 13.3 | `engagement` | table | Every `O-nn` assigned a horizon | 11.1 | — |
| 13.4 | `engagement` | table | Every `HYPOTHESIS`/`VALIDATE` item and every `materiality: high` gap covered | 11, App. F | `Q-16nn` |
| 13.5 | `engagement` | table | 7–12 actions, each with owner role, date, metric | 13.1–13.4 | `A-nn` |
| 13.6 | `engagement` | table | ≥3 triggers, each naming an observable signal and a source to monitor | 1.1 draft thesis, 12.1, App. F | — |

## Stage 5–6

| Agent | Output | Notes |
|-------|--------|-------|
| `qa-gate` | `<RUN_DIR>/qa/qa-report.md` + `qa-report.json`, §0.5 QA block | Executes `qa-protocol.md` F1–F10. **Failures are disclosed, never masked.** |
| `assembly` | `<RUN_DIR>/<slug>-aid.md` + Appendices A–L | Collates; resolves every inline ID against the registers; compiles Appendix L glossary from acronyms used in the body; mints nothing |

## Global invariants

1. **Single owner.** No section appears in two rows. Two agents writing one section is a defect,
   not a merge.
2. **Tier 2 is vendor-neutral.** `qa-gate` greps §2–§10 for the pursuing organization positioning language. A hit fails F7a.
3. **No forward references in Tier 2.** A Tier-2 section may not cite `O-nn` or `A-nn` — those
   do not exist yet. It may only flag neutral relevance.
4. **Evidence bar unmet ⇒ gap, never filler.** The correct render is:

   ```markdown
   ### 4.5 Valuation & Investor Expectations

   > **Verdict [Confidence: n/a].** Not established — see G-304.

   No retrieved source provided peer-comparable valuation multiples as of 2026-08-10.
   Four queries attempted (see Appendix H, #22–25). Resolution path: account-team validation
   via IR contact, or accept unknown. Materiality: low — does not affect the pursuit thesis.
   ```

5. **Envelope overrun is a smell.** A section running >1.5× its envelope usually means it has
   absorbed a neighbour's scope. `qa-gate` flags it (F5e) rather than truncating.
