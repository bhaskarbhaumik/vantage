// Command line of the TUI itself: `vantage-tui [screen] [positional] [--flags]`.
import type { PrefFlags } from './theme.js';

export const SCREENS = [
  'home', 'run', 'live', 'runs', 'export', 'doctor', 'backends', 'config', 'help',
] as const;
export type ScreenName = (typeof SCREENS)[number];

const ALIASES: Record<string, ScreenName> = {
  new: 'run',
  generate: 'run',
  dashboard: 'home',
  list: 'runs',
  settings: 'config',
};

// Flags that never take a value.
const BOOLEAN_FLAGS = new Set([
  'help', 'version', 'ascii', 'no-color', 'color', 'no-animations', 'ask-key', 'client-logo',
  'no-client-logo', 'quiet', 'verbose',
]);

const SHORT: Record<string, string> = { h: 'help', v: 'version', V: 'version' };

export interface RunPrefill {
  client?: string;
  slug?: string;
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
  remediationRounds?: string;
}

export interface ExportPrefill {
  dossier?: string;
  formats?: string[];
  depth?: string;
  siteMode?: string;
  authoring?: string;
  outDir?: string;
  classification?: string;
  brand?: string;
  clientLogo?: boolean;
}

export interface CliArgs {
  screen: ScreenName;
  positional: string[];
  flags: Record<string, string | boolean>;
  prefs: PrefFlags;
  run: RunPrefill;
  exportOpts: ExportPrefill;
  slug?: string;
  help: boolean;
  version: boolean;
  errors: string[];
}

function str(v: string | boolean | undefined): string | undefined {
  return typeof v === 'string' && v.length ? v : undefined;
}

export function parseArgs(argv: string[]): CliArgs {
  const flags: Record<string, string | boolean> = {};
  const positional: string[] = [];
  const errors: string[] = [];

  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--') {
      positional.push(...argv.slice(i + 1));
      break;
    }
    if (a.startsWith('--')) {
      const body = a.slice(2);
      const eq = body.indexOf('=');
      if (eq >= 0) {
        flags[body.slice(0, eq)] = body.slice(eq + 1);
        continue;
      }
      if (BOOLEAN_FLAGS.has(body)) {
        flags[body] = true;
        continue;
      }
      const next = argv[i + 1];
      if (next !== undefined && !next.startsWith('--')) {
        flags[body] = next;
        i++;
      } else {
        errors.push(`--${body} needs a value`);
      }
      continue;
    }
    if (a.length === 2 && a.startsWith('-') && SHORT[a[1]]) {
      flags[SHORT[a[1]]] = true;
      continue;
    }
    positional.push(a);
  }

  let screen: ScreenName = 'home';
  if (positional.length) {
    const head = positional[0].toLowerCase();
    const resolved = (SCREENS as readonly string[]).includes(head)
      ? (head as ScreenName)
      : ALIASES[head];
    if (resolved) {
      screen = resolved;
      positional.shift();
    } else {
      errors.push(`unknown screen "${positional[0]}" (expected one of: ${SCREENS.join(', ')})`);
    }
  }

  const prefs: PrefFlags = {
    ascii: flags.ascii === true,
    icons: str(flags.icons),
    noColor: flags['no-color'] === true,
    color: flags.color === true,
    theme: str(flags.theme),
    noAnimations: flags['no-animations'] === true,
  };
  if (prefs.icons && !['nerd', 'unicode', 'ascii'].includes(prefs.icons)) {
    errors.push(`--icons must be nerd, unicode or ascii (got "${prefs.icons}")`);
  }
  if (prefs.theme && !['dark', 'light'].includes(prefs.theme)) {
    errors.push(`--theme must be dark or light (got "${prefs.theme}")`);
  }

  const run: RunPrefill = {
    client: str(flags.client),
    slug: str(flags.slug),
    backend: str(flags.backend),
    tier: str(flags.tier)?.toUpperCase(),
    asOf: str(flags['as-of']),
    ticker: str(flags.ticker),
    vertical: str(flags.vertical),
    geography: str(flags.geography),
    commonName: str(flags['common-name']),
    capabilityPack: str(flags['capability-pack'])?.toUpperCase(),
    inputSheet: str(flags['input-sheet'])?.toUpperCase(),
    accountContext: str(flags['account-context']),
    relationship: str(flags.relationship),
    objectives: str(flags.objectives),
    authMode: str(flags.auth),
    askKey: flags['ask-key'] === true ? true : undefined,
    remediationRounds: str(flags['remediation-rounds']),
  };
  if (run.client === undefined && screen === 'run' && positional.length) run.client = positional[0];

  const formats = str(flags.formats) ?? str(flags.format);
  const exportOpts: ExportPrefill = {
    dossier: screen === 'export' ? positional[0] : undefined,
    formats: formats ? formats.split(',').map((f) => f.trim().toLowerCase()).filter(Boolean) : undefined,
    depth: str(flags.depth),
    siteMode: str(flags['site-mode']),
    authoring: str(flags.authoring),
    outDir: str(flags['out-dir']),
    classification: str(flags.classification),
    brand: str(flags.brand),
    clientLogo: flags['no-client-logo'] === true ? false : flags['client-logo'] === true ? true : undefined,
  };

  const slug = screen === 'runs' ? positional[0] ?? str(flags.slug) : undefined;

  return {
    screen,
    positional,
    flags,
    prefs,
    run,
    exportOpts,
    slug,
    help: flags.help === true || screen === 'help',
    version: flags.version === true,
    errors,
  };
}

export const HELP_TEXT = `vantage-tui — interactive terminal UI for the Vantage research engine

Usage
  vantage-tui [screen] [args] [flags]

Screens
  home                      dashboard (default)
  run    [--client NAME …]  new dossier form, prefilled from flags
  live                      live run dashboard
  runs   [SLUG]             runs browser, or one run's detail view
  export [SLUG|PATH] […]    export wizard for a finished dossier
  doctor                    environment and backend checks
  backends                  execution backends and readiness
  config                    browse and edit the effective configuration

Run prefill flags
  --client --slug --backend --tier --as-of --ticker --vertical --geography
  --common-name --capability-pack --input-sheet --account-context
  --relationship --objectives --auth subscription|api-key --ask-key
  --remediation-rounds 0|1|2

Export prefill flags
  --formats pptx,docx,pdf,html --depth exec|standard|full
  --site-mode microsite|deck --authoring deterministic|agents --out-dir DIR
  --classification TEXT --brand DOMAIN --client-logo | --no-client-logo

Presentation
  --ascii                   7-bit output only (= --icons ascii)
  --icons nerd|unicode|ascii
  --no-color                no ANSI colour (NO_COLOR is honoured too)
  --theme dark|light
  --no-animations           static spinners
  -h, --help                this help
  -v, --version             print the version

Environment
  VANTAGE_ENGINE            command used to call the engine
                            (default: uv run --project <repo> vantage)

The TUI needs an interactive terminal. For scripts and CI use \`vantage\` directly.
`;
