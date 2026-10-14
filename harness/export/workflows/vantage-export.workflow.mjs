export const meta = {
  name: 'vantage-export',
  description: 'Vantage export — design a finished Vantage dossier as a deck, a whitepaper/PDF and a self-contained HTML microsite. Agents plan, code renders.',
  phases: [
    { title: 'P0 Ingest',    detail: 'Parse the dossier and write the derived plans as the scaffold' },
    { title: 'P1 Narrative', detail: 'One agent decides the story: the verdict, the tension, what leads, the visual direction' },
    { title: 'P2 Author',    detail: 'Three concurrent agents write the deck, whitepaper and microsite plans' },
    { title: 'P3 QA',        detail: 'Adversarial gate — every number traced, no suppressed score, markers and errata intact' },
    { title: 'P4 Render',    detail: 'Deterministic: .pptx · .docx · .pdf · one self-contained .html' },
  ],
}

// ---------------------------------------------------------------------------
// Parameters. Pass via Workflow `args`. See harness/export/README.md.
//
//   dossier         (required) absolute path to <slug>-vantage.md
//   repo            the vantage checkout (default: two levels above harness_dir)
//   harness_dir     default: <repo>/harness/export
//   run_dir         default: <dossier-dir>/exports
//   depth           exec | standard | full            (default: standard)
//   formats         ["pptx","docx","pdf","html"]      (default)
//   site_mode       microsite | deck                  (default: microsite)
//   classification  marking on every page             (default: Confidential)
//   brand           pursuing organization's domain    (default: none — neutral theme)
//   render          false stops after QA              (default: true)
// ---------------------------------------------------------------------------

const P = (typeof args === 'string' ? JSON.parse(args) : args) || {}

function req(key) {
  const value = P[key]
  if (value === undefined || value === null || value === '') {
    throw new Error(`vantage-export: required arg "${key}" is missing. See harness/export/README.md.`)
  }
  return value
}

const DOSSIER = req('dossier')
const H = P.harness_dir || (P.repo ? `${P.repo}/harness/export` : 'harness/export')
const REPO = P.repo || H.replace(/\/harness\/export\/?$/, '') || '.'
const RUN_DIR = P.run_dir || `${DOSSIER.replace(/\/[^/]+$/, '')}/exports`
const PLAN_DIR = `${RUN_DIR}/plan`
const DEPTH = (P.depth || 'standard').toLowerCase()
const SITE_MODE = (P.site_mode || 'microsite').toLowerCase()
const FORMATS = P.formats || ['pptx', 'docx', 'pdf', 'html']
const CLASSIFICATION = P.classification || 'Confidential'
const BRAND = P.brand || ''
const RENDER = P.render !== false

if (!['exec', 'standard', 'full'].includes(DEPTH)) {
  throw new Error(`vantage-export: depth must be exec | standard | full, got "${DEPTH}"`)
}
if (!['microsite', 'deck'].includes(SITE_MODE)) {
  throw new Error(`vantage-export: site_mode must be microsite | deck, got "${SITE_MODE}"`)
}

// The engine runs from the repo so `uv run` resolves the right environment.
const ENGINE = `uv run --project "${REPO}" python -m vantage.export`

const PARAMS = `
== EXPORT PARAMETERS ==
DOSSIER:        ${DOSSIER}
RUN_DIR:        ${RUN_DIR}
PLAN_DIR:       ${PLAN_DIR}
HARNESS_DIR:    ${H}
DEPTH:          ${DEPTH}
SITE_MODE:      ${SITE_MODE}
FORMATS:        ${FORMATS.join(', ')}
CLASSIFICATION: ${CLASSIFICATION}
BRAND:          ${BRAND || '(none — neutral Vantage theme)'}
ENGINE:         ${ENGINE}
`.trim()

/**
 * Build an agent prompt. The workflow embeds no brief text — it passes paths and each agent
 * reads its own brief, so the prompt library stays editable as plain Markdown.
 */
function build(briefFile, label, upstream, extra) {
  return `You are agent "${label}" in the Vantage export harness.

READ THESE FILES BEFORE DOING ANYTHING ELSE, IN THIS ORDER:
  1. ${H}/prompts/system-vantage-editor.md  — your constitution; non-negotiable
  2. ${H}/prompts/briefs/_common.md         — shared preamble, incl. the visual helpers
  3. ${H}/prompts/briefs/${briefFile}       — YOUR brief; it defines your scope

${PARAMS}

${upstream ? `== UPSTREAM ==\n${upstream}\n` : ''}
${extra || ''}

Do the work your brief describes. Write exactly the file it names. Return a short plain-text
report of what you decided and why — not the file contents.`
}

