// Spawn the Python engine and stream its JSON event protocol.
import { spawn } from 'node:child_process';
import readline from 'node:readline';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

export interface RunEvent {
  type: string;
  ts?: number;
  stage?: string | null;
  agent?: string | null;
  message?: string | null;
  data?: Record<string, unknown>;
}

export interface RunParams {
  client: string;
  slug: string;
  backend?: string;
  tier?: string;
  capabilityPack?: string;
  inputSheet?: string;
  asOf?: string;
  ticker?: string;
  vertical?: string;
  geography?: string;
  commonName?: string;
  accountContext?: string;
  relationship?: string;
  objectives?: string;
  authMode?: string;
  askKey?: boolean;
}

export function repoRoot(): string {
  // cli/{src,dist}/lib/engine.{ts,js} -> ../../../ == repo root
  const here = fileURLToPath(import.meta.url);
  return path.resolve(path.dirname(here), '..', '..', '..');
}

export function engineCommand(): { cmd: string; baseArgs: string[] } {
  const override = process.env.VANTAGE_ENGINE;
  if (override) {
    const parts = override.split(' ').filter(Boolean);
    return { cmd: parts[0], baseArgs: parts.slice(1) };
  }
  return { cmd: 'uv', baseArgs: ['run', '--project', repoRoot(), 'vantage-engine'] };
}

function runFlags(p: RunParams): string[] {
  const a: string[] = ['run', '--client', p.client, '--slug', p.slug, '--json'];
  const push = (flag: string, val?: string) => {
    if (val && val.length) a.push(flag, val);
  };
  push('--backend', p.backend);
  push('--tier', p.tier);
  push('--capability-pack', p.capabilityPack);
  push('--input-sheet', p.inputSheet);
  push('--as-of', p.asOf);
  push('--ticker', p.ticker);
  push('--vertical', p.vertical);
  push('--geography', p.geography);
  push('--common-name', p.commonName);
  push('--account-context', p.accountContext);
  push('--relationship', p.relationship);
  push('--objectives', p.objectives);
  push('--auth', p.authMode);
  if (p.askKey) a.push('--ask-key');
  return a;
}

export interface RunOutcome {
  result: Record<string, unknown> | null;
  code: number;
  stderr: string;
}

export function runEngine(p: RunParams, onEvent: (ev: RunEvent) => void): Promise<RunOutcome> {
  const { cmd, baseArgs } = engineCommand();
  const child = spawn(cmd, [...baseArgs, ...runFlags(p)], { env: process.env });
  let result: Record<string, unknown> | null = null;
  let stderr = '';

  const rl = readline.createInterface({ input: child.stdout });
  rl.on('line', (line) => {
    const s = line.trim();
    if (!s) return;
    try {
      const obj = JSON.parse(s);
      if (obj && typeof obj === 'object' && 'result' in obj) result = obj.result;
      else onEvent(obj as RunEvent);
    } catch {
      /* ignore non-JSON noise */
    }
  });
  child.stderr.on('data', (d) => {
    stderr += d.toString();
  });

  return new Promise((resolve) => {
    child.on('close', (code) => resolve({ result, code: code ?? 1, stderr }));
    child.on('error', (e) => resolve({ result: null, code: 127, stderr: String(e) }));
  });
}

// Passthrough for non-run subcommands (doctor/backends/config/deploy/version).
export function passthrough(argv: string[]): Promise<number> {
  const { cmd, baseArgs } = engineCommand();
  const child = spawn(cmd, [...baseArgs, ...argv], { stdio: 'inherit', env: process.env });
  return new Promise((resolve) => {
    child.on('close', (code) => resolve(code ?? 0));
    child.on('error', () => resolve(127));
  });
}
