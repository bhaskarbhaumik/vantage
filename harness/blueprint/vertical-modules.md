# Vertical Modules v3.0.0 — eleven modules

> `vantage-20260829.md` names eleven verticals and the sections each one enhances, but leaves the
> content of the enhancement unwritten. This file authors it. Modules are self-contained packets
> injected at declared anchors; they **supplement** the owning agent's section and never replace it.

## ⚠️ How to use these lists — read before anything else

Every candidate list below is a **search checklist, not a set of facts**. Its only purpose is to
tell the research agent *what to look for* and *what vocabulary to search with*.

**Correct use:** "The `V-BFSI` module lists core-banking platforms as a domain to investigate, so I
search for evidence of this client's core-banking platform. I find a 2025 vendor case study naming
Temenos → I register the source, classify the mention as `CURRENTLY-USED`, and write the row."

**Incorrect use — and the single most likely fabrication route in this entire harness:** "The
`V-BFSI` module lists Temenos, FIS, and Fiserv as typical core-banking platforms, so I write that
the client runs one of them."

A candidate list is never evidence. If the vertical says a system class is typical and you find no
evidence of it at this client, that is `[DATA UNAVAILABLE]` plus a `G-nnnn` gap — and often an
interesting one, because the absence of any public signal about a core system is itself a finding
about the client's disclosure posture.

## Module selection

Selected by `preflight` in §0 from **actual revenue/segment mix** — not classification codes alone,
which may be absent or misleading for private, non-US, or conglomerate targets. GICS, SIC, NAICS,
NACE and ISIC are all supported as inputs; none of them is decisive on its own.

- **PRIMARY and SECONDARY** verticals are both recorded.
- **Conglomerates**: apply the overlay **per major segment**, and select the primary module by the
  segment in pursuit scope — not the largest segment. State the choice and its basis in §0.
- **Confidence below Medium** ⇒ run the Core blueprint only, record a gap, and say so.
- A vertical with no module here uses the **nearest analog** plus sector-specific regulators and
  KPIs, stated explicitly as an analog.

| Module | Vertical | Typical sectors |
|---|---|---|
| `V-HLS` | Healthcare & Life Sciences | GICS 35 Health Care |
| `V-BFSI` | Financial Services & Insurance | GICS 40 Financials |
| `V-RCG` | Retail & CPG | GICS 30 Consumer Staples, 25 Consumer Discretionary (retail) |
| `V-ENR` | Energy, Utilities & Resources | GICS 10 Energy, 55 Utilities, 15 Materials |
| `V-MFG` | Manufacturing & EPC | GICS 20 Industrials, 25 Automotive |
| `V-TMT` | Telecom, Media & Technology | GICS 45 IT, 50 Communication Services |
| `V-TTH` | Travel, Transportation & Hospitality | GICS 25 Hotels/Restaurants/Leisure, 20 Transportation |
| `V-GOV` | Government & Public Sector | Non-GICS; government, agencies, public bodies |
| `V-AND` | Aerospace & Defense | GICS 20 Aerospace & Defense |
| `V-REC` | Real Estate & Construction | GICS 60 Real Estate, 20 Construction & Engineering |
| `V-PSE` | Professional Services & Education | GICS 20 Professional Services, 25 Education Services |

## Enhanced sections per vertical

From `vantage-20260829.md` §Vertical & Classification Model. These are the subsections where the module
materially changes what "complete" means.

