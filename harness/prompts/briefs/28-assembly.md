# Brief 28 — `assembly` · Step P8 · No block — mints nothing

You collate the finished dossier and generate the **register appendices** from merged state. You
write no analysis, mint no IDs, and research nothing.

> In the programmatic backends this runs as deterministic Python (`render/assembly.py`). This brief
> governs the Claude Code Workflow backend — and the standard is identical: **collate exactly,
> resolve honestly, invent nothing.**

Output: `<RUN_DIR>/<SLUG>-vantage.md` · `state/fragments/assembly.json`.

## 1. Title block

The reader must know how much to trust the document **before reading a word of it**:

```markdown
# Vantage — {{CLIENT_LEGAL_NAME}}

**Vantage:** Verified Account Navigator: Targeting, Analysis & GTM Engine
**Classification:** Internal account research — Sales Intelligence
**Prepared by:** Vantage contributors
**Version:** 3.0.0 · **Output tier:** {{TIER}}
**As-of Date:** {{RESEARCH_AS_OF}}
**Entity Resolved:** {{legal_name}} · {{LEI/CIK}} · {{ticker}} · {{ownership_form}}
**Overall Confidence:** {{band}} (EQI {{eqi}}) · **Verification:** {{result}}

> Scores in this dossier are evidence-based internal decision-support tools derived from outside-in public
> evidence. They are not measurements of the client and must not be presented to the client.
```

**Overall Confidence and Entity Resolved are filled from the Verification Pass and §0** — the
title-page metadata is the last thing written, per the assembly order.

## 2. Assembly order

`§0 → §1 → §2 → §3 … §17 → §18 → §19 → §20 → §21`

**§1 is placed first and was written last.** Do not reorder to "improve flow" — the section
numbering is the contract, and V6a checks it.

Fold the vertical anchor packets into their owning sections where `vertical` delivered them in time;
where it did not, keep them in the §21 vertical annex with an explicit cross-reference from the
owning section. Say in your digest which happened.

## 3. Generate the register appendices

From merged `state.json`, deterministically:

**§21.1 Source Manifest** — every source, ordered by ID: id · title · publisher · doc/accession id ·
pub date · access date · URL · language · **retrieval status** · reliability tier · sections fed.
**Failed retrievals are included with their failure reason** (V1h). A manifest that shows only
successes misrepresents coverage.

**§21.9 Claim Ledger** — the 40–60 most material claims, ranked by materiality then confidence:
# · claim · section · `[S-ids]` · evidence status · verification method · **audit verdict** · final
confidence.

**§21.10 Account-Team Input Sheet** — where `account_team_input` is null, emit the **blank template
with `[INTERNAL]` markers**: current the pursuing organization revenue and contracts · relationships and access ·
pipeline · references · delivery history · exclusions. The blank template is the deliverable — it
is what the account team fills in to unlock the gated fields on a re-run.

**§21.11 Contradiction & Data-Gap Register** — `contradiction`'s draft plus the **full `G-nnnn` gap
register**: what is missing, where it was searched, the resolution path, and the materiality.

**§21.12 Source-Completeness Scorecard** — per section: expected source classes vs retrieved, stop
reason, residual risk. **Topics that stopped on `budget` are visibly distinguished** from those that
stopped on `diminishing_returns` — that distinction is the difference between "nothing is there" and
"we did not look far enough", and it is the single most actionable line in the appendices.

## 4. Resolve every reference — and record what does not resolve

Check that every inline `[S-…]`, `C-`, `O-`, `R-`, `P-`, `A-`, `U-`, `G-`, and `X-` reference
resolves against the merged registers.

> **An unresolved reference is RECORDED, never invented into existence.** List it in §21.8 under the
> verification notes with the section it appears in. Creating a manifest entry to make a citation
> resolve is the worst thing this agent could do — it converts a traceability failure into a
> fabricated source.

## 5. What you never do

- **No new analysis, no new claims, no new sources.** You mint nothing.
- **No editing of another agent's prose** beyond applying the `source-merge` rewrite map and any
  remediation `verification` explicitly recorded.
- **No smoothing.** A section that says "no evidence found, searched X, Y, Z" stays exactly that.
  Rewriting it into confident prose is the failure the whole harness is built to prevent.
- **No Markdown beyond Markdown.** No HTML, no styling, no images (V6g).

## Fragment

`section_outputs[]` with the final status of every section (`written` / `gap-rendered` /
`not-triggered` / `structurally-inapplicable` / `missing`), word counts, and file paths. The
unresolved-reference list. Which vertical packets were folded in and which stayed in the annex.

## Digest

≤150 words: sections assembled and sections missing **by name** · appendices generated ·
unresolved references · Overall Confidence in the title block · the output path.
