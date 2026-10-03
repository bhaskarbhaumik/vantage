# Vantage Dossier Blueprint v3.0.0

**Source of truth:** `aid-20260829.md` — *Account Intelligence Dossier — Combined Prompt (Claude
Fable 5)*, v3.0.0 (2026-08-29), Vantage contributors.
**Supersedes:** `aid-blueprint-v2.1.md` (content v2.2). The v2 section numbering does **not**
survive — v3 renumbers to a 22-section structure (§0–§21). A migration table is at the end.

> This file says **what each section contains**. `section-contracts.md` says **who writes it, how
> long, against what evidence bar, and what it depends on**. `verification-protocol.md` says **what
> it is graded against**. Agents read all three at runtime; the workflow encodes none of them.

---

## 1. Architecture

| Range | Name | Role | Written when | the pursuing organization content |
|---|---|---|---|---|
| §0 | Run Contract & Preflight | Entity, ownership form, adapters, tier, budgets | **First** — hard gate | None |
| §1 | Executive Summary & Company Snapshot | The only part many executives read | **Last**, placed first | Yes — conclusions only, all traceable |
| §2 | Research Scope & Methodology | How the dossier was made, and how much to trust it | After the body | None |
| §3–§17 | The dossier body — client reality | Evidence-led research | Research phases | **None** |
| §18–§20 | Pursuit | the pursuing organization strategy derived from §3–§17 | Synthesis | Yes |
| §21 | Appendices & Reference Data | Provenance, ledgers, registers, scorecards | Assembled last | Evidence only |

**Output tiers** (set in §0):

| Tier | Contents | Harness behaviour |
|---|---|---|
| `EXECUTIVE` | §0–§2 + §1-level synthesis + top tables (~15–25K words of output) | Research waves run at reduced scope; §§3–17 render as the synthesis inputs only |
| `STANDARD` | §0–§20, condensed appendices | Full agent roster, condensed §21 |
| `FULL_ANNEX` | All 22 sections + all appendices + ledgers | Full roster, full §21, all optional subsections |

`FULL_ANNEX` is the default.

**ID namespaces** — sources `S-nnnn`, claims `C-<section>-nn`, gaps `G-nnnn`, contradictions
`X-nnnn`, questions `Q-nnnn`, opportunities `O-nn`, use cases `U-nn`, stakeholders `P-nn`, risks
`R-nn`, actions `A-nn`, charts `C-<sec>.<n>`, figures `F-<sec>.<n>`, tables `T-<sec>[.<n>]`,
vertical modules `V-<CODE>`. Allocation under parallel execution: `prompts/id-allocation.md`.

---

## 2. Blueprint

Legend — **Core** (every run) · **Pub** (public targets) · **Priv** (private/PE branch adaptation)
· **V-\*** (vertical enhancement) · **Opt** (rendered only where evidence exists) · **Gated**
(rendered only from the §21.10 Account-Team Input Sheet or the Capability Pack).

### §0 Run Contract & Preflight

The completed run-contract table, plus identity-resolution evidence (how the entity was
disambiguated), ownership-form determination, and adapter selections with rationale.

| Field | Content |
|---|---|
| Target (as given) | The requester's string |
| Entity candidates considered | The candidate list + the disambiguation reasoning |
| Resolved entity | legal name · LEI · CIK/registry ID · ticker(s)/exchange(s) · HQ |
| Ownership form | public / private-VC / private-PE / SOE / subsidiary / nonprofit / cooperative / partnership / family-group |
| Jurisdiction adapter(s) | per `blueprint/jurisdiction-adapters.md` |
| Reporting standard | US GAAP / IFRS / local · FY end month |
| Research languages | English + local languages actually used |
| Primary + secondary verticals | Detected from **revenue mix**, not codes alone |
| Output tier | EXECUTIVE / STANDARD / FULL_ANNEX |
| Fetch/search budget | Per-phase, per the system prompt |
| Exclusions | none unless stated |
| Capability Pack | ATTACHED (dated) / NOT ATTACHED → generic-capability rule |
| Account-Team Input Sheet | ATTACHED / NOT ATTACHED → internal-input gates |
| Precomputed financials | ATTACHED / NOT ATTACHED |
| As-of date | The run's research-as-of date |

**§0 is a hard gate.** Nothing downstream runs until it is complete. Entity ambiguity that cannot
be resolved is a **stop condition**, not an assumption.

### §1 Executive Summary & Company Snapshot *(written last, placed first)*