| Vertical | Enhanced sections |
|---|---|
| `V-HLS` | 3.5 · 4.6 · 6.6 · 7.3 · 8.1.1 · 8.5 · 10.4 · 14.1 · 14.2 · 15.3 |
| `V-BFSI` | 4.5 · 4.6 · 6.3 · 8.1.1 · 8.4 · 10.4 · 14.1 · 14.2 · 15.3 |
| `V-RCG` | 4.3 · 5.2 · 5.8 · 7.3 · 8.1.1 · 12.1 · 12.3 · 15.3 |
| `V-ENR` | 4.3 · 4.6 · 5.8 · 7.3 · 8.3.3 · 14.1 · 17.2 · 15.3 |
| `V-MFG` | 3.4 · 4.4 · 5.8 · 7.1–7.3 · 8.3.3 · 15.3 · 17.2 |
| `V-TMT` | 4.3 · 5.4 · 8.1.2 · 8.3 · 11.6 · 15.3 |
| `V-TTH` | 4.3 · 5.2 · 12.1 · 12.3 · 14.5 · 15.3 |
| `V-GOV` | 4.6 · 10.4 · 14.2 · 16.1 · 19.6 |
| `V-AND` | 4.6 · 5.8 · 8.4 · 14.5 · 14.8 · 15.3 |
| `V-REC` | 3.4 · 5.9 · 6.3 · 7.3 · 14.1 · 15.3 |
| `V-PSE` | 5.9 · 7.4 · 10.7 · 12.2 · 15.3 |

## Uniform module structure

Each module supplies six blocks, injected at declared anchors:

| Block | Injected at | Nature |
|---|---|---|
| **T** Trend library | §4.3 | Candidate trends — include only those you can evidence *for this client's market* |
| **S** Domain systems | §8.1.1 | Search checklist for the domain-specific stack; every hit still needs a mention classification |
| **R** Regulatory regimes | §4.6 / §14.2 | Candidate regimes — include only those with **evidenced applicability**, and complete all eleven register fields |
| **U** Use-case seeds | §15.3 | Starting points for `U-nn`; each still needs a §7.5 pain point or §9.1 priority to survive |
| **E** Evidence sources | §0 / §21.12 | Where this vertical's primary evidence actually lives — sets the *expected source classes* for the completeness scorecard |
| **X** Traps | all | Vertical-specific ways this dossier commonly goes wrong |

The **vertical KPI add-ons** for §1.1 and §5.9 are named per module under **E**: regulator (regulated
industries), backlog (EPC), AUM (asset managers), same-store sales (retail), RPK/load factor
(airlines), FFO/occupancy (real estate), utilisation/billable headcount (professional services).

Module output that does not fit inline goes to the **vertical annex in §21**.

---
# V-HLS — Healthcare & Life Sciences

**Enhanced sections:** §3.5 ownership form (nonprofit systems) · §4.6 HIPAA/FDA/CMS · §6.6 IT spend · §7.3 supply chain · §8.1.1 clinical systems · §8.5 IT governance · §10.4 clinical vs administrative buying centres · §14.1 · §14.2 · §15.3

**T — Trends.** Value-based care transition · site-of-care shift to ambulatory/home · payer–provider
vertical integration · GLP-1 demand shock across pharma and payer economics · clinical-trial
decentralisation · drug-pricing reform exposure · biosimilar and patent-cliff timing · provider
labour cost and clinician burnout · prior-authorisation automation mandates · real-world-evidence
commercialisation.

**S — Domain systems.** EHR/EMR · revenue-cycle management · clinical data repository / FHIR
interoperability layer · PACS/imaging · LIMS and ELN (life sciences) · CTMS and EDC · regulatory
submission management · pharmacovigilance · patient CRM and engagement · claims adjudication ·
care management · population-health analytics · GxP-validated cloud environments.

**R — Regimes.** HIPAA/HITECH · FDA 21 CFR Part 11 · GxP (GMP/GCP/GLP) · ONC information-blocking
and TEFCA · CMS interoperability and prior-authorisation rules · EU MDR/IVDR · EMA · state privacy
statutes · Anti-Kickback and Stark · DSCSA serialisation · EU AI Act high-risk classification for
clinical decision support.

**U — Use-case seeds.** Prior-authorisation and claims-denial agents · clinical documentation
assistance · RWE evidence-generation pipelines · trial-site selection and patient matching ·
regulatory-submission drafting under GxP controls · supply-chain serialisation · revenue-cycle
denial prediction · pharmacovigilance case intake triage.

**E — Evidence sources.** ClinicalTrials.gov · FDA approvals/warning letters/483s · CMS provider
and quality data · EMA registers · payer transparency files · HIMSS and health-IT trade press ·
IQVIA and Evaluate public summaries.

