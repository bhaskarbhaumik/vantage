// Bridge to the Python engine. Every call spawns the `vantage` CLI and reads its JSON contract;
// nothing here throws — failures come back as `{ ok: false, error }` for an error panel.
import { spawn, type ChildProcess } from 'node:child_process';
import path from 'node:path';
import readline from 'node:readline';
import { fileURLToPath } from 'node:url';

// --- contract types ---------------------------------------------------------------------------

export interface RunEvent {
  type: string;
  ts?: number;
  stage?: string | null;
  agent?: string | null;
  message?: string | null;
  data?: Record<string, unknown>;
}

export interface Verification {
  result?: string | null;
  overall_confidence?: string | null;
  eqi?: number | string | null;
  blockers?: number | null;
  majors?: number | null;
  minors?: number | null;
  budget_limited_topics?: string[] | null;
  [k: string]: unknown;
}

export interface RunInfo {
  slug: string;
  run_dir: string;
  dossier: string | null;
  client: string | null;
  as_of: string | null;
  tier: string | null;
  mtime: number;
  verification: Verification | null;
  exports: string[];
  sections?: string[];
}

export interface VersionInfo {
  version: string;
  harness?: string;
  config?: string;
  python?: string;
}

export interface Check {
  group: string;
  name: string;
  status: 'ok' | 'warn' | 'fail' | string;
  detail: string;
}

export interface DoctorReport {
  version?: string;
  checks: Check[];
}

export interface BackendInfo {
  name: string;
  ready: boolean;
  issues: string[];
}

export interface BackendsReport {
  default: string;
  backends: BackendInfo[];
}

export interface RunParams {
  client: string;
  slug: string;
  backend?: string;
  tier?: string;
  asOf?: string;
  ticker?: string;
  vertical?: string;
  geography?: string;
  commonName?: string;
  capabilityPack?: string;
  inputSheet?: string;
  accountContext?: string;
  relationship?: string;
  objectives?: string;
  authMode?: string;
  askKey?: boolean;
  remediationRounds?: number;
}

export interface ExportParams {
  dossier: string;
  formats: string[];
  depth?: string;
  siteMode?: string;
  authoring?: string;
  outDir?: string;
  classification?: string;
  brand?: string;
  clientLogo?: boolean;
  // Only helpers that differ from the configured defaults are sent: icons|brand|stock_images
  // take on/off, diagrams|illustrations|charts take their value.
  helpers?: Record<string, string>;
}

export type Res<T> = { ok: true; data: T } | { ok: false; error: string; code?: number };

export interface StreamOutcome {
  result: Record<string, unknown> | null;
  code: number;
  stderr: string;
  cancelled: boolean;
}

export interface Stream {
  done: Promise<StreamOutcome>;
  cancel(): void;
}

export interface Bridge {
  describe(): string;
  version(): Promise<Res<VersionInfo>>;
  doctor(): Promise<Res<DoctorReport>>;
  backends(): Promise<Res<BackendsReport>>;
  configShow(): Promise<Res<Record<string, unknown>>>;
  configSet(key: string, value: string): Promise<Res<string>>;
  runsList(): Promise<Res<RunInfo[]>>;
  runsShow(slug: string): Promise<Res<RunInfo>>;
  startRun(p: RunParams, onEvent: (ev: RunEvent) => void): Stream;
  startExport(p: ExportParams, onEvent: (ev: RunEvent) => void): Stream;
}

// --- command line -----------------------------------------------------------------------------

export function repoRoot(): string {
  // tui/{src,dist}/lib/engine.{ts,js} -> ../../.. is the repo root
  const here = fileURLToPath(import.meta.url);
  return path.resolve(path.dirname(here), '..', '..', '..');
}

