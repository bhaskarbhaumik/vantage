import assert from 'node:assert/strict';
import { test } from 'node:test';
import { barString } from '../src/components/ui.js';
import { ICONS, type IconName, borderStyle, icon, spinnerType, toAscii } from '../src/lib/icons.js';
import { resolvePrefs } from '../src/lib/theme.js';

const is7bit = (s: string) => [...s].every((c) => (c.codePointAt(0) ?? 0) < 0x80);

test('every icon has nerd, unicode and ascii variants', () => {
  for (const [name, set] of Object.entries(ICONS)) {
    assert.equal(typeof set.nerd, 'string', name);
    assert.equal(typeof set.unicode, 'string', name);
    assert.equal(typeof set.ascii, 'string', name);
    assert.ok(set.nerd.length > 0, `${name} nerd glyph is empty`);
    assert.ok(set.unicode.length > 0, `${name} unicode glyph is empty`);
  }
});

test('ascii icons are 7-bit only', () => {
  for (const name of Object.keys(ICONS) as IconName[]) {
    const g = icon(name, 'ascii');
    assert.ok(is7bit(g), `${name} ascii glyph ${JSON.stringify(g)} is not 7-bit`);
  }
});

test('nerd icons use Nerd Font private-use glyphs for the main set', () => {
  for (const name of ['ok', 'fail', 'warn', 'home', 'config', 'export', 'runs'] as IconName[]) {
    const cp = icon(name, 'nerd').codePointAt(0) ?? 0;
    assert.ok(cp >= 0xe000 && cp <= 0xf8ff, `${name} should be a PUA glyph`);
  }
});

test('spinners, bars and borders fall back to ASCII', () => {
  assert.equal(spinnerType('ascii'), 'line');
  assert.equal(spinnerType('nerd'), 'dots');
  assert.equal(borderStyle('ascii'), 'classic');
  assert.equal(borderStyle('unicode'), 'round');
  const bar = barString(0.5, 12, 'ascii');
  assert.equal(bar, '[#####-----]');
  assert.ok(is7bit(bar));
  assert.ok(!is7bit(barString(0.5, 12, 'unicode')));
});

test('toAscii folds typography and strips everything else to 7-bit', () => {
  assert.equal(toAscii('Vantage™ — §21.8 · café → done…'), 'Vantage(TM) - S21.8 - cafe -> done...');
  assert.ok(is7bit(toAscii('漢字  ✓ ⚠')));
});

test('resolvePrefs: flags beat config, NO_COLOR beats config, --ascii forces ascii icons', () => {
  const ui = { icons: 'unicode', color: 'always', theme: 'light', animations: true };
  let p = resolvePrefs(ui, {}, {}, true);
  assert.deepEqual(p, { icons: 'unicode', color: true, theme: 'light', animations: true });
  p = resolvePrefs(ui, {}, { NO_COLOR: '1' }, true);
  assert.equal(p.color, false);
  p = resolvePrefs(ui, { ascii: true, noColor: true, theme: 'dark', noAnimations: true }, {}, true);
  assert.deepEqual(p, { icons: 'ascii', color: false, theme: 'dark', animations: false });
  p = resolvePrefs(undefined, { icons: 'nerd' }, {}, false);
  assert.equal(p.icons, 'nerd');
  assert.equal(p.color, false, 'auto colour is off when stdout is not a TTY');
});
