# Tooling Map v3.0.0 — where each section's evidence actually lives

> Condensed from `aid-tools-20260829.md` (AID Deep-Research Tooling Catalog v2.0.0, last verified
> 2026-08-29) into the form an agent needs at runtime: **for my section, what do I search, in what
> order, and what is that source class worth?**
>
> This file does not grant access. A tool listed here may or may not be wired into the run — the
> harness's own tools are `web_search`, `sec_edgar`, `market_data`, `read_file`, `list_dir`, and
> whichever MCP servers the environment loaded. **Runtime tool availability is run metadata, not
> catalog fact**: record what you actually used in your coverage record, and never cite a database
> by name unless you actually opened it.

## Three rules that override everything below

1. **Evidence strength.** Rows marked *signal* — job postings, review presence, certificates, DNS,
   SDKs, app data — produce `OBSERVED-SIGNAL` claims requiring corroboration. **They are never
   proof of an installed stack or of company behaviour on their own.**
2. **Compliance.** A commercial scraper or actor existing does not make its use licensed or
   ToS-compliant. **Vendor availability ≠ permission.** No paywall circumvention, no bulk scraping
   of ToS-restricted sites, no scanning or probing.
3. **Licensing.** Licensed analyst content, expert-network transcripts, and subscription datasets
   are **cited by name, never reproduced at length** in a generated dossier.

---

## Coverage map — Vantage section → primary tooling

| Vantage area | First choice | Backup / enrichment |
|---|---|---|
| Entity resolution (§0, §3.6) | Adapter registry lookup (EDGAR CIK, Companies House, …), **GLEIF LEI**, OpenFIGI, LSEG PermID | OpenCorporates, Wikidata (**verify against primary**) |
| Global filings backbone (§0 → all) | The §0 jurisdiction adapter's own system — see `jurisdiction-adapters.md` | `filings.xbrl.org` (ESEF/UKSEF), sec-api |
| Financials (§6, §21.3) | EDGAR / ESEF **XBRL** → the `precomputed-financials` block; `edgartools` | FMP, Alpha Vantage; `yfinance` **triage only** (unofficial wrapper) |
| Ownership & activism (§3.5–3.7) | Proxy tables, **13D/G** (beneficial), **Forms 3/4/5** (insider), OpenOwnership | BoardEx, Orbis (private) |
| Strategy & priorities (§9, §13.4) | IR decks + **official** transcripts/webcasts | Third-party transcripts (verify material quotes), Quartr |
| Operations & quality (§7) | Filings MD&A, CFPB complaint database, public status-page histories, recalls (openFDA), OSHA | ACSI, review sites (**weak**) |
| Tech stack (§8.1) | ATS feeds (**classified per the mention rule**), BuiltWith/Wappalyzer, GitHub | HG Insights, G2 (**weak**), crt.sh (**weak**) |
| AI & agentic posture (§8.3, §15) | Job postings, arXiv/OpenAlex, keynotes, engineering blogs | Patents, press releases (ANNOUNCED only) |
| Leadership & org (§10) | Proxy, IR bios, compliant workforce vendors | BoardEx, podcasts; **LinkedIn only via partner API or licensed vendor** |
| Peers (§11) | The §11.0 peer set's own filings | Exa find-similar, Owler (**estimates = LOW**) |
| Customers & brand (§12) | ACSI and standardized benchmarks, filings customer disclosure | GDELT sentiment (**method stated**), Meta Ad Library, review sites (**weak**) |
| Signals (§13) | ATS/careers JSON, PR wires, earnings calls, procurement portals | Adzuna, GDELT, Event Registry |
| Risk, legal, sanctions (§14) | Item 1A/1C equivalents, CourtListener/RECAP, **OFAC/EU/UK/UN lists**, SEC/DOJ/FTC/CFPB enforcement feeds | Violation Tracker, OpenSanctions, Senate LDA / FEC / EU Transparency Register (§14.9) |
| Vendors (§16) | Vendor PRs, joint case studies, ATS feeds | HG Insights, technographics (**modeled, not observed**) |
| ESG (§17) | Sustainability report, **SBTi database**, CDP | Headline ESG scores, EPA (ECHO/FLIGHT/TRI), Climate TRACE |
| Procurement (§13.7, §18.6) | USAspending, TED (EU), UK Contracts Finder, SAM.gov | GovTribe, CanadaBuys/AusTender |
| Patents & IP (§21.6) | PatentsView, EPO OPS, Google Patents | Lens.org, USPTO TSDR, WIPO/EUIPO trademarks |
| Digital presence (§21.7) | Cloudflare Radar, Tranco | Similarweb / Semrush (**licensed — check quoting terms**) |
| Preservation (§21.1) | **Wayback Save Page Now for every load-bearing URL** | Local response cache keyed by source ID |
| Macro (§4.7) | FRED, World Bank, IMF, OECD, Eurostat, BLS/Census/BEA | Nasdaq Data Link |

