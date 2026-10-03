# Brief — `financials` (block 3)

**Stage** 1 · **Owns** §4.1–4.5 · **Block** `300`–`399` · **Envelope** ~2,600 w
**Output** `<RUN_DIR>/sections/04-financials.md` · **Fragment** `financials.json`

Read `_common.md` first. **Tier 2 — write nothing about the pursuing organization.**

## Mission

Answer one question the rest of the dossier depends on: **can this client fund transformation, and
under what constraints?** Everything else in §4 supports that.

You are the agent most exposed to QA F2 (precision and reconciliation). Every figure carries
period, currency, units, source, and basis. Every derived figure shows its arithmetic.

## §4.1 Revenue Architecture — ~600 w · bar `T1×1`

Revenue streams and what actually drives each · segment and geographic mix with a 3-year trend ·
pricing model (transactional / subscription / contract / regulated tariff / consumption) and any
disclosed shift · channel mix economics · customer concentration where disclosed.

Segment revenues must reconcile to total; note reconciling items. Where §2.2 flagged a
resegmentation, either restate consistently or label the break — never trend across it silently.
Do not duplicate §3.6's demand analysis; this is monetisation mechanics.

**`+v2.2` Cost structure & profit pools** — the top cost drivers as a share of revenue (COGS,
SG&A, R&D where reported), the fixed/variable split where evidenced, and which lines or segments
carry the highest margin (the profit pools). Use the income statement and segment operating-margin
disclosure; where segment profitability is not disclosed, say so — this is exactly where the BCG
portfolio waiver applies (F5f). This is the section §11 mines for efficiency opportunities, so tie
each cost driver to whether it is structurally addressable, neutrally stated.

## §4.2 Financial Performance & Health — ~700 w · bar `T1×2` (two periods)

3–5 year trend: revenue, gross margin, operating margin, net income, FCF · leverage
(net debt / EBITDA, calculated and shown) · liquidity (cash, undrawn facilities, maturity wall) ·
working-capital direction · **the inflection points and what caused them**.

The inflection points are the intelligence. A table of five years with no explanation of why FY24
margin fell 300bps is data, not analysis.

**Private variant:** statutory-equivalent filings where they exist; otherwise `[DATA GAP]` with a
resolution path. Never synthesise a P&L from press coverage. Never estimate a private company's
margin from public peers and present it as the client's.

## §4.3 Capital Allocation & Investment Capacity — ~400 w · **Pub only** · bar `T1×1` cash-flow stmt

CapEx, R&D, M&A spend, dividends, buybacks — each against FCF, with the arithmetic shown ·
stated capital-allocation policy and priority order · **discretionary capacity**: what is left
after committed capital and shareholder returns.

Discretionary capacity is the number that matters for Model 1 dimension 1. Show how you derived it.

**`V-ENR` note:** for rate-regulated utilities, capex is regulator-approved, so "investment
capacity" means approved-plan and rate-base headroom, not FCF. Apply the substitution and record it.

## §4.4 Technology & Transformation Spend Signals — ~400 w · bar **none** (gap-tolerant by design)

The section most likely to be fabricated in any AID. It is explicitly gap-tolerant.

Acceptable, in order: a disclosed IT/digital spend figure · a disclosed programme budget from
§5.2 · a benchmark `[ESTIMATE]` stating the benchmark source, the method, the key assumption, and
a **range** · `[DATA GAP]` with `G-3nn`.

Not acceptable: a point estimate · "typically 3–5% of revenue for this sector" applied without a
retrieved benchmark source · any figure without a stated method.

**`V-TMT` note:** for technology and telecom clients, IT spend is a meaningless proxy — substitute
R&D and network capex, and say you did.

## §4.5 Valuation & Investor Expectations — ~400 w · **Pub only** · bar `T3×1` retrieved market data

Multiples vs. the §3.3 peer set · analyst consensus **direction** (not price targets you cannot
retrieve) · rating-agency actions with dates · activist presence · the gap between guidance and
consensus where evidenced.

The value here is *pressure on management*, not the numbers. A company trading at a discount with
an activist on the register behaves differently, and that is the finding.
Never invent an analyst opinion or a price target. If you cannot retrieve consensus, gap it.

## Scoring duty

None directly. Your claims feed Model 1 dim 1 (financial capacity) and Model 7 dim 1 (client
stability). Tag those claims `materiality: high` so the scoring agents find them.

## Fragment duties

- `canonical_facts_proposed`: revenue, EBITDA, operating margin, FCF, net debt, leverage, cash —
  each with period, basis, source, confidence.
- `handoff` to `opportunity`: disclosed programme budgets and discretionary capacity.
- `handoff` to `risk-reg`: covenant language, going-concern language, rating actions.
- Contradictions between guidance and filing are `X-3nn` with the recent-primary rule applied.

## Traps

- Non-GAAP vs. GAAP: label which you are using, every time. Companies lead with non-GAAP; the
  filing carries both. Mixing them across a trend table is a silent, serious error.
- Currency: state reporting currency and note constant-currency figures where the company does.
- **Never average conflicting figures.** Two sources disagreeing is `X-3nn` plus the recent-primary
  rule, surfaced in §0.4.
- Restatements break trends. Check for them; say so when you find one.
- Resist the pull toward a full financial-analysis essay. §4 answers "can they fund it, and what
  constrains them" — everything beyond that is envelope you owe §4.4 and §4.5.
