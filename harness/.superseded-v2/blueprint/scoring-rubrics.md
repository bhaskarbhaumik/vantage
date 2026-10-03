# Scoring Rubrics — the eight models, instantiated

> `prompts/aid-prompt-v2.md` Deliverable G left this as `{{Insert the eight scoring-model
> rubrics}}` and supplied only the *pattern*. This file instantiates all eight, plus the
> v2.1 Evidence Quality Index. Reproduced verbatim into **Appendix G** for every run, with the
> actually-applied scores filled in.

## Universal rules (apply to every model)

1. **Scale is 1–5, anchored.** Anchors are given for 1, 3, and 5. Score 2 or 4 when evidence
   sits clearly between two anchors. Never score a dimension you cannot anchor.
2. **Evidence requirement.** Every dimension needs ≥1 supporting claim ID. A dimension with no
   evidence is scored **`n/e`** (not evidenced), excluded from the composite, and the remaining
   weights are **reweighted to sum to 100%**. Show the reweighting.
3. **Confidence propagation.** A dimension inherits the **lowest** confidence among its
   supporting claims. High = current T1–T2, no contradiction. Medium = triangulated or single
   strong source with minor staleness. Low = limited, indirect, stale, or inference-heavy.
4. **Composite suppression.** If **≥2 dimensions are Low confidence**, suppress the numeric
   composite entirely and substitute a qualitative assessment naming which dimensions failed and
   why. Do not report a number with a caveat — report no number.
5. **`[UNVERIFIED]` claims may never support any dimension.** If removing them leaves a
   dimension unevidenced, score it `n/e`.
6. **Framing, mandatory on every scorecard render:**
   *"Scores are evidence-based internal decision aids derived from outside-in public evidence.
   They are not measurements of the client and must not be presented to the client."*
7. **Reproducibility.** Appendix G must record, per dimension: score, anchor met, claim IDs,
   confidence, and any reweighting applied — enough that a second analyst reaches the same
   number from the same claims.

### Standard render

```markdown
| Dimension | Wt | Score | Anchor met | Evidence | Conf. |
|-----------|---:|------:|------------|----------|-------|
| Financial capacity | 25% | 4 | "FCF positive 3 consecutive yrs + net leverage <2.5x" | C-4.2-03, C-4.3-01 | High |
| …               |    |   |            |          |       |
| **Composite**   | 100% | **3.6** | Band: *Develop* | | **Medium** |
```

---

## Model 1 — Engagement Readiness

**Purpose.** The go/no-go signal in §1.6 — is this account ready for the pursuing organization engagement now?
**Consumes:** Models 2, 3, 6 outputs plus §4 financials and §5.1 priorities.

| Dim | Wt | 1 | 3 | 5 | Evidence required |
|-----|---:|---|---|---|-------------------|
| Financial capacity to fund transformation | 25% | Negative FCF or leverage >4x; cost-cutting is the stated agenda | FCF positive but constrained; leverage 2.5–4x; discretionary spend flat | FCF positive 3 consecutive yrs, leverage <2.5x, disclosed growth investment | §4.2, §4.3 claims |
| Digital maturity | 15% | Model 2 composite <2.0 or suppressed-low | Model 2 composite 2.5–3.4 | Model 2 composite ≥4.0 | Model 2 |
| AI readiness | 15% | Model 3 composite <2.0 or suppressed-low | Model 3 composite 2.5–3.4 | Model 3 composite ≥4.0 | Model 3 |
| Strategic alignment | 20% | No stated priority maps to any services-addressable need | 1–2 stated priorities map to addressable needs | ≥3 dated, budgeted priorities map directly to addressable needs | §5.1 claims, dated |
| Priority fit with the pursuing organization focus areas | 15% | Needs fall outside provided `ACCOUNT_CONTEXT` capability set | Partial overlap; one strong adjacency | Direct overlap with ≥2 capabilities named in the pursuing organization input | §11.1 + the pursuing organization input |
| Stakeholder access | 10% | No evidenced relationship; no identified entry stakeholder | ≥1 `P-nn` identified, accessibility Medium | Existing relationship in `KNOWN_RELATIONSHIP_CONTEXT` **or** ≥2 `P-nn` at High accessibility | §8.3 / Model 6 |

