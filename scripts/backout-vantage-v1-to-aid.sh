#!/usr/bin/env bash
# backout-vantage-v1-to-aid.sh — swap the report format the engine produces.
#
#   apply    Vantage → AID.  Reinstates the pre-rename AID v3.0.0 harness from
#            harness/.superseded-aid-v3/, after stashing the current one.
#   restore  AID → Vantage.  Puts the stashed Vantage harness back.
#   status   Report which harness is installed. Changes nothing.
#
# Only harness/{blueprint,prompts,state,workflows} and the two harness docs move. No engine source
# is patched: Blueprint._resolve() accepts either filename set, and the dossier name follows the
# installed harness (<slug>-vantage.md vs <slug>-aid.md). Runs already on disk are never touched.
set -euo pipefail

REPO="${VANTAGE_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
HARNESS="$REPO/harness"
AID_SNAPSHOT="$HARNESS/.superseded-aid-v3"      # the AID v3.0.0 harness, frozen at the rename
VANTAGE_STASH="$HARNESS/.stashed-vantage"        # where `apply` parks the Vantage harness
PARTS=(blueprint prompts state workflows)
DOCS=(ARCHITECTURE.md HARNESS_README.md)

DRY=0
say()  { printf '%s\n' "$*"; }
die()  { printf 'backout: %s\n' "$*" >&2; exit 1; }
run()  { if [[ $DRY -eq 1 ]]; then printf '  [dry-run] %s\n' "$*"; else "$@"; fi; }

installed() {
  if   [[ -f "$HARNESS/blueprint/vantage-blueprint-v3.md" ]]; then echo vantage
  elif [[ -f "$HARNESS/blueprint/aid-blueprint-v3.md"     ]]; then echo aid
  else echo unknown; fi
}

# Replace harness/<parts> and the harness docs from $1, having first moved the current set to $2.
swap() {
  local from="$1" stash="$2"
  [[ -d "$from" ]] || die "source harness not found: $from"
  run rm -rf "$stash"
  run mkdir -p "$stash"
  for part in "${PARTS[@]}"; do
    [[ -d "$HARNESS/$part" ]] && run mv "$HARNESS/$part" "$stash/$part"
    run cp -R "$from/$part" "$HARNESS/$part"
  done
  for doc in "${DOCS[@]}"; do
    [[ -f "$HARNESS/$doc" ]] && run mv "$HARNESS/$doc" "$stash/$doc"
    [[ -f "$from/$doc" ]] && run cp "$from/$doc" "$HARNESS/$doc"
  done
}

cmd_status() {
  local cur; cur="$(installed)"
  say "harness dir       $HARNESS"
  say "installed report  $cur"
  case "$cur" in
    vantage) say "dossier filename  <slug>-vantage.md" ;;
    aid)     say "dossier filename  <slug>-aid.md" ;;
    *)       say "dossier filename  unknown — no recognised blueprint in $HARNESS/blueprint" ;;
  esac
  say "AID snapshot      $AID_SNAPSHOT $([[ -d $AID_SNAPSHOT ]] && echo '(present)' || echo '(MISSING — apply will fail)')"
  say "Vantage stash     $VANTAGE_STASH $([[ -d $VANTAGE_STASH ]] && echo '(present)' || echo '(none)')"
}

cmd_apply() {
  [[ "$(installed)" == "aid" ]] && { say "already on the AID report — nothing to do"; return 0; }
  say "backing out Vantage → AID v3.0.0"
  swap "$AID_SNAPSHOT" "$VANTAGE_STASH"
  say "done. Vantage harness stashed at $VANTAGE_STASH"
  say "New runs will produce <slug>-aid.md. Re-run 'vantage-engine doctor' to confirm."
}

cmd_restore() {
  [[ "$(installed)" == "vantage" ]] && { say "already on the Vantage report — nothing to do"; return 0; }
  [[ -d "$VANTAGE_STASH" ]] || die "no stashed Vantage harness at $VANTAGE_STASH (was apply ever run?)"
  say "restoring AID → Vantage"
  swap "$VANTAGE_STASH" "$AID_SNAPSHOT.reapply"
  run rm -rf "$AID_SNAPSHOT.reapply" "$VANTAGE_STASH"
  say "done. New runs will produce <slug>-vantage.md."
}

ACTION=""
for arg in "$@"; do
  case "$arg" in
    apply|restore|status) ACTION="$arg" ;;
    --dry-run)            DRY=1 ;;
    -h|--help)            sed -n '2,12p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *)                    die "unknown argument: $arg (expected apply | restore | status [--dry-run])" ;;
  esac
done
[[ -n "$ACTION" ]] || { sed -n '2,12p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 2; }
[[ -d "$HARNESS" ]] || die "harness dir not found: $HARNESS"
"cmd_$ACTION"