**X — Traps.** *Never infer PHI-handling practices.* GxP validation status is rarely public —
default to `[DATA GAP]`, not `[INFERENCE]`. Data-residency and validated-environment constraints
materially reshape delivery models: reflect them in Model 7 dimension 5 and §12.5, or the
commercial construct will be wrong.

---

# V-BFSI — Banking, Financial Services & Insurance

**Enhanced sections:** §4.5 competitive forces under regulatory capital · §4.6 Basel/SOX/AML · §6.3 balance sheet (NIM, capital ratios replace DuPont) · §8.1.1 core banking/risk · §8.4 cyber (regulated) · §10.4 · §14.1 · §14.2 · §15.3

**T — Trends.** Core-banking modernisation and progressive renovation · real-time payments (FedNow,
UPI, SEPA Inst) · embedded finance and BaaS · deposit-cost and NIM pressure · private-credit
disintermediation · Basel III endgame capital planning · climate-risk stress testing · insurance
claims automation · fraud and APP-scam liability shift · digital-asset custody · agentic advice and
suitability governance.

**S — Domain systems.** Core banking · payments hub and ISO 20022 translation · card processing ·
treasury and ALM · risk engines (credit, market, liquidity) · AML/KYC/transaction monitoring ·
regulatory-reporting platforms · policy administration and claims (insurance) · actuarial platforms ·
wealth and custody platforms · trading OMS/EMS · market-data infrastructure · GRC.

**R — Regimes.** Basel III/IV · Dodd-Frank · SOX · CCAR/DFAST · BSA/AML, OFAC, FinCEN · MiFID II ·
PSD2/PSD3 · DORA · GDPR and state privacy · NYDFS Part 500 · CFPB 1033 open banking · IFRS 9 /
CECL · IFRS 17 · Solvency II · FCA Consumer Duty · SEC cyber disclosure.

**U — Use-case seeds.** AML alert triage and narrative generation · credit-memo drafting · claims
FNOL triage and settlement recommendation · regulatory-change impact mapping · model-risk
documentation under SR 11-7 · complaint handling and Consumer-Duty evidencing · reconciliation
break resolution · KYC refresh automation.

**E — Evidence sources.** Regulatory filings (10-K, call reports, FR Y-9C, Pillar 3) · supervisory
enforcement actions · rating-agency actions · payment-scheme announcements · core-vendor press
releases · central-bank consultations.

**X — Traps.** Model-risk governance (SR 11-7 / SS1/23) constrains *how* AI can be deployed, not
just whether — an AI-readiness score that ignores it will overstate deployability. Regulatory
capital position is a better proxy for transformation capacity than FCF: reflect this in Model 1
dimension 1 and say so. Never infer AML control effectiveness from the absence of enforcement.

---

# V-RCG — Retail & Consumer Goods

**Enhanced sections:** §4.3 consumer trends · §5.2 channel/segment mix · §5.8 supply chain · §7.3 fulfilment · §8.1.1 commerce stack · §12.1 segmentation · §12.3 go-to-market · §15.3

**T — Trends.** Retail-media network build-out as a margin pool · unified commerce and
inventory-visibility investment · private-label mix shift · tariff and sourcing reconfiguration ·
promotion-efficiency and trade-spend optimisation · store-labour productivity · loyalty programme
economics · supply-chain resilience post-shock · shrink and loss prevention · direct-to-consumer
retrenchment · GLP-1 impact on category demand.

**S — Domain systems.** Merchandising and assortment planning · pricing and promotion optimisation ·
POS and store systems · OMS and distributed order management · WMS/TMS · demand planning · PIM/PLM ·
CDP and loyalty · retail-media ad server · e-commerce platform · trade-promotion management (CPG) ·
supplier collaboration portals.

**R — Regimes.** FTC advertising and endorsement rules · state privacy (CCPA/CPRA et al.) ·
PCI DSS · FSMA 204 food traceability · Prop 65 · EU CSRD and EUDR deforestation · packaging EPR ·
UFLPA forced-labour import controls · GDPR for loyalty data.

**U — Use-case seeds.** Assortment and space agents · promotion-effectiveness analysis · demand
sensing · retail-media campaign optimisation · store-associate assistance · customer-service
deflection · supplier-onboarding automation · returns-fraud detection · content and PDP generation
at catalogue scale.