| § | Purpose | Content | Output | Cond. |
|---|---|---|---|---|
| 1.1 | Company-at-a-Glance | Legal name · trade name · founded · HQ · ticker/exchange/registry IDs/LEI · CEO (since) · employees (as-of) · revenue (FY0, currency) · EBITDA & margin (basis labeled) · market cap (date) *or* last-round valuation (Priv) · credit ratings (rated entity + instrument **per rating**) · industry (primary + secondary) · FY end · vertical(s) · website/IR URL. Vertical add-ons: regulator (regulated industries), backlog (EPC), AUM (asset managers), same-store sales (retail). Every field populated, cited `[S-id]`, or explicitly gapped | `T-1.1` | Core |
| 1.2 | Key Findings & Strategic Highlights | 7–10 most decision-relevant insights | `T-1.2` — # · Finding · Evidence `[S-ids]` · Status · Confidence · Implication for the pursuing organization | Core |
| 1.3 | Strategic Relevance for the pursuing organization | Engagement thesis; capabilities cited `[CAPABILITY-PACK]` or marked `[INTERNAL: validate]`. Every target-side premise anchored to a later section | Prose | Core |
| 1.4 | Top Opportunities | Top 5–8 by **public opportunity attractiveness** (1–5, evidence-based rationale). Win-probability column filled **only** from the Input Sheet, else `[INTERNAL REQUIRED]`. Ranges + reasoning, never bare scores | `T-1.4` — # · Opportunity · Evidence Basis · Attractiveness (1–5) · Win Prob · Horizon · Lead Practice | Core |
| 1.5 | Top Risks & Watchpoints | 5–7 material risks to pursuit / positioning / delivery: type, severity, likelihood, mitigation | Table | Core |
| 1.6 | Engagement Readiness Score | Weighted composite 0–100 with per-dimension evidence. Financial Health 20% · Digital Maturity 20% · AI Readiness 20% · Strategic Alignment 15% · Stated Priorities Fit 15% · Stakeholder Access 10%. **Stakeholder Access is scored only with account-team input**; otherwise `NOT ASSESSED` and the remaining weights are renormalized, with the renormalization shown | `T-1.6` | Core |
| 1.7 | Recommended Next Actions | 5–7 time-bound, owner-assigned steps | Table — Action · Owner Role · Deadline · Success Metric | Core |

### §2 Research Scope & Methodology

| § | Purpose | Content | Output | Cond. |
|---|---|---|---|---|
| 2.1 | Research Objectives | 4–6 intelligence questions, mapped by audience (Exec / Sales / Solution / Delivery) | Table | Core |
| 2.2 | Scope of Analysis | Boundaries, time horizons, exclusions (per §0) | Prose | Core |
| 2.3 | Source Base & Data Inventory | Source classes used, counts, recency, reliability | `T-2.3` | Core |
| 2.4 | Analytical Framework | Lenses applied; section dependency flow | `F-2.4` figure-spec | Core |
| 2.5 | Limitations, Assumptions & Data Gaps | **Every autonomous assumption**; dossier-level gaps; per-section confidence; interpretation constraints | Table + prose | Core |
| 2.6 | Claim Verification Protocol | This run's corroboration rule; claim counts by evidence status; where to be most cautious | Table + prose | Core |

---

### §3 Company Overview & Corporate Profile

| § | Purpose | Content | Output | Cond. |
|---|---|---|---|---|
| 3.1 | Company History & Evolution | 3.1.1 Founding & early history · 3.1.2 Major milestones & pivotal events (dated, cited) · 3.1.3 Recent transformation journey (3–5 yrs) | Prose + `F-3.1.2` figure-spec | Core |
| 3.2 | Mission, Vision & Core Values | Verbatim, cited; alignment notes for later messaging | Prose | Core |
| 3.3 | Corporate Structure & Subsidiaries | 3.3.1 BU/division breakdown · 3.3.2 Key subsidiaries & JVs with ownership %, geography, function (Exhibit 21 or jurisdiction equivalent) | `T-3.3.1` (BU · Revenue % · Headcount · Leader · Mandate · Relevance) · `T-3.3.2` · `F-3.3` | Core |
| 3.4 | Global Footprint & Geographic Presence | Locations by function; **V-\***: plants/capacity (Mfg), store count (Retail), DC/regions (Tech) | `T-3.4` + `F-3.4` | Core |
| 3.5 | Ownership, Governance & Scale | Ownership form (from §0); major holders **from the correct instruments** — proxy ownership tables + 13D/G (beneficial owners) + Forms 3/4/5 (insiders). **13F is holdings OF institutional managers, not issuer ownership** — label it as such. Board summary; scale metrics | Table + prose | Pub (Priv: sponsor/founder control) |
| 3.6 | Entity & Securities Map | Ultimate parent → operating parent → material subsidiaries; share classes, ADRs and ratios, listed venues, debt-issuing entities, LEIs/registry IDs, regulator IDs. **The identifier crosswalk every later section attributes facts against** | `T-3.6` — Entity · Relationship · Jurisdiction · IDs · Securities/Instruments | Core |
| 3.7 | Activism, Beneficial Ownership & Insider Activity | 13D/G positions and stated intent, activist campaigns, proxy contests, notable insider buying/selling patterns, control-change dynamics — each dated and cited | Table + prose | Pub |