// ---------------------------------------------------------------------------
// P0 — ingest. Deterministic; the agent only runs commands.
// ---------------------------------------------------------------------------
phase('P0 Ingest')
log(`Dossier: ${DOSSIER}`)
log(`Exports: ${RUN_DIR}  ·  depth ${DEPTH}  ·  ${SITE_MODE}`)

const ingest = await agent(
  `Run these commands and report their output verbatim. Do not analyse the dossier — a later
agent does that.

  ${ENGINE} inspect "${DOSSIER}"
  ls "${PLAN_DIR}" 2>/dev/null || ${ENGINE} plan "${DOSSIER}" --out "${RUN_DIR}" --depth ${DEPTH} --site-mode ${SITE_MODE}

If plans already exist in ${PLAN_DIR}, do NOT regenerate them. If a command fails, report the
error and stop.`,
  { label: 'ingest', phase: 'P0 Ingest' },
)

// ---------------------------------------------------------------------------
// P1 — narrative. Single agent; everything downstream reads it.
// ---------------------------------------------------------------------------
phase('P1 Narrative')

const story = await agent(
  build('01-narrative.md', 'narrative', `Dossier structure and derived plans:\n${ingest || '(ingest returned nothing)'}`),
  { label: 'narrative', phase: 'P1 Narrative' },
)

// ---------------------------------------------------------------------------
// P2 — authoring. Three collaterals, concurrent: they share the story and are otherwise
// independent.
// ---------------------------------------------------------------------------
phase('P2 Author')

const upstream = `The narrative agent wrote ${PLAN_DIR}/story.md. Read it. Its report:\n${story || '(no report)'}`

const [deckReport, docReport, siteReport] = await parallel([
  () => agent(build('02-deck-plan.md', 'deck-plan', upstream), { label: 'deck-plan', phase: 'P2 Author' }),
  () => agent(build('03-doc-plan.md', 'doc-plan', upstream), { label: 'doc-plan', phase: 'P2 Author' }),
  () => agent(build('04-microsite-plan.md', 'site-plan', upstream,
    `SITE_MODE for this run is "${SITE_MODE}".`), { label: 'site-plan', phase: 'P2 Author' }),
])

// ---------------------------------------------------------------------------
// P3 — QA. Adversarial, and empowered to fix what it finds.
// ---------------------------------------------------------------------------
phase('P3 QA')

const qa = await agent(
  build('05-qa-gate.md', 'qa-gate',
    `Authoring reports:\n\n[deck]\n${deckReport || '—'}\n\n[whitepaper]\n${docReport || '—'}\n\n[microsite]\n${siteReport || '—'}`,
    'You may edit the plan files to fix blockers. Re-render (pptx/html only, for speed) to confirm each fix.'),
  { label: 'qa-gate', phase: 'P3 QA' },
)

// ---------------------------------------------------------------------------
// P4 — render. Deterministic; skipped when the caller renders itself.
// ---------------------------------------------------------------------------
let rendered = '(render skipped: the caller renders from the authored plans)'
if (RENDER) {
  phase('P4 Render')
  const formatFlags = FORMATS.map((f) => `--format ${f}`).join(' ')
  const brandFlag = BRAND ? ` --brand ${BRAND}` : ''
  rendered = await agent(
    `Run the export and report its output:

  ${ENGINE} render "${DOSSIER}" --out "${RUN_DIR}" --depth ${DEPTH} --site-mode ${SITE_MODE} --classification "${CLASSIFICATION}"${brandFlag} ${formatFlags}

Then verify, and say plainly whether each holds:
  1. Every requested collateral exists on disk and is non-empty.
  2. ${RUN_DIR}/manifest.json "plans" reads "authored" for deck, doc and site — if any reads
     "derived", that plan failed validation; quote the warning.
  3. manifest.json "classification" is "${CLASSIFICATION}".

Report file paths and sizes, the PDF page count, the slide count, and any warnings. Do not re-run
the export more than once unless it failed. Never publish any export to a public URL.`,
    { label: 'render', phase: 'P4 Render' },
  )
}

return {
  dossier: DOSSIER,
  run_dir: RUN_DIR,
  depth: DEPTH,
  formats: FORMATS,
  narrative: story,
  qa,
  render: rendered,
}
