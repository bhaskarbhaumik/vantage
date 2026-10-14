# Claude Code

The repository is a Claude Code plugin. Inside Claude Code it adds two skills, and with the default
backend the research runs in your session on your Claude plan.

## Install

```text
/plugin marketplace add bhaskarbhaumik/vantage
/plugin install vantage@vantage
```

To test a local clone, add it as a marketplace by path:

```text
/plugin marketplace add /path/to/your/vantage
/plugin install vantage@vantage
```

The skills run the engine from a clone of the repository, so keep one around and point
`VANTAGE_REPO` at it if the plugin install is not itself a clone with its dependencies installed
(`uv sync --extra export`, `npm ci && npm run build`). Resolution order: `VANTAGE_REPO`, then the
plugin root, then the clone behind a `~/.claude/skills/vantage` symlink.

`bash scripts/install-skill.sh` prints these instructions. For the short `/vantage` entry point
while developing, `bash scripts/install-skill.sh --link` symlinks the project skill and command into
`~/.claude` (`--unlink` removes them; nothing is deleted without an explicit flag).

## Commands

| Command | Source | Does |
|---|---|---|
| `/vantage:generate <company> [backend] [tier]` | `skills/generate/SKILL.md` | Research and write a dossier |
| `/vantage:export <run dir or dossier>` | `skills/export/SKILL.md` | Format a finished dossier as a deck, whitepaper, PDF and HTML |
| `/vantage <company> [backend] [tier]` | `.claude/commands/vantage.md`, `.claude/skills/vantage/` | Short alias of `/vantage:generate`, available when Claude Code is opened in this repository or after `install-skill.sh --link` |

You can also just ask: "run a Vantage dossier for Example Corp", "export the example-2026-10 run
as a deck".

## /vantage:generate

1. Resolves the repository and reads your defaults (`vantage config show`).
2. Gathers the run parameters. Only the client legal name is required; the skill infers ticker,
   vertical and tier, and picks `EXECUTIVE` when you ask for a quick read.
3. Picks the backend: the configured default unless you name one. **It never adds
   `--auth api-key` on its own**; it asks first and says that the run will be billed per token.
4. Runs the dossier:
   - **`workflow` backend:** runs `harness/workflows/vantage-v3.workflow.mjs` natively with the
     **Workflow tool**, in your session, on your plan. Claude Code asks you to opt in to the
     Workflow tool the first time; accept, or the harness cannot run.
   - **Any other backend:** `uv run --project "$VANTAGE_REPO" vantage run --backend <name> …`.
5. Reports the dossier path, Overall Confidence and verification result (and says plainly when it
   is `Insufficient`), the P7R rounds and their §21.8 outcome, agents ok/total with any
   non-returning agent named, topics that stopped on budget, the top gaps, and which fields are
   `[INTERNAL REQUIRED]` because the internal inputs were not attached.

If preflight reports an **entity ambiguity**, the skill relays it instead of proceeding: researching
the wrong company thoroughly is the worst outcome the engine can produce.

## /vantage:export

1. Finds the dossier (a run directory works) and reads its title block with
   `python -m vantage.export inspect`.
2. Gathers formats, depth, HTML shape, authoring mode, output directory, classification and brand,
   asking only when the request is ambiguous ("just the deck" means `--format pptx`).
3. Runs either:
   - **agent-authored:** `harness/export/workflows/vantage-export.workflow.mjs` with the Workflow
     tool. Claude writes the narrative and the deck, document and site plans, an adversarial QA
     agent checks them, and code renders; or
   - **deterministic:** `vantage export <run> --format … --depth …`.
4. Reports every artifact with its size and slide or page count, the plan sources (`authored`,
   `scaffold`, `derived`), the dossier's Overall Confidence and verification result, every warning,
   and the classification marking.

The skill can direct the helper skills for richer collateral when they are installed (icons, brand
assets, stock imagery, diagrams, and opt-in illustrations); see [Export](export.md#visual-helpers).
It never publishes an export to a public URL.

## Running a workflow by hand

Both workflows take their inputs as JSON arguments, and the scripts pass paths, never prompt
text, so each agent reads its own brief from disk. Ask Claude Code, for example:

> Use a workflow (this is an explicit opt-in). Run the workflow at
> `harness/workflows/vantage-v3.workflow.mjs` with these args and execute it to completion:
> `{"client_legal_name": "Example Corp", "slug": "example-2026-10", "research_as_of": "2026-10-14", "output_tier": "FULL_ANNEX"}`

`research_as_of` is required because a workflow script cannot read the clock. The full argument
list (including `remediation_rounds`, `run_dir` and the internal-input gates) is in
[harness/HARNESS_README.md](../harness/HARNESS_README.md#args-contract); the export workflow's is
in [harness/export/README.md](../harness/export/README.md#args).

## Resuming and caching

A resumed Workflow run replays an agent from cache only when its prompt and options are
byte-identical to the earlier run. Two consequences:

- The shared constitution `harness/prompts/system-vantage-analyst.md` is cached across every agent.
  Editing it, even whitespace, invalidates that cache for all of them, so change it only when the
  change is the point.
- In P7R, the re-merge and re-verification prompts name every owner that ran in the round, so a
  resumed run cannot replay a merge or verdict taken before an owner it now includes.

Contributors changing how prompts are composed should read
[CONTRIBUTING.md](../CONTRIBUTING.md#changing-the-harness-safely).

## From a terminal instead

Everything the skills do is available from the CLI: `vantage run` and `vantage export`, or the
[terminal UI](tui.md). The `workflow` backend shells out to the Claude Code CLI in headless mode,
so it still runs on your plan.
