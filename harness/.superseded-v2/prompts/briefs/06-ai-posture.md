# Brief — `ai-posture` (block 6)

**Stage** 1 · **Owns** §7.1–7.4 · **Block** `600`–`699` · **Envelope** ~1,800 w
**Output** `<RUN_DIR>/sections/07-ai.md` · **Fragment** `ai-posture.json`

Read `_common.md` first. **Tier 2 — write nothing about the pursuing organization.**
You score **Model 3 (AI & Agentic Readiness)**. Read `blueprint/scoring-rubrics.md`.

## Mission

Establish what the client has actually done with AI — not what is possible, not what peers do, not
what they should do. This is the section where enthusiasm most reliably outruns evidence, in both
directions: over-claiming maturity from a press release, and under-claiming it because production
deployments are rarely disclosed.

## §7.1 AI/GenAI Initiative Inventory — ~500 w · bar `any×1` per initiative

A register: initiative name · description · status (announced / pilot / production, **as
evidenced**) · disclosed partners and platforms · disclosed outcomes · date · source · confidence.

Also capture: named AI leadership roles (Chief AI Officer, Head of AI, AI CoE lead) — a named role
is strong evidence of organisational commitment · AI mentions in earnings calls with dates ·
AI-related partnerships and their announced scope.

**Status discipline.** "Announced" ≠ "piloting" ≠ "in production". Use the word the source uses. A
press release announcing a partnership is not evidence of deployment. Where status is unclear,
write `status: announced (deployment not evidenced)`.

**An empty register is a valid and informative render.** For many clients the honest finding is
"no public AI initiative evidenced as of {date}, across N queries" — that is a real result with
real pursuit implications, not a failure.

## §7.2 AI Maturity Assessment — ~500 w · Model 3

Score all six base dimensions: AI strategy & sponsorship (20%) · data readiness (25%) · talent
(15%) · infrastructure (15%) · governance & responsible AI (10%) · deployment maturity (15%).

Data readiness draws on `technology`'s §6.3 handoff — use their claim IDs rather than
re-researching. Talent draws on `strategy`'s §5.5 hiring handoff.

**Agentic overlay** — apply **only** if §7.4 carries ≥2 evidenced claims. Otherwise state
"agentic overlay not applied: insufficient evidence" and report the base composite alone.

`n/e` any dimension without a claim, reweight, and show the reweighting. Suppress the composite at
≥2 Low-confidence dimensions.

**Say this explicitly on the render:** deployment maturity is systematically under-observed from
outside, because companies disclose pilots far more readily than production. A low score means
"not disclosed", not "not happening". Without that sentence the score misleads.

## §7.3 Automation & Emerging-Tech Footprint — ~350 w · **Opt** · bar `any×2`

RPA/IA platform evidence · automation CoE signals · disclosed automation outcomes.

**`+v2.2` Emerging-technology bets** — evidenced investments in IoT, digital twins, blockchain/DLT,
AR/VR, or quantum, and the client's *stated* rationale for each. Evidence discipline is the whole
point: a press release announcing a "digital-twin initiative" is evidence of the announcement, not
of a deployment. The vertical module's **S** and **U** blocks name what to search for — they are
not evidence that the client runs it (the harness's signature fabrication route).

**If the bar is unmet, omit this section entirely** — it is Opt, not Core. Do not render an empty
heading. If only emerging-tech bets are evidenced (no RPA), keep the section and retitle the render
accordingly.

## §7.4 Agentic Readiness Signals — ~400 w · bar **none**, explicitly inference-heavy

Every statement here is `[INFERENCE]` with a stated basis. Label them all. This section is honest
speculation, clearly marked as such — which is why it has no evidence bar and why nothing in it
may support a score dimension without independent claims.

Signals worth reading: **API and integration maturity** — a public developer portal, documented
APIs, or a platform strategy indicates the substrate agentic systems require · **orchestration
and workflow platforms** evidenced in §6.1 · **data accessibility** — whether §6.3 evidence
suggests systems agents could actually reach · **governance posture** toward autonomous systems,
including human-in-the-loop language in any published AI policy · **executive statements** about
agents or autonomy, in either direction — a public statement *deferring* agentic adoption is
evidence too, and adjusts Model 3's overlay by −0.3.

Do not describe agentic technology in general. The reader knows what agents are. Assess *this
client's* readiness.

## Fragment duties

- `scoring_inputs.ai_maturity`: full Model 3 block, with the overlay applied or explicitly waived.
- `handoff` to `opportunity`: every evidenced initiative and every capability gap — these are the
  seeds for §11.2's `U-nn` backlog.
- Tag AI-initiative claims `materiality: high`; §11.2 depends on them.

## Traps

- **Vendor announcements are marketing.** "Client X partners with Vendor Y on AI" is evidence of a
  partnership announcement, not of a deployment, an outcome, or a budget.
- Do not import the vertical module's use-case seeds as if they were client initiatives. They are
  candidates for §11.2, which belongs to `opportunity` — pass them via `handoff`.
- Do not score AI maturity from industry reputation. A company famous for technology may have a
  weak internal AI estate, and the evidence is what you can retrieve about *them*.
- Resist writing recommendations. "The client should establish an AI CoE" is Tier 3 content and
  fails F7a. You assess; §11 recommends.
