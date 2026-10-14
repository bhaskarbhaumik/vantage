# Brief — microsite plan

Write `$PLAN_DIR/site.json`, validating against `$HARNESS_DIR/state/site.plan.schema.json`.

## Read first

1. `$PLAN_DIR/story.md`
2. `$HARNESS_DIR/blueprint/microsite-blueprint.md` — the two modes and the default grouping
3. `$PLAN_DIR/site.json` — the derived scaffold

## Your decisions

The smallest plan, and the easiest to over-think.

1. **Mode** — `microsite` renders the dossier's sections as a browsable document; `deck` renders
   the DeckPlan as an HTML deck. `SITE_MODE` for the run is given; keep it unless told otherwise.
2. **Grouping and order** — change the default when the account's story does. Every page needs at
   least one section that exists in this dossier.
3. **Page summaries** — one or two sentences per page, written for this client, so a reader who
   arrived from a link knows why the page matters.
4. **Page visuals** — an `icon` (lucide name) per page, and an `image_query` for pages that open a
   major part of the story.

## Do not

- Author content. Microsite body text is rendered *from the dossier*.
- Reorder sections within a page — they render in dossier order, which their cross-references
  assume.

## Check before you finish

- Every `section_ids` entry resolves (`$ENGINE inspect "$DOSSIER"`).
- `$ENGINE render "$DOSSIER" --out "$RUN_DIR" --format html` reports `site` as `authored`.
