export const meta = {
  name: 'aid-v3',
  description: 'Account Intelligence Dossier v3.0.0 — parallel Claude Code agent harness. 22 sections, evidence-locked, claim-ledgered, verification-gated. Markdown output.',
  phases: [
    { title: 'P0 Preflight',   detail: 'Entity resolution, ownership form, jurisdiction adapters, verticals, tier, budgets. Hard gate.' },
    { title: 'P1 Backbone',    detail: 'Fetch + normalize primary sources; precompute financials from XBRL; set expected source classes' },
    { title: 'P2 Wave A',      detail: 'Up to 10 concurrent vendor-neutral agents write §3 §4 §5 §6 §8 §9 §10 §13 §14 §17' },
    { title: 'P3 Wave B',      detail: '§7 §11 §12 §15 §16 + vertical packets — the sections that depend on Wave A' },
    { title: 'P4 Reconcile',   detail: 'Source dedup and state merge, then contradiction sweep and adversarial evidence audit' },
    { title: 'P5 Synthesis',   detail: '§18 opportunity register (mints O-nn), then §19 account strategy and §20 playbook concurrently' },
    { title: 'P6 Brief',       detail: '§1 executive summary (written last) and §2 methodology, concurrently' },
    { title: 'P7 Verification',detail: 'V1-V12 with fresh context; the six spec-mandated Pass checks; Overall Confidence / EQI' },
    { title: 'P8 Assemble',    detail: '§21.2-21.7 narrative appendices, then collate and generate §21.1/21.9/21.10/21.11/21.12' },
  ],
}

// ---------------------------------------------------------------------------
// Parameters. Pass via Workflow `args`. See harness/HARNESS_README.md.
// ---------------------------------------------------------------------------

// `args` may arrive as an object (inline) or a JSON string (some runtimes) — accept both.
const P = (typeof args === 'string' ? JSON.parse(args) : args) || {}

function req(key) {
  const v = P[key]
  if (v === undefined || v === null || v === '') {
    throw new Error(`aid-v3: required arg "${key}" is missing. See harness/HARNESS_README.md for the args contract.`)
  }
  return v
}

const CLIENT_LEGAL_NAME = req('client_legal_name')
const RESEARCH_AS_OF    = req('research_as_of')   // no Date.now() in workflow scripts — must be supplied
const SLUG              = req('slug')             // run directory name, e.g. "acme-2026-08"

const CLIENT_COMMON_NAME = P.client_common_name || CLIENT_LEGAL_NAME
const TICKER_OR_PRIVATE  = P.ticker_or_private  || 'AUTO-DETECT'
const PRIMARY_GEOGRAPHY  = P.primary_geography  || 'AUTO-DETECT'
const TARGET_VERTICAL    = P.target_vertical    || 'AUTO-DETECT'
const OUTPUT_TIER        = (P.output_tier || 'FULL_ANNEX').toUpperCase()
const CAPABILITY_PACK    = P.capability_pack       || 'NOT_ATTACHED'
const INPUT_SHEET        = P.account_team_input_sheet  || 'NOT_ATTACHED'
const ACCOUNT_CTX    = P.account_context       || 'NONE'
const KNOWN_RELATIONSHIP = P.known_relationship_context || 'NONE'
const PURSUIT_OBJECTIVES = P.strategic_pursuit_objectives || 'NONE'

const H       = P.harness_dir || 'harness'
const RUN_DIR = P.run_dir     || `runs/${SLUG}`

if (!['EXECUTIVE', 'STANDARD', 'FULL_ANNEX'].includes(OUTPUT_TIER)) {
  throw new Error(`aid-v3: output_tier must be EXECUTIVE | STANDARD | FULL_ANNEX, got "${OUTPUT_TIER}"`)
}

// ---------------------------------------------------------------------------
// Prompt construction.
//
// The workflow script has no filesystem access, so it never embeds blueprint or
// brief text. It passes PATHS; each agent reads them itself. That keeps the
// entire prompt library editable as plain Markdown without touching this file.
// ---------------------------------------------------------------------------

const PARAMS = `
== ENGAGEMENT PARAMETERS ==
CLIENT_LEGAL_NAME:        ${CLIENT_LEGAL_NAME}
CLIENT_COMMON_NAME:       ${CLIENT_COMMON_NAME}
TICKER_OR_PRIVATE_STATUS: ${TICKER_OR_PRIVATE}
PRIMARY_GEOGRAPHY:        ${PRIMARY_GEOGRAPHY}
TARGET_VERTICAL:          ${TARGET_VERTICAL}
RESEARCH_AS_OF_DATE:      ${RESEARCH_AS_OF}
OUTPUT_TIER:              ${OUTPUT_TIER}
RUN_DIR:                  ${RUN_DIR}
HARNESS_DIR:              ${H}

== GATED INPUTS (sole permitted basis for any organization content) ==
CAPABILITY_PACK:          ${CAPABILITY_PACK}
ACCOUNT_TEAM_INPUT_SHEET:     ${INPUT_SHEET}
ACCOUNT_CONTEXT:          ${ACCOUNT_CTX}
KNOWN_RELATIONSHIP_CONTEXT:   ${KNOWN_RELATIONSHIP}
STRATEGIC_PURSUIT_OBJECTIVES: ${PURSUIT_OBJECTIVES}
`.trim()

