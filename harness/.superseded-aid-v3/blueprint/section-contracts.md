# Section Contracts v3.0.0 — ownership, envelopes, evidence bars, dependencies

> The blueprint says *what* each section contains. This file says **who writes it**, **how long it
> may be**, **what evidence it needs before it may be written at all**, and **what it depends on**.
> Under parallel execution these must be declared, not inferred.

## How to read a row

- **Owner** — the single agent that may write this section. See `prompts/id-allocation.md`.
- **Env.** — target words at `STANDARD` tier. `EXECUTIVE` ≈ 0.4×, `FULL_ANNEX` ≈ 1.5×. A guide,
  **never a padding target**.
- **Evidence bar** — the minimum that must be in hand before the section may be *written*. Below
  the bar, emit the heading, one line naming what is missing and where you looked, and a `G-nnnn`
  gap object. This is a **decidable test**, so ten agents deciding independently still produce a
  consistent dossier.
- **Depends on** — what must exist before this section can be correct. `—` inside a wave means no
  dependency: safe to run concurrently.
- **Emits** — registers this section is the sole source of.

**Evidence-bar notation.** `T1×n` = n distinct Tier-1 sources · `T1-2×n` = n at Tier 1 or 2 ·
`any×n` = n at any tier · `ind×n` = n **independent** sources after the independence test
(`evidence-policy.md` §3) · `gov` = the governing source for that claim type · `none` = the section
is analysis over already-established claims.

**Source tiers.** T1 regulator filings and official transcripts · T2 corporate/IR/newsroom/
sustainability pages and official announcements · T3 named financial data services and tier-1
analyst research · T4 tier-1 business media and trade press · T5 jobs boards, review sites,
tech-discovery, social — **weak signals only**.

---

## §0 — Preflight (hard gate)

| § | Owner | Env. | Evidence bar | Depends on | Emits |
|---|---|---:|---|---|---|
| 0 | `preflight` | 600 | Entity resolved from `gov` (adapter filing or registry) **or** `T1-2×2` if private. **Unresolvable entity ambiguity is a STOP condition** | — | `S-0001`–`S-0049` (backbone), run contract |

Nothing downstream runs until §0 exists. `preflight` settles entity, ownership form, jurisdiction
adapter(s), reporting standard, languages, verticals, output tier, and budgets — the six decisions
that determine whether the rest of the run researches the right company under the right rules.

## §1 — Executive Summary *(written last, placed first)*

`exec-brief` performs **no new research** and mints **no sources**. Every §1 statement carries a
`C-` / `O-` / `R-` / `A-` / `P-` / `G-` reference. A §1 sentence with no ID is a **BLOCKER** (V8a).

| § | Owner | Env. | Evidence bar | Depends on | Emits |
|---|---|---:|---|---|---|
| 1.1 | `exec-brief` | table | Canonical facts in state; every field cited or explicitly gapped | §3, §6 | — |
| 1.2 | `exec-brief` | 600 | ≥7 claims at `materiality: high` that **survived** `evidence-audit` | all body | — |
| 1.3 | `exec-brief` | 350 | §18 non-empty **and** §19.2 written | §18, §19 | — |
| 1.4 | `exec-brief` | table | ≥3 `O-nn` | §18 | — |
| 1.5 | `exec-brief` | table | ≥3 `R-nn` | §14 | — |
| 1.6 | `exec-brief` | 300 | Model 1 scored, or a documented qualitative fallback. **Stakeholder Access `NOT ASSESSED` + renormalization shown when the Input Sheet is absent** | §6, §8.2, §15.1, §9 | — |
| 1.7 | `exec-brief` | table | ≥5 `A-nn` | §20.6 | — |

## §2 — Research Scope & Methodology

`methodology` also performs no new research. It reports what the run actually did.

| § | Owner | Env. | Evidence bar | Depends on | Emits |
|---|---|---:|---|---|---|
| 2.1 | `methodology` | 300 | §0 objectives present, else derived from the vertical default and flagged | §0 | — |
| 2.2 | `methodology` | 250 | none — restates §0 boundaries | §0 | — |
| 2.3 | `methodology` | table | Merged Source Manifest exists | §21.1 | — |
| 2.4 | `methodology` | 250 | none | — | `F-2.4` |
| 2.5 | `methodology` | 600 | **Every autonomous assumption recorded by any agent must appear.** Empty is only valid if no agent recorded one | all fragments | — |
| 2.6 | `methodology` | 400 | Claim counts by evidence status computed from the merged ledger | §21.9 | — |

