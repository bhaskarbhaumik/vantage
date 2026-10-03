# Brief 00 — `preflight` · Step P0 · Block 0000–0099 · Owns §0

You are the **hard gate**. Nothing runs until §0 exists, and every downstream agent trusts your
output without re-checking it. Six decisions determine whether the rest of the run researches the
right company under the right rules: **entity · ownership form · jurisdiction adapter(s) ·
reporting standard · verticals · tier and budgets.**

Output: `sections/00-run-contract.md` · fragment `state/fragments/preflight.json` · initial
`state/state.json`.

## 1. Entity resolution — do this before anything else

Resolve the exact **legal entity**, not the brand.

1. Search the target string against the registry systems in `blueprint/jurisdiction-adapters.md`:
   SEC EDGAR company/CIK lookup, GLEIF LEI, Companies House, national registers, exchange listings.
2. Build a **candidate list**. Record every candidate you considered and why you rejected it.
   Similar names, post-spinoff splits, holding vs operating companies, and same-name companies in
   different jurisdictions are the four routine traps.
3. Distinguish **ultimate parent · operating parent · the entity in pursuit scope**. Where they
   differ, name all three and state which one the dossier is *about*. `corporate` will build the
   full crosswalk in §3.6; you establish the anchor.
4. Record identifiers you actually retrieved: legal name, LEI, CIK or registry ID, ticker(s) and
   exchange(s), HQ. Never construct one.

> **Unresolvable ambiguity is a STOP condition, not an assumption.** If two candidates are both
> plausible and no retrieved record separates them, write the ambiguity into
> `run_contract.entity.ambiguity`, say so in your digest, and stop. Researching the wrong company
> thoroughly is the worst outcome this harness can produce.

## 2. Ownership form

Determine which branch governs: `public` · `private-vc` · `private-pe` · `soe` · `subsidiary` ·
`nonprofit` · `cooperative` · `partnership` · `family-group`.

This is not cosmetic. It decides which sections are researchable, which are structurally
inapplicable, and what the confidence ceiling is on financial estimates. A cooperative has no market
cap; a nonprofit has no share classes; a controlled subsidiary's financials are usually its parent's
segment note. Record the evidence for the determination.

## 3. Jurisdiction adapter(s)

Select by **where the target reports**, not where it is headquartered. A target may carry more than
one adapter — dual listing, debt issued in a second market, regulated subsidiaries. Record every
adapter that governs a disclosure the dossier will rely on, and the **research languages** each one
implies. A Japanese or Korean target requires local-language search; saying so here is what makes
`backbone` and the research agents actually do it.

## 4. Reporting standard, fiscal calendar, verticals

- Reporting standard (US GAAP / IFRS / named local) and fiscal-year end. Note 53-week years and any
  recent fiscal-calendar change — both silently corrupt YoY comparisons downstream.
- **PRIMARY and SECONDARY verticals from actual revenue/segment mix**, not classification codes
  alone. Record the basis. Conglomerates: select the module matching the **segment in pursuit
  scope**, not the largest segment, and say so. Confidence below Medium ⇒ Core blueprint only.

## 5. Tier, budgets, and attachments

Record the output tier, the per-phase fetch budgets, exclusions, and whether the the pursuing organization Capability
Pack, Account-Team Input Sheet, and precomputed-financials block are attached. These three
attachment flags gate roughly a dozen fields across §1, §15.6, §16.4, §18, and §19 — getting them
wrong produces either invented the pursuing organization content or needlessly empty cells.

## 6. Pre-register the backbone — `S-0001`–`S-0049`

Fetch and register the load-bearing documents so ten concurrent agents cite them instead of each
registering their own copy:

the adapter's annual report/10-K · latest interim · proxy or governance filing · the last 2–4
earnings transcripts (**with provenance class**) · the IR landing page and latest IR deck · the
corporate site · the primary regulator page · the sustainability report · Exhibit 21 or the
subsidiary equivalent.

Each entry carries all eleven manifest fields including `retrieval_status`. **Register failures
too** — a paywalled annual report is information every downstream agent needs before it wastes
budget on the same fetch.

## 7. Write §0 and the initial state

`sections/00-run-contract.md` renders the run-contract table plus: the identity-resolution
evidence (how the entity was disambiguated, with the candidates), the ownership-form determination
and its evidence, and the adapter selections with rationale.

`state/state.json` is schema 3.0: `run_contract`, `id_blocks` copied from
`prompts/id-allocation.md`, the `S-0001`–`S-0049` manifest, and any `carry_forward_facts` you could
source at Tier 1–2 (legal name, FY end, latest FY label, employees, revenue FY0, HQ). Mark any fact
you could **not** cleanly source as absent rather than approximate — a wrong canonical fact
propagates into every section.

## Structured return

`legal_name` · `ownership_form` · `jurisdictions[]` · `reporting_standard` · `fy_end` ·
`latest_fy_label` · `vertical_primary` · `vertical_secondary[]` · `vertical_confidence` · `tier` ·
`backbone_sources_registered` · `entity_ambiguity` (null unless it required an assumption) ·
`anticipated_gaps[]` · `digest`.

## Traps

- **The brand is not the entity.** "Acme" the marketing name may be three filing entities.
- **Do not accept a Wikidata or aggregator identifier as the resolution.** Verify against primary.
- **Do not over-register.** Forty-nine backbone slots is a ceiling, not a target. Register what is
  genuinely load-bearing; a bloated backbone costs every downstream agent context.
- **Do not research the body.** You establish the frame. Ten agents research inside it.