/**
 * Build an agent prompt.
 * @param {string} briefFile  filename under harness/prompts/briefs/
 * @param {string} label      agent label — must match prompts/id-allocation.md
 * @param {string} upstream   digests / notes from prior steps ('' for P0)
 * @param {string} extra      step-specific instructions appended verbatim
 */
function build(briefFile, label, upstream, extra) {
  return `You are agent "${label}" in the AID v3.0.0 harness.

READ THESE FILES BEFORE DOING ANYTHING ELSE, IN THIS ORDER:
  1. ${H}/prompts/system-aid-analyst.md        — the constitution; non-negotiable, wins on conflict
  2. ${H}/blueprint/evidence-policy.md         — status, confidence, corroboration, negative evidence
  3. ${H}/prompts/briefs/_common.md            — shared preamble
  4. ${H}/prompts/briefs/${briefFile}          — YOUR brief; it defines your scope
  5. ${H}/prompts/id-allocation.md             — find YOUR block; mint nothing outside it
  6. ${H}/blueprint/aid-blueprint-v3.md        — the section blueprint
  7. ${H}/blueprint/section-contracts.md       — envelopes, evidence bars, dependencies

Your brief names any further files you need: blueprint/jurisdiction-adapters.md,
blueprint/tooling-map.md, blueprint/vertical-modules.md, blueprint/scoring-rubrics.md,
blueprint/verification-protocol.md, state/state.schema.json, and the run artefacts under ${RUN_DIR}.

${PARAMS}
${upstream ? `\n== UPSTREAM CONTEXT ==\n${upstream}\n` : ''}${extra ? `\n== STEP NOTES ==\n${extra}\n` : ''}
Write your artefacts to disk as your brief specifies, then return a digest of AT MOST 200 WORDS.
The digest is concatenated into every downstream agent's prompt, so length here costs the whole
run. Do not return your section text — it belongs on disk.`
}

// ---------------------------------------------------------------------------
// Structured returns
// ---------------------------------------------------------------------------

const VERTICALS = ['V-HLS','V-BFSI','V-RCG','V-ENR','V-MFG','V-TMT','V-TTH','V-GOV','V-AND','V-REC','V-PSE','NONE']

const PREFLIGHT_SCHEMA = {
  type: 'object',
  required: ['legal_name', 'ownership_form', 'jurisdictions', 'vertical_primary', 'vertical_confidence', 'digest'],
  properties: {
    legal_name:          { type: 'string' },
    ownership_form:      { enum: ['public','private-vc','private-pe','soe','subsidiary','nonprofit','cooperative','partnership','family-group'] },
    jurisdictions:       { type: 'array', items: { enum: ['us-sec','canada','uk-eu','india','japan','korea','hk','sg','au-nz','brazil','generic'] } },
    reporting_standard:  { type: ['string', 'null'] },
    ticker:              { type: ['string', 'null'] },
    lei:                 { type: ['string', 'null'] },
    cik:                 { type: ['string', 'null'] },
    fy_end:              { type: ['string', 'null'] },
    latest_fy_label:     { type: ['string', 'null'] },
    languages:           { type: 'array', items: { type: 'string' } },
    vertical_primary:    { enum: VERTICALS },
    vertical_secondary:  { type: 'array', items: { enum: VERTICALS } },
    vertical_confidence: { enum: ['High', 'Medium', 'Low'] },
    tier:                { enum: ['EXECUTIVE', 'STANDARD', 'FULL_ANNEX'] },
    backbone_sources_registered: { type: 'integer' },
    entity_ambiguity:    { type: ['string', 'null'], description: 'Non-null when resolution required an assumption. An unclosable ambiguity is a STOP condition.' },
    anticipated_gaps:    { type: 'array', items: { type: 'string' } },
    digest:              { type: 'string' },
  },
}

const VERIFICATION_SCHEMA = {
  type: 'object',
  required: ['result', 'blockers', 'majors', 'minors', 'eqi', 'overall_confidence', 'digest'],
  properties: {
    result:             { enum: ['PASS', 'PASS WITH DISCLOSURES', 'FAIL'] },
    overall_confidence: { enum: ['Strong', 'Adequate', 'Thin', 'Insufficient'] },
    eqi:                { type: 'number' },
    eqi_components:     { type: 'object' },
    blockers:           { type: 'integer' },
    majors:             { type: 'integer' },
    minors:             { type: 'integer' },
    checks_executed:    { type: 'integer' },
    checks_passed:      { type: 'integer' },
    spec_checks: {
      type: 'object',
      description: 'The six mandated Verification Pass checks',
      properties: {
        numeric:        { enum: ['pass','fail','partial','pending'] },
        claims:         { enum: ['pass','fail','partial','pending'] },
        contradiction:  { enum: ['pass','fail','partial','pending'] },
        entity:         { enum: ['pass','fail','partial','pending'] },
        status_honesty: { enum: ['pass','fail','partial','pending'] },
        coverage:       { enum: ['pass','fail','partial','pending'] },
      },
    },
    disclosed_failures:    { type: 'array', items: { type: 'string' } },
    budget_limited_topics: { type: 'array', items: { type: 'string' } },
    digest:                { type: 'string' },
  },
}

