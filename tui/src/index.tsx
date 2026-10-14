#!/usr/bin/env node
// vantage-tui entry point: parse the command line, resolve presentation preferences, then render.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import React from 'react';
import { render } from 'ink';
import chalk from 'chalk';
import { App } from './app.js';
import { HELP_TEXT, parseArgs } from './lib/args.js';
import { defaultsFrom, loadLocalConfig, type JsonObject } from './lib/config.js';
import { CliBridge } from './lib/engine.js';
import { toAscii } from './lib/icons.js';
import { resolvePrefs, type UiPrefs, type UiSection } from './lib/theme.js';

export function tuiVersion(): string {
  try {
    const here = path.dirname(fileURLToPath(import.meta.url));
    const pkg = JSON.parse(fs.readFileSync(path.resolve(here, '..', '..', 'package.json'), 'utf8')) as { version?: string };
    return pkg.version ?? '0.0.0';
  } catch {
    return '0.0.0';
  }
}

// Chalk decides colour support once; force it to match the resolved preference.
export function applyColor(prefs: UiPrefs): void {
  if (!prefs.color) chalk.level = 0;
  else if (chalk.level === 0) chalk.level = 3;
}

function main(): void {
  const args = parseArgs(process.argv.slice(2));
  const config: JsonObject = loadLocalConfig();
  const prefs = resolvePrefs(config.ui as UiSection | undefined, args.prefs, process.env, Boolean(process.stdout.isTTY));
  const out = (s: string) => process.stdout.write(prefs.icons === 'ascii' ? toAscii(s) : s);

  if (args.version) {
    out(`vantage-tui ${tuiVersion()}\n`);
    return;
  }
  if (args.help) {
    out(HELP_TEXT);
    return;
  }
  if (args.errors.length) {
    for (const e of args.errors) process.stderr.write(`vantage-tui: ${e}\n`);
    process.stderr.write('run `vantage-tui --help` for usage\n');
    process.exitCode = 2;
    return;
  }
  if (!process.stdin.isTTY || !process.stdout.isTTY) {
    process.stderr.write(
      'vantage-tui needs an interactive terminal (stdin and stdout must be a TTY).\n' +
        'For scripts, pipes and CI use the engine CLI instead, for example:\n' +
        '  vantage run --client "Example Corp" --slug example-2026-10 --json\n' +
        '  vantage runs list --json\n',
    );
    process.exitCode = 1;
    return;
  }

  applyColor(prefs);
  const bridge = new CliBridge();
  const app = render(
    <App
      bridge={bridge}
      args={args}
      prefs={prefs}
      defaults={defaultsFrom(config)}
      localConfig={config}
      tuiVersion={tuiVersion()}
    />,
    { exitOnCtrlC: false },
  );
  void app.waitUntilExit().then(() => process.exit(0));
}

main();
