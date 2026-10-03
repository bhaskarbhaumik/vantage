# Brief — `risk-reg` (block 9)

**Stage** 1 · **Owns** §10.1–10.7 · **Block** `900`–`999` · **Sole owner of** `R-nn`
**Envelope** ~2,950 w · **Output** `<RUN_DIR>/sections/10-risk.md` · **Fragment** `risk-reg.json`

Read `_common.md` first.
You score **Model 7 (Delivery & Commercial Risk)**. Read `blueprint/scoring-rubrics.md`.

## Mission

Complete the client-reality picture with risk, regulation, ESG, litigation, and forward scenarios —
then bridge to Tier 3. **§10 is the last vendor-neutral section in the dossier**, and §10.5 is its
bridge: it translates client risk into delivery and commercial risk without promoting anything.
The two `+v2.2` sub-sections (§10.6 litigation, §10.7 scenarios) are additional client-reality
analysis that §10.5 draws on — write §10.5 to synthesise §10.1–10.4 **and** them.

## §10.1 Enterprise Risk Synthesis — ~600 w · bar `T1×1` risk-factor section

Top ~8 material risks, **distilled and not copied**.

A 10-K risk-factor section is 30 pages of legally-driven boilerplate. Your job is to identify which
risks are (a) specific to this company rather than generic to all public companies, (b) evidenced
as materialising rather than merely disclosed, and (c) consequential for a transformation
programme. A dossier that reproduces the risk factors has added nothing.

Per `R-nn`: risk · category · severity · likelihood · **rationale for both ratings** · sources ·
whether evidence suggests it is materialising.

Severity and likelihood without rationale are unreproducible. State the basis.

Corroborate from outside the filing: news of the risk materialising · analyst commentary ·
regulatory action · peer incidents in the same risk class. A risk disclosed in the 10-K *and*
visible in the news is materially different from one only disclosed.

**Private variant:** no risk-factor section exists. Build from statutory filings, credit-rating
rationales, sponsor disclosures, and news. Flag the weaker evidence base explicitly.

## §10.2 Regulatory & Compliance Landscape — ~500 w · bar `any×1` per regime

Regimes that **demonstrably apply to this client**, from the vertical module's **R** block as a
search checklist. Per regime: what it requires · jurisdiction · applicability evidence · compliance
or enforcement history · upcoming changes with dates.

Jurisdiction-tag everything. A US-listed company with European operations faces both regimes, and
which applies where is the whole point.

**The R block is candidates, not conclusions.** Include a regime only where applicability is
evidenced by the client's own disclosure, a regulator's register, or their operating footprint.
Listing every regime typical for the sector is filler and, worse, reads as analysis.

Forward-looking regulation with a compliance deadline is high-value: it is the strongest form of
dated urgency evidence for Model 4 dimension 2. Flag those for `opportunity`.

This section is canonical. §3.5 points here. Do not let regulation appear in two places.

## §10.3 Cyber & Incident History — ~300 w · bar `T1–2×1` per incident

Documented incidents with dates, disclosed scope, and consequences (8-K disclosures, breach
notifications, regulatory findings) · disclosed security posture and certifications ·
post-incident investment or organisational change.

**An empty section is common and valid.** Write "no publicly disclosed cyber incidents identified
as of {date}" rather than reaching for something. Do not report unconfirmed breach-forum claims or
security-vendor blog speculation as incidents.

## §10.4 ESG Position — ~400 w · **Opt** (Core for `V-ENR`) · bar `T2×1` sustainability report

Ratings where actually retrievable · stated targets with baseline years and deadlines ·
controversies with sources · regulatory ESG exposure (CSRD, SEC climate, CBAM).

ESG ratings are mostly paywalled. Cite only what you retrieved; `access_basis: secondary-summary`
where you have public reporting of a rating. If the bar is unmet and the vertical is not `V-ENR`,
omit the section — it is Opt.

## §10.5 Risk Implications for Pursuit & Delivery — ~400 w · Model 7 · **the bridge section**

Score Model 7's five dimensions: client financial stability (25%) · estate and programme
complexity (25%) · procurement style (20%) · dependency risk (15%) · regulatory and data-residency
constraint (15%).