// ---------------------------------------------------------------------------
// P0 — Preflight. Hard gate.
// ---------------------------------------------------------------------------

phase('P0 Preflight')
log(`AID v3.0.0 — ${CLIENT_LEGAL_NAME} · as-of ${RESEARCH_AS_OF} · tier ${OUTPUT_TIER} · run dir ${RUN_DIR}`)

const pre = await agent(
  build('00-preflight.md', 'preflight', '', `Create the run directory structure first:
  ${RUN_DIR}/sections/  ${RUN_DIR}/state/fragments/  ${RUN_DIR}/qa/

Then write ${RUN_DIR}/sections/00-run-contract.md (§0) and ${RUN_DIR}/state/state.json as
schema-3.0 initial state: run_contract (entity, ownership_form, jurisdictions, reporting_standard,
languages, verticals, tier "${OUTPUT_TIER}", fetch_budget, capability_pack "${CAPABILITY_PACK}",
account_team_input_sheet "${INPUT_SHEET}", as_of "${RESEARCH_AS_OF}"), id_blocks copied from
${H}/prompts/id-allocation.md, the S-0001..S-0049 backbone manifest, and any carry_forward_facts you
could source at Tier 1-2.

Twenty-seven agents launch on this file and cannot ask you questions. Entity identity, ownership
form, and jurisdiction adapter are the three decisions that determine whether the rest of the run
researches the right company under the right rules.

UNRESOLVABLE ENTITY AMBIGUITY IS A STOP CONDITION. Set entity_ambiguity and say so — researching
the wrong company thoroughly is the worst outcome this harness can produce.`),
  { label: 'preflight', phase: 'P0 Preflight', schema: PREFLIGHT_SCHEMA }
)

if (!pre) throw new Error('aid-v3: P0 preflight failed. Cannot proceed — every downstream agent depends on state.json.')

log(`Preflight: ${pre.legal_name} · ${pre.ownership_form} · ${(pre.jurisdictions || []).join('+') || 'generic'} · ${pre.vertical_primary} (${pre.vertical_confidence}) · ${pre.backbone_sources_registered || 0} backbone sources`)
if (pre.entity_ambiguity) log(`⚠ Entity ambiguity recorded: ${pre.entity_ambiguity}`)
if (pre.vertical_confidence === 'Low') log('⚠ Vertical confidence Low — Core blueprint only, no vertical module')

const CTX0 = `From P0 (preflight):
- Entity: ${pre.legal_name}${pre.ticker ? ` (${pre.ticker})` : ''}${pre.lei ? ` · LEI ${pre.lei}` : ''} · ownership_form: ${pre.ownership_form}
- Jurisdiction adapter(s): ${(pre.jurisdictions || ['generic']).join(', ')} · reporting standard: ${pre.reporting_standard || 'not established'}
- Research languages: ${(pre.languages || ['en']).join(', ')}
- Fiscal year: ${pre.fy_end || 'not established'} · latest FY label: ${pre.latest_fy_label || 'not established'}
- Verticals: ${pre.vertical_primary} primary${(pre.vertical_secondary || []).length ? `, ${pre.vertical_secondary.join('/')} secondary` : ''} (confidence ${pre.vertical_confidence})
- Output tier: ${OUTPUT_TIER} · Capability Pack: ${CAPABILITY_PACK} · Account-Team Input Sheet: ${INPUT_SHEET}
${pre.entity_ambiguity ? `- ⚠ Entity ambiguity: ${pre.entity_ambiguity}` : ''}
- Anticipated gaps: ${(pre.anticipated_gaps || []).join('; ') || 'none declared'}
- Run contract and backbone sources S-0001..S-0049 are in ${RUN_DIR}/state/state.json. CITE THEM; DO NOT RE-REGISTER.

${pre.digest}`

// ---------------------------------------------------------------------------
// P1 — Backbone. Primary sources + precomputed financials.
// ---------------------------------------------------------------------------

phase('P1 Backbone')