**Formula.** `composite = Σ(weight × score)` over evidenced dimensions, reweighted.
**Bands.** ≥4.0 **Engage now** · 3.0–3.9 **Develop** · 2.0–2.9 **Nurture** · <2.0 **Monitor**.
**Limitations.** Outside-in only. "Stakeholder access" is the dimension most likely to be wrong,
because absence of public evidence of a relationship is not evidence of absence — if
`KNOWN_RELATIONSHIP_CONTEXT` is `NONE`, score this dimension Low confidence by default.

---

## Model 2 — Digital Maturity

**Purpose.** §6.4 — structured relative placement of the client's digital estate.

| Dim | Wt | 1 | 3 | 5 | Evidence required |
|-----|---:|---|---|---|-------------------|
| Customer experience | 15% | No evidenced digital channel investment | Digital channel evidenced in ≥1 line of business; loyalty/app programme running | Unified cross-channel platform evidenced + disclosed CX outcome metrics | §3.6, §6.1 |
| Operations | 20% | Core processes evidenced as manual/legacy; no automation signal | Modernisation evidenced in ≥1 function | Enterprise-wide process platform evidenced across ≥2 functions with stated outcomes | §6.1, §6.5 |
| Workforce & ways of working | 10% | No evidence of digital-skills investment | Digital/agile hiring evidenced (T5 acceptable, flagged) | Named reskilling programme + digital org roles evidenced at leadership level | §5.5, §8.1 |
| Technology estate | 20% | Legacy/on-prem monolith evidenced; no modernisation intent stated | Hybrid; migration programme announced | Modern platform stack evidenced across ≥2 domains; deprecation of legacy stated | §6.1, §6.2 |
| Data & AI foundation | 25% | No evidenced enterprise data platform or governance | Modern data platform evidenced in ≥1 domain; governance signals present | Enterprise platform + governance + AI-consumption evidence across BUs (needs ≥2 T1–T3 claims) | §6.3 |
| Business-model digitalisation | 10% | Revenue entirely traditional | Digital revenue stream evidenced but not separately reported | Digital/platform revenue separately disclosed and growing | §4.1 |

**Bands.** ≥4.0 **Leading** · 3.0–3.9 **Advancing** · 2.0–2.9 **Developing** · <2.0 **Nascent**.
**Limitations.** Job postings (T5) are the most common evidence here and are hypothesis-grade.
A dimension resting only on T5 evidence is Low confidence by definition.

---

## Model 3 — AI & Agentic Readiness

**Purpose.** §7.2. Six base dimensions plus an agentic overlay applied only when §7.4 has evidence.

| Dim | Wt | 1 | 3 | 5 | Evidence required |
|-----|---:|---|---|---|-------------------|
| AI strategy & sponsorship | 20% | No public AI statement by any executive | AI named in ≥1 earnings call or strategy document within 12 mo | Board- or CEO-level AI agenda with disclosed investment figure or dedicated org | §5.1, §5.4, §7.1 |
| Data readiness | 25% | No evidence of enterprise data platform or governance | Modern platform evidenced in ≥1 domain; governance signals present | Enterprise platform + governance + AI-consumption evidence across BUs (≥2 T1–T3 claims) | §6.3 |
| Talent | 15% | No AI/ML roles evidenced | AI/ML hiring evidenced (T5 ok, flagged); no named AI leader | Named AI leadership role + sustained AI/ML hiring across ≥2 locations | §5.5, §8.1 |
| Infrastructure | 15% | No cloud posture evidenced | Cloud migration evidenced; no AI-specific infrastructure signal | Named AI platform/hyperscaler AI partnership evidenced | §6.2 |
| Governance & responsible AI | 10% | No AI governance disclosure | Responsible-AI principles published | Published governance framework + named accountable owner + disclosed controls | §7.1, §10.2 |
| Deployment maturity | 15% | No AI initiative evidenced | Pilots evidenced; no production claim | ≥2 production AI deployments evidenced with disclosed outcomes | §7.1 |

