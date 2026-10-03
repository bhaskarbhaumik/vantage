# Brief 10 — `risk` · Wave A · Block 1000–1099 · Owns §14 · Mints `R-nn`

You own the risk landscape and the two new integrity sections that most dossiers skip: **§14.8
sanctions and export controls**, and **§14.9 government relations and lobbying**. You are the sole
minter of the risk register `R-nn`, which §1.5 and §19 build on.

Output: `sections/14-risk.md` · fragment `state/fragments/risk.json`.

## §14.1 Enterprise Risk Factors

Top 10 from the risk-factor disclosure — Item 1A or the jurisdiction equivalent — **distilled, not
copied**. Boilerplate risk factors exist to protect the filer; your job is to extract the ones that
are specific to this company and material to a pursuit, and to say which are boilerplate.

Map each onto the **ISO 31000 taxonomy**: strategic · financial · operational · regulatory · cyber ·
geopolitical · reputational · ESG · legal. `T-14.1` + `F-14.1`. Severity and likelihood 1–5, each
with its basis.

Mint `R-nn` here. Every risk carries category, severity, likelihood, and a pursuit implication.

## §14.2 Regulatory & Compliance Requirements

The **enterprise** regulatory view, with all eleven register fields per regulation
(`jurisdiction-adapters.md`, end). `market` owns the **industry-level** regime map in §4.6 —
**cross-reference it rather than duplicating it**, and add what is specific to this entity: its own
enforcement history, its own consent decrees, its own registrations and licences.

Never assert "compliant" without regulator or company evidence.

## §14.3 Legal & Litigation Exposure

`T-14.3`. Material pending litigation, regulatory enforcement, consent decrees, settlements. From
the legal-proceedings note, material-event filings, and court or regulator records (CourtListener,
RECAP, regulator dockets).

**Disclosed exposure amounts only** (V9e, BLOCKER). Never estimate a litigation exposure figure —
record the matter, the stage, the claim as pleaded, and the company's own disclosure, and leave the
number absent if it is absent.

**Attribute each matter to the defendant entity** from §3.6 (V4e). Litigation against a subsidiary
is not litigation against the group, and vice versa.

For private targets this section is often **richer** than the financial sections — court records
are public where accounts are not. Do not thin it on the assumption that a private company is
opaque.

## §14.4 Cybersecurity & Data-Breach History

Disclosed incidents, dated and cited (the cybersecurity item of the annual filing, material-event
disclosures, regulator notifications, state AG breach notices). Regulator actions and remediation.
**Empty is a valid render.**

`technology` owns the posture view in §8.4 — you own the **incident and consequence** history.
Take their cyber findings via `handoff` rather than re-researching.

## §14.5 Geopolitical & Macroeconomic Risks

Exposure by geography and channel, grounded in the geographic revenue split and the filings'
own currency and geopolitical-risk discussion.

## §14.6 Scenario Analysis

Base / Bear / Bull on the two or three variables that most move this company's investment capacity
and pursuit timing. **Labelled analytical**, with assumptions stated, tied to evidenced drivers from
§6 and §14.1. `[INFERRED]` throughout — this is analysis, and saying so is what makes it usable.

## §14.7 Risk Implications for Pursuit & Delivery

Which client risks become delivery and commercial risks. Model 7 in `blueprint/scoring-rubrics.md`
— **polarity inverted, higher is worse; label it in-render every time.**

This is the bridge out of the neutral body, and it is **still vendor-neutral in wording** (V7a). Write
"a delivery partner would face…", not "the pursuing organization would face…". `account-strategy` translates it in §19.

## §14.8 Sanctions, Export Controls & Third-Party Integrity

Screen against the **official lists**: OFAC, EU, UK, UN consolidated. Screen the entity **and its
known affiliates** from §3.6.

Cover: export-control exposure (ITAR/EAR or equivalent), operations in restricted markets,
forced-labour and supply-chain integrity flags, critical-supplier concentration risk.

- **State entity-match certainty per hit.** Name collisions on sanctions lists are common and
  consequential; an `ambiguous` match reported as a hit is a serious error, and so is dismissing
  one silently.
- **A clean screen is a result and must be recorded as one**: "Screened <entity> and 4 affiliates
  against OFAC SDN, EU consolidated, UK OFSI, and UN lists on 2026-08-29; no matches."
- Source from the official lists themselves, not from a news summary of them.

## §14.9 Government Relations, Lobbying & Subsidies

Lobbying disclosures (Senate LDA, EU Transparency Register, national equivalents), political-spend
transparency data, subsidies and incentives received, government contracts held.

This is **both a risk lens and a public-sector entry signal** — hand the contract and vehicle
findings to `signals` (§13.7) and `opportunity` (§18.6). **Empty is a valid render.**

## Traps

- **Do not copy risk factors.** A distilled top-10 with company-specific reasoning is the product;
  a paraphrased Item 1A is not.
- **Severity and likelihood are scored with a basis**, or they are `n/e`.
- **Do not merge the parent's and the subsidiary's legal exposure** (V4f).
- **Do not screen by name string alone** — use the identifiers from §3.6.
- **Do not present a scenario as a forecast.** Base/Bear/Bull is a framing device with stated
  assumptions.

## Fragment

Claims `C-14.1-nn` … `C-14.9-nn`. **`risks[]` — the full `R-nn` register.** Sources `S-10nn`. Gaps
`G-10nn`. Coverage for §14 including which official sanctions lists you actually screened against.
`scoring_inputs.model_7`. Figure `F-14.1`. `handoff` to: `exec-brief` (the top risks for §1.5),
`account-strategy` (Model 7 output for §19.8), `opportunity` (regulatory drivers that create
demand), `signals` and `opportunity` (government contracts and vehicles from §14.9).
