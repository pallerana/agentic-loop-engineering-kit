# Agentic Loop Engineering Kit — Catalog

Loop Engineering OS for your monorepo repos and ops incidents.

## Loops

| Loop | Profile | Default mode | Entry |
|------|---------|--------------|-------|
| Feature (generic) | `springboot-default` | L1 | `/agentic-loop --profile springboot-default --repo <path> JIRA` |
| Cell Health MVP | `cell-health` | L1 | ` PROJ-153` |
| Ops incident | `ops-incident` | L1 | `/agentic-loop --profile ops-incident --pagerduty INC-…` |

## Repo matrix

| Profile | Repos | JaCoCo | Notes |
|---------|-------|--------|-------|
| `cell-health` | aggregator, central | 1.00 | E2E, Event Hub, Cosmos |
| `cellassignments` | assignments API | 0.80 | |
| `cellrouter` | http cell router | 0.80 | |
| `cellmigrator` | cell migrator | 0.80 | |
| `celldiscovery` | cell discovery | 0.80 | |
| `cellpersistence` | ODP cell persistence API | 0.80 | Cosmos per-type containers |
| `springboot-default` | any `--repo` | 0.80 | read `build.gradle.kts` |
| `ops-incident` | cross-cutting | n/a | investigate; handoff for fixes |

## Profile schema

Profiles live in [`profiles/`](profiles/). See [`profiles/README.md`](profiles/README.md).

Key fields: `extends`, `repos`, `jacoco_line_ratio`, `context_skill`, `pattern_doc`, `loop_playbook`, `known_quirks`, `self_improvement`, `phases_enabled`, `ship`, `default_mode`.

## Phase 9d (self-improvement)

L2/L3 only. TOON contract → `apply-loop-learning.sh --contract`. See [`contracts/README.md`](contracts/README.md), [`patterns/README.md`](patterns/README.md), [`loop-learnings/README.md`](../loop-learnings/README.md).

### Local preflight (required before validate and approve)

Primary enforcement for **local-only Cursor** loop. Recommended one-time setup:

```bash
python3 -m venv .venv-loop-9d && .venv-loop-9d/bin/pip install -r scripts/requirements-loop-9d.txt
```

Preflight auto-uses `.venv-loop-9d` when present (no manual `source` required). Prints `loop_9d_preflight: PY=...` for audit.

```bash
export CURSOR_PROJECT_DIR="$(pwd)"
./scripts/loop_9d_preflight.sh   # before validate; run again before approve
```

Runs [`scripts/loop_9d_coverage_check.py`](../../scripts/loop_9d_coverage_check.py) + [`scripts/loop_9d_conformance_check.py`](../../scripts/loop_9d_conformance_check.py) `--strict`. Verifies `jsonschema` + `coverage` are importable on the selected interpreter (does not auto-install).

Optional mirror when workspace is **shared in git**: [`.github/workflows/loop-9d-checks.yml`](../../.github/workflows/loop-9d-checks.yml) — same commands; never required for local-only usage.

### Run-log token (Phase 9d rows)

```text
9d-preflight: ok | 9d: PENDING_APPROVAL → APPLY_SUCCESS | staging=<path> | branch=<name>
```

Append `| allowlist=<line>:<reason>:<expiry>` when coverage allowlist is active.

### Apply-engine tests (developer)

```bash
pip install -r scripts/requirements-loop-9d.txt
export CURSOR_PROJECT_DIR="$(pwd)"
python3 .cursor/skills/agentic-loop/scripts/test_apply_loop_learning.py -v
python3 scripts/loop_9d_coverage_check.py
python3 scripts/loop_9d_conformance_check.py
python3 scripts/loop_9d_conformance_check.py --strict   # after doc parity complete
```

Validate-only (expect `PENDING_APPROVAL`):

```bash
.cursor/skills/agentic-loop/scripts/apply-loop-learning.sh \
  --contract docs/loop-learnings/contracts/your-service-api/PROJ-9999-20260623T120000Z-learning.json \
  --repo your-service-api
```

## Operating files

| File | Purpose |
|------|---------|
| [`STATE.md`](STATE.md) | Human inbox (all profiles) |
| [`cell-health-feature-state.md`](cell-health-feature-state.md) | Active Cell Health run |
| [`ops-incident-state.md`](ops-incident-state.md) | Active ops investigation |
| [`loop-run-log.md`](loop-run-log.md) | Append-only run history |
| [`loop-budget.md`](loop-budget.md) | Shared caps |
| [`GATES.md`](GATES.md) | Quality gates + Failure Router |
| [`patterns/cell-health-feature-loop.md`](patterns/cell-health-feature-loop.md) | Cell Health reference path |
| [`patterns/README.md`](patterns/README.md) | All `*-patterns.md` index |
| [`contracts/README.md`](contracts/README.md) | Phase 9d TOON contract spec |
| [`loop-learnings/README.md`](../loop-learnings/README.md) | Learnings index + archive layout |

## Commands

- `/agentic-loop --help` (Plan mode, L1 default)
- `` (alias)

### PR review (Phase 5)

`--pr <n>` or GitHub PR URL → `@pr-code-review` via Phase 5:

- Phase 0e: `pr_type` (`java-only` | `infra-only` | `mixed`)
- Phase 0f: existing-feedback registry (dedup open Copilot/human/bot threads)
- Pass 3 routed by type; synthesis reports `net_new_count` / `suppressed_count`

**Phase 7 + `--pr`** = thread hygiene only (`ce-resolve-pr-feedback`).

```text
/agentic-loop --profile cellrouter --mode L1 --pr 78
/agentic-loop --mode L1 https://github.com/<org>/<repo>/pull/<n>
/agentic-loop --profile cell-health --phase 7 --pr 2   # hygiene only
```

See [`GATES.md`](GATES.md) Phase 5 PR review gates and [`.cursor/rules/pr-code-review.mdc`](../../.cursor/rules/pr-code-review.mdc).

## Cadence

- On-demand; **L1 default**; Plan mode at start
- No scheduled auto-merge — see [`docs/safety.md`](../safety.md)

## Budget

See [`loop-budget.md`](loop-budget.md). Kill switch: `STATE.md` human inbox.

## MCP

Atlassian, GitHub, Glean (feature); Datadog, PagerDuty (ops). Template: `.cursor/mcp.agent-loop.template.json`

## Worktree

`ce-worktree` for parallel epics; one branch per spike.

## Root loop-audit files

Repo root: `STATE.md`, `LOOP.md`, `loop-budget.md`, `loop-run-log.md` (symlinks). Registry: `patterns/registry.yaml`.

## Skills & agents

- `.cursor/skills/agentic-loop/SKILL.md`
- `.cursor/skills/ops-incident-loop/SKILL.md`
- `.cursor/agents/agentic-loop-orchestrator.md`

## Wiki

- [`docs/wiki/your-loop-wiki.md`](../wiki/cell-health-agent-loop.md)

## Pilot checklist

1. Readiness: `npx @cobusgreyling/loop-audit . --suggest` (from workspace root). See [`loop-audit.md`](loop-audit.md) for CDP path mapping and false-negative triage/verifier.
2. L1 report-only: ` --mode L1 PROJ-153` — phases 0→2, update `cell-health-feature-state.md`.
3. L3-push: ` PROJ-153` — full loop; human merges PR.
4. Ops dry-run: `/agentic-loop --profile ops-incident --mode L1 --datadog-monitor <id>` (MCP required).
5. Record outcomes in `loop-run-log.md` via `update-loop-state.sh`.
