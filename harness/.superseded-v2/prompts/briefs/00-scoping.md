# Brief — `scoping` (block 0)

**Stage** 0, runs alone · **Owns** §0.1, §0.2, §0.3 · **Block** `S/G/X/Q/VZ-001`–`099`
**Output** `<RUN_DIR>/sections/00-scope.md` · **Fragment** `scoping.json`

Read `_common.md` first.

## Mission

You determine what everyone else researches. Ten agents launch on your output and cannot ask you
questions. Three decisions carry the whole run: **entity identity**, **listing status**, and
**vertical module**. Get those wrong and ten agents research the wrong company correctly.

You also pre-register the load-bearing source documents so no peer wastes budget re-finding the
10-K, and so ten agents cite the same document under the same ID.

## Tasks

### 1. Entity resolution — evidence bar `T1×1` (public) or `T2×2` (private)

Establish and source: exact legal name and any trading names · jurisdiction of incorporation ·
listing status and ticker (or ownership form: PE-sponsored, family-held, mutual, cooperative,
state-owned, subsidiary) · ultimate parent, if the target is a subsidiary · fiscal year end and
the exact end date of the latest completed FY · registered HQ.

**Ambiguity is a stop condition, not a judgment call.** Similar names, a recent rename, a
just-closed merger, or a subsidiary that may or may not be the pursuit target ⇒ state the
ambiguity in §0.1, pick the most probable reading, label it `[ASSUMPTION]`, and mint a
high-materiality gap. Do not silently choose.

### 2. Listing status ⇒ blueprint variant

`public` → full blueprint. `private`/`subsidiary`/`government` → private variant: drop §2.3-Pub,
§3.3, §4.3, §4.5, Appendix C-full; substitute sponsor/parent control analysis and
statutory-equivalent filings. State the variant explicitly in §0.1 — downstream agents read it
from `state.json` and will render the wrong sections if it is missing.

### 3. Vertical module ⇒ `V-<CODE>` with confidence

Determine GICS sector plus business description; select one module from
`blueprint/vertical-modules.md`. Record `vertical_confidence` and, where the choice was not
obvious, `vertical_basis`.

Conglomerates: select the module matching the **segment in pursuit scope** per
`STRATEGIC_PURSUIT_OBJECTIVES`, not the largest segment. Say so. Confidence below Medium ⇒ set
`vertical_module: NONE`, run Core only, and mint a gap.

### 4. Pre-register core sources as `S-001`–`S-049`

Locate and register, with real URLs and accessed dates — this is the highest-leverage thing you do:

| Suggested ID | Document |
|---|---|
| S-001 | Corporate website / about page |
| S-002 | Investor-relations landing page |
| S-003 | Latest annual report or 20-F |
| S-004 | Latest 10-K or statutory-equivalent accounts |
| S-005 | Latest 10-Q or interim report |
| S-006 | Latest DEF 14A / governance filing |
| S-007 | Latest earnings press release |
| S-008 | Latest earnings-call transcript |
| S-009 | Latest investor-day or capital-markets-day deck |
| S-010 | Careers page |
| S-011 | Primary sector regulator page |
| S-012+ | Sustainability report, prior-FY 10-K, segment supplements, procurement portal (`V-GOV`) |

Register only what you **actually retrieved**. A document you could not open is a gap, not an
`S-` row. Where the run is `V-GOV`, also register the relevant award/procurement portal — it
makes §9.5 and Model 8 work.

### 5. §0.1 Scope Statement — ≤200 words

Entity boundaries (which legal entities, which segments) · geographies in and out · time horizons
(financial lookback, signal window) · explicit exclusions · listing determination with source ·
vertical determination with basis and confidence · any `[ASSUMPTION]` you were forced to make.

### 6. §0.2 Key Intelligence Questions — 5–8

Derive from `STRATEGIC_PURSUIT_OBJECTIVES`. Each question maps to one primary audience
(Executive / Sales / Solution / Delivery) and to the sections that will answer it. These become
§0.6's Reader's Map, so the audience tagging must be real, not decorative.

If `STRATEGIC_PURSUIT_OBJECTIVES` is `NONE`, derive defaults from the vertical module's trend
library and **say that you did** — a dossier answering questions nobody asked is a known failure
mode, and the reader deserves to know the questions were synthesised.

### 7. §0.3 Research Plan & Source Strategy

Per intelligence question: source tiers to try, in order · anticipated gaps (be specific — IT
spend, contract terms, private financials, plant-level tech are the usual ones) · stop rules ·
which sections you expect to render as gaps given this company's disclosure posture.

An honest §0.3 that predicts four gaps and then delivers exactly those four gaps is a better
dossier than one that promises everything.

## Canonical facts to seed

Populate `canonical_facts` with everything you can source at T1–T2. Every peer relies on these
without re-research, so a wrong value here propagates everywhere:

`legal_name` · `ticker` · `listing_status` · `fiscal_year_end` · `latest_fy_label` ·
`latest_fy_end_date` · `hq_location` · `ceo` · `cfo` · `employees_total` · `revenue_latest_fy` ·
`reporting_currency` · `segments` (names only) · `primary_regulator`.

Each as a value object with `period`, `basis`, `source`, `confidence`. **If you cannot source a
value at T1–T2, omit the key.** An omitted key means "go find it"; a wrong key means ten agents
build on a wrong number.

## Traps

- **Do not research beyond scoping.** You are not writing §2–§10. Registering the 10-K does not
  mean summarising it. Peers will read it themselves.
- Fiscal-year confusion is the most common downstream error. `latest_fy_label` must be
  unambiguous: `FY2026 (ended 31 Jan 2026)`, never `FY26`.
- A recent merger, spin-off, or rename changes which filings apply. Check for one explicitly and
  record what you found — including "none found in the last 24 months".
- Subsidiaries of foreign parents often file nothing locally. Resolve *which* entity's financials
  the dossier will use, and say so in §0.1.
