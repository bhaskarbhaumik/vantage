# AID Dossier Blueprint v2.2

> **File path note.** This file keeps the `aid-blueprint-v2.1.md` path for reference stability —
> every brief, `_common.md`, and the workflow point at it. The *content* is now v2.2; the harness
> self-name (`aid-v2`, "AID v2.1 harness") is unchanged. Blueprint version and harness generation
> are allowed to differ.

**Base:** `prompts/aid-prompt-v2.md` Deliverable B (v2.0.0-P), as extended by v2.1.
**Status:** Backward-compatible enhancement. All v2.0 **and v2.1** section numbers are preserved;
v2.2 additions are appended within existing sections (new sub-sections at the end of a §, new
required elements inside a sub-section) so no existing ID moves. v2.2 restores the decision-relevant
coverage of the v1.2 21-section dossier (`outputs/guidewell/guidewell-aid.md`) that v2.0's
consolidation left without a canonical home — as single-owner, evidence-barred, gap-tolerant
sections, **not** as the four-way duplication v2.0 deliberately removed.

---

## 1. Architecture

| Tier | Name | Role | Written when | the pursuing organization content |
|------|------|------|--------------|-------------|
| 0 | Research Control Plane | Scope, plan, gaps, QA status | First (0.1–0.3) and last (0.4–0.6) | None |
| 1 | Executive Decision Brief | ≤3 pages; the only part many executives read | **Last** — derived from Tiers 2–3 | Yes (conclusions only, traceable) |
| 2 | Core Intelligence Dossier | Client reality, evidence-led | Stage 1 | **No** (neutral relevance flags only) |
| 3 | Pursuit Playbook | the pursuing organization strategy derived from Tier 2 | Stage 3 | Yes |
| 4 | Evidence Appendices | Provenance, registers, detail | Assembled last | No |

**ID namespaces:** sources `S-nnn`, claims `C-<section>-nn`, opportunities `O-nn`, use cases
`U-nn`, stakeholders `P-nn`, risks `R-nn`, gaps `G-nnn`, actions `A-nn`, contradictions `X-nnn`,
open questions `Q-nnn`, visual specs `VZ-nnn`, vertical modules `V-<CODE>`.
Allocation under parallel execution: `harness-v2/prompts/id-allocation.md`.

---

## 2. Changelog — what v2.1 changes and why

| # | Change | Type | Rationale |
|---|--------|------|-----------|
| 1 | Visual specs renamed `V-nn` → **`VZ-nn`** | **Defect fix** | v2.0 used `V-` for both visual specs and vertical modules (`V-HLS`). Ambiguous under any automated ID resolution; QA check F1b could not distinguish them. |
| 2 | **§0.6 Reader's Map** added | New | A 40–60 page dossier serves four audiences (Exec / Sales / Solution / Delivery). v2.0 defined the audiences in §0.2 but never told each audience which sections to read. One table, high leverage. |
| 3 | **§1.8 Material Unknowns** added | New | v2.0's central design bet is that declared gaps beat invented facts — but gaps live only in Appendix F, which executives never open. Surfacing the top 3 high-materiality gaps *in the brief* is what makes the anti-fabrication architecture visible to the decision-maker, and it pre-empts "why doesn't this cover X". |
| 4 | **§3.6 Client's Customers & Demand Drivers** added | Restoration | v2.0's migration table dissolved v1 §12 (Customer & Market) into §4.1 and §3.2. For a services pursuit, *who the client sells to* drives opportunity framing (their CX programs, their channel economics, their end-market cyclicality). v2.0 over-corrected on de-duplication and left no canonical home. |
| 5 | **§6.6 Sourcing & Operating Model** added | **Structural gap** | The single most predictive factor for an IT-services deal shape — GCC/captive footprint, outsourcing history, in-house vs. vendor posture, prior SI transitions — had no home in v2.0. v1 §7 was folded into §6.5 "legacy constraints", which is about technical debt, not sourcing posture. This is the most important addition in v2.1. |
| 6 | **§9.5 Contract & Renewal Signal Map** added | New | v2.0 correctly forbids inventing contract expiry dates, but then leaves *evidenced* renewal signals (public-sector award notices, disclosed multi-year commitments, RFP publications, transition announcements) with nowhere to go. Gap-tolerant by construction: empty is a valid render. |
| 7 | **§13.6 Kill Criteria & Disengagement Triggers** added | New | Tier 3 is the only the pursuing organization-positive layer and therefore the only one with a structural optimism bias. Naming in advance the conditions under which the pursuing organization should *stop* pursuing is the cheapest available counterweight, and it makes §1.1's verdict falsifiable. |
| 8 | **Evidence Sufficiency Bar** per section | New contract field | v2.0 says "triggered-but-empty sections render as a one-line gap" but never defines the threshold. Now each section carries an explicit minimum (see `section-contracts.md`), so "render or gap" is a decidable test rather than a judgment call — which matters when ten agents decide independently. |
| 9 | **Dossier Evidence Quality Index** in §0.5 | New | Per-claim confidence existed in v2.0; a dossier-level rollup did not. One number plus a distribution tells a reviewer in five seconds whether to trust the scores. |
| 10 | Section ownership + dependency DAG | New | v2.0's seven phases are strictly sequential. This harness runs Tier 2 as ten concurrent agents, which requires declared ownership and declared dependencies. See `section-contracts.md`. |
| 11 | All eight scoring rubrics instantiated | Fills placeholder | v2.0 Deliverable G left `{{Insert the eight scoring-model rubrics}}`. See `scoring-rubrics.md`. |
| 12 | All eight vertical modules written out | Fills placeholder | v2.0 named `V-HLS`…`V-GOV` and their anchor points but never authored their content. See `vertical-modules.md`. |