### §4 Industry & Market Landscape

| § | Purpose | Content | Output | Cond. |
|---|---|---|---|---|
| 4.1 | Industry Overview & Classification | Codes (GICS/SIC/NAICS/NACE as available), structure, structural economics | `T-4.1` | Core |
| 4.2 | Market Size, Growth & Forecast | TAM/SAM with the **full definitional controls** (definition, unit, geography, base/forecast year, nominal/real, methodology, comparability caveats); show ranges where estimates disagree | `C-4.2` chart-data | Core |
| 4.3 | Key Industry Trends & Disruptions | Top 5–7 with impact on the target; GenAI/agentic disruption analyzed wherever plausible | Table + prose | Core |
| 4.4 | Industry Value Chain Analysis | Target's position; AI/digital value points; third-party intervention points (**neutral framing**) | `F-4.4` figure-spec | Core |
| 4.5 | Competitive Forces (Porter) | Each force scored **with cited evidence** | Table + prose | Core |
| 4.6 | Regulatory & Compliance Landscape | Per-regulation applicability fields; AI-specific regulation included; fines/enforcement history | `T-4.6` — Regulation · Jurisdiction · Entity · Applicability test · Effective date · Obligation · Compliance evidence · Enforcement authority · Exposure · Confidence · Source | Core; `V-*` supplies the regime list |
| 4.7 | Macroeconomic & Geopolitical Drivers | 3–5 forces; FX exposure **from filings**; impact on investment capacity | Prose + table | Core |

### §5 Business Model & Revenue Architecture

| § | Purpose | Content | Output | Cond. |
|---|---|---|---|---|
| 5.1 | Business Model Canvas | 9 blocks, evidence-grounded | `T-5.1` + `F-5.1` | Core |
| 5.2 | Revenue Streams & Segmentation | 5.2.1 by segment (3 FY, **reconciled to total** — the segment note governs) · 5.2.2 by geography (3 FY) · 5.2.3 by product/service line — growth engines vs decliners | `T-5.2.1`+`C-5.2.1` · `T-5.2.2`+`C-5.2.2` | Core |
| 5.3 | Customer Segments & Value Proposition | Who they sell to and why those buyers buy | `T-5.3` | Core |
| 5.4 | Pricing Model & Monetization Strategy | Disclosed pricing architecture and monetization levers | Prose | Core |
| 5.5 | Channel & Distribution Model | Routes to market, partner-vs-direct mix | Prose + table | Core |
| 5.6 | Cost Structure & Profit Pools | Top cost drivers, fixed/variable split, highest-margin lines | Table + prose | Core |
| 5.7 | Customer Concentration & Key Accounts | **Filing disclosure first** (10% customers etc.) | `T-5.7` | Core |
| 5.8 | Supply Chain & Procurement Overview | Suppliers, sourcing footprint, procurement posture | Prose + table | Core |
| 5.9 | Unit Economics & Operating KPI Dashboard | The 6–12 KPIs this business actually runs on, 2–3 yr trend + peer context | `T-5.9` | Core |

### §6 Financial Performance & Health

> All numbers reconcile to `precomputed-financials` where attached. The normalization policy
> applies throughout. Sector-appropriate frameworks for FS / insurance / REITs.

| § | Purpose | Content | Output | Cond. |
|---|---|---|---|---|
| 6.1 | Financial Summary | 3–5 year trend | `T-6.1` + `C-6.1` | Core |
| 6.2 | Income Statement Analysis | 6.2.1 Revenue growth — YoY, CAGR, organic/inorganic · 6.2.2 Profitability & margins vs peers (per §11.0 protocol) · 6.2.3 OpEx breakdown | `C-6.2.1` · `C-6.2.2` · `T-6.2.3` | Core |
| 6.3 | Balance Sheet, Leverage & Obligations | Debt structure **by issuing entity**, covenants where disclosed, maturity wall, pensions, leases, off-balance-sheet items | `T-6.3` + `C-6.3` | Core |
| 6.4 | Cash Flow Analysis | Operating / investing / financing bridge | `C-6.4` waterfall | Core |
| 6.5 | Capital Allocation | **Stated framework (quoted) vs revealed behavior** | `T-6.5` + `C-6.5` | Core |
| 6.6 | IT & Technology Spending | Reported, or `[ESTIMATED]` **with the method shown** | `T-6.6` + `C-6.6` | Core |
| 6.7 | Market Valuation & Investor Signals | Multiples vs peers (date-stamped), short interest, ownership shifts. **Priv branch:** funding/debt history, last-round terms | Table + prose | Pub / Priv-substituted |
| 6.8 | Credit Ratings & Analyst Consensus | Per rating: **rated entity, instrument, seniority**, agency, outlook, action date; consensus distribution + bull/bear theses | `T-6.8` | Pub |
| 6.9 | DuPont & Quality of Earnings | Where applicable per the normalization policy; one-offs, restatements, auditor changes, revenue-recognition flags | Table + prose | Pub, sector-gated |
| 6.10 | Guidance Credibility & Earnings-Surprise History | Guidance vs actuals across recent periods, estimate revisions, credibility implications | Table + prose | Pub |