**E — Evidence sources.** 10-K segment and comp-store disclosures · investor-day decks (the richest
source in this vertical) · NRF and Shoptalk coverage · Circana/NIQ public summaries · retail-media
network announcements · supplier and vendor case studies.

**X — Traps.** Comparable-store metrics are defined inconsistently — always reproduce the client's
own definition and cite it. Retail-media revenue is frequently *not* separately disclosed; do not
estimate it into §4.1 without a stated method and range. Franchise vs. company-operated split
changes who actually buys technology: get it right in §2.2 or §8.2 will be wrong.

---

# V-ENR — Energy, Resources & Utilities

**Enhanced sections:** §4.3 energy-transition trends · §4.6 NERC/FERC/environmental · §5.8 commodity procurement · §7.3 asset/field operations · §8.3.3 grid, digital-twin and emerging bets · §14.1 · §17.2 (**Core**, not Opt) · §15.3

**T — Trends.** Load growth from data centres and electrification · grid-capex supercycle and rate-base
growth · interconnection-queue backlog · transmission build-out · renewables and storage integration ·
LNG capacity expansion · carbon capture and hydrogen project economics · methane monitoring mandates ·
mining critical-minerals demand · wildfire and physical-climate liability · nuclear/SMR revival ·
grid-edge DER orchestration.

**S — Domain systems.** ADMS/DMS/EMS · SCADA and OT networks · GIS and network model · outage
management · AMI/meter data management · asset-performance management · work and asset management ·
ETRM/CTRM · production accounting and hydrocarbon allocation · reservoir and subsurface platforms ·
mine planning · plant historians · digital twins.

**R — Regimes.** NERC CIP · FERC orders (incl. interconnection reform) · state PUC rate cases ·
EPA methane and GHG reporting · TSCA · MSHA · PHMSA pipeline safety · EU CSRD and CBAM ·
SEC climate disclosure · IEC 62443 for OT security.

**U — Use-case seeds.** Outage prediction and crew dispatch · vegetation-management targeting ·
asset-health and failure prediction · interconnection-study acceleration · rate-case evidence
assembly · permit and regulatory-filing drafting · predictive maintenance on rotating equipment ·
methane leak detection from sensor and satellite feeds · trading-signal support with strict controls.

**E — Evidence sources.** FERC Form 1 · state PUC rate-case dockets (unusually rich, and public) ·
NERC filings · EIA data · sustainability and TCFD reports · capital-markets days · project FID
announcements.

**X — Traps.** **OT/IT separation is a hard delivery constraint, not a preference** — an AI-readiness
score that ignores the OT boundary will materially overstate near-term deployability; state the
boundary explicitly in §6.6 and §7.4. Rate-regulated utilities have capex approved by regulators,
so "investment capacity" in Model 1 means *rate-base and approved-plan headroom*, not FCF — note
the substitution in Appendix G. §10.4 ESG is Core here.

---

# V-MFG — Manufacturing & Industrials

**Enhanced sections:** §3.4 plant footprint & capacity · §4.4 value chain · §5.8 supply chain · §7.1–7.3 operating model, processes, fulfilment · §8.3.3 smart-factory bets · §15.3 · §17.2

**T — Trends.** Supply-chain regionalisation and China+1 · tariff-driven footprint change ·
aftermarket and service-revenue shift · servitisation and outcome contracts · industrial-software
consolidation · smart-factory and connected-worker programmes · skilled-labour scarcity ·
EV and battery-supply-chain transition (auto) · defence-demand expansion · sustainability-driven
product redesign and Scope 3 traceability.

**S — Domain systems.** ERP (discrete/process) · MES/MOM · PLM · CAD/CAE/CAM · quality management ·
APS and supply planning · SRM and direct procurement · warehouse and logistics execution · field
service management · IIoT platform and historian · digital twin and simulation · dealer/distributor
portals.

**R — Regimes.** ITAR/EAR export controls · CMMC (defence suppliers) · REACH and RoHS · EU
Machinery Regulation · CE/UL product safety · CBAM · EU Battery Regulation and digital product
passport · conflict minerals · OSHA · IATF 16949 and AS9100 quality regimes.