Everything not listed above is unchanged from v2.0 and governed by `prompts/aid-prompt-v2.md`.

---

## 2b. Changelog — what v2.2 adds and why

v2.2 is a **coverage-restoration** pass. Mapping every v1.2 sub-section (as rendered in
`outputs/guidewell/guidewell-aid.md`) against the v2.1 blueprint surfaced ~15 old items with **no
canonical home** in v2.1 — content v2.0 either dissolved into a neighbour or dropped. Most old
content *was* covered (renamed and merged); these are the genuine gaps. Each is restored under a
single owner with an evidence bar, so it degrades to a one-line gap when unevidenced rather than
inviting filler. No duplication is reintroduced: stakeholders, regulatory, partnerships, SWOT, and
opportunities remain analysed exactly once.

**New sub-sections (own numbers, own evidence bar):**

| # | Added | Owner | Restores (v1.2) | Rationale |
|---|-------|-------|-----------------|-----------|
| 1 | **§5.6 Innovation & R&D Profile** `NEW v2.2` | `strategy` | §9.4, §15.5 | R&D intensity, innovation labs, CVC/venture arms, and experimentation culture had no home. Distinct from §5.2 programmes and §7 AI posture; points to Appendix I for patents. |
| 2 | **§6.7 Operational Pain Points & Process Hotspots** `NEW v2.2` | `technology` | §7.2, §7.5 | The single highest-value restoration. v2.0 "folded pain points into §11 need-evidence claims" but nothing *produced* the operational view opportunities derive from. vendor-neutral: evidenced pain, not "the pursuing organization solution" columns. |
| 3 | **§8.4 Workforce Profile & Talent Strategy** `NEW v2.2` | `leadership` | §10.7 | Aggregate workforce (headcount trend, geo/functional mix, attrition, union exposure, reskilling) — distinct from §5.5 forward hiring signals. Aggregate only; no individual profiling (F4b still binds). |
| 4 | **§10.6 Legal & Litigation Exposure** `NEW v2.2` | `risk-reg` | §14.3 | Material litigation, enforcement actions, consent decrees — a distinct evidence class (dockets, 8-K, legal-proceedings note). Empty is a valid render. |
| 5 | **§10.7 Scenario Analysis & Stress Points** `NEW v2.2` | `risk-reg` | §14.6 | Base/Bear/Bull on the 2–3 variables that most move the client's investment capacity and transformation timing. Explicitly `[INFERENCE]`/`[ESTIMATE]`; feeds §13.1 timing and the §1.1 thesis. |

**New required elements (folded into an existing sub-section, no new number):**

| Added element | Folded into | Restores | Note |
|---------------|-------------|----------|------|
| Industry value-chain positioning | §3.1 | §4.4 | Where the client sits and where value/AI pools — feeds §11 framing. |
| Macroeconomic & geopolitical demand drivers | §3.1 | §4.7 | Market-level macro; enterprise geopolitical *risk* stays in §10.1. |
| Product & service portfolio (by BU, lifecycle stage) | §3.6 | §12.2 | Inventory that anchors demand analysis; cross-refs §2.2, §4.1. |
| Brand perception & reputation signals | §3.6 | §12.5 | Sentiment/Glassdoor/rank — heavily anti-fabrication flagged (no invented NPS/CSAT). |
| Cost structure & profit pools | §4.1 | §5.6 (v1.2) | Top cost drivers and highest-margin pools — where efficiency opportunities sit. |
| Mission, vision & values | §2.1 | §3.2 | Two lines for messaging-alignment; not a values essay. |
| Emerging-technology bets | §7.3 | §8.3.3 | IoT/digital twin/blockchain/AR-VR/quantum — evidenced only; §7.3 stays Opt. |
| IT organisation & governance structure | §8.2 | §8.5 | CIO/CTO reporting line, IT governance model, budget ownership. |