## Source-class reliability tiers

The `tier` field on every Source Manifest entry.

| Tier | Classes |
|---|---|
| **1** | Regulator filings; official transcripts and webcasts; court and enforcement records; official sanctions lists; XBRL facts |
| **2** | Corporate/IR/newsroom/sustainability pages; official company announcements; standards-body registers (SBTi, accreditors) |
| **3** | Named financial data services; tier-1 analyst research; standardized benchmarks (ACSI); patent and trademark registers |
| **4** | Tier-1 business media; trade press |
| **5** | Jobs boards; review and culture sites; technographic inference; DNS/certificate/SDK observation; social — **weak signals only** |

A tier-5 source may support an `OBSERVED-SIGNAL` claim at `LOW` confidence. It may never be the
sole basis of a `CONFIRMED` claim, and it may never anchor a recommendation alone.

## Deterministic math lives outside the model

`backbone` produces the `precomputed-financials` block from XBRL (EDGAR company-facts / frames, or
ESEF via `filings.xbrl.org`) **before** §6 is written. The model reconciles against it and never
re-derives it (V2a). Where XBRL is unavailable — most private targets, several jurisdictions —
`backbone` says so explicitly and §6 recomputes from the stated filing figures with the inputs
shown.

Chart and figure blocks are validated against JSON Schema **by the renderer after the run**, not by
the writing agent. Invalid blocks are rejected and regenerated.

## Known catalog rot (verified 2026-08-29)

Re-verify quarterly. These four are the ones most likely to produce a wrong answer today:

| Entry | Status |
|---|---|
| Google Programmable Search (CSE) JSON API | **Deprecated** — closed to new customers, shutdown 2027-01-01. Plan a replacement. |
| Polygon.io | **Rebranded to Massive.com** — migrate to `api.massive.com` |
| Reddit Data API | **Commercial use requires a separate Reddit agreement** — not ordinary freemium |
| YouTube Data API | **Not a transcript API** — metadata and search only; caption tracks need OAuth. For quotes use official IR transcripts |

Also current-name-only: LSEG Data & Analytics (ex-Refinitiv) · Quantexa News API (ex-AYLIEN) ·
HubSpot Breeze Intelligence (ex-Clearbit) · Sensor Tower (data.ai retired).

## Unofficial sources — never a sole source for a material claim

`yfinance` · Google News RSS · `pytrends` · DuckDuckGo · `google-play-scraper` · ImportYeti ·
community EDGAR/yfinance MCP servers. Useful for triage and lead generation. A material claim built
on one of these alone is a V1/V3 failure.

## The free-tier reality

EDGAR/ESEF + XBRL + Docling + GDELT + ATS feeds + PatentsView + OFAC/EU lists + USAspending/TED +
FRED + Wayback gives a **MEDIUM-to-HIGH-confidence dossier on most public companies at zero
marginal cost**. Primary sources plus IR plus official transcripts alone deliver roughly 60% of the
dossier at HIGH confidence. Reach for a paid source when a *specific recurring gap* justifies it,
not up front — and record in §21.12 when a gap exists **because** a source was unavailable rather
than because the evidence does not exist. That distinction is what tells the account team whether
to buy access or accept the unknown.
