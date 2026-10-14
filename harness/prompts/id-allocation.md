# ID Allocation Table v3.0.0 — collision avoidance under parallel execution

> **Why this file exists.** `aid-20260829.md` assumes sequential phases with an append-only handoff
> file, so "next free ID" is unambiguous. This harness runs up to **ten agents concurrently** with
> no shared runtime state, so "next free ID" is undefined and every one of them would mint `S1`.
> ID space is therefore **partitioned in advance**. Every agent gets a numeric block and uses only
> that block.

## 1. Namespaces

| Prefix | Entity | Namespacing rule |
|---|---|---|
| `S-nnnn` | Source (Source Manifest, §21.1) | **Blocked** — global namespace, partitioned by agent (§2) |
| `G-nnnn` | Data gap (§21.11) | **Blocked** |
| `X-nnnn` | Contradiction (§21.11) | **Blocked** |
| `Q-nnnn` | Validation question (§19.9, §20) | **Blocked** |
| `C-<sec>-nn` | Claim (Claim Ledger, §21.9) | **Section-scoped** — no block needed; sections are single-owner. Number from `01` within each section |
| `O-nn` | Opportunity | **Single-owner** — only `opportunity` mints these |
| `U-nn` | AI / agentic use case | **Single-owner** — only `ai-readiness` mints these |
| `P-nn` | Stakeholder / person | **Single-owner** — only `leadership` mints these |
| `R-nn` | Risk | **Single-owner** — only `risk` mints these |
| `A-nn` | Action | **Single-owner** — only `playbook` mints these |
| `C-<sec>.<n>` | Chart (`chart-data` block) | **Section-scoped**, from the owning section number |
| `F-<sec>.<n>` | Figure (`figure-spec` block) | **Section-scoped** |
| `T-<sec>[.<n>]` | Table | **Section-scoped** |
| `V-<CODE>` | Vertical module | Fixed vocabulary — see `blueprint/vertical-modules.md` |

> **v3 change from v2.2.** `VZ-nnn` visual specs are retired. Charts and figures are now inline
> `chart-data` / `figure-spec` blocks (system prompt §9) with section-scoped IDs, so they need no
> global block. Sources widen from `S-nnn` to `S-nnnn` because the manifest now records *every*
> source consulted, including failed retrievals.
>
> Note that `C-` is deliberately overloaded — `C-6.1-01` (claim, three parts) versus `C-6.2.1`
> (chart, dotted). They never collide: a claim ID always contains a hyphen before its final number.

## 2. Per-agent blocks

Block index `k` ⇒ the agent owns `S-`, `G-`, `X-`, and `Q-` numbers in `[k·100, k·100+99]`.

| # | Agent | Step | Block | Sections owned | Single-owner registers |
|---|---|---|---|---|---|
| 0 | `preflight` | P0 | 0000–0099 | §0 | — (pre-registers the backbone as `S-0001`–`S-0049`) |
| 1 | `backbone` | P1 | 0100–0199 | — (evidence records + `precomputed-financials`) | — |
| 2 | `corporate` | P2 | 0200–0299 | §3 | — |
| 3 | `market` | P2 | 0300–0399 | §4 | — |
| 4 | `business-model` | P2 | 0400–0499 | §5 | — |
| 5 | `financials` | P2 | 0500–0599 | §6 | — |
| 6 | `technology` | P2 | 0600–0699 | §8 | — |
| 7 | `strategy` | P2 | 0700–0799 | §9 | — |
| 8 | `leadership` | P2 | 0800–0899 | §10 | `P-nn` |
| 9 | `signals` | P2 | 0900–0999 | §13 | — |
| 10 | `risk` | P2 | 1000–1099 | §14 | `R-nn` |
| 11 | `esg` | P2 | 1100–1199 | §17 | — |
| 12 | `operations` | P3 | 1200–1299 | §7 | — |
| 13 | `competition` | P3 | 1300–1399 | §11 | — |
| 14 | `customers` | P3 | 1400–1499 | §12 | — |
| 15 | `ai-readiness` | P3 | 1500–1599 | §15 | `U-nn` |
| 16 | `vendors` | P3 | 1600–1699 | §16 | — |
| 17 | `vertical` | P3 | 1700–1799 | Vertical packets + §21 vertical annex | — |
| 18 | `source-merge` | P4 | — | — | rewrites only; **mints nothing** |
| 19 | `contradiction` | P4 | 1900–1999 | §21.11 (draft) | `X-nnnn` |
| 20 | `evidence-audit` | P4 | 2000–2099 | — | — |
| 21 | `opportunity` | P5 | 2100–2199 | §18 | `O-nn` |
| 22 | `account-strategy` | P5 | 2200–2299 | §19 | — |
| 23 | `playbook` | P5 | 2300–2399 | §20 | `A-nn` |
| 24 | `exec-brief` | P6 | 2400–2499 | §1 | — |
| 25 | `methodology` | P6 | 2500–2599 | §2 | — |
| 26 | `verification` | P7 | 2600–2699 | §21.8 Verification Summary | — |
| 26a | `remediation-router` | P7R | — | — (work orders: `qa/remediation-orders.r<n>.json`) | **mints nothing** |
| 27 | `appendices` | P8 | 2700–2799 | §21.2–21.7 | — |
| 28 | `assembly` | P8 | — | Title metadata + final document | **mints nothing** |

