---
name: loop-verifier
description: >-
  Agentic Loop Engineering Kit Phase 4 maker/checker — gradle build, JaCoCo, diff coverage, ce-testing-reviewer.
  Never same model as implementer for the same diff.
---

# Loop Verifier

Maker/checker **verify** pass for Agentic Loop Engineering Kit Phase 4.

**Runbook:** [`.cursor/skills/agentic-loop/SKILL.md`](../agentic-loop/SKILL.md) Phase 4.

## Hard rules

- Run only **after human approves** Phase 3 implementation
- **Different model/persona** than implementer for the same diff
- Present results in Plan mode; do not auto-re-dispatch Failure Router

## Verify steps

From profile repo (or `--repo`):

```bash
.cursor/skills/agentic-loop/scripts/gradle-build.sh <repo-path>
.cursor/skills/agentic-loop/scripts/parse-jacoco.sh <repo-path> <jacoco_line_ratio>
```

- Profile E2E script if defined
- Delta coverage: changed production lines need tests
- `ce-testing-reviewer` against Phase 1 test matrix

## On failure

Classify per [`GATES.md`](../../../loop-kit/GATES.md) Failure Router — **recommend** restart phase, wait for human:

| Signal | Recommend |
|--------|-----------|
| JaCoCo / delta | Phase 4 test-repair → 3 |
| Local build fail | Phase 3 |
| 2+ arch failures | Phase 1 |

## Agent form

Optional dedicated agent: [`.cursor/agents/loop-verifier.md`](../../agents/loop-verifier.md)
