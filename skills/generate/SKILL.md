---
name: generate
description: >-
  Produce a Vantage dossier (Verified Account Navigator: Targeting, Analysis & GTM Engine) for a
  target company using the multi-agent, multi-backend Vantage engine. Use whenever the user asks
  to "run a Vantage dossier", "generate a dossier", "build an account research dossier",
  "research company X for the pursuing organization", "produce a pursuit dossier", or names a
  company to profile for account strategy. Supports six execution backends (workflow, api,
  agent-sdk, langgraph, adk, crewai); the default is the Claude Code Workflow (subscription, no
  API key). To turn a finished dossier into a deck, document, PDF or microsite, use
  /vantage:export instead.
argument-hint: <company legal name> [backend] [tier]
---

# Generate a Vantage dossier

**Vantage** = *Verified Account Navigator: Targeting, Analysis & GTM Engine*. It produces the
**v3.0.0** dossier: 22 sections, evidence-locked, claim-ledgered and verification-gated, written as
Markdown by 29 agents across 12 steps with up to ten running concurrently. Verification BLOCKERs
are routed back to the agents that own the defective text (P7R) before the dossier is assembled.

User request / target: $ARGUMENTS

## 0. Resolve the repo

The engine runs from a local clone of the Vantage repository. Never assume a location:

```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT}"
VANTAGE_REPO="${VANTAGE_REPO:-$PLUGIN_ROOT}"
if [ -z "$VANTAGE_REPO" ] && [ -L "$HOME/.claude/skills/vantage" ]; then
  VANTAGE_REPO="$(cd -P "$HOME/.claude/skills/vantage/../../.." && pwd -P)"
fi
[ -d "$VANTAGE_REPO/harness" ] || echo "set VANTAGE_REPO to your Vantage clone"
```

Order of precedence: `VANTAGE_REPO` (an explicit clone) → `${CLAUDE_PLUGIN_ROOT}` (the plugin
install, substituted by Claude Code when this skill runs from the plugin) → the clone behind a `~/.claude/skills/vantage` symlink. Use the resolved absolute path
wherever `$VANTAGE_REPO` appears below, including the Workflow tool arguments.

The commands below use `uv run --project "$VANTAGE_REPO" vantage …`. If `vantage` is already on
`PATH` (for example after `uv tool install`), plain `vantage …` is equivalent. `vantage-engine`
is an alias of `vantage`.

## 1. Gather parameters

Required: the **client legal name**. Ask only if it is missing; infer everything else.

| Param | Flag | Default |
|---|---|---|
| Client legal name | `--client` / `-c` | (required) |
| Run slug | `--slug` / `-s` | `<client-slug>-YYYY-MM` |
| Backend | `--backend` | from config (`workflow`) |
| Output tier | `--tier` | `FULL_ANNEX` (`EXECUTIVE` \| `STANDARD` \| `FULL_ANNEX`) |
| Ticker / private | `--ticker` | `AUTO-DETECT` |
| Vertical | `--vertical` | `AUTO-DETECT` |
| Geography | `--geography` | `AUTO-DETECT` |
| Capability Pack | `--capability-pack` | `NOT_ATTACHED` |
| Account-Team Input Sheet | `--input-sheet` | `NOT_ATTACHED` |
| Pursuing-organization account context | `--account-context` | `NONE` |
| Known relationship | `--relationship` | `NONE` |
| Pursuit objectives | `--objectives` | `NONE` |
| Owner-remediation rounds (P7R) | `--remediation-rounds` | from config |

Every config option is also a flag, and `--set <dotted.key>=<value>` overrides any key for one
run. `uv run --project "$VANTAGE_REPO" vantage run --help` lists them all.

Read defaults from `~/.config/vantage/default.json` (`engine.backend`, `engine.tier`,
`engine.available_backends`) or with `vantage config show`. If the file does not exist, run
`uv run --project "$VANTAGE_REPO" vantage config init` first.

**Tier guidance:** `FULL_ANNEX` for a real pursuit dossier. `EXECUTIVE` when the user wants a fast
read: it runs six research agents instead of sixteen and produces §0–§2 plus the §1 synthesis.

## 2. Choose the backend

Present the choice only if the user has not specified one; otherwise use the config default.

- **`workflow`** (default): runs on the Claude subscription, no API key. Best from inside
  Claude Code.
- **`api`**: direct multi-provider API fan-out (needs `ANTHROPIC_API_KEY`, optionally
  `OPENAI_API_KEY` / `GOOGLE_API_KEY`, plus `TAVILY_API_KEY` and `SEC_EDGAR_IDENTITY`).
