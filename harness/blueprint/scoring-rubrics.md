# Scoring Rubrics v3.0.0 — the eight models, instantiated

> Every score in the dossier comes from one of these models. A score with no rubric behind it is a
> V12b failure. Reproduced verbatim into §21.8, so the dossier documents whatever rubric was
> actually in force for that run.
>
> **These are internal decision-support tools derived from outside-in public evidence. They are not
> measurements of the client and must never be presented to the client.**

## Universal rules

1. **Anchored scales only.** Every dimension names what a 1 and a 5 look like. "Above average" is
   not a score.
2. **Evidence per dimension.** Each dimension cites ≥1 claim ID. A dimension with no cited claim
   scores `n/e` (not evidenced) — **not 3**. Defaulting an unknown to the midpoint is the most
   common way a scorecard launders ignorance into a number.
3. **`n/e` reweighting.** Drop `n/e` dimensions from the composite and renormalize the remaining
   weights to 100%. **Show the renormalization** — "Stakeholder Access NOT ASSESSED; remaining five
   weights renormalized from 90% to 100%".
4. **Confidence propagates downward.** A dimension inherits the **lowest** confidence among the
   claims supporting it.
5. **Composite suppression.** ≥2 dimensions at `LOW` confidence ⇒ **the composite is suppressed**.
   Report the dimension scores and say why there is no composite. A confident-looking number built
   on two weak legs is worse than no number.
6. **`NOT RELIABLY ASSESSABLE` is a valid result** and always carries its reason.
7. **Peer overlays** use only the §11.0 peer set and comparable evidence — never a peer scored from
   thinner data than the target.

### Standard render

```markdown
| Dimension | Weight | Score (1–5) | Evidence | Confidence |
|---|---:|---:|---|---|
| Data foundation | 20% | 3 | Lakehouse named in FY25 investor day [C-8.1-04] | MEDIUM |
| Talent & org | 20% | 2 | 3 AI roles posted, no named leader [C-13.3-02] | LOW |
| … | | | | |
| **Composite** | 100% | **2.6 / 5** | | **MEDIUM** |

*Rubric: Model 3 v3.0.0. Two dimensions n/e (dropped, weights renormalized). Composite not
suppressed — one LOW dimension.*
```

---

## Model 1 — Engagement Readiness *(§1.6)*

Weighted composite on **0–100**. Dimension scores are 0–10.

| Dimension | Weight | Source | 0–2 | 5–6 | 9–10 |
|---|---:|---|---|---|---|
| Financial Health | 20% | §6.1–6.4 | Distressed; covenant pressure; no discretionary capacity | Stable, modest growth, funded | Strong growth, high FCF, explicit investment capacity |
| Digital Maturity | 20% | §8.2 composite ×2 | Model 2 = 1 | Model 2 = 3 | Model 2 = 5 |
| AI Readiness | 20% | §15.1 composite ×2 | Model 3 = 1 | Model 3 = 3 | Model 3 = 5 |
| Strategic Alignment | 15% | §9.1 vs the opportunity set | No overlap between stated priorities and the register | Partial overlap on 1–2 themes | Register maps directly onto ≥3 quoted priorities |
| Stated Priorities Fit | 15% | §9.1, §13.4 | Priorities are unstated or unrelated | Adjacent | Priorities name the exact capability domain |
| Stakeholder Access | 10% | **Account-Team Input Sheet only** | — | — | — |

**Stakeholder Access cannot be derived from public data.** Without the Input Sheet it is
`NOT ASSESSED`, the remaining five weights renormalize from 90% to 100%, and the renormalization is
stated in-section (V5c, BLOCKER).

| Band | Score | Thesis |
|---|---|---|
| Pursue | ≥ 75 | Evidence supports active investment now |
| Develop | 60–74 | Invest in access and validation before committing pursuit cost |
| Nurture | 45–59 | Maintain relationship; revisit on a named trigger |
| Monitor | < 45 | No evidenced basis for investment this cycle |