## 3. Rules

1. **Never mint an ID outside your block.** Verification check **V1c** fails the run on any
   out-of-block ID.

2. **Reuse the backbone.** `preflight` and `backbone` pre-register the load-bearing documents as
   `S-0001`–`S-0049`: the adapter's annual report, latest interim, proxy/governance filing, the
   last 2–4 earnings transcripts, the IR deck, the corporate site, the primary regulator page, and
   the sustainability report. **Read `<RUN_DIR>/state/state.json` before registering anything.** If
   the document is already there, cite the existing ID.

3. **Cite freely across blocks; mint only in yours.** Citing `[S-0042]` from any agent is correct
   and expected. *Creating* `S-0042` when you are not its owner is a defect.

4. **Claim numbering** restarts at `01` for each section: `C-6.2-01`, `C-6.2-02`, … Because sections
   are single-owner, this is collision-free by construction.

5. **`exec-brief` and `methodology` should mint zero sources.** §1 and §2 are derived from the body.
   If either needs a new source, that is a signal the body is incomplete — record a `G-24nn` /
   `G-25nn` gap instead.

6. **`assembly` mints nothing.** It collates and resolves. An unresolved reference is **recorded in
   §21.8**, never invented into existence.

7. **Superseding a claim.** A later stage may never silently edit an earlier claim. It adds a new
   claim in its own section **plus** an `X-nnnn` contradiction object pointing at both.

8. **Remediation passes (P7R) reuse the owner's block.** An agent re-dispatched to fix its own
   section mints only in its own block, continues its own numbering (never reuses an ID), and
   supersedes rather than edits (rule 7). A re-run of `verification` uses block 2600–2699 again
   and continues after the highest ID the first pass minted.

9. **Locators are not IDs.** `[S-0301 §Item 1A]` cites source `S-0301` with a pinpoint. The pinpoint
   is free text; the ID must exist in the manifest.

## 4. Worked example

`financials` (block 5) researching FY2025 revenue:

- The 10-K is already registered by `backbone` as `S-0004` → cites `[S-0004 §Item 8]`, mints nothing.
- Finds a Q3 earnings release not yet registered → mints `S-0500` with
  `retrieval_status: "ok"`, `tier: 1`, `provenance_class: "official"`.
- Finds a paywalled analyst note → mints `S-0501` with `retrieval_status: "paywall"` and records
  the alternative attempted. **The source stays in the manifest** — a failed retrieval is evidence
  about coverage.
- Finds a Reuters piece giving a different capex figure → mints `S-0502`, then hands the conflict
  to `contradiction` via `handoff` rather than minting an `X-` outside its block.
- Cannot find IT spend as % of revenue after four queries → mints `G-0503` with the full search
  record, resolution path `account-team-validation`, and question `Q-0503`.
- Emits claims `C-6.1-01` … `C-6.10-04`, chart `C-6.2.1`, table `T-6.3`.
- Reconciles every figure against the `precomputed-financials` block; the one discrepancy it finds
  goes into `handoff` for `contradiction`, not into a silent correction.

All IDs land in block 5 or in section-scoped space. No collision is possible with any concurrent
peer.
