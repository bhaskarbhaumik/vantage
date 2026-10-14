# Vantage v3.0.0 Harness — Architecture

## What this is

A Claude Code agent harness that produces a Vantage dossier (*Verified Account Navigator: Targeting, Analysis & GTM Engine*) as Markdown. It runs
**29 agents across 12 steps**, with up to **ten working concurrently**, implementing
`vantage-20260829.md` (Vantage Prompt Package v3.0.0). It runs on your Claude subscription through the
Workflow tool — **no Anthropic API key, no SDK, no billing integration** — and the same agent
roster runs through five programmatic backends when you want one.

Output is Markdown and nothing else. Charts and figures are emitted as `chart-data` and
`figure-spec` blocks (schema v1), which a downstream renderer validates and draws without
re-reading the dossier.

## Lineage

| Artefact | Role here |
|---|---|
| `vantage-20260829.md` v3.0.0 | **The source of truth.** Its SYSTEM block is the constitution; its 22-section structure is the blueprint; its Verification Pass is the gate. |
| `vantage-tools-20260829.md` v2.0.0 | The tooling catalog, condensed into `blueprint/tooling-map.md` as a section→evidence map. |
| `vantage-ug-20260829.md` v1.0.0 | Access and key inventory. Path B (this harness) is the zero-config default it recommends. |

## The execution graph

```
P0  preflight                                          (1 agent, hard gate)
      │  §0 run contract: entity · ownership form · jurisdiction adapters ·
      │  reporting standard · verticals · tier · budgets; backbone S-0001..S-0049
      ▼
P1  backbone                                           (1 agent)
      │  fetch + normalize primary sources; precomputed-financials from XBRL;
      │  expected source classes per section
      ▼
P2  corporate  market  business-model  financials      (10 agents, concurrent)
    technology strategy leadership signals risk esg      §3 §4 §5 §6 §8 §9 §10 §13 §14 §17
      ▼
P3  operations competition customers                   (5–6 agents, concurrent)
    ai-readiness vendors [vertical]                      §7 §11 §12 §15 §16
      ▼
P4a source-merge                                       (deterministic)
      │  dedupe manifest, rewrite retired IDs, report false triangulation
P4b contradiction        evidence-audit                (2 agents, concurrent)
      │                     │  adversarial: tries to REFUTE every high-materiality claim
      ▼                     ▼
P5a opportunity                                        (1 agent, alone — mints O-nn)
P5b account-strategy     playbook                      (2 agents, concurrent)
      ▼
P6  exec-brief           methodology                   (2 agents — §1 derived last, §2)
      ▼
P7  verification                                       (1 agent, FRESH CONTEXT — V1..V12)
      ▼  only if BLOCKERs, up to remediation_rounds (default 1)
P7R remediation-router → owners rewrite their own      (registers → body → §18 → §19/§20 → §1/§2,
    sections → re-merge → verification (fresh)          each tier concurrent; see decision 7)
      ▼
P8a appendices                                         (§21.2–21.7)
P8b assembly                                           (deterministic — §21.1/9/10/11/12 + final doc)
```

`FULL_ANNEX` and `STANDARD` run the full roster. `EXECUTIVE` runs six Wave-A agents, skips Wave B
entirely, and drives §1 from that.

### Phase mapping — a deliberate deviation, and why

`vantage-20260829.md` specifies eight sequential phases. This harness maps them onto twelve steps:

| Spec phase | Harness step |
|---|---|
| 0 Preflight | **P0** |
| 1 Backbone | **P1** |
| 2 Corporate + Financial (§3–§6) | **P2** Wave A |
| 3 Ops + Technology (§7, §8) | §8 in **P2**; §7 in **P3** (blocks on §5) |
| 4 Strategy + Signals (§9, §13) | **P2** Wave A |
| 5 People + Competition + Customers (§10–§12) | §10 in **P2**; §11, §12 in **P3** |
| 6 Risk + AI + Vendors + ESG (§14–§17) | §14, §17 in **P2**; §15, §16 in **P3** |
| — | **P4** Reconcile *(harness-only)* |
| 7 Synthesis (§18–§20, then §1) | **P5**, **P6** |
| 8 Verification + Assembly | **P7**, **P8** |

Two deviations, both deliberate:

**1. Spec phases 2–6 collapse into two dependency waves.** Those phases are a *dependency*
ordering, not a concurrency constraint. Wave A holds every body section with no intra-body
dependency (ten agents); Wave B holds the five that genuinely block on a Wave A output —
§7←§5, §11←§6, §12←§5, §15←§8, §16←§8. Every phase-boundary persistence obligation is still met at
each wave end: updated Source Manifest, Claim Ledger entries, structured evidence, and the handoff
JSON. Running §14 after §10 buys nothing, and costs four sequential agent turns.

