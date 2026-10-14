---
name: vantage
description: >-
  Produce a Vantage dossier (Verified Account Navigator: Targeting, Analysis & GTM Engine) for a
  target company using the multi-agent, multi-backend Vantage engine. Use whenever the user asks
  to "run a Vantage dossier", "build an account research dossier", "research company X for the
  pursuing organization", "produce a pursuit dossier", or names a company to profile for account
  strategy. Short alias of the plugin skill /vantage:generate; for decks, documents, PDFs and
  microsites from a finished dossier use /vantage:export.
argument-hint: <company legal name> [backend] [tier]
---

# /vantage: generate a Vantage dossier

This is the short `/vantage` entry point. It behaves exactly like the plugin skill
`/vantage:generate`, whose instructions are the single source of truth.

User request / target: $ARGUMENTS

1. Resolve the repo:

   ```bash
   VANTAGE_REPO="${VANTAGE_REPO:-}"
   if [ -z "$VANTAGE_REPO" ] && [ -d "$PWD/harness" ] && [ -f "$PWD/skills/generate/SKILL.md" ]; then
     VANTAGE_REPO="$PWD"
   fi
   if [ -z "$VANTAGE_REPO" ] && [ -e "$HOME/.claude/skills/vantage" ]; then
     VANTAGE_REPO="$(cd -P "$HOME/.claude/skills/vantage/../../.." && pwd -P)"
   fi
   [ -f "$VANTAGE_REPO/skills/generate/SKILL.md" ] || echo "set VANTAGE_REPO to your Vantage clone"
   ```

2. Read `$VANTAGE_REPO/skills/generate/SKILL.md` in full and follow it step by step, with
   `$VANTAGE_REPO` already resolved and `$ARGUMENTS` as the user request.

Non-negotiables, in case the generate skill cannot be read:

- Ask only for a missing client legal name; infer everything else.
- Never add `--auth api-key` on your own initiative. It switches the run from the user's Claude
  subscription to metered API billing. Ask first.
- Relay an entity ambiguity from preflight instead of proceeding past it.
- Never invent facts about the pursuing organization.
