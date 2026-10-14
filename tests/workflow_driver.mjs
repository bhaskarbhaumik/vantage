// Runs harness/workflows/vantage-v3.workflow.mjs with stubbed Workflow globals and prints every
// agent call it makes, in order, as JSON. No model is called and nothing touches disk.
//
//   node tests/workflow_driver.mjs <workflow.mjs> <scenario.json>
//
// Scenario keys:
//   args           Workflow args (required keys are filled with defaults)
//   verifications  structured returns for successive verification calls, in order
//   router         structured return for every remediation-router call
//   null_labels    agent labels that return null, to simulate an agent that did not return
//
// Used by tests/test_workflow_remediation.py, and to prove that a harness change leaves the
// prompts of already-completed agents byte-identical — which is what lets a resumed run replay
// them from cache instead of paying for them again.

import { readFileSync } from 'node:fs'
import { createHash } from 'node:crypto'

const [, , wfPath, scenarioPath] = process.argv
const scenario = scenarioPath ? JSON.parse(readFileSync(scenarioPath, 'utf8')) : {}

const src = readFileSync(wfPath, 'utf8').replace(/^export const meta/m, 'const meta')
const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor
const body = new AsyncFunction('args', 'agent', 'parallel', 'phase', 'log', src)

const args = {
  client_legal_name: 'Acme Industries, Inc.',
  slug: 'acme-2026-10',
  research_as_of: '2026-10-14',
  ...(scenario.args || {}),
}

const calls = []
const logs = []
let verIdx = 0
const nullLabels = new Set(scenario.null_labels || [])

const PREFLIGHT = {
  legal_name: 'Acme Industries, Inc.', ownership_form: 'public', jurisdictions: ['us-sec'],
  vertical_primary: 'V-MFG', vertical_confidence: 'High', digest: 'preflight digest',
}
const CLEAN_VERIFICATION = {
  result: 'PASS', blockers: 0, majors: 0, minors: 0, eqi: 80, overall_confidence: 'Strong',
  digest: 'clean',
}

async function agent(prompt, opts = {}) {
  const label = opts.label
  calls.push({
    label,
    phase: opts.phase,
    has_schema: Boolean(opts.schema),
    schema: opts.schema || null,
    sha: createHash('sha256').update(prompt).digest('hex'),
    prompt,
  })
  if (nullLabels.has(label)) return null
  if (label === 'preflight') return PREFLIGHT
  if (label.startsWith('verification')) {
    const list = scenario.verifications || []
    return list[verIdx++] || CLEAN_VERIFICATION
  }
  if (label.startsWith('remediation-router')) return scenario.router ?? null
  return `digest from ${label}`
}

const parallel = tasks => Promise.all(tasks.map(t => t()))
const phase = () => {}
const log = m => logs.push(String(m))

const result = await body(args, agent, parallel, phase, log)
process.stdout.write(JSON.stringify({ calls, logs, result }))
