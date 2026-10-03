# Brief — `strategy` (block 4)

**Stage** 1 · **Owns** §5.1–5.6 · **Block** `400`–`499` · **Envelope** ~2,650 w
**Output** `<RUN_DIR>/sections/05-strategy.md` · **Fragment** `strategy.json`

Read `_common.md` first. **Tier 2 — write nothing about the pursuing organization.**

## Mission

Establish **intent**: what the company says it is doing, what it has actually committed to, and
what its hiring reveals about what it is really building. §5.1 is the most-referenced section in
the entire dossier — every message in §12.3 must trace to a `C-5.1-nn` priority claim, and every
opportunity in §11 is judged on fit to these priorities.

Priority claims must be **quotable, dated, and sourced**. A priority you paraphrase from a website
banner is not usable downstream.

## §5.1 Stated Strategic Priorities — ~500 w · bar `T1–2×2`, each dated

5–7 priorities **in the client's own framing and vocabulary**, each with source, date, and any
budget signal attached to it.

Where to look, in order: the strategy section of the annual report · the most recent investor-day
or capital-markets-day deck (usually the richest single source) · the CEO letter · the last four
earnings calls' prepared remarks · the 10-K MD&A overview.

Use their words. If the client calls it "Simplify, Focus, Grow", that is the priority label — not
your restatement as "operational efficiency". Downstream messaging depends on matching their
vocabulary, and paraphrase destroys that.

Each priority as a row: `Priority (their words) · Source · Date · Budget signal · Claim ID`.

## §5.2 Active & Announced Programs — ~600 w · bar `T2×1` per program

Named transformation programmes in flight: name · scope · status · disclosed budget · disclosed
partners · timeline and milestones · sponsoring executive where stated.

Disclosed budgets here are the highest-value numbers in the dossier for §4.4 and for Model 4's
sizing dimension — a client-disclosed programme budget is the only evidence that lets an
opportunity score `5` on value potential. Hunt for them.

Register only **named** programmes with evidence. "The company is investing in digital
transformation" is not a programme. An empty register is a valid render and a real finding.

## §5.3 M&A & Portfolio Moves — ~400 w · bar `T1–2×1` per deal

Deals over the last 3 years: target, value where disclosed, rationale in the company's words,
integration status · divestitures and what they signal about portfolio direction · stated appetite
and capacity from earnings calls.

Integration status is the pursuit-relevant part: an unintegrated acquisition is a systems-estate
and operating-model problem, which is where services demand originates. Where you find one,
`handoff` to `technology`.

## §5.4 Leadership Statements Digest — ~400 w · bar `T2×2` within 12 mo

Themes across the last four quarters of executive communication, with short sourced quotes
(**≤25 words, one per source**, attributed with date and speaker).

Organise by **theme**, not by event. Note what changed: a theme that appeared two quarters ago and
has intensified is a stronger signal than one repeated verbatim for three years. Note absences
too — a priority that vanished from the narrative is a finding.

Do not profile the speakers. Their bios and roles belong to `leadership` (§8.1).

## §5.5 Hiring & Investment Signals — ~400 w · bar `T5×5` postings min.

A **directional** read, explicitly hypothesis-grade. Every statement here is `[UNVERIFIED]` or
`[INFERENCE]` — job postings are T5 and can never support a `[FACT]` (QA F3a).

Role clusters being hired and their skill signatures · locations, especially new ones ·
seniority pattern (a new VP-level role is a stronger signal than twenty individual contributors) ·
technology named in requirements — this is often the only public evidence of a stack decision,
so `handoff` to `technology` · disclosed investments and site announcements.

Record your sampling method and date: what you searched, how many postings you saw, over what
window. Without that, the reader cannot weigh the signal. Detail tables go to Appendix E.

## §5.6 Innovation & R&D Profile — ~350 w · `+v2.2` · bar `T1–2×1` · empty is valid

**Where the company invents, and how it funds it** — distinct from §5.2 (named transformation
programmes) and from §7 (AI specifically). Cover only what is evidenced:

R&D spend and intensity (R&D / revenue) with a 2–3 year direction, from the filing's R&D line ·
named innovation labs, design centres, or R&D hubs and their focus · corporate-venture / CVC arm
and its notable bets or fund size · university and startup research partnerships (cross-ref §9.3 —
do not re-inventory alliances, just the R&D-relevant ones) · patent posture at a headline level,
pointing to **Appendix I** for detail if researched.

Interpret, briefly: is this a company that builds capability in-house (labs, high R&D intensity) or
buys it (M&A, CVC)? That read shapes how §11 frames a co-innovation vs. delivery opportunity — but
you only *establish* it here; §11 draws the conclusion.

Gap-tolerant. Many companies disclose little beyond an R&D line, and some disclose nothing. "R&D
not separately disclosed; no innovation-lab or CVC activity evidenced as of {date}" is a valid,
informative render — not a section to pad.

## Fragment duties

- `canonical_facts_proposed`: named strategic priorities with dates, named programmes with budgets.
- `handoff` to `technology`: technology named in postings or programmes.
- `handoff` to `ai-posture`: any AI-related priority, programme, or hiring cluster.
- `handoff` to `opportunity`: disclosed programme budgets — flag as sizing anchors.
- Tag every `C-5.1-nn` priority claim `materiality: high`. §12.3 cannot function without them.

## Traps

- Aspiration is not commitment. "We aim to be the leading X" is a T2 fact about *what they said*,
  not evidence of a funded programme. Keep the layers separate (D3).
- Investor-day decks are 18 months stale within a year. Date-label everything and flag `[stale]`
  past the 12-month strategy freshness window.
- Do not import competitor strategy here — that is §3.2.
- Resist writing the opportunity implications. You establish intent; §11 derives from it. A
  sentence beginning "this creates an opportunity for" belongs to a different agent and fails F7b.
