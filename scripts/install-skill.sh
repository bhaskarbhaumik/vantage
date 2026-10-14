#!/usr/bin/env bash
# Install Vantage into Claude Code.
#
#   scripts/install-skill.sh               print the plugin install instructions (recommended)
#   scripts/install-skill.sh --link        symlink the /vantage skill + command into ~/.claude (local dev)
#   scripts/install-skill.sh --unlink      remove those symlinks (only if they point into this repo)
#   scripts/install-skill.sh --list-stale  list dangling symlinks in ~/.claude/skills (read-only)
#   scripts/install-skill.sh --remove NAME remove the symlink ~/.claude/skills/NAME (never a real directory)
#
# Nothing is ever deleted without an explicit --unlink or --remove.
set -euo pipefail

REPO="${VANTAGE_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)}"
CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
SKILLS_DIR="$CLAUDE_DIR/skills"
COMMANDS_DIR="$CLAUDE_DIR/commands"

usage() { sed -n '2,10p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; }

print_plugin_instructions() {
  cat <<'EOF'
Install Vantage as a Claude Code plugin (recommended). Inside Claude Code run:

  /plugin marketplace add bhaskarbhaumik/vantage
  /plugin install vantage@vantage

That adds /vantage:generate (produce a dossier) and /vantage:export (decks, documents, PDFs and
microsites from a finished dossier).

To test a local clone instead, add it as a marketplace by path:

  /plugin marketplace add /path/to/your/vantage/clone

For the short /vantage skill and command while developing, run:

  scripts/install-skill.sh --link
EOF
}

# Resolve a path's symlink target to an absolute path (portable: macOS has no readlink -f by default).
resolve() {
  local target
  target="$(readlink "$1")"
  case "$target" in
    /*) printf '%s\n' "$target" ;;
    *) printf '%s/%s\n' "$(cd "$(dirname "$1")" && pwd -P)" "$target" ;;
  esac
}

link() {
  mkdir -p "$SKILLS_DIR" "$COMMANDS_DIR"
  for dest in "$SKILLS_DIR/vantage" "$COMMANDS_DIR/vantage.md"; do
    if [ -e "$dest" ] && [ ! -L "$dest" ]; then
      echo "refusing to replace $dest: it exists and is not a symlink" >&2
      exit 1
    fi
  done
  ln -sfn "$REPO/.claude/skills/vantage" "$SKILLS_DIR/vantage"
  ln -sfn "$REPO/.claude/commands/vantage.md" "$COMMANDS_DIR/vantage.md"
  echo "linked skill   $SKILLS_DIR/vantage -> $REPO/.claude/skills/vantage"
  echo "linked command $COMMANDS_DIR/vantage.md -> $REPO/.claude/commands/vantage.md"
  echo
  echo "The plugin skills (/vantage:generate, /vantage:export) come from the plugin install:"
  echo "  /plugin marketplace add $REPO"
  echo "  /plugin install vantage@vantage"
}

unlink_repo_links() {
  local dest removed=0
  for dest in "$SKILLS_DIR/vantage" "$COMMANDS_DIR/vantage.md"; do
    if [ -L "$dest" ]; then
      case "$(resolve "$dest")" in
        "$REPO"/*) rm "$dest"; echo "removed $dest"; removed=1 ;;
        *) echo "left $dest: it points outside $REPO" ;;
      esac
    fi
  done
  [ "$removed" = 1 ] || echo "nothing to remove"
}

list_stale() {
  local entry found=0
  [ -d "$SKILLS_DIR" ] || { echo "no $SKILLS_DIR"; return 0; }
  for entry in "$SKILLS_DIR"/*; do
    if [ -L "$entry" ] && [ ! -e "$entry" ]; then
      echo "stale: $(basename "$entry") -> $(readlink "$entry")"
      found=1
    fi
  done
  if [ "$found" = 1 ]; then
    echo
    echo "Remove one with: scripts/install-skill.sh --remove <name>"
  else
    echo "no dangling skill symlinks in $SKILLS_DIR"
  fi
}

remove_named() {
  local name="$1" dest
  case "$name" in
    ""|*/*|.|..) echo "invalid skill name: '$name'" >&2; exit 2 ;;
  esac
  dest="$SKILLS_DIR/$name"
  if [ -L "$dest" ]; then
    echo "removing symlink $dest -> $(readlink "$dest")"
    rm "$dest"
  elif [ -e "$dest" ]; then
    echo "refusing to remove $dest: it is not a symlink" >&2
    exit 1
  else
    echo "no $dest"
  fi
}

case "${1:-}" in
  "") print_plugin_instructions ;;
  --link) link ;;
  --unlink) unlink_repo_links ;;
  --list-stale) list_stale ;;
  --remove) shift; remove_named "${1:-}" ;;
  -h|--help) usage ;;
  *) echo "unknown option: $1" >&2; usage >&2; exit 2 ;;
esac
