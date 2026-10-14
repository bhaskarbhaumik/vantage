import assert from 'node:assert/strict';
import { after, before, test } from 'node:test';
import chalk from 'chalk';
import { ASCII_NOCOLOR, FakeBridge, KEYS, NERD, loadRuns, nonAscii, press, renderApp, stripAnsi, wait } from './helpers.js';
import { filterRuns, sortRuns } from '../src/screens/Runs.js';

// Force colour on so that any style that leaks through --no-color would show up as an escape.
let level: typeof chalk.level;
before(() => {
  level = chalk.level;
  chalk.level = 3;
});
after(() => {
  chalk.level = level;
});

const SCREENS = ['home', 'runs', 'doctor', 'backends', 'config', 'export', 'run'] as const;

test('colour mode does emit ANSI escapes (sanity check for the no-color test)', async () => {
  const app = renderApp({ prefs: NERD });
  await wait(80);
  assert.ok((app.lastFrame() ?? '').includes('\u001B['), 'expected ANSI escapes in colour mode');
  app.unmount();
});

for (const screen of SCREENS) {
  test(`--ascii --no-color: ${screen} renders 7-bit text with no ANSI escapes`, async () => {
    const app = renderApp({ prefs: ASCII_NOCOLOR, args: { screen } });
    await wait(80);
    const frame = app.lastFrame() ?? '';
    assert.ok(frame.length > 0);
    assert.ok(!frame.includes('\u001B'), `${screen}: ANSI escape found`);
    assert.deepEqual(nonAscii(frame), [], `${screen}: non-ASCII characters found`);
    app.unmount();
  });
}

test('--ascii --no-color: live dashboard and finished export stay 7-bit', async () => {
  const app = renderApp({ prefs: ASCII_NOCOLOR, args: { screen: 'run', run: { client: 'Example Corp', slug: 'ex-1' } } });
  await wait(60);
  // 18 focusable fields above the Start button.
  await press(app.stdin, ...Array(25).fill(KEYS.down), KEYS.enter);
  await wait(200);
  let frame = app.lastFrame() ?? '';
  assert.match(frame, /Dossier ready/);
  assert.match(frame, /P7R/);
  assert.deepEqual(nonAscii(frame), []);
  assert.ok(!frame.includes('\u001B'));
  // Export the finished dossier straight from the dashboard.
  await press(app.stdin, 'e');
  await press(app.stdin, ...Array(25).fill(KEYS.down), KEYS.enter);
  await wait(200);
  frame = app.lastFrame() ?? '';
  assert.match(frame, /example-2026-10\.pptx/);
  assert.match(frame, /done/);
  assert.deepEqual(nonAscii(frame), []);
  assert.ok(!frame.includes('\u001B'));
  app.unmount();
});

test('nerd mode uses Nerd Font glyphs in the chrome', async () => {
  const app = renderApp({ prefs: { ...NERD, color: false } });
  await wait(80);
  const frame = app.lastFrame() ?? '';
  assert.ok([...frame].some((c) => (c.codePointAt(0) ?? 0) >= 0xf000 && (c.codePointAt(0) ?? 0) <= 0xf2ff));
  assert.ok(!frame.includes('\u001B'));
  app.unmount();
});

test('runs list renders every run with its confidence band and B/M/m', async () => {
  const app = renderApp({ prefs: { ...NERD, color: false }, args: { screen: 'runs' } });
  await wait(80);
  const frame = stripAnsi(app.lastFrame() ?? '');
  for (const slug of ['example-2026-10', 'acme-2026-09', 'globex-2026-08', 'initech-2026-07']) {
    assert.ok(frame.includes(slug), `missing ${slug}`);
  }
  assert.match(frame, /Insufficient/);
  assert.match(frame, /6B\/18M\/30m/);
  assert.match(frame, /unverified/);
  // Newest first by default.
  assert.ok(frame.indexOf('example-2026-10') < frame.indexOf('initech-2026-07'));
  app.unmount();
});