---

## §3–§17 — the body. vendor-neutral. Wave A and Wave B.

> Wave A agents run **fully concurrently** after `backbone`. Wave B agents depend on a Wave A
> output and run after it. `technology`, `strategy`, `leadership`, `signals`, `risk`, and `esg` are
> in Wave A despite their spec phase number because nothing in the body depends on them — see
> `ARCHITECTURE.md` for the phase→wave mapping.

### §3 Company Overview — `corporate` (Wave A)

| § | Env. | Evidence bar | Depends on |
|---|---:|---|---|
| 3.1 | 600 | `T1-2×1` per dated milestone; the narrative may not exceed the dated events | — |
| 3.2 | 200 | `T1-2×1`, **verbatim** | — |
| 3.3 | 600 | `gov` segment/subsidiary disclosure (Exhibit 21 or equivalent); Priv: `T1-2×2` | — |
| 3.4 | 400 | `T1-2×1` | — |
| 3.5 | 500 | `gov` — proxy/statutory. **Instrument correctness is checked (V4c)**: 13D/G ≠ 13F | — |
| 3.6 | 400 | `gov` registry or filing per entity listed. **Every entity row carries at least one identifier** | 3.3 |
| 3.7 | 400 | `gov` beneficial-ownership/insider filings. **Empty is a valid render** | 3.5, 3.6 |

### §4 Industry & Market — `market` (Wave A)

| § | Env. | Evidence bar | Depends on |
|---|---:|---|---|
| 4.1 | 400 | `any×1` classification + `any×1` structure | — |
| 4.2 | 500 | `T3×1` sized estimate **with all seven definitional controls**; below that, gap the number and keep the qualitative structure | — |
| 4.3 | 600 | `any×1` per trend, each tied to a target-specific impact | — |
| 4.4 | 350 | `any×2` | 4.1 |
| 4.5 | 500 | `any×1` per force scored; a force with no evidence is `NOT RELIABLY ASSESSABLE` | 4.1, 4.3 |
| 4.6 | 600 | `gov` per regulation — **all eleven register fields or an explicit gap** | — |
| 4.7 | 350 | `T1×1` FX/geographic exposure from filings + `any×1` per macro force | — |

### §5 Business Model — `business-model` (Wave A)

| § | Env. | Evidence bar | Depends on |
|---|---:|---|---|
| 5.1 | 450 | `T1-2×2` across the nine blocks; unevidenced blocks are gapped, not guessed | — |
| 5.2 | 700 | `gov` segment note, **3 FY, footing to the reported total** | — |
| 5.3 | 350 | `T1-2×1` | 5.2 |
| 5.4 | 300 | `T1-2×1`; pricing that is not disclosed is gapped, never inferred from list prices | — |
| 5.5 | 300 | `T1-2×1` | — |
| 5.6 | 400 | `T1×1` from the income statement / segment notes, else `[DATA UNAVAILABLE]` | 5.2 |
| 5.7 | 300 | `gov` customer-concentration disclosure. **Empty is a valid render** | — |
| 5.8 | 400 | `T1-2×1`; supplier names only where evidenced | — |
| 5.9 | 450 | `T1-2×1` per KPI; a KPI without a disclosed definition is not a KPI | 5.2 |

### §6 Financial Performance — `financials` (Wave A)

> **Every number reconciles to `precomputed-financials` where attached.** A discrepancy is
> reported, not corrected (V2a).

