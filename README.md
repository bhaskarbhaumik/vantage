# Vantage — Verified Account Navigator: Targeting, Analysis & GTM Engine

Multi-agent, **multi-backend** research engine that produces **Vantage dossiers**
(the evidence-locked, claim-ledgered, verification-gated **v3.0.0 blueprint** in `harness/` —
22 sections, 29 agents, up to ten concurrent). It ships as a
Python (`uv`) engine + a TypeScript (`npm`) **Ink TUI**, runs a Claude Skill + `/vantage`
command inside Claude Code, and deploys to **GCP / Azure / AWS**.

> Scores are outside-in decision-support tools, never client-facing measurements.

## Backends (pick per run)

| Backend | What it is | Needs |
|---------|------------|-------|
| **`workflow`** *(default)* | Runs the bundled Claude Code Workflow harness — subscription, no API key | `claude` CLI |
| **`api`** | Direct multi-provider API fan-out. The full headless engine. | `--auth api-key` + `ANTHROPIC_API_KEY` (+ `TAVILY_API_KEY`, `SEC_EDGAR_IDENTITY`) |
| **`agent-sdk`** | Same pipeline, each agent run by the Claude Agent SDK | `+ uv sync --extra agent-sdk` |
| **`langgraph`** | A LangGraph `StateGraph` drives the stage pipeline | `+ uv sync --extra langgraph` |
| **`adk`** | Google ADK sequential-agent integration | `+ uv sync --extra adk` |
| **`crewai`** | CrewAI Flow integration | `+ uv sync --extra crewai` |

The default (`workflow`) runs on your Claude subscription and is best from inside Claude Code. The
cloud-deployable, headless path is **`api`** (and the framework backends). `api` is fully
implemented; `agent-sdk` swaps the per-agent runtime; `langgraph`/`adk`/`crewai` are genuine
framework integrations that drive the shared, tested stage pipeline.

## Credentials

**Vantage runs on your Claude subscription by default.** In `subscription` mode the engine reads no
API key at all — an `ANTHROPIC_API_KEY` exported for some other tool is deliberately ignored, so it
cannot silently turn a subscription run into a metered one. API billing is opt-in.

```bash
vantage-engine auth status                    # mode, what each agent class routes to, key presence
vantage-engine run -c Acme -s acme --auth api-key           # metered, this run only
vantage-engine run -c Acme -s acme --auth api-key --ask-key # prompt for the key; never stored
vantage-engine auth use api-key               # persist the default in ~/.config/vantage/default.json
```

Resolution order for a key: the env var → (with `--ask-key`) a hidden terminal prompt → fail with
the variable named. `ANTHROPIC_MODEL`, if set, pins every anthropic-routed agent to one model;
`doctor` and `run` warn that this collapses the `role_model_map` tiers.

Two credential **classes**, so the expensive fan-out can bill separately from the orchestrator:

| Profile | Agents | Config key |
|---|---|---|
| `orchestrator` | preflight, backbone, merge, reconcile, synthesis, verification, assembly (13) | `auth.orchestrator` |
| `research` | the section-wise deep-research agents — Wave A, Wave B, vertical annex (16) | `auth.research` |

Each takes `provider`, `api_key_env`, `model`, `model_env`; unset fields inherit from the role's
model tier. So the research fan-out can run on Gemini against its own key while the orchestrator
stays on Claude:

```json
"auth": {
  "mode": "api-key",
  "research": { "provider": "gemini", "api_key_env": "VANTAGE_RESEARCH_KEY" }
}
```

> Keys live in the environment only. Vantage never writes one to the config file and never logs one.

## Install

```bash
# Python engine
uv sync                      # core (workflow + api backends)
uv sync --extra dev          # + tests/lint
uv sync --extra langgraph    # a framework backend, on demand
uv sync --extra cloud        # all cloud SDKs

# Ink TUI
npm install && npm run build

# Env + config
cp .env.example .env         # fill in keys
uv run vantage-engine config init   # → ~/.config/vantage/default.json
uv run vantage-engine doctor        # environment diagnostics

# Terminal launcher + Claude skill/command
ln -sfn "$(pwd)/scripts/vantage" ~/.local/bin/vantage
bash scripts/install-skill.sh           # links skill + /vantage into ~/.claude
```

Python **3.14** (via `uv`), Node **≥18**.

> **Extras are exclusive per `uv sync`.** `uv sync --extra X` makes the env match *exactly* that
> set (dropping others) — list what you want together, e.g. `uv sync --extra dev --extra langgraph`.
> **`crewai` note:** its `chromadb` dependency still uses `pydantic.v1` and does not import on
> Python 3.14 — `doctor` reports it as "installed but not importable". Use Python ≤3.13 for the
> crewai backend, or prefer `langgraph` / `api`.

## Use

```bash
# Rich Ink TUI (backend + tier pickers, live per-agent progress)
vantage

# Or the engine CLI directly
uv run vantage-engine run \
  --client "Acme Industries, Inc." --slug acme-2026-08 \
  --backend api --tier FULL_ANNEX --ticker "NYSE: ACME"

# A fast read instead of a full pursuit dossier
uv run vantage-engine run -c "Acme" -s acme --tier EXECUTIVE

uv run vantage-engine backends     # readiness of all six
uv run vantage-engine doctor
uv run vantage-engine deploy --target gcp --dry-run
```

Inside **Claude Code**: `/vantage Acme Industries, Inc.` (or ask to "run a Vantage dossier for Acme").
The skill reads your default backend from `~/.config/vantage/default.json`.

Output lands in `~/.cache/vantage/run/<slug>/<slug>-vantage.md` (+ `state/`, `qa/`, `run.jsonl`).

