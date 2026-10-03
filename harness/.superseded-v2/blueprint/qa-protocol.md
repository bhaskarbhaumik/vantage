# QA Protocol — executable gate

> Base: `prompts/aid-prompt-v2.md` Deliverable F (F1–F9), restated as a *runnable* checklist.
> **F10 is new in v2.1** and covers integrity failures that only exist under parallel execution.
> Executed by the `qa-gate` agent. Results summarised in §0.5 and written in full to
> `<RUN_DIR>/qa/qa-report.md`.

## Operating rules

1. **Any FAIL that cannot be remediated is disclosed in §0.5, never masked.** A dossier that
   ships with three disclosed failures is more useful than one that hides them.
2. **Severity.** `BLOCKER` — do not deliver. `MAJOR` — deliver with the failure stated in §0.5.
   `MINOR` — deliver, log in the QA report only.
3. **Method column.** `auto` = mechanically checkable against the registers or by string search;
   `read` = requires reading the rendered section. Run every `auto` check first; they are cheap
   and catch most defects.
4. **On BLOCKER:** attempt one targeted remediation (re-research a single claim, fix an ID, drop
   an unsupported sentence). If it still fails, downgrade the affected content — convert the
   claim to a gap, suppress the score, cut the Tier 1 line — and record the downgrade.

---

## F1 — Traceability

| # | Check | Method | Sev |
|---|-------|--------|-----|
| F1a | Every material claim in the body has a claim ID and ≥1 resolvable source ID | auto | BLOCKER |
| F1b | Every inline `[S-nnn]`, `[C-…]`, `[O-nn]`, `[P-nn]`, `[R-nn]`, `[A-nn]`, `[U-nn]`, `[G-nnn]`, `[VZ-nnn]` resolves to a register entry | auto | BLOCKER |
| F1c | Every minted ID falls inside its agent's allocated block per `prompts/id-allocation.md` | auto | MAJOR |
| F1d | No source lacks an `accessed` date | auto | MAJOR |
| F1e | No database (Bloomberg, Capital IQ, Refinitiv, PitchBook, Gartner subscription content) is cited by name unless its source row carries `access_basis: direct` | auto | BLOCKER |
| F1f | Every `[TRIANGULATED]` claim lists ≥2 **independent** sources — two articles syndicating one wire story are one source | read | MAJOR |
| F1g | No orphan register entries: every `S-nnn` in Appendix A is cited at least once in the body | auto | MINOR |

## F2 — Precision & numbers

| # | Check | Method | Sev |
|---|-------|--------|-----|
| F2a | No unsupported precision. Every `[ESTIMATE]` is a **range** with a stated method | read | MAJOR |
| F2b | Every figure carries period, currency + units, source, and basis (`reported`/`calculated`/`estimated`) | read | MAJOR |
| F2c | Derived figures show their calculation | read | MAJOR |
| F2d | Segment revenues reconcile to total (reconciling items noted); growth rates match the underlying figures shown; capital allocation reconciles to FCF | read | BLOCKER |
| F2e | Fiscal periods labelled explicitly on first use; no bare `FY0`/`FY-1` | auto | MAJOR |
| F2f | The §0.5 freshness map matches the `recency`/`stale` metadata in the claim register | auto | MINOR |

## F3 — Evidence integrity

| # | Check | Method | Sev |
|---|-------|--------|-----|
| F3a | No `[FACT]` rests solely on a Tier 4–5 source | auto | BLOCKER |
| F3b | Every `[INFERENCE]` carries a stated basis | read | MAJOR |
| F3c | No `[UNVERIFIED]` claim supports a score dimension or appears in Tier 1 | auto | BLOCKER |
| F3d | Every open contradiction appears in §0.4; every resolved one names its resolution rule | auto | MAJOR |
| F3e | Stale-but-material evidence is flagged `[stale]` where used | auto | MINOR |
| F3f | Every claim the `evidence-audit` agent marked `refuted` has been downgraded, converted to a gap, or removed — **none survives as `[FACT]`** | auto | BLOCKER |

## F4 — People, vendors, contracts

