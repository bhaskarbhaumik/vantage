# CLI guide

`vantage` is the command-line interface to the engine. `vantage-engine` is the same program under
a second name, kept for scripts and the container entry point. This page explains how the CLI
behaves; the [CLI reference](reference/cli.md) lists every command and option and is generated
from the code.

```bash
uv run vantage --help          # from the clone; or activate .venv and drop "uv run"
uv run vantage run --help
uv run vantage options         # every option, including one flag per config key
```

## Three kinds of option

| Kind | Example | Where it goes |
|---|---|---|
| **Command options** | `run --client`, `export --format`, `runs list --limit` | After their command |
| **Global options** | `--backend`, `--tier`, `--auth`, `--set`, `--ascii`, `--quiet` | Before *or* after the command |
| **Config flags** | `--engine-max-concurrency 12`, `--export-helpers-charts plotly` | Before or after the command; hidden from `--help` |

Global options and config flags are injected into every command, so these are equivalent:

```bash
uv run vantage --tier STANDARD run --client "Example Corp"
uv run vantage run --client "Example Corp" --tier STANDARD
```

`--tui` and `--version` belong to the root command only. A command's own option wins a clash
with a global short alias: on `vantage deploy`, `-t` is `--target`, so spell `--tier` in full there.

### Config flags

Every leaf of the configuration model is a flag named after its dotted key:
`engine.max_concurrency` → `--engine-max-concurrency`, `export.helpers.diagrams` →
`--export-helpers-diagrams`. Booleans come as pairs (`--export-client-logo` /
`--no-export-client-logo`), lists are repeatable, and the literal `null` clears an optional value
(`--engine-harness-dir null`). They are hidden from `--help` to keep it readable;
`uv run vantage options --filter export` lists them, and shell completion offers them.

### `--set` and `--role-model`

`--set dotted.key=value` reaches any key, including the open-ended maps that have no generated
flag. The value is parsed as JSON when it can be (`8`, `true`, `null`, `["pptx","html"]`) and
used as a string otherwise. Unknown keys are rejected with a suggestion.

```bash
uv run vantage --set engine.max_concurrency=12 config get engine.max_concurrency    # 12
uv run vantage --set 'export.formats=["pptx","html"]' export example-2026-10
```

`--role-model agent=tier` routes one agent to a model tier (`synthesis`, `research` or `cheap`)
for this invocation. It writes `role_model_map.<agent>`:

```bash
uv run vantage run --client "Example Corp" --role-model financials=synthesis
```

Both are repeatable.

## Precedence

Lowest to highest:

1. The shipped defaults, `config/default.json`.
2. The user config, `~/.config/vantage/default.json` (or the file named by `--config` or
   `VANTAGE_CONFIG`; `XDG_CONFIG_HOME` moves the default directory).
3. Environment variables: the short names `VANTAGE_BACKEND`, `VANTAGE_TIER`,
   `VANTAGE_OUTPUT_DIR`, `VANTAGE_HARNESS_DIR`, `VANTAGE_AUTH_MODE`, then the generated
   `VANTAGE_<DOTTED_KEY>` name of every config flag (`VANTAGE_ENGINE_MAX_CONCURRENCY`,
   `VANTAGE_EXPORT_DEPTH`, …). When both spellings are set, the generated one wins.
4. Command-line flags, applied in the order given, so the last one wins.

```bash
VANTAGE_ENGINE_TIER=EXECUTIVE uv run vantage config get engine.tier                  # EXECUTIVE
VANTAGE_ENGINE_TIER=EXECUTIVE uv run vantage config get engine.tier --tier STANDARD  # STANDARD
```

`uv run vantage config show` prints the merged result. Flags never touch the user file; use
`vantage config set` to persist a value ([Configuration](configuration.md)).

## Output, JSON mode and piping

Human output (tables, progress, warnings) goes to **stderr**. Stdout carries only values meant to
be piped: JSON with `--json`, a path from `vantage runs path`, a value from `vantage config get`.