| § | Env. | Evidence bar | Depends on |
|---|---:|---|---|
| 6.1 | 400 | `gov` — 3 FY minimum; Priv: statutory or `[DATA UNAVAILABLE]` | — |
| 6.2 | 700 | `gov` for every line; derived numbers recompute from stated inputs | 6.1 |
| 6.3 | 500 | `gov`; **debt attributed to the issuing entity** | 6.1 |
| 6.4 | 350 | `gov` cash-flow statement | 6.1 |
| 6.5 | 400 | `T1-2×1` quoted framework + `gov` cash-flow behaviour. **Both, or say which is missing** | 6.4 |
| 6.6 | 350 | none — gap-tolerant by design. `[ESTIMATED]` **must** state the model and inputs | 6.1–6.2 |
| 6.7 | 400 | `T3×1` retrieved market data, date-stamped. Priv: funding/debt history substitutes | — |
| 6.8 | 350 | `gov` agency action per rating — **rated entity + instrument + seniority mandatory** | 3.6 |
| 6.9 | 400 | `gov`; `NOT RELIABLY ASSESSABLE` where the sector makes DuPont/EBITDA meaningless | 6.2, 6.3 |
| 6.10 | 350 | `T1×2` guidance/actual pairs. **Empty is a valid render** | 6.2 |

### §8 Technology & Digital Maturity — `technology` (Wave A)

| § | Env. | Evidence bar | Depends on |
|---|---:|---|---|
| 8.1.1 | 600 | ≥5 evidenced rows, each `any×1` with a **mention classification and confidence** | — |
| 8.1.2 | 350 | `any×2` | 8.1.1 |
| 8.1.3 | 400 | `any×2` | 8.1.1 |
| 8.1.4 | 450 | `any×1` per layer named; layers with no evidence are omitted, not filled | 8.1.1 |
| 8.2 | 450 | ≥1 cited claim per dimension, or the dimension scores `NOT RELIABLY ASSESSABLE` | 8.1 |
| 8.3.1 | 550 | `any×1` per initiative; **outcome claims require `ind×1`** | — |
| 8.3.2 | 250 | `any×1`. Empty is valid | — |
| 8.3.3 | 250 | `any×1` per bet. Empty is valid | — |
| 8.3.4 | 400 | `any×1`; **researched as its own topic with its own queries**, not inferred from 8.3.1 | — |
| 8.4 | 400 | `gov` for disclosed incidents; passive-public only. **Disclosed and observed rendered separately** | — |
| 8.5 | 300 | `T1-2×1` | — |
| 8.6 | 350 | `T2×1` exec statement **or** `T5×3` corroborated hiring signal | 8.1 |

### §9 Strategy & Transformation — `strategy` (Wave A)

| § | Env. | Evidence bar | Depends on |
|---|---:|---|---|
| 9.1 | 500 | `T1-2×2`, each **dated and quoted verbatim with provenance class** | — |
| 9.2 | 600 | `T2×1` per named program; budget/timeline only if CONFIRMED/ANNOUNCED or `[ESTIMATED]` with basis | — |
| 9.3 | 450 | `T1-2×1` per deal. **Pipeline is ANNOUNCED/OBSERVED-SIGNAL only — no invented deals** | — |
| 9.4 | 350 | `T1×1` R&D line **or** `T2×1` lab/CVC evidence. Empty is valid | — |
| 9.5 | 300 | `T2×1` per alliance | — |
| 9.6 | 450 | **`ind×1` per delivered outcome claimed.** A company saying it delivered is ANNOUNCED, not CONFIRMED | 9.2 |

### §10 Leadership & Organization — `leadership` (Wave A) · emits `P-nn`

> Public professional facts and attributed statements only. `evidence-policy.md` §10 governs.

| § | Env. | Evidence bar | Depends on |
|---|---:|---|---|
| 10.1 | 400 | `gov` proxy/governance filing. Priv: best-available, marked | — |
| 10.2 | 700 | `T1-2×1` per profile; statements quoted with date and venue | — |
| 10.3 | 300 | `T1-2×1` | — |
| 10.4 | 400 | `any×1` per centre; **authority and budget claims are `INFERRED` unless evidenced** | 10.2, 10.3 |
| 10.5 | 350 | `any×1`; every dynamic status-tagged | 10.4 |
| 10.6 | 450 | Canonical `P-nn` register; evidenced vs inferred marked per row | 10.2–10.5 |
| 10.7 | 400 | `gov` human-capital disclosure. **Aggregate only.** Attrition needs sample-size discipline | — |
| 10.8 | 400 | `any×1` per constraint. **Empty is a valid render** — it means none were evidenced, and it must say so | — |

### §13 Current Signals — `signals` (Wave A)

