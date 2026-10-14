# Configuration

Vantage reads one JSON configuration, built from layers. Config schema version: **2.2**.

```bash
uv run vantage config show                     # the merged, effective configuration
uv run vantage config get engine.tier
uv run vantage config set export.depth exec    # validated, written to the user file
uv run vantage config unset export.depth       # back to the shipped default
uv run vantage config edit                     # $VISUAL / $EDITOR, then validate
uv run vantage options --filter export         # every key as a flag, with env names
```

## Files and precedence

| Layer (low → high) | Where |
|---|---|
| Shipped defaults | `config/default.json` in the repository (bundled into the wheel) |
| User config | `~/.config/vantage/default.json`, created from the shipped file on first use. `--config PATH` or `VANTAGE_CONFIG` names another file; `XDG_CONFIG_HOME` moves the default directory |
| Environment | `VANTAGE_BACKEND`, `VANTAGE_TIER`, `VANTAGE_OUTPUT_DIR`, `VANTAGE_HARNESS_DIR`, `VANTAGE_AUTH_MODE`, and the generated `VANTAGE_<DOTTED_KEY>` for every key (generated names win over the short ones) |
| Command line | `--backend`, `--tier`, …, every config flag, `--set key=value`, `--role-model agent=tier`, in the order given |

Objects merge key by key; anything else (strings, numbers, lists) replaces the lower layer's
value. The [CLI guide](cli.md#precedence) has worked examples.

`config/default.schema.json` is the JSON Schema for the file. `vantage config init` and
`vantage config migrate` copy it next to the user config, so an editor that understands
`"$schema"` validates and completes keys as you type. `vantage config validate [PATH]` checks a
file against the model (and the schema when `jsonschema` is installed).

Keys are never secrets. Every `*_env` key holds the **name** of an environment variable, never its
value, and `vantage config set` refuses anything that looks like a credential.

## Sections

### engine

| Key | Default | Meaning |
|---|---|---|
| `backend` | `workflow` | `workflow` · `api` · `agent-sdk` · `langgraph` · `adk` · `crewai` ([Backends](backends.md)) |
| `available_backends` | all six | Backends the TUI offers |
| `tier` | `FULL_ANNEX` | `EXECUTIVE` · `STANDARD` · `FULL_ANNEX` |
| `max_concurrency` | `10` | Concurrent agents (1–32). Wave A launches ten; anything lower serialises it |
| `output_dir` | `~/.cache/vantage/run` | Run root; each run is `<output_dir>/<slug>`. Explicit on every platform (does not follow `XDG_CACHE_HOME`) |
| `harness_dir` | `null` | Prompt library. `null` = the bundled `harness/` |
| `max_iterations` | `24` | Maximum direct-API turns per agent |
| `tool_result_max_chars` | `24000` | Truncation for each direct-API tool result |
| `tool_timeout_seconds` | `120` | Wall-clock limit for one direct-API tool call |

### auth

Subscription-first credentials; read [Authentication and billing](auth.md) before changing these.

| Key | Default | Meaning |
|---|---|---|
| `mode` | `subscription` | `subscription` reads no key; `api-key` is billed per token |
| `api_key_env` | `ANTHROPIC_API_KEY` | Variable holding the Anthropic key (api-key mode only) |
| `model_env` | `ANTHROPIC_MODEL` | Variable that, when set, pins every Anthropic-routed agent to one model |
| `prompt_for_key` | `false` | Prompt on the terminal for a missing key (`run --ask-key`) |
| `orchestrator.*`, `research.*` | `null` | Per credential class: `provider`, `api_key_env`, `model`, `model_env`. Unset fields inherit |

### models

Three tiers, each a `provider`, `model`, and optional `max_tokens`, `temperature`, `effort`
(`null` inherits the global value):

| Tier | Default model | Effort |
|---|---|---|
| `synthesis` | `claude-opus-5-5` | `high` |
| `research` | `claude-sonnet-5-5` | `high` |
| `cheap` | `claude-haiku-4-5-20251001` | — |

Global: `temperature` (1.0), `max_tokens` (16000), and `thinking` (`enabled`, `mode`
`auto|adaptive|enabled`, `budget_tokens`, `effort`). Defaults were last verified on 2026-10-03
against the [Claude model catalog](https://platform.claude.com/docs/en/models/overview); the
optional providers default to `gpt-6.1-sol` (OpenAI) and `gemini-3.5-flash` (Gemini).

Provider behaviour: current Claude models use adaptive thinking, omit sampling parameters and keep
signed thinking blocks between tool calls; Haiku uses `budget_tokens` when thinking is on. OpenAI
runs through the Responses API with reasoning and tool-call continuity, and reasoning models omit
temperature. Gemini keeps thought signatures and uses a thinking level for Gemini 3 models.
Provider constraints win: an always-thinking model cannot be turned off with
`thinking.enabled=false`, and disabling thinking leaves OpenAI and Gemini at their provider
defaults.

### role_model_map

Maps each of the 29 agents to a tier (`synthesis`, `research` or `cheap`). An agent missing from
the map falls back to `research`; `vantage doctor` reports drift. Override one agent for one run
with `--role-model agent=tier`, or persist it with
`vantage config set role_model_map.financials synthesis`.

### providers

`anthropic`, `openai` and `gemini`, each with `enabled`, `api_key_env`, `default_model`,
`timeout_seconds`, `max_attempts` (including the first), `max_concurrency` (`null` inherits
`engine.max_concurrency`), `retry_min_seconds` and `retry_max_seconds`. Only `anthropic` is
enabled by default; enable another before routing a tier or credential class to it. When an auth
profile switches provider, the destination's `default_model` is used unless a model is pinned.

### tools

| Key | Default | Meaning |
|---|---|---|
| `web_search.enabled`, `provider` | `true`, `tavily` | `tavily` or `brave` |
| `web_search.api_key_env` | `TAVILY_API_KEY` | (`BRAVE_API_KEY` is used when the provider is `brave`) |
| `web_search.max_results`, `search_depth` | `6`, `advanced` | |
| `web_search.timeout_seconds`, `snippet_max_chars` | `20`, `500` | |
| `edgar.enabled`, `identity_env` | `true`, `SEC_EDGAR_IDENTITY` | SEC EDGAR filings; the identity is `"Name email@example.com"` |
| `edgar.filings_limit`, `statement_max_chars` | `8`, `2500` | |
| `market_data.enabled` | `true` | Quotes and multiples |

The tools are used by the backends that run Vantage's own tool loop (`api`, `langgraph`, `adk`,
`crewai`). The `workflow` backend researches with Claude Code's built-in web search; `agent-sdk`
uses the SDK's own tool loop. A timed-out SEC request stops being waited for, but its worker
thread cannot be killed.

### cloud

`target` (`gcp`, `azure` or `aws`), `image`, and one open map per cloud (`gcp.region`,
`azure.location`, `aws.cluster`, …) used by `vantage deploy`. See [Deployment](deployment.md).

### run_defaults

Defaults for `vantage run` options when they are not given: `primary_geography`,
`target_vertical`, `ticker_or_private` (all `AUTO-DETECT`), `capability_pack` and
`account_team_input_sheet` (`NOT_ATTACHED`), `account_context`, `known_relationship_context`,
`strategic_pursuit_objectives` (`NONE`). An explicit flag or request value always wins.

### output

`formats: ["md"]` and `keep_state: true`. These are the only supported values; the dossier is
Markdown, and `state/` and `qa/` are always kept. Use [export](export.md) for other formats.

### export

| Key | Default | Meaning |
|---|---|---|
| `formats` | `["pptx","docx","pdf","html"]` | Default `vantage export` formats (`pdf` implies `docx`) |
| `depth` | `standard` | `exec` ≈ 18 slides / ~40 pages · `standard` ≈ 31 / ~125 · `full` everything |
| `site_mode` | `microsite` | `microsite` or `deck` |
| `authoring` | `deterministic` | `deterministic` or `agents` |
| `out_dir` | `null` | `null` = `<run dir>/exports` |
| `classification` | `Confidential` | Marking on every page, slide and screen |
| `brand` | `null` | Domain whose brand themes the collateral; `null` = the neutral theme |
| `client_logo` | `true` | Client logo on the cover |
| `helpers.icons`, `helpers.brand`, `helpers.stock_images` | `true` | `get-icon`, `get-brand`, `get-stock` |
| `helpers.diagrams` | `auto` | `auto` · `dgm` · `drawio` · `mermaid` · `none` |
| `helpers.illustrations` | `none` | `napkin` spends Napkin credits, so it is opt-in |
| `helpers.charts` | `matplotlib` | or `plotly` |
| `helpers.libreoffice_bin` | `soffice` | LibreOffice binary for PDF |
| `helpers.timeout_seconds` | `60` | Per helper call |

### ui

| Key | Default | Meaning |
|---|---|---|
| `icons` | `nerd` | `nerd` (Nerd Font) · `unicode` · `ascii` |
| `color` | `auto` | `auto` honours `NO_COLOR` and whether the output is a terminal · `always` · `never` |
| `theme` | `dark` | `dark` · `light` |
| `animations` | `true` | Spinners and live redraws |

Shared by the CLI and the [TUI](tui.md).

## Which settings apply to which backend

The direct-API controls (`engine.max_iterations`, `engine.tool_*`, `providers.*`, `tools.*`,
`models.*`) apply to `api`, `langgraph`, `adk` and `crewai`, which share Vantage's executor. The
`workflow` backend uses Claude Code's own model and tool runtime and the `agent-sdk` backend uses
the SDK's loop, so those limits do not reach them. `engine.tier`, `engine.output_dir`,
`role_model_map` and `run_defaults` apply everywhere. Changing provider configuration never opts a
run into API billing; only `auth.mode` does.

## Environment variables

`.env.example` lists every variable by purpose. Copy it to `.env` (never commit it). The engine
loads `<repo>/.env` and a `.env` in the current directory; real environment variables win.

| Purpose | Variables |
|---|---|
| LLM providers (api-key mode only) | `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL`, `OPENAI_API_KEY`, `GOOGLE_API_KEY`, `GOOGLE_GENAI_USE_VERTEXAI` |
| Research tools | `TAVILY_API_KEY`, `BRAVE_API_KEY`, `SEC_EDGAR_IDENTITY` |
| Export helpers | `BRANDFETCH_CLIENT_ID`, `BRANDFETCH_SECRET_API_KEY`, `LOGO_DEV_PUBLIC_KEY`, `LOGO_DEV_SECRET_KEY`, `LOGOKIT_API_KEY`, `GEMINI_API_KEY` (`get-brand`); `NOUN_API_KEY`, `NOUN_API_SECRET` (`get-icon`); `NAPKIN_API_TOKEN` (`napkin`) |
| Engine | `VANTAGE_CONFIG`, `VANTAGE_BACKEND`, `VANTAGE_TIER`, `VANTAGE_AUTH_MODE`, `VANTAGE_OUTPUT_DIR`, `VANTAGE_HARNESS_DIR`, `VANTAGE_LOG_LEVEL`, `VANTAGE_<DOTTED_KEY>` |
| Claude Code | `CLAUDE_CLI` (path to the `claude` binary, for the `workflow` backend and agent-authored export) |
| TUI and launchers | `VANTAGE_ENGINE` (the engine command the TUI runs), `VANTAGE_REPO` (the clone `scripts/vantage-tui` and the skills use), `NO_COLOR` |
| Cloud | `GCP_PROJECT`, `GOOGLE_CLOUD_REGION`, `GOOGLE_APPLICATION_CREDENTIALS`; `AZURE_*`; `AWS_*` ([Deployment](deployment.md)) |

`FMP_API_KEY`, `FRED_API_KEY` and `ALPHA_VANTAGE_API_KEY` appear in the template as optional
market-data enrichment; the 0.2.0 engine does not read them.

## Migrating a user config

A user config written by an older version wins over the shipped template, so stale values survive
upgrades unless you migrate:

```bash
uv run vantage config migrate --dry-run     # show what would change
uv run vantage config migrate               # apply; the old file is kept as default.json.<stamp>.bak
```

`migrate` reconciles `role_model_map` with the current 29-agent roster, drops keys that no longer
exist (`engine.depth`, `tools.edgar.xbrl`), fills in keys the template has gained (the `export` and
`ui` sections in 2.2), raises `max_concurrency` to the Wave A size, upgrades known shipped model
defaults, moves legacy run roots (`~/vantage/runs`, `~/.cache/vantage/runs`) to
`~/.cache/vantage/run`, renames organization-prefixed run defaults to `capability_pack` and
`account_context`, and refreshes the adjacent schema file. Custom paths, model pins and role
mappings survive. It changes configuration only: move existing run folders yourself, checking for
duplicate slugs.

`vantage doctor` reports drift (`config drift`) and points here.

### From the v2.2 harness

The v3.0.0 harness renumbered the dossier (13 sections → 22), replaced the agent roster and moved
the state schema to 3.0.

- `--depth BRIEF|STANDARD|DEEP` became `--tier EXECUTIVE|STANDARD|FULL_ANNEX`
  (`VANTAGE_DEPTH` → `VANTAGE_TIER`).
- Old runs' `state.json` (schema 2.1) is not read by the v3 engine, and existing dossiers do not
  migrate: section numbers, evidence tags and appendix IDs (A–L → §21.1–21.12) all changed. The
  blueprint (`harness/blueprint/vantage-blueprint-v3.md`) ends with a v2.2 → v3 mapping table.

## Schema maintenance (contributors)

`config/default.schema.json` is generated from the pydantic models, so bounds, enums, nested
fields and `null` inheritance match runtime validation. Typed sections reject unknown keys; the
top-level metadata and the cloud maps stay open. After changing `src/vantage/models/config.py`:

```bash
uv run python scripts/generate-config-schema.py
uv run python scripts/generate-cli-reference.py     # the config flags table in docs/reference/cli.md
uv run python -m pytest tests/test_config.py tests/test_runtime_config.py tests/test_docs.py -q
```

Bump the config schema version as described in [VERSION.md](../VERSION.md).