**New appendix:** **L Glossary & Acronyms** `NEW v2.2` (restores v1.2 §21.2) — compiled by
`assembly` from acronyms actually used in the body. Mints nothing.

**Ownership impact:** no new agents, no new ID blocks. Sections owned by `strategy`, `technology`,
`leadership`, and `risk-reg` extend by one or two sub-sections each; `market` and `financials`
absorb required elements. See `section-contracts.md` and `prompts/id-allocation.md` (both updated),
which also **fix three stale v2.1 ownership rows** (`market` now correctly lists §3.6, `technology`
§6.6, `ecosystem` §9.5 — all present in the v2.1 blueprint but omitted from the old allocation table).

Everything not listed here or in §2 is unchanged from v2.0/v2.1.

---

## 3. Blueprint

Legend — **Core** (all accounts) · **Pub** (public only) · **Priv** (private adaptation) ·
**V-\*** (vertical module) · **Opt** (optional deep dive) · **Input** (rendered only from
provided the pursuing organization input). Rows marked **`NEW v2.1`** are additions.

### Tier 0 — Research Control Plane

| Section | Purpose | Primary questions | Expected evidence | Output | Cond. |
|---------|---------|-------------------|-------------------|--------|-------|
| 0.1 Dossier Scope Statement | Bound the analysis | What entity, geographies, BUs, time horizons are in and out of scope? | Input variables + Stage-0 verification | Prose ≤200 w | Core |
| 0.2 Key Intelligence Questions | Focus research on decisions | The 5–8 questions this dossier answers, mapped to Exec/Sales/Solution/Delivery | Derived from pursuit objectives | Table | Core |
| 0.3 Research Plan & Source Strategy | Make research auditable | Which source tiers, in what order, with what stop rules? | Stage-0 planning output | Table + prose | Core |
| 0.4 Assumptions, Exclusions & Open Contradictions | Protect the reader from silent uncertainty | What was assumed? What conflicts remain unresolved? | Contradiction + assumption state | Table | Core |
| 0.5 As-of Dates, Freshness Map, Evidence Quality & QA Status | Temporal integrity + quality signal | How current is each data class? How strong is the evidence overall? Did QA pass? | Claim recency metadata; Evidence Quality Index; QA gate output | Table | Core |
| **0.6 Reader's Map** `NEW v2.1` | Route each audience to what it needs | Which 5–8 sections matter to Exec / Sales / Solution / Delivery respectively? | Derived from §0.2 audience mapping | Table | Core |

### Tier 1 — Executive Decision Brief (≤3 pages, written last)

| Section | Purpose | Primary questions | Expected evidence | Output | Cond. |
|---------|---------|-------------------|-------------------|--------|-------|
| 1.1 Account Thesis | One-paragraph verdict | Should the pursuing organization invest in this account now, and on what basis? | Synthesis of §11–13, claim-traceable | Prose ≤150 w | Core |
| 1.2 Company Snapshot Card | Orient the reader in 30 seconds | Who is this company, at what scale, led by whom? | Canonical facts (T1/T2) | Factsheet table, gap-tolerant | Core (Priv drops market fields) |
| 1.3 Top Findings & Implications | The 7–10 insights that change decisions | What did research reveal the account team does not already know? | Highest-materiality Tier 2 claims | Table: Finding · Evidence · Implication · Confidence | Core |
| 1.4 Opportunity Themes | Where the money is | Top 5 themes with scores | §11 register (`O-nn`) | Table | Core |
| 1.5 Risks & Watchpoints | What could kill pursuit or delivery | Top 5–7 risks with mitigation stance | §10 + §12 (`R-nn`) | Table | Core |
| 1.6 Engagement Readiness Assessment | Overall go/no-go signal | How ready is this account for the pursuing organization engagement? | Scoring Model 1 | Scorecard or qualitative fallback | Core |
| 1.7 30/90/180-Day Actions | Make it operational | Who does what by when? | §13.5 (`A-nn`) | Table | Core |
| **1.8 Material Unknowns** `NEW v2.1` | Make the gaps visible where decisions are made | What are the 3 highest-materiality things we could **not** establish, and what would it take to close them? | Appendix F, filtered to `materiality: high` | Table: `G-nnn` · What's missing · Why it matters · Resolution path · Owner | Core |

