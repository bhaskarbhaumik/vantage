# Vantage™

**Verified Account Navigator: Targeting, Analysis & GTM Engine**

[![CI](https://github.com/bhaskarbhaumik/vantage/actions/workflows/ci.yml/badge.svg)](https://github.com/bhaskarbhaumik/vantage/actions/workflows/ci.yml)
[![Version](https://img.shields.io/badge/version-0.2.0-blue)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-3776ab)](pyproject.toml)
[![Node 18.19+](https://img.shields.io/badge/node-18.19%2B-339933)](package.json)

Vantage is a multi-agent research engine that writes an account research dossier on a named
company: 22 sections, every claim tied to a source, and a verification gate that decides how far
the result can be trusted before anyone reads it. A terminal UI and an export pipeline sit on top,
and the whole thing installs as a Claude Code plugin.

> Scores in a dossier are outside-in decision aids built from public evidence. They are not
> measurements of the company and must not be presented to it.

## Why it exists

Long, structured research written by a language model fails in a predictable way: the summary is
written first, the body is bent to fit it, and a confident fabrication reaches a decision maker as
a fact. Vantage is built around that failure.

- **Evidence-locked.** Every statement carries a source ID and an evidence status
  (`CONFIRMED`, `ANNOUNCED`, `OBSERVED-SIGNAL`, `INFERRED`, `UNKNOWN`) in a claim ledger. Gaps are
  recorded as gaps, not filled in.
- **Adversarial before synthesis.** An audit agent tries to refute every high-materiality claim
  before the opportunity and strategy sections are written. Refuted claims cannot be cited.
- **The executive summary is written last.** §1 is derived from the finished body and must point
  every sentence at a register entry.
- **A verification gate.** A fresh-context verifier runs checks V1–V12 and grades the dossier
  `Strong`, `Adequate`, `Thin` or `Insufficient`. *Insufficient means do not present it.*
- **Owner remediation (P7R).** Blocking findings go back to the agents that own the defective
  text. They rewrite their own sections in dependency order, everything downstream re-syncs, and
  a fresh verifier re-runs every check. §21.8 records the outcome of each round.

## Features

- 29 agents across 12 steps, up to ten running concurrently, driven by a Markdown harness you can
  edit without touching code ([harness/](harness/HARNESS_README.md)).
- Three output tiers: `EXECUTIVE`, `STANDARD` and `FULL_ANNEX` (default).
- Six execution backends. The default, `workflow`, runs on your Claude subscription with no API
  key.
- Subscription-first credentials. API billing is an explicit, per-run or per-config opt-in.
- `vantage` CLI: every config key is also a flag, `--json` on every read command, shell
  completion for bash, zsh and fish.
- `vantage-tui`: an Ink terminal UI with a live per-agent dashboard, a runs browser and an export
  wizard. Nerd Font icons by default, with `unicode` and `ascii` fallbacks.
- `vantage export`: turns a finished dossier into a PowerPoint deck, a Word whitepaper, a PDF and
  a single self-contained HTML microsite or deck, with a classification marking on every page.
- A Claude Code plugin with `/vantage:generate` and `/vantage:export`.
- Container image and deploy helpers for GCP, Azure and AWS.

## Quick start

You need [uv](https://docs.astral.sh/uv/) (it installs the pinned Python), Node.js 18.19 or newer
for the TUI, and the [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI signed in to
a Claude plan for the default backend.

```bash
git clone https://github.com/bhaskarbhaumik/vantage.git && cd vantage
uv sync --extra export         # engine + export renderers (use --extra dev to contribute)
npm ci && npm run build        # terminal UI -> tui/dist/
uv run vantage doctor          # configuration, auth, backends, export helpers, TUI
```

Write a dossier, then export it:

```bash
uv run vantage run --client "Example Industries, Inc." --slug example-2026-10
uv run vantage runs list
uv run vantage export example-2026-10 --format pptx --format html
uv run vantage --tui                                               # or the interactive UI
```

`vantage-engine` is an alias of `vantage`. The full walk-through, including PATH setup and a
first-run checklist, is in [Getting started](docs/getting-started.md).

```text
$ vantage --help        # excerpt: the command list
╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────╮
│ run         Run a dossier end to end with the selected backend.                                  │
│ generate    Alias of `run`: produce a dossier end to end.                                        │
│ backends    List execution backends and their readiness.                                         │
│ doctor      Environment, configuration, auth, backend, export and TUI diagnostics.               │
│ deploy      Build the container and deploy the engine to a cloud target.                         │
│ serve       Run the engine as an HTTP service (GET /healthz, POST /run) — for cloud service      │
│             deploys.                                                                             │
│ version     Print the engine version.                                                            │
│ options     List every CLI option — the friendly globals and one flag per config key.            │
│ export      Export a dossier to PPTX, DOCX, PDF and/or self-contained HTML.                      │
│ tui         Launch the Ink TUI (same as `vantage --tui`); extra arguments are forwarded.         │
│ config      Inspect and manage configuration.                                                    │
│ auth        Inspect and switch the credential mode.                                              │
│ runs        List, inspect, open and delete runs in the output dir.                               │
│ completion  Shell completion scripts (bash, zsh, fish).                                          │
╰──────────────────────────────────────────────────────────────────────────────────────────────────╯
```

The TUI home screen (`vantage-tui --ascii --no-color`, sample data):

```text
@ Vantage                                                             [* subscription]  engine 0.2.0
1:~ Home  2:+ New  3:* Live  4:= Runs  5:v Export  6:+ Doctor  7:# Backends  8:% Config
+--------------------------------------------------------------------++----------------------------+
| ~ Engine                                                           || > Quick actions            |
| version      0.2.0  harness 3.0.0  config 2.2                      || > + New dossier            |
| tui          0.2.0                                                 ||   = Browse runs            |
| auth         [* subscription]                                      ||   v Export a dossier       |
| backend      workflow                                              ||   + Doctor                 |
| tier         FULL_ANNEX                                            ||   # Backends               |
| engine cmd   uv run --quiet --project <repo> vantage               ||   % Configuration          |
+--------------------------------------------------------------------++----------------------------+
+--------------------------------------------------------------------------------------------------+
| = Recent runs                                                                       4 browse all |
| # example-2026-10                    Adequate      1B/5M/12m  2026-10-14                         |
| # acme-2026-09                       Insufficient  6B/18M/30m 2026-09-04                         |
| o globex-2026-08                     unverified    -          2026-08-12                         |
| # initech-2026-07                    Strong        0B/1M/4m   2026-07-20                         |
+--------------------------------------------------------------------------------------------------+
enter open - 1-8 screens - ? help - esc back - q quit
```

## Claude Code plugin

Inside Claude Code:

```text
/plugin marketplace add bhaskarbhaumik/vantage
/plugin install vantage@vantage
```

| Command | What it does |
|---|---|
| `/vantage:generate <company> [backend] [tier]` | Research and write a dossier |
| `/vantage:export <run dir or dossier>` | Turn a finished dossier into a deck, whitepaper, PDF and HTML |
| `/vantage <company>` | Short alias of `/vantage:generate`, available inside this repository or after `scripts/install-skill.sh --link` |

With the default backend the skill runs the bundled workflow in your Claude Code session through
the Workflow tool. See [Claude Code](docs/claude-code.md).

## Backends

| Backend | Runs on | Needs |
|---|---|---|
| `workflow` *(default)* | Claude subscription, through the Claude Code CLI | `claude` on PATH, signed in |
| `api` | Provider APIs directly (Anthropic, OpenAI, Gemini) | `--auth api-key` and the provider keys |
| `agent-sdk` | The same pipeline, each agent run by the Claude Agent SDK | `uv sync --extra agent-sdk` |
| `langgraph` | A LangGraph `StateGraph` over the shared pipeline | `uv sync --extra langgraph`, `--auth api-key` |
| `adk` | Google ADK sequential agents | `uv sync --extra adk`, `--auth api-key` |
| `crewai` | A CrewAI Flow | `uv sync --extra crewai`, `--auth api-key` |

`uv run vantage backends` shows readiness. Details and trade-offs: [Backends](docs/backends.md).

## Credentials

Vantage runs on your Claude subscription by default. In `subscription` mode the engine reads no API
key at all, so an `ANTHROPIC_API_KEY` exported for another tool cannot turn a run into a metered
one. Per-token billing happens only when you ask for it:

```bash
uv run vantage auth status                                     # what would be used, and whether keys are set
uv run vantage run --client "Example Corp" --backend api --auth api-key   # billed per token, this run only
```

Keys live in environment variables only and are never written to the config file. See
[Authentication and billing](docs/auth.md).

## Output

```text
~/.cache/vantage/run/<slug>/
  <slug>-vantage.md          the dossier
  sections/                  one Markdown file per owning agent
  state/                     merged run state (schema 3.0) and per-agent fragments
  qa/                        evidence audit, verification report(s), remediation orders
  run.jsonl                  structured event stream
  exports/                   vantage export output: deck, whitepaper, PDF, HTML, manifest.json, plan/
```

The run root is `engine.output_dir`. Reading a finished run (Overall Confidence, §21.12, §2.5):
[Architecture](docs/architecture.md#reading-a-dossier).

## Documentation

| | |
|---|---|
| [Getting started](docs/getting-started.md) | Install, first run, first export |
| [CLI guide](docs/cli.md) · [CLI reference](docs/reference/cli.md) | Commands, flags, precedence, JSON mode, exit codes |
| [Terminal UI](docs/tui.md) | Screens, keys, icon modes, themes |
| [Export](docs/export.md) | Formats, depth, branding, helpers, plans |
| [Configuration](docs/configuration.md) | Every section, environment variables, migration |
| [Backends](docs/backends.md) · [Authentication](docs/auth.md) | Execution and billing |
| [Architecture](docs/architecture.md) | Pipeline, P7R remediation, harness design |
| [Claude Code](docs/claude-code.md) | Plugin, skills, Workflow tool |
| [Deployment](docs/deployment.md) | Container, GCP, Azure, AWS |
| [Troubleshooting](docs/troubleshooting.md) · [FAQ](docs/faq.md) | When something is off |

All documentation: [docs/](docs/README.md).

## Contributing

Contributions are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md) for the development setup and
the rules for changing the harness, and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). Report security
issues privately as described in [SECURITY.md](SECURITY.md). Questions: [SUPPORT.md](SUPPORT.md).
Release history: [CHANGELOG.md](CHANGELOG.md) and [VERSION.md](VERSION.md).

## License

[MIT](LICENSE).
