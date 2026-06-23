#!/usr/bin/env bash
# Agentic Loop Engineering Kit — block edits to denylisted paths (secrets, prod deploy)
set -euo pipefail

INPUT=$(cat)
FILE=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('file_path',''))" 2>/dev/null || echo "")

DENYLIST=(
  '.env'
  'credentials.json'
  'secrets.'
  '/prod/'
  'deploy-prod'
  '.github/workflows/deploy'
  'kubeconfig'
)

for pat in "${DENYLIST[@]}"; do
  if echo "$FILE" | grep -qi "$pat"; then
    echo "{\"decision\":\"block\",\"reason\":\"Agentic Loop Engineering Kit: denylisted path $FILE — human gate required\"}"
    exit 0
  fi
done

echo '{"decision":"allow"}'
