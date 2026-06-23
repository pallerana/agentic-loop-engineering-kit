#!/usr/bin/env bash
# Agentic Loop Engineering Kit — append loop outcome hint to wiki log when loop state was touched
set -euo pipefail

ROOT="${CURSOR_PROJECT_DIR:-.}"
LOG="$ROOT/loop-kit/loop-run-log.md"
WIKI_LOG="$ROOT/docs/wiki/log.md"
DATE=$(date +%Y-%m-%d)

# Only append if loop-run-log was updated today and wiki log lacks today's loop entry
if [[ -f "$LOG" ]] && grep -q "$DATE" "$LOG" 2>/dev/null; then
  if [[ -f "$WIKI_LOG" ]] && ! grep -q "$DATE.*agent-loop" "$WIKI_LOG" 2>/dev/null; then
    LAST=$(grep "| $DATE |" "$LOG" | tail -1 | sed 's/|/ /g' | awk '{$1=$1; print $0}')
    echo "$DATE | agent-loop | session end — see loop-run-log: $LAST" >> "$WIKI_LOG"
  fi
fi

echo '{}'
