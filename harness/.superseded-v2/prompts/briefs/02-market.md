# Brief — `market` (block 2)

**Stage** 1 · **Owns** §3.1–3.6 · **Block** `200`–`299` · **Envelope** ~2,700 w
**Output** `<RUN_DIR>/sections/03-market.md` · **Fragment** `market.json`

Read `_common.md` first. **Tier 2 — write nothing about the pursuing organization.**

## Mission

Establish the pressures acting on the client from outside: the market they compete in, who they
compete against, how they are doing relative to peers, and who their customers are. §3.6 is new in
v2.1 and exists because opportunity framing in §11 needs the *client's customers*, not just the
client.

## §3.1 Industry Structure & Dynamics — ~800 w · bar `any×2`, ≥1 `T3` for sizing

Market definition — state which market you are sizing and why that boundary (this determines
whether every subsequent number is comparable) · size and growth with a **retrieved** source and
its own definition · structure (fragmented / consolidating / oligopoly) with evidence ·
5–7 trends, each with a **client-specific** impact statement.

Start from the vertical module's **T** block as a search checklist. Include a trend only when you
can evidence it *for this client's market*. A trend with no client-specific impact statement is
filler — cut it.

Market-size figures are the most-fabricated numbers in any dossier. Either cite a retrieved source
with its definition, or write `[DATA GAP]`. Never a round number with no provenance.

**`+v2.2` Value-chain position** — one short paragraph: where the client sits in the industry
value chain (upstream / midstream / downstream / platform / aggregator), what it does and does not
control, and where digital/AI value concentrates in that chain. This is the frame §11 uses to
locate opportunities — keep it structural, not a process map (§6.7 owns process detail).

**`+v2.2` Macro & geopolitical demand drivers** — the 2–4 macro forces acting on *this market*
(rates, input-cost cycles, trade/tariff policy, FX exposure, regional concentration) and their
direction. Market-level only; enterprise geopolitical *risk* is §10.1, and forward stress scenarios
are §10.7 — cross-reference, do not duplicate.

## §3.2 Competitive Position — ~600 w · bar ≥3 named competitors, each `any×1`

Named competitor set with the basis for inclusion · relative position on the dimensions that
matter in this industry · share and share *direction* where sourced, `[ESTIMATE]` with method
otherwise · where the client demonstrably wins and loses.

Competitor set is a judgment — state yours and its basis. The client's own 10-K competition
section is T1 evidence of who *they* think they compete with, which is itself a finding when it
diverges from the market view.

## §3.3 Peer Benchmarking — ~400 w · **Pub only** · bar `T1×3` peer filings

3–5 named peers on comparable metrics: revenue growth, operating margin, ROIC, and one
industry-specific metric. Every figure period-labelled and sourced to the **peer's own filing**.

Fiscal years differ between peers. Either align periods and say how, or label the mismatch. Do not
compare a FY-ending-January company to a FY-ending-December one without saying so.
**Private variant:** qualitative positioning only; state the substitution.

## §3.4 Client-Reality SWOT — ~300 w · bar ≥6 claims across §2–3

A 2×2 where **every cell entry carries claim IDs**. Structural and sustainable items only — not a
list of everything true about the company.

This is the *client's* SWOT, not the pursuing organization's view of the account. §12.1 is the the pursuing organization-lens SWOT and belongs
to a different agent. Writing the pursuing organization content here fails QA F7a.

Cross-agent note: §2.x claims are being written concurrently. Use `state.json` canonical facts and
your own §3 research. Where you need a §2 fact you cannot source yourself, write `see §2.2` — do
not invent it and do not block.

## §3.5 Regulatory Context Pointer — 1 line

`Regulatory landscape for this industry is analysed in §10.2.` That is the whole section. It
exists to stop the duplication that made v1.2 self-contradictory.

## §3.6 Client's Customers, Demand & Portfolio — ~550 w · `NEW v2.1` `+v2.2` · bar `T1–2×1`

Who the client sells to, what drives *their* spending, and what the client sells them:

Customer segments as the client defines them · concentration where disclosed (top-10 share,
any >10% customer) · channel mix (direct / distributor / franchise / marketplace / OEM) and how it
is shifting · the demand drivers behind the client's revenue — end-market cyclicality, consumer
behaviour, regulatory-driven demand, replacement cycles · CX or channel programmes the client runs
for its own customers, with evidence.

**`+v2.2` Product & service portfolio** — the principal product/service lines by business unit
with a lifecycle read (Growth / Mature / Declining) where evidenced, and which lines are the stated
growth engines vs. run-off. A compact table is right here. Cross-reference §2.2 (segment map) and
§4.1 (revenue mix) — do not restate their numbers; this is the *what they sell* inventory that the
segment and revenue views quantify.

**`+v2.2` Brand perception & reputation** — brand strength where there is a **retrieved** signal
(Interbrand/BrandZ rank, Glassdoor rating, an award, media-sentiment direction) and any reputation
risk. **Anti-fabrication is acute here:** never invent an NPS, CSAT, or J.D. Power score. A number
you cannot retrieve is `[DATA GAP]`; a company's self-description of its brand is a T2 claim about
*what they say*, not a measurement.

Why this exists: the client's customer-facing programmes and portfolio direction are where services
opportunities concentrate, and a dossier that describes the client without describing their demand
cannot frame §11 credibly. Do **not** duplicate §4.1's revenue mechanics — that is *how they
monetise*; this is *who they serve, why demand moves, and what they sell*.

## Fragment duties

- `canonical_facts_proposed`: named competitor set, market definition used, customer-concentration
  figures if disclosed.
- `handoff` to `ecosystem`: competitors that are also partners or customers.
- `handoff` to `opportunity`: client customer-facing programmes that imply services demand.

## Traps

- Analyst-firm numbers are usually paywalled. A press release *about* a report is a legitimate T3
  source with `access_basis: secondary-summary` — the report itself is not, unless you opened it.
- Do not restate the client's marketing claims about its position as fact. "Leading provider of X"
  from the company website is a T2 claim about *what they say*, not about market share.
- Trends without client impact are the most common padding in this section. Cut them.
