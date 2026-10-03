# Brief 21 — `opportunity` · Step P5 · Block 2100–2199 · Owns §18 · Mints `O-nn`

**Tier 3 begins here. the pursuing organization content is now permitted** — under the Capability-Pack and Input-Sheet
gates. You run alone so that §19 and §20 have stable `O-nn` IDs to reference.

You are the sole minter of the opportunity register, and the register is the spine of the whole
pursuit half of the dossier.

Output: `sections/18-opportunity.md` · fragment `state/fragments/opportunity.json`.

## Two binding constraints, before anything else

**1. The refuted list.** Read `qa/evidence-audit.json`. **No `O-nn` may cite a refuted claim as its
need evidence** (V3f, BLOCKER). Where a refutation empties an opportunity, the opportunity does not
exist — do not substitute a weaker claim to keep it alive.

**2. The internal-input gates.** Win probability, account revenue, relationship strength, and
stakeholder access **cannot be derived from public data**. Without the Account-Team Input Sheet,
every such field is exactly `[INTERNAL REQUIRED]` (V5b, V8f, BLOCKER). What you *can* report
from public evidence is **opportunity attractiveness**, and that is what §18 is built on.

## The `O-nn` register

Minted here, referenced everywhere downstream. Per opportunity:

`O-nn` · title · service line · **`need_evidence` — the claim IDs that establish the need** ·
sizing basis · sizing range · attractiveness (Model 4, 1–5) · win probability (**gated**) · horizon
· lead practice · status (`CONFIRMED` / `HYPOTHESIS` / `VALIDATE`) · confidence.

**Status discipline:**
- `CONFIRMED` — the need is established by claims that survived the audit at `CONFIRMED`/`HIGH`.
- `HYPOTHESIS` — the need rests on `INFERRED` or `LOW`-confidence claims. Must appear in the §19.9
  validation actions and in §20.6 (V7e).
- `VALIDATE` — plausible but the anchoring evidence is a signal, not a finding.

An opportunity whose only need evidence is a `LOW` claim **must** be `HYPOTHESIS`
(`evidence-policy.md` §4).

## §18.1 Strategic Account Potential

`T-18.1` — Service Line · Yr1–Yr3 **range** · Sizing Basis · Attractiveness · Win Prob (gated) ·
Confidence.

> **Ranges and sizing logic always. Never a bare number.** A bare authoritative-looking figure is
> the most damaging thing this section can produce, because it is the number that ends up on a
> slide.

Sizing bases, in descending order of quality: a **disclosed programme budget** → a **disclosed
contract value** for comparable scope → the §6.6 IT-spend estimate applied with a stated
addressable share → a peer-derived analogue from the §11.0 peer set. State which one you used, show
the inputs, and give a range wide enough to be honest.

Where §6.6 was gapped, say so: sizing built on nothing is `[ESTIMATED]` with no basis, which is not
allowed (V2h).

## §18.2 Business Opportunity Themes

The 4–6 themes the register clusters into. `F-18`. Themes are how §19.2 and §1.4 read the register;
cluster by client problem, not by the pursuing organization service line.

## §18.3 Functional Opportunity Mapping

`T-18.3`. By business function, **≥1 evidenced §7.5 pain point per row**. A function with no
evidenced pain does not get a row.

## §18.4 Technology & Transformation Opportunities

`T-18.4`. By technology domain, anchored in §8.6 constraints and §9.2 programmes. Take the `U-nn`
backlog from `ai-readiness` — do not re-mint use cases; cite them.

## §18.5 Partnership & Co-Innovation Potential

Where a joint play with an evidenced partner (§9.5, §16.3) beats a direct one.

## §18.6 Timing & Entry Points

`T-18.6` + `C-18`. **Evidenced events only**: fiscal calendar from §6, contract and RFP events from
§13.7 and §14.9, leadership changes from §10.2, programme milestones from §9.2.

**No invented dates** (V9d, BLOCKER). Where §13.7 was empty, this section leans on fiscal calendar
and leadership changes instead — and says so, because that is a weaker timing basis and the account
team should know it.

## the pursuing organization content rules

Capability, offering, accelerator, and proof-point references come **only** from the Capability
Pack, cited `[CAPABILITY-PACK]`. Without a pack, describe the capability class generically and mark it
`[INTERNAL: validate with practice]`. **Never invent an organization reference, client name, or
quantified outcome** (V7b, BLOCKER).

## Traps

- **Do not build an opportunity from an industry trend.** Every `O-nn` traces to a claim about
  *this* company.
- **Do not let the `U-nn` backlog become the opportunity register.** Use cases are capability
  applications; opportunities are commercial propositions with a sizing basis.
- **Attractiveness is not desirability.** Score Model 4 against evidenced need, sizing basis, timing
  signal, and capability fit — not against how much you would like to win it.
- **A displacement opportunity needs an evidenced incumbent** (§16.5), not an assumed one.
- **Do not fill a thin register.** Six well-anchored opportunities beat fourteen where eight are
  generic.

## Fragment

Claims `C-18.1-nn` … `C-18.6-nn`. **`opportunities[]` — the full `O-nn` register with
`need_evidence` claim IDs.** Sources `S-21nn` (you should need very few — this is synthesis).
Gaps `G-21nn`. `scoring_inputs.model_4`. Chart `C-18`; figure `F-18`. `handoff` to
`account-strategy` and `playbook` (the register is theirs to build on), `exec-brief` (the top 5–8
for §1.4).
