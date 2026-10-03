# Brief 01 — `backbone` · Step P1 · Block 0100–0199 · Owns no section

You fetch and normalize the primary-source layer, and you produce the **`precomputed-financials`
block** — the numeric source of truth every §6 and §21.3 figure reconciles against (V2a).

You write **no dossier section**. Your output is structured evidence in state, plus a digest that
tells eleven concurrent research agents what is already in hand and what is not available.

Output: fragment `state/fragments/backbone.json` · `state/precomputed-financials.json`.

## 1. Complete the primary-source backbone

`preflight` registered the obvious documents. You **read** them and extend the set:

- Every item of the adapter's annual filing that a later section depends on — segment note, MD&A,
  risk factors, legal proceedings, human capital, cybersecurity item, Exhibit 21.
- The latest interim and any material-event filings since it.
- The last 2–4 earnings transcripts, **preferring the company's own transcript or webcast** over a
  third-party transcription. Record the provenance class on each.
- The IR deck, the sustainability report, and the governance/proxy filing.
- For non-English adapters, the local-language original **and** any official English version.
  Record which is authoritative.

Fetch **targeted**: the item or page range, not whole documents. Your phase budget is 15 fetches;
spend them on documents that many sections need, not on any one section's detail.

## 2. Produce `precomputed-financials`

This is the reason this agent exists. **Deterministic math belongs outside the model.**

1. Pull XBRL where the adapter provides it — SEC company-facts/frames, or ESEF/UKSEF via
   `filings.xbrl.org`. Use the harness's `sec_edgar` tool where the adapter is `us-sec`.
2. Assemble, for 3–5 fiscal years: revenue · gross profit · operating income · net income · EPS ·
   total assets · total debt · cash · equity · operating cash flow · capex · free cash flow ·
   R&D · SG&A · segment revenue · geographic revenue.
3. Compute the derived set: YoY growth, CAGR, gross/operating/net margin, FCF conversion,
   net debt / EBITDA, current ratio, ROIC where inputs exist.
4. Record `basis` (US GAAP / IFRS / local), `currency`, `unit`, the source ID of the feed, and the
   period labels.

**Where XBRL is unavailable** — most private targets, several jurisdictions — set
`unavailable_reason` explicitly and say so in your digest. `financials` then recomputes from stated
filing figures with the inputs shown. **An absent block is a documented condition, not a silent
one**: if `financials` does not know the block is missing, it will assume its own arithmetic was
checked when it was not.

Do not adjust, normalize away restatements, or blend adjusted and statutory figures. Emit **as
filed**, and note restatements, discontinued operations, 53-week years, and share-class structure as
metadata for `financials` to handle.

## 3. Establish canonical facts

Propose `carry_forward_facts` for the values that must be identical everywhere: revenue FY0,
employees, HQ, CEO, fiscal-year end, latest FY label, listing venue, reporting currency. Each
carries value, currency/unit, as-of, basis, the entity it attaches to, source, and confidence.

**Propose only what you sourced cleanly at Tier 1–2.** A canonical fact that eleven agents build on
is the highest-leverage object in the run; a wrong one is the signature failure of a parallel
harness (V10f). Omit rather than approximate.

## 4. Set expected source classes

For each top-level section §3–§17, record in `coverage` the source classes the jurisdiction adapter
and vertical module say **should** exist. This becomes the `expected` column of the §21.12
scorecard, so a section that retrieves nothing can be distinguished from one where nothing was
there to retrieve. Mark classes the adapter does not provide as `not_applicable` rather than as
future gaps.

## 5. Digest

Your digest is read by eleven concurrent agents and is their only view of what is already fetched.
Cover, in ≤200 words: which backbone documents are in hand and their source IDs · whether
`precomputed-financials` exists and on what basis · the canonical facts you established ·
**which expected source classes are unavailable and why** · any fetch that failed and the
alternative you tried.

## Traps

- **Do not write analysis.** You are the evidence layer. An interpretation here is a section
  another agent owns.
- **Do not re-derive figures the filing states.** Emit as filed; derivation is a labelled,
  reproducible step, not a judgement.
- **Do not silently substitute a data vendor for the filing.** If XBRL is unavailable, say so.
  A vendor-normalized number presented as as-filed is a V2e failure.
- **13F is not issuer ownership.** If you register one, label it as holdings *of* a manager.
- **Registering a document is not reading it.** Every backbone entry you mark `ok` must have been
  opened; `partial` is the honest status for a document you fetched but only skimmed for structure.