const backbone = await agent(
  build('01-backbone.md', 'backbone', CTX0,
    `Write ${RUN_DIR}/state/precomputed-financials.json and
${RUN_DIR}/state/fragments/backbone.json. You write NO dossier section.

Deterministic math belongs outside the model. Pull XBRL where the adapter provides it and emit the
statements and derived metrics AS FILED. Where XBRL is unavailable, set unavailable_reason
explicitly — if the financials agent does not know the block is missing, it will assume its
arithmetic was checked when it was not.

Also record, per top-level section §3-§17, the source classes the jurisdiction adapter and vertical
module say SHOULD exist. That becomes the "expected" column of the §21.12 scorecard, so a section
that retrieves nothing can be distinguished from one where nothing was there to retrieve.

Your fetch budget is 15. Spend it on documents many sections need, not on any one section's detail.`),
  { label: 'backbone', phase: 'P1 Backbone' }
)

if (!backbone) log('⚠ Backbone agent returned nothing — §6 will recompute from filings and precomputed-financials will be absent')

const CTX1 = `${CTX0}\n\n== P1 (backbone) ==\n${backbone || '(no return — precomputed-financials may be absent; §6 must recompute from stated filing figures with inputs shown)'}`

// ---------------------------------------------------------------------------
// P2 — Research Wave A. vendor-neutral, fully concurrent.
//
// Spec phases 2-6 are collapsed into two dependency waves. Wave A holds every
// section with no intra-body dependency; Wave B holds the five that block on a
// Wave A output. See ARCHITECTURE.md for the phase->wave mapping.
// ---------------------------------------------------------------------------

phase('P2 Wave A')

const WAVE_A = [
  { brief: '02-corporate.md',      label: 'corporate',      out: '03-company.md' },
  { brief: '03-market.md',         label: 'market',         out: '04-market.md' },
  { brief: '04-business-model.md', label: 'business-model', out: '05-business-model.md' },
  { brief: '05-financials.md',     label: 'financials',     out: '06-financials.md' },
  { brief: '06-technology.md',     label: 'technology',     out: '08-technology.md' },
  { brief: '07-strategy.md',       label: 'strategy',       out: '09-strategy.md' },
  { brief: '08-leadership.md',     label: 'leadership',     out: '10-leadership.md' },
  { brief: '09-signals.md',        label: 'signals',        out: '13-signals.md' },
  { brief: '10-risk.md',           label: 'risk',           out: '14-risk.md' },
  { brief: '11-esg.md',            label: 'esg',            out: '17-esg.md' },
]

// EXECUTIVE tier researches only what §1's synthesis actually consumes.
const WAVE_A_EXEC = ['corporate', 'financials', 'technology', 'strategy', 'leadership', 'risk']

const waveA = OUTPUT_TIER === 'EXECUTIVE'
  ? WAVE_A.filter(a => WAVE_A_EXEC.includes(a.label))
  : WAVE_A

const NEUTRAL_NOTE = `§3-§17 ARE VENDOR-NEUTRAL. Promotional references to the pursuing organization must not appear in your
output. V7a is a BLOCKER. The single exception in the whole range is §15.6, owned by ai-readiness.`

const aTasks = waveA.map(a => () => agent(
  build(a.brief, a.label, CTX1,
    `Write your section to ${RUN_DIR}/sections/${a.out} and your fragment to
${RUN_DIR}/state/fragments/${a.label}.json.

You run CONCURRENTLY with ${waveA.length - 1} peer agents. You cannot see their output and they
cannot see yours. Where you need a fact another agent owns, take it from state.json
carry_forward_facts or write "see §x.y" — never invent it, never block.

${NEUTRAL_NOTE}${OUTPUT_TIER === 'EXECUTIVE' ? '\n\nEXECUTIVE tier: research only what §1 consumes. Envelopes are ~0.4x. Skip Opt subsections entirely.' : ''}`),
  { label: a.label, phase: 'P2 Wave A' }
))

const aLabels = waveA.map(a => a.label)
const aOut = await parallel(aTasks)
const aMissing = aLabels.filter((_, i) => !aOut[i])
log(`Wave A: ${aLabels.length - aMissing.length}/${aLabels.length} returned${aMissing.length ? ` — NO RETURN FROM: ${aMissing.join(', ')} (V10e will flag missing fragments)` : ''}`)

const A_DIGESTS = aOut
  .map((d, i) => (d ? `--- ${aLabels[i]} ---\n${d}` : `--- ${aLabels[i]} ---\n(no return — section and fragment may be missing)`))
  .join('\n\n')

// ---------------------------------------------------------------------------
// P3 — Research Wave B. Each depends on a Wave A section.
// ---------------------------------------------------------------------------

const CTX2 = `${CTX1}\n\n== WAVE A DIGESTS ==\n${A_DIGESTS}`

const WAVE_B = [
  { brief: '12-operations.md',   label: 'operations',   out: '07-operations.md',   dep: '§5 (business-model)' },
  { brief: '13-competition.md',  label: 'competition',  out: '11-competition.md',  dep: '§6 (financials)' },
  { brief: '14-customers.md',    label: 'customers',    out: '12-customers.md',    dep: '§5 (business-model)' },
  { brief: '15-ai-readiness.md', label: 'ai-readiness', out: '15-ai-readiness.md', dep: '§8 (technology), §7.5 (operations)' },
  { brief: '16-vendors.md',      label: 'vendors',      out: '16-vendors.md',      dep: '§8 (technology)' },
]

