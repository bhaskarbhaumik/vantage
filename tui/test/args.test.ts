import assert from 'node:assert/strict';
import { test } from 'node:test';
import { initialRoutes } from '../src/app.js';
import { parseArgs } from '../src/lib/args.js';
import { exportArgs, runArgs, splitCommand } from '../src/lib/engine.js';

test('no arguments opens the home dashboard', () => {
  const a = parseArgs([]);
  assert.equal(a.screen, 'home');
  assert.deepEqual(a.errors, []);
  assert.deepEqual(initialRoutes(a), [{ screen: 'home' }]);
});

test('run deep link prefills the form', () => {
  const a = parseArgs(['run', '--client', 'Example Corp', '--slug=ex-1', '--tier', 'standard', '--ask-key', '--backend', 'api']);
  assert.equal(a.screen, 'run');
  assert.equal(a.run.client, 'Example Corp');
  assert.equal(a.run.slug, 'ex-1');
  assert.equal(a.run.tier, 'STANDARD');
  assert.equal(a.run.backend, 'api');
  assert.equal(a.run.askKey, true);
  const routes = initialRoutes(a);
  assert.equal(routes[0].screen, 'run');
  assert.equal(routes[0].params?.client, 'Example Corp');
});

test('aliases and positional client', () => {
  assert.equal(parseArgs(['new', 'Acme']).run.client, 'Acme');
  assert.equal(parseArgs(['settings']).screen, 'config');
});

test('runs with a slug opens the detail view over the list', () => {
  const a = parseArgs(['runs', 'example-2026-10']);
  assert.equal(a.slug, 'example-2026-10');
  assert.deepEqual(initialRoutes(a).map((r) => r.screen), ['runs', 'runDetail']);
});

test('export deep link carries the dossier and options', () => {
  const a = parseArgs(['export', 'example-2026-10', '--formats', 'pptx,PDF', '--depth', 'exec', '--no-client-logo', '--brand', 'example.org']);
  assert.equal(a.screen, 'export');
  assert.equal(a.exportOpts.dossier, 'example-2026-10');
  assert.deepEqual(a.exportOpts.formats, ['pptx', 'pdf']);
  assert.equal(a.exportOpts.depth, 'exec');
  assert.equal(a.exportOpts.clientLogo, false);
  assert.equal(a.exportOpts.brand, 'example.org');
});

test('presentation flags', () => {
  const a = parseArgs(['doctor', '--ascii', '--no-color', '--theme', 'light', '--no-animations', '--icons', 'unicode']);
  assert.equal(a.screen, 'doctor');
  assert.deepEqual(a.prefs, { ascii: true, icons: 'unicode', noColor: true, color: false, theme: 'light', noAnimations: true });
});

test('help, version and errors', () => {
  assert.equal(parseArgs(['--help']).help, true);
  assert.equal(parseArgs(['-h']).help, true);
  assert.equal(parseArgs(['help']).help, true);
  assert.equal(parseArgs(['--version']).version, true);
  assert.equal(parseArgs(['-v']).version, true);
  assert.match(parseArgs(['bogus']).errors[0], /unknown screen/);
  assert.match(parseArgs(['--icons', 'emoji']).errors[0], /--icons/);
  assert.match(parseArgs(['run', '--client']).errors[0], /needs a value/);
});

test('engine argument builders follow the CLI contract', () => {
  const r = runArgs({ client: 'Example Corp', slug: 'ex', tier: 'STANDARD', authMode: 'subscription', remediationRounds: 1 });
  assert.deepEqual(r, ['run', '--client', 'Example Corp', '--slug', 'ex', '--json', '--tier', 'STANDARD', '--auth', 'subscription']);
  assert.ok(runArgs({ client: 'a', slug: 'b', remediationRounds: 2 }).join(' ').endsWith('--remediation-rounds 2'));
  const e = exportArgs({
    dossier: '/r/x', formats: ['pptx', 'pdf'], depth: 'full', outDir: '/o', clientLogo: false,
    helpers: { charts: 'plotly', icons: 'off', stock_images: 'on' },
  });
  assert.deepEqual(e, [
    'export', '/r/x', '--json', '--format', 'pptx', '--format', 'pdf', '--depth', 'full', '--out', '/o',
    '--no-client-logo', '--charts', 'plotly', '--no-helper-icons', '--stock-images',
  ]);
});

test('VANTAGE_ENGINE splitting honours quotes', () => {
  assert.deepEqual(splitCommand('uv run --project "/a b/c" vantage'), ['uv', 'run', '--project', '/a b/c', 'vantage']);
  assert.deepEqual(splitCommand("python -m 'vantage.cli'"), ['python', '-m', 'vantage.cli']);
});

test('VANTAGE_CONFIG overrides the XDG user config path', async () => {
  const { userConfigPath } = await import('../src/lib/config.js');
  assert.equal(userConfigPath({ VANTAGE_CONFIG: '/tmp/x.json' }), '/tmp/x.json');
  assert.equal(userConfigPath({ XDG_CONFIG_HOME: '/xdg' }), '/xdg/vantage/default.json');
});
