#!/usr/bin/env bash
# Agentic Loop Engineering Kit — block dangerous git operations
set -euo pipefail

INPUT=$(cat)
CMD=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('command',''))" 2>/dev/null || echo "")

BLOCK_PATTERNS=(
  'git push.*--force'
  'git push -f'
  'git push origin main'
  'git push origin master'
  'git reset --hard'
  'git clean -fd'
  'git checkout main'
  'git checkout master'
)

for pat in "${BLOCK_PATTERNS[@]}"; do
  if echo "$CMD" | grep -qiE "$pat"; then
    echo '{"decision":"block","reason":"Agentic Loop Engineering Kit: dangerous git operation blocked by block-dangerous-git.sh"}'
    exit 0
  fi
done

echo '{"decision":"allow"}'
