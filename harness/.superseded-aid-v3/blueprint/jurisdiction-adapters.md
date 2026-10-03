# Jurisdiction Adapters v3.0.0

> `preflight` selects the adapter(s) in §0 from where the target **reports**, not where it is
> headquartered — a US-listed foreign private issuer files 20-F with the SEC; a UK subsidiary of a
> US parent files at Companies House. A target may carry **more than one** adapter (dual listing,
> debt issued in a second market, regulated subsidiaries). Record every adapter that governs a
> disclosure the dossier relies on.

Every adapter answers the same four questions:
**(1)** what is the annual disclosure? **(2)** what is the interim? **(3)** where is governance and
ownership disclosed? **(4)** what is the machine-readable financial feed, if any?

---

## US — SEC

| Slot | Instrument |
|---|---|
| Annual | 10-K (domestic) · 20-F (foreign private issuer) · 11-K (benefit plans) |
| Interim | 10-Q · 8-K (material events, incl. Item 1.05 cyber) |
| Governance / ownership | DEF 14A proxy · SC 13D/13G (**beneficial ownership + control intent**) · Forms 3/4/5 (**insider transactions**) |
| Machine-readable | XBRL company facts + frames API |
| Also | S-1/S-4 (offerings, M&A), Exhibit 21 (subsidiaries), Item 1A (risk factors), Item 1C (cybersecurity) |

**13F is holdings OF an institutional manager** — it is not issuer ownership and must never be
presented as such. Enforcement: SEC · DOJ · FTC · CFPB feeds. Litigation: CourtListener / RECAP.

## Canada

| Slot | Instrument |
|---|---|
| Annual | Annual Information Form + audited financials (SEDAR+) |
| Interim | Quarterly filings, material change reports (SEDAR+) |
| Governance / ownership | Management information circular · **SEDI** insider data |
| Machine-readable | None stable — SEDAR+ is a fetch target, not an API |

## UK & EU (listed)

| Slot | Instrument |
|---|---|
| Annual | Annual report + **ESEF/UKSEF inline XBRL** (`filings.xbrl.org`) |
| Interim | Half-yearly report; RNS / Euronext announcements |
| Governance / ownership | Remuneration + governance reports; **Companies House** (officers, PSCs); national registers; EU **BRIS** |
| Machine-readable | `filings.xbrl.org` xBRL-JSON |

National registers vary in cost and API availability (Handelsregister, Infogreffe, …). Verify per
country before promising coverage; record the register actually used.

## India

| Slot | Instrument |
|---|---|
| Annual | Annual report; MCA21 filings |
| Interim | NSE/BSE quarterly results and announcements |
| Governance / ownership | Shareholding patterns (quarterly), related-party disclosures |
| Machine-readable | Exchange announcement feeds |

## Japan · Korea

| Jurisdiction | Annual / interim | Feed |
|---|---|---|
| Japan | Yūka Shōken Hōkokusho via **EDINET** (API v2), TSE disclosures | EDINET XBRL |
| Korea | **DART** disclosures, financials, ownership, material events | Open DART API |

Both require local-language search **in addition to** English. Record `language` on every manifest
entry and mark machine translations.

## Hong Kong · Singapore

| Jurisdiction | Instrument |
|---|---|
| Hong Kong | HKEXnews listed-company filings; Companies Registry (paid documents) |
| Singapore | SGXNet announcements; **ACRA Bizfile** profiles/officers/shareholders (per-document fees) |

## Australia · New Zealand

ASX announcements (continuous disclosure is unusually rich — treat announcements as a primary
class), ASIC company extracts (paid), NZ Companies Register.

## Brazil & LatAm

**CVM** open data: issuer registrations, periodic filings (DFP/ITR), reference forms
(*formulário de referência* — governance, risk, related parties). Local-language search required.

## Generic local-registry mode

When no adapter above fits: state explicitly **what the jurisdiction discloses and what it does
not**, set expectations in §2.5, and adjust the §21.12 scorecard's expected source classes to that
reality. Absence of a disclosure regime is not a research failure — it is a documented boundary.

---

## Ownership-form branching

Applied **with** the jurisdiction adapter, not instead of it.

| Form | Financial backbone | Governance / ownership | Confidence ceiling |
|---|---|---|---|
| **Public** | Adapter's full set | Proxy + beneficial-ownership filings | — |
| **Private-VC** | Statutory accounts where filed; funding history | Cap-table reporting where public; founder control | `MEDIUM` on financial estimates |
| **Private-PE** | Statutory accounts, lender disclosures, bond covenants if debt is public | Sponsor identity, ultimate-owner chain | `MEDIUM` on financial estimates |
| **State-owned** | Annual report to the ministry/parliament; national audit office | Ministry oversight, board appointment mechanism | — |
| **Nonprofit** | Form 990 (US) or national equivalent | Board + related-party schedules | — |
| **Cooperative / mutual** | Member-facing annual report | Member governance, delegate structures | — |
| **Partnership / LLP** | Partnership accounts where filed | Partner structure | `MEDIUM` |
| **Family group** | Holding-company accounts; per-entity filings | Family holding chain, often opaque | `MEDIUM` |
| **Controlled subsidiary** | **Parent's** segment note + local statutory accounts | Parent chain via §3.6 | Attribute facts to the correct entity |

**Never force public-company fields onto a form that does not have them.** A cooperative has no
market cap, a nonprofit no EPS, an SOE no activist register. Those are `structurally-inapplicable`
(§ evidence-policy 7), not gaps, and they do not depress the coverage scorecard.

For **controlled subsidiaries** the single most common failure is attributing the parent's
financials, ratings, or litigation to the subsidiary. §3.6 exists to prevent it; every fact carries
the entity it attaches to.

---

## Regulatory register fields (§4.6 / §14.2)

Per regulation, all eleven fields or an explicit gap:

`Regulation` · `Jurisdiction` · **`Legal entity it applies to`** · `Applicability test`
(size/role/timing thresholds) · `Effective / transition dates` · `Obligation` ·
`Evidence of compliance posture` · `Enforcement authority` · `Exposure` · `Confidence` · `Source`

**Never assert "compliant"** without regulator or company evidence. "No enforcement action found"
is a negative-evidence statement with a search record, not a compliance finding.
