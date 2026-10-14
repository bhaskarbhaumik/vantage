// One table maps every semantic icon to its Nerd Font glyph, a plain Unicode symbol and a 7-bit
// ASCII fallback. Nothing else in the TUI hard-codes a decorative glyph.

export type IconMode = 'nerd' | 'unicode' | 'ascii';

export interface IconSet {
  nerd: string;
  unicode: string;
  ascii: string;
}

// Nerd Font glyphs are taken from the Font Awesome range (U+F000-U+F2E0), which every Nerd Font
// release ships, so the default works on v2 and v3 patched fonts alike.
export const ICONS = {
  logo: { nerd: '', unicode: '◎', ascii: '@' },
  tm: { nerd: '™', unicode: '™', ascii: '' },
  home: { nerd: '', unicode: '⌂', ascii: '~' },
  newRun: { nerd: '', unicode: '+', ascii: '+' },
  live: { nerd: '', unicode: '◉', ascii: '*' },
  runs: { nerd: '', unicode: '≡', ascii: '=' },
  export: { nerd: '', unicode: '⇩', ascii: 'v' },
  doctor: { nerd: '', unicode: '✚', ascii: '+' },
  backends: { nerd: '', unicode: '▦', ascii: '#' },
  config: { nerd: '', unicode: '⚙', ascii: '%' },
  help: { nerd: '', unicode: '?', ascii: '?' },
  ok: { nerd: '', unicode: '✓', ascii: 'v' },
  fail: { nerd: '', unicode: '✗', ascii: 'x' },
  warn: { nerd: '', unicode: '⚠', ascii: '!' },
  info: { nerd: '', unicode: 'ℹ', ascii: 'i' },
  error: { nerd: '', unicode: '✖', ascii: 'X' },
  pending: { nerd: '', unicode: '○', ascii: 'o' },
  running: { nerd: '', unicode: '◉', ascii: '*' },
  done: { nerd: '', unicode: '●', ascii: '#' },
  skipped: { nerd: '', unicode: '⊘', ascii: '-' },
  paused: { nerd: '', unicode: '⏸', ascii: '=' },
  pointer: { nerd: '', unicode: '❯', ascii: '>' },
  bullet: { nerd: '', unicode: '•', ascii: '*' },
  dot: { nerd: '·', unicode: '·', ascii: '-' },
  sep: { nerd: '│', unicode: '│', ascii: '|' },
  arrow: { nerd: '', unicode: '→', ascii: '->' },
  link: { nerd: '─', unicode: '─', ascii: '-' },
  checkOn: { nerd: '', unicode: '☑', ascii: '[x]' },
  checkOff: { nerd: '', unicode: '☐', ascii: '[ ]' },
  toggleOn: { nerd: '', unicode: '◉', ascii: '(*)' },
  toggleOff: { nerd: '', unicode: '○', ascii: '( )' },
  cycle: { nerd: '', unicode: '⇅', ascii: '<>' },
  edit: { nerd: '', unicode: '✎', ascii: '/' },
  search: { nerd: '', unicode: '⌕', ascii: '/' },
  filter: { nerd: '', unicode: '⧩', ascii: '/' },
  sort: { nerd: '', unicode: '⇅', ascii: '^' },
  clock: { nerd: '', unicode: '◷', ascii: 't' },
  tokens: { nerd: '', unicode: '⚡', ascii: '$' },
  agent: { nerd: '', unicode: '◆', ascii: '+' },
  phase: { nerd: '', unicode: '◇', ascii: '>' },
  remediation: { nerd: '', unicode: '↻', ascii: 'R' },
  log: { nerd: '', unicode: '▤', ascii: '>' },
  folder: { nerd: '', unicode: '▸', ascii: '>' },
  file: { nerd: '', unicode: '▪', ascii: '-' },
  copy: { nerd: '', unicode: '⧉', ascii: 'c' },
  open: { nerd: '', unicode: '↗', ascii: 'o' },
  key: { nerd: '', unicode: '⚿', ascii: 'k' },
  subscription: { nerd: '', unicode: '●', ascii: '*' },
  billing: { nerd: '', unicode: '$', ascii: '$' },
  client: { nerd: '', unicode: '▣', ascii: '#' },
  calendar: { nerd: '', unicode: '▦', ascii: 'd' },
  shield: { nerd: '', unicode: '◈', ascii: 'V' },
  chart: { nerd: '', unicode: '▥', ascii: '%' },
  tree: { nerd: '', unicode: '┬', ascii: '+' },
  expand: { nerd: '', unicode: '▾', ascii: 'v' },
  collapse: { nerd: '', unicode: '▸', ascii: '>' },
  leaf: { nerd: '', unicode: '─', ascii: '-' },
  pptx: { nerd: '', unicode: '▭', ascii: 'P' },
  docx: { nerd: '', unicode: '▤', ascii: 'W' },
  pdf: { nerd: '', unicode: '▧', ascii: 'F' },
  html: { nerd: '', unicode: '◫', ascii: 'H' },
  manifest: { nerd: '', unicode: '☰', ascii: 'M' },
  rocket: { nerd: '', unicode: '▶', ascii: '>' },
  keyboard: { nerd: '', unicode: '⌨', ascii: 'K' },
  plug: { nerd: '', unicode: '⚡', ascii: '~' },
  brand: { nerd: '', unicode: '✦', ascii: '*' },
  globe: { nerd: '', unicode: '◍', ascii: '@' },
  hourglass: { nerd: '', unicode: '⧗', ascii: '.' },
} as const satisfies Record<string, IconSet>;

export type IconName = keyof typeof ICONS;

export function icon(name: IconName, mode: IconMode): string {
  return ICONS[name][mode];
}

export function isIconMode(v: unknown): v is IconMode {
  return v === 'nerd' || v === 'unicode' || v === 'ascii';
}

// Frames for the spinner and glyphs for bars and borders, per mode.
export function spinnerType(mode: IconMode): 'dots' | 'line' {
  return mode === 'ascii' ? 'line' : 'dots';
}

export function barChars(mode: IconMode): { full: string; empty: string; open: string; close: string } {
  return mode === 'ascii'
    ? { full: '#', empty: '-', open: '[', close: ']' }
    : { full: '█', empty: '░', open: '', close: '' };
}

export function borderStyle(mode: IconMode): 'classic' | 'round' {
  return mode === 'ascii' ? 'classic' : 'round';
}

const ASCII_MAP: Record<string, string> = {
  '—': '-', '–': '-', '−': '-', '·': '-', '•': '*', '…': '...', '→': '->', '←': '<-',
  '↑': '^', '↓': 'v', '‘': "'", '’': "'", '“': '"', '”': '"', '§': 'S', '™': '(TM)',
  '©': '(c)', '®': '(R)', '×': 'x', '≥': '>=', '≤': '<=', '≠': '!=', '✓': 'v', '✗': 'x',
  '⚠': '!', '│': '|', '─': '-', ' ': ' ',
};

// Fold any string to 7-bit ASCII: known typographic characters are transliterated, accents are
// stripped, anything else becomes '?'. Used for every rendered string in --ascii mode.
export function toAscii(s: string): string {
  let out = '';
  for (const ch of s) {
    const code = ch.codePointAt(0) ?? 0;
    if (code < 0x80) {
      out += ch;
      continue;
    }
    const mapped = ASCII_MAP[ch];
    if (mapped !== undefined) {
      out += mapped;
      continue;
    }
    const base = ch.normalize('NFD').replace(/[̀-ͯ]/g, '');
    out += base.length && (base.codePointAt(0) ?? 0x80) < 0x80 ? base : '?';
  }
  return out;
}
