# Vantage Deep-Research Tooling Catalog — Combined (v2)
**Version:** 2.0.0 · **Last verified:** 2026-08-29
**Classification:** Internal account research
**Supersedes:** `vantage-fable-5-tools.md` v1.0.0, incorporating all findings and 50 additions from `codex_review_comments.md` (Codex review, 2026-08-29)
**Companion to:** `vantage-20260829.md` (prompt v3.0.0)

**Legend:** 🟢 Free · 🟡 Freemium · 🔴 Paid · 🏢 Enterprise · 🔑 API key · 📜 ToS/registration limits · ⚖️ Licensing/reuse restrictions — verify before quoting/persisting/redistributing · ⚠️ Unofficial or breakage-prone — never a sole source for a material claim

> **Maintenance schema (review finding 19):** every production integration must record — official docs URL, owner, last-verified date, base URL/version, auth, rate limits, pricing basis, geographic coverage, freshness, licensing/retention/redistribution terms, PII risk, and fallback. This catalog carries the summary columns; the full record belongs in `config/research.yaml` per wrapper.
>
> **Evidence-strength rule (finding 7):** entries marked *signal* (job postings, review presence, certificates, DNS, SDKs) are OBSERVED-SIGNALs requiring corroboration — never proof of installed stack or company behavior on their own.
>
> **Compliance rule (finding 6):** a commercial scraper/actor existing does not make its use licensed or ToS-compliant. Source-specific legal review + documented lawful basis required; vendor availability ≠ permission.

---

## 0. Recommended Core Stack

| Tool | Type | Access | Status | Role |
|---|---|---|---|---|
| Anthropic `web_search_20260209` | Claude server tool | 🔴 ($10/1K searches) | available | Primary in-session search, dynamic filtering |
| Anthropic `web_fetch_20260209` | Claude server tool | 🟢 (token cost) | available | Fetch-before-assert; targeted retrieval with citations |
| `edgartools` (Python) | Library | 🟢 | **installed** (`pyproject.toml`) | SEC EDGAR backbone + XBRL for precomputed financials |
| `yfinance` (Python) | Library | 🟢 📜 ⚠️ | **installed** | Triage/reconciliation only — unofficial Yahoo wrapper; final market/financial claims come from filings or licensed feeds (finding 14) |
| `tavily-python` | API + library | 🟡 🔑 | **installed** | Out-of-session search/extract/crawl |
| Claude Code Workflow (`vantage` engine) | Harness | 🟢 (subscription) | **external** — lives at `~/Developer/vantage`, not this repo (finding 17) | Default multi-agent Vantage runner |
| LangGraph / CrewAI / Google ADK | OSS frameworks | 🟢 | **external** — backends of the vantage engine, not declared in this repo | Alternate orchestration backends |

---

## 1. General Web Search APIs

| Service | Type | Access | What it provides | Status/caveats | Vantage §§ |
|---|---|---|---|---|---|
| Anthropic Web Search | Server tool | 🔴 | In-session search + dynamic filtering + citations | available | All |
| Brave Search API | REST | 🟡 🔑 | Independent index; web+news; generous free tier | available | All |
| Google Programmable Search (CSE) JSON API | REST | 🟡 🔑 | Google index via CSE | ⚠️ **DEPRECATED — closed to new customers; shutdown 2027-01-01** (finding T-1). Existing keys only; plan replacement (Serper/SerpAPI/Vertex AI Search) | — |
| Kagi Search / FastGPT | REST | 🔴 🔑 | Ad-free index, summarizer | available | All |
| SerpAPI | REST (SERP) | 🟡 🔑 | Structured Google/News/Patents/Scholar/Maps SERPs | available | All, §21.6 |
| Serper.dev | REST (SERP) | 🟡 🔑 | Fast cheap Google SERP JSON | available | All |
| Azure AI Grounding with Bing | Agent API | 🔴 🔑 | Bing-backed grounding (Bing v7 successor) | available | All |
| DuckDuckGo | Unofficial | 🟢 📜 ⚠️ | Zero-key quick lookups | triage only | — |

## 2. AI-Native Search & Deep-Research APIs