| # | Check | Method | Sev |
|---|-------|--------|-----|
| F4a | Every named person is sourced and as-of dated | auto | BLOCKER |
| F4b | No personality profiling, communication-style inference, or private-circumstance speculation about any named individual | read | BLOCKER |
| F4c | Vendor/SI relationship claims carry signal recency | read | MAJOR |
| F4d | Contract values and expiry dates appear **only** if disclosed — never estimated, never inferred from engagement start plus a typical term | auto | BLOCKER |
| F4e | the pursuing organization relationship/reference content derives only from `ACCOUNT_CONTEXT` / `KNOWN_RELATIONSHIP_CONTEXT`; sections say "input not provided" otherwise | read | BLOCKER |

## F5 — Structure & density

| # | Check | Method | Sev |
|---|-------|--------|-----|
| F5a | Duplication scan — stakeholders, regulatory, partnerships, SWOT, and opportunities each analysed **once**; elsewhere by cross-reference only | read | MAJOR |
| F5b | Every major section opens with a confidence-tagged verdict | auto | MAJOR |
| F5c | No decorative placeholders, no empty tables, no ASCII boxes anywhere | auto | MAJOR |
| F5d | Conditional sections match their triggers (Pub/Priv/`V-*`/Opt/Input); non-triggered sections absent; triggered-but-empty sections show a one-line gap | read | MAJOR |
| F5e | No section exceeds 1.5× its `section-contracts.md` envelope — overrun usually means it absorbed a neighbour's scope | auto | MINOR |
| F5f | Frameworks used only where data supports them; a one-line waiver is present wherever one was skipped | read | MINOR |
| F5g | Every section listed in `section-contracts.md` as Core is present, or explicitly marked unavailable with a reason | auto | BLOCKER |

## F6 — Scoring

| # | Check | Method | Sev |
|---|-------|--------|-----|
| F6a | Every scored dimension carries: score + anchor met + claim IDs + confidence | auto | BLOCKER |
| F6b | Composite suppressed wherever ≥2 dimensions are Low confidence | auto | BLOCKER |
| F6c | Weights sum to 100% after any reweighting for `n/e` dimensions, and the reweighting is shown | auto | MAJOR |
| F6d | Appendix G numbers match the numbers rendered in the body | auto | MAJOR |
| F6e | Interpretation bands and the "decision aid, not a measurement" framing are present on every scorecard | auto | MAJOR |
| F6f | Model 7's inverted polarity (higher = worse) is stated on its render | auto | MINOR |
| F6g | Model 8 in §9.4 reports the four-dimension partial only; differentiation is deferred to §12.4 | read | MAJOR |

## F7 — Strategy discipline

| # | Check | Method | Sev |
|---|-------|--------|-----|
| F7a | **Tier 2 is vendor-neutral.** Search §2–§10 for the pursuing organization’s name/branding from account context and positioning verbs (`we can`, `our offering`, `partner of choice`, `well-positioned`). Only single-line neutral relevance flags are permitted | auto | BLOCKER |
| F7b | No Tier 2 section cites an `O-nn` or `A-nn` — those do not exist when Tier 2 is written | auto | MAJOR |
| F7c | Every `O-nn` cites need-evidence claims and carries `CONFIRMED`/`HYPOTHESIS`/`VALIDATE` status | auto | BLOCKER |
| F7d | Every recommendation names stakeholder, value narrative, entry vehicle, proof required, likely objection, next action | read | MAJOR |
| F7e | §13.4 backlog covers every `HYPOTHESIS`/`VALIDATE` item **and** every `materiality: high` gap | auto | MAJOR |
| F7f | §13.6 kill criteria name ≥3 triggers, each with an observable signal and a source to monitor | auto | MAJOR |

## F8 — Executive brief

| # | Check | Method | Sev |
|---|-------|--------|-----|
| F8a | Every Tier 1 statement traces to a body ID. **A Tier 1 sentence with no ID is a failure** | auto | BLOCKER |
| F8b | Nothing appears in Tier 1 that is not in the body | read | BLOCKER |
| F8c | Tier 1 confidence labels match the confidence of the underlying claims | auto | MAJOR |
| F8d | The §1.1 account thesis is consistent with the §1.6 readiness band — a *Monitor* band under a "pursue aggressively" thesis is a contradiction | read | BLOCKER |
| F8e | §1.7 actions are specific, sequenced, owner-role-assigned, dated, and metric-bearing | read | MAJOR |
| F8f | §1.8 lists the top 3 `materiality: high` gaps, or explicitly states there are none | auto | MAJOR |
| F8g | `exec-brief` minted zero new sources | auto | MAJOR |