### §7 Operations & Value Chain

| § | Purpose | Content | Output | Cond. |
|---|---|---|---|---|
| 7.1 | Operating Model Overview | How the company converts inputs to delivered value | `F-7.1` | Core |
| 7.2 | Core Business Processes | 5–7 E2E processes with pain level and automation potential | `T-7.2` + `F-7.2` | Core |
| 7.3 | Supply Chain & Fulfillment | Incl. supplier/facility evidence from trade and open-supply data where available | Prose + table | Core |
| 7.4 | Shared Services & Back Office | Outsourcing status, **named providers where evidenced**, GCC/captive footprint | Table + prose | Core |
| 7.5 | Operational Pain Points & Bottlenecks | Top 7, each tied to evidence with status tags | `T-7.5` + `C-7.5` | Core |
| 7.6 | Product Quality, Service Reliability & Complaint Signals | Outages (status-page history), recalls, regulator complaint databases (e.g. CFPB), app/service incidents, remediation — **sample sizes and windows stated** | Table + prose | Core (gap-tolerant) |

### §8 Technology Landscape & Digital Maturity

| § | Purpose | Content | Output | Cond. |
|---|---|---|---|---|
| 8.1 | Enterprise Technology Stack | 8.1.1 Core platforms (ERP/CRM/HCM) · 8.1.2 Cloud infrastructure & strategy · 8.1.3 Data & analytics platform (warehouse/lakehouse, BI, governance, MDM, lineage, residency/sovereignty) · 8.1.4 Enterprise architecture & integration landscape (APIs, middleware/iPaaS, event architecture, DevSecOps, observability, ITSM, contact centre, EUC) | `T-8.1.1` — Domain · Platform · Vendor · Deployment · Evidence · **Classification** · Confidence · Modernization Signal; `T-8.1.2` | Core |
| 8.2 | Digital Maturity Assessment | 6 dimensions, **anchored rubric**, evidence per score | `C-8.2` radar | Core |
| 8.3 | AI & Advanced Technology Adoption | 8.3.1 AI/ML/GenAI initiatives — models/platforms, partners, disclosed outcomes (**independent corroboration for outcome claims**), AI leadership · 8.3.2 Automation & RPA footprint · 8.3.3 Emerging technology bets · 8.3.4 **Agentic AI & ecosystem posture** — agent frameworks, MCP/tool-integration signals, copilot deployments, stated agent strategy | `T-8.3.1` | Core; 8.3.4 researched as its own topic |
| 8.4 | Cybersecurity Posture & Data Privacy | **Passive-public boundary.** Disclosed vs observed clearly separated; frameworks, incidents (dated), CISO identity | Table + prose | Core |
| 8.5 | IT Organization & Governance | CIO/CTO reporting line, governance model, budget ownership | `F-8.5` | Core |
| 8.6 | Legacy Constraints & Modernization Needs | Evidenced technical debt, fragmentation, stated modernization intent | `F-8.1` + prose | Core |

**Every stack entry carries a mention classification**: `CURRENTLY-USED` / `MIGRATING-TO` /
`EVALUATING` / `SKILL-PREFERENCE` / `AMBIGUOUS`. No entry reaches CONFIRMED on a single weak signal.

### §9 Strategic Priorities & Transformation Agenda

| § | Purpose | Content | Output | Cond. |
|---|---|---|---|---|
| 9.1 | Stated Corporate Strategy & Priorities | 5–7, each with a **verbatim quote (provenance class)** + relevance note | `T-9.1` | Core |
| 9.2 | Active Transformation Programs | Evidence-status tagged; budget/timeline only CONFIRMED/ANNOUNCED or `[ESTIMATED with basis]`; incumbents where evidenced | `T-9.2` + `F-9.2` | Core |
| 9.3 | M&A Strategy & Recent Transactions | 9.3.1 Acquisitions & divestitures (3 yrs) · 9.3.2 Pipeline & stated intent — **ANNOUNCED/OBSERVED-SIGNAL only, no invented deals** | `T-9.3.1` | Core |
| 9.4 | Innovation & R&D Focus | R&D spend/intensity, labs, CVC arms, university/startup partnerships | Prose + table | Core |
| 9.5 | Strategic Partnerships & Alliances | Named alliances and what they signal | Table | Core |
| 9.6 | Transformation Outcomes & Benefits Realization | **Announced vs delivered** milestones, KPIs, adoption evidence, failure/reset signals — the credibility check on §9.2 | Table + prose | Core |

### §10 Organizational Structure & Leadership

> Profiles contain **public professional facts and attributed statements only**. No sensitive
> personal data. No speculation about loyalties or motives.

