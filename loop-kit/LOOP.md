# Agentic Loop Engineering Kit — Catalog

Loop Engineering OS for your monorepo repos and ops incidents.

## Loops

| Loop | Profile | Default mode | Entry |
|------|---------|--------------|-------|
| Feature (generic) | `springboot-default` | L1 | `/agentic-loop --profile springboot-default --repo <path> JIRA` |
| your service MVP | `my-service` | L1 | `/agentic-loop --profile my-service PROJ-123` |
| Ops incident | `ops-incident` | L1 | `/agentic-loop --profile ops-incident --pagerduty INC-…` |

## Repo matrix

| Profile | Repos | JaCoCo | Notes |
|---------|-------|--------|-------|
| `my-service` | aggregator, central | 1.00 | E2E, Event Hub, Cosmos |
| `your-service` | assignments API | 0.80 | |
| `your-service` | http cell router | 0.80 | |
| `your-service` | cell migrator | 0.80 | |
| `your-service` | cell discovery | 0.80 | |
| `springboot-default` | any `--repo` | 0.80 | read `build.gradle.kts` |
| `ops-incident` | cross-cutting | n/a | investigate; handoff for fixes |

## Profile schema

Profiles live in [`profiles/`](profiles/). See [`profiles/README.md`](profiles/README.md).

Key fields: `extends`, `repos`, `jacoco_line_ratio`, `context_skill`, `phases_enabled`, `ship`, `default_mode`.

## Operating files

| File | Purpose |
|------|---------|
| [`STATE.md`](STATE.md) | Human inbox (all profiles) |
| [`feature-state.md`](feature-state.md) | Active your service run |
| [`ops-incident-state.md`](ops-incident-state.md) | Active ops investigation |
| [`loop-run-log.md`](loop-run-log.md) | Append-only run history |
| [`loop-budget.md`](loop-budget.md) | Shared caps |
| [`GATES.md`](GATES.md) | Quality gates + Failure Router |
| [`patterns/feature-loop-example.md`](patterns/feature-loop-example.md) | your service reference path |

## Commands

- `/agentic-loop --help` (Plan mode, L1 default)
- `/agentic-loop --profile my-service` (alias)

### PR review (Phase 5)

`--pr <n>` or GitHub PR URL → `@pr-code-review` via Phase 5:

- Phase 0e: `pr_type` (`java-only` | `infra-only` | `mixed`)
- Phase 0f: existing-feedback registry (dedup open Copilot/human/bot threads)
- Pass 3 routed by type; synthesis reports `net_new_count` / `suppressed_count`

**Phase 7 + `--pr`** = thread hygiene only (`ce-resolve-pr-feedback`).

```text
/agentic-loop --profile your-service --mode L1 --pr 78
/agentic-loop --mode L1 https://github.com/<org>/<repo>/pull/<n>
/agentic-loop --profile my-service --phase 7 --pr 2   # hygiene only
```

See [`GATES.md`](GATES.md) Phase 5 PR review gates and [`.cursor/rules/pr-code-review.mdc`](../../.cursor/rules/pr-code-review.mdc).

## Cadence

- On-demand; **L1 default**; Plan mode at start
- No scheduled auto-merge — see [`docs/safety.md`](../safety.md)

## Budget

See [`loop-budget.md`](loop-budget.md). Kill switch: `STATE.md` human inbox.

## MCP

Atlassian, GitHub, Glean (feature); Datadog, PagerDuty (ops). Template: `.cursor/mcp.agentic-loop.template.json`

## Worktree

`ce-worktree` for parallel epics; one branch per spike.

## Root loop-audit files

Repo root: `STATE.md`, `LOOP.md`, `loop-budget.md`, `loop-run-log.md` (symlinks). Registry: `patterns/registry.yaml`.

## Skills & agents

- `.cursor/skills/agentic-loop/SKILL.md`
- `.cursor/skills/ops-incident-loop/SKILL.md`
- `.cursor/agents/agentic-loop-orchestrator.md`

## Wiki

- [`docs/wiki/your-loop-wiki.md`](../wiki/your-loop-wiki.md)

## Pilot checklist

1. Readiness: `npx @cobusgreyling/loop-audit . --suggest` (from workspace root).
2. L1 report-only: `/agentic-loop --profile my-service --mode L1 PROJ-123` — phases 0→2, update `feature-state.md`.
3. L3-push: `/agentic-loop --profile my-service PROJ-123` — full loop; human merges PR.
4. Ops dry-run: `/agentic-loop --profile ops-incident --mode L1 --datadog-monitor <id>` (MCP required).
5. Record outcomes in `loop-run-log.md` via `update-loop-state.sh`.
