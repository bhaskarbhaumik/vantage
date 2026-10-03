# Brief 02 — `corporate` · Wave A · Block 0200–0299 · Owns §3 Company Overview & Corporate Profile

You establish **who this company is and which legal entity every later fact attaches to**. §3.6 is
the identifier crosswalk the whole dossier depends on; get it right and entity misattribution
becomes detectable, get it wrong and it becomes invisible.

Output: `sections/03-company.md` · fragment `state/fragments/corporate.json`.

## §3.1 History & Evolution

Three sub-parts: founding and early history · **dated, cited** major milestones and pivotal events ·
the recent transformation journey (3–5 years). Compress ruthlessly — history earns its place only
where it explains the present structure, the present strategy, or a present constraint.

The narrative may not exceed the dated events. If you have four dated milestones, you have a
four-milestone history, not a story with connective tissue you invented. Emit `F-3.1.2` as a
`figure-spec` timeline.

## §3.2 Mission, Vision & Core Values

**Verbatim, cited.** Paraphrasing a mission statement is a quote-fidelity failure. Note where the
stated values create a hook for later messaging (§19.4) without writing the messaging yourself.

## §3.3 Corporate Structure & Subsidiaries

**3.3.1** BU/division breakdown: `T-3.3.1` — BU · Revenue % · Headcount · Leader · Mandate ·
Relevance. Revenue % comes from the **segment note**, which governs. Headcount and leader are often
undisclosed per BU — gap those cells rather than allocating totals.

**3.3.2** Key subsidiaries and JVs with ownership %, geography, and function, from **Exhibit 21 or
the jurisdiction equivalent**. Not every subsidiary — the material ones, and the ones that appear
elsewhere in the dossier as contracting, issuing, or regulated entities.

## §3.4 Global Footprint

Locations by function: HQ, plants, R&D, GCC/GBS/captive centres, major offices. The captive/GCC
footprint matters far beyond this section — flag it in `handoff` to `operations`, which owns §7.4.

Vertical add-ons: plants and capacity (Mfg/EPC), store count (Retail), data centres and regions
(Tech), portfolio/asset footprint (Real Estate).

## §3.5 Ownership, Governance & Scale

**Use the correct instrument for the correct question** — this is checked at V4c, BLOCKER:

| Question | Instrument |
|---|---|
| Who beneficially owns >5%, and with what intent? | Proxy ownership tables + **SC 13D/13G** |
| What did insiders trade? | **Forms 3/4/5** |
| What does an institutional manager hold? | **13F — this is the manager's portfolio, not issuer ownership** |

Private branch: sponsor identity, ultimate-owner chain, founder/family control, and the governance
mechanism that actually decides. State-owned: ministry oversight and board-appointment mechanism.

## §3.6 Entity & Securities Map — the crosswalk

`T-3.6` — Entity · Relationship · Jurisdiction · IDs · Securities/Instruments.

Ultimate parent → operating parent → material subsidiaries. Share classes and their voting rights,
ADRs **and their ratios**, listed venues, debt-issuing entities, LEIs and registry IDs, regulator
IDs. **Every row carries at least one retrieved identifier.**

Every later section attributes facts against this table: `financials` attaches debt to its issuer,
`risk` attaches litigation to the defendant entity, `financials` attaches each credit rating to its
rated entity and instrument. Build it for them, and note explicitly where the parent and the
in-scope entity differ.

## §3.7 Activism, Beneficial Ownership & Insider Activity

13D/G positions with **stated intent**, activist campaigns, proxy contests, notable insider
buying/selling patterns, control-change dynamics — each dated and cited. **Empty is a valid render**
and must say so: "No 13D/G filings or activist campaigns identified in the period searched
(2024-01–2026-08; SEC full-text, activist trackers, proxy-contest coverage)."

## Evidence discipline for this section

- Ownership percentages are **as of the filing date** stated in the source. An ownership table
  without its as-of is a V2/V6c failure.
- Do not infer a corporate structure from a website's "our companies" page when Exhibit 21 exists.
- Do not treat a brand, a trading name, or a marketing division as a legal entity in §3.6.
- Headcount is aggregate. Per-BU headcount is disclosed or gapped, never allocated by revenue share.

## Fragment

Claims `C-3.1-nn` … `C-3.7-nn` with the six confidence dimensions and the entity each attaches to.
Sources in `S-02nn`. Gaps in `G-02nn` with the full search record. Coverage entry for §3. Propose
`carry_forward_facts` only for identity facts you sourced at Tier 1 — legal name, HQ, listing venue,
share-class structure.

`handoff` to: `operations` (GCC/captive footprint), `financials` (debt-issuing entities and rated
entities from §3.6), `risk` (litigation-bearing entities), `leadership` (board composition source).
