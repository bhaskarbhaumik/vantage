import assert from 'node:assert/strict';
import { test } from 'node:test';
import { exportProgress, exportReducer, expectedStages, initialExportState } from '../src/lib/exportState.js';
import { applyEvent, initialRunState, phaseKey, progress, runReducer, type RunState } from '../src/lib/runState.js';
import { loadStream } from './helpers.js';

function replayRun(): RunState {
  const rec = loadStream('run-events.jsonl');
  let s = runReducer(initialRunState(), { kind: 'start', client: 'Example Corp', now: 0 });
  s = runReducer(s, { kind: 'batch', events: rec.events });
  return runReducer(s, { kind: 'result', result: rec.result, code: 0, stderr: '', cancelled: false, now: 1 });
}

test('phaseKey parses stage titles and agent steps', () => {
  assert.equal(phaseKey('P0 Preflight'), 'P0');
  assert.equal(phaseKey('P4 Reconcile'), 'P4');
  assert.equal(phaseKey('P7R Remediation'), 'P7R');
  assert.equal(phaseKey('p8'), 'P8');
  assert.equal(phaseKey('render:pptx'), null);
  assert.equal(phaseKey(null), null);
});

test('recorded run: every phase incl. P7R completes', () => {
  const s = replayRun();
  assert.equal(s.status, 'done');
  const byKey = Object.fromEntries(s.phases.map((p) => [p.key, p]));
  for (const k of ['P0', 'P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P7R', 'P8']) {
    assert.equal(byKey[k].status, 'done', `${k} should be done`);
  }
  assert.deepEqual(byKey.P4.steps, ['P4 Merge', 'P4 Reconcile']);
  assert.equal(byKey.P7R.message, 'BLOCKERs 3 -> 1');
  assert.equal(progress(s), 1);
});

test('recorded run: agents, tokens, warnings and result', () => {
  const s = replayRun();
  const agents = Object.fromEntries(s.agents.map((a) => [a.label, a]));
  assert.equal(agents.financials.status, 'error');
  assert.equal(agents.financials.error, 'tool budget exhausted');
  assert.equal(agents.market.outputTokens, 6100);
  assert.equal(agents['verification-r1'].phase, 'P7R');
  assert.equal(agents['market-r1'].status, 'done');
  assert.equal(s.totals.agentsError, 1);
  assert.equal(s.totals.agentsOk, s.agents.length - 1);
  assert.equal(s.totals.outputTokens, 50700);
  assert.equal(s.warnings.length, 2);
  assert.match(s.warnings[1], /stopped on budget/);
  assert.equal(s.result?.slug, 'example-2026-10');
  assert.equal(s.result?.runDir, '/tmp/vantage/run/example-2026-10');
  assert.equal(s.result?.verification?.overall_confidence, 'Moderate');
  assert.equal(s.result?.verification?.blockers, 1);
  assert.ok(s.logs.some((l) => l.text.includes('P7R round 1')));
});

test('mid-run state: running phase, running agents and live token counts', () => {
  const rec = loadStream('run-events.jsonl');
  let s = initialRunState();
  // Stop right after the agent_progress event inside Wave A.
  const cut = rec.events.findIndex((e) => e.type === 'agent_progress');
  for (const ev of rec.events.slice(0, cut + 1)) s = applyEvent(s, ev);
  assert.equal(s.status, 'running');
  assert.equal(s.currentPhase, 'P2');
  assert.equal(s.phases.find((p) => p.key === 'P2')?.status, 'running');
  assert.equal(s.phases.find((p) => p.key === 'P3')?.status, 'pending');
  const market = s.agents.find((a) => a.label === 'market');
  assert.equal(market?.status, 'running');
  assert.equal(market?.outputTokens, 700);
  assert.ok(progress(s) > 0 && progress(s) < 1);
});

test('phases a plan skips are marked skipped, not left pending', () => {
  let s = initialRunState();
  for (const stage of ['P0 Preflight', 'P1 Backbone', 'P2 Wave A', 'P4 Merge']) {
    s = applyEvent(s, { type: 'stage_start', stage, ts: 1 });
    s = applyEvent(s, { type: 'stage_done', stage, ts: 2 });
  }
  assert.equal(s.phases.find((p) => p.key === 'P3')?.status, 'skipped');
  s = applyEvent(s, { type: 'stage_start', stage: 'P8 Assemble', ts: 3 });
  assert.equal(s.phases.find((p) => p.key === 'P7R')?.status, 'skipped');
});

test('engine failure without a result marks the run failed and keeps stderr', () => {
  let s = runReducer(initialRunState(), { kind: 'start', client: 'X', now: 0 });
  s = applyEvent(s, { type: 'stage_start', stage: 'P0 Preflight', ts: 1 });
  s = runReducer(s, { kind: 'result', result: null, code: 2, stderr: 'No such option: --remediation-rounds', cancelled: false });
  assert.equal(s.status, 'failed');
  assert.equal(s.phases[0].status, 'error');
  assert.match(s.errors.at(-1) ?? '', /No such option/);
});

test('export reducer: stages, artifacts, warnings and result', () => {
  const rec = loadStream('export-events.jsonl');
  assert.deepEqual(expectedStages(['pdf']), ['ingest', 'plan', 'assets', 'charts', 'render:docx', 'render:pdf']);
  let s = exportReducer(initialExportState(), { kind: 'start', formats: ['pptx'], now: 0 });
  s = exportReducer(s, { kind: 'batch', events: rec.events });
  assert.equal(s.artifacts.length, 1);
  assert.equal(s.artifacts[0].slides, 24);
  assert.equal(s.stages.find((x) => x.name === 'render:pptx')?.status, 'done');
  s = exportReducer(s, { kind: 'result', result: rec.result, code: 0, stderr: '', cancelled: false });
  assert.equal(s.status, 'done');
  assert.equal(s.outDir, '/tmp/vantage/run/example-2026-10/exports');
  assert.deepEqual(s.plans, { deck: 'scaffold' });
  assert.equal(s.warnings.length, 1, 'warning from the stream and the result is not duplicated');
  assert.ok(exportProgress(s) > 0);
});

test('text-only backends: phases are inferred from log lines and never move backwards', () => {
  let s = runReducer(initialRunState(), { kind: 'start', client: 'X', now: 0 });
  s = applyEvent(s, { type: 'run_start', message: 'X', ts: 1, data: { backend: 'workflow' } });
  s = applyEvent(s, { type: 'log', agent: 'workflow', message: 'P2 Wave A: launching 10 agents', ts: 2 });
  assert.equal(s.currentPhase, 'P2');
  assert.equal(s.inferred, true);
  s = applyEvent(s, { type: 'log', agent: 'workflow', message: 'P7R round 1: 3 BLOCKER(s)', ts: 3 });
  s = applyEvent(s, { type: 'log', agent: 'workflow', message: 'back-reference to P1 output', ts: 4 });
  assert.equal(s.currentPhase, 'P7R');
  assert.equal(s.phases.find((p) => p.key === 'P2')?.status, 'done');
  s = applyEvent(s, { type: 'run_done', message: '/tmp/x-vantage.md', ts: 5 });
  assert.equal(s.phases.find((p) => p.key === 'P7R')?.status, 'done');
  assert.equal(s.phases.find((p) => p.key === 'P8')?.status, 'pending', 'unknown phases are not claimed as skipped');
});
