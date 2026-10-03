# Brief 16 — `vendors` · Wave B (← §8) · Block 1600–1699 · Owns §16 Partnership & Vendor Ecosystem

You map **the incumbent landscape** — who is already inside this account, in what domains, and where
a new entrant could enter. §16.5 feeds §19.7 directly, and §16.4 is fully gated on account-team
input.

Read `technology`'s §8.1 output first; every vendor they evidenced is your starting register.

Output: `sections/16-vendors.md` · fragment `state/fragments/vendors.json`.

## §16.1 Major Technology Vendor Relationships

`T-16.1`. Per entry: vendor · domain · relationship type · **evidence type · mention classification
· confidence** · signal recency.

The mention-classification rule from `evidence-policy.md` §6 applies here exactly as it does in
§8.1. A vendor's customer-logo page is `OBSERVED-SIGNAL` about a relationship of unknown depth and
unknown currency — logo pages are notoriously stale.

**Contract signals only as evidenced.** Never a contract value, never a term, never a renewal date
that is not disclosed (V9d, BLOCKER).

## §16.2 SI & Consulting Partnerships — the competitive incumbency

`T-16.2` + `F-16.2`. Which systems integrators and consultancies are evidenced at this account, in
which domains, since when.

**Contract-timeline estimates only with the basis shown.** A public-sector award record with a
stated end date is evidence; a five-year assumption applied to a press release is not.

This is the section §19.7 competes against. Be precise about **domain and recency** — an SI that ran
a 2019 ERP programme is a different competitive fact from one running managed services today, and
conflating them produces a wrong win strategy.

Take `operations`' §7.4 named providers via `handoff`, and `competition`'s §11.7 findings.

## §16.3 Startup & Innovation Partnerships

Named, dated partnerships and accelerator relationships. **Empty is a valid render.**

## §16.4 the pursuing organization Current Relationship Status — fully gated

Renders **only** from the `ACCOUNT_TEAM_INPUT_SHEET` / `ACCOUNT_CONTEXT` /
`KNOWN_RELATIONSHIP_CONTEXT` inputs.

**Where those are `NOT_ATTACHED` / `NONE`, this subsection is exactly:**

```markdown
### 16.4 the pursuing organization Current Relationship Status

[INTERNAL: account team to complete]

Current revenue, active contracts, delivery history, references, and pipeline at this account
cannot be established from public evidence and are not inferred here. See §21.10.
```

**Never guessed, never inferred from a public case study, never assembled from a logo page**
(V7h, BLOCKER). An organization logo on the client's partner page is not a relationship description.

Note the tier boundary: §16 is inside the vendor-neutral range, and §16.4 is a gated exception. Keep
the rest of §16 free of the pursuing organization references.

## §16.5 Vendor Displacement Opportunities

`T-16.5`. Model 8 in `blueprint/scoring-rubrics.md`, **dimensions 1–4 only**:

1. Relationship age and depth
2. Evidenced dissatisfaction
3. Contract or renewal signal (from §13.7)
4. Capability gap at the incumbent

> **Dimension 5 (relative advantage) is deliberately deferred to §19.7**, because assessing a
> organization-relative advantage inside the neutral range is a V7a tier violation. Score four dimensions,
> state that the fifth is deferred, and hand off.

Frame neutrally throughout: "third-party entry potential", not "the pursuing organization displacement opportunity".
Every row needs ≥1 evidenced incumbent — a displacement assessment with no evidenced incumbent is
speculation about a vacancy.

## Whitespace — the absence finding

Domains where the target plainly has a need (from §7.5, §8.6) and **no incumbent is evidenced** are
worth stating explicitly. But be careful: absence of public evidence of an incumbent is not evidence
of absence. Write it as *"no incumbent evidenced in [domain] across [what you searched]"* — a
whitespace **hypothesis**, `OBSERVED-SIGNAL` at most, for §18 to validate.

## Traps

- **Vendor logo pages and case studies are self-reported by both parties** and are frequently years
  stale. `independence: self-reported`, `MEDIUM` at best.
- **Technographic vendors model installations; they do not observe them.**
- **A partnership announcement is `ANNOUNCED`** — it says nothing about deployment or spend.
- **Do not infer displacement from dissatisfaction in a review site.** Sample-size discipline
  applies (V9h).
- **Do not name an SI's contract value.** It is disclosed or it is absent.

## Fragment

Claims `C-16.1-nn` … `C-16.5-nn`, each with mention classification. Sources `S-16nn`. Gaps `G-16nn`.
Coverage for §16. `scoring_inputs.model_8` (dimensions 1–4, with dimension 5 marked deferred).
Figure `F-16.2`. `handoff` to: `account-strategy` (the incumbent register and the deferred Model 8
dimension 5 for §19.7), `opportunity` (whitespace hypotheses and displacement candidates),
`playbook` (renewal windows worth acting on).
