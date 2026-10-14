# Getting started

From a clean machine to a finished dossier and a deck. Every command here runs from the root of
your clone.

## 1. Prerequisites

| Requirement | Why | Check |
|---|---|---|
| [uv](https://docs.astral.sh/uv/) | Installs the pinned Python (3.14; 3.12+ supported) and the engine | `uv --version` |
| Node.js **18.19+** and npm | The terminal UI (`vantage-tui`) | `node --version` |
| [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI, signed in to a Claude plan | The default `workflow` backend runs through it | `claude --version` |
| git | Cloning | `git --version` |
| LibreOffice *(optional)* | PDF export | `soffice --version` |

Sign in to Claude Code once, interactively (it opens a browser):

```bash
claude            # choose your Claude plan account, then /exit
claude -p 'Reply with exactly: SUBSCRIPTION-OK'
```

If the second command prints `SUBSCRIPTION-OK`, runs on the default backend bill to your plan. Two
variables redirect the Claude Code CLI itself (to a gateway or a cloud provider) and are outside
Vantage's control: `ANTHROPIC_BASE_URL` and `ANTHROPIC_AUTH_TOKEN`. Leave them unset if you expect
a plan-funded run. See [Authentication and billing](auth.md).

## 2. Install

```bash
git clone https://github.com/bhaskarbhaumik/vantage.git
cd vantage
uv sync --extra export        # engine + export renderers
npm ci && npm run build       # terminal UI -> tui/dist/index.js
```

- `uv sync` alone installs the engine with the `workflow` and `api` backends; `--extra export`
  adds `vantage export`. Contributors use `uv sync --extra dev`, which includes `export`.
- `uv sync --extra X` makes the environment match *exactly* that set of extras. List everything
  you want in one call, for example `uv sync --extra export --extra langgraph`.

### Put the commands on your PATH (optional)

`uv run vantage …` works from the clone without any PATH change. To type `vantage` directly,
activate the project environment, and link the TUI launcher:

```bash
source .venv/bin/activate                                   # vantage and vantage-engine
mkdir -p ~/.local/bin
ln -sfn "$PWD/scripts/vantage-tui" ~/.local/bin/vantage-tui # vantage-tui from anywhere
```

`scripts/vantage-tui` follows its own symlink back to the clone; `VANTAGE_REPO` overrides that.

## 3. Configure and check

```bash
uv run vantage config init     # creates ~/.config/vantage/default.json from the template
uv run vantage doctor
```

`doctor` groups its checks by `engine`, `harness`, `auth`, `tools`, `backends`, `export`,
`export helpers` and `tui`. On the default path, the lines that matter are:

```text
auth      mode       ok    subscription — runs on your Claude plan; no API key is read, even if one is exported
backends  workflow   ok    ready
```

The other five backends report warnings until you install their extra and opt into API billing.
That is expected. Upgrading from an older install? Run `uv run vantage config migrate --dry-run`
first ([Configuration](configuration.md#migrating-a-user-config)).

Optionally copy the environment template. No LLM key is needed for the subscription path; the
research-tool entries are the useful ones:

```bash
cp .env.example .env
# SEC_EDGAR_IDENTITY="Your Name you@example.com"   (SEC fair-access policy asks for it)
# TAVILY_API_KEY=...                                (web search for the API-driven backends)
```

Never commit `.env`. The engine loads `<repo>/.env` and a `.env` in the current directory;
variables already set in the environment win.

## 4. Write your first dossier

```bash
uv run vantage run --client "Example Industries, Inc." --slug example-2026-10
```

That runs the `FULL_ANNEX` tier on the `workflow` backend. Without `--slug`, the run directory is
named from the client name minus its legal suffix plus the year and month
(`example-industries-2026-10`). Useful options:

```bash
uv run vantage run --client "Example Industries, Inc." --slug example-2026-10 \
  --tier EXECUTIVE --ticker "NYSE: EXMP" --dry-run      # print the resolved job; run nothing
uv run vantage run --client "Example Industries, Inc." --tier EXECUTIVE   # a fast read
```

The dossier lands in `~/.cache/vantage/run/<slug>/<slug>-vantage.md`. Check the run:

```bash
uv run vantage runs list
uv run vantage runs show example-2026-10
```

Read the **Overall Confidence** in the title block first: `Strong` ≥80, `Adequate` 65–79, `Thin`
50–64, `Insufficient` <50. An `Insufficient` dossier should not be presented.

Prefer an interactive run? `uv run vantage --tui` opens the terminal UI on its home screen; press
`2` for the new-dossier form ([Terminal UI](tui.md)).

## 5. Export it

```bash
uv run vantage export example-2026-10                       # every format in export.formats
uv run vantage export example-2026-10 --format pptx --depth exec
uv run vantage export example-2026-10 --format html --site-mode deck --open
```

Output goes to `<run dir>/exports/`: `<slug>-deck.pptx`, `<slug>-whitepaper.docx`, the matching
PDF (with LibreOffice), `<slug>-microsite.html` (or `-deck.html`) and `manifest.json`. Every page
is marked `Confidential` unless you change `--classification`. See [Export](export.md).

## 6. Inside Claude Code

```text
/plugin marketplace add bhaskarbhaumik/vantage
/plugin install vantage@vantage
/vantage:generate Example Industries, Inc.
/vantage:export example-2026-10
```

See [Claude Code](claude-code.md).

## Quick fixes

| Symptom | Fix |
|---|---|
| `vantage: command not found` | Use `uv run vantage …`, or `source .venv/bin/activate` |
| `cannot start the TUI: the TUI is not built …` | `npm ci && npm run build` |
| `Claude Code CLI 'claude' not found` | Install Claude Code, or set `CLAUDE_CLI=/full/path/to/claude` |
| `backend 'api' … cannot use the Claude subscription` | Expected on the default path: use `--backend workflow`, or opt into `--auth api-key` ([Auth](auth.md)) |
| `export support is unavailable … uv sync --extra export` | `uv sync --extra export` |
| PDF missing from an export | Install LibreOffice; `vantage doctor` shows whether `soffice` is found |
| `doctor` reports config drift | `uv run vantage config migrate` |

More in [Troubleshooting](troubleshooting.md).