| § | Purpose | Content | Output | Cond. |
|---|---|---|---|---|
| 10.1 | Board of Directors | Composition, tenure, committee structure, relevant backgrounds | `T-10.1` | Pub |
| 10.2 | C-Suite & Executive Leadership | 10.2.1 CEO profile & strategic orientation · 10.2.2 CIO/CTO/CDO/CAIO profiles — public statements, conference appearances, tenure; **prior-vendor exposure as a weak OBSERVED-SIGNAL hypothesis only** · 10.2.3 CFO & procurement leadership | `T-10.2` + `F-10.2` | Core |
| 10.3 | Business Unit Leadership | BU leaders and mandates | Table | Core |
| 10.4 | Functional Buying Centers | Evidence-tagged; **authority/budget claims marked INFERRED unless evidenced** | `T-10.4` | Core |
| 10.5 | Decision-Making Dynamics & Culture | Procurement centralization, budget cycle, RFP propensity — status-tagged | `T-10.5` + `F-10.5` | Core |
| 10.6 | Stakeholder Map for Pursuit | Canonical `P-nn` register; evidenced vs inferred marked | `T-10.6` + `F-10.6` | Core |
| 10.7 | Workforce Profile & Talent Strategy | Headcount trend, mix, attrition signals (**with sample-size discipline**), HR priorities — aggregate only | `T-10.7` + `C-10.7` | Core |
| 10.8 | Delivery Constraints | Works councils/unions, security clearances, localization and data-residency requirements, offshore restrictions, regulated-outsourcing rules, accessibility mandates — **everything that shapes a delivery model** | Table + prose | Core |

### §11 Competitive Positioning & Peer Benchmarking

| § | Purpose | Content | Output | Cond. |
|---|---|---|---|---|
| 11.0 | **Peer Set & Selection Protocol** | Candidate universe, selection dimensions, exclusions, fiscal/currency/accounting normalization, data vintage. **Stated once, applied throughout §11 and by every other agent that benchmarks** | Table + prose | Core — **written before any other §11 subsection** |
| 11.1 | Competitive Landscape Overview | Named competitor set and structure | `F-11.1` | Core |
| 11.2 | Market Position & Share | **Source + vintage per estimate**; comparability caveats | `C-11.2` | Core |
| 11.3 | Peer Financial Benchmarking | Normalized per §11.0 | `T-11.3` + `C-11.3` | Pub |
| 11.4 | Peer Technology & Digital Benchmarking | Comparable evidence only | `T-11.4` | Core |
| 11.5 | Competitive Advantages & Vulnerabilities | SWOT of the **target**, not of the pursuing organization | `F-11.5` | Core |
| 11.6 | Portfolio Frameworks | BCG / GE-McKinsey **only where per-BU market data exists**; else a qualitative assessment labeled as such | Table + prose | Opt |
| 11.7 | Win/Loss & Deal Intelligence | Public evidence vs `[INTERNAL]` **clearly split** | Table | Core |

### §12 Customer & Market Intelligence

| § | Purpose | Content | Output | Cond. |
|---|---|---|---|---|
| 12.1 | Customer Segmentation & Demographics | Segments and their economics | `C-12.1` | Core |
| 12.2 | Product & Service Portfolio | Portfolio by BU with lifecycle stage | `T-12.2` | Core |
| 12.3 | Go-to-Market Strategy & Channels | Incl. ad-transparency signals where available | `F-12.3` | Core |
| 12.4 | Customer Experience & Satisfaction | Public CSAT/NPS, **standardized benchmarks (e.g. ACSI) preferred over anecdote**; review signals with sample size / window / bias stated. **Never an invented NPS or CSAT** | Table + prose | Core (gap-tolerant) |
| 12.5 | Brand Perception & Reputation | Rankings, media sentiment (12 mo, **method stated**), reputation risks | `T-12.5` + `C-12.5` | Core |

### §13 Current Signals, Initiatives & Intent Intelligence

| § | Purpose | Content | Output | Cond. |
|---|---|---|---|---|
| 13.1 | Announced Strategic Programs (12–24 mo) | Dated, status-tagged | `T-13.1` + `C-13` | Core |
| 13.2 | Technology & Vendor Investments | Press, calls, procurement signals; status-tagged | Table | Core |
| 13.3 | Hiring & Talent Signals | **Posting window stated**; technologies classified per the mention rule; role density → investment priorities as OBSERVED-SIGNAL | `T-13.3` + `C-13.3` | Core |
| 13.4 | Recent Leadership Statements | Last 4 calls + investor day + interviews; **verbatim quotes with provenance class** | Table | Core |
| 13.5 | Partnership & Alliance Signals (12 mo) | Dated | `T-13.5` | Core |
| 13.6 | Analyst & Market Expectations | 12–24 mo forward | Table + prose | Pub |
| 13.7 | Procurement & Contract-Renewal Intelligence | RFP channels, framework agreements/vehicles, public contract awards + expiry dates (public sector), renewal evidence and uncertainty for commercial contracts — evidence-status tagged. **No invented renewal dates** | Table | Core — **empty is a valid render** |

