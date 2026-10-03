# Evidence Policy v3.0.0 — status, confidence, corroboration, classification

> The operational expansion of §3–§4 of `prompts/system-vantage-analyst.md`. Every agent applies this;
> `evidence-audit` and `verification` grade against it. Where this file and a brief disagree, this
> file wins.

---

## 1. The evidence-status enum

Exactly one status per material non-financial assertion. This is a **claim about what the evidence
establishes**, not about how likely the claim is to be true.

| Status | Establishes | Typical evidence | Never means |
|---|---|---|---|
| `CONFIRMED` | The fact, from governing or independent evidence | Filing, regulator record, ≥2 independent direct sources | "the company said so" |
| `ANNOUNCED` | That an intent was **stated** | Company press release, earnings call, investor day | that it happened, shipped, or succeeded |
| `OBSERVED-SIGNAL` | That a **signal** exists | Job postings, hiring patterns, TLS certs, DNS, app SDKs, review presence, conference talks | that the underlying system/process/outcome exists |
| `INFERRED` | Your reasoning from other claims | Synthesis across ≥2 cited claims, with the trail shown | evidence |
| `UNKNOWN` | You searched and did not establish it | Negative-evidence record | "does not exist" |

### Status transitions are one-way and explicit

`ANNOUNCED` → `CONFIRMED` requires **independent** evidence of the outcome, not a follow-up press
release. `OBSERVED-SIGNAL` → `CONFIRMED` requires corroboration from a different evidence class.
An agent may never promote a status it did not itself re-evidence, and a downstream agent may never
promote one at all — it cites the status it was given.

**The single most common failure this prevents:** a §9.2 transformation program marked ANNOUNCED
becomes an §18 opportunity's need evidence, then a §19.4 message, then a §20.6 action, then a §1.2
finding — arriving at the executive as a fact. `evidence-audit` exists to break that chain before
§18.

## 2. Claim-sensitive source rules

There is no blanket "primary source wins." The governing source depends on the claim type.

| Claim type | Governing source | A company statement proves |
|---|---|---|
| Filed financials | The filing (10-K / annual report / XBRL) | nothing extra |
| Enforcement, litigation, sanction | Regulator or court record | nothing extra |
| Announced intent (program, partnership, M&A) | The company's official announcement | that it was **announced** |
| Outcome, market share, claimed savings, implementation status, customer success, reputation | **Independent** source required | only that the company made the claim |
| Executive quote | Official transcript / webcast > third-party transcription > machine transcription | — |
| Credit rating | The agency's own action release (rated entity + instrument + seniority) | nothing |
| Technology in use | Corroborated across ≥2 evidence classes | a preference, not an installation |
| Headcount, attrition | Filing human-capital disclosure > company report > vendor estimate | — |
| Ownership | Proxy tables, 13D/G (beneficial), Forms 3/4/5 (insider). **13F = holdings OF a manager** | — |

## 3. Corroboration rule

| Claim class | Requirement | Ceiling if unmet |
|---|---|---|
| Filed financial fact | One governing filing | — |
| Consequential non-financial claim — vendor relationships, program status/budgets, AI deployments, ESG outcomes | One authoritative source **plus one independent corroborator** | `MEDIUM`, and the evidence status is tagged down accordingly |
| Weak-signal claim | ≥2 signals of **different classes**, or explicit `OBSERVED-SIGNAL` framing | `LOW` |
| Snippet-only (no fetch) | Not permitted for a load-bearing fact | `LOW` + `[SNIPPET-ONLY]` |

**Independence test.** Two outlets running the same wire story are **one** source. A vendor case
study and the vendor's press release are **one** source. A company's 10-K and its own investor deck
are **one** source for a self-reported outcome. Collapsing these is exactly what `source-merge`
detects and what makes false triangulation the signature failure of a parallel harness.

## 4. The six confidence dimensions

Score each, then take the composite. Record the dimensions in the claim-ledger entry so the
Verification Pass can re-derive the composite rather than trusting it.

