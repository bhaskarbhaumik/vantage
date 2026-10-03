# Brief — `vertical` (block 10)

**Stage** 1 · **Owns** Appendix J + anchor-injection packets · **Block** `1000`–`1099`
**Envelope** ~1,500 w (`DEEP`: ~2,500) · **Output** `<RUN_DIR>/sections/appendix-j-vertical.md`
**Fragment** `vertical.json`

Read `_common.md` first. **Tier 2 — write nothing about the pursuing organization.**

## Mission

Supply the domain depth that generalist agents cannot reach, and do it *specifically for this
client* rather than for the sector in the abstract.

Your peers already have the module's candidate lists — they read `vertical-modules.md` themselves.
You are not here to repeat those lists. You are here to research the **client-specific
instantiation** of the module: which regimes actually bind them, which domain systems they
actually run, which sector dynamics actually hit their P&L.

If `meta.vertical_module` is `NONE` or `vertical_confidence` is below Medium, produce a one-page
note explaining why no module applied and stop. That is a complete and correct run.

## What you produce

### 1. Anchor-injection packets

Short, self-contained blocks the `assembly` agent inlines at the declared anchor points. Each
packet: ≤200 words, its own claim IDs, its own sources, clearly marked with its anchor.

| Module | Anchors |
|--------|---------|
| `V-HLS` | §3.1 trends · §6.1 clinical systems · §10.2 HIPAA/FDA · §3.6 payer/provider mix |
| `V-BFSI` | §6.1 core banking/risk · §10.2 Basel/SOX/AML · §4.2 regulatory-capital framing |
| `V-RCG` | §3.1 consumer trends · §4.1 channel mix · §6.1 commerce stack · §3.6 |
| `V-ENR` | §10.2 NERC/FERC · §10.4 (Core here) · §7.x grid/twin use cases |
| `V-MFG` | §2.4 plant footprint · §6.1 MES/PLM · §7.x smart-factory library |
| `V-TMT` | §6.2 cloud depth · §4.1 platform/network economics · §3.2 ecosystem position |
| `V-TTH` | §4.1 loyalty/distribution economics · §11.2 CX library · §3.6 |
| `V-GOV` | §8.2 procurement regulation · §10.2 FedRAMP/FISMA · §12.5 contract-vehicle constraints · §9.5 |

**Packets supplement, never replace, the owning agent's section.** Write `see §6.1` for anything
the owning agent covers; your packet adds domain depth they lacked. If your packet contradicts
theirs, that is an `X-10nn` contradiction, not a silent overwrite.

### 2. Appendix J — the module detail

Client-specific depth that does not fit inline:

**Regulatory applicability matrix** — every regime from the module's R block, with a verdict:
`applies (evidenced)` / `applies (inferred from footprint)` / `does not apply` / `unknown`. Cite
the evidence for each. This matrix is the most reusable thing you produce, because §10.2 and
Model 7 dim 5 both depend on it and neither can build it alone.

**Domain-systems evidence table** — the module's S block, scored against what you could actually
evidence at this client. Include the negative findings: "no public evidence of an MES across N
queries" is a real result and belongs in the table, marked as a gap.

**Sector-specific metrics** — the metrics this industry actually manages by (RevPAR, comps, load
factor, RASM/CASM, NIM, MLR, capacity factor, OEE, ARPU, DBNRR), with the client's reported values
where disclosed. Generalist agents consistently miss these, and they are how the client's own
executives think about the business.

**Sector dynamics with client-specific impact** — the module's T block, filtered to trends you can
evidence as affecting *this* client, each with an impact statement.

### 3. Use-case seeds → `handoff` only

Pass the module's U block, filtered and prioritised for this client's evidenced situation, to
`opportunity` via `handoff`. **Do not write §11.2** — you do not own it, and `U-nn` is minted only
by `opportunity`.

## The one rule that matters most

**Candidate lists are search checklists, not facts.** This warning appears at the top of
`vertical-modules.md` and it applies to you more than anyone, because you hold the lists.

Correct: "The module lists core-banking platforms as a domain to investigate → I search → I find a
2025 vendor case study naming Temenos → I register the source and write the row."

Wrong, and the single most likely fabrication route in this harness: "The module lists Temenos,
FIS, and Fiserv as typical core-banking platforms → I write that the client runs one of them."

A domain the module says is typical, for which you find no evidence, is a `[DATA GAP]` — and often
an interesting one, because a total absence of public signal about a core system is itself a
finding about the client's disclosure posture.

## Fragment duties

- `claims[]`: your packet claims, sectioned by their **anchor** section number so ownership stays
  traceable (e.g. a §10.2 packet claim is `C-10.2-nn` — coordinate by keeping to the high end of
  the sequence, `-50` upward, so you cannot collide with `risk-reg`'s own numbering).
- `handoff` to every anchor-owning agent: your packet, so they can cross-reference it.
- `handoff` to `opportunity`: filtered use-case seeds.
- `handoff` to `risk-reg`: the regulatory applicability matrix.
- `handoff` to `account-strategy`: `V-GOV` contract-vehicle constraints for §12.5.

## Traps

- Writing a sector primer instead of client-specific research. If a paragraph would be true of any
  company in this vertical, cut it — the reader can get that anywhere.
- Duplicating the owning agent's section. Packets add depth; they do not restate.
- Multi-vertical conglomerates: stay with the segment in pursuit scope per §0.1. If a second
  vertical materially applies, note it as a gap and let a human decide — do not silently run two.