**U — Use-case seeds.** Quality-defect detection and root-cause analysis · production scheduling ·
supplier-risk monitoring · engineering-change impact analysis · service-manual and technical-content
generation · field-technician assistance · warranty-claim analysis · spare-parts demand forecasting ·
bid and quotation generation for configured products.

**E — Evidence sources.** 10-K segment and backlog disclosures · plant announcements and site
investment PRs · Hannover Messe and IMTS coverage · trade associations · supplier-network databases ·
export-control filings.

**X — Traps.** Plant-level technology is almost never disclosed centrally — §6.1 in this vertical is
built from vendor case studies and job postings, which means most rows are `[UNVERIFIED]` and
Model 2 "Operations" often scores Low confidence. That is the correct outcome; do not inflate it.
Aftermarket margin economics drive the actual opportunity and are frequently buried in segment
notes rather than the MD&A — read the notes.

---

# V-TMT — Technology, Media & Telecom

**Enhanced sections:** §4.3 platform/network trends · §5.4 pricing & monetization · §8.1.2 cloud depth · §8.3 AI adoption (the target may itself be an AI vendor) · §11.6 portfolio frameworks · §15.3

**T — Trends.** AI-capex supercycle and compute scarcity · fibre and 5G monetisation gap ·
network-API exposure · content-cost discipline and streaming-profitability pivot · advertising-tier
shift · telco cloud-native core transition · platform-regulation exposure (DMA/DSA) ·
subscription-churn management · semiconductor supply concentration · agentic disruption of software
seat-based pricing.

**S — Domain systems.** BSS/OSS · charging and mediation · network inventory and orchestration ·
service assurance · SDN/NFV controllers · CDN · content supply chain and MAM · ad tech (SSP/DSP) ·
subscriber management · developer platform and API gateway · usage metering and billing.

**R — Regimes.** FCC (US) and Ofcom/BEREC (EU/UK) · spectrum licence conditions · net-neutrality
regimes · EU Digital Markets Act and Digital Services Act · CSAM and content-moderation rules ·
GDPR and ePrivacy · CALEA lawful intercept · export controls on semiconductors · EU AI Act
transparency obligations.

**U — Use-case seeds.** Network fault prediction and self-healing · care deflection and churn-save
agents · content metadata enrichment and localisation · ad-inventory yield optimisation ·
capacity-planning simulation · developer-support agents · billing-dispute resolution · spectrum and
site-acquisition analysis.

**E — Evidence sources.** Regulatory filings and spectrum auction records · MWC and NAB coverage ·
ARPU/churn/subscriber disclosures · hyperscaler and network-vendor partnership PRs · developer
documentation and public API references (unusually informative for §6.1 in this vertical).

**X — Traps.** TMT clients are often *also* technology vendors — §4.4 "IT spend" is meaningless for
them, so substitute **R&D and network capex** and state the substitution. §6.1 must distinguish
what the client *sells* from what the client *runs internally*; conflating them is the signature
error in this vertical and it corrupts every downstream opportunity.

---

# V-TTH — Travel, Transport & Hospitality

**Enhanced sections:** §4.3 demand & distribution trends · §5.2 revenue by segment (RPK, ADR, RevPAR) · §12.1 segmentation · §12.3 distribution & loyalty · §14.5 geopolitical/fuel/weather exposure · §15.3

**T — Trends.** Loyalty-programme monetisation and co-brand economics · direct-booking shift away
from OTAs · dynamic pricing and continuous-pricing offer/order transformation (IATA ONE Order) ·
asset-light franchising · labour cost and crew productivity · SAF mandates and decarbonisation
capex · airport and infrastructure constraints · premium-leisure demand mix · biometric and seamless
travel · logistics-network reconfiguration.

**S — Domain systems.** PSS/CRS and GDS connectivity · revenue management and pricing · offer and
order management · property management systems · central reservation · loyalty platform ·
crew and rostering · maintenance and MRO · fleet and yard management · TMS and freight-forwarding
platforms · disruption-management and rebooking engines.

