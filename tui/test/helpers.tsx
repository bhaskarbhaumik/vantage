// Shared test helpers: a fake engine bridge backed by the recorded fixtures, and render helpers.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import React from 'react';
import { render } from 'ink-testing-library';
import { App, type AppProps } from '../src/app.js';
import type { CliArgs } from '../src/lib/args.js';
import { defaultsFrom, type JsonObject } from '../src/lib/config.js';
import type {
  Bridge,
  ExportParams,
  Res,
  RunEvent,
  RunInfo,
  RunParams,
  Stream,
  StreamOutcome,
} from '../src/lib/engine.js';
import type { UiPrefs } from '../src/lib/theme.js';

const here = path.dirname(fileURLToPath(import.meta.url));
export const FIXTURES = path.join(here, 'fixtures');

export interface Recorded {
  events: RunEvent[];
  result: Record<string, unknown> | null;
}

export function loadStream(name: string): Recorded {
  const lines = fs.readFileSync(path.join(FIXTURES, name), 'utf8').split('\n').filter(Boolean);
  const events: RunEvent[] = [];
  let result: Record<string, unknown> | null = null;
  for (const l of lines) {
    const o = JSON.parse(l) as Record<string, unknown>;
    if ('result' in o && !('type' in o)) result = o.result as Record<string, unknown>;
    else events.push(o as unknown as RunEvent);
  }
  return { events, result };
}

export function loadRuns(): RunInfo[] {
  return (JSON.parse(fs.readFileSync(path.join(FIXTURES, 'runs-list.json'), 'utf8')) as { runs: RunInfo[] }).runs;
}

export const CONFIG: JsonObject = {
  engine: { backend: 'workflow', tier: 'FULL_ANNEX', available_backends: ['workflow', 'api', 'agent-sdk'] },
  auth: { mode: 'subscription' },
  run_defaults: { capability_pack: 'NOT_ATTACHED', account_team_input_sheet: 'NOT_ATTACHED' },
  export: { formats: ['pptx', 'docx'], depth: 'standard', helpers: { icons: true, diagrams: 'auto' } },
  ui: { icons: 'nerd', color: 'auto', theme: 'dark', animations: true },
};

function replay(rec: Recorded, onEvent: (ev: RunEvent) => void, failWith?: string): Stream {
  let cancelled = false;
  const done = new Promise<StreamOutcome>((resolve) => {
    let i = 0;
    const tick = () => {
      if (cancelled) return resolve({ result: null, code: 143, stderr: '', cancelled: true });
      if (i < rec.events.length) {
        onEvent(rec.events[i++]);
        setImmediate(tick);
      } else if (failWith) {
        resolve({ result: null, code: 2, stderr: failWith, cancelled: false });
      } else {
        resolve({ result: rec.result, code: 0, stderr: '', cancelled: false });
      }
    };
    setImmediate(tick);
  });
  return { done, cancel: () => (cancelled = true) };
}

export class FakeBridge implements Bridge {
  calls: string[][] = [];
  constructor(private readonly opts: { failAll?: string } = {}) {}
  private res<T>(data: T): Promise<Res<T>> {
    return Promise.resolve(this.opts.failAll ? { ok: false, error: this.opts.failAll } : { ok: true, data });
  }
  describe(): string {
    return 'fake-engine';
  }
  version() {
    this.calls.push(['version']);
    return this.res({ version: '0.2.0', harness: '3.0.0', config: '2.2', python: '3.14.0' });
  }
  doctor() {
    this.calls.push(['doctor']);
    return this.res({
      version: '0.2.0',
      checks: [
        { group: 'auth', name: 'mode', status: 'ok', detail: 'subscription' },
        { group: 'export', name: 'soffice', status: 'warn', detail: 'not on PATH - pdf disabled' },
        { group: 'backends', name: 'crewai', status: 'fail', detail: 'package not installed' },
      ],
    });
  }
  backends() {
    this.calls.push(['backends']);
    return this.res({
      default: 'workflow',
      backends: [
        { name: 'workflow', ready: true, issues: [] },
        { name: 'api', ready: false, issues: ['ANTHROPIC_API_KEY not set'] },
      ],
    });
  }
  configShow() {
    this.calls.push(['config', 'show']);
    return this.res(CONFIG as Record<string, unknown>);
  }
  configSet(key: string, value: string) {
    this.calls.push(['config', 'set', key, value]);
    return this.res(`${key} = ${value}`);
  }
  runsList() {
    this.calls.push(['runs', 'list']);
    return this.res(loadRuns());
  }
  runsShow(slug: string) {
    this.calls.push(['runs', 'show', slug]);
    const r = loadRuns().find((x) => x.slug === slug);
    if (!r) return Promise.resolve({ ok: false as const, error: `no run ${slug}` });
    return this.res({ ...r, sections: ['00-run-contract.md', '03-company.md', '04-market.md'] });
  }
  startRun(p: RunParams, onEvent: (ev: RunEvent) => void): Stream {
    this.calls.push(['run', p.client, p.slug]);
    return replay(loadStream('run-events.jsonl'), onEvent, this.opts.failAll);
  }
  startExport(p: ExportParams, onEvent: (ev: RunEvent) => void): Stream {
    this.calls.push(['export', p.dossier, p.formats.join(',')]);
    return replay(loadStream('export-events.jsonl'), onEvent, this.opts.failAll);
  }
}

export const NERD: UiPrefs = { icons: 'nerd', color: true, theme: 'dark', animations: false };
export const ASCII_NOCOLOR: UiPrefs = { icons: 'ascii', color: false, theme: 'dark', animations: false };

export function renderApp(
  opts: {
    bridge?: Bridge;
    prefs?: UiPrefs;
    args?: Partial<Pick<CliArgs, 'screen' | 'run' | 'exportOpts' | 'slug' | 'help'>>;
    width?: number;
  } = {},
) {
  const props: AppProps = {
    bridge: opts.bridge ?? new FakeBridge(),
    args: { screen: 'home', run: {}, exportOpts: {}, help: false, ...opts.args },
    prefs: opts.prefs ?? NERD,
    defaults: defaultsFrom(CONFIG),
    localConfig: CONFIG,
    tuiVersion: '0.2.0',
    width: opts.width ?? 100,
    height: 40,
  };
  return render(<App {...props} />);
}

export const wait = (ms = 40) => new Promise((r) => setTimeout(r, ms));

export const KEYS = {
  up: '\u001B[A',
  down: '\u001B[B',
  right: '\u001B[C',
  left: '\u001B[D',
  enter: '\r',
  esc: '\u001B',
  tab: '\t',
  shiftTab: '\u001B[Z',
};

export async function press(stdin: { write(s: string): void }, ...keys: string[]): Promise<void> {
  for (const k of keys) {
    stdin.write(k);
    await wait(25);
  }
  await wait(40);
}

// eslint-disable-next-line no-control-regex
const ANSI = /\u001B\[[0-9;?]*[ -/]*[@-~]|\u001B\][^\u0007]*\u0007/g;

export function stripAnsi(s: string): string {
  return s.replace(ANSI, '');
}

export function nonAscii(s: string): string[] {
  return [...new Set([...s].filter((c) => (c.codePointAt(0) ?? 0) > 0x7f))];
}
