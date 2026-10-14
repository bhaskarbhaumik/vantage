# Brief — whitepaper plan

Write `$PLAN_DIR/doc.json`, validating against `$HARNESS_DIR/state/doc.plan.schema.json`.

## Read first

1. `$PLAN_DIR/story.md`
2. `$HARNESS_DIR/blueprint/document-blueprint.md` — treatments, appendices, numbering
3. `$PLAN_DIR/doc.json` — the derived scaffold
4. §0 and §1 in full; the opening verdict of every body section

## Your decisions

You are not rewriting the dossier. You decide **what a reader gets, in what order, with what
framing**.

### 1. The abstract
400–700 characters, shown as a callout on the front-matter page. The verdict and its single
biggest caveat — not a description of the document.

### 2. Per-section treatment
`verbatim` where the dossier's prose is the value; `condense` where the reader does not need the
workings (keeps every table, register, chart, figure, callout and marker-bearing paragraph);
`summary` only where you can genuinely say it shorter — you then author that text and it must keep
its claim references and markers; `omit` almost never. `DEPTH` sets the default; override where
the story demands it (a regulatory thesis keeps §14 `verbatim` even at `standard`).

### 3. Leads
One italic line under each section heading saying what it is for, written against *this* client.

### 4. Callouts
Add a `disclaimer` callout carrying the scoring sentence under any section that reports a score
(§1.6, §8.2, §15.1, §18.1, §19.4, §14.7). Add a `warning` callout where the dossier's QA flagged
something a reader must not miss — a suppressed model, an ANNOUNCED-not-closed transaction, an
erratum that changes a figure.

### 5. Appendices
`appendix_policy: "selected"` with `appendices` naming §21 subsections — usually `21.1` (sources),
`21.8` (verification) and `21.11` (contradictions and gaps).

## Do not

- Change any section number, or supply a `heading_override` that does.
- Set `page_break_before` on more than a handful of sections.

## Check before you finish

- Abstract is 400–700 chars and states a verdict.
- Every kept section has a lead written for this client; every scored section its disclaimer.
- `$ENGINE render "$DOSSIER" --out "$RUN_DIR" --format docx` reports `doc` as `authored`.
