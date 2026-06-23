#!/usr/bin/env bash
# Phase 9d local preflight — primary gate for local-only Cursor loop.
# Prefers $ROOT/.venv-loop-9d/bin/python3 when executable; does not auto-install or create venv.
# Run before validate AND before approve.
set -euo pipefail

ROOT="${CURSOR_PROJECT_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
export CURSOR_PROJECT_DIR="$ROOT"
REQ="$ROOT/scripts/requirements-loop-9d.txt"

PY="python3"
VENV_PY="$ROOT/.venv-loop-9d/bin/python3"
USING_VENV=0
if [[ -x "$VENV_PY" ]]; then
  PY="$VENV_PY"
  USING_VENV=1
fi

echo "loop_9d_preflight: PY=$PY"

if [[ "$USING_VENV" -eq 1 ]]; then
  INSTALL_HINT=".venv-loop-9d/bin/pip install -r scripts/requirements-loop-9d.txt"
else
  INSTALL_HINT="pip install -r scripts/requirements-loop-9d.txt"
fi

if ! "$PY" -c "import jsonschema" 2>/dev/null; then
  echo "loop_9d_preflight: missing deps (jsonschema); run: $INSTALL_HINT" >&2
  exit 1
fi
if ! "$PY" -c "import coverage" 2>/dev/null; then
  echo "loop_9d_preflight: missing deps (coverage); run: $INSTALL_HINT" >&2
  exit 1
fi

"$PY" "$ROOT/scripts/loop_9d_coverage_check.py"
"$PY" "$ROOT/scripts/loop_9d_conformance_check.py" --strict
echo "loop_9d_preflight: ok"
