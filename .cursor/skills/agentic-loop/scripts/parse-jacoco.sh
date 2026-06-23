#!/usr/bin/env bash
# Agentic Loop Engineering Kit — parse JaCoCo HTML report; compare line ratio to threshold
set -euo pipefail

REPO="${1:?usage: parse-jacoco.sh <repo-path> [min-ratio]}"
MIN_RATIO="${2:-0.80}"
ROOT="${CURSOR_PROJECT_DIR:-$(cd "$(dirname "$0")/../../../.." && pwd)}"
REPORT="$ROOT/$REPO/build/reports/jacoco/jacocoTestReport/jacocoTestReport.xml"

if [[ ! -f "$REPORT" ]]; then
  # fallback: index.html table parse
  HTML="$ROOT/$REPO/build/reports/jacoco/jacocoTestReport/index.html"
  if [[ -f "$HTML" ]]; then
    # Extract "Total" row missed/covered from standard JaCoCo HTML
    LINE=$(grep -A2 'Total</td>' "$HTML" | tail -1 || true)
    if [[ -n "$LINE" ]]; then
      MISSED=$(echo "$LINE" | sed -n 's/.*>\([0-9,]*\)<.*>\([0-9,]*\)<.*/\1/p' | tr -d ',')
      COVERED=$(echo "$LINE" | sed -n 's/.*>\([0-9,]*\)<.*>\([0-9,]*\)<.*/\2/p' | tr -d ',')
      if [[ -n "$MISSED" && -n "$COVERED" ]]; then
        TOTAL=$((MISSED + COVERED))
        if [[ "$TOTAL" -gt 0 ]]; then
          RATIO=$(awk "BEGIN {printf \"%.4f\", $COVERED / $TOTAL}")
          echo "JaCoCo line ratio: $RATIO (min $MIN_RATIO)"
          awk "BEGIN {exit !($RATIO >= $MIN_RATIO)}"
          exit $?
        fi
      fi
    fi
  fi
  echo "WARN: JaCoCo report not found at $REPORT — skipping ratio gate" >&2
  exit 0
fi

# XML: counter type=LINE missed= covered=
MISSED=$(grep 'counter type="LINE"' "$REPORT" | tail -1 | sed -n 's/.*missed="\([0-9]*\)".*/\1/p')
COVERED=$(grep 'counter type="LINE"' "$REPORT" | tail -1 | sed -n 's/.*covered="\([0-9]*\)".*/\1/p')
TOTAL=$((MISSED + COVERED))
if [[ "$TOTAL" -eq 0 ]]; then
  echo "WARN: no LINE counters in JaCoCo XML" >&2
  exit 0
fi
RATIO=$(awk "BEGIN {printf \"%.4f\", $COVERED / $TOTAL}")
echo "JaCoCo line ratio: $RATIO (min $MIN_RATIO)"
awk "BEGIN {exit !($RATIO >= $MIN_RATIO)}"