// Split VANTAGE_ENGINE like a shell would for the simple cases: whitespace, single/double quotes.
export function splitCommand(s: string): string[] {
  const out: string[] = [];
  let cur = '';
  let quote: string | null = null;
  let has = false;
  for (const ch of s) {
    if (quote) {
      if (ch === quote) quote = null;
      else cur += ch;
    } else if (ch === '"' || ch === "'") {
      quote = ch;
      has = true;
    } else if (/\s/.test(ch)) {
      if (has || cur) out.push(cur);
      cur = '';
      has = false;
    } else {
      cur += ch;
      has = true;
    }
  }
  if (has || cur) out.push(cur);
  return out;
}

export function engineCommand(env: NodeJS.ProcessEnv = process.env): { cmd: string; baseArgs: string[] } {
  const override = env.VANTAGE_ENGINE;
  if (override && override.trim()) {
    const parts = splitCommand(override.trim());
    return { cmd: parts[0], baseArgs: parts.slice(1) };
  }
  return { cmd: 'uv', baseArgs: ['run', '--quiet', '--project', repoRoot(), 'vantage'] };
}

export function runArgs(p: RunParams): string[] {
  const a: string[] = ['run', '--client', p.client, '--slug', p.slug, '--json'];
  const push = (flag: string, val?: string) => {
    if (val !== undefined && val.trim().length) a.push(flag, val.trim());
  };
  push('--backend', p.backend);
  push('--tier', p.tier);
  push('--as-of', p.asOf);
  push('--common-name', p.commonName);
  push('--ticker', p.ticker);
  push('--vertical', p.vertical);
  push('--geography', p.geography);
  push('--capability-pack', p.capabilityPack);
  push('--input-sheet', p.inputSheet);
  push('--account-context', p.accountContext);
  push('--relationship', p.relationship);
  push('--objectives', p.objectives);
  push('--auth', p.authMode);
  if (p.askKey) a.push('--ask-key');
  // Sent only when it differs from the engine default (1 round), so older engines still run.
  if (p.remediationRounds !== undefined && p.remediationRounds !== 1) {
    a.push('--remediation-rounds', String(p.remediationRounds));
  }
  return a;
}

const HELPER_SWITCHES: Record<string, [string, string]> = {
  icons: ['--helper-icons', '--no-helper-icons'],
  brand: ['--helper-brand', '--no-helper-brand'],
  stock_images: ['--stock-images', '--no-stock-images'],
};

export function exportArgs(p: ExportParams): string[] {
  const a: string[] = ['export', p.dossier, '--json'];
  for (const f of p.formats) a.push('--format', f);
  const push = (flag: string, val?: string) => {
    if (val !== undefined && val.trim().length) a.push(flag, val.trim());
  };
  push('--depth', p.depth);
  push('--site-mode', p.siteMode);
  push('--authoring', p.authoring);
  push('--out', p.outDir);
  push('--classification', p.classification);
  push('--brand', p.brand);
  if (p.clientLogo !== undefined) a.push(p.clientLogo ? '--client-logo' : '--no-client-logo');
  for (const [k, v] of Object.entries(p.helpers ?? {})) {
    const sw = HELPER_SWITCHES[k];
    if (sw) a.push(v === 'on' ? sw[0] : sw[1]);
    else push(`--${k.replace(/_/g, '-')}`, v);
  }
  return a;
}

// --- process helpers --------------------------------------------------------------------------

function tail(s: string, lines = 6): string {
  return s.split('\n').map((l) => l.trimEnd()).filter(Boolean).slice(-lines).join('\n');
}

function spawnError(e: NodeJS.ErrnoException, cmd: string): string {
  if (e.code === 'ENOENT') {
    return `engine command not found: ${cmd}. Install uv (https://docs.astral.sh/uv/) or set VANTAGE_ENGINE.`;
  }
  return `could not start the engine (${cmd}): ${e.message}`;
}

