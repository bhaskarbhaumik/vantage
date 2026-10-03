# Brief 11 — `esg` · Wave A · Block 1100–1199 · Owns §17 ESG, Sustainability & Corporate Responsibility

You cover the licence-to-operate layer — and §17.6, **AI governance and responsible-AI posture**,
which is simultaneously a risk lens and one of the clearest advisory signals in the dossier.

Output: `sections/17-esg.md` · fragment `state/fragments/esg.json`.

## §17.1 ESG Ratings & Performance

`T-17.1` + `C-17.1`. **Per rating: provider, score, and rating date.** An ESG score without its
provider and vintage is uninterpretable — the providers disagree substantially and by design, and
scores are restated.

Headline scores are public; detail is licensed. Cite the provider by name; do not reproduce
licensed rating detail at length. Where providers disagree, show the spread rather than picking one.

## §17.2 Environmental Commitments & Carbon Strategy

Targets **verbatim** from the sustainability report or annual filing. Scope 1, 2, and 3 emissions as
disclosed, with the reporting boundary and any restatement noted. **SBTi validation status** checked
against the SBTi database — "committed" and "validated" are different things and are routinely
conflated. `C-17.2`.

Note the assurance level: whether the emissions data is externally assured, and by whom, materially
changes what it is worth.

## §17.3 Social Responsibility & DEI

**Disclosed data only.** Where a company does not disclose workforce composition, that is the
finding — do not substitute an estimate or a peer average. `leadership` owns the workforce profile
in §10.7; take their aggregate data via `handoff` rather than re-deriving it.

## §17.4 Governance & Ethics

Proxy-based compensation alignment (is pay tied to the stated strategy?), controversy record, board
independence and governance structure. Public companies; adapt to the ownership form otherwise.

## §17.5 Sustainability-Driven Technology Opportunities

CSRD and equivalent reporting readiness, carbon-accounting platforms, product-level footprint
capability, circularity systems. **Neutral framing** — a capability gap, not a pitch.

## §17.6 AI Governance & Responsible-AI Posture

Published AI principles · governance bodies and their composition · **EU AI Act readiness** where
in scope (and the applicability test: which of the company's systems fall into which risk class) ·
model-risk management · AI-related controversies.

This subsection is read in two directions. `ai-readiness` scores Model 3 dimension 4 from it, and
`risk` reads it as regulatory exposure. Write it so both can use it: what exists, what is published,
what is merely stated, and what is absent.

**An absent AI governance posture at a company with production AI is a genuine finding**, not a
gap — state it that way, with the search record.

## Evidence discipline for this section

- **A sustainability report is self-reported.** `independence: self-reported`, `MEDIUM` at best for
  any outcome claim. Targets are `ANNOUNCED`; achieved reductions need external assurance or
  independent corroboration to reach `CONFIRMED`.
- Emissions restatements are routine and material. Use the latest restated figures and note the
  restatement, exactly as in §6.
- Regulatory data (EPA ECHO/FLIGHT/TRI, national registers) is Tier 1 and often contradicts the
  company's own narrative. Where it does, that is a contradiction to hand off, not a discrepancy to
  smooth.

## Traps

- **Do not average ESG scores across providers.** Their methodologies are not commensurable.
- **"Net zero by 2050" is an announcement.** Interim targets and reported trajectory are the
  evidence of whether it means anything.
- **Do not infer DEI or culture from review sites** (V9h; sample-size discipline).
- **Do not treat a UN Global Compact signature or a framework membership as performance.**
  Participation is `ANNOUNCED`.
- **CSRD applicability has a test.** Turnover, balance-sheet, and headcount thresholds plus EU
  nexus — apply it rather than assuming.

## Fragment

Claims `C-17.1-nn` … `C-17.6-nn`. Sources `S-11nn`. Gaps `G-11nn`. Coverage for §17 recording which
rating providers and regulatory databases you reached, and which were paywalled. Charts `C-17.1`,
`C-17.2`. `handoff` to: `ai-readiness` (§17.6 governance findings feed Model 3 dimension 4),
`risk` (environmental enforcement and AI-regulatory exposure), `opportunity` (§17.5 capability
gaps).