test('runs list: filter, sort and open detail', async () => {
  const bridge = new FakeBridge();
  const app = renderApp({ bridge, prefs: { ...NERD, color: false }, args: { screen: 'runs' } });
  await wait(80);
  await press(app.stdin, '/', 'a', 'c', 'm', 'e', KEYS.enter);
  let frame = app.lastFrame() ?? '';
  assert.ok(frame.includes('acme-2026-09'));
  assert.ok(!frame.includes('initech-2026-07'));
  await press(app.stdin, KEYS.enter);
  frame = app.lastFrame() ?? '';
  assert.match(frame, /BLOCKER/);
  assert.match(frame, /04-market\.md/);
  assert.deepEqual(bridge.calls.at(-1), ['runs', 'show', 'acme-2026-09']);
  await press(app.stdin, KEYS.esc);
  assert.match(app.lastFrame() ?? '', /Runs \(1 of 4\)/);
  app.unmount();
});

test('sortRuns and filterRuns', () => {
  const runs = loadRuns();
  assert.deepEqual(sortRuns(runs, 'eqi', true).map((r) => r.slug)[0], 'initech-2026-07');
  assert.deepEqual(sortRuns(runs, 'confidence', false).map((r) => r.slug)[0], 'globex-2026-08');
  assert.deepEqual(sortRuns(runs, 'slug', false).map((r) => r.slug)[0], 'acme-2026-09');
  assert.deepEqual(filterRuns(runs, 'insufficient').map((r) => r.slug), ['acme-2026-09']);
});

test('global navigation: number keys, tab, help overlay, esc back', async () => {
  const app = renderApp({ prefs: { ...NERD, color: false } });
  await wait(60);
  await press(app.stdin, '6');
  assert.match(app.lastFrame() ?? '', /Doctor - engine 0\.2\.0/);
  await press(app.stdin, KEYS.tab);
  assert.match(app.lastFrame() ?? '', /not ready/);
  await press(app.stdin, '?');
  assert.match(app.lastFrame() ?? '', /Keybindings/);
  await press(app.stdin, KEYS.esc);
  assert.doesNotMatch(app.lastFrame() ?? '', /Keybindings/);
  await press(app.stdin, KEYS.esc);
  assert.match(app.lastFrame() ?? '', /Doctor - engine/);
  app.unmount();
});

test('switching auth to api-key asks for an explicit cost confirmation', async () => {
  const app = renderApp({ prefs: { ...NERD, color: false }, args: { screen: 'run', run: { client: 'Example Corp' } } });
  await wait(60);
  // Fields: client slug common ticker vertical geo asOf cap sheet ctx rel obj backend tier auth
  await press(app.stdin, ...Array(14).fill(KEYS.down), KEYS.right);
  let frame = app.lastFrame() ?? '';
  assert.match(frame, /Billed per token/);
  assert.match(frame, /per-token prices/);
  await press(app.stdin, 'n');
  frame = app.lastFrame() ?? '';
  assert.doesNotMatch(frame, /per-token prices/);
  assert.match(frame, /subscription/);
  await press(app.stdin, KEYS.right, 'y');
  frame = app.lastFrame() ?? '';
  assert.match(frame, /api-key - billed per token/);
  assert.match(frame, /Prompt for key/);
  app.unmount();
});

test('engine failures render an error panel instead of crashing', async () => {
  const bridge = new FakeBridge({ failAll: 'this engine does not support `vantage runs list --json` yet' });
  for (const screen of ['runs', 'doctor', 'backends', 'config'] as const) {
    const app = renderApp({ bridge, prefs: { ...NERD, color: false }, args: { screen } });
    await wait(80);
    const frame = app.lastFrame() ?? '';
    assert.match(frame, /does not support/, `${screen} should show the engine error`);
    app.unmount();
  }
});

test('narrow terminals get the narrow layout', async () => {
  const app = renderApp({ prefs: { ...ASCII_NOCOLOR }, args: { screen: 'runs' }, width: 80 });
  await wait(80);
  const frame = app.lastFrame() ?? '';
  assert.ok(frame.split('\n').every((l) => l.length <= 80), 'no line wider than the terminal');
  assert.doesNotMatch(frame, /Verified Account Navigator/);
  app.unmount();
});
