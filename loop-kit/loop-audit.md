---
title: loop-audit adapter — CDP Cursor paths
source: codex_l3_plan_sync
created: 2026-06-23
---

# loop-audit adapter (CDP)

[`@cobusgreyling/loop-audit`](https://www.npmjs.com/package/@cobusgreyling/loop-audit) scores loop maturity from repo layout and activity. **Score is advisory** — CDP gates live in [`GATES.md`](GATES.md) and Phase 9d `LOOP_LEARNING_RESULT` codes.

## Tooling: Cursor only

This workspace uses **Cursor** (`.cursor/skills/`). **Do not** install or maintain `.grok/skills/*` — that layout is from loop-audit starters only.

**Do not** run `cp -r starters/minimal-loop/*` — it would overwrite stronger CDP assets.

## Why triage / verifier show as missing

loop-audit scans starter paths (`.grok/`, `.claude/`, `.codex/`) — **not** `.cursor/skills/`. A score like **88/100 L1** with “No triage skill” / “No loop-verifier skill” is a **false negative** when CDP skills exist under Cursor paths.

## CDP skill mapping

| loop-audit expects | CDP equivalent (Cursor) |
|--------------------|-------------------------|
| `loop-triage` skill | [`.cursor/skills/loop-triage/SKILL.md`](../../.cursor/skills/loop-triage/SKILL.md) |
| `loop-verifier` | [`.cursor/skills/loop-verifier/SKILL.md`](../../.cursor/skills/loop-verifier/SKILL.md) |
| `loop-budget` | [`.cursor/skills/loop-budget/SKILL.md`](../../.cursor/skills/loop-budget/SKILL.md) |
| Agent loop runbook | [`.cursor/skills/agentic-loop/SKILL.md`](../../.cursor/skills/agentic-loop/SKILL.md) |
| Orchestrator | [`.cursor/agents/agentic-loop-orchestrator.md`](../../.cursor/agents/agentic-loop-orchestrator.md) |
| `STATE.md` | [`loop-kit/STATE.md`](STATE.md) (symlinked at repo root) |
| Loop activity | [`loop-run-log.md`](loop-run-log.md) + `update-loop-state.sh` |
| Maker / checker | Phase 4 `loop-verifier` + Phase 5 `@pr-code-review` |

## Local enforcement (primary)

Phase 9d is enforced **locally** in Cursor:

1. `scripts/loop_9d_preflight.sh` before validate and again before approve
2. Two-step apply: `PENDING_APPROVAL` → human STOP → `APPLY_SUCCESS` / `IDEMPOTENT_SKIP`
3. Canonical run-log tokens — see [`LOOP.md`](LOOP.md)

[`.github/workflows/loop-9d-checks.yml`](../../.github/workflows/loop-9d-checks.yml) is an **optional mirror** when the workspace is shared in git. It is never required for local-only usage.

## TOON expansion (frozen)

TOON contract expansion remains **frozen** until Phase 9d has stable repeated local runs (multiple L2/L3 cycles with preflight green). First candidate after stability: gate-evaluation contract (`GATE_PHASE4_JACOCO`, etc.).

## Refresh evidence

1. Run an L2 or L3 loop on a locked pilot ticket (e.g. `PROJ-153` / `cell-health`).
2. Update [`STATE.md`](STATE.md) and append [`loop-run-log.md`](loop-run-log.md) (include Phase 9d `LOOP_LEARNING_RESULT` sequences when applicable).
3. Re-run from workspace root:

```bash
npx @cobusgreyling/loop-audit . --suggest
```

Activity rows in `loop-run-log.md` improve the activity dimension; triage/verifier warnings may persist until upstream loop-audit adds `.cursor/skills/` scanning.

## CDP L3 vs loop-audit L3

| Concept | Meaning |
|---------|---------|
| **CDP L2** | Phases 0–8 with human gates |
| **CDP Phase 9d** | `PENDING_APPROVAL` → STOP → human `approve` |
| **CDP L3-push** | Phase 6 ship: push + babysit CI (≤3); explicit user “push” approval |
| **loop-audit score** | Maturity metric only — not authorization to skip CDP gates |

## Related

- [`LOOP.md`](LOOP.md) — catalog and pilot checklist
- [`contracts/README.md`](contracts/README.md) — Phase 9d result codes
- [`.cursor/skills/loop-self-improvement/SKILL.md`](../../.cursor/skills/loop-self-improvement/SKILL.md)
