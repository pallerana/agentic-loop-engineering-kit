#!/usr/bin/env bash
# Phase 9d — apply TOON loop-learning contract (wrapper)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${CURSOR_PROJECT_DIR:-$(cd "$SCRIPT_DIR/../../../.." && pwd)}"
export CURSOR_PROJECT_DIR="$ROOT"

IMPORT_ERROR_STDERR="validation error: jsonschema not installed; run: pip install -r scripts/requirements-loop-9d.txt"

CONTRACT=""
REPO=""
DRY_RUN=""
DECISION=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --contract)
      CONTRACT="$2"
      shift 2
      ;;
    --repo)
      REPO="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN="--dry-run"
      shift
      ;;
    approve|reject)
      DECISION="$1"
      shift
      ;;
    *)
      echo "unknown arg: $1" >&2
      exit 1
      ;;
  esac
done

if [[ -z "$CONTRACT" ]]; then
  echo "usage: apply-loop-learning.sh --contract <path> [--repo <repo>] [--dry-run] [approve|reject]" >&2
  exit 1
fi

use_jsonschema=true
if [[ -n "${LOOP_TOON_VALIDATOR:-}" ]]; then
  toon_bin="${LOOP_TOON_VALIDATOR%% *}"
  if command -v "$toon_bin" &>/dev/null || [[ -x "$toon_bin" ]]; then
    use_jsonschema=false
  fi
elif command -v toon &>/dev/null && toon validate --version &>/dev/null 2>&1; then
  use_jsonschema=false
fi

if [[ "$use_jsonschema" == true ]] && ! python3 -c "import jsonschema" 2>/dev/null; then
  echo "$IMPORT_ERROR_STDERR" >&2
  echo "LOOP_LEARNING_RESULT=SCHEMA_INVALID"
  exit 1
fi

ARGS=(--contract "$CONTRACT")
[[ -n "$REPO" ]] && ARGS+=(--repo "$REPO")
[[ -n "$DRY_RUN" ]] && ARGS+=("$DRY_RUN")
[[ -n "$DECISION" ]] && ARGS+=("$DECISION")

exec python3 "$SCRIPT_DIR/apply_loop_learning.py" "${ARGS[@]}"