| Service | Type | Access | What it provides | Status/caveats | Vantage §§ |
|---|---|---|---|---|---|
| Tavily | REST+SDK+MCP | 🟡 🔑 | Search/extract/crawl/map for LLM research | available | All |
| Exa | REST+MCP | 🟡 🔑 | Semantic search, find-similar-companies, contents | available | §4, §11 |
| Perplexity Sonar | REST+MCP | 🔴 🔑 | Grounded answers with citations; deep-research endpoint | available | Triangulation |
| **OpenAI Responses API — web search tool** | REST | 🔴 🔑 | Search-grounded OpenAI responses with citations | split from the old combined row (finding T-3); own request format & pricing | Verification |
| **Gemini API — Grounding with Google Search** | REST | 🔴 🔑 | Google-grounded Gemini responses, grounding metadata | split row (finding T-3); different semantics from OpenAI's tool | Verification |
| Jina AI (Reader/Search) | REST | 🟡 🔑 | URL→markdown; search→markdown | available | Fetch fallback |
| You.com / Linkup | REST | 🟡 🔑 | LLM-tuned web/news search | available | All |

## 3. Web Fetching, Scraping & Crawling

| Service | Type | Access | What it provides | Status/caveats | Vantage §§ |
|---|---|---|---|---|---|
| Anthropic Web Fetch | Server tool | 🟢 | Page/PDF retrieval + citations | available | All |
| Firecrawl | REST+SDK+MCP | 🟡 🔑 | Scrape/crawl/map/extract → markdown/JSON | available | §3, §8, §12 |
| Apify | Platform+API+MCP | 🟡 🔑 ⚖️ | 4,000+ maintained actors | per-source ToS/legal review required — actor availability ≠ permission (finding T-6) | §10.7, §13.3 |
| Bright Data | Platform+API+MCP | 🔴 🔑 ⚖️ | Proxy network, dataset marketplace, SERP APIs | same compliance rule; contractual assurances needed | hard targets |
| ScrapingBee / ScraperAPI / Zyte | REST | 🟡 🔑 ⚖️ | JS-rendered retrieval | same compliance rule | fallback |
| Crawl4AI | OSS | 🟢 | Self-hosted crawler → markdown | robots.txt discipline | batch |
| **Playwright MCP** (Microsoft) | MCP | 🟢 | Browser automation | split row (finding T-12): Microsoft-maintained | IR portals |
| **Puppeteer-based MCPs** | MCP | 🟢 ⚠️ | Browser automation | community-maintained — record repo/maintainer, security-review before use | fallback |
| Diffbot | REST | 🔴 🔑 | ML extraction + org Knowledge Graph | available | §3, §11 |
| Internet Archive / Wayback | REST | 🟢 | Historical snapshots | available | §3.1, §9 |
| Common Crawl | Open dataset | 🟢 | Web-scale corpus | research use | — |

## 4. Document Parsing & OCR *(new category — finding T-20)*

| Service | Type | Access | What it provides | Vantage §§ |
|---|---|---|---|---|
| Docling | OSS | 🟢 | PDF/DOCX/PPTX parsing, tables, reading order → structured output | filings, IR decks |
| Unstructured | OSS + hosted | 🟢/🔴 | Partitioning/extraction from PDF/Office/HTML/email | all fetched docs |
| Apache Tika + Tesseract/OCRmyPDF | OSS | 🟢 | Text/metadata extraction + OCR for scanned filings | older filings, non-US docs |
| Azure Document Intelligence / Google Document AI / AWS Textract | Cloud API | 🔴 🔑 | Managed OCR, layout, financial-table extraction | §21.3 precompute |

## 5. Identifiers & Entity Resolution *(new category — findings T-9, additions 9–13)*

| Service | Type | Access | What it provides | Vantage §§ |
|---|---|---|---|---|
| GLEIF LEI API | REST | 🟢 | LEI records + corporate hierarchy | §0, §3.6 |
| OpenFIGI | REST | 🟢 🔑 | FIGI/ticker/exchange/security mapping | §3.6 |
| LSEG PermID | REST | 🟡 🔑 | Entity/instrument/org identifiers + relationships | §3.6 |
| SEC EDGAR company/CIK lookup | REST | 🟢 📜 | CIK↔ticker↔name resolution | §0 |
| OpenOwnership Register | Open data/API | 🟢 | Beneficial-ownership data (BODS), jurisdiction-dependent | §3.5–3.7 |
| Wikidata | SPARQL | 🟢 ⚠️ | Entity backbone — verify against primary | §0 |
| Moody's Orbis (Bureau van Dijk) | Enterprise | 🏢 | Global private-company financials + ownership trees | private branch |

