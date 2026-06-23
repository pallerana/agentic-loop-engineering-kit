---
name: loop-self-improvement
description: >-
  Phase 9d self-improvement — extract loop learnings, emit TOON contract JSON,
  invoke apply-loop-learning.sh. L2/L3 only; human-gated.
---

# Loop Self-Improvement (Phase 9d)

Extract durable **agent-facing** learnings from a completed loop run. Do **not** update wiki (that's Phase 9c `ce-compound`).

## When to run

- Profile has `self_improvement: true` (or rationale-only fallback for `--repo` without named profile)
- Loop completed Phases 1–8 at L2/L3
- L1 loops **skip** 9d → orchestrator ends 9d with `NO_LEARNINGS` / skip (no contract emitted)

Emit `NO_LEARNINGS` when:

- L1 mode
- `self_improvement: false` on profile
- Duplicate fingerprint with no new insight vs existing pattern/quirk
- No durable agent-facing learning from the run

## Inputs

- Active profile YAML (`pattern_doc`, `known_quirks`, `repos`)
- Active `--repo` path
- JIRA key, PR URL, test names, failure router signals from the run
- `docs/loop-learnings/README.md` index (fingerprint run counts)

## Scope routing

| Scope | Min runs | Contract mode | Target |
|-------|----------|---------------|--------|
| Single repo | 1 | `loop_learning` | `pattern_doc` append + `upsert_known_quirk` |
| `context_skill` | 2+ (1 if Phase 8 AC→test map) | `promotion_proposal` | e.g. `cell-health-mvp/SKILL.md` |
| Profile family | 2+ | `promotion_proposal` | `springboot-default.yaml` |
| Spring Boot all | 5+ | `promotion_proposal` | `java-springboot-standards.mdc` |
| Ops | 1 | `loop_learning` | `ops-incident-patterns.md` |
| PR review | 2+ | `promotion_proposal` | `pr-code-review.mdc` |
| No profile | n/a | `loop_learning` | rationale only (`targets: []`) |

## Output (TOON contract)

Emit one shared `<UTC-ts>` = `YYYYMMDDTHHMMSSZ` per run.

1. **Rationale:** `docs/loop-learnings/by-repo/<repo>/<JIRA-KEY>-<UTC-ts>.md`
2. **Learning contract:** `docs/loop-learnings/contracts/<repo>/<JIRA-KEY>-<UTC-ts>-learning.json`
3. **Promotion (if threshold met):** `docs/loop-learnings/pending-promotion/<scope>/<JIRA-KEY>-<UTC-ts>-promotion.json`

### Example `loop_learning` contract

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

## Apply (two-step — mandatory)

Install deps once per venv: `pip install -r scripts/requirements-loop-9d.txt`

**Step 0a — preflight (before validate):**

```bash
export CURSOR_PROJECT_DIR="$(pwd)"
./scripts/loop_9d_preflight.sh
```

Must print `loop_9d_preflight: ok`. Fail closed — do not validate if preflight fails.

**Step 1 — validate (no approve):**

```bash
.cursor/skills/agentic-loop/scripts/apply-loop-learning.sh \
  --contract docs/loop-learnings/contracts/<repo>/<JIRA>-<UTC-ts>-learning.json \
  --repo <repo>
```

Expect `LOOP_LEARNING_RESULT=PENDING_APPROVAL` and staging summary at `docs/loop-learnings/staging/<JIRA>-<UTC-ts>-summary.md`. Present summary table to human; **STOP**.

**Step 2a — preflight (before approve; same script as 0a):**

```bash
./scripts/loop_9d_preflight.sh
```

**Step 2 — apply (after explicit user approval only):**

```bash
.cursor/skills/agentic-loop/scripts/apply-loop-learning.sh \
  --contract docs/loop-learnings/contracts/<repo>/<JIRA>-<UTC-ts>-learning.json \
  --repo <repo> approve
```

Optional preview: add `--dry-run` to step 1 — also returns `PENDING_APPROVAL` (not `APPLY_SUCCESS`).

### Summary template (present at STOP)

| Field | Value |
|-------|-------|
| jira_key | … |
| mode | … |
| fingerprint | … |
| scope | … |
| repo | … |
| run | … |
| contract | path |
| targets | count |
| actions | count |

Parse result: `LOOP_LEARNING_RESULT=<CODE>`.

### Run-log token (canonical — append via `update-loop-state.sh`)

```text
9d-preflight: ok | 9d: PENDING_APPROVAL → APPLY_SUCCESS | staging=<path> | branch=<name>
```

If coverage allowlist active, append `| allowlist=<line>:<reason>:<YYYY-MM-DD>` on the same row.

## Dual-contract order

1. Apply `-learning.json` first
2. Stage `-promotion.json` only after `APPLY_SUCCESS` or `IDEMPOTENT_SKIP`

## Rules

- Detail → `pattern_doc`; one-line summary → profile `known_quirks` (max 5)
- Marker: `LOOP-LEARNING:<fingerprint>:<run>` (≤20 lines inside block)
- No wiki writes; no full YAML rewrites in v1
- Fingerprint = slug of learning title; increment `runs` in learnings index on approve

## References

- [`loop-kit/contracts/README.md`](../../../loop-kit/contracts/README.md)
- [`loop-kit/contracts/loop-learning-v1.schema.json`](../../../loop-kit/contracts/loop-learning-v1.schema.json)
- [`docs/loop-learnings/README.md`](../../../docs/loop-learnings/README.md)
