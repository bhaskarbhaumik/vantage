// Presentation preferences (icons, colour, theme, animation) and the colour palettes.
import { type IconMode, isIconMode } from './icons.js';

export type ThemeName = 'dark' | 'light';
export type ColorMode = 'auto' | 'always' | 'never';

export interface UiPrefs {
  icons: IconMode;
  color: boolean;
  theme: ThemeName;
  animations: boolean;
}

export interface Palette {
  accent: string;
  accent2: string;
  ok: string;
  warn: string;
  err: string;
  info: string;
  muted: string;
  text: string;
  selectFg: string;
  selectBg: string;
}

export const PALETTES: Record<ThemeName, Palette> = {
  dark: {
    accent: '#5FA8FF',
    accent2: '#B48EFF',
    ok: '#4ADE80',
    warn: '#FACC15',
    err: '#F87171',
    info: '#38BDF8',
    muted: '#8B95A5',
    text: '#E5E9F0',
    selectFg: '#0B1220',
    selectBg: '#5FA8FF',
  },
  light: {
    accent: '#1F5FBF',
    accent2: '#6E40C9',
    ok: '#1A7F37',
    warn: '#9A6700',
    err: '#CF222E',
    info: '#0969DA',
    muted: '#57606A',
    text: '#1F2328',
    selectFg: '#FFFFFF',
    selectBg: '#1F5FBF',
  },
};

export type Tone = keyof Omit<Palette, 'selectFg' | 'selectBg'>;

export interface UiSection {
  icons?: unknown;
  color?: unknown;
  theme?: unknown;
  animations?: unknown;
}

export interface PrefFlags {
  ascii?: boolean;
  icons?: string;
  noColor?: boolean;
  color?: boolean;
  theme?: string;
  noAnimations?: boolean;
}

// Precedence: built-in defaults < config `ui` section < NO_COLOR env < command-line flags.
export function resolvePrefs(
  ui: UiSection | undefined,
  flags: PrefFlags,
  env: NodeJS.ProcessEnv,
  stdoutIsTTY: boolean,
): UiPrefs {
  let icons: IconMode = isIconMode(ui?.icons) ? ui.icons : 'nerd';
  if (isIconMode(flags.icons)) icons = flags.icons;
  if (flags.ascii) icons = 'ascii';

  const cfgColor: ColorMode =
    ui?.color === 'always' || ui?.color === 'never' || ui?.color === 'auto' ? ui.color : 'auto';
  let color = cfgColor === 'always' ? true : cfgColor === 'never' ? false : stdoutIsTTY;
  if (env.NO_COLOR !== undefined && env.NO_COLOR !== '') color = false;
  if (flags.color) color = true;
  if (flags.noColor) color = false;

  let theme: ThemeName = ui?.theme === 'light' ? 'light' : 'dark';
  if (flags.theme === 'light' || flags.theme === 'dark') theme = flags.theme;

  let animations = typeof ui?.animations === 'boolean' ? ui.animations : true;
  if (flags.noAnimations) animations = false;

  return { icons, color, theme, animations };
}

export const DEFAULT_PREFS: UiPrefs = { icons: 'nerd', color: true, theme: 'dark', animations: true };

// Confidence bands as the verifier writes them, mapped to a tone.
export function bandTone(band: string | null | undefined): Tone {
  const b = (band ?? '').toLowerCase();
  if (!b) return 'muted';
  if (b.startsWith('insufficient')) return 'err';
  if (b.startsWith('thin') || b.startsWith('low')) return 'warn';
  if (b.startsWith('moderate') || b.startsWith('medium') || b.startsWith('adequate')) return 'info';
  return 'ok';
}