## 6. Regulatory & Corporate Filings — US

| Service | Type | Access | What it provides | Status/caveats | Vantage §§ |
|---|---|---|---|---|---|
| SEC EDGAR (full-text, submissions, XBRL frames) | REST | 🟢 📜 (UA header) | 10-K/10-Q/8-K/DEF 14A/S-1 + XBRL facts | primary backbone | §3, §5, §6, §10, §14 |
| **SEC 13D/13G feeds** | REST/filings | 🟢 | **Beneficial ownership** + control intent | distinct interpretation (finding T-9) | §3.7 |
| **SEC Forms 3/4/5** | REST/filings | 🟢 | **Insider transactions** | distinct | §3.7 |
| **SEC Form 13F** | REST/filings | 🟢 | Holdings **of institutional managers** — not issuer ownership | do not conflate (finding T-9) | §3.5 |
| `edgartools` | Python | 🟢 | Parsed filings, statements, insiders | installed | same |
| sec-api.io | REST | 🔴 🔑 | Filing stream, extracted items | optional | §14.1 |
| CourtListener / RECAP | REST | 🟢 🔑 | Federal dockets/opinions | available | §14.3 |
| Federal Register API | REST | 🟢 | Rulemaking mentions | available | §4.6, §14.2 |

## 7. Regulatory & Corporate Filings — Global *(expanded per finding T-8; one row per system)*

| Jurisdiction | Service | Access | What it provides |
|---|---|---|---|
| EU/UK (listed) | filings.xbrl.org API | 🟢 | ESEF/UKSEF Inline XBRL filings, xBRL-JSON |
| UK registry | Companies House API | 🟢 🔑 | Officers, PSCs (beneficial owners), accounts |
| EU registries | BRIS + national registers (Handelsregister 🟡, Infogreffe 🟡, …) | varies | Statutory filings — each register has its own API/fees; verify per country |
| Canada | SEDAR+ (filings) + SEDI (insiders) | 🟢 web | Canadian public-company filings; no stable public API — treat as fetch target |
| Japan | EDINET API v2 | 🟢 🔑 | Filings + XBRL + metadata |
| Korea | Open DART API | 🟢 🔑 | Disclosures, financials, ownership, material events |
| India | NSE/BSE announcement feeds + MCA21 | 🟢/🟡 | Exchange announcements, shareholding patterns; MCA docs per-fee |
| Hong Kong | HKEXnews + Companies Registry | 🟢/🟡 | Listed-company filings; registry docs paid |
| Singapore | ACRA Bizfile | 🟡🔴 | Profiles, officers, shareholders — per-document fees |
| Australia/NZ | ASX announcements + ASIC registers + NZ Companies Register | 🟢/🟡 | Market announcements; ASIC extracts paid |
| Brazil | CVM Open Data | 🟢 | Issuer registrations, periodic filings, reference forms |
| Other | Generic local-registry mode | varies | Per §0 jurisdiction adapter |

## 8. Financial Market & Fundamentals Data

| Service | Type | Access | What it provides | Status/caveats | Vantage §§ |
|---|---|---|---|---|---|
| `yfinance` | Python | 🟢 📜 ⚠️ | Prices, statements, multiples, holders | **triage/reconciliation only** — unofficial wrapper (finding T-14) | §6 |
| Financial Modeling Prep | REST | 🟡 🔑 | Statements, ratios, peers, transcripts | verify plan limits | §6, §11.3, §13.4 |
| Alpha Vantage | REST | 🟡 🔑 | Fundamentals, prices, FX | free tier tight | §6 |
| **Massive.com (formerly Polygon.io)** | REST | 🟡 🔑 | Market/reference data, corporate actions | **rebranded Oct 2025; migrate to `api.massive.com`** (finding T-2) | §6.7 |
| Finnhub / Tiingo | REST | 🟡 🔑 | Fundamentals, estimates, insider data / EOD + news | available | §6.8, §13.6 |
| Nasdaq Data Link | REST | 🟡 🔑 | Curated datasets | available | §4.7 |
| Morningstar / S&P Capital IQ / **LSEG Data & Analytics (ex-Refinitiv)** / Bloomberg / FactSet | Enterprise | 🏢 ⚖️ | Gold-standard estimates, ownership, private financials | current product names (finding T-11); cite by name; check redistribution terms | §6, §11 |

