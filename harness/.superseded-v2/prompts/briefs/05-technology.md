# Brief — `technology` (block 5)

**Stage** 1 · **Owns** §6.1–6.7 · **Block** `500`–`599` · **Envelope** ~3,300 w
**Output** `<RUN_DIR>/sections/06-technology.md` · **Fragment** `technology.json`

Read `_common.md` first. **Tier 2 — write nothing about the pursuing organization.**
You score **Model 2 (Digital Maturity)**. Read `blueprint/scoring-rubrics.md`.

## Mission

Establish what the client actually runs, how modern it is, and — new in v2.1 — **how they source
and operate it**. §6.6 is the highest-value section this agent produces: sourcing posture predicts
deal shape better than any other single fact in the dossier, and it had no home in v2.0.

## §6.1 Known Technology Stack — ~600 w · bar ≥5 evidenced rows, each `any×1`

An inventory table where **every row carries its own source and confidence**. No row without
evidence. Domains: ERP · CRM · HCM · data platform · integration/middleware · analytics/BI ·
collaboration · plus the domain systems from the vertical module's **S** block.

Evidence hierarchy, best to worst: client case study published by the vendor (T4, and usually the
best available) · client executive naming the system publicly (T2) · vendor press release (T4) ·
conference talk by a client employee (T4) · job posting requiring the system (T5, `[UNVERIFIED]`).

**The vertical module's S block is a search checklist, not an answer key.** Searching for evidence
of an MES is correct. Writing that the client runs an MES because manufacturers typically do is
the single most likely fabrication in this harness.

Where evidence is thin, an honest 6-row table beats a 20-row table with 14 guesses. Deployment
posture (cloud/on-prem/hybrid, version, scope) only where evidenced.

## §6.2 Cloud & Infrastructure Posture — ~400 w · bar `any×2`

Hyperscalers in evidence and in which domains · migration programmes with dates and disclosed
scope · stated multi-cloud or single-cloud posture · data-centre footprint and any exit programme ·
`V-ENR` / `V-MFG`: the OT/IT boundary, which is a **delivery constraint**, not a preference.

## §6.3 Data & Analytics Maturity — ~400 w · bar `any×2`

Data platform evidence · governance signals (named CDO, published policy, catalogue tooling) ·
analytics footprint and where it sits organisationally · data-quality or fragmentation problems
the client has acknowledged publicly.

This section drives Model 3's heaviest-weighted dimension (data readiness, 25%). Evidence here is
disproportionately valuable — spend budget accordingly.

## §6.4 Digital Maturity Assessment — ~500 w · Model 2

Score all six dimensions. **Each needs ≥1 claim ID or is scored `n/e` and excluded with the
remaining weights reweighted and shown.** Suppress the composite if ≥2 dimensions are Low
confidence — substitute a qualitative assessment naming which dimensions failed and why.

Render: dimension · weight · score · anchor met · claim IDs · confidence, then composite, band,
and the mandatory "decision aid, not a measurement" framing.

## §6.5 Legacy Constraints & Modernization Needs — ~400 w · bar `T2×1` exec stmt or `T5×3` hiring

Evidenced technical debt — **acknowledged by the client** wherever possible: modernisation
programmes imply the debt they address; incident history implies fragility; COBOL/mainframe
hiring implies a legacy estate; exec statements about "simplifying the technology landscape" are
direct evidence.

Client-acknowledged constraints are worth more than inferred ones, because §11 can cite them as
`CONFIRMED` need evidence rather than `HYPOTHESIS`.

## §6.6 Sourcing & Operating Model — ~500 w · `NEW v2.1` · bar `T1–2×1` locations **or** `T4×2` SI/GCC

The most important addition in v2.1. Four questions:

**1. Captive / GCC footprint.** Does the client run its own offshore or nearshore capability
centres? Where, how large, which functions, when established, expanding or contracting? Search:
GCC/GBS announcement press · careers pages filtered by city · local business press in India,
Poland, Mexico, Philippines, Costa Rica, Romania · LinkedIn location signals · `corporate`'s
§2.4 handoff.