### Tier 2 — Core Intelligence Dossier (vendor-neutral)

#### §2 Company Profile & Corporate Structure

| Section | Purpose | Primary questions | Expected evidence | Output | Cond. |
|---------|---------|-------------------|-------------------|--------|-------|
| 2.1 Corporate Identity & Evolution | Compressed history that explains the present | What path led to today's structure and strategy? Which pivots still matter? | Company history, filings, major-event coverage | Prose ≤400 w + optional `VZ-nn` timeline | Core |
| 2.2 Business Unit & Segment Map | How the company organizes value | Reported segments, their scale, leadership, mandate | Segment reporting, org announcements | Table + prose | Core (Priv: best-available) |
| 2.3 Ownership, Governance & Control | Who controls decisions and capital | Ownership >5%, board composition, control dynamics | DEF 14A / statutory filings | Table + prose | Pub (Priv: sponsor/founder control) |
| 2.4 Global Footprint | Where the company operates and builds | Key locations by function (HQ, plants, R&D, GCC/GBS) | Filings, careers pages, press releases | Table | Core |

#### §3 Market & Competitive Context

| Section | Purpose | Primary questions | Expected evidence | Output | Cond. |
|---------|---------|-------------------|-------------------|--------|-------|
| 3.1 Industry Structure & Dynamics | Frame the pressures on the client | Market definition, sourced size/growth, structure, top 5–7 trends and their client-specific impact; **`+v2.2`** where the client sits in the industry **value chain** and where value/AI pools; **`+v2.2`** macro & geopolitical demand drivers acting on the market | Retrieved analyst summaries, trade press, filings | Prose + trend table | Core; trend library from `V-*` |
| 3.2 Competitive Position | Where the client wins and loses | Named competitor set, relative position, share direction | Filings, credible share estimates, trade press | Table + prose | Core |
| 3.3 Peer Benchmarking | Quantified relative performance | How does the client compare to 3–5 named peers on growth, margin, digital posture? | Peer filings | Benchmark table | Pub (Priv: qualitative) |
| 3.4 Client-Reality SWOT | Consolidated competitive assessment | Sustainable advantages and structural vulnerabilities | Synthesis of §2–3 claims | 2×2 with claim IDs | Core |
| 3.5 Regulatory Context Pointer | Avoid duplication | Which regulations shape the industry? | Cross-reference | 1 line → §10.2 | Core |
| **3.6 Client's Customers, Demand & Portfolio** `NEW v2.1` `+v2.2` | Understand the demand the client is serving and what it sells into it | Who does the client sell to (segments, concentration, channel)? What drives their customers' spend? What CX/channel programs is the client running? **`+v2.2`** the product/service portfolio by BU with lifecycle stage; **`+v2.2`** brand perception & reputation signals (rank/rating/sentiment — never an invented NPS/CSAT) | Segment notes, MD&A, IR materials, trade press, rating/rank summaries | Table + prose ≤550 w | Core |

#### §4 Business Model & Financial Performance

| Section | Purpose | Primary questions | Expected evidence | Output | Cond. |
|---------|---------|-------------------|-------------------|--------|-------|
| 4.1 Revenue Architecture | How the company makes money | Streams, segment/geo mix and 3-year trend, pricing model, channel mix, customer concentration; **`+v2.2`** cost structure & profit pools (top cost drivers, fixed/variable split, highest-margin lines) | Segment notes, MD&A, IR | Tables + prose | Core |
| 4.2 Financial Performance & Health | Can they fund transformation? | 3–5 yr revenue/margin/FCF trend, leverage, liquidity, inflection points | Filings, earnings releases | Dashboard table + prose | Core (Priv: statutory or `[DATA GAP]`) |
| 4.3 Capital Allocation & Investment Capacity | Where discretionary money goes | CapEx/R&D/M&A/dividends/buybacks vs. FCF; implied tech-investment capacity | Cash-flow statements, MD&A, calls | Table + prose | Pub |
| 4.4 Technology & Transformation Spend Signals | Size the wallet honestly | What is disclosed or credibly estimable about IT/digital spend? | Filings, earnings calls, credible estimates — else `[ESTIMATE]` with method or `[DATA GAP]` | Prose + evidence table | Core |
| 4.5 Valuation & Investor Expectations | External pressure on management | Multiples vs. peers, analyst consensus direction, activist presence | Retrieved market data, rating actions | Table + prose | Pub |