**Agentic overlay** — apply **only** if §7.4 carries ≥2 evidenced claims; otherwise state
"agentic overlay not applied: insufficient evidence" and report the base composite alone.
Overlay adjusts the composite by up to ±0.5:

| Signal | Adjustment |
|--------|-----------:|
| Public API / integration platform evidenced as a strategic asset | +0.2 |
| Orchestration or workflow-automation platform evidenced | +0.2 |
| Human-in-the-loop / AI governance controls evidenced for autonomous systems | +0.1 |
| Executive statement explicitly rejecting or deferring agentic adoption | −0.3 |

**Bands.** ≥4.0 **AI-scaling** · 3.0–3.9 **AI-experimenting** · 2.0–2.9 **AI-aware** ·
<2.0 **Pre-AI**.
**Limitations.** Deployment maturity is systematically under-observed from outside — companies
disclose pilots more readily than production. Treat a low score here as "not disclosed" rather
than "not happening", and say so.

---

## Model 4 — Opportunity Attractiveness

**Purpose.** §11.1 / §11.3. Scored **per `O-nn`**.

| Dim | Wt | 1 | 3 | 5 | Evidence required |
|-----|---:|---|---|---|-------------------|
| Value potential | 25% | Sizing basis absent; no analogue | `[ESTIMATE]` with stated benchmark method, range spans >2× | Sizing anchored to a disclosed client figure (programme budget, segment cost base) | §4, §5.2 |
| Urgency | 20% | No dated driver | Driver evidenced but undated, or dated >12 mo out | Dated driver within 12 mo — regulatory deadline, contract event (§9.5), announced programme milestone | §5.2, §9.5, §10.2 |
| Budget signal | 20% | No evidence of funding for this need | Adjacent spend evidenced | Disclosed budget or capex/opex line tied to this need | §4.3, §4.4, §5.2 |
| Strategic fit to client priorities | 20% | Maps to no stated priority | Maps to a stated priority indirectly | Maps directly to a dated `C-5.1-nn` priority claim | §5.1 |
| Expansion potential | 15% | Single-scope, no follow-on path | Follow-on plausible in same BU | Evidenced multi-BU or multi-geo applicability | §2.2, §2.4 |

**Bands.** ≥4.0 **Pursue now** · 3.0–3.9 **Develop** · 2.0–2.9 **Watch** · <2.0 **Park**.
**Limitations.** "Value potential" is the dimension most exposed to wishful sizing. A `5` requires
a *client-disclosed* number; a benchmark-derived estimate caps this dimension at `3`.

---

## Model 5 — Win Probability

**Purpose.** §11.1 / §11.3. Scored **per `O-nn`**. Paired with Model 4 on the prioritisation grid.

| Dim | Wt | 1 | 3 | 5 | Evidence required |
|-----|---:|---|---|---|-------------------|
| Need-evidence strength | 25% | Need is `HYPOTHESIS` from a single T5 signal | Need is `HYPOTHESIS` from ≥2 T3–T4 sources | Need is `CONFIRMED` — client stated it publicly, T1–T2 | Need-evidence claim IDs |
| Access | 20% | No identified stakeholder for this opportunity | `P-nn` identified, accessibility Medium | Existing relationship per the pursuing organization input, or `P-nn` at High accessibility | §8.3, the pursuing organization input |
| Incumbency position | 20% | Entrenched incumbent evidenced, recently renewed | Incumbent evidenced, no recency signal | No incumbent evidenced in this domain, or displacement signal present (§9.5) | §9.2, §9.4, §9.5 |
| Differentiation | 20% | the pursuing organization capability generic to all major SIs | One credible differentiator per the pursuing organization input | ≥2 differentiators tied to a client-specific constraint (geography, domain, existing estate) | §11.1 + the pursuing organization input |
| Timing | 15% | No entry window evidenced | Window inferred from fiscal cycle | Dated window evidenced — RFP, renewal, programme milestone, leadership change | §9.5, §13.1 |