export function parseJsonOutput(stdout: string): unknown {
  const s = stdout.trim();
  if (!s) throw new Error('empty output');
  try {
    return JSON.parse(s);
  } catch {
    // Tolerate a stray banner line: take the last line that parses.
    const lines = s.split('\n').reverse();
    for (const l of lines) {
      try {
        return JSON.parse(l);
      } catch {
        /* keep looking */
      }
    }
    throw new Error('output is not JSON');
  }
}

interface Captured {
  code: number;
  stdout: string;
  stderr: string;
  spawnError?: string;
}

function capture(cmd: string, args: string[], timeoutMs: number): Promise<Captured> {
  return new Promise((resolve) => {
    let stdout = '';
    let stderr = '';
    let settled = false;
    let child: ChildProcess;
    const finish = (c: Captured) => {
      if (!settled) {
        settled = true;
        clearTimeout(timer);
        resolve(c);
      }
    };
    try {
      child = spawn(cmd, args, { env: { ...process.env, NO_COLOR: '1' }, stdio: ['ignore', 'pipe', 'pipe'] });
    } catch (e) {
      resolve({ code: 127, stdout: '', stderr: '', spawnError: spawnError(e as NodeJS.ErrnoException, cmd) });
      return;
    }
    const timer = setTimeout(() => {
      child.kill('SIGTERM');
      finish({ code: 124, stdout, stderr: `${stderr}\ntimed out after ${Math.round(timeoutMs / 1000)}s` });
    }, timeoutMs);
    child.stdout?.on('data', (d: Buffer) => (stdout += d.toString()));
    child.stderr?.on('data', (d: Buffer) => (stderr += d.toString()));
    child.on('error', (e) => finish({ code: 127, stdout, stderr, spawnError: spawnError(e, cmd) }));
    child.on('close', (code) => finish({ code: code ?? 1, stdout, stderr }));
  });
}

function describeFailure(c: Captured, label: string): string {
  if (c.spawnError) return c.spawnError;
  const err = tail(c.stderr);
  if (/No such (command|option)|unexpected extra argument|Got unexpected/i.test(c.stderr)) {
    return `this engine does not support \`vantage ${label}\` yet — update the engine.\n${err}`;
  }
  return err || `\`vantage ${label}\` exited with code ${c.code}`;
}

// --- default bridge: spawns the CLI ----------------------------------------------------------

export class CliBridge implements Bridge {
  private readonly cmd: string;
  private readonly baseArgs: string[];

  constructor(env: NodeJS.ProcessEnv = process.env, private readonly timeoutMs = 120_000) {
    const c = engineCommand(env);
    this.cmd = c.cmd;
    this.baseArgs = c.baseArgs;
  }

  describe(): string {
    return [this.cmd, ...this.baseArgs].join(' ');
  }

  private async json<T>(args: string[], label: string, accept?: (c: Captured) => T | null): Promise<Res<T>> {
    const c = await capture(this.cmd, [...this.baseArgs, ...args], this.timeoutMs);
    if (c.code === 0) {
      try {
        return { ok: true, data: parseJsonOutput(c.stdout) as T };
      } catch {
        const alt = accept?.(c);
        if (alt) return { ok: true, data: alt };
        return { ok: false, error: `\`vantage ${label}\` did not return JSON — update the engine.`, code: c.code };
      }
    }
    const alt = accept?.(c);
    if (alt) return { ok: true, data: alt };
    return { ok: false, error: describeFailure(c, label), code: c.code };
  }

  version(): Promise<Res<VersionInfo>> {
    // Older engines print a bare version string and reject --json.
    return this.json<VersionInfo>(['version', '--json'], 'version --json', (c) => {
      const m = /(\d+\.\d+\.\d+\S*)/.exec(c.stdout);
      return c.code === 0 && m ? { version: m[1] } : null;
    });
  }

  doctor(): Promise<Res<DoctorReport>> {
    return this.json<DoctorReport>(['doctor', '--json'], 'doctor --json').then((r) =>
      r.ok && !Array.isArray(r.data.checks) ? { ok: false, error: 'doctor JSON has no "checks" list' } : r,
    );
  }