#### §5 Strategy & Transformation Agenda

| Section | Purpose | Primary questions | Expected evidence | Output | Cond. |
|---------|---------|-------------------|-------------------|--------|-------|
| 5.1 Stated Strategic Priorities | The client's own words | 5–7 priorities from filings/earnings/investor day, each sourced and dated | Transcripts, annual report strategy sections, CEO letters | Table: Priority · Source · Date · Budget signal | Core |
| 5.2 Active & Announced Programs | Transformation in flight | Named programs, status, disclosed budgets/partners, timeline | Press releases, calls, trade press | Program register | Core |
| 5.3 M&A & Portfolio Moves | Structural change signals | Deals last 3 yrs (value, rationale, integration state), stated appetite | Deal announcements, filings | Table + prose | Core |
| 5.4 Leadership Statements Digest | Primary-source intent | Key themes from last 4 quarters of exec communication, short sourced quotes | Transcripts, interviews, keynotes | Theme table, quotes ≤25 w | Core |
| 5.5 Hiring & Investment Signals | What the org is actually building | Directional read of job postings, org announcements, disclosed investments (6–12 mo) | Careers pages, retrieved job listings, press | Signal table, hypothesis-grade | Core (detail → App. E) |
| **5.6 Innovation & R&D Profile** `NEW v2.2` | Where the company invents, and how it funds it | R&D spend/intensity trend; innovation labs/centres; corporate-venture / CVC arms and notable bets; university/startup partnerships (cross-ref §9.3); experimentation-culture signals | Filings (R&D line), IR, press, CVC announcements; patents → App. I | Prose ≤350 w + optional table | Core (gap-tolerant; empty is valid) |

#### §6 Technology, Data & Operating Model

| Section | Purpose | Primary questions | Expected evidence | Output | Cond. |
|---------|---------|-------------------|-------------------|--------|-------|
| 6.1 Known Technology Stack | Ground truth on platforms | Which ERP/CRM/HCM/data platforms are *evidenced*? Deployment posture where known | Vendor announcements, case studies, job postings (T5, flagged) | Inventory table with per-row evidence + confidence | Core; `V-*` adds domain systems |
| 6.2 Cloud & Infrastructure Posture | Modernization stage | Providers in evidence, migration signals, hybrid/multi-cloud stance | Hyperscaler PRs, job postings, exec statements | Table + prose | Core |
| 6.3 Data & Analytics Maturity | AI-readiness foundation | Data platform evidence, governance signals, analytics footprint | Job postings, conference talks, vendor cases | Prose + evidence table | Core |
| 6.4 Digital Maturity Assessment | Structured relative placement | Scored assessment across 6 dimensions (Model 2) | Synthesis of §5–6 | Rubric scorecard or qualitative fallback | Core |
| 6.5 Legacy Constraints & Modernization Needs | Where friction lives | Evidenced technical debt, fragmentation, stated modernization intent | Exec statements, incident history, hiring patterns | Prose with claim IDs | Core |
| **6.6 Sourcing & Operating Model** `NEW v2.1` | The strongest single predictor of deal shape | Does the client run captive/GCC centres, and where? What is the in-house vs. outsourced split by function? What is the outsourcing history — prior SI transitions, insourcing moves, managed-service posture? What is procurement's stated vendor-consolidation stance? | Filings (headcount/locations), GCC announcements, prior SI press, job postings, exec statements on sourcing | Table + prose ≤500 w | Core |
| **6.7 Operational Pain Points & Process Hotspots** `NEW v2.2` | Where friction lives at the process level — the origin of most opportunities | Which core end-to-end processes (O2C, P2P, H2R, R2R, plan-to-produce, claims, servicing…) are evidenced as painful? Ranked register of **evidenced** operational pain points: process · function · severity · evidence · automation/AI relevance (neutral flag, no the pursuing organization) | Exec statements, earnings-call operational commentary, incident/quality disclosures, analyst/trade press, hiring for remediation roles | Table + prose ≤500 w | Core (gap-tolerant) |

#### §7 AI & Automation Posture

