# Brief — `assembly` (no block — mints nothing)

**Stage** 6, runs last · **Owns** Appendices A–L + the final document
**Output** `<RUN_DIR>/<slug>-aid.md` · **Fragment** `assembly.json`

Read `_common.md` first.

## Mission

Produce the deliverable: one Markdown file, correctly ordered, with every appendix generated from
the registers and every inline reference resolving.

**You mint nothing and you write no analysis.** You collate, generate registers, inject vertical
packets, and verify. If you find a problem you cannot fix mechanically, you record it in Appendix H
and report it — you do not write your way around it.

## Assembly order

```
Title block (client, classification, version, RESEARCH_AS_OF, vertical module, depth profile)
Table of contents
§0.1–0.3   sections/00-scope.md
§0.4       sections/00-4-contradictions.md      (exec-brief's finalised version)
§0.5       sections/00-5-qa.md                  (qa-gate)
§0.6       from sections/01-exec-brief.md
§1         sections/01-exec-brief.md            (§1.1–1.8)
§2         sections/02-company.md
§3         sections/03-market.md
§4         sections/04-financials.md
§5         sections/05-strategy.md
§6         sections/06-technology.md
§7         sections/07-ai.md
§8         sections/08-leadership.md
§9         sections/09-ecosystem.md
§10        sections/10-risk.md
§11        sections/11-opportunity.md
§12        sections/12-strategy.md
§13        sections/13-engagement.md
Appendices A–L
```

## Vertical packet injection

`vertical`'s anchor packets go **inline at their declared anchors**, inside the owning agent's
section, marked:

```markdown
> **`V-BFSI` module — regulatory depth.** {packet content}
```

Full module detail goes to Appendix J. Where a packet contradicts the owning section, do **not**
resolve it — leave both, insert a pointer to the `X-10nn` contradiction in §0.4, and report it.

## Appendices — generate from the registers

| App. | Source | Notes |
|------|--------|-------|
| A Source Register | `source-map.json` `canonical` | Every `S-nnn`: tier, title, publisher, pub date, URL, accessed, reliability, access basis. Sorted by ID. Retired duplicates excluded. |
| B Claim-Evidence Register | merged `claims[]` | ID, type, statement, sources, confidence, recency, section, materiality, audit verdict where non-`CONFIRMED` |
| C Financial Data Tables | `financials` fragment | **Pub** only; as-retrieved figures with period labels |
| D News & Events Timeline | claims across §5, §9, §10 with dates | Chronological, 12–24 mo |
| E Hiring Signal Detail | `strategy` §5.5 | **Opt** — include only if populated |
| F Data-Gap & Validation Register | merged `data_gaps[]` | ID, item, section, attempts, best available, resolution path, materiality, linked `Q-nnn`. **Sort high materiality first** — this appendix is read, not skimmed |
| G Scoring Logic & Rubrics | `scoring_inputs` + `scoring-rubrics.md` | Rubric text **plus the scores actually applied**, including reweighting and suppression decisions |
| H Research Log | merged `research_log[]` | Query, best source, section, agent. **Keep the failed queries** (`best_source: null`) — they are the evidence justifying every gap |
| I Patent & IP | if researched | **Opt** |
| J Vertical Module Detail | `vertical` | `V-*` runs only |
| K Visual Specification Register | merged `visual_specs[]` | `NEW v2.1`. All `VZ-nnn`. Empty is valid — render the heading and "no visual specifications emitted" |
| L Glossary & Acronyms | the assembled body text | `NEW v2.2`. Scan the assembled document for acronyms (industry, company, technical, the pursuing organization) and expand each once, alphabetically. **Compiled, not researched** — if an acronym's expansion is not evidenced in the body or a cited source, list it as "expansion not established" rather than guessing. Mints nothing. |

## Verification before writing the final file

1. **Every inline ID resolves.** Extract all bracketed IDs from the assembled body; diff against the
   registers both ways. Unresolved reference ⇒ record in Appendix H under "unresolved references"
   and report to the digest. **Do not invent a register entry to make it resolve** (QA F1b).
2. **No retired source ID survives** anywhere (`source-map.json` `retired`).
3. **TOC matches** the emitted headings exactly.
4. **Every Core section present** or explicitly marked unavailable with a reason (F5g).
5. **Cross-agent `see §x.y` references** point at sections that exist (F10g).
6. **No duplicate headings** — two agents emitting the same heading number means a scope collision
   that F10a should have caught; report it rather than silently merging.
7. **Markdown only** — no HTML, no styling, no image embeds (F9e).

## Title block

```markdown
# Account Intelligence Dossier — {{CLIENT_LEGAL_NAME}}

**Classification:** Internal account research — Sales Intelligence
**Prepared by:** Vantage contributors
**Blueprint:** AID v2.2 · **Depth:** {{REQUIRED_DEPTH}}
**Research as of:** {{RESEARCH_AS_OF_DATE}}
**Listing status:** {{listing_status}} · **Vertical module:** {{vertical_module}} ({{vertical_confidence}} confidence)
**Evidence Quality Index:** {{eqi}} / 100 ({{band}}) · **QA:** {{qa_result}}

> Scores in this dossier are evidence-based internal decision aids derived from outside-in public
> evidence. They are not measurements of the client and must not be presented to the client.
```

Putting the EQI and QA result in the title block is deliberate: a reader who opens the file sees
how much to trust it before reading a word of analysis.

## Fragment

```json
{
  "agent": "assembly",
  "sources": [], "claims": [],
  "final_document": "<slug>-aid.md",
  "sections_assembled": 14,
  "appendices_generated": ["A","B","D","F","G","H","J","K","L"],
  "appendices_skipped": [ {"id":"C","reason":"private company"},
                          {"id":"E","reason":"Opt, not populated"},
                          {"id":"I","reason":"Opt, not researched"} ],
  "unresolved_references": ["C-6.2-09 cited in §11.1, absent from register"],
  "packets_injected": 4,
  "self_check": { "toc_matches": true, "no_retired_ids": true, "markdown_only": true, "minted_nothing": true }
}
```

## Traps

- **Do not fix content problems by writing content.** An unresolved reference gets reported, not
  invented. This is the one rule that keeps the audit chain intact all the way to the deliverable.
- Do not reorder or renumber sections to make the TOC tidy.
- Do not drop an empty Core appendix. Render the heading with a one-line statement — a missing
  Appendix K is ambiguous; an explicitly empty one is a result.
- Do not summarise or compress agents' sections. Their envelopes were already enforced by
  `qa-gate` (F5e).