const runVertical = OUTPUT_TIER !== 'EXECUTIVE'
  && pre.vertical_primary !== 'NONE'
  && pre.vertical_confidence !== 'Low'

if (OUTPUT_TIER === 'EXECUTIVE') {
  log('EXECUTIVE tier — Wave B skipped; §1 synthesis runs on Wave A only')
}

let bOut = []
let bLabels = []
let B_DIGESTS = '(Wave B not run — EXECUTIVE tier)'

if (OUTPUT_TIER !== 'EXECUTIVE') {
  phase('P3 Wave B')

  const bTasks = WAVE_B.map(b => () => agent(
    build(b.brief, b.label, CTX2,
      `Write your section to ${RUN_DIR}/sections/${b.out} and your fragment to
${RUN_DIR}/state/fragments/${b.label}.json.

You depend on ${b.dep} — READ IT FROM DISK under ${RUN_DIR}/sections/ before you start. Do not
re-research what it established; cite its claim IDs.

You run CONCURRENTLY with ${WAVE_B.length - 1} peer agents.

${NEUTRAL_NOTE}`),
    { label: b.label, phase: 'P3 Wave B' }
  ))
  bLabels = WAVE_B.map(b => b.label)

  if (runVertical) {
    bTasks.push(() => agent(
      build('17-vertical.md', 'vertical', CTX2,
        `Module in force: ${pre.vertical_primary} (confidence ${pre.vertical_confidence})${(pre.vertical_secondary || []).length ? ` · secondary: ${pre.vertical_secondary.join(', ')}` : ''}.
Write ${RUN_DIR}/sections/21-vertical-annex.md, ${RUN_DIR}/state/fragments/vertical-packets.json,
and ${RUN_DIR}/state/fragments/vertical.json.

Your anchor packets SUPPLEMENT the owning agents' sections; they never replace them. Most owning
agents have already written, so route each packet through handoff and put anything that lands too
late into the annex with a cross-reference — and SAY IN YOUR DIGEST which packets landed late.

The candidate lists in vertical-modules.md are SEARCH CHECKLISTS, NOT FACTS. Writing that this
client runs a system because the module says it is typical is the single most likely fabrication in
this harness.`),
      { label: 'vertical', phase: 'P3 Wave B' }
    ))
    bLabels.push('vertical')
  }

  bOut = await parallel(bTasks)
  const bMissing = bLabels.filter((_, i) => !bOut[i])
  log(`Wave B: ${bLabels.length - bMissing.length}/${bLabels.length} returned${bMissing.length ? ` — NO RETURN FROM: ${bMissing.join(', ')}` : ''}`)

  B_DIGESTS = bOut
    .map((d, i) => (d ? `--- ${bLabels[i]} ---\n${d}` : `--- ${bLabels[i]} ---\n(no return — section and fragment may be missing)`))
    .join('\n\n')
}

// ---------------------------------------------------------------------------
// P4 — Reconcile. Merge first (2a/2b sequencing matters), then sweep + audit.
// ---------------------------------------------------------------------------

phase('P4 Reconcile')

const CTX3 = `${CTX2}\n\n== WAVE B DIGESTS ==\n${B_DIGESTS}`

const mergeOut = await agent(
  build('18-source-merge.md', 'source-merge', CTX3,
    `Read every fragment in ${RUN_DIR}/state/fragments/. Write the consolidated
${RUN_DIR}/state/state.json, ${RUN_DIR}/qa/source-rewrite-map.json, and
${RUN_DIR}/state/fragments/source-merge.json. Apply the rewrite map to every section file on disk.

Your highest-value output is the FALSE TRIANGULATION LIST: every claim whose confidence rests on
multiple sources that collapsed to one document after dedup. That is confidence inflation no other
check can see, and it exists only because of parallelism.

Promote a canonical fact ONLY where no peer disagreed. Where two agents disagree, set contested:true
and OMIT it from downstream use — do not average, do not pick the more recent by default. Omitting a
contested fact is always better than guessing one.

You are a collator, not a corrector. RECORD structural defects; do not repair them.`),
  { label: 'source-merge', phase: 'P4 Reconcile' }
)

const CTX3B = `${CTX3}\n\n--- source-merge ---\n${mergeOut || '(no return)'}`