| § | Env. | Evidence bar | Depends on |
|---|---:|---|---|
| 13.1 | 450 | `T2×1` per program, dated | — |
| 13.2 | 400 | `any×1` per investment, status-tagged | — |
| 13.3 | 450 | `T5×8` postings minimum, **window stated**, every technology mention classified. Never above `OBSERVED-SIGNAL` | — |
| 13.4 | 450 | `T1×2` transcripts/investor day within 12 mo, **verbatim with provenance class** | — |
| 13.5 | 300 | `T2×1` per signal, dated | — |
| 13.6 | 300 | `T3×1`. Pub only | — |
| 13.7 | 400 | `gov` award/contract record or published RFP. **Empty is a valid render; never estimate an expiry date** | — |

### §14 Risk & Regulatory — `risk` (Wave A) · emits `R-nn`

| § | Env. | Evidence bar | Depends on |
|---|---:|---|---|
| 14.1 | 550 | `gov` risk-factor disclosure, **distilled not copied**, ISO 31000 taxonomy applied | — |
| 14.2 | 500 | `gov` per regulation — all eleven register fields. May cross-reference §4.6 rather than duplicate | — |
| 14.3 | 400 | `gov` legal-proceedings note or court/regulator record. **Disclosed exposure figures only** | 3.6 |
| 14.4 | 350 | `gov` disclosure for incidents. Empty is valid | — |
| 14.5 | 350 | `T1×1` geographic exposure + `any×1` per force | — |
| 14.6 | 400 | none — analysis over §6 and §14.1 claims, `[INFERRED]`-labelled, assumptions stated | 14.1 |
| 14.7 | 400 | ≥5 claims across §14. **Still vendor-neutral in wording** | 14.1–14.6 |
| 14.8 | 400 | Official list screening (OFAC/EU/UK/UN). **Entity-match certainty stated per hit.** A clean screen is a result and must be recorded as one | 3.6 |
| 14.9 | 350 | `gov` lobbying/subsidy disclosure. Empty is valid | — |

### §17 ESG & Responsibility — `esg` (Wave A)

| § | Env. | Evidence bar | Depends on |
|---|---:|---|---|
| 17.1 | 300 | `T3×1` per rating — **provider, score, and rating date each** | — |
| 17.2 | 400 | `T1-2×1` sustainability report; targets **verbatim**; SBTi status checked | — |
| 17.3 | 300 | `T1-2×1`. **Disclosed data only** | — |
| 17.4 | 350 | `gov` proxy. Pub only | — |
| 17.5 | 300 | `any×1`. Neutral framing | 17.2 |
| 17.6 | 400 | `T1-2×1` published principles/governance body; EU AI Act readiness where in scope | — |

### §7 Operations — `operations` (Wave B ← §5)

| § | Env. | Evidence bar | Depends on |
|---|---:|---|---|
| 7.1 | 350 | `T1-2×1` | 5.1 |
| 7.2 | 500 | `any×1` per process; pain level and automation potential **evidence-tagged** | 5.1, 5.6 |
| 7.3 | 400 | `T1-2×1`; facility/supplier evidence where available | 5.8 |
| 7.4 | 450 | `any×1`; **named providers only where evidenced.** GCC/captive footprint is the strongest single predictor of deal shape — do not thin it | 5.8 |
| 7.5 | 500 | `any×1` per pain point, ranked, each tied to a cited claim. **This is the origin of most §18 opportunities** | 7.2 |
| 7.6 | 400 | `any×1` per signal class, **sample size and window stated**. Empty is valid | — |

### §11 Competition & Peers — `competition` (Wave B ← §6)

> **§11.0 is written before every other §11 subsection** and is binding on every agent that
> benchmarks anywhere in the dossier.

| § | Env. | Evidence bar | Depends on |
|---|---:|---|---|
| 11.0 | 400 | Candidate universe, dimensions, exclusions, normalization, vintage — **all five** | 6.1 |
| 11.1 | 350 | ≥3 named competitors, each `any×1` | 11.0 |
| 11.2 | 400 | `T3×1` per share estimate with **source + vintage**; comparability caveat when mixing definitions | 11.0 |
| 11.3 | 500 | `gov` peer filings ×3, normalized per 11.0. Priv: qualitative, labelled | 11.0, 6.1–6.2 |
| 11.4 | 400 | `any×1` per peer dimension — **comparable evidence only**, never a peer scored from thinner data than the target | 11.0, 8.2 |
| 11.5 | 400 | ≥6 claims across §3–§11. SWOT of the **target** | 11.1–11.4 |
| 11.6 | 350 | Per-BU market data present, else a qualitative assessment **labelled as such** | 3.3, 11.2 |
| 11.7 | 300 | Public evidence and `[INTERNAL]` **rendered in separate blocks** | 11.1 |

