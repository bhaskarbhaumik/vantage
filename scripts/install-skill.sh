#!/usr/bin/env bash
# Symlink the vantage skill + command into ~/.claude so Claude Code can use them.
set -euo pipefail
REPO="${VANTAGE_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"

mkdir -p "$HOME/.claude/skills" "$HOME/.claude/commands"
ln -sfn "$REPO/.claude/skills/vantage" "$HOME/.claude/skills/vantage"
ln -sf  "$REPO/.claude/commands/vantage.md" "$HOME/.claude/commands/vantage.md"

echo "linked skill   -> ~/.claude/skills/vantage  ->  $REPO/.claude/skills/vantage"
echo "linked command -> ~/.claude/commands/vantage.md"
