#!/usr/bin/env bash
# Agentic Loop Engineering Kit — append run-log line and touch state file
set -euo pipefail

PROFILE="${1:?usage: update-loop-state.sh <profile> <phase> <outcome> [jira-or-incident]}"
PHASE="${2:?}"
OUTCOME="${3:?}"
TARGET="${4:-}"
ROOT="${CURSOR_PROJECT_DIR:-$(cd "$(dirname "$0")/../../../.." && pwd)}"
LOG="$ROOT/loop-kit/loop-run-log.md"
DATE=$(date +%Y-%m-%d)
TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)

mkdir -p "$ROOT/loop-kit"
if [[ ! -f "$LOG" ]]; then
  echo "# Loop run log" > "$LOG"
  echo "" >> "$LOG"
  echo "| date | profile | phase | target | outcome |" >> "$LOG"
  echo "|------|---------|-------|--------|---------|" >> "$LOG"
fi

echo "| $DATE | $PROFILE | $PHASE | $TARGET | $OUTCOME |" >> "$LOG"

STATE="$ROOT/loop-kit/${PROFILE}-state.md"
if [[ -f "$STATE" ]]; then
  # touch last_updated in frontmatter if present
  if grep -q '^last_updated:' "$STATE" 2>/dev/null; then
    sed -i.bak "s/^last_updated:.*/last_updated: $TS/" "$STATE" && rm -f "${STATE}.bak"
  fi
fi

echo "Logged: profile=$PROFILE phase=$PHASE outcome=$OUTCOME"
