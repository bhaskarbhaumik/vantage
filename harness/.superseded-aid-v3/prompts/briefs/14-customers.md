# Brief 14 — `customers` · Wave B (← §5) · Block 1400–1499 · Owns §12 Customer & Market Intelligence

You cover **who the target's customers are and what they think** — the demand side of the business
model, and the one place in the dossier where invented metrics are most tempting. §12.4 has a hard
rule: **never an invented NPS or CSAT.**

Read `business-model`'s §5.3 and §5.5 first; segment definitions and channels are your inputs.

Output: `sections/12-customers.md` · fragment `state/fragments/customers.json`.

## §12.1 Customer Segmentation & Demographics

Segments and their economics, extending `business-model`'s structural view with demographic and
behavioural detail where disclosed. `C-12.1`. Where the company reports customer counts, ARPU,
cohort behaviour, or churn, use its definitions verbatim — these terms are defined differently by
every company.

## §12.2 Product & Service Portfolio

`T-12.2`. Portfolio by business unit with **lifecycle stage**. Lifecycle stage is evidenced (stated
end-of-life, launch dates, investment commentary) or marked `INFERRED` with the reasoning. Note
discontinued and sunset lines — what a company is exiting says as much as what it is launching.

## §12.3 Go-to-Market Strategy & Channels

Route-to-market execution, campaign posture, and **ad-transparency signals where available** (Meta
Ad Library, Google Ads Transparency Center — noting that API coverage varies by ad type and
jurisdiction, and the Google tool is portal-only). `F-12.3`.

Ad-transparency data is `OBSERVED-SIGNAL`: it shows what is being promoted, not what is selling.

## §12.4 Customer Experience & Satisfaction — the hard rule

**Prefer standardized benchmarks over anecdote.** ACSI, sector satisfaction indices, regulator
complaint statistics, and published survey results with methodology are usable. Company-reported NPS
is usable **when the company published it**, cited, with its date and methodology.

> **Never an invented NPS or CSAT** (`evidence-policy.md` §12). Not derived from review-site
> averages, not estimated from complaint volume, not benchmarked from a sector figure. If the
> company does not publish one and no standardized benchmark covers it, the honest output is:
> *"No published CSAT/NPS identified. ACSI does not cover this sector. Review-site signal is
> summarised below as OBSERVED-SIGNAL only."*

Review signals require **sample size, time window, collection method, and known biases** stated
(V9h) — and even then are `OBSERVED-SIGNAL` at `LOW`. Review populations are self-selected and
skewed; never infer enterprise-wide satisfaction from them.

`operations` owns the complaint and reliability data in §7.6. Take it via `handoff`; do not
re-research it, and cite their claims.

## §12.5 Brand Perception & Reputation

`T-12.5` + `C-12.5`. Published rankings (with their methodology named — a ranking whose methodology
you cannot state is marketing), media sentiment over 12 months **with the method stated** (corpus,
window, tool, scoring approach), and reputation risks.

**Empty is a valid render.** For a B2B target with little consumer presence, the honest answer is
usually that public brand data is thin — and saying so is more useful than assembling a sentiment
score from a hundred articles with an unstated method.

## Evidence discipline for this section

- **Every satisfaction and sentiment figure carries its method.** A number without a method cannot
  be compared to anything, including itself over time.
- **Traffic and app data are licensed and modelled.** Similarweb and equivalents are `MEDIUM`
  modelled estimates; name the source and check quoting terms. `appendices` owns the detail in
  §21.7.
- **Do not use social-media volume as a proxy for sentiment.**

## Traps

- **Review-site star averages are the single most misused number in account research.** They are
  `LOW`-confidence `OBSERVED-SIGNAL` with a selection bias, and they are not comparable across
  companies with different review volumes.
- **A "Best Places to Work" or industry award is a marketing artefact** unless you can state the
  methodology and the entrant pool.
- **Do not infer customer concentration here** — `business-model` owns it in §5.7 from the filing
  disclosure.
- **Media sentiment over an unstated corpus is not evidence.**

## Fragment

Claims `C-12.1-nn` … `C-12.5-nn`. Sources `S-14nn`. Gaps `G-14nn`. Coverage for §12 recording which
benchmark sources (ACSI, regulator complaint databases, ranking publishers) you reached and which do
not cover this sector — the "does not cover this sector" case is `not_applicable`, not a gap.
Charts `C-12.1`, `C-12.5`; figure `F-12.3`. `handoff` to: `appendices` (digital-presence detail for
§21.7), `opportunity` (CX gaps that are evidenced, not inferred), `account-strategy` (brand and
reputation constraints on messaging).