### §12 Customer & Market Intelligence — `customers` (Wave B ← §5)

| § | Env. | Evidence bar | Depends on |
|---|---:|---|---|
| 12.1 | 350 | `T1-2×1` | 5.3 |
| 12.2 | 400 | `T1-2×1`; lifecycle stage evidenced or marked `INFERRED` | 5.2 |
| 12.3 | 350 | `T1-2×1` | 5.5 |
| 12.4 | 400 | Standardized benchmark (`T3×1`) preferred; review signals need **sample size, window, method, bias**. **Never an invented NPS/CSAT** | — |
| 12.5 | 400 | `T3×1` ranking or a sentiment read with **method stated**. Empty is valid | — |

### §15 AI & Innovation Readiness — `ai-readiness` (Wave B ← §8) · emits `U-nn`

| § | Env. | Evidence bar | Depends on |
|---|---:|---|---|
| 15.1 | 500 | ≥1 cited claim per dimension against the anchored rubric, or `NOT RELIABLY ASSESSABLE` | 8.2, 8.3 |
| 15.2 | 350 | `any×2` | 8.1.3 |
| 15.3 | 700 | **Every use case grounded in a cited §7.5 pain point or §9.1 priority.** A use case with no anchor is filler and is deleted, not softened | 7.5, 8.3, 9.1 |
| 15.4 | 450 | **`any×1` from §8.3.4 per opportunity.** No §8.3.4 evidence ⇒ the section states that and stops | 8.3.4 |
| 15.5 | 300 | `any×1`. Empty is valid | 9.4 |
| 15.6 | 350 | **Capability Pack attached**, else the whole subsection is `[INTERNAL: validate with practice]` | 15.3, 15.4 |
| 15.7 | 350 | `any×1` sourcing-history evidence | 7.4, 9.3 |

### §16 Vendor Ecosystem — `vendors` (Wave B ← §8)

| § | Env. | Evidence bar | Depends on |
|---|---:|---|---|
| 16.1 | 500 | `any×1` per row with **evidence type + classification + confidence**. Contract signals only as evidenced | 8.1 |
| 16.2 | 450 | `any×1` per SI named. **Contract-timeline estimates only with the basis shown** | 8.1, 13.2 |
| 16.3 | 250 | `T2×1` per partnership. Empty is valid | — |
| 16.4 | table | **Account-Team Input Sheet attached**, else `[INTERNAL: account team to complete]` — never guessed | — |
| 16.5 | 400 | ≥1 evidenced incumbent per displacement row. Neutral framing in-section | 16.1, 16.2 |

---

## §18–§20 — Pursuit. the pursuing organization content permitted.

> Every `O-nn` cites at least one claim that **survived `evidence-audit`**. A REFUTED claim may not
> be cited as need evidence — **BLOCKER (V3f)**.

### §18 Opportunity Assessment — `opportunity` · emits `O-nn`

| § | Env. | Evidence bar | Depends on |
|---|---:|---|---|
| 18.1 | 500 | Per line: sizing basis shown, **range not a point**; win-prob gated | 15.3, 7.5, 6.6 |
| 18.2 | 350 | ≥4 `O-nn` clustered | 18.1 |
| 18.3 | 400 | ≥1 evidenced pain per function row | 7.5, 10.4 |
| 18.4 | 400 | ≥1 evidenced constraint or initiative per row | 8.6, 9.2 |
| 18.5 | 250 | `any×1` ecosystem evidence | 16.3, 9.5 |
| 18.6 | 400 | **Evidenced** contract/fiscal/leadership events only. No invented dates | 13.7, 6.1, 10.2 |

### §19 Account Strategy — `account-strategy`