**2. In-house vs. outsourced split by function.** Which functions are run internally vs. by third
parties — application development, infrastructure, service desk, BPO, engineering? What has the
client said publicly about that split?

**3. Outsourcing history.** Prior SI relationships and how they ended · insourcing or repatriation
moves and their stated rationale · managed-service vs. staff-augmentation posture · any public
transition, rebid, or consolidation.

**4. Procurement posture toward vendors.** Stated vendor-consolidation or vendor-rationalisation
drives · preferred-supplier programmes · public statements about partner strategy.

Why this matters, stated plainly for the reader: a client with a 4,000-person captive in
Hyderabad, a stated consolidation drive, and a history of insourcing is a fundamentally different
pursuit from one that outsources everything to two incumbents. §12.5 derives the commercial
construct directly from this section — and gets it wrong without it.

Gap-tolerant: much of this is genuinely not public. `[DATA GAP]` with an account-team-validation
path is the correct output where evidence is absent, and these gaps belong in §13.4.

## §6.7 Operational Pain Points & Process Hotspots — ~500 w · `+v2.2` · bar ≥3 evidenced pain points

**Where friction lives at the process level.** This is where most §11 opportunities originate, and
in v2.0 it had no home — pain points were "folded into §11 need-evidence claims" but nothing
*produced* the operational view. You produce it. Two parts:

**1. Core process read.** For the end-to-end processes that matter in this business (Order-to-Cash,
Procure-to-Pay, Hire-to-Retire, Record-to-Report, Plan-to-Produce, claims/servicing, and the
vertical module's domain processes), note current-state maturity where evidenced. Keep it to the
processes with a *signal* — this is not an exhaustive process catalogue.

**2. Ranked pain-point register.** The core output. Each evidenced operational pain point as a row:
`# · pain point · function/process · severity (1–5, with rationale) · evidence · automation/AI
relevance`. Evidence comes from: earnings-call operational commentary (margin pressure, service
levels, backlog, manual effort) · quality/incident/recall disclosures · analyst or trade-press
operational critique · hiring surges for remediation/transformation roles (T5, `[UNVERIFIED]`) ·
the client's own "we need to simplify/modernise X" statements (the strongest evidence — cite as
`CONFIRMED`-grade need in §6.5 style).

**Hard vendor-neutrality rule.** This section is the most tempting place in the whole dossier to write
a solution. **Do not.** No "the pursuing organization solution" column, no `O-nn` (they do not exist yet — F7b), no "we
can". The neutral flag is *automation/AI relevance* — "high manual effort, rules-based, high volume"
describes the pain, not the fix. §11 turns these into opportunities; you only surface and rate them.
A pain point here without evidence is filler — if you cannot get to three evidenced ones, render the
heading, a one-line gap, and a `G-5nn`, and move on.

## Fragment duties

- `canonical_facts_proposed`: named ERP/CRM/data platform where evidence is T1–T4; GCC locations
  and scale.
- `scoring_inputs.digital_maturity`: full Model 2 block.
- `handoff` to `ai-posture`: data-platform and governance findings for Model 3 dim 2.
- `handoff` to `account-strategy`: sourcing posture — flag as the §12.5 input.
- `handoff` to `ecosystem`: every vendor you evidenced, so §9.1 can reconcile.
- `handoff` to `opportunity`: the §6.7 pain-point register — these are prime §11 need-evidence
  claims. Tag the high-severity, client-acknowledged ones `materiality: high`.

## Traps

- Job postings are T5. They may support `[UNVERIFIED]` and `[INFERENCE]`, **never** `[FACT]`.
- Vendor case studies overstate deployment scope. "Implemented X" often means one business unit —
  say what was actually evidenced.
- Technology facts decay in 6–12 months. Carry signal recency on every row; flag `[stale]`.
- Do not assess AI here beyond the data foundation — §7 belongs to `ai-posture`. The boundary:
  you own the substrate, they own what runs on it.