### Output tiers

| Tier | Contents | Agents |
|---|---|---|
| `EXECUTIVE` | §0–§2 + §1 synthesis + top tables | 19 |
| `STANDARD` | §0–§20, condensed appendices | 29 |
| `FULL_ANNEX` *(default)* | All 22 sections + §21.1–21.12 | 29 |

## Architecture

```
preflight (P0, hard gate: entity · ownership form · jurisdiction adapters · verticals · tier)
  └─ backbone (P1: primary sources + precomputed-financials from XBRL)
  └─ Wave A (P2, 10 concurrent): corporate · market · business-model · financials · technology
        strategy · leadership · signals · risk · esg            §3 §4 §5 §6 §8 §9 §10 §13 §14 §17
  └─ Wave B (P3): operations · competition · customers · ai-readiness · vendors · vertical
                                                                §7 §11 §12 §15 §16
  └─ reconcile (P4): source-merge → contradiction + evidence-audit
  └─ synthesis (P5): opportunity → account-strategy + playbook   §18 §19 §20
  └─ exec-brief + methodology (P6 — §1 derived last)             §1 §2
  └─ verification (P7, fresh context, V1–V12) → appendices + assembly (P8)   §21
```

Four properties do most of the work:

- **§1 is written last and placed first.** An executive summary written first invents conclusions
  the body then has to justify — the mechanism that produces confident fabrication in long
  structured generation.
- **The adversarial audit runs before §18.** A refuted claim caught at P4 costs one downgrade;
  caught at verification it costs a rebuild of §18–§20.
- **§3–§17 are vendor-neutral**, checked at BLOCKER severity, so the dossier reads as research rather
  than pre-sales material. §15.6 is the one gated exception.
- **Win probability, account revenue, relationship strength, and stakeholder access are gated** on
  the §21.10 Account-Team Input Sheet. Without it they render `[INTERNAL REQUIRED]` and §21.10
  is emitted as a blank template for the account team to fill in.

- **One generic executor** runs every LLM agent, driven by its Markdown brief in `harness/` — so
  "port all agents" is one code path, not 29. `source-merge` and `assembly` are deterministic
  Python (collation must be exact), as is the XBRL precompute that §6 reconciles against.
- **Provider-agnostic** tool loop (Anthropic native; OpenAI + Gemini translated) with a
  `submit_section` terminal tool; research via **web search (Tavily/Brave)**, **SEC EDGAR**,
  **market data (yfinance)**.
- **Injectable per-agent runner + stage lifecycle** (`prepare`/`execute_step`) is what lets every
  backend reuse the identical DAG.

See `harness/ARCHITECTURE.md` for the dossier design and the phase→wave mapping and `docs`-in-code docstrings for the engine.

## Layout

```
config/default.json          engine + MAS config (→ ~/.config/vantage/default.json)
harness/                     the v3.0.0 blueprint, briefs, contracts, state schema, workflow
src/vantage/
  settings.py models/        config + canonical-state models + events
  blueprint/                 loader + stage DAG
  providers/ tools/          anthropic|openai|gemini + web/edgar/market + run-dir fs
  agents/ pipeline/ render/   executor · orchestrator · merge · assembly
  engine/                    6 backends + registry
  auth.py                    subscription-first credential resolution
  cli.py server.py cloud/    Typer CLI · HTTP service · gcp|azure|aws deploy
cli/                         TypeScript Ink TUI  →  ~/.local/bin/vantage
scripts/                     launcher · skill installer
.claude/skills|commands/     vantage skill + /vantage command
deploy/                      Dockerfile targets + per-cloud manifests/READMEs
tests/                       pytest suite
```

## Migrating from the v2.2 harness

The v3 rewrite renumbers the dossier (13 sections → 22), replaces the agent roster, and changes the
state schema (2.1 → 3.0). Three things need attention:

1. **Run `vantage-engine config migrate`.** A v2-era user config wins over the shipped template
   and carries the old `role_model_map` plus `max_concurrency: 8`, which silently serialises the
   ten-agent research wave — and an `output_dir` still pointing at `~/vantage/runs`. `migrate` drops
   `engine.depth` and agents that no longer exist, fills in keys the template has gained, and
   keeps any genuine override (it backs the old file up to `default.json.bak`). `--dry-run` shows
   the changes first; `doctor` reports the drift and points here.
2. **`--depth BRIEF|STANDARD|DEEP` is now `--tier EXECUTIVE|STANDARD|FULL_ANNEX`**
   (`VANTAGE_DEPTH` → `VANTAGE_TIER`). Old runs' `state.json` is schema 2.1 and is not read
   by the v3 engine.
3. **Existing dossiers do not migrate.** Section numbers, evidence tags (`[FACT]`/`[TRIANGULATED]`
   → the `CONFIRMED`/`ANNOUNCED`/`OBSERVED-SIGNAL`/`INFERRED`/`UNKNOWN` enum), and appendix IDs
   (A–L → §21.1–21.12) all change. `harness/blueprint/vantage-blueprint-v3.md` ends with a v2.2→v3
   mapping table.

## Configuration

See [configuration reference](docs/configuration.md) for current model defaults, per-tier
generation settings, runtime limits, and config migration. Runs default to
`~/.cache/vantage/run`; migrate existing settings with `uv run vantage-engine config migrate`.

## Develop

```bash
uv run python -m pytest -q      # 59 tests
uv run ruff check src tests
npm run typecheck
```

Edit dossier structure/prompts in `harness/` (read at runtime — no code change). Edit the pipeline
in `src/vantage/`. Add a backend: implement `engine/Backend`, register in `engine/registry.py`.

## License

Vantage is available under the [MIT License](LICENSE).