| § | Env. | Evidence bar | Depends on |
|---|---:|---|---|
| 19.1 | 350 | ≥6 claims; weaknesses **must be populated** — an all-strengths SWOT is a V7 failure | 16, 11.5 |
| 19.2 | 400 | §18 non-empty; **every premise footnoted to an evidencing section** | 18 |
| 19.3 | 500 | Per-stakeholder props tied to `P-nn`; the Challenger insight is **one**, labelled `INFERRED`, derived from cited evidence | 10.6, 18 |
| 19.4 | 400 | Every theme tested against a **quoted** priority from §9.1 or §13.4 | 9.1, 13.4 |
| 19.5 | table | Capability Pack attached, else `[INTERNAL: validate]` throughout | Pack |
| 19.6 | 400 | ≥3 `P-nn` | 10.6 |
| 19.7 | 400 | ≥1 evidenced incumbent | 16.2, 16.5 |
| 19.8 | 350 | §7.4 sourcing posture and §15.7 disposition both read | 7.4, 15.7 |
| 19.9 | table | **All eight MEDDPICC fields present.** Each carries status, source, and a next validation action. Unknown fields are `[INTERNAL REQUIRED]` — **never blank** | 10.4, 10.6, 18 |

### §20 Pursuit Playbook — `playbook` · emits `A-nn`

| § | Env. | Evidence bar | Depends on |
|---|---:|---|---|
| 20.1 | 400 | **Each quick win tied to an evidenced pain AND a named `P-nn`** | 7.5, 10.6, 18 |
| 20.2 | 350 | `O-nn` reference per row | 18 |
| 20.3 | 350 | `O-nn` reference per row | 18 |
| 20.4 | 300 | `P-nn` reference per row | 10.6 |
| 20.5 | 250 | Ties to §19.4 themes | 19.4 |
| 20.6 | table | 7–12 `A-nn`: owner, date, success metric. **Coverage is mechanically checked (V7e):** every `HYPOTHESIS`/`VALIDATE` opportunity and every `materiality: high` gap must appear as an action or a §19.9 validation item | 18, 19.9, gaps |

---

## §21 — Appendices

| § | Owner | Evidence bar | Notes |
|---|---|---|---|
| 21.1 | `assembly` (deterministic) | Merged manifest | **Includes failed retrievals with their reason.** Generated from state, not written |
| 21.2 | `appendices` | none | Compiled from the assembled body; expands each term once |
| 21.3 | `appendices` | `gov` statements | As filed **plus** reconciliation to any adjusted figures used |
| 21.4 | `appendices` | Dated claims across §9, §13, §14 | 12–24 mo |
| 21.5 | `appendices` | §13.3 researched | Classifications included. Opt |
| 21.6 | `appendices` | `any×1` | Opt |
| 21.7 | `appendices` | `T3×1` with **named source + method** | Opt |
| 21.8 | `verification` | Verification Pass executed | **Verification Summary first**, then scoring logic and calibration |
| 21.9 | `assembly` (deterministic) | Merged ledger | The 40–60 most material claims, ranked by materiality then confidence |
| 21.10 | `assembly` (deterministic) | — | Emitted **blank with `[INTERNAL]` markers** when not supplied |
| 21.11 | `contradiction` → `assembly` | — | Contradictions with resolution + rationale, plus the full `G-nnnn` register |
| 21.12 | `assembly` (deterministic) | Coverage records from every agent | Per section: expected vs retrieved classes, stop reason, residual risk |

---

## Cross-cutting hard rules

1. **Single owner per section.** Two agents writing the same subsection is a merge conflict the
   harness cannot resolve. Route findings via `handoff`.
2. **The evidence bar decides whether you write, not how well you write.** Below the bar: heading +
   one-line gap + `G-nnnn`. Never filler, never a plausible-sounding paragraph.
3. **"Empty is a valid render"** appears on §3.7, §5.7, §6.10, §7.6, §9.4, §10.8, §12.5, §13.7,
   §14.4, §14.9, §16.3. For these, an empty section must **say it is empty and what was searched** —
   silence is not the same as absence.
4. **`structurally-inapplicable` ≠ gap.** Applied per the ownership-form branch; does not depress
   the §21.12 scorecard.
5. **§3–§17 contain no the pursuing organization content** except §15.6. V7a is a BLOCKER.
6. **Envelopes are ceilings on ambition, not floors on output.** A 200-word §12.5 that says what was
   found and what was not beats a 400-word one that pads.