**Bands.** ≥4.0 **Strong** · 3.0–3.9 **Competitive** · 2.0–2.9 **Long shot** · <2.0 **Not now**.
**Limitations.** Incumbency and timing depend on contract evidence that is usually absent outside
regulated/public-sector accounts. When §9.5 is empty, both dimensions cap at Medium confidence,
which frequently triggers composite suppression — **that is the intended behaviour**, not a bug.

---

## Model 6 — Stakeholder Influence & Accessibility

**Purpose.** §8.3. **Not a 1–5 composite.** Two independent H/M/L axes, scored per `P-nn`.
There is no composite and no weighting: collapsing two orthogonal axes into one number destroys
the only decision the model supports (who to approach, and how).

### Axis A — Influence over the relevant buying decision

| Level | Anchor | Evidence required |
|-------|--------|-------------------|
| **High** | Named budget authority, P&L ownership, or executive sponsorship of a relevant programme | T1–T2: filing, org announcement, programme press release |
| **Medium** | Functional leadership in a domain the opportunity touches, without evidenced budget authority | T2 bio or org announcement |
| **Low** | Advisory, technical, or influencer role only | Any tier |

### Axis B — Accessibility to the pursuing organization

| Level | Anchor | Evidence required |
|-------|--------|-------------------|
| **High** | Existing evidenced the pursuing organization relationship in `KNOWN_RELATIONSHIP_CONTEXT` | the pursuing organization input **only** |
| **Medium** | Public-facing (conference speaker, published interviews, active professional presence) — a plausible cold path exists | T2–T4 |
| **Low** | No public engagement surface and no the pursuing organization relationship | Absence, stated as `[INFERENCE]` |

**Mandatory basis statement.** Every axis score carries an explicit basis, e.g.
`Accessibility: Medium (INFERENCE: keynote speaker at two 2026 industry events [S-712]; no evidenced the pursuing organization relationship)`.

**Priority quadrant.** High/High = **engage first** · High/Low = **needs sponsor path** ·
Low/High = **route to a High-influence stakeholder** · Low/Low = **deprioritise**.
**Limitations.** Accessibility is `NONE`-biased: when `KNOWN_RELATIONSHIP_CONTEXT` is absent,
every stakeholder scores Medium or Low regardless of reality. State this once in §8.3.

---

## Model 7 — Delivery & Commercial Risk

**Purpose.** §10.5. Translates client risk into the pursuing organization-facing risk. **Higher score = higher risk**
— note the inverted polarity on every render, since every other model is higher-is-better.

| Dim | Wt | 1 (low risk) | 3 | 5 (high risk) | Evidence required |
|-----|---:|---|---|---|-------------------|
| Client financial stability | 25% | Investment-grade, FCF positive, no going-concern language | Leverage elevated or margin compression evidenced | Distress signals: covenant language, rating downgrade, restructuring announced | §4.2, §10.1 |
| Estate & programme complexity | 25% | Single-region, modern stack, one BU in scope | Multi-BU or hybrid estate | Multi-geo, multi-BU, heavy legacy, evidenced integration debt | §2.2, §2.4, §6.5 |
| Procurement style | 20% | Direct, relationship-led, evidenced sole-source precedent | Standard competitive RFP | Reverse-auction, heavy compliance regime, evidenced vendor-consolidation drive against incumbents | §6.6, §8.2 |
| Dependency risk | 15% | No third-party dependency in scope | Dependency on one incumbent for handover | Critical dependency on an incumbent with evidenced incentive to obstruct | §9.1, §9.2 |
| Regulatory & data-residency constraint | 15% | No special regime | Sector regime applies (e.g. SOX, GDPR) | Restrictive regime constraining delivery location or data movement (e.g. `V-GOV` FedRAMP, `V-HLS` PHI, `V-BFSI` data residency) | §10.2, `V-*` |

