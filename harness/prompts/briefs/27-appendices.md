# Brief 27 — `appendices` · Step P8 · Block 2700–2799 · Owns §21.2–21.7

You write the **narrative appendices**. The register appendices — §21.1 Source Manifest, §21.9 Claim
Ledger, §21.10 Account-Team Input Sheet, §21.11 gap register, §21.12 Source-Completeness Scorecard —
are generated deterministically by `assembly` from merged state, and you must not duplicate them.

Output: `sections/21-appendices.md` · fragment `state/fragments/appendices.json`.

## §21.2 Glossary

Every industry, company, and technical term or acronym used in the body, **expanded once**, with a
one-line definition in the sense the dossier uses it.

Compile from the assembled body — read the section files, extract the terms, and define them. An
acronym you cannot expand from the dossier's own sources is listed as
"expansion not established", not guessed. Company-specific programme names and internal
abbreviations matter more here than standard industry terms.

## §21.3 Detailed Financial Data Tables

`T-21.3` — P&L, balance sheet, cash flow, **as filed**, plus a **reconciliation to any adjusted
figures used in §6**.

Take the figures from `precomputed-financials` where it exists; where it does not, from
`financials`' claims. Every column carries currency, unit, period label, and basis. **You compute
nothing new** — a derived figure that did not appear in §6 does not belong here.

The reconciliation is the point: a reader who sees an adjusted EBITDA in §6.1 should be able to walk
from the statutory figure to it here, line by line.

## §21.4 News & Events Timeline

`T-21.4`. 12–24 months of significant, dated, cited events, assembled from the dated claims in §9,
§13, §14, and §17. Chronological. Each row: date · event · category · source.

Do not research new events — you are collating what the body established. An event with no claim
behind it does not go in.

## §21.5 Job-Posting Intelligence

`T-21.5`. The detail behind §13.3, from `signals`' handoff: role and skill breakdown by function and
geography, **with the posting window stated**, and **the mention classification on every technology
named**.

Opt — rendered only where `signals` actually researched postings. Where it did not, say so in one
line rather than omitting the heading.

## §21.6 Patent, Trademark & Open-Source Analysis

Patent filing trend and technology domains (PatentsView, EPO OPS, Google Patents), trademark
activity (USPTO TSDR, WIPO/EUIPO), and public-repository and OSS posture (GitHub/GitLab org
activity).

**Attribution is the trap.** Patents and repos attach to specific legal entities and specific org
accounts — verify against §3.6 before attributing them. A subsidiary's patent portfolio is not the
group's, and a similarly-named GitHub org is a common false positive.

Opt. Where you research it, this is one of the few places genuine forward-looking technical
direction is publicly visible, so it is worth the budget on a technology-heavy target.

## §21.7 Digital Presence Audit

Traffic (**named source and method** — Similarweb and equivalents are licensed, modelled estimates;
check quoting terms and never present a modelled figure as measured), social presence, and thought
leadership.

Opt. `customers`' §12.3 and §12.5 handoffs are your input.

## Rules that apply to everything you write

- **You are collating, not researching.** Your block exists for the few sources §21.6 and §21.7
  genuinely require. If you find yourself researching the body, stop — the finding belongs to the
  owning section, and it is too late for it to be integrated.
- **Every table carries its data-as-of.** Appendices are the most-quoted and least-dated part of a
  dossier.
- **Opt sections are honest about being empty.** "Not researched — outside the STANDARD tier scope"
  and "researched; no material patent activity identified (PatentsView, assignee search on 3
  entity variants, 2020–2026)" are both fine. An absent heading is not.

## Fragment

Claims `C-21.6-nn`, `C-21.7-nn` only where you established something new in those two subsections.
Sources `S-27nn`. Gaps `G-27nn`. Coverage entries for §21.5–21.7. `handoff` to `verification` if you
found an inconsistency between §6 and the as-filed statements while building §21.3 — that is a V2
finding and it is better caught here than not at all.