### §14 Risk Landscape & Regulatory Environment

| § | Purpose | Content | Output | Cond. |
|---|---|---|---|---|
| 14.1 | Enterprise Risk Factors | Top 10 from the risk-factor disclosure (Item 1A or jurisdiction equivalent), **taxonomy-mapped (ISO 31000)** | `T-14.1` + `F-14.1` | Core |
| 14.2 | Regulatory & Compliance Requirements | Full applicability fields per the system rule | Table | Core |
| 14.3 | Legal & Litigation Exposure | Filings + court/regulator records; **disclosed** exposure amounts only | `T-14.3` | Core — empty is valid |
| 14.4 | Cybersecurity & Data-Breach History | Disclosed incidents (dated, cited), regulator actions, remediation | Table + prose | Core |
| 14.5 | Geopolitical & Macroeconomic Risks | Exposure by geography and channel | Prose | Core |
| 14.6 | Scenario Analysis | Base / Bear / Bull, **labeled analytical**, assumptions stated | Prose | Core |
| 14.7 | Risk Implications for Pursuit & Delivery | Which client risks become delivery/commercial risks. **The bridge out of the neutral body — still vendor-neutral in wording** | Table | Core |
| 14.8 | Sanctions, Export Controls & Third-Party Integrity | Screening against OFAC / EU / UK / UN lists (entity + known affiliates), export-control exposure, restricted-market operations, forced-labor/supply-chain integrity flags, critical-supplier risk — **from official lists; entity-match certainty stated** | Table | Core |
| 14.9 | Government Relations, Lobbying & Subsidies | Lobbying disclosures, political-spend transparency data, subsidies/incentives received, government contracts — **both a risk lens and a public-sector entry signal** | Table + prose | Core |

### §15 AI & Innovation Readiness Assessment

| § | Purpose | Content | Output | Cond. |
|---|---|---|---|---|
| 15.1 | AI Maturity Assessment | 6 dimensions, anchored rubric, **evidence + confidence per cell**; `NOT RELIABLY ASSESSABLE` allowed | `T-15.1` + `C-15.1` radar | Core |
| 15.2 | Data Readiness & Quality | Foundations the AI agenda depends on | Prose + table | Core |
| 15.3 | AI Use-Case Opportunity Map | 10–15 use cases (`U-nn`) **grounded in observed pain points/priorities — no generic filler**; impact × feasibility × paradigm × accelerator fit | `T-15.3` + `F-15.3` | Core |
| 15.4 | Agentic AI Opportunity Assessment | 5–8 opportunities tied to **§8.3.4 evidence** | `T-15.4` | Core |
| 15.5 | Innovation Ecosystem & Culture | Labs, OSS posture, publication/patent activity | Prose | Core |
| 15.6 | the pursuing organization Engagement Fit | Capability (**from the Capability Pack**) × opportunity fit scores | `T-15.6` + `F-15.6` | **Gated** — the one organization-specific subsection inside §3–§17 |
| 15.7 | Build–Buy–Partner Disposition | Sourcing history → deal-shape implications | Prose + table | Core |

### §16 Partnership & Vendor Ecosystem

| § | Purpose | Content | Output | Cond. |
|---|---|---|---|---|
| 16.1 | Major Technology Vendor Relationships | **Evidence type + classification + confidence per entry**; contract signals only as evidenced | `T-16.1` | Core |
| 16.2 | SI & Consulting Partnerships | Engagement domains evidenced; contract-timeline estimates **only with basis shown** | `T-16.2` + `F-16.2` | Core |
| 16.3 | Startup & Innovation Partnerships | Named, dated | Table | Core |
| 16.4 | the pursuing organization Current Relationship Status | **From the Account-Team Input Sheet**, else `[INTERNAL: account team to complete]` — never guessed | Table | **Gated** |
| 16.5 | Vendor Displacement Opportunities | Displacement potential per incumbent, neutral framing in-section | `T-16.5` | Core |

### §17 ESG, Sustainability & Corporate Responsibility

| § | Purpose | Content | Output | Cond. |
|---|---|---|---|---|
| 17.1 | ESG Ratings & Performance | **Provider, score, rating date each** | `T-17.1` + `C-17.1` | Core |
| 17.2 | Environmental Commitments & Carbon Strategy | Targets verbatim; Scope 1/2/3 from the sustainability report; SBTi validation status | `C-17.2` | Core |
| 17.3 | Social Responsibility & DEI | **Disclosed data only** | Table | Core |
| 17.4 | Governance & Ethics | Proxy-based comp alignment, controversy record | Table + prose | Pub |
| 17.5 | Sustainability-Driven Technology Opportunities | CSRD readiness, carbon platforms | Prose | Core |
| 17.6 | AI Governance & Responsible-AI Posture | Principles, governance bodies, EU AI Act readiness, controversies — risk lens **and** advisory opportunity | Table + prose | Core |

