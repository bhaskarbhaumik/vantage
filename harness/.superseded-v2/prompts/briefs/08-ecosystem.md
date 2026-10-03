# Brief — `ecosystem` (block 8)

**Stage** 1 · **Owns** §9.1–9.5 · **Block** `800`–`899` · **Envelope** ~2,000 w
**Output** `<RUN_DIR>/sections/09-ecosystem.md` · **Fragment** `ecosystem.json`

Read `_common.md` first. **Tier 2 — write nothing about the pursuing organization.**
You score **Model 8 (Vendor Displacement Potential)** — four dimensions only. Read
`blueprint/scoring-rubrics.md`.

## Mission

Map the incumbent landscape: who already supplies this client, in what domains, how entrenched
they are, and where a new entrant could get in. This is the competitive intelligence layer of the
pursuit — and it is Tier 2, so it is written **about third parties in general**, not about the pursuing organization.

**Framing discipline.** §9.4 assesses *third-party entry potential*, never "the pursuing organization's chance to
displace". §12.4 does the the pursuing organization-specific version. Getting this wrong fails QA F7a at BLOCKER
severity, and it is easy to slip into.

## §9.1 Technology Vendor Relationships — ~500 w · bar ≥4 evidenced rows with recency

By domain: vendor · what they supply · scope as evidenced · relationship start where known ·
**signal recency** (how recent is the evidence) · source · confidence.

Reconcile against `technology`'s §6.1 handoff. §6.1 is *what the client runs*; §9.1 is *who
supplies and supports it*. They overlap and must not contradict — where §6.1 evidences a platform,
§9.1 covers the commercial relationship around it. Cross-reference rather than duplicate.

Signal recency is mandatory on every row. A 2019 case study and a 2026 press release are not
equivalent evidence of a current relationship, and Model 8 scores them differently.

## §9.2 SI & Consulting Landscape — ~400 w · bar `any×1` per SI named

Which system integrators, consultancies, and managed-service providers are evidenced at this
account, in which domains, at what apparent scale, with what recency.

Evidence: joint press releases · vendor case studies naming the client · analyst-report summaries ·
public procurement awards (`V-GOV`: rich and definitive) · client executives naming partners in
talks · SI job postings referencing the client account · conference co-presentations.

`[UNVERIFIED]` is tolerated here **with an explicit flag** — incumbency evidence is genuinely
thin outside regulated sectors. Contract values only if disclosed (QA F4d is a BLOCKER).

**Never estimate a contract value or an expiry date.** Not from deal-size heuristics, not from
"typical five-year terms", not from engagement start plus a standard duration. This is the
specific fabrication v2.0 was designed to eliminate.

## §9.3 Alliance & Ecosystem Moves — ~400 w · bar `T2×1` per alliance, within 18 mo

Hyperscaler, ISV, startup, and academic partnerships announced in the last 12–18 months, and what
each signals about direction. Joint go-to-market arrangements where the client is the *partner*
rather than the customer — this distinction matters and is often blurred in press releases.

The signal is directional: three hyperscaler-AI partnerships in a year says something about intent
that no strategy statement does.

## §9.4 Displacement & Whitespace Assessment — ~400 w · Model 8, four dimensions

Per evidenced incumbent, score: entrenchment (30%) · satisfaction signals (20%) · contract timing
evidence (25%) · switching cost (25%). **Dimension 5 (differentiation) is the pursuing organization-specific and
deferred to §12.4** — report the four-dimension partial and point there (QA F6g).

Then: **whitespace** — domains with *no* evidenced incumbent. Absence of evidence is weak evidence
of absence, so label these `[INFERENCE]` with the basis stated ("no supplier evidenced across N
queries covering domain X"). Whitespace is often the most actionable output of this section, and
also the easiest to overstate.

Contract-timing evidence defaults to `3` for most private-sector accounts because expiry dates are
not public. A `5` requires a §9.5 row. Say so on the render.

## §9.5 Contract & Renewal Signal Map — ~300 w · `NEW v2.1` · bar **none**

**Publicly evidenced** contract, renewal, and re-compete signals only:

Public procurement award notices and their stated periods of performance · published RFPs, RFIs,
and tender notices · disclosed multi-year commitments in filings or material-contract exhibits ·
transition and rebid announcements · 8-K material-contract disclosures · regulatory filings
naming supplier arrangements.

Row: `Signal · Counterparty · Evidenced date · Window implied · Source · Confidence`.

**An empty table is the expected and correct render for most private-sector accounts.** Say so
explicitly — "no publicly evidenced contract or renewal signals identified as of {date}; contract
terms are not disclosed for this client" — rather than leaving the section blank or, far worse,
populating it with inference.

`V-GOV` is the opposite case: USAspending, FPDS, SAM.gov, TED, and Contracts Finder publish award
dates, ceilings, option years, and incumbents. Here, an empty §9.5 means the research was
incomplete, not that the data is private. Search these portals deliberately.

## Fragment duties

- `scoring_inputs.displacement`: per-incumbent Model 8 four-dimension blocks.
- `canonical_facts_proposed`: named incumbent SIs and their evidenced domains.
- `handoff` to `account-strategy`: the incumbent set and their entrenchment scores, for §12.4.
- `handoff` to `engagement`: any dated §9.5 signal — these become §13.1 trigger events.

## Traps

- Vendor case studies are marketing and systematically overstate scope and outcome. Report what
  was evidenced, not what was claimed.
- A partnership announcement is not a customer relationship. Read carefully which direction the
  commercial relationship runs.
- Do not assume the absence of a named SI means no SI. It usually means no public disclosure.
  Say which one you mean.
- Do not write win strategy, differentiation, or competitive positioning. That is §12.4, a
  different agent, a different tier.