§1.3's engagement thesis must be **consistent with this band** (V8d, BLOCKER).

## Model 2 — Digital Maturity *(§8.2)*

Six dimensions, 1–5, equal weight, using the system prompt's universal maturity anchors:

> **1** no public evidence of capability · **2** isolated pilots/hires · **3** production
> deployments in ≥1 BU with named platforms · **4** enterprise-scale platforms + governance +
> measurable outcomes · **5** capability is a stated competitive differentiator with independent
> corroboration

| # | Dimension | Evidence source | Domain reading of the anchors |
|---|---|---|---|
| 1 | Core platform modernity | §8.1.1 | 1 = only legacy/unknown ERP-CRM-HCM · 5 = modern suite live enterprise-wide, independently corroborated |
| 2 | Cloud & infrastructure | §8.1.2 | 1 = no cloud evidence · 5 = stated cloud-first with named landing zones and measurable migration outcomes |
| 3 | Data & analytics | §8.1.3 | 1 = no platform evidence · 5 = governed lakehouse with lineage, MDM, and disclosed business outcomes |
| 4 | Integration & architecture | §8.1.4 | 1 = no API/iPaaS evidence · 5 = event-driven, API-productized, observability across the estate |
| 5 | Digital channels & product | §12.3, §5.4 | 1 = no digital channel · 5 = digital is the primary channel with disclosed metrics |
| 6 | IT operating model & governance | §8.5 | 1 = no evidenced structure · 5 = named governance body, disclosed budget model, product-team operating model |

## Model 3 — AI & Agentic Readiness *(§15.1)*

Six dimensions, 1–5, equal weight, same universal anchors.

| # | Dimension | Evidence source |
|---|---|---|
| 1 | Data foundation for AI | §8.1.3, §15.2 |
| 2 | AI initiative depth | §8.3.1 — pilots vs production, named platforms, disclosed outcomes |
| 3 | Talent & organization | §13.3 role density, §10.2.2 named AI leadership |
| 4 | Governance & responsible AI | §17.6 — principles, governance body, EU AI Act readiness |
| 5 | Partner & vendor ecosystem | §16.1, §9.5 — hyperscaler/model-provider relationships |
| 6 | **Agentic posture** | §8.3.4 — agent frameworks, MCP/tool-integration signals, copilot deployments, stated agent strategy |

**Dimension 6 has its own research task (§8.3.4) and may not be inferred from dimension 2.** It is
the whitespace signal the dossier exists to surface; inferring it from general AI activity is the
most likely way this model produces a wrong answer.

**Deployment maturity is systematically under-observed.** Companies announce pilots loudly and
production quietly. A 2 that "should" be a 3 is the expected error direction — say so in the
evidence column rather than compensating with an unevidenced bump.

## Model 4 — Opportunity Attractiveness *(§18.1, §1.4)*

**Public, evidence-based, ungated.** 1–5 composite from four dimensions.

| Dimension | Weight | 1 | 3 | 5 |
|---|---:|---|---|---|
| Evidenced need | 35% | Inferred from a general trend | One cited pain point or priority | ≥2 cited, independently sourced, at `CONFIRMED` |
| Sizing basis | 25% | No basis — cannot be sized | Analogue or disclosed-budget anchor | Disclosed programme budget or contract value |
| Timing signal | 20% | No dated trigger | A fiscal or milestone window | An evidenced contract/RFP/leadership event with a date |
| Capability fit | 20% | Adjacent to the Capability Pack | Pack names the domain | Pack names the domain **and** a comparable proof point |

Without a Capability Pack, "capability fit" is `n/e`, dropped, and the other three renormalize.

## Model 5 — Win Probability *(§18.1, §1.4)* — **GATED**

**Cannot be derived from public data.** Rendered **only** from the §21.10 Account-Team Input Sheet.
Without it, every win-probability cell reads `[INTERNAL REQUIRED]` (V8f, BLOCKER).

With the Input Sheet, 1–5 from: existing relationship depth · incumbent strength · delivery
credentials in the domain · commercial fit · stakeholder access. The rubric is not reproduced here
because the harness never scores it from public evidence.