## 9. Earnings Calls, Transcripts & IR — with provenance classes *(finding T-15)*

| Service | Provenance class | Access | Caveats | Vantage §§ |
|---|---|---|---|---|
| Company IR site: prepared remarks, official transcripts, webcasts | **Official** | 🟢 | The quote-governing source | §9, §13.4 |
| Motley Fool / Seeking Alpha transcripts | **Third-party transcription** | 🟢/🟡 📜 ⚖️ | Transcription errors possible; verify material quotes against audio/official text | §13.4 |
| FMP / API Ninjas transcript endpoints | Third-party | 🟡 🔑 | Verify availability per plan before implementation | §13.4 |
| Quartr | Third-party + audio | 🔴 🔑 | Audio search useful for quote verification | §13.4 |
| AlphaSense / Tegus | Licensed platform | 🏢 ⚖️ | Expert-call content is licensed — no redistribution/quoting in generated dossiers without checking terms (finding T-10) | §9, §13 |

## 10. News, Media & Event Monitoring

| Service | Type | Access | What it provides | Status/caveats | Vantage §§ |
|---|---|---|---|---|---|
| GDELT 2.0 | Open API+BigQuery | 🟢 | Global news graph, tone, entities | available | §12.5, §21.4 |
| NewsAPI.org | REST | 🟡 🔑 | Article search | free tier = dev only | §21.4 |
| Event Registry (NewsAPI.ai) | REST | 🔴 🔑 | Event clustering, entity news | available | §13 |
| NewsData.io / Mediastack / GNews | REST | 🟡 🔑 | Budget aggregation | available | §21.4 |
| Google News RSS | RSS | 🟢 ⚠️ | Zero-key per-company feed | **UNOFFICIAL — no contract/SLA** (finding T-13); fallback required; never sole source | monitoring |
| **Quantexa News API (ex-AYLIEN)** | REST | 🔴 🔑 | NLP-enriched news | current product name (finding T-11) | §12.5 |
| PR Newswire / Business Wire / GlobeNewswire | Web | 🟢 | Primary press releases | "primary" = the company said it (claim-sensitive rule) | §13.1 |

## 11. Company, Startup & Private-Market Intelligence

| Service | Type | Access | What it provides | Status/caveats | Vantage §§ |
|---|---|---|---|---|---|
| Crunchbase | REST | 🔴 🔑 ⚖️ | Funding, investors, people | check redistribution terms | §9.3, §16.3 |
| PitchBook / CB Insights / Dealroom / Tracxn | Enterprise | 🏢 ⚖️ | Private valuations, market maps | licensed | §6.7, §11 |
| Mergermarket / Dealogic | Enterprise | 🏢 ⚖️ | Deal pipelines, advisers, transactions | new (addition 46) | §9.3 |
| Owler | Freemium | 🟡 | Competitor sets, estimates | estimates = LOW confidence | §11.1 |
| People Data Labs / Coresignal | Data API | 🔴 🏢 ⚖️ | Firmographic/workforce datasets | licensed; PII handling review | §10.7 |
| Apollo.io / **HubSpot Breeze Intelligence (ex-Clearbit)** | REST | 🟡 🔑 ⚖️ | Firmographics, enrichment | current product name (finding T-11); legacy Clearbit APIs differ | §10, §16 |
| ZoomInfo | Enterprise | 🏢 ⚖️ | Org charts, contacts, intent | licensed; PII rules | §10.4 |
| BoardEx / ExecuComp (WRDS) | Enterprise | 🏢 | Board/exec histories, networks, comp | new (addition 47) | §10.1–10.2 |

## 12. Jobs, Talent & Organizational Signals *(all rows = OBSERVED-SIGNAL class)*

