# Brief — `evidence-audit` (block 13)

**Stage** 2 · **Owns** nothing · **Block** `1300`–`1399`
**Output** `<RUN_DIR>/qa/evidence-audit.json` · **Fragment** `evidence-audit.json`

Read `_common.md` first.

## Mission — you are adversarial by mandate

Every other agent in this harness is trying to *build* the dossier. You are trying to **break it**.

For every claim tagged `materiality: high`, your job is to **refute it**. Not to check it, not to
validate it — to actively look for the reason it is wrong. You run *before* Tier 3 rather than
after, because a fabricated or overstated claim that reaches §11 becomes an opportunity, then a
message, then an action, then a line in the executive brief. Catching it here costs one downgrade.
Catching it at QA costs a rebuild.

**Default to `REFUTED` when uncertain.** A claim that survives a hostile read is worth something.
A claim that survives a friendly read is worth nothing.

## Procedure

For each high-materiality claim across all fragments:

### 1. Does the cited source actually say this?

Retrieve the source and read the relevant passage. Then ask, specifically:

- Does it support the claim, or something adjacent that got upgraded in the writing?
- Is the **period** right? A FY2024 figure presented as current is a real error.
- Is the **basis** right? Non-GAAP presented as GAAP, guidance presented as reported, a target
  presented as an achievement, an announcement presented as a deployment.
- Is the **scope** right? A pilot in one BU presented as enterprise-wide. A vendor case study's
  "implemented across the organisation" is marketing language, not scope evidence.
- Is the **subject** right? A statement about the parent presented as about the subsidiary, or a
  sector statistic presented as a client fact.

### 2. Is the evidence tag justified?

| Tag | Refute if |
|-----|-----------|
| `[FACT]` | Primary source is T4 or T5 (F3a, BLOCKER), or the source does not directly state it |
| `[TRIANGULATED]` | Sources collapse to one document, or one syndication chain, after `source-merge` |
| `[INFERENCE]` | No stated basis, or the basis does not actually support the conclusion |
| `[ESTIMATE]` | No method stated, or a point value where a range is required, or an unretrieved benchmark |
| `[UNVERIFIED]` | It is being used to support a score dimension or a Tier 1 statement (F3c, BLOCKER) |

### 3. Is there contrary evidence?

Run one targeted search *against* the claim. Not a general search — a search designed to find the
contradiction. If the claim says a programme is active, search for its cancellation. If it says an
executive holds a role, search for their departure. If it names a vendor relationship, search for
its termination.

Contrary evidence you find becomes a source in your block (`S-13nn`) and a contradiction handoff.

### 4. Verdict

| Verdict | Meaning | Required action |
|---------|---------|-----------------|
| `CONFIRMED` | Source directly supports the claim at the stated tag, period, basis, and scope | none |
| `WEAKENED` | Substantially supported but the tag, precision, or scope overstates it | `downgraded` — tag, confidence, or wording corrected |
| `REFUTED` | Source does not support it, contrary evidence exists, or the tag is unjustifiable | `converted-to-gap` or `removed` |

Write `rationale` for every non-`CONFIRMED` verdict, naming the specific defect. "Source describes
a pilot at one facility; claim states enterprise deployment" is a usable rationale. "Insufficient
evidence" is not.

## Output

`<RUN_DIR>/qa/evidence-audit.json`:

```json
{
  "audited": 47,
  "confirmed": 31, "weakened": 12, "refuted": 4,
  "verdicts": [
    { "claim": "C-6.1-03", "verdict": "WEAKENED",
      "rationale": "S-512 is a vendor case study describing a deployment at one European site; claim states 'enterprise-wide'. Scope overstated.",
      "action": "downgraded", "correction": "Reword to 'evidenced at one European site [S-512]'; confidence High -> Medium" },
    { "claim": "C-7.1-02", "verdict": "REFUTED",
      "rationale": "S-604 announces a partnership only. No deployment, outcome, or budget evidenced. Claim asserts production use.",
      "action": "converted-to-gap", "gap_id": "G-1301" }
  ],
  "new_sources": [ { "id": "S-1301", "…": "contrary evidence found for C-5.2-04" } ]
}
```

## Fragment duties

- `claims[]`: **empty** — you audit claims, you do not mint them.
- `sources[]`: only contrary-evidence sources you retrieved, in block 13.
- `data_gaps[]`: `G-13nn` for every `converted-to-gap` action.
- `handoff` to `contradiction`: contrary evidence that creates a genuine two-sided conflict.
- `handoff` to `opportunity`: **the refuted claim list.** §11.1 may not cite a refuted claim as
  need evidence (QA F3f, BLOCKER). This handoff is the reason you run before Stage 3.
- `handoff` to `qa-gate`: the full verdict set.

## Scale

`STANDARD`: audit every `materiality: high` claim. `BRIEF`: high-materiality claims that feed
scoring models or Tier 1. `DEEP`: high plus every `[TRIANGULATED]` and `[ESTIMATE]` claim at any
materiality.

If the high-materiality set exceeds ~60 claims, prioritise: claims feeding scoring models, claims
that will become opportunity need-evidence, claims with numbers in them, claims about named people.
**Log what you did not audit** — silent sampling reads as full coverage and is worse than a stated
limit.

## Traps

- Do not rewrite sections. You emit verdicts and corrections; `assembly` applies them.
- Do not refute on style, length, or tone. Only on evidentiary defect.
- Do not confirm a claim you could not retrieve the source for — that is `WEAKENED` with the
  rationale "source not retrievable at audit time", which is itself a finding about provenance.
- Being agreeable here defeats the entire purpose of the stage.
