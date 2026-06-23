#!/usr/bin/env bash
# Agentic Loop Engineering Kit — optional local act run (dry-run friendly)
set -euo pipefail

REPO="${1:-.}"
EVENT="${2:-pull_request}"
ROOT="${CURSOR_PROJECT_DIR:-$(cd "$(dirname "$0")/../../../.." && pwd)}"
cd "$ROOT/$REPO"

if ! command -v act >/dev/null 2>&1; then
  echo "SKIP: act not installed" >&2
  exit 0
fi

act -n -j build-and-test -e "$EVENT" 2>/dev/null || act -l