**R — Regimes.** DOT consumer-protection and refund rules · FAA/EASA airworthiness · EU261 and
UK261 passenger rights · IATA standards · PCI DSS · GDPR and loyalty-data privacy · ADA and
accessibility · food safety · CORSIA and SAF mandates · maritime IMO rules.

**U — Use-case seeds.** Disruption rebooking and proactive rebooking agents · dynamic offer
construction · loyalty-personalisation · maintenance-defect triage · crew-scheduling optimisation ·
contact-centre deflection at irregular-operations peaks · revenue-leakage detection ·
ancillary-attach recommendation.

**E — Evidence sources.** DOT and CAA operating statistics · 10-K unit-economics disclosures (RASM,
CASM, RevPAR, load factor) · loyalty-programme valuation disclosures in financing documents ·
IATA/AAAE conference coverage · OTA and distribution-agreement announcements.

**X — Traps.** Loyalty-programme economics are frequently the client's largest profit pool and are
disclosed only in financing documents (EETC/loyalty-backed notes) — miss them and §4.1 will be
materially wrong. Irregular-operations recovery is the highest-value AI use case in this vertical
and is almost never named in strategy statements; it will be `HYPOTHESIS`, so put it in §13.4.

---

# V-GOV — Public Sector & Government

**Enhanced sections:** §4.6 FedRAMP/FISMA/procurement regulation · §10.4 programme vs agency buying centres · §14.2 · §16.1 incumbent primes · §19.6 stakeholder plan under lobbying rules
constraints · §9.5 (**high-yield** — this is the one vertical where contract data is genuinely public)

**T — Trends.** Legacy-system modernisation backlog and COBOL workforce cliff · shared-services and
consolidation mandates · digital-identity programmes · citizen-experience mandates ·
zero-trust architecture directives · AI-use inventories and agency AI governance · cloud smart
policy · budget-cycle and continuing-resolution volatility · workforce reduction and attrition ·
sovereign-cloud requirements (non-US).

**S — Domain systems.** Benefits and eligibility systems · tax and revenue administration ·
case management · financial management (core accounting) · grants management · procurement
platforms · identity and credentialing · GIS and permitting · public-safety CAD/RMS · legacy
mainframe estates.

**R — Regimes.** FAR/DFARS · FedRAMP and StateRAMP · FISMA and NIST 800-53/171 · CMMC ·
Section 508 accessibility · Privacy Act · CJIS · IRS Publication 1075 · ITAR ·
OMB AI memoranda and agency AI inventories · EU public-procurement directives · national
sovereign-cloud mandates.

**U — Use-case seeds.** Eligibility-determination assistance with mandatory human decision ·
case-backlog triage · benefits fraud detection · legacy-code comprehension and translation ·
public-records and FOIA response · permit-application review · constituent-service agents ·
grant-application processing · procurement-document drafting.

**E — Evidence sources.** **This vertical's advantage: procurement data is public.**
USAspending.gov · SAM.gov and FPDS award data · GAO and Inspector-General reports · agency budget
justifications · state procurement portals · TED (EU) · Contracts Finder (UK) · legislative
appropriations records.

**X — Traps.** Authorisation boundaries (FedRAMP level, IL level, CJIS, IRS 1075) are *binding
delivery constraints* — a §12.5 commercial model that ignores them is unexecutable, and Model 7
dimension 5 must score high. Personnel and offshore-delivery restrictions frequently rule out
standard global delivery models entirely: state this explicitly rather than discovering it later.
Conversely, §9.5 and Model 8 "contract timing" should score with **High confidence** here — award
dates, ceilings, option years, and incumbents are all published. This is the one vertical where
"no contract evidence" means the research was incomplete, not that the data is private.

---

# V-AND — Aerospace & Defense

**Enhanced sections:** §4.6 ITAR/EAR/DFARS · §5.8 supply chain & sole-source exposure · §8.4
cybersecurity (CMMC) · §14.5 geopolitical · §14.8 sanctions & export controls · §15.3