| Service | Access | What it provides | Caveats | Vantage §§ |
|---|---|---|---|---|
| Careers site + ATS public JSON (Greenhouse/Lever/Workday) | 🟢 | Ground-truth open roles | classify tech mentions: CURRENTLY-USED/MIGRATING-TO/EVALUATING/SKILL-PREFERENCE/AMBIGUOUS (finding 20) | §13.3, §21.5 |
| LinkedIn | 🏢 📜 ⚖️ | Headcount/hiring/moves | partner API or licensed vendors only | §10, §13.3 |
| Coresignal / Revelio / Live Data | 🔴 🏢 ⚖️ | Licensed workforce flows | licensed | §10.7 |
| Adzuna API | 🟡 🔑 | Aggregated postings + salary | signal | §13.3 |
| Indeed / Glassdoor | 🟡 📜 ⚖️ | Postings, reviews | no general public API; compliant vendors only; sample-size discipline on reviews (finding 31) | §12.5, §10.7 |
| layoffs.fyi / state WARN databases | 🟢 | Layoff events | formats vary by state | §10.7 |
| OSHA / NLRB data | 🟢 | Safety citations, labor cases, union activity | new (addition 19) | §10.8, §14 |
| GitHub API / GitLab API + package registries | 🟢 🔑 | Engineering activity, OSS posture, adoption signals | attribution to the right org required | §8, §15.5, §21.6 |

## 13. Technology Stack & Product Discovery *(signal class — corroborate before CONFIRMED)*

| Service | Access | What it provides | Evidence strength | Vantage §§ |
|---|---|---|---|---|
| BuiltWith / Wappalyzer | 🔴/🟡 🔑 | Web-facing stack + history | Medium — web-facing only | §8.1 |
| HG Insights / SimilarTech | 🏢 | Back-office technographics (ERP/CRM installs) | Medium-high (modeled) | §8.1.1, §16.1 |
| StackShare | 🟢 | Self-reported stacks | Self-reported | §8.1 |
| G2 / TrustRadius / Gartner Peer Insights | 🟡 📜 ⚖️ | Review presence + buyer sentiment | **Weak signal — a review ≠ the company runs it** (finding T-7); corroborate | §8.1, §16.1 |
| 42matters / Sensor Tower (data.ai brand retired) | 🔴 🏢 | App portfolio, SDKs, downloads | current naming (finding T-11) | §8, §12.4 |
| Shodan / Censys | 🟡 🔑 | Internet-exposed footprint | passive lookups only; attribution checks mandatory | §8.4 |
| crt.sh / DNS / ICANN RDAP | 🟢 | Subdomains, SaaS-tenant hints, registration data | **Weak signal — cert/CNAME ≠ confirmed tenant** (finding T-7); shared infra causes false positives | §8.1.1 |
| SecurityTrails / DomainTools | 🔴 🏢 | DNS history, infra relationships | new (addition 32) | §8.4 |

## 14. Patents, Trademarks, Research & IP *(expanded)*

| Service | Access | What it provides | Vantage §§ |
|---|---|---|---|
| PatentsView (USPTO) | 🟢 🔑 | US patents, assignees, citations | §9.4, §21.6 |
| EPO OPS | 🟢 🔑 | European/worldwide families | §21.6 |
| Google Patents (+BigQuery) | 🟢 | Global search + bulk analytics | §21.6 |
| Lens.org | 🟡 🔑 | Patents + scholarly linked | §9.4 |
| **USPTO TSDR / Trademark Search** | 🟢 | US trademark status/ownership | new (addition 33) — §21.6 |
| **WIPO Global Brand DB / EUIPO** | 🟢 📜 | International/EU trademarks | new (addition 34) — §21.6 |
| OpenAlex / Semantic Scholar / arXiv / Crossref | 🟢 | Scholarly output, corporate AI-lab preprints | §8.3, §9.4 |

## 15. Sanctions, Enforcement, Integrity & Influence *(new category — findings T-20, additions 14–21)*

| Service | Access | What it provides | Vantage §§ |
|---|---|---|---|
| OFAC Sanctions List Service | 🟢 | US sanctions lists | §14.8 |
| EU / UK / UN consolidated sanctions lists | 🟢 | Non-US restricted-party data | §14.8 |
| OpenSanctions | 🟢 open data / 🔴 API | Consolidated sanctions + PEP + corporate networks | §14.8 |
| SEC / DOJ / FTC / CFPB enforcement feeds | 🟢 | Cases, settlements, consumer-finance actions | §14.2–14.3 |
| CFPB Consumer Complaint Database API | 🟢 | Complaint narratives + trends by company | §7.6 |
| Violation Tracker (Good Jobs First) | 🟢 | Misconduct/penalty history | §14.3 |
| Senate LDA / FEC API / OpenSecrets | 🟢/🟡 🔑 | Lobbying, political contributions | §14.9 |
| EU Transparency Register | 🟢 | EU lobbying entities + expenditure | §14.9 |

