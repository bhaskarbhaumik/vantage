# Backends

A backend decides *how* the agents run. Every backend executes the same harness: the same briefs,
the same 22-section blueprint, the same stage graph. Pick one per run with `--backend`, or set
`engine.backend`.

```bash
uv run vantage backends                 # readiness of all six, the default starred
uv run vantage run --client "Example Corp" --backend api --auth api-key
```

| Backend | Runs on | Install | Auth | Owner remediation (P7R) |
|---|---|---|---|---|
| `workflow` *(default)* | The Claude Code CLI, headless, running the bundled Workflow | core | Subscription | Yes |
| `api` | Vantage's own tool loop against provider APIs | core | `--auth api-key` | Not yet |
| `agent-sdk` | The same pipeline, each agent run by the Claude Agent SDK | `--extra agent-sdk` | Subscription or API key | Not yet |
| `langgraph` | A LangGraph `StateGraph` driving the stage pipeline | `--extra langgraph` | `--auth api-key` | Not yet |
| `adk` | Google ADK sequential agents | `--extra adk` | `--auth api-key` | Not yet |
| `crewai` | A CrewAI Flow | `--extra crewai` | `--auth api-key` | Not yet |

Install an extra with `uv sync --extra <name>`, listing every extra you want in the same call
(`uv sync --extra export --extra langgraph`).

## workflow

Runs `harness/workflows/vantage-v3.workflow.mjs` through the Claude Code CLI in headless print
mode. Agents research with Claude Code's built-in web search. Nothing here reads an API key: the
CLI authenticates with your Claude login, so the run is paid for by your plan.

- Needs `claude` on PATH (or `CLAUDE_CLI=/path/to/claude`) and a plan with the Workflow tool.
- Inside Claude Code, `/vantage:generate` runs the same workflow natively in your session instead
  of shelling out ([Claude Code](claude-code.md)).
- It is the only backend that implements P7R owner remediation (`--remediation-rounds 0|1|2`,
  default 1).
- With `--auth api-key` the backend warns: the Claude Code CLI still uses its own credentials, so
  the key would not be spent. Use `--backend api` for metered runs.
- It needs an interactive Claude login, so it does not deploy to cloud.

## api

The headless engine: Vantage's provider-agnostic tool loop (Anthropic native; OpenAI and Gemini
translated) with a `submit_section` terminal tool, and research through Tavily or Brave web
search, SEC EDGAR and market data. `source-merge`, `assembly` and the XBRL financial precompute run
as deterministic Python. This is the backend for servers and cloud jobs.

Needs `--auth api-key` (billed per token), the key for every provider the role map routes to, and
usually `TAVILY_API_KEY` and `SEC_EDGAR_IDENTITY`. `vantage backends` names whatever is missing.

## agent-sdk

The same stage pipeline, with each agent run by the Claude Agent SDK. Without an API key it uses
Claude Code's own credentials, so it works in subscription mode.

## langgraph, adk, crewai

Framework integrations: a LangGraph `StateGraph`, a Google ADK sequential agent, or a CrewAI Flow
drives the shared, tested stage pipeline. They use Vantage's executor, so the
[direct-API settings](configuration.md#which-settings-apply-to-which-backend) apply, and they need
`--auth api-key`.

`crewai` note: its `chromadb` dependency still imports `pydantic.v1`, which does not work on
Python 3.14. `doctor` then reports *installed but not importable*. Use Python 3.13 or earlier for
that backend, or prefer `langgraph` or `api`.

## Choosing

- Inside Claude Code, or on your own machine with a Claude plan: **`workflow`**.
- Unattended, on a server or in the cloud: **`api`**.
- You already standardise on LangGraph, ADK or CrewAI and want Vantage inside it: the matching
  framework backend.

## Readiness

`vantage backends` and `vantage doctor` call each backend's readiness check: the auth mode, the
installed extra, the Claude Code CLI, the routed providers' keys. `vantage backends --json` gives
the same as `{"default", "backends": [{"name", "ready", "issues"}]}`.

## Adding a backend

Implement `vantage.engine.base.Backend` (`run(job)` and `check()`), register it in
`src/vantage/engine/registry.py`, add it to the `engine.backend` choices in
`src/vantage/models/config.py`, regenerate the schema and the CLI reference, and add tests with
mocked providers. See [CONTRIBUTING.md](../CONTRIBUTING.md).