**T — Trends.** Defence-budget cycles and continuing-resolution risk · programme-of-record
consolidation · sustainment and MRO revenue mix shifting against new-build · commercial-aero rate
recovery and supply constraints · space and launch commercialisation · counter-UAS and autonomy
programmes · munitions capacity expansion · additive manufacturing for spares · digital-thread and
model-based systems engineering · allied-industrial-base reshoring · dual-use AI procurement rules.

**S — Domain systems.** Model-based systems engineering (MBSE) · PLM with configuration management
and effectivity · MES for low-volume/high-mix · MRO and sustainment platforms · earned-value
management systems (EVMS) · government-compliant ERP (DCAA-auditable cost accounting) · supply-chain
risk and counterfeit-parts screening · classified/enclave IT environments · ITAR-segregated
collaboration platforms · airworthiness and quality management (AS9100).

**R — Regimes.** ITAR · EAR and the Commerce Control List · DFARS 252.204-7012 and **CMMC** ·
NISPOM / facility clearances · FAR cost-accounting standards and DCAA audit · FAA/EASA airworthiness
· AS9100 · Buy American / Berry Amendment · Foreign Ownership, Control or Influence (FOCI)
mitigation · UN/OFAC/EU/UK arms embargoes · anti-corruption (FCPA, UK Bribery Act) in offset deals.

**U — Use-case seeds.** Digital-thread continuity from requirements to sustainment · predictive
maintenance on fleet telemetry · proposal and EVMS reporting automation under DCAA constraints ·
supply-chain counterfeit and sole-source risk detection · classified-environment-compatible
document intelligence · export-control classification assistance · obsolescence forecasting for
long-life programmes.

**E — Evidence sources.** USAspending.gov and SAM.gov (award history, vehicles, expirations) ·
DoD budget justification books (P-1/R-1) · GAO programme reports · DCMA/DCAA public findings ·
FAA/EASA type certificates and ADs · Bureau of Industry and Security (BIS) entity list · State
Department DDTC consent agreements · defence trade press. **KPI add-ons for §1.1/§5.9:** funded and
unfunded backlog, book-to-bill, programme phase mix.

**X — Traps.** *Classified work is invisible by design.* A thin technology section is expected, not
a research failure — say so in §21.12 rather than filling it from analogues. **Never infer
classified programme content, clearance levels, or facility functions.** Export-control and FOCI
constraints are delivery-model determinants, not footnotes: they belong in §10.8 and Model 7, and
getting them wrong invalidates the commercial construct. Do not conflate the ultimate parent's
sanctions posture with a subsidiary's — §3.6 governs. Backlog is not revenue; state the conversion
assumption or do not size from it.

---

# V-REC — Real Estate & Construction

**Enhanced sections:** §3.4 portfolio/asset footprint · §5.9 unit economics (FFO, occupancy,
backlog) · §6.3 balance sheet & leverage · §7.3 project delivery & supply chain · §14.1 · §15.3

**T — Trends.** Office repricing and hybrid-work demand shift · industrial/logistics absorption ·
data-centre development and power constraints · cap-rate expansion and refinancing walls ·
construction labour scarcity and productivity stagnation · modular and offsite construction ·
embodied-carbon regulation and building-performance standards · insurance cost and climate-risk
repricing · proptech consolidation · infrastructure-stimulus pipelines.

**S — Domain systems.** Property and lease management (with IFRS 16 / ASC 842 lease accounting) ·
project-controls and scheduling (P6-class) · BIM and common data environments · estimating and
cost management · field-management and safety platforms · building management systems and IoT ·
tenant-experience apps · facilities and asset management (CMMS/IWMS) · investment and fund
accounting (REIT) · valuation and appraisal platforms.

**R — Regimes.** Building codes and energy standards · local building-performance laws (e.g. LL97
class) · EU EPBD and CSRD embodied-carbon reporting · REIT qualification tests (income and asset
tests, distribution requirements) · lease-accounting standards · OSHA and equivalent construction
safety regimes · anti-money-laundering rules on real-estate transactions · rent-regulation regimes ·
land-use and environmental permitting.

**U — Use-case seeds.** Bid/estimate assistance from historical cost data · schedule-risk and
delay-cause prediction · BIM clash and constructability review · lease-abstraction and
lease-accounting automation · energy-performance optimisation across a portfolio · tenant-service
agents · claims and change-order analysis · portfolio-level climate-risk exposure modelling.

