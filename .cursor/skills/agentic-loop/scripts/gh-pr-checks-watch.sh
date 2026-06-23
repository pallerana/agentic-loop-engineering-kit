#!/usr/bin/env bash
# Agentic Loop Engineering Kit — watch GitHub PR checks until all pass or timeout
set -euo pipefail

PR="${1:?usage: gh-pr-checks-watch.sh <pr-number> [repo] [max-wait-sec]}"
REPO="${2:-}"
MAX_WAIT="${3:-1800}"
INTERVAL=30
ELAPSED=0

ARGS=(pr checks "$PR" --watch)
if [[ -n "$REPO" ]]; then
  ARGS+=(--repo "$REPO")
fi

while [[ "$ELAPSED" -lt "$MAX_WAIT" ]]; do
  if gh pr checks "$PR" ${REPO:+--repo "$REPO"} 2>/dev/null | grep -qE 'fail|pending'; then
    sleep "$INTERVAL"
    ELAPSED=$((ELAPSED + INTERVAL))
    continue
  fi
  if gh pr checks "$PR" ${REPO:+--repo "$REPO"} 2>/dev/null | grep -qvE 'pass|skipping'; then
    sleep "$INTERVAL"
    ELAPSED=$((ELAPSED + INTERVAL))
    continue
  fi
  echo "PR #$PR checks green"
  exit 0
done

echo "TIMEOUT: PR #$PR checks not green after ${MAX_WAIT}s" >&2
gh pr checks "$PR" ${REPO:+--repo "$REPO"} || true
exit 1
