#!/usr/bin/env bash
# Agentic Loop Engineering Kit — repo-adaptive build (Gradle preferred for cellcp)
set -euo pipefail

REPO="${1:?usage: gradle-build.sh <repo-path>}"
ROOT="${CURSOR_PROJECT_DIR:-$(cd "$(dirname "$0")/../../../.." && pwd)}"
cd "$ROOT/$REPO"

if [[ -f "./gradlew" ]]; then
  chmod +x ./gradlew 2>/dev/null || true
  ./gradlew clean build
elif [[ -f "./mvnw" ]]; then
  chmod +x ./mvnw 2>/dev/null || true
  ./mvnw clean verify
else
  echo "ERROR: no gradlew or mvnw in $REPO" >&2
  exit 1
fi