- **`agent-sdk` / `langgraph` / `adk` / `crewai`**: the same pipeline via that framework; each
  needs its extra installed (`uv sync --extra <name>`) and `ANTHROPIC_API_KEY`.

`uv run --project "$VANTAGE_REPO" vantage backends` shows readiness.

**Credentials.** The engine defaults to `auth.mode=subscription`: it runs on the user's Claude plan
and reads no API key, even if one is exported. Every backend except `workflow` and `agent-sdk`
needs `--auth api-key`, which is **billed per token**, so never add that flag on your own
initiative. Ask first, and say plainly that it costs money. Add `--ask-key` only if the user wants
to type the key at the terminal (it is not stored). `vantage auth status` shows the current
posture.

## 3. Run

### Backend = `workflow` (preferred inside Claude Code)

Run the bundled workflow natively with the Workflow tool: the same script the engine would
otherwise shell out to, running on the subscription in this session.

> Use a workflow (this is an explicit opt-in). Run the workflow at
> `<VANTAGE_REPO>/harness/workflows/vantage-v3.workflow.mjs` with args:
> ```json
> {"client_legal_name":"<client>","slug":"<slug>","research_as_of":"<today>",
>  "output_tier":"<tier>","ticker_or_private":"<ticker>","target_vertical":"<vertical>",
>  "run_dir":"<output_dir>/<slug>","harness_dir":"<VANTAGE_REPO>/harness",
>  "capability_pack":"<ATTACHED|NOT_ATTACHED>",
>  "account_team_input_sheet":"<ATTACHED|NOT_ATTACHED>",
>  "account_context":"<...>","known_relationship_context":"<...>",
>  "strategic_pursuit_objectives":"<...>"}
> ```

### Any other backend

```bash
uv run --project "$VANTAGE_REPO" vantage run \
  --client "<client>" --slug "<slug>" --backend <backend> --tier <tier> \
  --ticker "<ticker>" --vertical "<vertical>" \
  --capability-pack <ATTACHED|NOT_ATTACHED> --input-sheet <ATTACHED|NOT_ATTACHED> \
  --account-context "<...>" --objectives "<...>"
```

`vantage generate` is a synonym for `vantage run`. Add `--json` for machine-readable progress
events. For live per-agent progress in a terminal, the user can run `vantage --tui` (or
`vantage-tui`).

## 4. Report

When done, report from the dossier's title block and §21:

1. **Dossier path**: `~/.cache/vantage/run/<slug>/<slug>-vantage.md`
   (`vantage runs list` shows recent runs).
2. **Overall Confidence** and the verification result: `Strong` ≥80 · `Adequate` 65–79 ·
   `Thin` 50–64 · `Insufficient` <50. **Say plainly if it is `Insufficient`: the dossier should
   not be presented.**
3. **Remediation**: how many P7R rounds ran and what §21.8 records (fixed, partly fixed, not
   fixed, regressed, declined).
4. **Agents ok/total**, and **name** any agent that did not return. Silent data loss is the failure
   mode a parallel harness must not have.
5. **Topics that stopped on budget** rather than on diminishing returns (§21.12). These are worth
   re-running with an extended budget; everything else genuinely found nothing.
6. **The top high-materiality gaps** (§2.5, §21.11).
7. If the Capability Pack or Input Sheet was not attached, say which fields are consequently
   `[INTERNAL REQUIRED]` and that §21.10 is emitted blank for the account team to fill in.

If the run produced no dossier, surface the readiness issues from `vantage doctor` (usually a
missing key, an auth mode that does not match the chosen backend, or a user config predating v3)
rather than retrying blindly.

## Notes

- **Entity ambiguity is a stop condition.** If preflight reports one, relay it. Researching the
  wrong company thoroughly is the worst outcome this engine can produce.
- **Never invent facts about the pursuing organization.** `--capability-pack`, `--input-sheet`,
  `--account-context` and `--relationship` are the sole basis for any capability or relationship
  content.
- **A thin dossier is not a failed run.** §21.12 and §2.5 exist to distinguish "nothing was there"
  from "we did not look far enough". Report the distinction rather than apologising for the gaps.
- The default output root is `~/.cache/vantage/run`; `harness/` in the repo holds the blueprint.
- To format the finished dossier as a deck, document, PDF or microsite, use **`/vantage:export`**
  (or `vantage export <run-dir>` in a terminal).
