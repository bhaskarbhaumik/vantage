// Pure reducer from the engine's RunEvent stream to the live run dashboard's state.
import type { RunEvent, Verification } from './engine.js';

export const PHASES: { key: string; title: string }[] = [
  { key: 'P0', title: 'Preflight' },
  { key: 'P1', title: 'Backbone' },
  { key: 'P2', title: 'Wave A' },
  { key: 'P3', title: 'Wave B' },
  { key: 'P4', title: 'Reconcile' },
  { key: 'P5', title: 'Synthesis' },
  { key: 'P6', title: 'Brief' },
  { key: 'P7', title: 'Verification' },
  { key: 'P7R', title: 'Remediation' },
  { key: 'P8', title: 'Assembly' },
];

export type PhaseStatus = 'pending' | 'running' | 'done' | 'error' | 'skipped';
export type AgentStatus = 'running' | 'done' | 'error';

export interface PhaseState {
  key: string;
  title: string;
  status: PhaseStatus;
  open: number;
  steps: string[];
  startedAt?: number;
  endedAt?: number;
  message?: string;
}

export interface AgentState {
  label: string;
  phase: string;
  status: AgentStatus;
  startedAt: number;
  endedAt?: number;
  inputTokens: number;
  outputTokens: number;
  iters?: number;
  lastTool?: string;
  error?: string;
}

export type LogLevel = 'info' | 'stage' | 'tool' | 'ok' | 'warn' | 'error';

export interface LogLine {
  ts: number;
  level: LogLevel;
  source: string;
  text: string;
}

export interface RunTotals {
  inputTokens: number;
  outputTokens: number;
  agentsOk: number;
  agentsError: number;
  agentsTotal: number;
}

export interface RunResultSummary {
  dossier: string | null;
  runDir: string | null;
  slug: string | null;
  agentsOk: number;
  agentsTotal: number;
  verification: Verification | null;
  entityAmbiguity: string | null;
  errors: string[];
}

export interface RunState {
  status: 'idle' | 'running' | 'done' | 'failed' | 'cancelled';
  client: string | null;
  startedAt?: number;
  endedAt?: number;
  currentPhase: string | null;
  phases: PhaseState[];
  agents: AgentState[];
  logs: LogLine[];
  warnings: string[];
  errors: string[];
  totals: RunTotals;
  result: RunResultSummary | null;
  // True once the engine sent a real stage event. Until then (the workflow backend streams plain
  // text) phases are inferred from P-tokens in log lines.
  sawStages: boolean;
  inferred: boolean;
}

export const MAX_LOG_LINES = 2000;

export function initialRunState(): RunState {
  return {
    status: 'idle',
    client: null,
    currentPhase: null,
    phases: PHASES.map((p) => ({ key: p.key, title: p.title, status: 'pending', open: 0, steps: [] })),
    agents: [],
    logs: [],
    warnings: [],
    errors: [],
    totals: { inputTokens: 0, outputTokens: 0, agentsOk: 0, agentsError: 0, agentsTotal: 0 },
    result: null,
    sawStages: false,
    inferred: false,
  };
}

// "P4 Reconcile" -> P4, "P7R Remediation" -> P7R, "p2" -> P2. Unknown stages fall back to null.
export function phaseKey(stage: string | null | undefined): string | null {
  if (!stage) return null;
  const m = /^\s*(P\d+R?)/i.exec(stage);
  return m ? m[1].toUpperCase() : null;
}

function num(v: unknown): number {
  return typeof v === 'number' && Number.isFinite(v) ? v : 0;
}

function usageOf(data: Record<string, unknown> | undefined): { input: number; output: number } | null {
  const u = data?.usage as Record<string, unknown> | undefined;
  if (!u || typeof u !== 'object') return null;
  return { input: num(u.input_tokens), output: num(u.output_tokens) };
}

function pushLog(s: RunState, line: LogLine): LogLine[] {
  const logs = s.logs.length >= MAX_LOG_LINES ? s.logs.slice(-(MAX_LOG_LINES - 1)) : s.logs.slice();
  logs.push(line);
  return logs;
}

function updatePhase(s: RunState, key: string, fn: (p: PhaseState) => PhaseState): PhaseState[] {
  let found = false;
  const phases = s.phases.map((p) => {
    if (p.key !== key) return p;
    found = true;
    return fn(p);
  });
  if (!found) {
    // An engine phase this TUI does not know: append it rather than drop it.
    phases.push(fn({ key, title: key, status: 'pending', open: 0, steps: [] }));
  }
  return phases;
}

