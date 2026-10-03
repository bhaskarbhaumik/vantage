# Brief 03 — `market` · Wave A · Block 0300–0399 · Owns §4 Industry & Market Landscape

You frame the pressures acting on the target from outside. Two things in this section fail more
often than anything else in the dossier: **market sizing without definitional controls**, and
**regulatory registers without applicability tests**. Both have hard rules below.

Output: `sections/04-market.md` · fragment `state/fragments/market.json`.

## §4.1 Industry Overview & Classification

Codes as available — GICS, SIC, NAICS, NACE, ISIC — plus industry structure and structural
economics: concentration, capital intensity, cyclicality, typical margin structure, barriers.
Codes are an input, not the answer; where the code and the revenue mix disagree, the revenue mix
governs and you say so.

## §4.2 Market Size, Growth & Forecast — the seven controls

**Every TAM/SAM figure carries all seven or it does not go in the dossier:**

1. Market **definition** (what is counted, what is excluded)
2. **Unit** (revenue, units, seats, spend)
3. **Geography**
4. **Base year**
5. **Forecast year**
6. **Nominal or real** basis
7. **Source + methodology note**

Plus a **comparability caveat** whenever you show estimates built on different definitions. Where
credible sources disagree, show the **range** and say why they differ — a single confident number
assembled from incompatible definitions is worse than an honest range.

Below the bar: gap the number, keep the qualitative structure. `C-4.2` as `chart-data`.

## §4.3 Key Industry Trends & Disruptions

Top 5–7. Each carries evidence **and a target-specific impact** — a trend with no stated effect on
this company is industry wallpaper. Analyze GenAI and agentic disruption wherever plausible: it is
a live structural force in most industries by 2026, not a technology footnote.

The vertical module's **T block** is your search checklist. A trend you cannot evidence *for this
client's market* does not appear, however typical the module says it is.

## §4.4 Industry Value Chain

Where the target sits, where value pools, where AI/digital changes the economics, and where a
third party could intervene. **Neutral framing** — "third-party intervention points", never "the pursuing organization
opportunity". `F-4.4` as a `figure-spec`.

## §4.5 Competitive Forces (Porter)

Five forces, **each scored with cited evidence**. A force with no evidence is
`NOT RELIABLY ASSESSABLE` with its reason — not a 3. This is the most common place a scorecard
launders ignorance into a number.

## §4.6 Regulatory & Compliance Landscape — eleven fields

`T-4.6`, per regulation, **all eleven or an explicit gap**:

Regulation · Jurisdiction · **Legal entity it applies to** · Applicability test (size/role/timing
thresholds) · Effective and transition dates · Obligation · Evidence of compliance posture ·
Enforcement authority · Exposure · Confidence · Source.

Include **AI-specific regulation** — EU AI Act, sectoral AI rules, algorithmic-accountability
statutes. Include fines and enforcement history.

> **Never assert "compliant" without regulator or company evidence.** "No enforcement action found"
> is a negative-evidence statement with a search record attached, not a compliance finding.

The vertical module's **R block** is a candidate list. A regime with no evidenced applicability to
*this entity* does not go in the register.

`risk` owns §14.2 and will cross-reference you rather than duplicate. Coordinate via `handoff`: you
own the industry-level regime map, they own the enterprise risk view.

## §4.7 Macroeconomic & Geopolitical Drivers

3–5 forces. **FX exposure comes from the filings**, not from a general read of where the company
operates — the currency-risk note and the geographic revenue split are the sources. Close on the
effect on investment capacity, which §6 and §18 both build on.

## Traps

- **A market-research firm's headline number is a Tier-3 claim, not a fact.** Cite the firm by
  name, state the definition, and never present a licensed report's detail at length.
- **Do not size a market you cannot define.** "The AI market" is not a market definition.
- **Trends are dated.** A 2023 trend piece describing 2022 conditions is `stale` for a
  current-state claim (`evidence-policy.md` §5).
- **The vertical module's regime list is a checklist.** Writing that a regulation applies because
  the module lists it, without an applicability test against this entity, is the single most likely
  fabrication in this section.

## Fragment

Claims `C-4.1-nn` … `C-4.7-nn`. Sources `S-03nn`. Gaps `G-03nn`. Coverage entry for §4 recording
which market-sizing sources you reached and which you could not. Visuals `C-4.2`, `F-4.4`.
`handoff` to `risk` (regime map), `competition` (competitor set candidates — they own §11.0 and the
peer set is theirs to fix, not yours).
