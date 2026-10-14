# Setting up Vantage v1 — CLI and `/vantage` command

**Vantage** = *Verified Account Navigator: Targeting, Analysis & GTM Engine*.
**Classification:** Internal account research.

This guide gets you from a clean machine to a working Vantage install with two entry points:

| Entry point | What it is | Where it runs |
|---|---|---|
| **`/vantage`** | Claude Code slash command → the `vantage` skill | Inside your Claude Code session |
| **`vantage`** | Terminal CLI (Ink TUI) → the Python engine | Your terminal |

Both run on **your Claude subscription by default**. No Anthropic API key is required, and none is
read — see [§7](#7-how-the-subscription-path-works) for why that is enforced rather than assumed.

---

## 1. Prerequisites

| Requirement | Why | Check |
|---|---|---|
| **Claude subscription** (Pro or Max) | Pays for every agent in the default path | `claude` opens without asking for a key |
| **Claude Code CLI** ≥ 2.0 | The default `workflow` backend shells out to it | `claude --version` |
| **Python ≥ 3.12** | The engine | `python3 --version` |
| **uv** | Dependency + venv manager | `uv --version` |
| **Node ≥ 18** | The Ink TUI | `node --version` |
| **git** | Cloning | `git --version` |

Install the missing ones:

```bash
# macOS
brew install node git
curl -LsSf https://astral.sh/uv/install.sh | sh          # uv (also installs a managed Python)
npm install -g @anthropic-ai/claude-code                 # Claude Code CLI (or your
                                                         # platform's package manager)

# Linux — same, minus brew
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then sign in to Claude Code once, interactively. **Run this yourself in a terminal** — it opens a
browser and cannot be automated:

```bash
claude          # follow the login prompt, choose your Pro/Max account, then /exit
```

Verify the session is live and on your subscription:

```bash
claude -p 'Reply with exactly: SUBSCRIPTION-OK'
# → SUBSCRIPTION-OK
```

If that prints the phrase, everything below will bill to your plan rather than an API key.

---

## 2. Clone the repo

```bash
mkdir -p ~/Developer && cd ~/Developer
git clone <your-vantage-remote> vantage
cd vantage
```

The launcher and skill installer discover the checkout from their own location. To
select another checkout explicitly, export `VANTAGE_REPO`:

```bash
echo 'export VANTAGE_REPO="$HOME/path/to/vantage"' >> ~/.zshrc   # or ~/.bashrc
export VANTAGE_REPO="$HOME/path/to/vantage"
```

---

## 3. Install the engine and the TUI

```bash
cd "${VANTAGE_REPO:-$HOME/Developer/vantage}"

uv sync                    # Python engine — covers the workflow + api backends
npm install && npm run build   # Ink TUI → cli/dist/index.js
```

`uv sync` creates `.venv/` and installs the `vantage-engine` console script inside it.

> **Extras are exclusive per `uv sync`.** `uv sync --extra X` makes the environment match *exactly*
> that set and drops the others. List everything you want together:
> `uv sync --extra dev --extra langgraph`. You do **not** need any extra for the subscription path.

---

## 4. Install the two entry points

### 4a. The `vantage` terminal CLI

```bash
ln -sfn "$(pwd)/scripts/vantage" ~/.local/bin/vantage
```

Make sure `~/.local/bin` is on your `PATH`:

```bash
case ":$PATH:" in *":$HOME/.local/bin:"*) echo "on PATH";; *)
  echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc; export PATH="$HOME/.local/bin:$PATH";;
esac
vantage version     # → 0.1.0
```

### 4b. The `/vantage` Claude Code command

```bash
bash scripts/install-skill.sh
```

That symlinks two things into `~/.claude`:

```
~/.claude/skills/vantage      -> $VANTAGE_REPO/.claude/skills/vantage
~/.claude/commands/vantage.md -> $VANTAGE_REPO/.claude/commands/vantage.md
```

Because they are symlinks, `git pull` updates the skill with no reinstall. Restart Claude Code (or
run `/skills`) so it picks them up.

---

## 5. Create and check your config

```bash
uv run vantage-engine config init     # → ~/.config/vantage/default.json
uv run vantage-engine doctor
```

`doctor` should report:

```
harness          .../vantage/harness  ok
default backend  workflow · tier FULL_ANNEX
concurrency      10