function totalsFrom(agents: AgentState[], base: RunTotals): RunTotals {
  let inputTokens = 0;
  let outputTokens = 0;
  let ok = 0;
  let bad = 0;
  for (const a of agents) {
    inputTokens += a.inputTokens;
    outputTokens += a.outputTokens;
    if (a.status === 'done') ok++;
    if (a.status === 'error') bad++;
  }
  return { ...base, inputTokens, outputTokens, agentsOk: ok, agentsError: bad, agentsTotal: agents.length };
}

export type RunAction =
  | { kind: 'event'; event: RunEvent; now?: number }
  | { kind: 'batch'; events: RunEvent[] }
  | { kind: 'start'; client: string; now?: number }
  | { kind: 'result'; result: Record<string, unknown> | null; code: number; stderr: string; cancelled: boolean; now?: number }
  | { kind: 'reset' };

export function runReducer(s: RunState, action: RunAction): RunState {
  switch (action.kind) {
    case 'reset':
      return initialRunState();
    case 'start':
      return { ...initialRunState(), status: 'running', client: action.client, startedAt: action.now ?? Date.now() };
    case 'result':
      return finishRun(s, action);
    case 'event':
      return applyEvent(s, action.event, action.now);
    case 'batch':
      return action.events.reduce((acc, ev) => applyEvent(acc, ev), s);
  }
}