| Command | `--json` writes to stdout |
|---|---|
| `run`, `generate` | One `RunEvent` per line while the run progresses, then `{"result": {...}}` |
| `export` | `RunEvent` lines (`stage_start`/`stage_done` for `ingest`, `plan`, `assets`, `charts`, `render:pptx` …, `artifact`, `run_warning`), then `{"result": {...}}` |
| `runs list` | `{"runs": [{"slug", "run_dir", "dossier", "client", "as_of", "tier", "mtime", "verification", "exports"}]}` |
| `runs show <slug>` | One run object as above, plus `"sections"` |
| `doctor` | `{"version", "checks": [{"group", "name", "status", "detail"}]}` with status `ok`, `warn` or `fail` |
| `backends` | `{"default", "backends": [{"name", "ready", "issues"}]}` |
| `auth status` | `{"mode", "subscription", "profiles", "model_pin_warning"}` |
| `config show` | The effective configuration, compact |
| `config get <key>` | The value as JSON (without `--json`, strings print raw) |
| `options` | `{"options": [...]}`: every global option and config flag with type, default, env and description |
| `version` | `{"version", "harness", "config", "python"}` |

`run --dry-run` prints the resolved job, backend, run directory, harness directory and full
configuration as JSON and runs nothing. It is the quickest way to see what a combination of
flags, environment and config files resolves to.

```bash
uv run vantage runs list --json | jq -r '.runs[] | select(.verification.overall_confidence == "Insufficient") | .slug'
uv run vantage doctor --json | jq '.checks[] | select(.status != "ok")'
```

## Presentation

| Option | Effect |
|---|---|
| `--icons nerd\|unicode\|ascii` | Icon set. `nerd` (the default) needs a [Nerd Font](tui.md#nerd-fonts) |
| `--ascii` | Same as `--icons ascii` |
| `--no-color` | No colour. `NO_COLOR` in the environment is honoured whenever `ui.color` is `auto` |
| `--theme dark\|light` | Colour theme |
| `--no-animations` | No spinners or live redraws |
| `--quiet`, `-q` | Only warnings, errors and the final result |
| `--verbose`, `-v` | Extra detail: tool calls, resolved paths |

The same `ui` settings drive the [terminal UI](tui.md).

## Exit codes

| Code | Meaning |
|---|---|
| `0` | Success |
| `1` | The command ran but did not produce its result: no dossier, no export artifacts, a missing run, `config validate` on an invalid file, a declined `runs rm` |
| `2` | Usage, configuration or startup error: a bad flag or value, an unknown config key, an invalid configuration, a backend that cannot start |

`vantage-tui` exits `2` on bad arguments and `1` when it is not attached to a terminal.

## Launching the TUI

`vantage --tui [args]` and `vantage tui [args]` replace the CLI process with the terminal UI. They
prefer `<repo>/tui/dist/index.js` under `node`, then a `vantage-tui` on PATH. Arguments after the
flag go to the TUI (`vantage --tui runs example-2026-10`). Presentation options given to the CLI
(`--ascii`, `--icons`, `--no-color`, `--theme`, `--no-animations`) are forwarded as TUI flags;
other config overrides are exported as their `VANTAGE_*` variables so the engine processes the TUI
starts see the same configuration.

## Recipes

```bash
# A fast read on the API backend, billed per token, prompting for the key
uv run vantage run --client "Example Corp" --tier EXECUTIVE --backend api --auth api-key --ask-key

# Attach the internal inputs that unlock gated fields
uv run vantage run --client "Example Corp" --capability-pack ATTACHED --input-sheet ATTACHED

# Two owner-remediation rounds instead of one (workflow backend)
uv run vantage run --client "Example Corp" --remediation-rounds 2

# Runs somewhere else, for this invocation only
uv run vantage --output-dir ~/dossiers runs list

# Persist defaults
uv run vantage config set engine.tier STANDARD
uv run vantage config set export.brand example.org

# Export just the executive deck, themed, and open the folder
uv run vantage export example-2026-10 -f pptx --depth exec --brand example.org --open

# Housekeeping
uv run vantage runs path example-2026-10 --dossier
uv run vantage runs rm example-2026-10 --yes
```