## 16. ESG, Sustainability & Governance

| Service | Access | What it provides | Vantage §§ |
|---|---|---|---|
| Company sustainability/CSR report | 🟢 | Scope 1/2/3, targets — self-reported (independence rule applies to outcome claims) | §17.2 |
| CDP | 🟡 🏢 ⚖️ | Standardized climate disclosures | §17.1 |
| MSCI ESG / Sustainalytics / S&P CSA | 🟡 🏢 ⚖️ | Headline scores public; detail licensed | §17.1 |
| SBTi database | 🟢 | Validated net-zero commitments | §17.2 |
| EPA (ECHO, FLIGHT, TRI) | 🟢 | US emissions/violations | §14.4, §17.2 |
| Climate TRACE | 🟢 | Facility-level emission estimates | §17.2 |
| UN Global Compact participants | 🟢 | Participation status, COPs | new (addition 48) — §17 |
| ISS / Glass Lewis | 🏢 ⚖️ | Governance scores, proxy recs | §17.4 |

## 17. Sector & Macro Data *(new rows per additions 35–37)*

| Service | Access | What it provides | Vantage §§ |
|---|---|---|---|
| FRED / World Bank / IMF / OECD / Eurostat | 🟢 (🔑 for FRED) | Macro series | §4.7 |
| BLS / Census / BEA | 🟢 🔑 | US labor/industry structure | §4.1, §4.7 |
| ClinicalTrials.gov API | 🟢 | Sponsor trials, phases, outcomes | Healthcare vertical §§ |
| openFDA APIs | 🟢 🔑 | Adverse events, recalls, labels, enforcement | Healthcare §14 |
| EIA API / IEA datasets | 🟢 🔑 / mixed | Energy production, prices, infrastructure | Energy vertical §§ |
| ACSI + sector complaint regulators | 🟢 summaries | Standardized satisfaction benchmarks | §12.4 |

## 18. Public Contracts & Procurement *(globalized per additions 38–40)*

| Service | Access | What it provides | Vantage §§ |
|---|---|---|---|
| USAspending.gov API | 🟢 | US federal awards to the company | §13.7, §16 |
| SAM.gov / GovTribe / HigherGov | 🟡 🔑 | US opportunities, vehicles, expirations | §18.6 |
| TED Search API (EU) | 🟢 | EU notices, buyers, winners, CPV codes | §13.7 |
| UK Contracts Finder API | 🟢 | UK opportunities + awards | §13.7 |
| CanadaBuys / AusTender | 🟢 | Canadian/Australian notices + awards | §13.7 |

## 19. Supply Chain, Trade & Facilities *(expanded per additions 26–28, 41–42)*

| Service | Access | What it provides | Vantage §§ |
|---|---|---|---|
| UN Comtrade / USITC DataWeb | 🟢 | Trade flows | §5.8, §14.5 |
| Open Supply Hub | 🟢 | Facility/supplier locations with provenance | §7.3 |
| ImportYeti | 🟢 web ⚠️ | US bill-of-lading relationships | reuse/API terms unverified — check before production | §5.8 |
| ImportGenius / Panjiva (S&P) | 🏢 ⚖️ | Shipment-level import/export records | §5.8, §7.3 |
| Sayari | 🏢 | Ownership + trade + sanctions relationship graphs | §14.8 |
| OpenStreetMap Overpass API | 🟢 (attribution) | Mapped offices/plants/stores | §3.4 |
| Global Energy Monitor | 🟢 (license) | Power/mining/steel/oil-gas facility datasets | Energy §3.4 |

## 20. Cyber & Reliability Signals *(new category — additions 29–31, 44)*

