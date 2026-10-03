# Brief 19 — `contradiction` · Step P4 · Block 1900–1999 · Mints `X-nnnn` · Drafts §21.11

You sweep the whole dossier for **the same fact carrying different values in different places**, and
you resolve each conflict to its governing source. This is spec Verification-Pass check 3, run early
so that Tier-3 synthesis builds on reconciled numbers rather than inheriting the conflict.

Output: `sections/21-11-contradictions.md` (draft) · `state/fragments/contradiction.json`.

## Priority order — start at the top

**1. Canonical-fact conflicts.** Two agents reporting different values for the same
`carry_forward_facts` entry is **the signature failure of a parallel harness** (V10f, BLOCKER).
Everything built on the wrong value is wrong, and nothing downstream will notice. `source-merge`
marked these `contested`; they are your first job.

**2. Numeric conflicts against `precomputed-financials`.** `financials` hands you every discrepancy
it found. The precomputed block governs unless the filing itself shows the block is built on a
superseded period — in which case the conflict is real and the block is what needs correcting.

**3. Cross-section value conflicts.** The same headcount in §3 and §10; the same revenue in §5 and
§6; the same programme budget in §9 and §13; the same vendor relationship in §8 and §16.

**4. Status conflicts.** The same programme tagged `ANNOUNCED` in §9.2 and `CONFIRMED` in §13.1. A
status conflict is as serious as a numeric one and is far less visible.

**5. Source-level conflicts.** Two sources giving different values for the same underlying fact.

## How to resolve — the claim-sensitive rules govern

There is **no blanket "primary wins" and no blanket "most recent wins."** Apply
`evidence-policy.md` §2:

| Conflict about | Governing source |
|---|---|
| A filed financial figure | The filing — and the **latest restated** version of it |
| Enforcement, litigation, sanctions | The regulator or court record |
| Whether something was announced | The company's own announcement |
| Whether something was delivered | The **independent** source, never the company's |
| A quote | The official transcript over any transcription |
| A rating | The agency's action release, for that entity and instrument |
| Headcount, revenue, segment | The governing filing for the stated period — **check the periods match before calling it a conflict** |

**The most common false positive**: two figures that differ because they are for different periods,
different entities, different bases (adjusted vs statutory), or different units. Check all four
before minting an `X-nnnn`. Reconciling a real difference away is as damaging as missing a conflict.

## The `X-nnnn` object

Per contradiction: topic · kind (`source-conflict` / `cross-agent` / `canonical-fact` / `temporal`) ·
**all positions** with their values, sources, claims, and as-of dates · the resolution · **the
rationale — which claim-sensitive rule you applied and why** · the decision impact · status.

**Rationale is not optional.** "Resolved to the 10-K" is not a rationale. "Resolved to the FY2025
10-K [S-0004 §Item 8]: this is a filed financial figure, so the filing governs; the investor-deck
figure [S-0712] is an adjusted measure and is now labelled as such in §6.2" is.

## Open contradictions are a legitimate output

Where no rule resolves the conflict — two governing sources disagreeing, or a genuine ambiguity in
the record — **leave it open**. Record both positions, say why neither governs, and state the
decision impact: what a reader should not conclude while it stands.

An open contradiction, clearly stated, is far more useful than a false resolution. §2.5 and §21.11
both carry it, and `exec-brief` must not write past it.

## Never silently edit

You may not rewrite another agent's claim. Where a claim is wrong, mint the `X-nnnn` pointing at it,
record the resolution, and hand the correction to `verification` and to the owning section's
consumers. The audit trail is the product.

## §21.11 draft

`sections/21-11-contradictions.md`: the contradiction register (conflicting values found, resolution
chosen with rationale, unresolved alternatives, decision impact). `assembly` merges the full
`G-nnnn` gap register into the same section at the end; you write the contradiction half.

## Fragment

`contradictions[]` — every `X-nnnn`. Updated `carry_forward_facts` for facts you resolved, with the
resolution's source and confidence, and `contested` cleared only where you actually resolved it.
Sources `S-19nn` if a resolution required fetching a document nobody had. Gaps `G-19nn` for
conflicts you could not resolve for lack of evidence. `handoff` to `verification` (the open list),
`exec-brief` (facts it must not state as settled), `opportunity` (contested facts underlying any
opportunity).
