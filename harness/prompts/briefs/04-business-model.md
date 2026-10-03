# Brief 04 — `business-model` · Wave A · Block 0400–0499 · Owns §5 Business Model & Revenue Architecture

You establish **how this company makes money** — the structure everything downstream reasons about.
§5.2 and §5.6 feed §6, §7, §11, §12, and §18. Two Wave-B agents (`operations`, `customers`) block
on your output, so write the segment and channel structure early and clearly.

Output: `sections/05-business-model.md` · fragment `state/fragments/business-model.json`.

## §5.1 Business Model Canvas

Nine blocks, evidence-grounded: customer segments · value propositions · channels · customer
relationships · revenue streams · key resources · key activities · key partnerships · cost
structure. `T-5.1` + `F-5.1`.

Blocks you cannot evidence are **gapped, not guessed**. A canvas with nine confident boxes on a
target that discloses four of them is the classic framework-driven fabrication.

## §5.2 Revenue Streams & Segmentation

**5.2.1 By segment, 3 fiscal years.** The **segment note governs** — not the MD&A narrative, not
the investor deck's "adjusted" view. The table **must foot to the reported total** (V2c); where it
does not, there is an "other/corporate/eliminations" line and you show it.

**5.2.2 By geography, 3 fiscal years.** Same rule. Note where geographic reporting differs from
operational reality (a "Europe" line that includes the Middle East, for example).

**5.2.3 By product/service line.** Growth engines versus decliners. Where the company does not
report at this granularity, say so — do not construct product lines from marketing pages.

Charts `C-5.2.1`, `C-5.2.2`. Reconcile every figure to `precomputed-financials` where attached.

## §5.3 Customer Segments & Value Proposition

Who they sell to and **why those buyers buy**. Segment economics where disclosed. `customers` owns
§12.1 and will go deeper on demographics; you own the structural view.

## §5.4 Pricing Model & Monetization

Disclosed pricing architecture — subscription, usage, transaction, licence, mixed — and the
monetization levers management talks about. **Pricing that is not disclosed is gapped, never
inferred from public list prices**, which are rarely what enterprise customers pay.

## §5.5 Channel & Distribution Model

Routes to market, direct-versus-partner mix, channel economics where disclosed.

## §5.6 Cost Structure & Profit Pools

Top cost drivers, fixed/variable split, and the highest-margin lines. Source from the income
statement and segment notes; `T1×1` or `[DATA UNAVAILABLE]`. Most companies do not disclose a
fixed/variable split — the honest output names the cost lines they do disclose and marks the split
`INFERRED` with the reasoning, or gaps it.

This subsection is the anchor for §7.5 pain points and §18.3 functional opportunities. Flag the two
or three cost pools that dominate.

## §5.7 Customer Concentration & Key Accounts

**Filing disclosure first** — the 10% customer disclosure, or the jurisdiction equivalent. Named
customers only where the company or the customer named them. **Empty is a valid render** and says
so: concentration below the disclosure threshold is a finding.

## §5.8 Supply Chain & Procurement

Supplier structure, sourcing footprint, procurement posture, single-source exposure where
disclosed. Named suppliers **only where evidenced** — a trade-data inference is
`OBSERVED-SIGNAL`, never a supplier relationship.

## §5.9 Unit Economics & Operating KPI Dashboard

The **6–12 KPIs this business actually runs on** — the ones management reports and is measured
against, not a generic set. Two-to-three-year trend plus peer context where §11.0 exists.

A KPI without a disclosed definition is not a KPI: same-store sales, ARR, active users, and
utilisation are all defined differently by different companies, and comparing across definitions is
a V2 failure. State each definition as the company states it.

Vertical KPI add-ons are in the module's **E** block: backlog and book-to-bill (EPC, A&D), AUM and
NIM (financial services), RPK and load factor (airlines), FFO and occupancy (real estate),
utilisation and realisation (professional services), same-store sales (retail).

## Traps

- **Adjusted is not reported.** Label every column. Mixing them unlabelled is V2e.
- **A segment table that does not foot is wrong**, not "approximately right".
- **Do not build a canvas block from a competitor's model.** This is the target's canvas.
- **Do not infer margin by product line** from a company that reports only segment margin.

## Fragment

Claims `C-5.1-nn` … `C-5.9-nn`. Sources `S-04nn`. Gaps `G-04nn`. Coverage entry for §5. Charts
`C-5.2.1`, `C-5.2.2`; figure `F-5.1`. Propose `carry_forward_facts` for segment structure and
revenue mix. `handoff` to `operations` (cost pools and supply-chain structure), `customers`
(segment definitions), `financials` (any figure that disagrees with `precomputed-financials`).