harness
  config matches the v3.0.0 agent roster

auth
  mode           subscription — runs on your Claude plan; no API key is read, even if one is exported

backends
  workflow   ready
```

**`workflow   ready` is the line that matters.** The other five backends reporting "not ready" is
correct and expected — they are the metered API path (see [§8](#8-optional-the-metered-api-path)).

If you are upgrading an install that predates the rename, run the migration instead of `config init`:

```bash
uv run vantage-engine config migrate --dry-run   # preview
uv run vantage-engine config migrate             # apply; keeps a .bak
```

Optionally copy the env template. **You do not need to fill in any LLM key for the subscription
path** — the only entries worth setting are the free research-tool ones:

```bash
cp .env.example .env
# SEC_EDGAR_IDENTITY="Your Name you@example.com"   ← required by SEC fair-access policy
# TAVILY_API_KEY=...                                ← optional, improves web search
```

Never commit `.env`. The repo `.gitignore` already excludes every `.env*` except the template.

---

## 6. Run it

### 6a. Via `/vantage` (inside Claude Code)

```
/vantage Acme Industries, Inc.
```

The skill gathers the run parameters, then executes the bundled workflow **natively in your current
Claude Code session** using the Workflow tool. Agents research with Claude Code's built-in web
search. This is the lowest-friction path and the one to prefer.

The first time you run it, Claude Code asks you to opt in to the Workflow tool. Accept — the harness
cannot run otherwise.

You can pin the shape of the run in the same line:

```
/vantage Acme Industries, Inc. workflow EXECUTIVE
```

`EXECUTIVE` runs six research agents instead of sixteen for a fast read; `FULL_ANNEX` (the default)
runs the full 29-agent pursuit dossier.

### 6b. Via the `vantage` CLI (in a terminal)

```bash
vantage
```

That opens the Ink TUI, which walks you through client → slug → backend → tier and then streams
per-agent progress. Under the hood it spawns the Python engine, which shells out to `claude -p` —
so it is still your subscription paying, not an API key.

Non-interactive equivalent:

```bash
cd "$VANTAGE_REPO"
uv run vantage-engine run \
  --client "Acme Industries, Inc." \
  --slug   acme-2026-09 \
  --backend workflow \
  --tier   FULL_ANNEX
```

Output lands in `~/.cache/vantage/run/<slug>/<slug>-vantage.md`, alongside `sections/` (per-agent
section Markdown), `state/` (the canonical `state.json` plus each agent's fragment), `qa/`, and
`run.jsonl` (the per-agent event stream).

---

## 7. How the subscription path works

Two layers have to agree, and both default to your plan:

**Layer 1 — the auth mode.** `auth.mode` is `subscription`, so the engine reads no API key. This is
enforced, not merely defaulted: an `ANTHROPIC_API_KEY` exported for some other tool is *deliberately
ignored*, so it cannot silently turn a plan-funded run into a metered one. Switching to metered
billing takes an explicit `--auth api-key`.

**Layer 2 — the backend.** `workflow` is the default. It does not call the Anthropic API at all; it
runs the harness through the Claude Code CLI, which uses your existing login.

```
/vantage  ──► Claude Code session (your subscription) ──► Workflow tool ──► 29 agents
vantage   ──► Ink TUI ──► vantage-engine ──► claude -p ──► Workflow tool ──► 29 agents
```

Check the posture any time:

```bash
vantage auth status
```

```
mode           subscription — runs on your Claude plan; no API key is read, even if one is exported
orchestrator   13 agents · provider anthropic · model (per role_model_map tier)
research       16 agents · provider anthropic · model (per role_model_map tier)
```

**Things that would divert you off the subscription** — confirm all are unset if you expect a
plan-funded run:

```bash
for v in ANTHROPIC_API_KEY ANTHROPIC_AUTH_TOKEN ANTHROPIC_BASE_URL VANTAGE_AUTH_MODE; do
  printenv "$v" >/dev/null 2>&1 && echo "$v = SET" || echo "$v = unset"
