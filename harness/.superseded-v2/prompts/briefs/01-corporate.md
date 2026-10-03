# Brief — `corporate` (block 1)

**Stage** 1 · **Owns** §2.1–2.4 · **Block** `100`–`199` · **Envelope** ~1,700 w
**Output** `<RUN_DIR>/sections/02-company.md` · **Fragment** `corporate.json`

Read `_common.md` first. **Tier 2 — write nothing about the pursuing organization.**

## Mission

Establish how the company is *built*: its history compressed to what still explains today, how it
organises value, who controls it, and where it physically operates. Every downstream agent uses
your segment map and footprint; get those right before polishing the history.

## §2.1 Corporate Identity & Evolution — ≤450 w · bar `T1–2×1`

Not a chronology. Answer: **which past decisions still constrain or explain present strategy?**

Founding and original business model · the 3–5 pivots that changed what the company is (not every
acquisition — the ones that changed the answer to "what business are you in") · how the current
portfolio was assembled · any identity-level event still shaping the present (a major incident,
divestiture, bankruptcy, nationalisation, founder transition).

**`+v2.2` Mission, vision & stated values** — two lines, not a values essay: quote the official
mission/vision verbatim (T2, sourced) and note any explicit values that recur in leadership
communication. This exists only so §12.3 messaging can align to the client's own language — its
weight is one sentence of downstream utility, not a paragraph of corporate copy. Skip it if the
company publishes none; do not paraphrase marketing into a "mission".

A `VZ-1nn` timeline spec is warranted only if the pivots are genuinely hard to follow in prose.

## §2.2 Business Unit & Segment Map — ~500 w · bar `T1×1` segment disclosure

The single most-reused output of this agent.

Reported segments exactly as the company defines them · revenue and operating profit per segment
for the latest FY with period labels · segment leadership where disclosed · what each segment
actually sells and to whom · any restatement or resegmentation in the last 3 years — **flag it
loudly**; peers comparing across years will otherwise compare incompatible numbers.

Segment revenues must sum to total with reconciling items noted (QA F2d). If the company reports
one segment, say so plainly and describe the internal structure from other disclosures.
Private/subsidiary: build the best-available structure from statutory accounts and organisational
announcements, flagged accordingly.

## §2.3 Ownership, Governance & Control — ~400 w · **Pub only** · bar `T1×1`

Holders >5% with as-of dates · dual-class or golden-share structures and what they enable ·
board size, independence, average tenure, notable domain competence · committee structure ·
activist positions with dates · recent governance events.

**Private variant:** replace with sponsor/founder control analysis — sponsor name, entry date and
vintage, stated hold period, board control, co-investors, disclosed exit signals. State the
substitution in the section header. A PE sponsor near end-of-hold changes pursuit timing more than
almost any other fact in the dossier, so this is worth the effort.

## §2.4 Global Footprint — ~300 w · bar `T1–2×1`

Locations **by function**, not a country list: HQ · manufacturing/plants · R&D · data centres ·
shared-service and GCC/GBS centres · major sales geographies.

**GCC/captive centres are load-bearing.** They feed §6.6 (sourcing model), which feeds §12.5
(commercial construct). Search deliberately: careers pages by city, GCC announcement press,
"global capability centre" / "global business services" / "shared services centre" plus the
company name, and local-market business press in India, Poland, Mexico, Philippines, Costa Rica.
An unlisted GCC is a material miss; record what you searched even when you find nothing.

## Fragment duties

- `canonical_facts_proposed`: segment names and latest-FY segment revenues, employee counts by
  region if disclosed, GCC locations.
- `handoff` to `technology`: any GCC/shared-services finding, for §6.6.
- `handoff` to `financials`: any restatement or resegmentation affecting comparability.
- `handoff` to `leadership`: segment leaders you sourced (do **not** profile them — that is §8.1).

## Traps

- History is the easiest section to overwrite and the least decision-relevant. Hold the 400-word
  envelope; §2.2 and §2.4 deserve the budget instead.
- Segment definitions differ between the 10-K, the earnings release, and the investor deck. Use
  the **filing** definition and note the divergence.
- Ownership percentages go stale fast. Always carry the as-of date.
- Do not profile executives here, do not describe technology here, do not assess risk here. Those
  belong to `leadership`, `technology`, and `risk-reg` respectively.
