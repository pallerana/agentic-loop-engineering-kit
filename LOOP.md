# Agentic Loop Engineering Kit — LOOP config

Canonical kit: [`loop-kit/`](loop-kit/). This root file satisfies loop-audit discovery.

## Cadence

- **Trigger:** on-demand via `/agentic-loop` or `/agentic-loop --profile my-service`
- **Default mode:** L1 (Plan mode, Phase 0→2, report-only)
- **No scheduled auto-merge** — human merges all PRs
- **Phase 3+** only after explicit human approval in chat

## Budget

See [`loop-budget.md`](loop-budget.md) (symlink to `loop-kit/loop-budget.md`).

- Remote CI babysit: max **3** per PR
- Local build retry: max **5** per phase
- Kill switch: human inbox in [`STATE.md`](STATE.md) or `loop-pause` note in state frontmatter
- Run history: [`loop-run-log.md`](loop-run-log.md)

## Safety gates

See [`docs/safety.md`](docs/safety.md).

- **Plan-mode-first** — never start loop in Agent mode; `SwitchMode(plan)` at invocation
- **No auto-merge** on `main`; branch protection + 2 code-owner reviews
- **Denylist hooks** — `block-dangerous-git.sh`, `block-denylist-edits.sh`
- **No `terraform apply`** inside the loop
- **Human gate** after Phase 2 before implement/verify/ship

## MCP connectors

Template: [`.cursor/mcp.agentic-loop.template.json`](.cursor/mcp.agentic-loop.template.json)

| Profile | MCP |
|---------|-----|
| Feature | Atlassian (Jira/Confluence), GitHub, Glean |
| Ops | Datadog, PagerDuty, Glean, GitHub (read) |

Ops L1: investigate only — no prod writes.

## Worktree isolation

- Parallel epics: `ce-worktree` skill — one feature branch per spike
- Document active worktree in profile state file

## Handoff

Ops → feature: `/agentic-loop --profile ops-incident --handoff my-service --from-state loop-kit/ops-incident-state.md`

## PR review (Phase 5)

`--pr <n>` or GitHub PR URL triggers `@pr-code-review` (not generic `ce-code-review`):

- Auto `pr_type`: java-only | infra-only | mixed
- Dedup via Phase 0f feedback registry
- Default L1 report-only; Phase 7 + `--pr` = thread hygiene only

```text
/agentic-loop --profile your-service --mode L1 --pr 78
/agentic-loop --mode L1 https://github.com/<org>/<repo>/pull/<n>
```

Gates: [`loop-kit/GATES.md`](loop-kit/GATES.md) · Rule: [`.cursor/rules/pr-code-review.mdc`](.cursor/rules/pr-code-review.mdc)

## Patterns registry

[`patterns/registry.yaml`](patterns/registry.yaml)

## Skills

| Skill | Role |
|-------|------|
| `loop-triage` | Phase 0–0b context + ticket ack |
| `loop-verifier` | Phase 4 maker/checker verify |
| `loop-budget` | Budget cap enforcement |
| `agentic-loop-runbook` | Full phase machine (via `/agentic-loop` command) |

## Full catalog

[`loop-kit/LOOP.md`](loop-kit/LOOP.md) · [`GATES.md`](loop-kit/GATES.md) · [`docs/wiki/your-loop-wiki.md`](docs/wiki/your-loop-wiki.md)