**Polarity is inverted here — higher score means higher risk.** Every other model in this dossier
is higher-is-better. State the inversion on the render (QA F6f) or the reader will misread it.

Then translate: which `R-nn` become delivery risks · which become commercial risks · which
constrain the operating model (offshore restrictions, data residency, validated environments,
authorisation boundaries).

**Write this vendor-neutrally.** "Data-residency requirements under {regime} constrain offshore
delivery for in-scope workloads" — not "the pursuing organization should propose an onshore model". The constraint is
the finding; §12.5 draws the conclusion. This is the boundary that keeps Tier 2 trustworthy to
delivery leaders rather than reading as pre-sales material.

Model 7 dim 3 (procurement style) usually rests on `[INFERENCE]` outside `V-GOV`. Say so — §12.5
depends on it and needs to know how firm the ground is.

## §10.6 Legal & Litigation Exposure — ~350 w · `+v2.2` · bar `T1×1` per matter · empty is valid

Material litigation and legal exposure as a distinct evidence class from §10.1's risk factors.

Per matter: nature · counterparty/regulator · status · disclosed financial exposure **only if the
client disclosed it** · what it signals. Sources: the 10-K/annual-report **legal-proceedings** note
(T1) · 8-K material-event filings · court dockets · credible legal press. Material matters that meet
the risk bar also become `R-nn` (category `regulatory`, `operational`, or `reputational`) so §10.5
and §11 can reference them.

**Two hard rules.** (1) **Never estimate an exposure figure.** If the client did not disclose a
dollar amount, the exposure is "undisclosed" — never a guess, never a plaintiff's demand reported
as the exposure (F4d-adjacent). (2) Distinguish *pending* from *settled/resolved*; a closed matter
with a paid settlement is a different signal from live litigation.

**An empty section is common and valid** for many companies: "no material litigation beyond
ordinary-course matters disclosed as of {date}". Do not trawl for minor suits to fill it.

## §10.7 Scenario Analysis & Stress Points — ~400 w · `+v2.2` · bar none (analytical synthesis)

Forward-looking, and explicitly analytical — **every statement here is `[INFERENCE]` or
`[ESTIMATE]` with a stated basis.** This is the one section that is honest modelling, not retrieval,
so it carries no evidence bar but every scenario must cite the evidenced drivers it rests on.

Identify the **2–3 variables that most move this client's capacity and timing** for transformation
(e.g. a policy/reimbursement change, a rate cycle, a commodity price, a demand shock, a refinancing
wall — drawn from §4.2 and §10.1 claims). Then Base / Bear / Bull:

- what each scenario assumes for those variables (cite the driver claim IDs),
- the directional effect on **investment capacity** and on **pursuit timing**,
- the observable signal that would tell you which scenario is unfolding.

Keep it tied to *this* client's economics — a generic macro paragraph is filler. The output feeds
§13.1 (timing) and the §1.1 thesis, and several of these signals become §13.6 kill-criteria monitors.
Do not model the pursuing organization revenue; model the *client's* capacity. This section stays vendor-neutral like the
rest of §10.

## Fragment duties

- `risks[]`: every `R-nn` with `pursuit_implication` populated from §10.5, **including litigation
  risks promoted from §10.6**.
- `scoring_inputs.delivery_risk`: full Model 7 block with the inversion noted.
- `handoff` to `opportunity`: regulatory deadlines with dates — urgency evidence for Model 4.
- `handoff` to `account-strategy`: delivery constraints from §10.5, for §12.5.
- `handoff` to `engagement`: compliance deadlines — §13.1 trigger events; §10.7 scenario signals —
  candidate §13.6 kill-criteria monitors.

## Traps

- Copying risk factors is the failure mode here. Distil, rate, and justify.
- Do not rate every risk High. A risk register where everything is severe carries no information.
- Regulatory horizon-scanning drifts into generic sector commentary. Tie every regime to evidenced
  applicability *for this client*.
- §10.5 is the boundary. One the pursuing organization-positioning sentence here fails F7a at BLOCKER severity and
  contaminates the tier separation the whole design rests on.
