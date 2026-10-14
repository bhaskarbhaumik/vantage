# Troubleshooting

Start with `uv run vantage doctor`. It checks the engine, the user config against the current
agent roster, auth, research-tool variables, every backend, the export dependencies and helpers,
and the TUI, and says what to do about each warning. `uv run vantage doctor --json` gives the same
for scripts.

## Install and launch

| Symptom | Cause | Fix |
|---|---|---|
| `vantage: command not found` | The console script lives in `.venv/` | `uv run vantage …`, or `source .venv/bin/activate` |
| `cannot start the TUI: the TUI is not built …` | `tui/dist/` is missing | `npm ci && npm run build` |
| `cannot start the TUI: Node.js 18+ is not on PATH …` | No `node` | Install Node.js 18.19 or newer |
| `vantage-tui needs an interactive terminal` | stdin or stdout is not a TTY (pipe, CI, IDE task) | Use `vantage … --json` instead |
| `engine command not found: uv …` in the TUI | The TUI calls `uv run --project <repo> vantage` | Install uv, or set `VANTAGE_ENGINE=vantage` |
| Boxes or `?` instead of icons | The terminal font has no Nerd Font glyphs | Install a Nerd Font, or `--icons unicode` / `--ascii` ([TUI](tui.md#nerd-fonts)) |
| Extras disappeared after `uv sync --extra X` | `uv sync` matches exactly the extras you list | List them together: `uv sync --extra dev --extra langgraph` |
| `crewai installed but not importable` | `chromadb` imports `pydantic.v1`, broken on Python 3.14 | Use Python 3.13 or earlier for crewai, or `langgraph` / `api` |

## Running a dossier

| Symptom | Cause | Fix |
|---|---|---|
| `Claude Code CLI 'claude' not found` | Not installed or not on PATH | Install Claude Code, or set `CLAUDE_CLI=/full/path/to/claude` |
| Workflow finished but no dossier was produced | The Workflow tool was not opted into, or the Claude login lapsed | Run `claude` interactively, accept the Workflow opt-in, re-run |
| `backend 'api' … cannot use the Claude subscription` | Expected in subscription mode | Use `--backend workflow`, or opt into `--auth api-key` ([Auth](auth.md)) |
| `auth mode is 'api-key' but the workflow backend always runs on the Claude Code CLI's own credentials` | `workflow` ignores API keys | Use `--backend api` to spend the key, or drop `--auth api-key` |
| `ANTHROPIC_API_KEY is not set …` | `--auth api-key` without the key | Export it, add `--ask-key`, or drop `--auth api-key` |
| `--ask-key ignored: subscription mode reads no API key` | `--ask-key` without `--auth api-key` | Add `--auth api-key` if you meant to pay per token |
| `--remediation-rounds applies to the workflow backend only` | P7R is implemented by `workflow` | Expected on other backends |
| `--slug must be one path component …` | A slash or an unusual character in the slug | Letters, digits, `.`, `_`, `-` only |
| `doctor`: config drift, `max_concurrency is 8 but Wave A launches 10`, legacy `output_dir`, unknown `role_model_map` agents | A user config from an older version | `uv run vantage config migrate --dry-run`, then without `--dry-run` |
| `invalid configuration` with a key path | A value fails validation | `uv run vantage config validate`, then `config set` / `config unset` the key |
| Run stops at P0 with an entity ambiguity | Two plausible companies | Add `--ticker` or a fuller legal name. Do not push past it |
| Many sections read "no evidence found" | Thin disclosure, or a light jurisdiction | Check §21.12: `budget` means re-run with more; `not_applicable` means the adapter has no such source |
| §6 numbers do not reconcile | No XBRL for this company (common for private targets) | Expected; §6 recomputes from filings and says so |
| Overall Confidence `Insufficient` | Evidence too thin for the tier | Do not present it. Try `--tier EXECUTIVE`, or re-run the topics §21.12 flags |
| Every organization field says `[INTERNAL …]` | No Capability Pack or Input Sheet attached | Expected; attach them (`--capability-pack ATTACHED --input-sheet ATTACHED`) and re-run |

More harness-level symptoms: [harness/HARNESS_README.md](../harness/HARNESS_README.md#troubleshooting).

## Exporting

| Symptom | Fix |
|---|---|
| `export support is unavailable … uv sync --extra export` | `uv sync --extra export` |
| `no dossier, run directory or run slug '…'` | Pass a slug under the output dir, a run directory, or the `*-vantage.md` path; `vantage runs list` shows slugs |
| No PDF; LibreOffice warning | Install LibreOffice or pass `--libreoffice-bin` |
| A helper warning (`get-icon`, `get-brand`, `get-stock`, `dgm` …) | The helper is missing or failed; the export used its fallback. `vantage doctor` lists what was found |
| A depth or HTML-mode change has no effect | A plan in `<out>/plan/` wins; export to another `--out` or remove the old plans |
| `agent authoring unavailable — …` | Claude Code is missing or not signed in; the export used derived plans |

See [Export](export.md#troubleshooting).

## Still stuck

Run the command again with `--verbose`, collect `vantage doctor --json` and the last lines of
`<run dir>/run.jsonl`, and open an issue as described in [SUPPORT.md](../SUPPORT.md). Remove
client names and anything from `.env` before you share output.