| Section | Purpose | Primary questions | Expected evidence | Output | Cond. |
|---------|---------|-------------------|-------------------|--------|-------|
| 7.1 AI/GenAI Initiative Inventory | What exists today | Known AI programs, pilots, partnerships, AI leadership roles — each sourced | PRs, earnings mentions, talks, hiring | Register table | Core |
| 7.2 AI Maturity Assessment | Placement on the curve | Scored 6-dimension assessment (Model 3) | Synthesis of §6–7 | Rubric scorecard or qualitative fallback | Core |
| 7.3 Automation & Emerging-Tech Footprint | Beyond GenAI | RPA/IA evidence, automation CoE signals; **`+v2.2`** evidenced emerging-tech bets (IoT, digital twins, blockchain, AR/VR, quantum) and their stated rationale | Vendor cases, job postings, press | Prose + table | Opt |
| 7.4 Agentic Readiness Signals | Forward-looking assessment | API maturity, orchestration signals, governance posture | §6–7 claims; inference-heavy, labeled | Prose, `[INFERENCE]`-labeled | Core |

#### §8 Leadership, Organization & Buying Centers

| Section | Purpose | Primary questions | Expected evidence | Output | Cond. |
|---------|---------|-------------------|-------------------|--------|-------|
| 8.1 Executive Leadership Profiles | Who the pursuing organization must engage | CEO/CFO/CIO/CTO/CDO + relevant BU leaders: tenure, background, stated priorities, public statements — professional facts only | Company bios, filings, credible interviews | Profile table (`P-nn`) + short prose | Core |
| 8.2 Buying Centers & Decision Dynamics | How money gets approved | Technology/ops/finance buying centers, evidenced budget authority, procurement style, known cycle timing; **`+v2.2`** IT organisation & governance structure (CIO/CTO reporting line, IT governance model, budget ownership) | Org announcements, procurement disclosures, `[INFERENCE]` where needed | Table + prose, heavily flagged | Core; `V-GOV` adds procurement regulation |
| 8.3 Stakeholder Register (canonical) | Single source of truth for people | Influence/accessibility per stakeholder (Model 6) | §8.1–8.2 + the pursuing organization input | Register (`P-nn`) | Core |
| **8.4 Workforce Profile & Talent Strategy** `NEW v2.2` | The talent base the transformation runs on | Total headcount and trend; geographic/functional distribution; attrition where disclosed; union/labour exposure; reskilling & talent-strategy programmes; key talent risks — **aggregate only, no individual profiling** | 10-K human-capital disclosure, IR, sustainability report, credible press | Table + prose ≤400 w | Core |

#### §9 Vendor & Partner Ecosystem

| Section | Purpose | Primary questions | Expected evidence | Output | Cond. |
|---------|---------|-------------------|-------------------|--------|-------|
| 9.1 Technology Vendor Relationships | The incumbent landscape | Evidenced vendor relationships by domain, with signal recency | Vendor PRs, case studies, job postings | Registry table | Core |
| 9.2 SI & Consulting Landscape | Competitive incumbency | Which SIs are evidenced at the account, in what domains? Contract values only if disclosed | Press, analyst notes, hiring signals | Table + prose | Core |
| 9.3 Alliance & Ecosystem Moves | Strategic direction via partners | Hyperscaler/ISV/startup partnerships (12–18 mo) and what they signal | Announcements | Table | Core |
| 9.4 Displacement & Whitespace Assessment | Where a new entrant can enter | Displacement potential per incumbent (Model 8); whitespace domains | §9.1–9.3 + §5–7 | Assessment table | Core (vendor-neutral framing: "third-party entry potential") |
| **9.5 Contract & Renewal Signal Map** `NEW v2.1` | Timing intelligence, honestly bounded | What contract, renewal, or re-compete signals are **publicly evidenced** — award notices, disclosed multi-year commitments, transition announcements, published RFPs, tender portals? | Public procurement portals, 8-K/material-contract exhibits, award databases, vendor PRs | Table: Signal · Counterparty · Evidenced date · Window implied · Source · Confidence | Core — **empty is a valid render**; never estimate an expiry date |

#### §10 Risk, Regulatory & ESG