export function applyEvent(s: RunState, ev: RunEvent, nowArg?: number): RunState {
  const now = nowArg ?? (ev.ts && ev.ts > 0 ? ev.ts * 1000 : Date.now());
  const key = phaseKey(ev.stage);
  const msg = ev.message ?? '';
  switch (ev.type) {
    case 'run_start': {
      return {
        ...s,
        status: 'running',
        client: msg || s.client,
        startedAt: s.startedAt ?? now,
        logs: pushLog(s, { ts: now, level: 'info', source: 'run', text: `run started${msg ? `: ${msg}` : ''}` }),
      };
    }
    case 'stage_start': {
      if (!key) {
        return { ...s, logs: pushLog(s, { ts: now, level: 'stage', source: 'stage', text: `start ${ev.stage ?? ''}` }) };
      }
      const phases = updatePhase(s, key, (p) => ({
        ...p,
        status: 'running',
        open: p.open + 1,
        steps: ev.stage && !p.steps.includes(ev.stage) ? [...p.steps, ev.stage] : p.steps,
        startedAt: p.startedAt ?? now,
        endedAt: undefined,
      }));
      // A later phase starting means anything still pending before it was not part of this plan.
      const idx = phases.findIndex((p) => p.key === key);
      const settled = phases.map((p, i) =>
        i < idx && p.status === 'pending' && PHASES.some((k) => k.key === p.key)
          ? { ...p, status: 'skipped' as PhaseStatus }
          : p,
      );
      return {
        ...s,
        sawStages: true,
        status: s.status === 'idle' ? 'running' : s.status,
        startedAt: s.startedAt ?? now,
        currentPhase: key,
        phases: settled,
        logs: pushLog(s, { ts: now, level: 'stage', source: key, text: `start ${ev.stage}` }),
      };
    }
    case 'stage_done': {
      if (!key) return s;
      const phases = updatePhase(s, key, (p) => {
        const open = Math.max(0, p.open - 1);
        return {
          ...p,
          open,
          status: open === 0 ? (p.status === 'error' ? 'error' : 'done') : p.status,
          endedAt: open === 0 ? now : p.endedAt,
          message: msg || p.message,
        };
      });
      return {
        ...s,
        phases,
        logs: pushLog(s, { ts: now, level: 'ok', source: key, text: `done ${ev.stage}${msg ? ` - ${msg}` : ''}` }),
      };
    }
    case 'agent_start': {
      const label = ev.agent ?? '?';
      const phase = key ?? s.currentPhase ?? '?';
      const existing = s.agents.find((a) => a.label === label);
      const agent: AgentState = {
        label,
        phase,
        status: 'running',
        startedAt: now,
        inputTokens: existing?.inputTokens ?? 0,
        outputTokens: existing?.outputTokens ?? 0,
      };
      const agents = existing ? s.agents.map((a) => (a.label === label ? agent : a)) : [...s.agents, agent];
      return {
        ...s,
        agents,
        totals: totalsFrom(agents, s.totals),
        logs: pushLog(s, { ts: now, level: 'info', source: label, text: 'started' }),
      };
    }
    case 'agent_tool':
    case 'agent_progress': {
      const label = ev.agent ?? '?';
      const u = usageOf(ev.data);
      const agents = s.agents.map((a) =>
        a.label === label
          ? {
              ...a,
              lastTool: ev.type === 'agent_tool' && msg ? msg : a.lastTool,
              outputTokens: u ? Math.max(a.outputTokens, u.output) : a.outputTokens,
              inputTokens: u ? Math.max(a.inputTokens, u.input) : a.inputTokens,
            }
          : a,
      );
      return {
        ...s,
        agents,
        totals: u ? totalsFrom(agents, s.totals) : s.totals,
        logs: msg ? pushLog(s, { ts: now, level: 'tool', source: label, text: msg }) : s.logs,
      };
    }
    case 'agent_done': {
      const label = ev.agent ?? '?';
      const u = usageOf(ev.data);
      const iters = typeof ev.data?.iters === 'number' ? ev.data.iters : undefined;
      let agents = s.agents.map((a) =>
        a.label === label
          ? {
              ...a,
              status: 'done' as AgentStatus,
              endedAt: now,
              iters,
              inputTokens: u ? u.input : a.inputTokens,
              outputTokens: u ? u.output : a.outputTokens,
            }
          : a,
      );
      if (!s.agents.some((a) => a.label === label)) {
        agents = [...agents, {
          label, phase: key ?? s.currentPhase ?? '?', status: 'done', startedAt: now, endedAt: now,
          inputTokens: u?.input ?? 0, outputTokens: u?.output ?? 0, iters,
        }];
      }
      return {
        ...s,
        agents,
        totals: totalsFrom(agents, s.totals),
        logs: pushLog(s, {
          ts: now, level: 'ok', source: label, text: `done${u ? ` (${u.output} out tok)` : ''}`,
        }),
      };
    }
    case 'agent_error': {
      const label = ev.agent ?? '?';
      let agents = s.agents.map((a) =>
        a.label === label ? { ...a, status: 'error' as AgentStatus, endedAt: now, error: msg } : a,
      );
      if (!s.agents.some((a) => a.label === label)) {
        agents = [...agents, {
          label, phase: key ?? s.currentPhase ?? '?', status: 'error', startedAt: now, endedAt: now,
          inputTokens: 0, outputTokens: 0, error: msg,
        }];
      }
      return {
        ...s,
        agents,
        totals: totalsFrom(agents, s.totals),
        errors: [...s.errors, `${label}: ${msg}`],
        logs: pushLog(s, { ts: now, level: 'error', source: label, text: msg || 'failed' }),
      };
    }
    case 'run_warning':
      return {
        ...s,
        warnings: msg ? [...s.warnings, msg] : s.warnings,
        logs: pushLog(s, { ts: now, level: 'warn', source: key ?? 'run', text: msg }),
      };
    case 'run_error':
      return {
        ...s,
        errors: [...s.errors, msg],
        phases: key ? updatePhase(s, key, (p) => ({ ...p, status: 'error' })) : s.phases,
        logs: pushLog(s, { ts: now, level: 'error', source: key ?? 'run', text: msg }),
      };
    case 'log': {
      const logged = { ...s, logs: pushLog(s, { ts: now, level: 'info', source: ev.agent ?? key ?? 'log', text: msg }) };
      return s.sawStages ? logged : inferPhase(logged, msg, now);
    }
    case 'run_done': {
      const d = ev.data ?? {};
      const u = usageOf(d);
      const ver = (d.verification as Verification | undefined) ?? null;
      const phases = s.phases.map((p) =>
        p.status === 'pending' && !s.inferred
          ? { ...p, status: 'skipped' as PhaseStatus }
          : p.status === 'running'
            ? { ...p, status: 'done' as PhaseStatus, open: 0, endedAt: now }
            : p,
      );
      return {
        ...s,
        status: 'done',
        endedAt: now,
        phases,
        currentPhase: null,
        totals: {
          ...s.totals,
          inputTokens: u ? Math.max(u.input, s.totals.inputTokens) : s.totals.inputTokens,
          outputTokens: u ? Math.max(u.output, s.totals.outputTokens) : s.totals.outputTokens,
        },
        result: {
          dossier: msg && msg !== '(no dossier)' ? msg : null,
          runDir: null,
          slug: null,
          agentsOk: num(d.agents_ok) || s.totals.agentsOk,
          agentsTotal: num(d.agents_total) || s.totals.agentsTotal,
          verification: ver && Object.keys(ver).length ? ver : null,
          entityAmbiguity: null,
          errors: s.errors,
        },
        logs: pushLog(s, { ts: now, level: 'ok', source: 'run', text: `run done: ${msg}` }),
      };
    }
    default:
      return s;
  }
}