## Model 6 — Stakeholder Influence & Accessibility *(§10.6, §19.6)*

Two independent axes. **Never averaged** — the grid is the output.

### Axis A — Influence over the relevant buying decision (1–5)

| Score | Anchor |
|---|---|
| 1 | No evidenced role in technology or sourcing decisions |
| 2 | Consulted; no evidenced authority |
| 3 | Owns a function that the opportunity touches |
| 4 | Evidenced budget authority in the domain |
| 5 | Evidenced decision authority **and** public ownership of the relevant strategic priority |

### Axis B — Accessibility (1–5) — **partially gated**

Public evidence supports at most a 3: conference speaking, published contact route, active public
presence, analyst-day participation. **4 and 5 require account-team input** (existing relationship,
warm introduction path). Without the Input Sheet, cap at 3 and mark the axis
`[INTERNAL REQUIRED for 4–5]`.

## Model 7 — Delivery & Commercial Risk *(§14.7, §19.8)*

**Polarity is inverted: higher is worse.** Label it in-render every time; a reader scanning
scorecards will otherwise read 5 as good.

| Dimension | 1 (low risk) | 5 (high risk) |
|---|---|---|
| Financial capacity to fund | Strong FCF, funded programme | Covenant pressure, programme deferrals evidenced |
| Delivery constraints (§10.8) | No evidenced constraint | Works councils, clearances, residency, offshore restrictions all in play |
| Regulatory exposure | Light regime, clean record | Active enforcement, multi-jurisdiction obligations |
| Incumbent entrenchment | No evidenced incumbent | Long-tenure SI across the target domains |
| Organizational volatility | Stable leadership and structure | Recent CIO/CFO change, restructuring, activist pressure |
| Integrity screening (§14.8) | Clean screen against official lists | Sanctions/export/forced-labour flags with certain entity match |

## Model 8 — Vendor Displacement Potential *(§16.5, §19.7)*

1–5 per incumbent relationship. **Dimension 5 is deliberately deferred** from §16.5 to §19.7 —
§16 is inside the vendor-neutral range and cannot assess a organization-relative advantage.

| # | Dimension | 1 | 5 |
|---|---|---|---|
| 1 | Relationship age & depth | Recently renewed, deeply embedded | Ageing, narrow scope, single domain |
| 2 | Evidenced dissatisfaction | None found | Public incidents, complaints, or exec commentary |
| 3 | Contract/renewal signal | No evidenced window | Evidenced award expiry or published re-compete |
| 4 | Capability gap at the incumbent | Incumbent covers the whole domain | Evidenced gap in the domain the opportunity needs |
| 5 | **Relative advantage** *(§19.7 only)* | Pack shows no differentiator | Pack shows a named differentiator with a comparable proof point |

Scoring dimension 5 inside §16.5 is a V7a tier violation.

---

## MEDDPICC evidence matrix *(§19.9)* — not a score

Eight fields. Each carries **status · source · next validation action**. This is a completeness
instrument, not a scale: the value is in showing which fields public research **cannot** fill.

| Field | Public evidence can establish | Typically `[INTERNAL REQUIRED]` |
|---|---|---|
| **M**etrics | Disclosed KPIs, stated programme targets | The client's own success criteria for this deal |
| **E**conomic buyer | Named budget owner where evidenced (§10.4) | Confirmation and access |
| **D**ecision criteria | Published RFP criteria, procurement policy | Weighting |
| **D**ecision process | Procurement centralization, cycle timing (§10.5) | Approval chain for this deal |
| **P**aper process | Framework agreements, vehicles (§13.7) | Legal/security review path |
| **I**dentified pain | §7.5 register, §9.1 priorities | Prioritization among them |
| **C**hampion | — | Always internal |
| **C**ompetition | Evidenced incumbents (§16.2) | Who is actually bidding |

A blank field is a V7f failure. "We do not know, and here is the action that would find out" is the
correct output for six of these eight on a typical run.