const [contraOut, auditOut] = await parallel([
  () => agent(
    build('19-contradiction.md', 'contradiction', CTX3B,
      `Write ${RUN_DIR}/sections/21-11-contradictions.md and
${RUN_DIR}/state/fragments/contradiction.json.

Priority order: (1) contested canonical facts from source-merge — two agents reporting different
values for the same fact is the signature failure of a parallel harness and it corrupts everything
built on top; (2) numeric conflicts against precomputed-financials; (3) cross-section value
conflicts; (4) status conflicts; (5) source-level conflicts.

Before minting an X-nnnn, check the four false-positive causes: different periods, different
entities, different bases (adjusted vs statutory), different units. Reconciling a real difference
away is as damaging as missing a conflict.

Every resolution carries a RATIONALE naming the claim-sensitive rule you applied. An open
contradiction, clearly stated, is a legitimate output.`),
    { label: 'contradiction', phase: 'P4 Reconcile' }
  ),
  () => agent(
    build('20-evidence-audit.md', 'evidence-audit', CTX3B,
      `Write ${RUN_DIR}/qa/evidence-audit.json and ${RUN_DIR}/state/fragments/evidence-audit.json.

YOU ARE ADVERSARIAL BY MANDATE. For every materiality:high claim, try to REFUTE it. Default to
REFUTED when uncertain.

You run before §18 precisely so a bad claim cannot become an opportunity, then a message, then an
action, then a line in the executive summary. Catching it here costs one downgrade; catching it at
verification costs a rebuild of §18-§20.

Your refuted list is BINDING: no O-nn may cite a refuted claim as need evidence (V3f, BLOCKER).

If you return a high confirm rate on a first pass, you did not open the sources.`),
    { label: 'evidence-audit', phase: 'P4 Reconcile' }
  ),
])

log('P4 complete: sources deduplicated, state merged, contradictions swept, evidence audited')

// ---------------------------------------------------------------------------
// P5 — Synthesis. §18 first (mints O-nn), then §19 and §20 concurrently.
// ---------------------------------------------------------------------------

phase('P5 Synthesis')

const CTX4 = `${CTX3}

== P4 RECONCILIATION ==
source-merge:   ${mergeOut  || '(no return)'}
contradiction:  ${contraOut || '(no return)'}
evidence-audit: ${auditOut  || '(no return)'}

Merged state is at ${RUN_DIR}/state/state.json. The refuted-claim list in
${RUN_DIR}/qa/evidence-audit.json is BINDING.`

const oppOut = await agent(
  build('21-opportunity.md', 'opportunity', CTX4,
    `Write ${RUN_DIR}/sections/18-opportunity.md and ${RUN_DIR}/state/fragments/opportunity.json.

You run alone so §19 and §20 have stable O-nn IDs to reference. You are the sole minter.

TIER 3 BEGINS HERE: the pursuing organization content is now permitted, under the gates.
- Capability, offering, accelerator, and proof-point references come ONLY from the Capability Pack
  (${CAPABILITY_PACK}), cited [CAPABILITY-PACK]. Without a pack: [INTERNAL: validate with practice].
- Win probability, account revenue, relationship strength, and stakeholder access CANNOT be derived
  from public data. Account-Team Input Sheet is ${INPUT_SHEET}. Without it every such field is
  exactly [INTERNAL REQUIRED] (V8f, BLOCKER).

Ranges and sizing logic always. NEVER a bare number — a bare authoritative-looking figure is the
most damaging thing this section can produce, because it is the number that ends up on a slide.`),
  { label: 'opportunity', phase: 'P5 Synthesis' }
)

if (!oppOut) log('⚠ Opportunity agent returned nothing — §19 and §20 will have no O-nn to reference')

const CTX5 = `${CTX4}\n\n== OPPORTUNITY REGISTER (§18) ==\n${oppOut || '(no return — §18 unavailable)'}`

const [stratOut, playOut] = await parallel([
  () => agent(
    build('22-account-strategy.md', 'account-strategy', CTX5,
      `Write ${RUN_DIR}/sections/19-account-strategy.md and
${RUN_DIR}/state/fragments/account-strategy.json.

You run CONCURRENTLY with playbook. You own positioning, messaging, competitive strategy, the
commercial construct, and the MEDDPICC matrix. They own timing, horizons, and the action plan.
DO NOT WRITE ACTIONS OR DATES — you would produce a second, conflicting plan.

§19.1 weaknesses and threats MUST be populated (V7g). An all-strengths SWOT is a failure.
§19.7 completes Model 8 dimension 5, deferred from §16.5.
§19.8 derives from §7.4 sourcing posture — read it before writing, it is the most expensive thing
in the dossier to get wrong.
§19.9 MEDDPICC: all eight fields, evidence or [INTERNAL REQUIRED], never blank (V7f).`),
    { label: 'account-strategy', phase: 'P5 Synthesis' }
  ),
  () => agent(
    build('23-playbook.md', 'playbook', CTX5,
      `Write ${RUN_DIR}/sections/20-playbook.md and ${RUN_DIR}/state/fragments/playbook.json.

You run CONCURRENTLY with account-strategy. You own timing, horizon sequencing, relationship
priorities, and the A-nn action register. They own positioning and messaging.
DO NOT WRITE POSITIONING OR MESSAGING CONTENT.

§20.6 coverage is mechanically checked (V7e): every HYPOTHESIS/VALIDATE opportunity and every
materiality:high gap must appear as an action here or as a §19.9 validation item. Read
account-strategy's handoff to see what §19.9 covers, then cover the remainder.

Tier 3 is structurally optimistic. Dated actions with falsifiable success metrics are the
counterweight — do not soften them to protect the thesis.`),
    { label: 'playbook', phase: 'P5 Synthesis' }
  ),
])

