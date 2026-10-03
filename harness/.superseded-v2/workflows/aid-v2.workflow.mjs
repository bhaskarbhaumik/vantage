export const meta = {
  name: 'aid-v2',
  description: 'Account Intelligence Dossier v2.1 — parallel Claude Code agent harness. Markdown output, evidence-first, claim-registered, QA-gated.',
  phases: [
    { title: 'P0 Scope',      detail: 'Entity, listing status, vertical module; pre-register core sources S-001..S-049' },
    { title: 'P1 Reality',    detail: 'Up to 10 concurrent vendor-neutral research agents write Tier 2 (§2-§10) + vertical packets' },
    { title: 'P2 Reconcile',  detail: 'Contradiction sweep + adversarial evidence audit, then source dedup and state merge' },
    { title: 'P3 Pursuit',    detail: 'Opportunity register (§11), then account strategy (§12) and engagement plan (§13) concurrently' },
    { title: 'P4 Brief',      detail: 'Executive Decision Brief (§1) derived last from the body; §0.4 final, §0.6 reader map' },
    { title: 'P5 QA',         detail: 'F1-F10 gate, Evidence Quality Index, disclosure of unremediated failures' },
    { title: 'P6 Assemble',   detail: 'Collate sections, generate Appendices A-L from the registers, verify every ID resolves' },
  ],
}

// ---------------------------------------------------------------------------
// Parameters. Pass via Workflow `args`. See harness-v2/README.md.
// ---------------------------------------------------------------------------

// `args` may arrive as an object (inline) or a JSON string (some runtimes) — accept both.
const P = (typeof args === 'string' ? JSON.parse(args) : args) || {}

function req(key) {
  const v = P[key]
  if (v === undefined || v === null || v === '') {
    throw new Error(`aid-v2: required arg "${key}" is missing. See harness-v2/README.md for the args contract.`)
  }
  return v
}

const CLIENT_LEGAL_NAME = req('client_legal_name')
const RESEARCH_AS_OF    = req('research_as_of')       // no Date.now() in workflow scripts — must be supplied
const SLUG              = req('slug')                 // run directory name, e.g. "acme-2026-08"

const CLIENT_COMMON_NAME  = P.client_common_name  || CLIENT_LEGAL_NAME
const TICKER_OR_PRIVATE   = P.ticker_or_private   || 'AUTO-DETECT'
const PRIMARY_GEOGRAPHY   = P.primary_geography   || 'AUTO-DETECT'
const TARGET_VERTICAL     = P.target_vertical     || 'AUTO-DETECT'
const REQUIRED_DEPTH      = (P.required_depth     || 'STANDARD').toUpperCase()
const ACCOUNT_CONTEXT = P.account_context || 'NONE'
const KNOWN_RELATIONSHIP  = P.known_relationship_context || 'NONE'
const PURSUIT_OBJECTIVES  = P.strategic_pursuit_objectives || 'NONE'

const H       = P.harness_dir || 'harness-v2'
const RUN_DIR = P.run_dir     || `${H}/runs/${SLUG}`