**2. Reconciliation runs at P4, before synthesis, rather than inside phase 8.** This is the
single most important scheduling decision in the design — see below.

## Seven design decisions, and why

### 1. Agents write to disk; only ≤200-word digests flow through the orchestrator

A naive harness concatenates every research agent's full output and passes it to every section
writer. Cost scales as *agents × consumers*, and later agents drown in material they do not need.

Here each agent writes `sections/*.md` and `state/fragments/*.json` itself and returns a digest.
Downstream agents read the specific files they need. This is possible because the Workflow script
has no filesystem access but **subagents do** — the script passes paths, agents read them. A useful
consequence: the entire prompt library stays editable as plain Markdown without touching the runner.

### 2. ID space is partitioned in advance

The v3 handoff contract is append-only with sequential phases, so "next free ID" is well defined.
Ten concurrent agents have no shared runtime state, so it is not — they would all mint `S1`.

Each agent gets a 100-block (`prompts/id-allocation.md`). Claims need no block because
`C-<section>-nn` is section-scoped and sections are single-owner, making claim IDs collision-free by
construction. Single-owner registers (`P-`, `R-`, `U-`, `O-`, `A-`, `X-`) are minted by exactly one
agent each, and a second agent's copy is recorded as a defect rather than merged.

Blocks cause duplicate *sources* — three agents finding the same 10-K register it three times — so
`source-merge` deduplicates and rewrites. Its highest-value output is catching claims whose
corroboration collapses to one document after dedup. **That is confidence inflation no other check
can see, and it exists only because of parallelism.**

### 3. The adversarial audit runs before §18, not at verification

`evidence-audit` is instructed to **refute**, not verify, and to default to `REFUTED` when
uncertain. It runs at P4 rather than as part of the Verification Pass because of what happens to a
bad claim downstream:

> it becomes an opportunity in §18, then a message in §19.4, then an action in §20.6, then a finding
> in §1.2 — arriving at an executive as a fact.

Catching it at P4 costs one downgrade. Catching it at P7 costs a rebuild of §18–§20. The refuted
list is binding: an `O-nn` may not cite a refuted claim as need evidence (V3f, BLOCKER).

### 4. §1 is written last and placed first

The most important structural decision in the design, and it is the spec's own: an executive
summary written first invents conclusions the body then has to justify — the exact mechanism that
produces confident fabrication in long structured generation.

`exec-brief` reads the assembled body, mints zero sources, and must attach a register ID to every
statement (V8a, BLOCKER). When it wants to say something the body cannot support, that becomes a
`G-24nn` gap and surfaces in **§2.5 Limitations** — where the whole anti-fabrication architecture
becomes visible to the person making the decision.

### 5. Tier separation is enforced mechanically

§3–§17 are written vendor-neutral by fifteen agents that are told, repeatedly, that promotional references to the pursuing organization must not appear. `verification` checks for them at BLOCKER severity (V7a). The single
exception is §15.6, a gated positioning subsection owned by `ai-readiness`.

This is what makes the dossier trustworthy to delivery leaders rather than reading as pre-sales
material — and it is only enforceable because the agents writing the body are different agents from
those writing the pursuit, with no shared context that could leak positioning backward.

### 6. Deterministic math and deterministic collation live outside the model

`backbone` produces `precomputed-financials` from XBRL before §6 is written; `financials`
**reconciles against it and never re-derives it** (V2a). Where XBRL is unavailable, that is stated
explicitly rather than silently — if `financials` does not know the block is missing, it will assume
its arithmetic was checked when it was not.

Likewise `source-merge` (P4a) and `assembly` (P8b) run as Python in the programmatic backends,
because collation must be exact and reproducible. The Workflow backend performs the same work with
an agent against the same brief and the same standard.

### 7. Verification findings go back to the owners, not into a footnote

Verification may downgrade a claim or add a label; it may not rewrite another agent's analysis,
because a verifier that rewrites is no longer independent of what it checks. Before P7R that rule
left every prose defect *annotated*: across the first runs, refuted and weakened claims went on
being asserted in §3–§17, and qualifiers lost in the body stayed lost in §18–§20 and §1, while the
title block read PASS WITH DISCLOSURES.

