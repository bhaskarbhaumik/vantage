// Pure reducer from `vantage export --json` events to the export wizard's progress state.
import type { RunEvent } from './engine.js';

export interface ExportArtifact {
  format: string;
  path: string;
  bytes: number;
  pages?: number | null;
  slides?: number | null;
}

export interface ExportStage {
  name: string;
  status: 'pending' | 'running' | 'done' | 'error' | 'skipped';
  message?: string;
}

export interface ExportState {
  status: 'idle' | 'running' | 'done' | 'failed' | 'cancelled';
  startedAt?: number;
  endedAt?: number;
  stages: ExportStage[];
  artifacts: ExportArtifact[];
  warnings: string[];
  errors: string[];
  logs: string[];
  outDir: string | null;
  manifest: string | null;
  plans: Record<string, string>;
}

// The stage list the engine announces for a given format selection (pdf implies docx).
export function expectedStages(formats: string[]): string[] {
  const set = new Set(formats);
  if (set.has('pdf')) set.add('docx');
  const order = ['pptx', 'docx', 'pdf', 'html'].filter((f) => set.has(f));
  return ['ingest', 'plan', 'assets', 'charts', ...order.map((f) => `render:${f}`)];
}

export function initialExportState(formats: string[] = []): ExportState {
  return {
    status: 'idle',
    stages: expectedStages(formats).map((name) => ({ name, status: 'pending' })),
    artifacts: [],
    warnings: [],
    errors: [],
    logs: [],
    outDir: null,
    manifest: null,
    plans: {},
  };
}

function setStage(stages: ExportStage[], name: string, patch: Partial<ExportStage>): ExportStage[] {
  if (!stages.some((s) => s.name === name)) return [...stages, { name, status: 'pending', ...patch }];
  return stages.map((s) => (s.name === name ? { ...s, ...patch } : s));
}

export type ExportAction =
  | { kind: 'start'; formats: string[]; now?: number }
  | { kind: 'event'; event: RunEvent }
  | { kind: 'batch'; events: RunEvent[] }
  | { kind: 'reset' }
  | { kind: 'result'; result: Record<string, unknown> | null; code: number; stderr: string; cancelled: boolean; now?: number };

function toArtifact(d: Record<string, unknown>): ExportArtifact | null {
  if (typeof d.path !== 'string') return null;
  return {
    format: typeof d.format === 'string' ? d.format : 'file',
    path: d.path,
    bytes: typeof d.bytes === 'number' ? d.bytes : 0,
    pages: typeof d.pages === 'number' ? d.pages : null,
    slides: typeof d.slides === 'number' ? d.slides : null,
  };
}

export function exportReducer(s: ExportState, a: ExportAction): ExportState {
  if (a.kind === 'reset') return initialExportState();
  if (a.kind === 'batch') return a.events.reduce((acc, event) => exportReducer(acc, { kind: 'event', event }), s);
  if (a.kind === 'start') return { ...initialExportState(a.formats), status: 'running', startedAt: a.now ?? Date.now() };
  if (a.kind === 'result') {
    const r = a.result;
    const artifacts = Array.isArray(r?.artifacts)
      ? (r.artifacts as Record<string, unknown>[]).map(toArtifact).filter((x): x is ExportArtifact => x !== null)
      : s.artifacts;
    const warnings = Array.isArray(r?.warnings) ? (r.warnings as unknown[]).map(String) : s.warnings;
    const status: ExportState['status'] = a.cancelled ? 'cancelled' : r && a.code === 0 ? 'done' : 'failed';
    return {
      ...s,
      status,
      endedAt: a.now ?? Date.now(),
      artifacts: artifacts.length ? artifacts : s.artifacts,
      warnings: Array.from(new Set([...s.warnings, ...warnings])),
      errors: !r && a.stderr ? [...s.errors, a.stderr] : s.errors,
      outDir: typeof r?.out_dir === 'string' ? r.out_dir : s.outDir,
      manifest: typeof r?.manifest === 'string' ? r.manifest : s.manifest,
      plans: r?.plans && typeof r.plans === 'object' ? (r.plans as Record<string, string>) : s.plans,
      stages: s.stages.map((st) =>
        st.status === 'running'
          ? { ...st, status: status === 'done' ? 'done' : 'error' }
          : st.status === 'pending' && status === 'done'
            ? { ...st, status: 'skipped' }
            : st,
      ),
    };
  }
  const ev = a.event;
  const msg = ev.message ?? '';
  const logs = msg ? [...s.logs.slice(-499), `${ev.stage ?? ev.type}: ${msg}`] : s.logs;
  switch (ev.type) {
    case 'stage_start':
      return ev.stage ? { ...s, logs, stages: setStage(s.stages, ev.stage, { status: 'running' }) } : s;
    case 'stage_done':
      return ev.stage ? { ...s, logs, stages: setStage(s.stages, ev.stage, { status: 'done', message: msg || undefined }) } : s;
    case 'artifact': {
      const art = toArtifact(ev.data ?? {});
      return art ? { ...s, logs, artifacts: [...s.artifacts.filter((x) => x.path !== art.path), art] } : s;
    }
    case 'run_warning':
      return { ...s, logs, warnings: msg ? [...s.warnings, msg] : s.warnings };
    case 'run_error':
      return {
        ...s,
        logs,
        errors: [...s.errors, msg],
        stages: ev.stage ? setStage(s.stages, ev.stage, { status: 'error', message: msg }) : s.stages,
      };
    default:
      return { ...s, logs };
  }
}

export function exportProgress(s: ExportState): number {
  if (!s.stages.length) return 0;
  const done = s.stages.filter((x) => x.status !== 'pending' && x.status !== 'running').length;
  const running = s.stages.filter((x) => x.status === 'running').length;
  return Math.min(1, (done + running * 0.5) / s.stages.length);
}