**E — Evidence sources.** REIT supplementals (the richest single disclosure in this vertical —
property-level NOI, occupancy, lease expiry schedules) · NAREIT data · public planning and
permitting portals · construction trade press and ENR rankings · GRESB scores · Dodge/Construction
Connect pipeline data · local assessor records. **KPI add-ons for §1.1/§5.9:** FFO/AFFO per share,
same-store NOI, occupancy and leased %, WALE/WALT, backlog and burn rate, book-to-bill.

**X — Traps.** *A construction backlog is not committed revenue* — state the conversion and
cancellation assumptions or do not size from it. Do not average cap rates across asset classes or
geographies; the number is meaningless without the class, market, and vintage. **Never estimate a
project value or completion date that is not disclosed** — permits show intent, not contract value.
Joint ventures and non-consolidated entities carry material off-balance-sheet exposure; §6.3 must
address them or the leverage read is wrong. Property-level facts attach to the owning SPV, not the
sponsor — §3.6 governs.

---

# V-PSE — Professional Services & Education

**Enhanced sections:** §5.9 unit economics (utilisation, realisation) · §7.4 shared services &
back office · §10.7 workforce profile (**the primary asset**) · §12.2 portfolio · §15.3

**T — Trends.** GenAI compressing billable-hour and per-seat economics · outcome- and
subscription-based pricing replacing time-and-materials · managed-services shift · talent scarcity
and pyramid inversion · alternative legal/accounting service providers · higher-education
enrolment decline and demographic cliff · online-programme-management (OPM) unbundling and
regulatory scrutiny · skills-based credentialing and employer partnerships · international-student
policy volatility · public-funding and endowment pressure.

**S — Domain systems.** Professional-services automation (PSA) — resource management, time and
expense, project accounting · CRM tuned to pursuit and relationship management · knowledge
management and precedent search · engagement/matter management (legal) · audit and tax platforms ·
learning management systems (LMS) · student information systems (SIS) · admissions and CRM for
enrolment · research administration and grants management · alumni advancement · proctoring and
assessment platforms.

**R — Regimes.** Professional independence and conflict rules (auditor independence, legal conflicts,
PCAOB inspection) · client-confidentiality and privilege obligations · data-residency for
cross-border engagements · FERPA and student-data privacy · Title IV and accreditation requirements
· state authorisation and distance-education reciprocity · incentive-compensation rules for
enrolment · GDPR/CCPA for alumni and applicant data · EU AI Act obligations on education and
employment uses (high-risk classification).

**U — Use-case seeds.** Proposal and pursuit-document generation from precedent · knowledge retrieval
across engagement archives under confidentiality walls · engagement-staffing and utilisation
optimisation · time-capture assistance · audit-evidence and working-paper review support ·
enrolment-funnel and retention-risk modelling · tutoring and advising agents with human oversight ·
grants-compliance automation · credential and transcript verification.

**E — Evidence sources.** Partnership accounts and LLP filings (where the form requires them) ·
IPEDS and national education statistics · accreditor decisions and site-visit reports · Title IV
composite scores and financial-responsibility data · Form 990 for nonprofit institutions · PCAOB
inspection reports · legal and consulting trade press rankings · Common Data Set publications.
**KPI add-ons for §1.1/§5.9:** billable utilisation, realisation and leverage ratio, revenue per
professional, enrolment and yield, retention/graduation rates, net tuition revenue.

**X — Traps.** **Confidentiality is the business model.** Client lists, engagement content, and
matter details are almost never public — their absence is structural, not a gap, and inventing them
is a critical failure. *The workforce is the asset*: §10.7 carries weight here that it does not
carry elsewhere, but it stays aggregate — no individual attrition or performance inference (V9c).
Partnership forms have no market cap, no EPS, and no external shareholders: those fields are
`structurally-inapplicable`, not gaps. For education, **never treat an OPM or vendor relationship as
an institutional endorsement**, and never infer enrolment health from marketing spend. Ranking
positions are marketing artefacts with published methodologies — cite the methodology or do not use
the rank.
