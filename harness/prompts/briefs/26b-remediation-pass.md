# Brief 26b — remediation pass · Step P7R · Read by an owning agent re-dispatched after verification

You wrote a section earlier in this run. Verification has since found defects in text or records
**you own**, and you have a work order. This brief governs the pass. It wins over your own brief
where they conflict; the constitution wins over both.

Your earlier section and fragment are on disk. **Revise them; do not start again.**

## Scope

1. **Fix what the order names, everywhere it occurs in your own files.** The order lists locations;
   search your whole section and fragment for the same defect restated elsewhere and fix that too.
   An origin fixed and a restatement left behind is the failure this pass exists to remove.
2. **Change nothing else.** No new analysis, no restructuring, no growth past your envelope. A
   reviewer comparing before and after should see only the corrections.
3. **Your files only** (constitution §14.2). A defect you find in another agent's section goes in
   your `handoff` array, not into their file.
4. **Research is out of scope.** Your step notes give a fetch budget, usually 0. Spend it only to
   re-open a source already in the manifest. If a fix needs a document nobody retrieved, decline
   that item and record a `G-nnnn` gap in your block saying what would close it.

## How to make each kind of fix

**A refuted claim** (evidence-audit or verification). Remove the assertion from prose. You may
mention it only as refuted — never as fact, never softened into "reportedly". The ledger entry
stays, at its refuted status; IDs are never deleted or renumbered.

**A weakened or downgraded claim.** Carry the audited status and confidence in the prose wherever
the claim is used: `ANNOUNCED`, `INFERRED`, `OBSERVED-SIGNAL`, `LOW`. A qualifier that holds in the
origin section and disappears at a restatement is the V5a failure.

**A changed value** (a resolved contradiction, a superseded target, a corrected count). Never edit
the old claim's value silently (id-allocation rule 7). Mint a new claim in your own section
numbering carrying the governing value, cite the `X-nnnn` that settled it, and set `superseded_by`
on the old entry. If no X-nnnn exists yet, `contradiction` was given an order this round and ran
before you — read `state/fragments/contradiction.json`. If it is still absent, hand off to
`contradiction` and label the passage as contested rather than picking a value.

**Wrong-entity evidence** (V4: a predecessor company, a former parent, a divested unit). Remove it
from every current-state statement. Keep it only where history is the point, labelled with the
entity it belongs to and its date.

**A broken chain into §18–§20 or §1.** If you own synthesis, re-derive the passage from the
corrected body, not from your earlier text. An opportunity, message or action whose evidence was
refuted is withdrawn or restated at the evidence's real status; it is not kept on a new rationale
invented to save it.

**A verification annotation** (`[Verification Vx]` notes in your section). Where you fixed the
defect it marks, remove the note. Where you did not, leave it.

## Re-sync passes

A synthesis owner (§18, §19, §20, §1, §2) can be dispatched with a **re-sync** block and no finding
of its own: upstream owners corrected text yours builds on. Read their `remediation_log` entries,
find every passage of yours that restates, scores, counts, ranks or dates something those entries
changed, and re-derive it from the corrected record. Typical: a date that became a contingency, a
score whose input was suppressed, a risk whose severity moved, an incumbent that turned out to be
the predecessor company's. Passages that the logs did not touch stay exactly as they are. A re-sync
that finds nothing to change says so in its return and writes no `remediation_log` entry.

## Your fragment — read this twice

Your fragment will be the **newest file** at the next re-merge, and the merge applies the newest
value field by field. So:

- **Every claim of yours that evidence-audit or verification downgraded must carry the downgraded
  status and confidence when you write.** Read them from `state/state.json`. Writing back the
  status you originally minted would reinstate a refuted claim across the whole dossier, and it
  would do so invisibly.
- **Read the existing fragment, modify it, write it whole.** Do not drop sources, claims, gaps or
  handoffs you are not changing.
- Add a `remediation_log` array, one entry per action:
  `{ "round": n, "finding_id": "...", "location": "§8.2", "action": "rewritten | relabelled |
  removed | superseded | declined", "before": "<≤30 words>", "after": "<≤30 words>",
  "claim_ids": ["..."], "reason": "<required when declined>" }`.

**Declining is allowed; ignoring is not.** If a required outcome is wrong on the record, or needs
research, decline it in the log with the reason. The re-verifier checks every order against your
log.

## Return

At most 100 words: findings fixed, findings declined and why, and anything a later owner in this
round must know.
