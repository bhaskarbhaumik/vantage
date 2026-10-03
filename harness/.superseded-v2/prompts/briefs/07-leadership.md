# Brief — `leadership` (block 7)

**Stage** 1 · **Owns** §8.1–8.4 · **Block** `700`–`799` · **Sole owner of** `P-nn`
**Envelope** ~2,350 w · **Output** `<RUN_DIR>/sections/08-leadership.md` · **Fragment** `leadership.json`

Read `_common.md` first. **Tier 2 — write nothing about the pursuing organization.**
You score **Model 6 (Stakeholder Influence & Accessibility)**. Read `blueprint/scoring-rubrics.md`.

## ⚠️ The hardest constraint in this harness

You write about **real, named, identifiable people**. Two rules override everything else:

1. **Public professional facts only.** Role, tenure, prior employers, education, stated
   priorities, sourced public statements. Every named person needs `T1–T2×1` — no exceptions, no
   unsourced names (QA F4a, BLOCKER).

2. **No personality profiling. No communication-style inference. No speculation about private
   circumstances, motivations, or "what they really want."** Not "likely a consensus builder", not
   "appears risk-averse", not "probably frustrated with the pace of change". This is a
   BLOCKER-severity check (F4b), and it is the rule most often broken in practice because the
   temptation to profile is strong and the output sounds insightful.

The legitimate substitute for profiling is **evidence of stated priorities**: what has this person
publicly said they are trying to do, with a date and a source. That is more useful to an account
team than any inferred trait, and it is defensible.

## §8.1 Executive Leadership Profiles — ~700 w · bar `T1–2×1` **per person**

Cover the roles relevant to this pursuit: CEO, CFO, and whichever of CIO / CTO / CDO / CAIO exist,
plus BU leaders for segments in pursuit scope (from `corporate`'s §2.2 handoff) and any function
head named in `STRATEGIC_PURSUIT_OBJECTIVES`.

Per person: name · exact title · appointment date and tenure · prior employers and roles ·
functional background · scope of responsibility as disclosed · **stated priorities with claim IDs
and dates** · sourced public statements (≤25 words, attributed, dated).

Where to look: DEF 14A and annual-report bios (T1) · corporate leadership pages (T2) · appointment
press releases (T2) · earnings-call speaker attributions (T2) · published conference talks and
credible interviews (T3–T4).

**Vacancies and interim appointments are findings.** A CIO role open for eight months, or a third
CFO in four years, is material intelligence about decision velocity. Record it.

Recent arrivals matter disproportionately: an executive under 12 months in role is typically still
setting agenda and forming vendor relationships. Note tenure explicitly for that reason.

## §8.2 Buying Centers & Decision Dynamics — ~500 w · bar `T1–2×1` **or** a labelled `[INFERENCE]` block

Where technology, operations, and transformation spend is approved · evidenced budget authority ·
procurement organisation and its stated posture · approval thresholds where disclosed · known
cycle timing (budget-setting months, fiscal-year boundary).

Most of this is not public for private-sector clients. **Segregate what you know from what you
infer**: an evidenced block with sources, then a clearly headed `[INFERENCE]` block whose basis is
stated. Do not blend them into confident prose.

**`+v2.2` IT organisation & governance structure** — where evidenced: the CIO/CTO/CDO reporting
line (to CEO? to CFO? to COO — a materially different budget posture), the IT governance model
(central vs. federated, any published operating model), and who owns the technology budget. A CIO
reporting to the CFO signals cost-led IT; one reporting to the CEO signals strategic IT — that
distinction shapes §12.5. Keep it factual and sourced; where it is inference, label it.

`V-GOV`: procurement is regulated and largely public — apply the module's procurement-regulation
content and expect much higher confidence here.

## §8.3 Stakeholder Register (canonical) — table · Model 6

The **single source of truth for people** in this dossier. §12.3 and §13.2 reference `P-nn` and
must never re-profile anyone.

Per `P-nn`: name · title · influence (H/M/L) **with basis** · accessibility (H/M/L) **with basis** ·
stated priorities as claim IDs · sources · priority quadrant.

Model 6 is **two independent axes with no composite** — collapsing them destroys the only decision
the model supports. Both axes require an explicit basis statement:

`Accessibility: Medium (INFERENCE: keynote speaker at two 2026 industry events [S-712]; no evidenced the pursuing organization relationship)`

**State once, prominently:** when `KNOWN_RELATIONSHIP_CONTEXT` is `NONE`, accessibility is
structurally biased low for everyone, because absence of public evidence of a relationship is not
evidence of absence. Without that caveat the register reads as a finding when it is an artefact.

Accessibility High requires `KNOWN_RELATIONSHIP_CONTEXT` evidence — **the only place the pursuing organization input
enters Tier 2**, and only as a scoring input, never as narrative. Do not write about the pursuing organization here.

## §8.4 Workforce Profile & Talent Strategy — ~400 w · `+v2.2` · bar `T1–2×1` human-capital disclosure

The talent base the transformation runs on — **aggregate populations, never named individuals.**
The two people-rules above (F4b) still bind: this is headcount and cohorts, not profiles.

Total headcount and its 2–3 year trend · geographic and functional distribution where disclosed ·
attrition/turnover where disclosed · unionisation and organised-labour exposure (material to
delivery models and change programmes) · stated talent strategy — reskilling/upskilling programmes,
tech-talent hiring posture, return-to-office or location strategy · any disclosed talent risk
(skills shortage, key-person concentration, wage inflation).

Primary source is the 10-K **Human Capital** disclosure (mandatory for US filers since 2020) plus
the sustainability/ESG report and IR. Distinguish this from §5.5: that section reads *forward*
hiring signals from job postings (hypothesis-grade); this is the *disclosed current* workforce
(evidence-grade). Cross-reference §6.6 for GCC/captive headcount rather than re-counting it.

Gap-tolerant for private companies — headcount is often the only workforce figure available; render
what you have and gap the rest.

## Fragment duties

- `stakeholders[]`: every `P-nn`, fully populated.
- `canonical_facts_proposed`: CEO, CFO, CIO/CTO/CDO with as-of dates; total headcount with period.
- `scoring_inputs.stakeholder_model6`: per-`P-nn` two-axis scores with bases.
- `handoff` to `account-strategy`: which `P-nn` map to which stated priorities, for §12.3.
- `handoff` to `engagement`: `P-nn` priority quadrants, for §13.2.
- `handoff` to `opportunity`: talent/skills gaps and reskilling programmes from §8.4 — services
  demand signals for §11.

## Traps

- LinkedIn profiles are self-reported and frequently stale. Usable as T5 corroboration; never the
  sole source for a named person's title or tenure.
- Do not infer influence from title alone. A CIO without evidenced budget authority scores Medium,
  and the basis statement should say why.
- Board members are governance (§2.3, `corporate`), not buying-centre stakeholders — unless one
  chairs a technology committee with evidenced programme oversight, in which case say exactly that.
- Do not write engagement plans. You establish who and how reachable; §13.2 decides what to do.