// Text-only engines (the workflow backend) still mention phases: "P7R round 1: ...", "P2 Wave A".
// Advance the timeline when a later phase is named; never move it backwards.
export function inferPhase(s: RunState, text: string, now: number): RunState {
  const m = /\b(P[0-8]R?)\b/.exec(text);
  if (!m) return s;
  const key = m[1];
  const idx = s.phases.findIndex((p) => p.key === key);
  const cur = s.phases.findIndex((p) => p.key === s.currentPhase);
  if (idx < 0 || idx <= cur) return s;
  return {
    ...s,
    inferred: true,
    status: s.status === 'idle' ? 'running' : s.status,
    currentPhase: key,
    phases: s.phases.map((p, i) =>
      i === idx
        ? { ...p, status: 'running', open: 1, startedAt: now }
        : p.status === 'running'
          ? { ...p, status: 'done', open: 0, endedAt: now }
          : p,
    ),
  };
}

function finishRun(
  s: RunState,
  a: { result: Record<string, unknown> | null; code: number; stderr: string; cancelled: boolean; now?: number },
): RunState {
  const now = a.now ?? Date.now();
  const r = a.result;
  const strOrNull = (v: unknown) => (typeof v === 'string' && v.length ? v : null);
  const prev = s.result;
  const errors = Array.isArray(r?.errors) ? (r.errors as unknown[]).map(String) : prev?.errors ?? s.errors;
  const summary: RunResultSummary | null = r
    ? {
        dossier: strOrNull(r.dossier) ?? prev?.dossier ?? null,
        runDir: strOrNull(r.run_dir),
        slug: strOrNull(r.slug),
        agentsOk: num(r.agents_ok) || prev?.agentsOk || 0,
        agentsTotal: num(r.agents_total) || prev?.agentsTotal || 0,
        verification: (r.verification as Verification | null) ?? prev?.verification ?? null,
        entityAmbiguity: strOrNull(r.entity_ambiguity),
        errors,
      }
    : prev;
  const u = usageOf(r ?? undefined);
  const status: RunState['status'] = a.cancelled
    ? 'cancelled'
    : summary && (summary.dossier || a.code === 0)
      ? 'done'
      : 'failed';
  const extra = !r && a.stderr ? [a.stderr] : [];
  return {
    ...s,
    status,
    endedAt: s.endedAt ?? now,
    currentPhase: null,
    phases: s.phases.map((p) =>
      p.status === 'running'
        ? { ...p, status: (status === 'done' ? 'done' : 'error') as PhaseStatus, open: 0, endedAt: now }
        : p.status === 'pending' && status === 'done' && !s.inferred
          ? { ...p, status: 'skipped' as PhaseStatus }
          : p,
    ),
    agents: status === 'done' ? s.agents : s.agents.map((ag) => (ag.status === 'running' ? { ...ag, status: 'error', endedAt: now, error: a.cancelled ? 'cancelled' : 'engine exited' } : ag)),
    totals: u ? { ...s.totals, inputTokens: u.input, outputTokens: u.output } : s.totals,
    errors: [...s.errors, ...extra],
    result: summary,
    logs: pushLog(s, {
      ts: now,
      level: status === 'done' ? 'ok' : 'error',
      source: 'engine',
      text: a.cancelled ? 'run cancelled' : `engine exited with code ${a.code}`,
    }),
  };
}

// Phases that make up the overall progress fraction: everything not skipped.
export function progress(s: RunState): number {
  const live = s.phases.filter((p) => p.status !== 'skipped');
  if (!live.length) return 0;
  const done = live.filter((p) => p.status === 'done' || p.status === 'error').length;
  const running = live.filter((p) => p.status === 'running').length;
  return Math.min(1, (done + running * 0.5) / live.length);
}
