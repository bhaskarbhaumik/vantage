# Brief — deck plan

Write `$PLAN_DIR/deck.json`, validating against `$HARNESS_DIR/state/deck.plan.schema.json`.

## Read first

1. `$PLAN_DIR/story.md` — the narrative. Your deck argues *that*.
2. `$HARNESS_DIR/blueprint/deck-blueprint.md` — the spine, the layouts, the limits.
3. `$HARNESS_DIR/blueprint/design-system.md` — emphasis, charts, icons, imagery.
4. `$PLAN_DIR/deck.json` — the derived scaffold you are replacing.
5. The dossier sections the story points at, in full.

## Build

Follow the spine. Then make it argue.

**Findings are where a deck is won or lost.** The scaffold turns each §1.2 row into a statement
whose title is the finding's first sentence. Rewrite each title as the *claim* in the fewest words
that still carry it, and the body as what it means for the pursuit. Keep the status and
confidence in `subtitle`. Six is the ceiling; four is usually better.

Weak: *"No IT systems integrator is evidenced at the company after a 16-firm search"*
Better: *"No incumbent integrator is evidenced"* / body: *"There is no displacement play; the
alternatives are in-house build and deferral (C-19.7-01, [INFERRED], LOW)."*

Where §1 prints a verification erratum for a finding, use the **corrected reading**.

## Visuals

- `chart` slides: prefer the dossier's own chart-data blocks for the sections the story leans on
  (copy the spec; never edit a value). Good candidates: §6 financial trend, §18 attractiveness,
  §14 risk severity/likelihood, §11 peer benchmarks. Never chart a SUPPRESSED composite; a
  dimension chart is fine if its title says the composite is suppressed.
- `figure` slides: one or two dossier figures that carry the argument (an org/decision map, a
  dependency or value chain). Copy the figure-spec verbatim into `figure`.
- `icon` on every content slide and KPI tile — lucide names (check with
  `get-icon iconify search <term> -p lucide`). Keep one icon per idea across the deck.
- `image_query` on the cover and on each divider — specific to the client's industry and the
  section ("bauxite mine haul trucks at dawn", not "business").

## Provenance

- `source_sections` on every substantive slide.
- `claim_refs` for anything quantitative — they print in the footer.
- `notes` = what the presenter says, including the caveat that did not fit on the slide. Put the
  scoring disclaimer in `notes` of any scored slide (the renderer prints it on the face).

## Length

`DEPTH` decides: `exec` 12–18, `standard` 25–35, `full` 45–70.

## Check before you finish

- Every `layout` is one the blueprint lists; no slide exceeds its limits.
- No SUPPRESSED composite appears as a number anywhere; every negative kept its `−`.
- Every marker in a source cell survives on the slide.
- Material unknowns and Verification slides are present; the closing card is last.
- `$ENGINE render "$DOSSIER" --out "$RUN_DIR" --format pptx` reports `deck` as `authored`.
