#!/usr/bin/env bash
# Agentic Loop Engineering Kit — optional Jira close-the-loop comment (requires jira-cli or Atlassian MCP in agent)
set -euo pipefail

JIRA_KEY="${1:?usage: jira-close-loop.sh <JIRA-KEY> <PR-url> <commit-sha> [test-names]}"
PR_URL="${2:?}"
SHA="${3:?}"
TESTS="${4:-see PR description}"

COMMENT="Agentic Loop Engineering Kit close-the-loop

PR: $PR_URL
Commit: $SHA
Tests: $TESTS

Automated comment from agentic-loop Phase 8."

if command -v jira-cli >/dev/null 2>&1; then
  jira-cli jira workitem comment create --key "$JIRA_KEY" --body "$COMMENT" && exit 0
fi

echo "POST comment to $JIRA_KEY (jira-cli not available — use Atlassian MCP):"
echo "$COMMENT"
exit 0
