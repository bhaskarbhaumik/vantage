# Vertical Modules — V-HLS · V-BFSI · V-RCG · V-ENR · V-MFG · V-TMT · V-TTH · V-GOV

> `prompts/aid-prompt-v2.md` named these eight modules and their anchor points but left their
> content unwritten. This file authors them.

## ⚠️ How to use these lists — read before anything else

Every candidate list below is a **search checklist, not a set of facts**. Its only purpose is to
tell the research agent *what to look for* and *what vocabulary to search with*.

**Correct use:** "The `V-BFSI` module lists core-banking platforms as a domain to investigate, so
I search for evidence of this client's core-banking platform. I find a 2025 vendor case study
naming Temenos → I register the source and write the row."

**Incorrect use — and the single most likely fabrication route in this entire harness:**
"The `V-BFSI` module lists Temenos, FIS, and Fiserv as typical core-banking platforms, so I write
that the client runs one of them."

A candidate list is never evidence. If the vertical says a system class is typical and you find
no evidence of it at this client, that is a `[DATA GAP]` — and often an interesting one, because
absence of any public signal about a core system is itself a finding about the client's
disclosure posture.

## Module selection

Selected by the `scoping` agent in §0.1, from GICS sector plus business description, with a
confidence level. Confidence below Medium ⇒ run `Core` blueprint only and record a gap.
Multi-vertical conglomerates: select the module matching the **segment in pursuit scope**, not
the largest segment; state the choice and its basis in §0.1.

| Module | Vertical | Typical GICS sectors |
|--------|----------|----------------------|
| `V-HLS` | Healthcare & Life Sciences | 35 Health Care |
| `V-BFSI` | Banking, Financial Services & Insurance | 40 Financials |
| `V-RCG` | Retail & Consumer Goods | 30 Consumer Staples, 25 Consumer Discretionary (retail) |
| `V-ENR` | Energy, Resources & Utilities | 10 Energy, 55 Utilities, 15 Materials |
| `V-MFG` | Manufacturing & Industrials | 20 Industrials, 25 Auto |
| `V-TMT` | Technology, Media & Telecom | 45 IT, 50 Communication Services |
| `V-TTH` | Travel, Transport & Hospitality | 25 Hotels/Restaurants/Leisure, 20 Transportation |
| `V-GOV` | Public Sector & Government | Non-GICS; government, defence, public agencies |

## Uniform module structure

Each module supplies six blocks, injected at declared anchors:

| Block | Injected at | Nature |
|-------|-------------|--------|
| **T** Trend library | §3.1 | Candidate trends — include only those you can evidence *for this client's market* |
| **S** Domain systems | §6.1 | Search checklist for the domain-specific stack |
| **R** Regulatory regimes | §10.2 | Candidate regimes — include only those with evidenced applicability |
| **U** Use-case seeds | §11.2 | Starting points for `U-nn`; each still needs a §6/§7 claim to survive |
| **E** Evidence sources | §0.3 | Where this vertical's primary evidence actually lives |
| **X** Traps | all | Vertical-specific ways this dossier commonly goes wrong |

Full module output that does not fit inline goes to **Appendix J**.

---

# V-HLS — Healthcare & Life Sciences

**Extra anchors:** §3.1 trends · §6.1 clinical systems · §10.2 HIPAA/FDA · §3.6 payer/provider mix

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

**Extra anchors:** §6.1 core banking/risk · §10.2 Basel/SOX/AML · §4.2 regulatory-capital framing

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

**Extra anchors:** §3.1 consumer trends · §4.1 channel mix · §6.1 commerce stack · §3.6 (Core)

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

**Extra anchors:** §10.2 NERC/FERC · §10.4 ESG (**Core**, not Opt) · §7.x grid/twin use cases

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

**Extra anchors:** §2.4 plant footprint · §6.1 MES/PLM · §7.x smart-factory library

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

**Extra anchors:** §6.2 cloud depth · §4.1 platform/network economics · §3.2 ecosystem position

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

**Extra anchors:** §4.1 loyalty/distribution economics · §11.2 CX library · §3.6 (Core)

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

**Extra anchors:** §8.2 procurement regulation · §10.2 FedRAMP/FISMA · §12.5 contract-vehicle
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