---

### §18 Opportunity Assessment

> Attractiveness comes from public evidence. Win-probability and account-revenue fields are **gated
> on the Account-Team Input Sheet** — else `[INTERNAL REQUIRED]`. Ranges and sizing logic are
> always shown; **never a bare number**.

| § | Purpose | Content | Output | Cond. |
|---|---|---|---|---|
| 18.1 | Strategic Account Potential | Per service line | `T-18.1` — Service Line · Yr1–Yr3 range · Sizing Basis · Attractiveness · Win Prob (gated) · Confidence | Core |
| 18.2 | Business Opportunity Themes | The 4–6 themes the register clusters into | `F-18` | Core |
| 18.3 | Functional Opportunity Mapping | By business function | `T-18.3` | Core |
| 18.4 | Technology & Transformation Opportunities | By technology domain | `T-18.4` | Core |
| 18.5 | Partnership & Co-Innovation Potential | Where a joint play beats a direct one | Prose | Core |
| 18.6 | Timing & Entry Points | Fiscal calendar, milestones, leadership changes, **evidenced contract events** | `T-18.6` + `C-18` | Core |

The canonical **Opportunity Register (`O-nn`)** is minted here: need evidence (claim IDs), sizing
basis, attractiveness 1–5, horizon, lead practice, status (`CONFIRMED` / `HYPOTHESIS` / `VALIDATE`).

### §19 Account Strategy & Engagement Plan

| § | Purpose | Content | Output | Cond. |
|---|---|---|---|---|
| 19.1 | Account SWOT (the pursuing organization perspective) | Honest position assessment | `T-19.1` | Core |
| 19.2 | Account Positioning Thesis | 2–3 paragraph internal memo; **premises footnoted to evidencing sections** | Prose | Core |
| 19.3 | Value Proposition & Challenger Hypothesis | Per-stakeholder value props; one Challenger-style commercial teaching insight derived from the evidence (what the target underappreciates about its own situation), **labeled INFERRED** | Table + prose | Core |
| 19.4 | Executive Messaging Themes | **Tested against their quoted priorities (§9.1, §13.4)** | `T-19.4` | Core |
| 19.5 | Solution Alignment | **Capability Pack references only** | `T-19.5` | Gated |
| 19.6 | Stakeholder Engagement Plan | Per-`P-nn` actions | `T-19.6` + `F-19.6` | Core |
| 19.7 | Competitive Win Strategy | vs incumbent SIs identified in §16.2 | Table + prose | Core |
| 19.8 | Commercial Model & Governance | Constructs matched to §15.7 and §7.4 sourcing posture | Prose + table | Core |
| 19.9 | **MEDDPICC Evidence & Gap Matrix** | Field by field — Metrics · Economic buyer · Decision criteria · Decision process · Paper process · Identified pain · Champion · Competition — each with status (public evidence / `[INTERNAL REQUIRED]`), source, and **next validation action** | `T-19.9` | Core |

### §20 Pursuit Playbook & Recommended Actions

| § | Purpose | Content | Output | Cond. |
|---|---|---|---|---|
| 20.1 | Quick Wins (0–6 mo) | **Each tied to an evidenced pain + a named stakeholder** | Table | Core |
| 20.2 | Medium-Term Growth (6–18 mo) | Sequenced from the register | Table | Core |
| 20.3 | Strategic Plays (18+ mo) | Sequenced from the register | Table | Core |
| 20.4 | Relationship-Building Priorities | Per `P-nn` | Table | Core |
| 20.5 | Marketing Messages & Content Gaps | What exists vs what is needed | Table | Core |
| 20.6 | Next Steps & Action Items | Canonical `A-nn` register: owned, dated, with success metrics | `T-20.6` + `C-20` + `F-20` | Core |

---

### §21 Appendices & Reference Data