| Section | Purpose | Primary questions | Expected evidence | Output | Cond. |
|---------|---------|-------------------|-------------------|--------|-------|
| 10.1 Enterprise Risk Synthesis | Client's own risk view + analyst view | Top ~8 material risks distilled (not copied) with severity/likelihood | 10-K risk factors, news | Risk register (`R-nn`) | Core |
| 10.2 Regulatory & Compliance Landscape | Compliance pressure map | Applicable regimes, enforcement history, upcoming changes | Regulator sites, filings, legal press | Register | Core; `V-*` supplies regime list |
| 10.3 Cyber & Incident History | Trust and urgency signals | Documented incidents, disclosed posture, response investments | Breach disclosures, 8-Ks, credible press | Prose + table | Core |
| 10.4 ESG Position | License-to-operate + opportunity | Ratings where retrievable, targets, controversies | Sustainability reports, rating summaries | Table + prose | Opt (Core for `V-ENR`) |
| 10.5 Risk Implications for Pursuit & Delivery | Translate risk to the pursuing organization terms | Which client risks become the pursuing organization delivery/commercial risks (Model 7)? | §10.1–10.4, §10.6–10.7 | Table | Core — bridge section; **the whole of §10 is the last vendor-neutral analysis**, §10.5 its bridge |
| **10.6 Legal & Litigation Exposure** `NEW v2.2` | Distinct risk evidence class | Material pending litigation, regulatory enforcement, consent decrees, settlements, disclosed financial exposure | 10-K legal-proceedings note, 8-K, court dockets, credible legal press | Register table + prose ≤350 w | Core — **empty is a valid render**; never estimate an exposure figure |
| **10.7 Scenario Analysis & Stress Points** `NEW v2.2` | Forward-looking effect on investment capacity & timing | Base/Bear/Bull on the 2–3 variables that most move the client's transformation capacity and pursuit timing, each tied to evidenced drivers | Synthesis of §4 + §10.1 claims; macro sources | Prose ≤400 w, `[INFERENCE]`/`[ESTIMATE]`-labelled | Core |

### Tier 3 — Pursuit Playbook (organization-specific)

#### §11 Opportunity Portfolio

| Section | Purpose | Primary questions | Expected evidence | Output | Cond. |
|---------|---------|-------------------|-------------------|--------|-------|
| 11.1 Opportunity Register (canonical) | Single scored list | 8–15 opportunities (`O-nn`): need evidence, the pursuing organization fit, sizing basis, attractiveness + win-probability (Models 4–5), status | Tier 2 claims + the pursuing organization input | Master register | Core |
| 11.2 AI & Agentic Use-Case Backlog | The AI-specific slice | 8–12 use cases (`U-nn`) with paradigm, impact/feasibility, accelerator fit, HITL needs | §6–7 + `V-*` use-case library | Backlog table | Core |
| 11.3 Prioritization View | Decide sequence | Impact × feasibility × timing; explicit trade-offs | §11.1–11.2 | Prioritized table + optional `VZ-nn` | Core |

#### §12 Account Strategy

| Section | Purpose | Primary questions | Expected evidence | Output | Cond. |
|---------|---------|-------------------|-------------------|--------|-------|
| 12.1 Account SWOT (the pursuing organization lens) | Honest position assessment | the pursuing organization strengths/weaknesses at this account; opportunities/threats incl. incumbents | §9 + the pursuing organization input + §3.4 | 2×2 with IDs | Core |
| 12.2 Positioning Thesis | The narrative | Why the pursuing organization, why now, on what proof — as an internal memo | Tier 2 + §11 | Prose ≤300 w | Core |
| 12.3 Stakeholder Messaging Framework | Resonant messages | Per-persona value narrative tied to evidenced priorities (claim IDs required) | §5.1, §8, §11 | Table | Core |
| 12.4 Competitive Win Strategy | Beat the incumbents | Differentiation vs. evidenced incumbents; likely objections + counters | §9.2, §9.4 | Table + prose | Core |
| 12.5 Commercial & Governance Model | Deal shape | Recommended constructs matched to client procurement style and sourcing posture (§6.6); governance cadence | §6.6, §8.2, §11 | Prose + table | Core |

#### §13 Engagement Plan

| Section | Purpose | Primary questions | Expected evidence | Output | Cond. |
|---------|---------|-------------------|-------------------|--------|-------|
| 13.1 Entry Vehicles & Timing Calendar | When and how to move | Trigger events (fiscal cycle, leadership change, program milestones, contract signals from §9.5) mapped to entry actions | §4–5, §9 | Calendar table | Core |
| 13.2 Stakeholder Engagement Plan | Who-what-when | Per-stakeholder actions referencing `P-nn` and message IDs | §8.3, §12.3 | Plan table | Core |
| 13.3 Three-Horizon Pursuit Roadmap | Sequence the register | `O-nn` mapped to 0–6 / 6–18 / 18+ months with dependencies | §11.1 | Roadmap table | Core |
| 13.4 Validation Question Backlog | What sales must confirm | Every Hypothesis/Validate item as a question with owner | §11, gap register | Table | Core |
| 13.5 Action Plan | Commit | 7–12 owned, dated actions (`A-nn`) with success metrics | §13.1–13.4 | Action table | Core |
| **13.6 Kill Criteria & Disengagement Triggers** `NEW v2.1` | Make the thesis falsifiable | What observable conditions would mean the pursuing organization should stop investing in this pursuit? Which assumption, if disproved, collapses the thesis? What is the review date? | §1.1 thesis + §12.1 weaknesses + high-materiality gaps | Table: Trigger · Observable signal · Source to monitor · Decision if triggered · Review date | Core |