log('P5 complete: opportunity register, account strategy, pursuit playbook')

// ---------------------------------------------------------------------------
// P6 — §1 (written last) and §2, concurrently. Neither researches.
// ---------------------------------------------------------------------------

phase('P6 Brief')

const CTX6 = `${CTX4}

== TIER 3 ==
opportunity:      ${oppOut   || '(no return)'}
account-strategy: ${stratOut || '(no return)'}
playbook:         ${playOut  || '(no return)'}`

const [execOut, methOut] = await parallel([
  () => agent(
    build('24-exec-brief.md', 'exec-brief', CTX6,
      `Write ${RUN_DIR}/sections/01-exec-brief.md (§1.1-1.7) and
${RUN_DIR}/state/fragments/exec-brief.json.

NO NEW RESEARCH. NO NEW SOURCES (V8c). Every §1 statement carries a C-/O-/R-/A-/P-/G- reference; a
§1 sentence with no ID is a BLOCKER (V8a). Nothing appears in §1 that is not in the body (V8b).

Writing §1 last is the structural decision that removes the incentive to fabricate. If you want to
say something the body does not support, that is a G-24nn gap — hand it to methodology for §2.5.

§1.3 must be consistent with the §1.6 readiness band (V8d, BLOCKER). If the evidence says nurture,
write nurture.
§1.6 Stakeholder Access: Account-Team Input Sheet is ${INPUT_SHEET}. Without it, NOT ASSESSED and
the remaining five weights renormalize from 90% to 100% — SHOW THE RENORMALIZATION (V5c, BLOCKER).
§1.4 win-probability column: Input-Sheet-derived or [INTERNAL REQUIRED] throughout (V8f).
A carry_forward_fact marked contested is NOT stated in §1.1 — write "contested, see §21.11".`),
    { label: 'exec-brief', phase: 'P6 Brief' }
  ),
  () => agent(
    build('25-methodology.md', 'methodology', CTX6,
      `Write ${RUN_DIR}/sections/02-methodology.md (§2.1-2.6) and
${RUN_DIR}/state/fragments/methodology.json.

NO NEW RESEARCH, NO NEW SOURCES. You report what the run actually did, from merged state.

§2.5 is the most important subsection you own: every autonomous assumption any agent recorded,
dossier-level high-materiality gaps, per-section confidence, and interpretation constraints — what
the reader should specifically NOT conclude.

§2.3 reports the retrieval-status distribution INCLUDING failures. A manifest with 14 paywalled and
6 dead entries out of 180 tells the reader something real; hiding them makes §2.3 marketing.

You are describing the dossier's limits, not apologising for them. Flat and specific — no hedging
language that makes thin evidence sound adequate.`),
    { label: 'methodology', phase: 'P6 Brief' }
  ),
])

// ---------------------------------------------------------------------------
// P7 — Verification. Fresh context, adversarial.
// ---------------------------------------------------------------------------

phase('P7 Verification')

const ver = await agent(
  build('26-verification.md', 'verification',
    `You are running with FRESH CONTEXT and did not write this dossier. The digests below are
context only — verify against the ARTEFACTS on disk, not against these claims about them.

${CTX0}

Sections are in ${RUN_DIR}/sections/. Merged state is ${RUN_DIR}/state/state.json. The adversarial
audit is ${RUN_DIR}/qa/evidence-audit.json.`,
    `Execute ${H}/blueprint/verification-protocol.md V1-V12 IN FULL. Write
${RUN_DIR}/qa/verification-report.md, ${RUN_DIR}/qa/verification-report.json,
${RUN_DIR}/sections/21-8-verification.md, and ${RUN_DIR}/state/fragments/verification.json.

YOUR JOB IS TO FIND FAILURES, NOT TO CERTIFY SUCCESS. Every prior agent had an incentive to produce
a complete-looking section; you are the only one whose incentive runs the other way. Zero failures
across ~60 checks on a first run means you did not run them — re-read V3e, V5a, V6e, V11d.

The trace that matters most is V5a: take each materiality:high claim whose status is not CONFIRMED
and follow it origin -> §18 need evidence -> §19.4 message -> §20.6 action -> §1.2 finding,
confirming the qualifier survived every hop. The failure is rarely a lie; it is an ANNOUNCED
programme that loses its qualifier at the third restatement.

Any failure that cannot be remediated is DISCLOSED in the Verification Summary and handed to §2.5.
NEVER MASKED.

budget_limited_topics is not cosmetic: it tells the orchestrator that extending a fetch budget and
re-running a topic would materially improve the dossier, as opposed to there being nothing to find.`),
  { label: 'verification', phase: 'P7 Verification', schema: VERIFICATION_SCHEMA }
)