| § | Appendix | Content | Cond. |
|---|---|---|---|
| 21.1 | **Source Manifest** | One record per source consulted: `[S-id]` · title · publisher · doc/accession ID · pub date · access date · URL · language · retrieval status · reliability tier · sections fed. **Includes failed retrievals with the failure reason** | `T-21.1` Core |
| 21.2 | Glossary | Industry/company/technical terms used in the body | Core |
| 21.3 | Detailed Financial Data Tables | As filed, **plus reconciliation to any adjusted figures used** | `T-21.3` (P&L / BS / CF) Pub |
| 21.4 | News & Events Timeline | 12–24 mo | `T-21.4` Core |
| 21.5 | Job-Posting Intelligence | Detail behind §13.3, **classifications included** | `T-21.5` Opt |
| 21.6 | Patent, Trademark & Open-Source Analysis | Patent trend + domains; trademark activity; public repos / OSS posture | Opt |
| 21.7 | Digital Presence Audit | Traffic (**named source + method**), social, thought leadership | Opt |
| 21.8 | Analytical Notes & Scoring Logic | **Verification Summary FIRST**, then methodology assumptions, scoring logic, confidence calibration | Core |
| 21.9 | **Claim Ledger** | The 40–60 most material claims: # · claim · section · `[S-ids]` · evidence status · verification method · final confidence | `T-21.9` Core |
| 21.10 | **Account-Team Input Sheet** | The internal-input template: current the pursuing organization revenue/contracts, relationships and access, pipeline, references, delivery history, exclusions. **Emitted blank with `[INTERNAL]` markers when not supplied** | Core |
| 21.11 | **Contradiction & Data-Gap Register** | Conflicting values found, resolution chosen + rationale, unresolved alternatives, decision impact; plus the full `G-nnnn` gap register | Core |
| 21.12 | **Source-Completeness Scorecard** | Per section: expected source classes vs actually retrieved, stopping reason (`diminishing_returns` / `budget` / `not_applicable`), residual risk | `T-21.12` Core |

---

## 3. Conditional logic

- **Public company** — full blueprint.
- **Private / PE-owned** — §6.7 substitutes funding/debt history and last-round terms for
  multiples; §6.8 renders only where rated; §3.5 becomes sponsor/founder control; §10.1 board
  becomes best-available. Confidence ceiling **MEDIUM** on unverifiable financial estimates. §7.4
  sourcing and §14.3 litigation are often *more* discoverable than financials (court records are
  public) — do not thin them.
- **State-owned / cooperative / nonprofit / partnership / family group / controlled subsidiary** —
  adapt §3.5, §6, §10.1, §17.4 to the form (ministry reports, Form 990s, cooperative reports).
  **Structurally inapplicable fields are marked inapplicable, not gapped.**
- **Vertical modules** — enhancements are injected at declared anchors. See `vertical-modules.md`.
- **Gated content** — §15.6, §16.4, §19.5, and every win-probability / account-revenue field render
  only from the Capability Pack or Account-Team Input Sheet; otherwise the `[INTERNAL…]` marker.

## 4. Output tier profiles

| Tier | Body | Appendices | Research waves |
|---|---|---|---|
| `EXECUTIVE` | §0–§2 + §1 synthesis + `T-1.1`, `T-1.2`, `T-1.4`, `T-1.6` | 21.1, 21.9, 21.12 only | Wave A at reduced scope; Wave B skipped |
| `STANDARD` | §0–§20, Opt subsections only where evidence exists | 21.1–21.4, 21.8–21.12 | Both waves, full roster |
| `FULL_ANNEX` | All 22 sections, all subsections | 21.1–21.12 | Both waves, full roster, vertical module expanded |

Length envelopes are guides, **never padding targets**. A `STANDARD` run that honestly lands short
because evidence was thin is a **pass**, not a failure.

---

## 5. Migration from v2.2

| v2.2 | v3.0.0 |
|---|---|
| §0.1–0.3 Scope / questions / plan | §0 (contract) + §2.1–2.3 |
| §0.4 Assumptions & contradictions | §2.5 + §21.11 |
| §0.5 Freshness / EQI / QA | §2.6 + §21.8 (Verification Summary) + §21.12 |
| §0.6 Reader's Map | §2.1 (audience mapping) |
| §1.1–1.8 Executive brief | §1.1–1.7 (§1.8 Material Unknowns → §2.5 + §21.11) |
| §2 Company profile | §3 |
| §3 Market & competitive | §4 (industry) + §11 (peers) + §12 (customers) |
| §4 Business model & financials | §5 (model) + §6 (financials) |
| §5 Strategy | §9 + §13 (signals) |
| §6 Technology & operating model | §8 (technology) + §7 (operations) |
| §7 AI posture | §8.3 (adoption) + §15 (readiness) |
| §8 Leadership & buying centers | §10 |
| §9 Vendor ecosystem | §16 |
| §10 Risk, regulatory & ESG | §14 (risk/reg) + §17 (ESG) |
| §11 Opportunity portfolio | §18 + §15.3–15.4 (use cases) |
| §12 Account strategy | §19 |
| §13 Engagement plan | §19.6 + §20 |
| Appendices A–L | §21.1–21.12 |
| `VZ-nnn` visual specs | `chart-data` / `figure-spec` blocks, IDs `C-<sec>.<n>` / `F-<sec>.<n>` |
| Evidence tags `[FACT]`/`[TRIANGULATED]`/`[INFERENCE]`/`[ESTIMATE]`/`[UNVERIFIED]` | Evidence-status enum `CONFIRMED`/`ANNOUNCED`/`OBSERVED-SIGNAL`/`INFERRED`/`UNKNOWN` |
| QA `F1–F10` + EQI | Verification Pass `V1–V12` + Verification Summary + §21.12 scorecard |