| Dimension | Values | Notes |
|---|---|---|
| `authority` | `high` / `medium` / `low` | The publisher's standing for **this** claim type |
| `independence` | `governing` / `independent` / `self-reported` | A press release is `self-reported` even though it is primary |
| `directness` | `primary` / `secondary` / `commentary` | Did you read the record, or someone's description of it? |
| `corroboration` | integer count of **independent** sources | After the independence test above |
| `recency` | `current` / `aging` / `stale` | Relative to the claim type — see §5 |
| `entity_match` | `certain` / `probable` / `ambiguous` | Against the §3.6 entity map |

**Composite:**

| Composite | Test |
|---|---|
| `HIGH` | (`independence` = `governing` **and** `directness` = `primary`) **or** `corroboration` ≥ 2 with `independence` ≠ `self-reported`; **and** `entity_match` = `certain`; **and** `recency` ≠ `stale` |
| `MEDIUM` | One reputable direct source; **or** a triangulated estimate from disclosed data; **or** `independence` = `self-reported` from an authoritative party |
| `LOW` | `directness` = `commentary`, `[SNIPPET-ONLY]`, weak signals only, `entity_match` = `ambiguous`, or `recency` = `stale` |

Two hard consequences:

1. **A self-promotional primary source is never automatically HIGH.** A marketing case study is
   `authority: medium`, `independence: self-reported`, `directness: primary` → `MEDIUM` at best.
2. **A `LOW` claim never anchors a recommendation alone.** An `O-nn` whose only need evidence is a
   `LOW` claim must be status `HYPOTHESIS` and must appear in the §19.9 validation actions.

## 5. Temporal policy — staleness is claim-relative

| Claim class | Current | Aging | Stale |
|---|---|---|---|
| Current-state operational (stack, org, program status, headcount) | ≤ 12 mo | 12–24 mo | > 24 mo → `[STALE — as of <date>]` |
| Financial period data | Latest reported period | Prior period | Superseded by a restatement |
| Market sizing / share | ≤ 24 mo | 24–36 mo | > 36 mo |
| Leadership identity | ≤ 6 mo | 6–12 mo | > 12 mo without re-check |
| Stable historical fact (founding, completed M&A, historical financials) | **never stale** | — | — |
| Ratings, sanctions, litigation status | ≤ 6 mo | 6–12 mo | > 12 mo |

"Recent" without a date is a defect (V2). Every `##` section carries an as-of footer; every
material table carries its own data-as-of.

## 6. Technology mention classification

Every entry in `T-8.1.1`, `T-8.1.2`, `T-16.1` and every technology named in §13.3 carries one:

| Class | Signal | May reach CONFIRMED? |
|---|---|---|
| `CURRENTLY-USED` | Named in a filing, an exec statement, a joint customer announcement, or a corroborated case study | Yes |
| `MIGRATING-TO` | Announced migration, RFP, or hiring explicitly framed as a transition | Only with the announcement fetched |
| `EVALUATING` | Pilot language, POC references, "assessing" | No — `ANNOUNCED` at best |
| `SKILL-PREFERENCE` | The technology appears only in job-posting requirements | No — `OBSERVED-SIGNAL` |
| `AMBIGUOUS` | Signal exists but attribution or currency is unclear | No |

**A job posting is a hiring signal, not a stack fact.** A G2 review, a TLS certificate, a CNAME,
or an app SDK is not a tenancy proof — shared infrastructure and CDNs produce false positives, and
entity attribution must be verified before the row is written at all.

## 7. Negative evidence

`UNKNOWN` is a research product with a required shape. A gap object without the search record is
itself a defect (V3).

```json
{
  "id": "G-0512",
  "item": "IT spend as % of revenue",
  "section": "6.6",
  "searched": ["10-K Item 7 MD&A", "FY2025 investor day deck", "last 4 earnings transcripts",
               "trade press 2024-2026"],
  "queries_tried": ["\"<target>\" IT spend percentage revenue",
                    "\"<target>\" technology budget 2025",
                    "\"<target>\" CIO investment disclosure"],
  "languages": ["en"],
  "date_range": "2023-01..2026-08",
  "best_available": "Total SG&A only; no technology line disclosed",
  "resolution_path": "account-team-validation",
  "materiality": "high"
}
```

`resolution_path` ∈ `account-team-validation` · `retry-later` · `paid-source-required` ·
`accept-unknown` · `structurally-inapplicable`.

