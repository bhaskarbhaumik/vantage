# Brief 08 — `leadership` · Wave A · Block 0800–0899 · Owns §10 · Mints `P-nn`

You establish **who decides, on what authority, and what constrains delivery**. You are the sole
minter of the stakeholder register `P-nn`, which §19.6 and §20.4 build on directly.

You also own the strictest privacy boundary in the dossier. Read `evidence-policy.md` §10 before
writing a word about a person.

Output: `sections/10-leadership.md` · fragment `state/fragments/leadership.json`.

## The privacy boundary — V9a/V9b are BLOCKERs

**Permitted:** role, tenure, prior roles, public statements with citation, conference appearances,
board memberships, compensation as disclosed in the proxy.

**Forbidden:** inferred personality or working style · family or personal circumstances · health ·
political or religious affiliation · unverified social-media attribution · **any loyalty or
preference claim**.

Prior-vendor employment may appear **only** as: *"prior employment at X (OBSERVED-SIGNAL; no
inference of preference)"*. Writing that a CIO "is likely to favour" a vendor because they worked
there is a BLOCKER, and it is also bad analysis — it is unfalsifiable.

## §10.1 Board of Directors

`T-10.1`. Composition, tenure, committee structure, backgrounds relevant to technology,
transformation, or the target's regulatory exposure. From the proxy or governance filing.
Private and other forms: best-available, marked as such.

## §10.2 C-Suite & Executive Leadership

**10.2.1 CEO** — profile and strategic orientation, in their own quoted words where possible.
**10.2.2 CIO / CTO / CDO / CAIO** — public statements, conference appearances, tenure. These are
the profiles the pursuit turns on; invest the search budget here.
**10.2.3 CFO & procurement leadership** — the people who approve.

`T-10.2` + `F-10.2` org figure. Every quote carries speaker, role at the time, event, date, and
provenance class.

**Recency matters unusually here.** Leadership identity older than 12 months without a re-check is
`stale` (`evidence-policy.md` §5). Check for departures before you write anyone in.

## §10.3 Business Unit Leadership

BU leaders and their mandates, tied to the `corporate` §3.3.1 BU table.

## §10.4 Functional Buying Centers

`T-10.4`. Where technology, operations, and finance decisions get made. **Authority and budget
claims are `INFERRED` unless evidenced** — an org chart shows reporting lines, not spending power.
Show the inference trail.

## §10.5 Decision-Making Dynamics & Culture

Procurement centralization, budget cycle timing, RFP propensity. Every dynamic status-tagged.
`T-10.5` + `F-10.5`. This is inference-heavy by nature; label it as such rather than thinning it,
because §19.8 and §20.6 timing depend on it.

## §10.6 Stakeholder Map for Pursuit — the `P-nn` register

The canonical register. Per stakeholder: `P-nn` · name · title · entity (from §3.6) · **influence
1–5 with its basis** · **accessibility 1–5 with its basis** · evidenced-versus-inferred flag ·
sources.

Model 6 in `blueprint/scoring-rubrics.md`. The two axes are **never averaged** — the grid is the
output.

> **Public evidence caps accessibility at 3.** Conference speaking, a published contact route, an
> active public presence, analyst-day participation — these support a 3. **4 and 5 require
> account-team input.** Without the Input Sheet, cap at 3 and mark the axis
> `[INTERNAL REQUIRED for 4–5]`. This is a gated field (V5b).

## §10.7 Workforce Profile & Talent Strategy

Headcount trend, geographic and functional mix, attrition signals, HR priorities, union and
works-council exposure. `T-10.7` + `C-10.7`.

**Aggregate only** (V9c). From the human-capital disclosure, the sustainability report, and credible
press. Attrition from review sites requires **sample size, window, method, and known biases** stated
— and even then it is `OBSERVED-SIGNAL` at `LOW`. Never infer enterprise-wide culture from reviews.

## §10.8 Delivery Constraints

Works councils and unions · security clearances · localization and data-residency requirements ·
offshore restrictions · regulated-outsourcing rules (financial-services outsourcing regimes,
public-sector sovereignty requirements) · accessibility mandates.

**Everything that shapes how work can actually be delivered.** This section drives Model 7 and
§19.8's commercial construct: get it wrong and the recommended deal shape is undeliverable.

**Empty is a valid render** — but it must say "no delivery constraints evidenced in [what you
searched]", not simply be absent. An unexamined works council is how a European delivery model
fails after signature.

## Traps

- **Do not build an org chart from LinkedIn.** LinkedIn is accessible only through a partner API or
  a licensed vendor; an unlicensed scrape is a compliance failure regardless of what it shows.
- **A press-release title is a title at that date.** People move.
- **Do not name people below the executive and BU-leader level.** Granularity below that is neither
  decision-relevant nor appropriate.
- **Budget ownership is never stated as fact** (V9d-adjacent, and `evidence-policy.md` §12).

## Fragment

Claims `C-10.1-nn` … `C-10.8-nn`. **`stakeholders[]` — the full `P-nn` register.** Sources `S-08nn`.
Gaps `G-08nn`. Coverage for §10. `scoring_inputs.model_6`. Figures `F-10.2`, `F-10.5`, `F-10.6`;
chart `C-10.7`. `handoff` to: `account-strategy` and `playbook` (the `P-nn` register is theirs to
build on), `opportunity` (buying-centre structure), `risk` (delivery constraints that are also
risks), `technology` (CIO/CTO identity if you found it first).