  backends(): Promise<Res<BackendsReport>> {
    return this.json<BackendsReport>(['backends', '--json'], 'backends --json').then((r) =>
      r.ok && !Array.isArray(r.data.backends) ? { ok: false, error: 'backends JSON has no "backends" list' } : r,
    );
  }

  configShow(): Promise<Res<Record<string, unknown>>> {
    return this.json<Record<string, unknown>>(['config', 'show', '--json'], 'config show --json');
  }

  async configSet(key: string, value: string): Promise<Res<string>> {
    const c = await capture(this.cmd, [...this.baseArgs, 'config', 'set', key, value], this.timeoutMs);
    if (c.code === 0) return { ok: true, data: tail(c.stdout || c.stderr, 2) || `${key} = ${value}` };
    return { ok: false, error: describeFailure(c, 'config set'), code: c.code };
  }

  async runsList(): Promise<Res<RunInfo[]>> {
    const r = await this.json<{ runs?: RunInfo[] }>(['runs', 'list', '--json'], 'runs list --json');
    if (!r.ok) return r;
    if (!Array.isArray(r.data.runs)) return { ok: false, error: 'runs JSON has no "runs" list' };
    return { ok: true, data: r.data.runs };
  }

  runsShow(slug: string): Promise<Res<RunInfo>> {
    return this.json<RunInfo>(['runs', 'show', slug, '--json'], 'runs show --json');
  }

  private stream(args: string[], onEvent: (ev: RunEvent) => void): Stream {
    let child: ChildProcess | null = null;
    let cancelled = false;
    const done = new Promise<StreamOutcome>((resolve) => {
      let result: Record<string, unknown> | null = null;
      let stderr = '';
      let settled = false;
      const finish = (o: StreamOutcome) => {
        if (!settled) {
          settled = true;
          resolve(o);
        }
      };
      try {
        child = spawn(this.cmd, [...this.baseArgs, ...args], {
          env: { ...process.env, NO_COLOR: '1' },
          stdio: ['ignore', 'pipe', 'pipe'],
        });
      } catch (e) {
        finish({ result: null, code: 127, stderr: spawnError(e as NodeJS.ErrnoException, this.cmd), cancelled });
        return;
      }
      const c = child;
      const rl = readline.createInterface({ input: c.stdout! });
      rl.on('line', (line) => {
        const s = line.trim();
        if (!s.startsWith('{')) return;
        try {
          const obj = JSON.parse(s) as Record<string, unknown>;
          if ('result' in obj && !('type' in obj)) result = (obj.result as Record<string, unknown>) ?? null;
          else if (typeof obj.type === 'string') onEvent(obj as unknown as RunEvent);
        } catch {
          /* ignore non-JSON noise */
        }
      });
      c.stderr?.on('data', (d: Buffer) => {
        stderr += d.toString();
        if (stderr.length > 64_000) stderr = stderr.slice(-32_000);
      });
      c.on('error', (e) => finish({ result, code: 127, stderr: spawnError(e, this.cmd), cancelled }));
      c.on('close', (code) => {
        rl.close();
        const failed = (code ?? 1) !== 0 && !result;
        finish({
          result,
          code: code ?? 1,
          stderr: failed ? describeFailure({ code: code ?? 1, stdout: '', stderr }, args[0]) : tail(stderr),
          cancelled,
        });
      });
    });
    return {
      done,
      cancel: () => {
        cancelled = true;
        child?.kill('SIGTERM');
      },
    };
  }

  startRun(p: RunParams, onEvent: (ev: RunEvent) => void): Stream {
    return this.stream(runArgs(p), onEvent);
  }

  startExport(p: ExportParams, onEvent: (ev: RunEvent) => void): Stream {
    return this.stream(exportArgs(p), onEvent);
  }
}
