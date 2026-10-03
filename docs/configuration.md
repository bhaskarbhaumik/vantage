# Configuration

Vantage merges `config/default.json`, the user configuration (normally
`~/.config/vantage/default.json`), `VANTAGE_*` environment overrides, then CLI flags.
`--config` or `VANTAGE_CONFIG` selects another user file; `XDG_CONFIG_HOME` changes
its default location. Credentials remain environment-variable names in JSON.

## Paths and upgrades

The default run root is **`~/.cache/vantage/run`**. Each dossier lives in
`<root>/<slug>/`, with its sections, state, QA artifacts, and event log.
`VANTAGE_OUTPUT_DIR` or `engine.output_dir` selects a different root.
This default is explicit on all platforms; it does not follow `XDG_CACHE_HOME`.

Run `uv run vantage-engine config migrate --dry-run` to review an upgrade, then
`uv run vantage-engine config migrate` to apply it. Migration keeps a timestamped
backup, refreshes the adjacent `default.schema.json`, adds new settings, and upgrades
known shipped model defaults. Custom output paths, model pins, and role mappings survive.
Legacy `~/vantage/runs` and `~/.cache/vantage/runs` settings become the new cache path.
Config v2.1 uses `run_defaults.capability_pack` and `run_defaults.account_context`;
legacy organization-prefixed settings migrate automatically. The CLI uses
`--account-context`, and HTTP/workflow inputs use `account_context` and
`capability_pack`. Update callers to those neutral names. Generated reports use
`[INTERNAL REQUIRED]` and `[CAPABILITY-PACK]` markers.

Migration changes configuration only: move existing run folders separately, checking
for duplicate slugs before merging. No cache cleanup or retention deletion is automatic.

The launcher discovers the checkout through its installed symlink, so it works
from any workspace location. `VANTAGE_REPO` overrides discovery. After relocation, reinstall the
editable Python package, rebuild the UI, and run `bash scripts/install-skill.sh` to
refresh the Claude skill links.

## Models

Defaults verified on **2026-10-03**:

| Role/provider | Model | Source |
| --- | --- | --- |
| Synthesis | `claude-opus-5-5` | [Claude model catalog](https://platform.claude.com/docs/en/models/overview) |
| Research | `claude-sonnet-5-5` | [Claude model catalog](https://platform.claude.com/docs/en/models/overview) |
| Cheap | `claude-haiku-4-5-20251001` | [Claude model catalog](https://platform.claude.com/docs/en/models/overview) |
| Optional OpenAI | `gpt-6.1-sol` | [OpenAI model guide](https://developers.openai.com/api/docs/guides/latest-model/gpt-6-astra.md) |
| Optional Gemini | `gemini-3.5-flash` | [Gemini stable model](https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash) |

`role_model_map` maps agent names to synthesis/research/cheap. Each tier supports
`max_tokens`, `temperature`, and `effort`; null inherits the global setting.
Enable an optional provider with `providers.<name>.enabled=true` before routing to it.
An auth profile can override its class's provider and model. When changing provider,
the destination's `default_model` is used unless the profile or environment pins a model.

Current Claude models use adaptive thinking, omit sampling parameters, and preserve
signed thinking blocks between tool calls. Haiku uses `budget_tokens` when thinking is
on. OpenAI uses Responses with reasoning and tool-call continuity; reasoning models
omit temperature. Gemini retains thought signatures and uses a thinking level for
Gemini 3 models. Provider constraints take precedence: always-thinking models cannot
be disabled with `thinking.enabled=false`. Disabled thinking otherwise leaves Gemini
and OpenAI at their provider defaults; it does not guarantee reasoning is off.

## Runtime controls

| Setting | Effect |
| --- | --- |
| `engine.max_concurrency` | Shared Python pipeline concurrency; provider limits can lower it |
| `engine.max_iterations` | Maximum direct-API turns per agent |
| `engine.tool_result_max_chars` | Truncation limit for direct-API tool results |
| `engine.tool_timeout_seconds` | Wall-clock timeout for each direct-API tool call |
| `providers.*.enabled` | Allow or reject direct calls to this provider |
| `providers.*.timeout_seconds` | SDK request timeout |
| `providers.*.max_attempts` | Total attempts including the first request |
| `providers.*.max_concurrency` | Per credential client concurrency; null inherits engine limit |
| `providers.*.retry_min_seconds`, `retry_max_seconds` | Retry backoff bounds |
| `tools.web_search.max_results` | Maximum search results, including agent overrides |
| `tools.web_search.timeout_seconds`, `snippet_max_chars` | Search deadline and snippet cap |
| `tools.edgar.filings_limit`, `statement_max_chars` | Filing count and financial statement excerpt caps |
| `run_defaults.*` | CLI/HTTP engagement defaults; explicit request values win |

The direct-API controls apply to `api`, `langgraph`, `adk`, and `crewai`, which share
the Python executor. The `workflow` backend uses Claude Code's own model/tool runtime;
`agent-sdk` uses its SDK tool loop. Their runtime limits are not set by these API-loop
controls. Both retain subscription authentication by default. Timing out a threaded
SEC request stops waiting for its result but cannot forcibly stop the worker thread.

`tools.edgar.xbrl` was removed because it never controlled engine behavior. Output
currently supports only `formats: ["md"]` and `keep_state: true`; other values fail
validation. Changing provider configuration never opts a run into API billing.

## Schema maintenance

`config/default.schema.json` is generated from the Pydantic models, so numeric bounds,
enums, nested fields, and null inheritance match runtime validation. Regenerate with:

```bash
uv run python scripts/generate-config-schema.py
uv run pytest tests/test_config.py tests/test_runtime_config.py -q
```

Typed sections reject unknown settings. Top-level metadata and cloud provider maps
remain extensible. Retry maximum must also be at least the minimum (checked at runtime).
