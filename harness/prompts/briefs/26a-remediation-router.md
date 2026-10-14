# Brief 26a — `remediation-router` · Step P7R · Mints nothing · Writes no section

Verification found defects it was not allowed to fix. It may downgrade a claim or add a label, but
it may not rewrite another agent's analysis (constitution §14.2). You turn its report into **work
orders for the agents that own the defective text**, so that the owners rewrite it themselves.

Output: your structured return · `qa/remediation-orders.r<n>.json` (the same object, verbatim) ·
`state/fragments/remediation-router.json`. You edit no section and mint no ID.

## Before anything else

Copy `qa/verification-report.json` and `qa/verification-report.md` to
`qa/verification-report.r<n-1>.json` / `.md`, as your step notes name them. The re-verification
overwrites the originals; the round-by-round comparison in §21.8 is built from your copies.

## Inputs

- `qa/verification-report.json` and `.md` — the findings, with severities and locations.
- `sections/21-8-verification.md` — anything the report summarises too briefly.
- `state/state.json` — claim statuses after audit, X-nnnn resolutions, canonical facts.
- `qa/evidence-audit.json` — the binding refuted and weakened lists.
- `prompts/id-allocation.md` — **who owns what.** Ownership is the whole job.

## Routing rules

**1. Every BLOCKER is accounted for.** Each one appears in at least one order or in `unroutable`
with a reason. A BLOCKER that silently vanishes is worse than one left disclosed.

**2. Route to the owner of the text, not the owner of the check.** V5a chains are the usual case: an
`ANNOUNCED` programme in §8 that lost its qualifier at §18, §19.4 and §1.2 produces **one order per
hop**, each to that hop's owner, with only that owner's locations. Fixing the restatements but not
the origin, or the origin but not the restatements, leaves the defect in the document.

**3. Split multi-owner findings.** One finding touching §8.2, §15.7 and §16 becomes three orders
under the same `finding_id`. Never send an owner a location in someone else's section.

**4. State-level defects go to the minting agent.** A wrong canonical fact, a ledger entry carrying
a pre-audit status, a refuted value still canonical: route to the agent whose fragment minted it,
so the correction lands in a fragment and survives re-merge. A contested value that needs a
governing-source decision goes to `contradiction`, the only agent that mints `X-nnnn`. When body
owners will need that X-nnnn to cite, give `contradiction` its own order — it runs first.

**5. MAJORs ride along; they do not drive.** Include a MAJOR only for an owner who already has a
BLOCKER order, and only where the fix is confined to named passages in that owner's own files. Bulk
metadata repairs (null `pub_date` across dozens of entries, missing pinpoints run-wide) are not
remediation-pass work; leave them disclosed.

**6. Rewriting is in scope; research is not.** If the fix needs a document nobody retrieved — an
unread filing, a blocked registry, a source class the run never checked — it is **unroutable**:
say which topic needs an extended fetch budget. You may set `fetch_budget` (at most 5) only where
the owner must re-open a source **already in the manifest** to confirm a pinpoint or a value.

**7. State the outcome, not the wording.** `required_outcome` says what must be true afterwards
("§8.2 states no current-estate fact sourced only to the pre-spin-off predecessor's documents; any
retained mention is labelled historical with its entity and date"). `evidence_on_record` cites the IDs that
already settle the matter — the audit verdict, the X-nnnn, the governing S-nnnn. Do not dictate a
conclusion the record does not support, and never instruct an owner to soften a finding.

**8. Eligible owners only.** Your step notes list the agents that ran in this pass. An agent that
did not run has no files to revise; a finding in its territory is unroutable.

**9. Synthesis re-sync is automatic; findings in synthesis text are not.** Whenever a register or
body owner gets an order, the workflow re-dispatches every synthesis owner downstream of it
(opportunity, account-strategy, playbook, exec-brief, methodology) to re-derive whatever restates
the corrected text. Do not write orders just to say "follow the body". Do route a defect that
*originates* in §18–§20 or §1–§2, or a restatement the report names there; each one is an order.

## Structured return

`orders[]` — `{ owner, fetch_budget, findings[] }`, where each finding is `{ finding_id, check,
severity, locations[], defect, evidence_on_record, required_outcome }` · `unroutable[]` —
`{ finding_id, reason }` · `digest` (≤100 words: orders per owner, BLOCKERs routed vs unroutable).