if (ver) {
  log(`Verification: ${ver.result} · Overall Confidence ${ver.overall_confidence} (EQI ${ver.eqi}) · ${ver.blockers}B / ${ver.majors}M / ${ver.minors}m · ${ver.checks_passed}/${ver.checks_executed} checks passed`)
  if (ver.blockers > 0) log(`⚠ ${ver.blockers} BLOCKER(s) unremediated — see ${RUN_DIR}/qa/verification-report.md before any use`)
  if (ver.overall_confidence === 'Insufficient') log('⚠ Overall Confidence Insufficient — DO NOT PRESENT. Re-run with better sources or reduce scope.')
  if ((ver.budget_limited_topics || []).length) log(`ℹ Stopped on budget (not diminishing returns): ${ver.budget_limited_topics.join(', ')} — extending the budget and re-running these would materially improve coverage`)
} else {
  log('⚠ Verification returned nothing — dossier is UNVERIFIED')
}

// ---------------------------------------------------------------------------
// P8 — Appendices, then assembly.
// ---------------------------------------------------------------------------

phase('P8 Assemble')

const appOut = await agent(
  build('27-appendices.md', 'appendices', `${CTX0}

Verification: ${ver ? `${ver.result} · ${ver.overall_confidence} (EQI ${ver.eqi})` : 'DID NOT COMPLETE'}
signals digest: ${aOut[aLabels.indexOf('signals')] || '(no return)'}`,
    `Write ${RUN_DIR}/sections/21-appendices.md (§21.2-21.7) and
${RUN_DIR}/state/fragments/appendices.json.

You write the NARRATIVE appendices only. §21.1, §21.9, §21.10, §21.11, and §21.12 are generated
deterministically by assembly from merged state — DO NOT DUPLICATE THEM.

You are collating, not researching. §21.3's reconciliation from statutory to any adjusted figure
used in §6 is the point of that appendix. §21.6 attribution is the trap — patents and repos attach
to specific legal entities; verify against §3.6.

Opt subsections are honest about being empty. An absent heading is not.`),
  { label: 'appendices', phase: 'P8 Assemble' }
)

const finalOut = await agent(
  build('28-assembly.md', 'assembly', `${CTX0}

Verification: ${ver ? `${ver.result} · Overall Confidence ${ver.overall_confidence} · EQI ${ver.eqi} · ${ver.blockers}B/${ver.majors}M/${ver.minors}m` : 'DID NOT COMPLETE'}
${ver && (ver.disclosed_failures || []).length ? `Disclosed failures: ${ver.disclosed_failures.join('; ')}` : ''}
exec-brief:  ${execOut || '(no return)'}
methodology: ${methOut || '(no return)'}
appendices:  ${appOut  || '(no return)'}`,
    `Assemble ${RUN_DIR}/${SLUG}-aid.md from ${RUN_DIR}/sections/ in blueprint order
(§0 → §1 → §2 → §3 … §17 → §18 → §19 → §20 → §21) and generate the register appendices —
§21.1 Source Manifest, §21.9 Claim Ledger, §21.10 Account-Team Input Sheet, §21.11 Contradiction &
Data-Gap Register, §21.12 Source-Completeness Scorecard — from ${RUN_DIR}/state/state.json.
Fragment: ${RUN_DIR}/state/fragments/assembly.json.

§1 is placed FIRST and was written LAST. Do not reorder to improve flow — the numbering is the
contract (V6a).

You mint nothing and write no analysis. An unresolved reference is RECORDED in §21.8, never invented
into existence — creating a manifest entry to make a citation resolve converts a traceability
failure into a fabricated source.

§21.1 includes failed retrievals with their reason. §21.12 visibly distinguishes topics that stopped
on budget from those that stopped on diminishing returns — that is the most actionable line in the
appendices.

Put Overall Confidence and Entity Resolved in the title block so a reader knows how much to trust
the document before reading a word of it. Markdown only.`),
  { label: 'assembly', phase: 'P8 Assemble' }
)

// ---------------------------------------------------------------------------

log(`Done. Dossier: ${RUN_DIR}/${SLUG}-aid.md`)

return {
  client: CLIENT_LEGAL_NAME,
  research_as_of: RESEARCH_AS_OF,
  output_tier: OUTPUT_TIER,
  run_dir: RUN_DIR,
  dossier: `${RUN_DIR}/${SLUG}-aid.md`,
  entity: { legal_name: pre.legal_name, ticker: pre.ticker || null, lei: pre.lei || null, cik: pre.cik || null },
  ownership_form: pre.ownership_form,
  jurisdictions: pre.jurisdictions || [],
  vertical_primary: pre.vertical_primary,
  vertical_confidence: pre.vertical_confidence,
  entity_ambiguity: pre.entity_ambiguity || null,
  wave_a_launched: aLabels.length,
  wave_a_returned: aOut.filter(Boolean).length,
  wave_b_launched: bLabels.length,
  wave_b_returned: bOut.filter(Boolean).length,
  verification: ver || null,
  assembly: finalOut || null,
}