## F9 — Completeness

| # | Check | Method | Sev |
|---|-------|--------|-----|
| F9a | Appendices A, B, F, G, H are populated | auto | BLOCKER |
| F9b | Final `state.json` is internally consistent — every ID referenced exists, no duplicates | auto | BLOCKER |
| F9c | §0.6 Reader's Map covers all four audiences | auto | MINOR |
| F9d | Appendix K lists every `VZ-nnn` emitted anywhere in the body | auto | MINOR |
| F9e | Output is Markdown only — no HTML, no CSS, no inline styling, no image embeds | auto | MAJOR |
| F9f | Appendix L (Glossary) is present and every acronym in it is compiled from the body — no researched/guessed expansions (`+v2.2`) | auto | MINOR |
| F9g | The `+v2.2` Core sub-sections (§5.6, §6.7, §8.4, §10.6, §10.7) are each present or rendered as a one-line gap per their evidence bar; none silently absent (`+v2.2`) | auto | MAJOR |

## F10 — Parallel-execution integrity `NEW v2.1`

These failures cannot occur in a sequential pipeline and are therefore absent from v2.0's
Deliverable F. They are the most likely defects in this harness.

| # | Check | Method | Sev |
|---|-------|--------|-----|
| F10a | **Single ownership** — no section number appears in two agents' `sections_owned` lists | auto | BLOCKER |
| F10b | **No ID collision** — no `S-`/`G-`/`X-`/`Q-`/`VZ-` ID minted by two agents; no duplicate ID in the merged register | auto | BLOCKER |
| F10c | **Source dedup applied** — no two `S-nnn` entries point at the same URL or the same document. `source-merge`'s rewrite map has been applied to every section file | auto | MAJOR |
| F10d | **Shared-core reuse** — no agent re-registered a document already present as `S-001`–`S-049` | auto | MAJOR |
| F10e | **Fragment completeness** — every Stage-1 agent produced both a section file and a state fragment. A missing fragment means silent data loss, not a clean skip | auto | BLOCKER |
| F10f | **Canonical fact agreement** — where two agents proposed the same `canonical_facts` key, the values agree, or an `X-nnn` contradiction exists. Two agents reporting different revenue figures is the signature failure of this architecture | auto | BLOCKER |
| F10g | **Cross-agent references resolve** — every `see §x.y` written by one agent points at a section another agent actually produced | auto | MAJOR |
| F10h | **Digest/section agreement** — no agent's returned digest claims coverage its section file does not contain | read | MINOR |

---

## Report format

`<RUN_DIR>/qa/qa-report.md`:

```markdown
# QA Report — {{CLIENT}} AID, {{RESEARCH_AS_OF}}

**Result:** PASS WITH DISCLOSURES · 3 MAJOR, 5 MINOR, 0 BLOCKER
**Evidence Quality Index:** 68 / 100 (Adequate)

## Failures

| Check | Sev | Detail | Remediation | Final state |
|-------|-----|--------|-------------|-------------|
| F2a | MAJOR | §4.4 IT-spend estimate given as a point value | Converted to range $180–240M, method stated | Fixed |
| F10c | MAJOR | S-208 and S-411 both = Reuters 2026-03-04 | Rewrite map applied, S-411 retired | Fixed |
| F1f | MAJOR | C-3.2-04 tagged TRIANGULATED on two syndications of one wire story | Downgraded to FACT, single source | Fixed |
| F5e | MINOR | §6.6 ran 780 w against a 500 w envelope | Accepted — sourcing detail is load-bearing for §12.5 | Accepted |

## Checks passed: 47 / 51
## Disclosed in §0.5: F5e (accepted overrun)
```

The §0.5 QA block carries the headline result, the EQI, and every unremediated failure. Nothing
else from this report needs to reach the reader.