**`structurally-inapplicable` is not a gap.** A private company has no market cap; a nonprofit has
no share classes. Mark the field inapplicable with the ownership-form reason — do not gap it, and
do not let it depress the coverage scorecard.

## 8. Retrieval status

Every Source Manifest entry carries one. Failures are recorded, never dropped.

| Status | Meaning | Required follow-up |
|---|---|---|
| `ok` | Fetched and read | — |
| `partial` | Fetched, but the needed section was truncated or unparseable | Name what was missing |
| `paywall` | Blocked by a paywall | Name the alternative source attempted |
| `blocked` | robots/ToS/403 | **Do not circumvent.** Name the alternative |
| `dead` | 404 / moved | Try the Wayback snapshot; record which |
| `parse_error` | Fetched but unreadable (broken PDF, scanned image) | Name the alternative |
| `not_attempted` | Known to exist, out of budget | Record in §21.12 with `stop_reason: budget` |

A load-bearing fact may not rest on a source whose retrieval status is anything but `ok` or
`partial` (with the pinpoint verified).

## 9. Quote fidelity

A quote in the dossier carries: verbatim text, speaker, role at the time, event, date, and
**transcript provenance class** — `official` (company transcript/webcast) · `third-party`
(Motley Fool, Seeking Alpha, media transcription) · `machine` (auto-caption or machine
translation).

For non-English sources: search in the local language **and** English, record
`language` on the manifest entry, and keep the original-language excerpt for any consequential
claim. **Machine-translated text is never presented as a verbatim English quote.**

## 10. Privacy boundary for people

Executive and stakeholder content is **public professional facts and attributed statements only**.

Permitted: role, tenure, prior roles, public statements with citation, conference appearances,
disclosed compensation from the proxy, board memberships.

Forbidden: inferred personality or working style, family or personal circumstances, health,
political or religious affiliation, unverified social-media attribution, and **any loyalty claim**.
Prior-vendor employment may be recorded as a weak `OBSERVED-SIGNAL` hypothesis with the phrase
"prior employment at X (OBSERVED-SIGNAL; no inference of preference)" — never as a predisposition.

Aggregate workforce data (§10.7) is aggregate only. No individual attrition, performance, or
compensation outside the proxy's named-executive disclosure.

## 11. Numeric integrity

1. Where `precomputed-financials` is attached it is **the numeric source of truth**. Reconcile the
   filing against it; where they differ, report the discrepancy — **do not silently re-derive**.
2. Where absent, every derived number recomputes from stated inputs, and the inputs are shown.
3. Segment tables **foot to the reported total** (± rounding, noted). A segment table that does not
   foot is a V2 failure.
4. Currency and unit in every table header. FX rates and the fiscal-year mapping are shown, never
   applied silently.
5. Adjusted vs statutory is labeled per column. Vendor-normalized and as-filed data never share an
   unlabeled table.
6. Accounting basis, restatements, continuing vs discontinued operations, 53-week years, ADR
   ratios, share-class aggregation, splits, and material pension/lease effects are stated where
   they affect a number in the dossier.
7. For banks / insurers / REITs, sector metrics (NIM, combined ratio, FFO, book value per share)
   replace DuPont/EBITDA framing; forcing the general framework is `NOT RELIABLY ASSESSABLE`.

## 12. What may never be estimated

| Never estimated | Instead |
|---|---|
| A contract value not disclosed | `[DATA UNAVAILABLE]` + gap |
| A contract expiry or renewal date not evidenced | Record the *evidenced* signal and the window it implies, with confidence |
| A litigation exposure figure not disclosed | Record the matter without a number |
| Budget ownership or approval authority | `INFERRED` with the trail, never a stated fact |
| NPS / CSAT | Only published, standardized figures (ACSI etc.), with method |
| An organization reference, client name, or quantified outcome | `[INTERNAL: validate with practice]` |
| Win probability, account revenue, relationship strength, stakeholder access | `[INTERNAL REQUIRED]` |

Market sizing, IT spend, and opportunity sizing **may** be estimated — with `[ESTIMATED]`, the
model, the inputs, and a range.