P7R closes the loop without breaking the rule. `remediation-router` (brief 26a) turns the report
into work orders for the agents that own the defective text — one order per hop of a V5a chain —
and each owner revises only its own section and fragment under brief 26b. Owners run in dependency
order, because a fix to §18 made before its §8 origin is fixed simply restates the defect. Once a
register or body owner rewrites, every synthesis owner downstream of it is re-dispatched to re-sync
even when no finding names its text: the first proof run fixed §4 and §8 and left §18, §19
and §1 restating the pre-fix values, which the re-verifier then raised as new BLOCKERs. A fresh
verifier then re-runs **every** check, since a rewrite can introduce a defect as easily as remove
one, and §21.8 records the round: fixed, partly fixed, not fixed, regressed, declined.

The loop is for rewriting, not research. A finding that needs a document nobody retrieved is
unroutable and stays disclosed with the topic named for an extended-budget re-run. The workflow
backend implements P7R; the programmatic backends do not yet.

## What parallelism costs

Five failure modes exist here that a sequential pipeline cannot produce. All five are checked in
**V10**, which the spec's Verification Pass does not contain because a single-session run cannot
produce them:

| Failure | Mechanism | Check |
|---|---|---|
| **Conflicting canonical facts** | Two agents read different sources, periods, or bases for the same fact. *The signature failure — everything built on the wrong value is wrong.* | V10f (BLOCKER) + `source-merge` marks it `contested` and **omits it downstream** |
| **ID collision** | Two agents mint the same ID | V10b (BLOCKER) — prevented by blocks, verified anyway |
| **Duplicate sources / false triangulation** | Same document registered N times; a claim looks corroborated when both sources are one article | V10c, V10h — `source-merge` downgrades and reports |
| **Silent data loss** | An agent dies; its section and fragment never exist; assembly proceeds without noticing | V10e (BLOCKER) — missing agents are **named**, never absorbed |
| **Cross-section writes** | Two agents write the same subsection | V10g — single-owner enforced at merge |

The mitigation that matters most is `preflight`: by settling entity, ownership form, jurisdiction
adapter, reporting standard, and verticals *before* fan-out, most cross-agent disagreement is
eliminated at the source rather than reconciled after.

## Gated content — what public research cannot produce

Four things cannot be derived from public evidence, and the harness refuses to pretend otherwise:
**win probability · account revenue · relationship strength · stakeholder access.**

Without the §21.10 Account-Team Input Sheet, every such field renders `[INTERNAL REQUIRED]`,
§1.6 scores Stakeholder Access as `NOT ASSESSED` **and shows the weight renormalization**, and §16.4
renders a completion marker. Without the Capability Pack, every capability, offering, proof
point, and reference renders `[INTERNAL: validate with practice]`.

The §21.10 blank template is itself a deliverable: it is exactly what the account team fills in to
unlock those fields on a re-run.

## What this harness deliberately does not do

- **No rendering.** Markdown only. `chart-data` / `figure-spec` blocks carry enough intermediate
  representation for a downstream renderer, which validates them against schema v1 after the run.
- **No API keys on the default path.** The Workflow backend runs on a Claude subscription.
- **No client-facing output.** Every scorecard carries the "decision-support tool, not a measurement, must
  not be presented to the client" framing.
- **No unbounded research.** Every topic has stopping criteria, every section has a coverage record,
  and §21.12 distinguishes *stopped on diminishing returns* from *stopped on budget*.

## Extending it

**Add a research agent** — write `prompts/briefs/NN-<label>.md`, add a block row to
`prompts/id-allocation.md`, add rows to `blueprint/section-contracts.md`, add an `AgentSpec` to
`blueprint/stages.py` and a wave entry, and add the label to `config/default.json`'s
`role_model_map`. `tests/test_blueprint.py` fails until all five agree.

**Change the report structure** — edit `blueprint/vantage-blueprint-v3.md` and
`blueprint/section-contracts.md`, then `render/assembly.py`'s `SECTION_ORDER`. Agents read the
blueprint at runtime; the workflow encodes no structure.

**Change a rubric** — edit `blueprint/scoring-rubrics.md`. It is reproduced into §21.8, so the
dossier documents whatever rubric was actually in force.

**Add a vertical** — add a module to `blueprint/vertical-modules.md` following the uniform six-block
structure, add its code to `VERTICAL_CODES` in `stages.py`, to the `verticalCode` enum in
`state/state.schema.json`, and to `VERTICALS` in the workflow.

**Add a jurisdiction** — add an adapter section to `blueprint/jurisdiction-adapters.md` and its code
to the `jurisdictions` enum in the schema and the workflow.