| Service | Access | What it provides | Caveats | Vantage §§ |
|---|---|---|---|---|
| CISA KEV catalog | 🟢 | Exploited-vulnerability list | context for vendor/product risk | §8.4 |
| NVD API | 🟢 (🔑 for limits) | CVE/CVSS/CPE data | product-level, not company-level | §8.4 |
| BitSight / SecurityScorecard | 🏢 | External cyber-risk ratings | treat as estimates, not audits | §8.4 |
| Public Statuspage histories / incident feeds | 🟢 | Outage/incident patterns | availability varies | §7.6 |

## 21. Social, Community & Sentiment *(sample-size discipline applies — finding 31)*

| Service | Access | What it provides | Status/caveats | Vantage §§ |
|---|---|---|---|---|
| Reddit Data API | 🔑 📜 ⚖️ | Community sentiment | **Commercial use requires a separate Reddit agreement** (finding T-5) — not ordinary freemium; retention/deletion rules apply | §12.5 |
| X (Twitter) API v2 | 🔴 🔑 | Executive/brand posts | costly tiers | §13 |
| YouTube Data API | 🟢 🔑 | Video **metadata + search**; caption tracks need OAuth | **not a general transcript API** (finding T-4) — for quotes use official IR transcripts or licensed transcription | §13.4 |
| Hacker News (Algolia) | 🟢 | Tech-community signal | anecdotal | §12.5 |
| Stack Exchange API | 🟢 🔑 | Developer traction | signal | §8 |
| Meta Ad Library | 🟢 (API scope varies) | Ad creative/spend — **API coverage varies by ad type & jurisdiction** (finding T-16) | portal vs API distinguished | §12.3 |
| Google Ads Transparency Center | 🟢 **portal only** ⚠️ | Ad creative lookup | no general public API | §12.3 |
| Podcast Index / Listen Notes | 🟡 🔑 | Executive interviews | check transcript provenance | §13.4 |
| Google Trends (`pytrends`) | 🟢 📜 ⚠️ | Search-interest trends | UNOFFICIAL — breakage risk; never sole source | §12.5 |

## 22. Web Traffic & Digital Presence

| Service | Access | What it provides | Vantage §§ |
|---|---|---|---|
| Similarweb | 🔴 🔑 ⚖️ | Traffic/engagement (licensed — check quoting terms) | §21.7 |
| Semrush / Ahrefs | 🔴 🔑 | SEO/keywords/backlinks | §21.7 |
| Cloudflare Radar / Tranco | 🟢 | Domain ranking & trends | §21.7 |
| 42matters / AppFollow / `google-play-scraper` ⚠️ | 🟡 | App ratings/reviews/updates | §12.4 |

## 23. Source Preservation & Provenance *(new category — additions 45, 50)*

| Service | Access | What it provides | Vantage §§ |
|---|---|---|---|
| Internet Archive Save Page Now / WARC storage | 🟢 📜 | Reproducible snapshots of changeable evidence — archive every load-bearing URL | §21.1 |
| Zotero API or internal provenance store | 🟢 🔑 / self-hosted | Bibliography, source IDs, snapshots, dedup — backs the §21.1 Source Manifest | §21.1, §21.9 |
| SQLite `storage/` layer (this repo) | 🟢 | Raw response cache keyed by source ID — enables re-verification without re-fetch | all |

## 24. MCP Servers (Claude-native)

| MCP server | Maintainer | Access | Notes |
|---|---|---|---|
| Fetch / Filesystem / Memory (reference) | Anthropic/MCP org | 🟢 | Baseline fetch + evidence-ledger persistence |
| Playwright MCP | Microsoft | 🟢 | JS-heavy IR portals |
| GitHub MCP | GitHub | 🟢 🔑 | §8, §15.5 |
| Brave Search MCP | Brave | 🟡 🔑 | Search fallback |
| Tavily MCP / Exa MCP / Firecrawl MCP / Perplexity MCP | Vendors | 🟡/🔴 🔑 | Agent-ready search/extract/grounded-answers |
| Bright Data MCP / Apify MCP | Vendors | 🔴/🟡 🔑 ⚖️ | Compliance rule applies per source |
| Financial Datasets MCP / AlphaVantage MCP | Vendors | 🟡 🔑 | §6 |
| Community EDGAR / yfinance MCPs | Community | 🟢 ⚠️ | Audit code first; prefer in-repo wrappers |

