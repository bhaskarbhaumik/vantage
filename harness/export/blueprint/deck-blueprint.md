# Deck blueprint

The deck answers one question for one room: **should the pursuing organization spend pursuit
budget on this account, and on what first?** Everything else is supporting material.

## Length

| Depth | Slides | Carries |
|---|---:|---|
| `exec` | 12–18 | §1 only — verdict, snapshot, findings, opportunities, risks, readiness, actions |
| `standard` | 25–35 | the above + one slide per body group §3–§20, with key charts |
| `full` | 45–70 | the above + per-section slides, charts, figures and detail tables |

## Spine

1. **Cover** — client, "Vantage dossier", as-of, tier, vertical. The renderer adds Overall
   Confidence (EQI) and the verification result; do not restate them in `body`.
2. **How far this dossier can be trusted** — EQI, verification result, open blockers, checks.
3. **Read before use** — the dossier's banner, when it has one.
4. **The verdict** — §1's opening verdict as a dark statement.
5. **Company at a glance** — up to 4 KPI tiles from §1.1, then the snapshot card.
6. **What we found** — divider, then one statement per §1.2 finding (cap 6): the finding as the
   title, its implication as the body, its status/confidence as the subtitle.
7. **Where the work is** — divider, the §1.4 table, the attractiveness chart (suppressed
   composites left out, never estimated).
8. **Risks and watchpoints** — §1.5 as risk | mitigation stance, plus severity vs likelihood.
9. **Engagement readiness** — §1.6 as a matrix. A SUPPRESSED composite stays the word SUPPRESSED.
10. **Recommended next actions** — §1.7 as a timeline (≤ 5 steps).
11. *(standard/full)* **The evidence** — divider, then §3–§20.
12. **Material unknowns** — the §21.11 gaps §1 cites. Never omit this slide.
13. **Verification and disclosures** — §21.8.
14. **Closing** — the scoring disclaimer.

## Layouts

Only these. A plan naming anything else is invalid.

| `layout` | Use for | Hard limits |
|---|---|---|
| `title` | the cover | set `image_query` for a splash image |
| `section` | dividers | title + subtitle; `icon`, `image_query` |
| `statement` | one idea that must land | title ≤ 230 chars, body ≤ 300 |
| `bullets` | a short list | ≤ 7 bullets, ≤ 230 chars each |
| `two-column` | paired lists (risk / stance) | ≤ 7 rows each |
| `kpi` | 2–4 headline numbers | value ≤ 12 chars; `icon` per tile |
| `table` | a register extract | ≤ 8 rows, ≤ 6 columns |
| `chart` | a quantitative comparison | needs `chart` |
| `figure` | a dossier diagram | needs `figure` (copy the figure-spec verbatim) |
| `quote` | a leadership statement | needs `attribution` |
| `timeline` | dated actions | ≤ 5 steps |
| `matrix` | a scored grid | renders as a table |
| `closing` | the end card | — |

Over-length content is trimmed with an ellipsis (markers are re-appended). That is a safety net,
not a licence — write to the limit.

## Rules that are not style

- **Every substantive slide sets `source_sections`.**
- **`claim_refs` for anything quantitative.** They print in the slide footer.
- **Never invent a number.** `[ESTIMATED]`, `[DATA GAP]`, `[INTERNAL REQUIRED]` and `SUPPRESSED`
  appear on the slide exactly as the dossier writes them. A range stays a range.
- **Preserve the sign.** The dossier writes negatives with U+2212 (`−`).
- **A score never appears without the disclaimer** — put it in `notes` or `chart.note`.
- **Errata govern.** Where §1 prints a verification erratum, the slide states the corrected reading.
- **`notes` is what the presenter says**, not a repeat of the slide.
- Sentence-case titles, no terminal full stop.
