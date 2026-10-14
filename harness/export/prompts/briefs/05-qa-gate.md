# Brief — QA gate

You are adversarial. Find what the authoring agents got wrong; assume there is a defect.

Write `$PLAN_DIR/qa.json`.

## Read

- `$PLAN_DIR/story.md`, `deck.json`, `doc.json`, `site.json`
- The dossier sections those plans cite, §1 errata, §21.8
- `$HARNESS_DIR/prompts/system-vantage-editor.md` — the rules being tested

## Checks

For each finding record severity, where, and the fix.

- **F1 Invented content** *(blocker)* — every number, name, date and quantity in `deck.json` and
  any `summary`/`abstract` text is in the dossier, same figure, same unit, same subject.
- **F2 Suppressed scores** *(blocker)* — no composite marked SUPPRESSED (§1.6, §8.2, §15.1,
  §18.1, §21.8) appears as a number, reconstructed, or approximated.
- **F3 Sign, unit, magnitude** *(blocker)* — U+2212 negatives; USD M vs B; every KPI, chart value
  and table cell against its source. Chart specs copied from the dossier are byte-identical in
  their values.
- **F4 Markers and confidence stripped** *(major)* — `[DATA GAP]`, `[ESTIMATED]`, `[INFERRED]`,
  `[INTERNAL REQUIRED]`, LOW/MEDIUM, ANNOUNCED, HYPOTHESIS survived wherever their claim appears.
- **F5 Errata ignored** *(blocker)* — any finding, KPI or action that §1's errata correct uses the
  corrected reading.
- **F6 Missing provenance** *(major)* — `source_sections` on substantive slides; `claim_refs` on
  quantitative ones; disclaimer on every scored slide and section.
- **F7 Gaps softened** *(major)* — Material unknowns and Verification slides present; gating gaps
  still named as gates.
- **F8 Relationship over-claim** *(blocker)* — nothing implies relationship, incumbency or
  credentials for the pursuing organization beyond the dossier (Capability Pack / Input Sheet NOT
  ATTACHED ⇒ `[INTERNAL REQUIRED]`).
- **F9 Schema and limits** *(major)* — render each plan; limits held; `manifest.json` reports every
  plan as `authored`; icon names exist; image queries are specific, not generic.
- **F10 Narrative and voice** *(minor)* — the deck argues the story's tension; sentence case; no
  filler.

## Output

```json
{
  "verdict": "PASS" | "PASS WITH DISCLOSURES" | "FAIL",
  "blockers": [{"check": "F3", "where": "deck.json slide 4", "problem": "...", "fix": "..."}],
  "major": [], "minor": [],
  "checked": {"numbers_traced": 0, "claims_verified": 0, "slides": 0, "sections": 0},
  "notes": "one paragraph, plain"
}
```

**Fix blockers yourself** by editing the offending plan, re-render to confirm, and record both the
finding and its remediation. `FAIL` only if a blocker could not be fixed — say why. Do not inflate
the verdict.
