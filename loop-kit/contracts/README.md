# Loop learning contracts (TOON v1)

JSON contracts for Phase 9d self-improvement. Schema: [`loop-learning-v1.schema.json`](./loop-learning-v1.schema.json).

## Runtime validation

TOON defines contract **shape**; a runtime engine enforces the schema file at apply time.

**Validator selection (in order):**

1. `LOOP_TOON_VALIDATOR` env — executable command if set
2. `toon validate --version` on PATH succeeds → use `toon validate`
3. **Default:** `jsonschema` against `loop-learning-v1.schema.json`

Install default path: `pip install -r scripts/requirements-loop-9d.txt`

Do **not** invoke a TOON CLI unless a supported validator is detected.

## Modes

| Mode | v1 apply |
|------|----------|
| `loop_learning` | Auto-apply markdown append + `upsert_known_quirk` (human approve) |
| `promotion_proposal` | Stage to `docs/loop-learnings/pending-promotion/<scope>/` only |

## Error codes

Apply script prints `LOOP_LEARNING_RESULT=<CODE>`:

| Code | Exit | Meaning |
|------|------|---------|
| `PENDING_APPROVAL` | 0 | Validation passed; awaiting human approve (`--dry-run` also returns this) |
| `APPLY_SUCCESS` | 0 | Applied or staged after `approve` |
| `IDEMPOTENT_SKIP` | 0 | Marker already present |
| `NO_LEARNINGS` | 0 | Skill/orchestrator: no 9d contract to apply |
| `SCHEMA_INVALID` | 1 | Schema validation failed (incl. missing `jsonschema`) |
| `PATH_NOT_ALLOWED` | 2 | Path outside allowlist |
| `REPO_MISMATCH` | 3 | `contract.repo` ≠ active `--repo` |
| `RATIONALE_MISSING` | 4 | Rationale file missing |
| `ORPHAN_PROMOTION` | 5 | Promotion without sibling `-learning.json` |
| `LEARNING_NOT_APPLIED` | 6 | Promotion before learning applied |
| `USER_REJECTED` | 0 | Human rejected |

## Path allowlist

- `loop-kit/`
- `.cursor/skills/`
- `.cursor/rules/`
- `docs/loop-learnings/`

`docs/wiki/` is **not** writable by 9d (Phase 9c only).

## Marker schema

`LOOP-LEARNING:<fingerprint>:<run>` — independent of contract serialization.

## Dual-contract order

1. Apply `...-<UTC-ts>-learning.json`
2. Stage `...-<UTC-ts>-promotion.json` only after step 1 returns `APPLY_SUCCESS` or `IDEMPOTENT_SKIP`

## Example `loop_learning` contract

```json
{
  "contract_version": "1",
  "mode": "loop_learning",
  "jira_key": "PROJ-153",
  "fingerprint": "jacoco-cosmos-sdk-exclusion",
  "scope": "single-repo",
  "profile": "cell-health",
  "repo": "your-service-cell-health-aggregator",
  "rationale_path": "docs/loop-learnings/by-repo/your-service-cell-health-aggregator/PROJ-153-20260623T161430Z.md",
  "targets": [
    {
      "path": "loop-kit/patterns/cell-health-patterns.md",
      "action": "append_markdown",
      "subsection": "Known Quirks (aggregator)",
      "lines": [
        "JaCoCo gate fails when Cosmos SDK internals measured; exclude com.azure.cosmos.* SDK classes."
      ]
    }
  ],
  "actions": [
    {
      "action": "upsert_known_quirk",
      "profile": "cell-health",
      "summary": "JaCoCo: exclude Cosmos SDK internals from measured scope"
    }
  ]
}
```

## Schema file (copy to `loop-learning-v1.schema.json`)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "loop-learning-v1.schema.json",
  "title": "Loop Learning Contract v1",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "contract_version", "mode", "jira_key", "fingerprint", "scope",
    "profile", "repo", "rationale_path", "targets", "actions"
  ],
  "properties": {
    "contract_version": { "const": "1" },
    "mode": { "enum": ["loop_learning", "promotion_proposal"] },
    "jira_key": { "type": "string", "pattern": "^[A-Z]+-[0-9]+$" },
    "fingerprint": { "type": "string", "pattern": "^[a-z0-9-]+$" },
    "scope": {
      "enum": ["single-repo", "profile-family", "context_skill", "springboot-all", "ops", "pr-review"]
    },
    "profile": { "type": "string" },
    "repo": { "type": "string" },
    "rationale_path": { "type": "string", "pattern": "^docs/loop-learnings/" },
    "min_runs": { "type": "integer", "minimum": 1 },
    "runs": { "type": "integer", "minimum": 0 },
    "targets": { "type": "array", "items": { "$ref": "#/$defs/target" } },
    "actions": { "type": "array", "items": { "$ref": "#/$defs/action" } }
  },
  "$defs": {
    "allowedPath": {
      "type": "string",
      "pattern": "^(loop-kit/|\\.cursor/skills/|\\.cursor/rules/|docs/loop-learnings/)"
    },
    "target": {
      "type": "object",
      "additionalProperties": false,
      "required": ["path", "action"],
      "properties": {
        "path": { "$ref": "#/$defs/allowedPath" },
        "action": { "enum": ["append_markdown"] },
        "subsection": { "type": "string" },
        "lines": { "type": "array", "items": { "type": "string" }, "maxItems": 20 },
        "note": { "type": "string" }
      }
    },
    "action": {
      "type": "object",
      "additionalProperties": false,
      "required": ["action", "profile", "summary"],
      "properties": {
        "action": { "enum": ["upsert_known_quirk"] },
        "profile": { "type": "string" },
        "summary": { "type": "string", "maxLength": 200 }
      }
    }
  }
}
```
