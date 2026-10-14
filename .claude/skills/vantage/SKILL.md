---
name: vantage
description: >-
  Produce a Vantage dossier (Verified Account Navigator: Targeting, Analysis & GTM Engine)
  for a target company using the multi-agent,
  multi-backend vantage engine. Use whenever the user asks to "run a Vantage dossier", "build an account
  intelligence dossier", "research company X for the pursuing organization", "produce a pursuit dossier", or names a
  company to profile for account strategy. Supports six execution backends (workflow, api,
  agent-sdk, langgraph, adk, crewai); default is the Claude Code Workflow (subscription, no API key).
---

# vantage — run a Vantage dossier

**Vantage** = *Verified Account Navigator: Targeting, Analysis & GTM Engine*.

Drives the **vantage** engine from a local clone of the repo.

**Resolve the repo path first** — this skill is shared by every user, so never assume a location:

```bash
VANTAGE_REPO="${VANTAGE_REPO:-$(cd -P "$HOME/.claude/skills/vantage/../../.." && pwd -P)}"
[ -d "$VANTAGE_REPO/harness" ] || echo "set VANTAGE_REPO to your vantage clone"
```

Use `$VANTAGE_REPO` in every command below. Where a literal path is needed (the Workflow tool
args), substitute the resolved absolute path.
It produces the **v3.0.0** Vantage dossier — 22 sections, evidence-locked, claim-ledgered, verification-gated —
as Markdown, from 29 agents across 12 steps with up to ten running concurrently.

## 1. Gather parameters

Required: **client legal name**. Ask only if it is missing — infer everything else.

| Param | Flag | Default |
|---|---|---|
| Client legal name | `--client` | (required) |
| Run slug | `--slug` | `<client-slug>-YYYY-MM` |
| Backend | `--backend` | from config (`workflow`) |
| Output tier | `--tier` | `FULL_ANNEX` (`EXECUTIVE` \| `STANDARD` \| `FULL_ANNEX`) |
| Ticker / private | `--ticker` | `AUTO-DETECT` |
| Vertical | `--vertical` | `AUTO-DETECT` |
| Geography | `--geography` | `AUTO-DETECT` |
| Capability Pack | `--capability-pack` | `NOT_ATTACHED` |
| Account-Team Input Sheet | `--input-sheet` | `NOT_ATTACHED` |
| the pursuing organization account context | `--account-context` | `NONE` |
| Known relationship | `--relationship` | `NONE` |
| Pursuit objectives | `--objectives` | `NONE` |

Read defaults from `~/.config/vantage/default.json` (`engine.backend`, `engine.tier`,
`engine.available_backends`). If it does not exist, run `uv run --project "$VANTAGE_REPO" vantage-engine config init` first.

**Tier guidance:** `FULL_ANNEX` for a real pursuit dossier. `EXECUTIVE` when the user wants a fast
read — it runs six research agents instead of sixteen and produces §0–§2 plus the §1 synthesis.

## 2. Choose the backend

Present the choice only if the user has not specified one; otherwise use the config default.

- **`workflow`** (default) — runs on the Claude subscription, no API key. **Best from inside
  Claude Code.**
- **`api`** — direct multi-provider API fan-out (needs `ANTHROPIC_API_KEY`, optionally
  `OPENAI_API_KEY` / `GOOGLE_API_KEY`, plus `TAVILY_API_KEY` and `SEC_EDGAR_IDENTITY`).
- **`agent-sdk` / `langgraph` / `adk` / `crewai`** — same pipeline via that framework; each needs
  its extra installed (`uv sync --extra <name>`) and `ANTHROPIC_API_KEY`.

`uv run --project "$VANTAGE_REPO" vantage-engine backends` shows readiness.

**Credentials.** The engine defaults to `auth.mode=subscription`: it runs on the user's Claude plan
and reads no API key, even if one is exported. Every backend except `workflow` and `agent-sdk`
needs `--auth api-key`, which is **billed per token** — so never add that flag on your own
initiative. Ask first, and say plainly that it costs money. Add `--ask-key` only if the user wants
to type the key at the terminal (it is not stored). `vantage-engine auth status` shows the current
posture.

## 3. Run

### Backend = `workflow` (preferred inside Claude Code)

Run the bundled workflow **natively** with the Workflow tool — the same script the engine would
otherwise shell out to, running on the subscription in this session:

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
cd "$VANTAGE_REPO"
uv run vantage-engine run \
  --client "<client>" --slug "<slug>" --backend <backend> --tier <tier> \
  --ticker "<ticker>" --vertical "<vertical>" \
  --capability-pack <ATTACHED|NOT_ATTACHED> --input-sheet <ATTACHED|NOT_ATTACHED> \
  --account-context "<...>" --objectives "<...>"
```

For a rich terminal UI, tell the user they can run `vantage` (the Ink TUI wrapper).

## 4. Report

When done, report from the dossier's title block and §21:

1. **Dossier path** — `~/.cache/vantage/run/<slug>/<slug>-vantage.md`
2. **Overall Confidence** and the verification result — `Strong` ≥80 · `Adequate` 65–79 ·
   `Thin` 50–64 · `Insufficient` <50. **Say plainly if it is `Insufficient`: the dossier should not
   be presented.**
3. **Agents ok/total**, and **name** any agent that did not return — silent data loss is the failure
   mode a parallel harness must not have.
4. **Topics that stopped on budget** rather than diminishing returns (§21.12). These are worth
   re-running with an extended budget; everything else genuinely found nothing.
5. **The top high-materiality gaps** (§2.5, §21.11).
6. If the Capability Pack or Input Sheet was not attached, say which fields are consequently
   `[INTERNAL REQUIRED]` and that §21.10 is emitted blank for the account team to fill in.

If the run produced no dossier, surface the readiness issues from `vantage-engine doctor`
(usually a missing key, an auth mode that does not match the chosen backend, or a user config
predating v3) rather than retrying blindly.

## Notes

- **Entity ambiguity is a stop condition.** If preflight reports one, relay it — researching the
  wrong company thoroughly is the worst outcome this engine can produce.
- **Never invent the pursuing organization facts.** `--capability-pack`, `--input-sheet`, `--account-context`, and
  `--relationship` are the sole basis for any organization capability or relationship content.
- **A thin dossier is not a failed run.** §21.12 and §2.5 exist to distinguish "nothing was there"
  from "we did not look far enough". Report the distinction rather than apologising for the gaps.
- The default output root is `~/.cache/vantage/run`; the in-repo `harness/` holds the blueprint.
- To format the finished dossier as a deck, whitepaper, or microsite, use the **vantage-export** skill.