### Tier 4 — Appendices

| ID | Appendix | Purpose | Cond. |
|----|----------|---------|-------|
| A | Source Register | All `S-nnn`: tier, publisher, date, URL, accessed, reliability, access basis | Core |
| B | Claim-Evidence Register | All `C-nn` with type, sources, confidence, recency, materiality | Core |
| C | Financial Data Tables | 3–5 yr P&L/BS/CF as retrieved, with period labels | Pub (Priv: as available) |
| D | News & Events Timeline | Significant events, 12–24 mo | Core |
| E | Hiring Signal Detail | Role/skill/location analysis with retrieval date | Opt |
| F | Data-Gap & Validation Register | All `G-nnn`: what's missing, attempts, resolution path, materiality | Core |
| G | Scoring Logic & Rubrics | Rubric anchors, weights, calculations, confidence adjustments **actually applied** | Core |
| H | Research Log | Compact query → best source → section | Core |
| I | Patent & IP Analysis | Filing trends, domains | Opt |
| J | Vertical Module Detail | Full `V-*` output not inlined above | `V-*` |
| **K** | **Visual Specification Register** `NEW v2.1` | All `VZ-nnn` objects in one place so a downstream renderer needs only this appendix, not the whole dossier | Core (empty = valid) |
| **L** | **Glossary & Acronyms** `NEW v2.2` | Every industry/company/technical acronym used in the body, expanded once. Compiled by `assembly` from the assembled text — mints nothing | Core |

---

## 4. Conditional logic

- **Public company** — full blueprint.
- **Private company** — drop 2.3 (Pub variant), 3.3, 4.3, 4.5, Appendix C-full; substitute
  sponsor/ownership analysis, statutory-equivalent filings, clearly flagged secondary estimates.
  §4.2 degrades to `[DATA GAP]` rather than fabricating. §6.6 becomes *more* important, not less.
  **`v2.2`:** §6.7 (pain points), §8.4 (workforce), §10.6 (litigation) and §10.7 (scenarios) all
  apply to private companies on a thinner evidence base — render the gap, do not synthesise. §10.6
  legal exposure is often *more* discoverable than financials (court records are public).
- **Vertical modules** — self-contained, injected at declared anchors. See `vertical-modules.md`.
- **the pursuing organization-input-dependent** — §12.1 (partially) and any organization relationship history render only from
  `{{ACCOUNT_CONTEXT}}` / `{{KNOWN_RELATIONSHIP_CONTEXT}}`; otherwise a one-line
  "input not provided" note.

## 5. Depth profiles

| Profile | Target | Included | Stage-1 agents |
|---------|--------|----------|----------------|
| `BRIEF` | ~12–18 pp | Tiers 0, 1, 3 + slim Tier 2 (§2.1–2.2, 4.1–4.2, 5.1–5.2, 6.1, 6.6, 8.1, 9.1–9.2, 10.1) | 5 (`corporate+market` merged, `financials`, `strategy+ai` merged, `leadership+ecosystem` merged, `risk-reg`) |
| `STANDARD` | ~25–40 pp | Full blueprint incl. all v2.2 sections, Opt sections only where evidence exists | 10 |
| `DEEP` | ~40–60 pp | Full blueprint + all Opt sections + Appendices E, I, J | 10 + `vertical` runs expanded |

**v2.2 sections are `STANDARD`/`DEEP` only.** `BRIEF` deliberately omits §5.6, §6.7, §8.4, §10.6,
and §10.7 (and the folded elements in §3.1/§3.6/§4.1) — a smaller number of complete core sections
beats a wider shallow sweep. Appendix L (glossary) is produced at every depth; it is near-free.

Length envelopes are guides, never padding targets. A `STANDARD` run that honestly lands at
20 pages because evidence was thin is a **pass**, not a failure.