done
```

`ANTHROPIC_BASE_URL` and `ANTHROPIC_AUTH_TOKEN` redirect the *Claude Code CLI itself* (to Bedrock,
Vertex, or a gateway) and are outside the engine's control — the engine's subscription mode cannot
override them.

---

## 8. Optional: the metered API path

Only if you want headless or cloud runs, which the `workflow` backend cannot do — it needs an
interactive Claude Code login.

> **This is billed per token against your API key, not your subscription.**

```bash
export ANTHROPIC_API_KEY=...                  # never commit it
uv run vantage-engine run -c "Acme" -s acme --backend api --auth api-key

# or have it prompted on the terminal instead (never stored, never logged):
uv run vantage-engine run -c "Acme" -s acme --backend api --auth api-key --ask-key

# to make metered the persistent default:
uv run vantage-engine auth use api-key
```

Two credential classes can point at different vendors and keys, so the expensive research fan-out
bills separately from the orchestrator. In `~/.config/vantage/default.json`:

```json
"auth": {
  "mode": "api-key",
  "orchestrator": { "provider": "anthropic" },
  "research":     { "provider": "gemini", "api_key_env": "VANTAGE_RESEARCH_KEY" }
}
```

Keys live in the environment only. Vantage never writes one to the config file and never logs one —
put the *name* of the variable there, never the value.

---

## 9. Verifying the whole install

```bash
claude -p 'Reply with exactly: SUBSCRIPTION-OK'   # subscription is live
vantage version                                   # → 0.1.0
vantage doctor                                    # workflow: ready
vantage backends                                  # workflow ★ yes
ls ~/.claude/commands/vantage.md ~/.claude/skills/vantage/SKILL.md
```

Then in Claude Code, type `/vantage` — it should autocomplete.

---

## 10. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `vantage: command not found` | `~/.local/bin` not on `PATH` | §4a |
| `vantage: TUI not built at …` | `npm run build` not run, or wrong clone path | `npm install && npm run build`; set `VANTAGE_REPO` |
| `/vantage` doesn't autocomplete | Symlinks missing, or Claude Code not restarted | `bash scripts/install-skill.sh`, restart |
| `Claude Code CLI 'claude' not found` | Not installed or not on `PATH` | §1; or set `CLAUDE_CLI=/full/path/to/claude` |
| `workflow finished but no dossier was produced` | Workflow tool not opted into | Re-run and accept the opt-in prompt |
| `backend 'api' … cannot use the Claude subscription` | Expected on the default path | Use `--backend workflow`, or opt into §8 |
| `ANTHROPIC_API_KEY is not set` | You passed `--auth api-key` without a key | Export it, add `--ask-key`, or drop `--auth api-key` |
| `role_model_map names agents that no longer exist` | Config predates v3.0.0 | `vantage-engine config migrate` |
| `max_concurrency is 8 but Wave A launches 10` | Same | Same |
| `output_dir still points at a legacy run tree` | Config predates the current run layout | Same |
| `crewai installed but not importable` | Its `chromadb` dep needs `pydantic.v1`, broken on Python 3.14 | Use `langgraph` or `api`, or Python ≤ 3.13 |

---

## Appendix — every command in one block

For a machine that already has Claude Code, Python 3.12+, uv, and Node 18+:

```bash
git clone <your-vantage-remote> ~/Developer/vantage
cd ~/Developer/vantage
uv sync
npm install && npm run build
ln -sfn "$(pwd)/scripts/vantage" ~/.local/bin/vantage
bash scripts/install-skill.sh
uv run vantage-engine config init
uv run vantage-engine doctor          # expect: workflow ready · mode subscription
```

Then `/vantage <Company>` in Claude Code, or `vantage` in a terminal.