**Bands (inverted).** ≥4.0 **High risk — structure defensively** · 3.0–3.9 **Elevated** ·
2.0–2.9 **Manageable** · <2.0 **Low**.
**Limitations.** Procurement style is rarely disclosed outside public-sector accounts. When it
rests on `[INFERENCE]`, say so in §12.5 — it drives the recommended commercial construct.

---

## Model 8 — Vendor Displacement Potential

**Purpose.** §9.4. Scored **per evidenced incumbent**. §9 is Tier 2 and therefore vendor-neutral:
score and render the first four dimensions as *third-party entry potential*. Dimension 5
(differentiation) is **the pursuing organization-specific and must be deferred to §12.4** — compute it there, and in
§9.4 report only the four-dimension partial with a pointer.

| Dim | Wt | 1 (hard to displace) | 3 | 5 (displaceable) | Evidence required |
|-----|---:|---|---|---|-------------------|
| Entrenchment | 30% | Incumbent embedded across ≥3 domains over ≥5 yrs | Incumbent in 1–2 domains | Recent, narrow, or project-scoped engagement only | §9.1, §9.2 |
| Satisfaction signals | 20% | Public reference, expanded scope, joint announcement within 12 mo | No signal either way | Public dissatisfaction, scope reduction, litigation, or incident evidenced | §9.2, §10.3, T3–T4 |
| Contract timing evidence | 25% | Renewal evidenced within last 12 mo | No timing evidence — **default** | Re-compete, RFP, or transition evidenced in §9.5 | §9.5 **only** — never estimated |
| Switching cost | 25% | Deep proprietary integration evidenced | Standard platform, moderate coupling | Commodity or replicable scope; multi-vendor already evidenced | §6.1, §9.1 |
| *(5) Differentiation vs. this incumbent* | — | *Deferred to §12.4* | | | the pursuing organization input |

**Bands.** ≥4.0 **Open** · 3.0–3.9 **Contestable** · 2.0–2.9 **Defended** · <2.0 **Locked**.
**Limitations.** "Contract timing evidence" defaults to `3` for almost every private-sector
account because expiry dates are not public. **A `5` here requires a §9.5 row.** Never infer a
renewal window from engagement start date plus a typical term — that is exactly the fabrication
v2.0 was designed to eliminate.

---

## Evidence Quality Index (EQI) — `NEW v2.1`

**Purpose.** §0.5. A dossier-level rollup that tells a reviewer in five seconds how much to trust
everything else. Computed by `qa-gate` from the merged claim register — **not scored by judgment**.

```
EQI = 100 × ( 0.40·(claims_T1_T2 / claims_total)
            + 0.25·(claims_high_conf / claims_total)
            + 0.20·(1 − claims_stale / claims_total)
            + 0.15·(1 − high_materiality_gaps / (high_materiality_gaps + claims_high_materiality)) )
```

Where `claims_T1_T2` counts claims whose *primary* source is Tier 1 or 2, and `claims_stale`
counts claims flagged `stale: true` per the §5 freshness windows.

| EQI | Band | What it means |
|-----|------|---------------|
| ≥75 | **Strong** | Scores and the exec brief are defensible in front of a client partner |
| 60–74 | **Adequate** | Usable for pursuit planning; validate the flagged gaps before any client-facing use |
| 45–59 | **Thin** | Treat all composites as directional; §13.4 backlog is the primary deliverable |
| <45 | **Insufficient** | Do not present. Re-run with better sources or reduce scope per the thin-evidence degradation mode |

Render alongside the raw distribution — never the index alone:

```markdown
**Evidence Quality Index: 68 / 100 (Adequate)**

| Metric | Value |
|--------|-------|
| Claims registered | 142 |
| Primary source T1–T2 | 89 (63%) |
| High confidence | 71 (50%) · Medium 54 (38%) · Low 17 (12%) |
| Flagged stale | 9 (6%) |
| High-materiality gaps unresolved | 4 |
```
