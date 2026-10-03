# ID Allocation Table — collision avoidance under parallel execution

> **Why this file exists.** `aid-prompt-v2.md` assumes sequential phases with an append-only
> state file, so "next free ID" is unambiguous. This harness runs up to ten agents
> concurrently with no shared runtime state, so "next free ID" is undefined and two agents
> would both mint `S-01`. ID space is therefore **partitioned in advance**. Every agent gets a
> numeric block and uses only that block.

## 1. Namespaces

| Prefix | Entity | Namespacing rule |
|--------|--------|------------------|
| `S-nnn` | Source | **Blocked** — global namespace, partitioned by agent (§2) |
| `G-nnn` | Data gap | **Blocked** — global namespace, partitioned by agent (§2) |
| `X-nnn` | Contradiction | **Blocked** — global namespace, partitioned by agent (§2) |
| `VZ-nnn` | Visual specification | **Blocked** — global namespace, partitioned by agent (§2) |
| `C-<sec>-nn` | Claim | **Section-scoped** — no block needed; sections are single-owner. Number from `01` within each section |
| `Q-nn` | Open question | **Blocked** — global namespace, partitioned by agent (§2) |
| `O-nn` | Opportunity | **Single-owner** — only `opportunity` mints these |
| `U-nn` | AI/agentic use case | **Single-owner** — only `opportunity` mints these |
| `P-nn` | Stakeholder / person | **Single-owner** — only `leadership` mints these |
| `R-nn` | Risk | **Single-owner** — only `risk-reg` mints these |
| `A-nn` | Action | **Single-owner** — only `engagement` mints these |
| `V-<CODE>` | Vertical module | Fixed vocabulary: `V-HLS`, `V-BFSI`, `V-RCG`, `V-ENR`, `V-MFG`, `V-TMT`, `V-TTH`, `V-GOV` |

> **v2.1 change.** `aid-prompt-v2.md` used `V-nn` for *both* visual specifications and vertical
> modules (`V-HLS`). That collides. Visual specs are now **`VZ-nn`**; `V-` is reserved for
> vertical modules. See `blueprint/aid-blueprint-v2.1.md` §Changelog.

## 2. Per-agent blocks

Block index `k` ⇒ the agent owns `S-`, `G-`, `X-`, `VZ-`, and `Q-` numbers in `[k·100, k·100+99]`.

| # | Agent label | Stage | Block | Sections owned | Single-owner registers |
|---|-------------|-------|-------|----------------|------------------------|
| 0 | `scoping` | 0 | 001–099 | 0.1, 0.2, 0.3 | — (pre-registers core sources `S-001`–`S-049`) |
| 1 | `corporate` | 1 | 100–199 | 2.1–2.4 | — |
| 2 | `market` | 1 | 200–299 | 3.1–3.6 | — |
| 3 | `financials` | 1 | 300–399 | 4.1–4.5 | — |
| 4 | `strategy` | 1 | 400–499 | 5.1–5.6 | — |
| 5 | `technology` | 1 | 500–599 | 6.1–6.7 | — |
| 6 | `ai-posture` | 1 | 600–699 | 7.1–7.4 | — |
| 7 | `leadership` | 1 | 700–799 | 8.1–8.4 | `P-nn` |
| 8 | `ecosystem` | 1 | 800–899 | 9.1–9.5 | — |
| 9 | `risk-reg` | 1 | 900–999 | 10.1–10.7 | `R-nn` |
| 10 | `vertical` | 1 | 1000–1099 | Appendix J + anchor injections | — |
| 11 | `source-merge` | 2 | — | — | rewrites only; mints nothing |
| 12 | `contradiction` | 2 | 1200–1299 | 0.4 (draft) | — |
| 13 | `evidence-audit` | 2 | 1300–1399 | — | — |
| 14 | `opportunity` | 3 | 1400–1499 | 11.1–11.3 | `O-nn`, `U-nn` |
| 15 | `account-strategy` | 3 | 1500–1599 | 12.1–12.5 | — |
| 16 | `engagement` | 3 | 1600–1699 | 13.1–13.5 | `A-nn` |
| 17 | `exec-brief` | 4 | 1700–1799 | 1.1–1.8, 0.4 (final), 0.6 | — |
| 18 | `qa-gate` | 5 | 1800–1899 | 0.5 (QA block) | — |
| 19 | `assembly` | 6 | — | Appendices A–L | mints nothing |

> **v2.2 change.** Sections-owned extended for the restored sub-sections: `market` +§3.6 (also a
> stale-row fix — §3.6 shipped in v2.1), `strategy` +§5.6, `technology` +§6.6 (stale-row fix)
> +§6.7, `leadership` +§8.4, `ecosystem` +§9.5 (stale-row fix), `risk-reg` +§10.6 +§10.7,
> `assembly` appendix range A–I → A–L. **Blocks are unchanged** — the same 100-number range still
> covers each agent, and no new single-owner register was introduced (litigation risks mint from
> `risk-reg`'s existing `R-nn`). Claim IDs for new sections follow the section-scoped rule
> (`C-5.6-01`, `C-6.7-01`, `C-8.4-01`, `C-10.6-01`, `C-10.7-01`, …), collision-free by construction.

### Rules

1. **Never mint an ID outside your block.** QA check F1c fails the run on any out-of-block ID.
2. **Reuse shared core sources.** `scoping` pre-registers the load-bearing documents as
   `S-001`–`S-049` (latest 10-K/annual report, latest 10-Q, DEF 14A, IR landing page, latest
   earnings release + transcript, corporate site, primary regulator page). Read
   `<RUN_DIR>/state/state.json` **before** registering anything. If the document is already
   there, cite the existing ID.
3. **Cite freely across blocks; mint only in yours.** Citing `[S-003]` from any agent is correct
   and expected. Creating `S-003` when you are not `scoping` is a defect.
4. **`exec-brief` should mint zero sources.** Tier 1 is derived from the body. If the exec-brief
   agent needs a new source, that is a signal the body is incomplete — it must record a
   `G-17nn` gap instead.
5. **`assembly` mints nothing.** It only collates and resolves. If assembly finds an unresolved
   reference, it records it in the QA appendix rather than inventing a register entry.
6. **Claim numbering.** `C-4.2-01`, `C-4.2-02`, … Restart at `01` for each section. Because
   sections are single-owner, this is collision-free by construction.
7. **Superseding a claim.** A later stage may never silently edit an earlier claim. It adds a
   new claim in its own section plus an `X-nnn` contradiction object pointing at both.

## 3. Worked example

`financials` (block 3) researching FY2025 revenue:

- Finds the 10-K already registered by `scoping` as `S-004` → cites `[S-004]`, mints nothing.
- Finds a Q3 earnings press release not yet registered → mints `S-300`.
- Finds a Reuters piece giving a different capex figure → mints `S-301`, then mints
  contradiction `X-300` with both positions and applies the recent-primary rule.
- Cannot find IT spend as % of revenue after four queries → mints gap `G-300`, resolution path
  `account-team-validation`, and open question `Q-300`.
- Emits claims `C-4.1-01` … `C-4.5-07`.
- Proposes a chart → `VZ-300 | show margin compression drivers | stacked bar + line | …`.

All IDs land in block 3 or in section-scoped claim space. No collision is possible with any
concurrent peer.