if (!['BRIEF', 'STANDARD', 'DEEP'].includes(REQUIRED_DEPTH)) {
  throw new Error(`aid-v2: required_depth must be BRIEF | STANDARD | DEEP, got "${REQUIRED_DEPTH}"`)
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
CLIENT_LEGAL_NAME:       ${CLIENT_LEGAL_NAME}
CLIENT_COMMON_NAME:      ${CLIENT_COMMON_NAME}
TICKER_OR_PRIVATE_STATUS:${TICKER_OR_PRIVATE}
PRIMARY_GEOGRAPHY:       ${PRIMARY_GEOGRAPHY}
TARGET_VERTICAL:         ${TARGET_VERTICAL}
RESEARCH_AS_OF_DATE:     ${RESEARCH_AS_OF}
REQUIRED_DEPTH:          ${REQUIRED_DEPTH}
RUN_DIR:                 ${RUN_DIR}
HARNESS_DIR:             ${H}

== the pursuing organization-PROVIDED CONTEXT (sole permitted basis for any organization-history content) ==
ACCOUNT_CONTEXT:           ${ACCOUNT_CONTEXT}
KNOWN_RELATIONSHIP_CONTEXT:    ${KNOWN_RELATIONSHIP}
STRATEGIC_PURSUIT_OBJECTIVES:  ${PURSUIT_OBJECTIVES}
`.trim()

/**
 * Build an agent prompt.
 * @param {string} briefFile  filename under harness-v2/prompts/briefs/
 * @param {string} label      agent label — must match prompts/id-allocation.md
 * @param {string} upstream   digests / notes from prior stages ('' for P0)
 * @param {string} extra      stage-specific instructions appended verbatim
 */
function build(briefFile, label, upstream, extra) {
  return `You are agent "${label}" in the AID v2.1 harness.

READ THESE FILES BEFORE DOING ANYTHING ELSE, IN THIS ORDER:
  1. ${H}/prompts/system-aid-analyst.md      — the constitution; non-negotiable
  2. ${H}/prompts/briefs/_common.md          — shared preamble
  3. ${H}/prompts/briefs/${briefFile}        — YOUR brief; it defines your scope
  4. ${H}/prompts/id-allocation.md           — find YOUR block; mint nothing outside it
  5. ${H}/blueprint/aid-blueprint-v2.1.md    — the section blueprint
  6. ${H}/blueprint/section-contracts.md     — envelopes, evidence bars, dependencies

Your brief names any further files you need (scoring rubrics, vertical modules, QA protocol,
state schema, upstream artefacts under ${RUN_DIR}).

${PARAMS}
${upstream ? `\n== UPSTREAM CONTEXT ==\n${upstream}\n` : ''}${extra ? `\n== STAGE NOTES ==\n${extra}\n` : ''}
Write your two artefacts to disk as your brief specifies, then return a digest of AT MOST 200
WORDS. The digest is concatenated into every downstream agent's prompt, so length here costs the
whole run. Do not return your section text — it belongs on disk.`
}

// ---------------------------------------------------------------------------
// Structured returns
// ---------------------------------------------------------------------------

const SCOPE_SCHEMA = {
  type: 'object',
  required: ['legal_name', 'listing_status', 'vertical_module', 'vertical_confidence', 'digest'],
  properties: {
    legal_name:          { type: 'string' },
    listing_status:      { enum: ['public', 'private', 'subsidiary', 'government', 'nonprofit'] },
    ticker:              { type: ['string', 'null'] },
    vertical_module:     { enum: ['V-HLS','V-BFSI','V-RCG','V-ENR','V-MFG','V-TMT','V-TTH','V-GOV','NONE'] },
    vertical_confidence: { enum: ['High', 'Medium', 'Low'] },
    fiscal_year_end:     { type: 'string' },
    latest_fy_label:     { type: 'string' },
    core_sources_registered: { type: 'integer' },
    entity_ambiguity:    { type: ['string', 'null'], description: 'Non-null when entity resolution required an assumption' },
    anticipated_gaps:    { type: 'array', items: { type: 'string' } },
    digest:              { type: 'string' },
  },
}

const QA_SCHEMA = {
  type: 'object',
  required: ['result', 'blockers', 'majors', 'minors', 'eqi', 'eqi_band', 'digest'],
  properties: {
    result:    { enum: ['PASS', 'PASS WITH DISCLOSURES', 'FAIL'] },
    blockers:  { type: 'integer' },
    majors:    { type: 'integer' },
    minors:    { type: 'integer' },
    eqi:       { type: 'number' },
    eqi_band:  { enum: ['Strong', 'Adequate', 'Thin', 'Insufficient'] },
    checks_passed: { type: 'integer' },
    checks_total:  { type: 'integer' },
    disclosed_failures: { type: 'array', items: { type: 'string' } },
    digest:    { type: 'string' },
  },
}

// ---------------------------------------------------------------------------
// P0 — Scope
// ---------------------------------------------------------------------------

phase('P0 Scope')
log(`AID v2.1 — ${CLIENT_LEGAL_NAME} · as-of ${RESEARCH_AS_OF} · depth ${REQUIRED_DEPTH} · run dir ${RUN_DIR}`)

const scope = await agent(
  build('00-scoping.md', 'scoping', '', `Create the run directory structure first:
  ${RUN_DIR}/sections/  ${RUN_DIR}/state/fragments/  ${RUN_DIR}/qa/

Then write ${RUN_DIR}/state/state.json as schema-2.1 initial state: meta (including
listing_status, vertical_module, vertical_confidence, fiscal_year_end, latest_fy_label,
required_depth "${REQUIRED_DEPTH}", research_as_of "${RESEARCH_AS_OF}"), id_blocks copied from
${H}/prompts/id-allocation.md, canonical_facts you could source at T1-T2, and the S-001..S-049
core source register.

Ten agents launch on this file and cannot ask you questions. Entity identity, listing status, and
vertical module are the three decisions that determine whether the rest of the run researches the
right company.`),
  { label: 'scoping', phase: 'P0 Scope', schema: SCOPE_SCHEMA }
)

if (!scope) throw new Error('aid-v2: P0 scoping failed. Cannot proceed — every downstream agent depends on state.json.')

log(`Scope: ${scope.legal_name} · ${scope.listing_status} · ${scope.vertical_module} (${scope.vertical_confidence}) · ${scope.core_sources_registered || 0} core sources`)
if (scope.entity_ambiguity) log(`⚠ Entity ambiguity recorded: ${scope.entity_ambiguity}`)
if (scope.vertical_confidence === 'Low') log('⚠ Vertical confidence Low — running Core blueprint only, no vertical module')

const SCOPE_CTX = `From P0 (scoping):
- Entity: ${scope.legal_name}${scope.ticker ? ` (${scope.ticker})` : ''} · listing_status: ${scope.listing_status}
- Vertical module: ${scope.vertical_module} (confidence ${scope.vertical_confidence})
- Fiscal year: ${scope.fiscal_year_end || 'not established'} · latest FY label: ${scope.latest_fy_label || 'not established'}
- Blueprint variant: ${scope.listing_status === 'public' ? 'PUBLIC — full blueprint' : 'PRIVATE variant — drop §2.3-Pub, §3.3, §4.3, §4.5, Appendix C-full; substitute per blueprint §4'}
${scope.entity_ambiguity ? `- ⚠ Entity ambiguity: ${scope.entity_ambiguity}` : ''}
- Anticipated gaps: ${(scope.anticipated_gaps || []).join('; ') || 'none declared'}
- Canonical facts and core sources S-001..S-049 are in ${RUN_DIR}/state/state.json. CITE THEM; DO NOT RE-REGISTER.

${scope.digest}`

// ---------------------------------------------------------------------------
// P1 — Client reality. Tier 2, vendor-neutral, fully concurrent.
// ---------------------------------------------------------------------------

phase('P1 Reality')

const TIER2_STANDARD = [
  { brief: '01-corporate.md',   label: 'corporate',  out: '02-company.md' },
  { brief: '02-market.md',      label: 'market',     out: '03-market.md' },
  { brief: '03-financials.md',  label: 'financials', out: '04-financials.md' },
  { brief: '04-strategy.md',    label: 'strategy',   out: '05-strategy.md' },
  { brief: '05-technology.md',  label: 'technology', out: '06-technology.md' },
  { brief: '06-ai-posture.md',  label: 'ai-posture', out: '07-ai.md' },
  { brief: '07-leadership.md',  label: 'leadership', out: '08-leadership.md' },
  { brief: '08-ecosystem.md',   label: 'ecosystem',  out: '09-ecosystem.md' },
  { brief: '09-risk-reg.md',    label: 'risk-reg',   out: '10-risk.md' },
]

// BRIEF depth merges adjacent scopes rather than thinning every section — a
// smaller number of complete sections beats ten shallow ones.
const TIER2_BRIEF = [
  { brief: '01-corporate.md',  label: 'corporate',  out: '02-company.md',
    note: 'BRIEF depth: also cover §3.1-3.2 and §3.6 at reduced scope (market structure, competitor set, customer segments). Skip §3.3 peer benchmarking and §3.4 SWOT.' },
  { brief: '03-financials.md', label: 'financials', out: '04-financials.md',
    note: 'BRIEF depth: §4.1-4.2 only. Skip §4.3, §4.4, §4.5 unless evidence is already in hand.' },
  { brief: '04-strategy.md',   label: 'strategy',   out: '05-strategy.md',
    note: 'BRIEF depth: §5.1-5.2 only, plus a compressed §7.1 AI initiative inventory appended under its own heading. Skip §5.3-5.6 and §7.2-7.4 (§5.6 innovation is STANDARD+).' },
  { brief: '05-technology.md', label: 'technology', out: '06-technology.md',
    note: 'BRIEF depth: §6.1 and §6.6 only. §6.6 sourcing model is REQUIRED even at BRIEF — it drives §12.5. Skip §6.2-6.5, §6.7, and Model 2 (§6.7 pain points is STANDARD+).' },
  { brief: '07-leadership.md', label: 'leadership', out: '08-leadership.md',
    note: 'BRIEF depth: §8.1 and §8.3, plus a compressed §9.1-9.2 vendor and SI register appended under its own heading. Skip §8.2, §8.4, §9.3-9.5 (§8.4 workforce is STANDARD+).' },
  { brief: '09-risk-reg.md',   label: 'risk-reg',   out: '10-risk.md',
    note: 'BRIEF depth: §10.1 and §10.5 only. Skip §10.2-10.4, §10.6, §10.7 (litigation and scenarios are STANDARD+).' },
]

const tier2 = REQUIRED_DEPTH === 'BRIEF' ? TIER2_BRIEF : TIER2_STANDARD

const runVertical = REQUIRED_DEPTH !== 'BRIEF'
  && scope.vertical_module !== 'NONE'
  && scope.vertical_confidence !== 'Low'

const p1Tasks = tier2.map(a => () => agent(
  build(a.brief, a.label, SCOPE_CTX,
    `Write your sections to ${RUN_DIR}/sections/${a.out} and your fragment to
${RUN_DIR}/state/fragments/${a.label}.json.

You are running CONCURRENTLY with ${tier2.length - 1} peer agents plus reconciliation. You cannot
see their output and they cannot see yours. Where you need a fact another agent owns, take it from
state.json canonical_facts or write "see §x.y" — never invent it, never block.

TIER 2 IS VENDOR-NEUTRAL. Promotional references to the pursuing organization must not appear in your output except in a single
neutral relevance flag. QA F7a is a BLOCKER.${a.note ? `\n\n${a.note}` : ''}`),
  { label: a.label, phase: 'P1 Reality' }
))

if (runVertical) {
  p1Tasks.push(() => agent(
    build('10-vertical.md', 'vertical', SCOPE_CTX,
      `Module in force: ${scope.vertical_module} (confidence ${scope.vertical_confidence}).
Write to ${RUN_DIR}/sections/appendix-j-vertical.md and ${RUN_DIR}/state/fragments/vertical.json.

Your anchor packets supplement the owning agents' sections; they never replace them. The candidate
lists in vertical-modules.md are SEARCH CHECKLISTS, NOT FACTS — writing that this client runs a
system because the module says it is typical is the single most likely fabrication in this harness.`),
    { label: 'vertical', phase: 'P1 Reality' }
  ))
}

// Labels in launch order, so a null return can be attributed to the right agent.
const p1Labels = tier2.map(a => a.label)
if (runVertical) p1Labels.push('vertical')

const p1 = await parallel(p1Tasks)
const p1Missing = p1Labels.filter((_, i) => !p1[i])
log(`P1 complete: ${p1Labels.length - p1Missing.length}/${p1Labels.length} agents returned${p1Missing.length ? ` — NO RETURN FROM: ${p1Missing.join(', ')} (QA F10e will flag missing fragments)` : ''}`)

const P1_DIGESTS = p1
  .map((d, i) => (d ? `--- ${p1Labels[i]} ---\n${d}` : `--- ${p1Labels[i]} ---\n(no return — section and fragment may be missing)`))
  .join('\n\n')

// ---------------------------------------------------------------------------
// P2 — Reconcile. 2a concurrent; 2b after, because it merges 2a's output.
// ---------------------------------------------------------------------------

phase('P2 Reconcile')

const P2_CTX = `${SCOPE_CTX}\n\n== P1 AGENT DIGESTS ==\n${P1_DIGESTS}`

const [contradictionOut, auditOut] = await parallel([
  () => agent(
    build('12-contradiction.md', 'contradiction', P2_CTX,
      `Read every fragment in ${RUN_DIR}/state/fragments/ and every section in ${RUN_DIR}/sections/.
Write ${RUN_DIR}/sections/00-4-contradictions.md and ${RUN_DIR}/state/fragments/contradiction.json.

Priority: cross-agent canonical_facts conflicts. Two agents reporting different values for the same
fact is the signature failure of a parallel harness and it corrupts everything built on top.`),
    { label: 'contradiction', phase: 'P2 Reconcile' }
  ),
  () => agent(
    build('13-evidence-audit.md', 'evidence-audit', P2_CTX,
      `Write ${RUN_DIR}/qa/evidence-audit.json and ${RUN_DIR}/state/fragments/evidence-audit.json.

You are ADVERSARIAL BY MANDATE. For every materiality:high claim, try to REFUTE it. Default to
REFUTED when uncertain. You run before Tier 3 precisely so a bad claim cannot become an
opportunity, then a message, then an action, then a line in the executive brief.`),
    { label: 'evidence-audit', phase: 'P2 Reconcile' }
  ),
])

const mergeOut = await agent(
  build('11-source-merge.md', 'source-merge',
    `${P2_CTX}\n\n--- contradiction ---\n${contradictionOut || '(no return)'}\n\n--- evidence-audit ---\n${auditOut || '(no return)'}`,
    `Two jobs. (1) Deduplicate the source register across all fragments, apply the rewrite map to
every section file, and report any claim whose [TRIANGULATED] tag collapses to a single source.
(2) Build the consolidated ${RUN_DIR}/state/state.json that Stages 3-6 read — merge every fragment,
apply evidence-audit verdicts, and promote canonical_facts ONLY where no peer disagreed.

Omit a contested canonical fact rather than guessing. Downstream agents trust that object without
re-checking, so a wrong value there propagates everywhere.`),
  { label: 'source-merge', phase: 'P2 Reconcile' }
)

log('P2 complete: contradictions swept, evidence audited, sources deduplicated, state merged')

// ---------------------------------------------------------------------------
// P3 — Pursuit. §11 first (mints O-nn), then §12 and §13 concurrently.
// ---------------------------------------------------------------------------

phase('P3 Pursuit')

const P3_CTX = `${SCOPE_CTX}

== P1 AGENT DIGESTS ==
${P1_DIGESTS}

== P2 RECONCILIATION ==
contradiction: ${contradictionOut || '(no return)'}
evidence-audit: ${auditOut || '(no return)'}
source-merge: ${mergeOut || '(no return)'}

Merged state is at ${RUN_DIR}/state/state.json. The refuted-claim list in
${RUN_DIR}/qa/evidence-audit.json is BINDING.`

const oppOut = await agent(
  build('14-opportunity.md', 'opportunity', P3_CTX,
    `Write ${RUN_DIR}/sections/11-opportunity.md and ${RUN_DIR}/state/fragments/opportunity.json.

You run alone so §12 and §13 have stable O-nn and U-nn IDs to reference. You are the sole minter of
both. Every O-nn cites at least one claim that SURVIVED evidence-audit — a REFUTED claim may not be
cited as need evidence (QA F3f, BLOCKER).

Tier 3 begins here: the pursuing organization content is now permitted. Accelerator and capability content renders only
from ACCOUNT_CONTEXT; where that is NONE, write "input not provided".`),
  { label: 'opportunity', phase: 'P3 Pursuit' }
)

if (!oppOut) log('⚠ Opportunity register agent returned nothing — §12 and §13 will have no O-nn to reference')

const P3B_CTX = `${P3_CTX}\n\n== OPPORTUNITY REGISTER (§11) ==\n${oppOut || '(no return — §11 unavailable)'}`

const [strategyOut, engagementOut] = await parallel([
  () => agent(
    build('15-account-strategy.md', 'account-strategy', P3B_CTX,
      `Write ${RUN_DIR}/sections/12-strategy.md and ${RUN_DIR}/state/fragments/account-strategy.json.

You run CONCURRENTLY with the engagement agent. You own positioning, messaging, competitive
strategy, and commercial construct. They own timing, stakeholder actions, and the action plan.
Do not write actions or dates — you would produce a second, conflicting plan.

§12.5 derives from §6.6 sourcing posture. §12.4 completes Model 8 dimension 5, deferred from §9.4.`),
    { label: 'account-strategy', phase: 'P3 Pursuit' }
  ),
  () => agent(
    build('16-engagement.md', 'engagement', P3B_CTX,
      `Write ${RUN_DIR}/sections/13-engagement.md and ${RUN_DIR}/state/fragments/engagement.json.

You run CONCURRENTLY with the account-strategy agent. You own timing, stakeholder actions, the
validation backlog, the action plan, and kill criteria. They own positioning and commercial shape.
Do not write positioning or messaging content.

§13.4 coverage is mechanically checked (QA F7e): every HYPOTHESIS/VALIDATE opportunity and every
materiality:high gap must appear. §13.6 kill criteria are the counterweight to Tier 3's structural
optimism — do not soften them to protect the thesis.`),
    { label: 'engagement', phase: 'P3 Pursuit' }
  ),
])

log('P3 complete: opportunity register, account strategy, engagement plan')

// ---------------------------------------------------------------------------
// P4 — Executive brief. Written LAST, derived strictly from the body.
// ---------------------------------------------------------------------------

phase('P4 Brief')

const execOut = await agent(
  build('17-exec-brief.md', 'exec-brief', `${P3_CTX}

== TIER 3 ==
opportunity: ${oppOut || '(no return)'}
account-strategy: ${strategyOut || '(no return)'}
engagement: ${engagementOut || '(no return)'}`,
    `Write ${RUN_DIR}/sections/01-exec-brief.md (§1.1-1.8, §0.6) and finalise
${RUN_DIR}/sections/00-4-contradictions.md (§0.4). Fragment: ${RUN_DIR}/state/fragments/exec-brief.json.

NO NEW RESEARCH. NO NEW SOURCES (QA F8g). Every Tier 1 statement carries a C-/O-/R-/A-/P-/G-
reference; a Tier 1 sentence with no ID is a BLOCKER (F8a). Nothing appears in Tier 1 that is not
in the body (F8b).

Writing the brief last is the structural decision that removes the incentive to fabricate. If you
want to say something the body does not support, that is a G-17nn gap — and it belongs in §1.8.

§1.1 must be consistent with §1.6's readiness band (F8d, BLOCKER). If the evidence says nurture,
write nurture.`),
  { label: 'exec-brief', phase: 'P4 Brief' }
)

// ---------------------------------------------------------------------------
// P5 — QA gate
// ---------------------------------------------------------------------------

phase('P5 QA')

const qa = await agent(
  build('18-qa-gate.md', 'qa-gate', `${SCOPE_CTX}

== ALL STAGE DIGESTS ==
${P1_DIGESTS}
contradiction: ${contradictionOut || '(no return)'}
evidence-audit: ${auditOut || '(no return)'}
source-merge: ${mergeOut || '(no return)'}
opportunity: ${oppOut || '(no return)'}
account-strategy: ${strategyOut || '(no return)'}
engagement: ${engagementOut || '(no return)'}
exec-brief: ${execOut || '(no return)'}`,
    `Execute ${H}/blueprint/qa-protocol.md F1-F10 in full. Write ${RUN_DIR}/qa/qa-report.md,
${RUN_DIR}/qa/qa-report.json, ${RUN_DIR}/sections/00-5-qa.md, and
${RUN_DIR}/state/fragments/qa-gate.json. Fold the Stage 3-4 fragments into state.json — they
postdate source-merge and Appendices A-L depend on them.

YOUR JOB IS TO FIND FAILURES, NOT TO CERTIFY SUCCESS. Every prior agent had an incentive to produce
a complete-looking section; you are the only one whose incentive runs the other way. Zero failures
across 51 checks on a first run means you did not run them — re-read F4b, F5a, F1f, F2c.

Any FAIL that cannot be remediated is DISCLOSED in §0.5, never masked.`),
  { label: 'qa-gate', phase: 'P5 QA', schema: QA_SCHEMA }
)

if (qa) {
  log(`QA: ${qa.result} · ${qa.blockers} blocker / ${qa.majors} major / ${qa.minors} minor · EQI ${qa.eqi} (${qa.eqi_band})`)
  if (qa.blockers > 0)          log(`⚠ ${qa.blockers} BLOCKER(s) unremediated — see ${RUN_DIR}/qa/qa-report.md before any use`)
  if (qa.eqi_band === 'Insufficient') log('⚠ EQI band Insufficient — do not present. Re-run with better sources or reduce scope per the thin-evidence degradation mode.')
} else {
  log('⚠ QA gate returned nothing — dossier is UNVERIFIED')
}

// ---------------------------------------------------------------------------
// P6 — Assembly
// ---------------------------------------------------------------------------

phase('P6 Assemble')

const finalOut = await agent(
  build('19-assembly.md', 'assembly', `${SCOPE_CTX}

QA result: ${qa ? `${qa.result} · EQI ${qa.eqi} (${qa.eqi_band}) · ${qa.blockers}B/${qa.majors}M/${qa.minors}m` : 'QA DID NOT COMPLETE'}
${qa && qa.disclosed_failures && qa.disclosed_failures.length ? `Disclosed failures: ${qa.disclosed_failures.join('; ')}` : ''}
exec-brief: ${execOut || '(no return)'}`,
    `Assemble ${RUN_DIR}/${SLUG}-aid.md from ${RUN_DIR}/sections/ in blueprint order, inject the
vertical anchor packets, and generate Appendices A-L from the registers in
${RUN_DIR}/state/state.json. Fragment: ${RUN_DIR}/state/fragments/assembly.json.

You mint nothing and write no analysis. Verify every inline ID resolves; an unresolved reference is
RECORDED in Appendix H, never invented into existence. Markdown only — no HTML, no styling, no
images.

Put the Evidence Quality Index and QA result in the title block so a reader knows how much to trust
the document before reading a word of it.`),
  { label: 'assembly', phase: 'P6 Assemble' }
)

// ---------------------------------------------------------------------------

log(`Done. Dossier: ${RUN_DIR}/${SLUG}-aid.md`)

return {
  client: CLIENT_LEGAL_NAME,
  research_as_of: RESEARCH_AS_OF,
  depth: REQUIRED_DEPTH,
  run_dir: RUN_DIR,
  dossier: `${RUN_DIR}/${SLUG}-aid.md`,
  listing_status: scope.listing_status,
  vertical_module: scope.vertical_module,
  vertical_confidence: scope.vertical_confidence,
  tier2_agents_launched: p1Tasks.length,
  tier2_agents_returned: p1.filter(Boolean).length,
  qa: qa || null,
  assembly: finalOut || null,
}