> Runtime MCP availability is **run metadata, not catalog fact** (finding T-18): each pipeline run should record which MCPs were actually loaded in its environment.

## 25. Orchestration & Harnesses

| Tool | Access | Status | Role |
|---|---|---|---|
| Claude Messages API + server tools (Fable 5) | 🔴 | available | Single-session Executive-tier runs |
| Claude Managed Agents | 🔴 (beta) | available | Hosted phased runs, rubric-graded outcomes, scheduled refreshes |
| Claude Agent SDK | 🔴 | available | Self-hosted harness |
| Claude Code Workflow (`vantage` engine) | 🟢 subscription | **external** (`~/Developer/vantage`) | Default multi-agent runner |
| LangGraph / CrewAI / Google ADK | 🟢 | **external** (vantage backends) | Alternates |
| `src/company_research/tools/` + `rate_limiter.py` + `storage/` | 🟢 | **installed** (scaffold) | In-repo wrappers, rate limiting, cache |

---

## Coverage Map — Vantage Section → Primary Tooling (v3 sections)

| Vantage area | First choice | Backup / enrichment |
|---|---|---|
| Entity resolution (§0, §3.6) | EDGAR/registry lookup, GLEIF, OpenFIGI, PermID | OpenCorporates, Wikidata |
| Global filings backbone | Jurisdiction adapter row (§7 above) | filings.xbrl.org, sec-api |
| Financials (§6, §21.3) | EDGAR/ESEF XBRL via `edgartools`/Docling → precomputed | FMP, Alpha Vantage; `yfinance` triage |
| Ownership & activism (§3.5–3.7) | Proxy tables, 13D/G, Forms 3/4/5, OpenOwnership | BoardEx, Orbis |
| Strategy & priorities (§9, §13.4) | IR decks + official transcripts | Third-party transcripts (verified), Quartr |
| Tech stack (§8) | ATS feeds (classified), BuiltWith/Wappalyzer, GitHub | HG Insights, G2 (weak), crt.sh (weak) |
| AI & agentic posture (§8.3, §15) | Job postings, arXiv/OpenAlex, keynotes, eng blogs | Patents, press releases |
| Leadership & org (§10) | Proxy, IR bios, compliant workforce vendors | BoardEx, podcasts |
| Risk, legal, sanctions (§14) | Item 1A/1C equivalents, CourtListener, OFAC/EU/UK/UN lists, enforcement feeds | Violation Tracker, OpenSanctions |
| Procurement (§13.7) | USAspending, TED, Contracts Finder, SAM.gov | GovTribe, CanadaBuys/AusTender |
| Quality/reliability (§7.6) | CFPB complaints, statuspages, recalls (openFDA) | ACSI, review sites (weak) |
| ESG (§17) | Sustainability report, SBTi, CDP | Headline ESG scores, EPA, Climate TRACE |
| Preservation (§21.1) | Wayback SPN + SQLite cache | Zotero/provenance store |

---

## Selection Guidance (v2)

1. **Primary-source first** — jurisdiction-adapter filings + IR + official transcripts give ~60% of the dossier at HIGH confidence for $0.
2. **One tool per job in the hot path** — the Fable 5 session runs on Anthropic web_search + web_fetch; everything else is pre-fetch pipeline or MCP-equipped subagents.
3. **Signals are not facts** — every ⚠️/signal-class source feeds OBSERVED-SIGNAL claims that need corroboration before CONFIRMED.
4. **Licensing is a per-source legal question** — ⚖️ rows require documented reuse rights; vendor availability ≠ permission; expert-network and licensed analyst content is never redistributed in generated dossiers.
5. **Cache + archive everything** — route APIs through `rate_limiter.py`, persist raw responses in `storage/`, archive load-bearing URLs via Save Page Now; the Verification Pass re-checks from cache.
6. **Free-tier viable stack** — EDGAR/ESEF + `edgartools` + Docling + GDELT + ATS feeds + PatentsView + OFAC/EU lists + USAspending/TED + FRED + Wayback + Brave free tier: MEDIUM-to-HIGH-confidence dossier on most public companies at $0.
7. **Re-verify this catalog quarterly** — entries carry a last-verified date at the top; the Google CSE retirement and Polygon→Massive rebrand show how fast rows rot.

---

*Vantage Tooling Catalog v2.0.0 | Vantage contributors*
