# Terminal UI

`vantage-tui` is an interactive terminal UI built with [Ink](https://github.com/vadimdemedes/ink).
It drives the same `vantage` CLI you can script, through its `--json` contracts, so anything the
TUI shows you can also get from the [CLI](cli.md).

## Starting it

```bash
npm ci && npm run build          # once, from the clone: builds tui/dist/
uv run vantage --tui             # through the CLI (or: uv run vantage tui)
node tui/dist/index.js           # directly
scripts/vantage-tui              # the shell launcher (link it onto PATH as vantage-tui)
npm run dev                      # from source, for development
```

The TUI needs an interactive terminal: stdin and stdout must both be a TTY. In scripts, pipes and
CI use `vantage … --json` instead. It needs Node.js 18.19 or newer.

To call the engine, the TUI runs `uv run --quiet --project <repo> vantage`. Set `VANTAGE_ENGINE`
to use another command, for example an installed `vantage`:

```bash
VANTAGE_ENGINE=vantage vantage-tui
```

## Screens

| Key | Screen | What it does |
|---|---|---|
| `1` | Home | Engine and auth summary, quick actions, recent runs |
| `2` | New | The new-dossier form: client, slug, backend, tier, auth, ticker, vertical, the internal-input gates, remediation rounds |
| `3` | Live | The run dashboard: phase strip P0 … P7R … P8, progress, per-agent rows, warnings, the result card and the event log |
| `4` | Runs | Every run under the output dir with tier, Overall Confidence, B/M/m counts, EQI; `enter` opens a run's detail view |
| `5` | Export | The export wizard: dossier, formats, depth, HTML mode, authoring, output dir, brand, classification, helpers |
| `6` | Doctor | `vantage doctor`, grouped, with a problems-only filter |
| `7` | Backends | Readiness of each backend; `enter` starts a new dossier on it |
| `8` | Config | Browse the effective configuration and edit values (through `vantage config set`) |

A run or an export keeps going when you switch screens. Quitting while one is active asks first,
and stops the engine.

### Live run

```text
@ Vantage                                                             [* subscription]  engine 0.2.0
1:~ Home  2:+ New  3:* Live  4:= Runs  5:v Export  6:+ Doctor  7:# Backends  8:% Config
+--------------------------------------------------------------------------------------------------+
| * Example Corp  - example-2026-10                                                        t 00:00 |
| backend workflow  tier FULL_ANNEX  [* subscription]  status done                                 |
|                                                                                                  |
| v P0 - v P1 - v P2 - v P3 - v P4 - v P5 - v P6 - v P7 - v P7R - v P8                             |
| [######################################] 100%                                                    |
| + 13/14 agents ok  1 failed  $ 405k in / 51k out                                                 |
+--------------------------------------------------------------------------------------------------+
+-----------------------------------------------------------------++-------------------------------+
| + Agents (14)                                                   || ! Warnings (3)                |
| x financials                                 00:22      0       || X financials: tool budget exh.|
| v appendices                                 00:07   3.3k       || ! no return from: financials .|
| v verification-r1                            00:07   6.4k       || ! stopped on budget (not dimi.|
| v market-r1                                  00:07   2.1k       ||                               |
| v remediation-router-r1                      00:07    900       ||                               |
| v verification                               00:07   7.0k       ||                               |
| v exec-brief                                 00:07   2.5k       ||                               |
| v opportunity                                00:07   3.9k       ||                               |
| v contradiction                              00:07   2.0k       ||                               |
| v competition                                00:07   4.8k       ||                               |
| +4 more finished agents                                         ||                               |
+-----------------------------------------------------------------++-------------------------------+
+--------------------------------------------------------------------------------------------------+
| # Dossier ready                                                                                  |
| agents      11/12 ok                                                                             |
| verify      PASS WITH DISCLOSURES Adequate EQI 71  1B/5M/12m                                     |
| stopped on budget (not diminishing returns): supply chain                                        |
| tokens      405k in / 51k out                                                                    |
| dossier     /tmp/vantage/run/example-2026-10/example-2026-10-vantage.md                          |
+--------------------------------------------------------------------------------------------------+
p pause - l log - / filter - c cancel - q quit - ? help - esc back
```

Agents that ran in a remediation round carry an `-r1`/`-r2` suffix. An agent that did not return
is named, never silently dropped. When the result is `Insufficient`, the result card says not to
present the dossier.

### Runs

```text
+--------------------------------------------------------------------------------------------------+
| = Runs (4)                                                                    sort modified desc |
|     slug                client               tier       confidence   B/M/m      EQI  modified    |
| > # example-2026-10     Example Corp         FULL_ANNEX Adequate     1B/5M/12m  71   2026-10-14  |
|   # acme-2026-09        Acme Industries      STANDARD   Insufficient 6B/18M/30m 38   2026-09-04  |
|   o globex-2026-08      -                    -          unverified   -          -    2026-08-12  |
|   # initech-2026-07     Initech              EXECUTIVE  Strong       0B/1M/4m   88   2026-07-20  |
+--------------------------------------------------------------------------------------------------+
enter open - s sort - / filter - e export - o open dir - c copy - ? help - esc back - q quit
```

The frames on this page were rendered with `ink-testing-library` from the recorded test fixtures
in `--ascii --no-color` mode (sample data).

## Keybindings

Press `?` on any screen for the keys that apply there.

### Everywhere

| Key | Action |
|---|---|
| `tab` / `shift-tab` | Next / previous screen |
| `1`–`8` | Jump to a screen |
| `esc` | Back, or cancel an edit |
| `?` | Toggle help |
| `q` | Quit (asks first while a run or export is active) |
| `ctrl-c` | Quit now (stops the engine) |

### Per screen

| Screen | Keys |
|---|---|
| Home | `up`/`down` move · `enter` open the highlighted action |
| New | `up`/`down` move between fields · `enter` edit text, toggle, or start · `left`/`right`/`space` cycle a choice · `backspace` clear a text field · `esc` cancel an edit |
| Live | `p` pause/resume log autoscroll · `l` show/hide the log · `/` filter the log · `up`/`down`/`pgup`/`pgdn` scroll the log · `c` cancel the run · `e` export the finished dossier · `r` open the finished run |
| Runs | `up`/`down` move · `enter` open run detail · `s`/`S` cycle sort key / reverse order · `/` filter · `e` export the selected dossier · `o` open the run folder · `c` copy the dossier path · `r` reload |
| Run detail | `up`/`down` scroll sections · `e` export · `o` open the folder · `c` copy the dossier path · `r` reload · `esc` back to the list |
| Export | `up`/`down` move · `left`/`right` cycle a choice or pick a format · `space` toggle · `enter` edit text or start · `x` stop a running export · `n` new export after one finishes · `o`/`c` open/copy the output folder |
| Doctor | `r` re-run the checks · `f` show only warnings and failures |
| Backends | `up`/`down` move · `enter` new dossier on this backend · `r` reload |
| Config | `up`/`down` move · `right`/`enter` expand a section · `left` collapse · `enter`/`e` edit a value · `space` toggle a boolean · `esc` cancel an edit · `r` reload |

## Deep links

The first argument names a screen; the rest prefill it.

```bash
vantage-tui run --client "Example Corp" --tier EXECUTIVE     # the form, prefilled
vantage-tui run "Example Corp"                               # same: a bare name is the client
vantage-tui runs                                             # the runs browser
vantage-tui runs example-2026-10                             # one run's detail view
vantage-tui export example-2026-10 --formats pptx,html --depth exec
vantage-tui doctor
```

Screens: `home` (default), `run`, `live`, `runs`, `export`, `doctor`, `backends`, `config`.

| Prefill | Flags |
|---|---|
| New dossier | `--client --slug --backend --tier --as-of --ticker --vertical --geography --common-name --capability-pack --input-sheet --account-context --relationship --objectives --auth subscription\|api-key --ask-key --remediation-rounds 0\|1\|2` |
| Export | `--formats pptx,docx,pdf,html --depth exec\|standard\|full --site-mode microsite\|deck --authoring deterministic\|agents --out-dir DIR --classification TEXT --brand DOMAIN --client-logo \| --no-client-logo` |

Through the CLI: `uv run vantage --tui runs example-2026-10`. `vantage-tui --help` prints the full
usage.

## Icons, colour, theme and motion

| Flag | Config key | Values |
|---|---|---|
| `--icons` | `ui.icons` | `nerd` (default) · `unicode` · `ascii` |
| `--ascii` | `ui.icons` | Same as `--icons ascii`: 7-bit output only, including borders and spinners |
| `--no-color` | `ui.color` | `auto` (default) · `always` · `never`. `--no-color` means `never` |
| `--theme` | `ui.theme` | `dark` (default) · `light` |
| `--no-animations` | `ui.animations` | Static spinners, no live redraws |

The TUI resolves them in this order, lowest to highest: built-in defaults, the `ui` section of the
shipped and user config files, `NO_COLOR` (any non-empty value turns colour off), then flags.
With `ui.color` set to `auto`, colour is on only when stdout is a terminal.

- **`nerd`** uses Nerd Font glyphs (Font Awesome range). Pick it when your terminal font is a
  patched Nerd Font.
- **`unicode`** uses plain symbols (✓ ✗ ▲ •) that render in any modern font.
- **`ascii`** is for CI logs, serial consoles, screen readers and fonts with poor coverage. It
  pairs well with `--no-animations`.

Persist a choice with `uv run vantage config set ui.icons unicode` or
`uv run vantage config set ui.theme light`. Layouts narrower than 100 columns switch to a compact
arrangement.

### Nerd Fonts

If you see boxes or question marks instead of icons, your terminal font lacks the glyphs.

1. Install a patched font from [nerdfonts.com](https://www.nerdfonts.com/), for example
   *JetBrainsMono Nerd Font* (macOS: `brew install --cask font-jetbrains-mono-nerd-font`).
2. Select it as the terminal's font (iTerm2: Profiles → Text; Terminal.app: Settings → Profiles →
   Font; Windows Terminal: profile → Appearance; VS Code: `terminal.integrated.fontFamily`).
3. Re-open the terminal. If you cannot change the font, use `--icons unicode`.
