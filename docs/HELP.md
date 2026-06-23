# Agentic Loop — HELP

Canonical reference for `/agentic-loop`. Also embedded in [README.md](../README.md) and [`.cursor/commands/agentic-loop.md`](../.cursor/commands/agentic-loop.md).

```text
Agentic Loop Engineering Kit — plan-mode-first Loop OS for Java/Spring Boot repos

USAGE
  /agentic-loop --help
  /agentic-loop --profile <id> [options] [target]

PROFILES (shipped)
  springboot-default   Any Java/Spring Boot repo (Gradle); requires --repo
  ops-incident         Datadog / PagerDuty investigation (L1 default)

MODES
  L1        Phase 0→2, report-only, no code/git (DEFAULT)
  L2        Implement + review; PR draft; human may push
  L3-push   L2 + push feature branch + CI babysit (max 3); human merge

OPTIONS
  --profile <id>         Required except --help
  --mode L1|L2|L3-push   Override profile default
  --repo <path>          Repo under workspace (springboot-default)
  --handoff <profile>    Ops→feature handoff
  --from-state <path>    Resume from loop-kit/*-state.md
  --phase <n|name>       Start at phase
  --dry-run              Print plan; no writes
  --help                 This reference

TARGET
  <JIRA-KEY>             e.g. PROJ-123
  --datadog-monitor <id>
  --pagerduty <id>
  --pr <n>               PR review or hygiene (with --phase)

PR REVIEW (Phase 5 @pr-code-review when --pr or PR URL)
  Default L1 report-only; pr_type java|infra|mixed; Phase 0f dedup

PHASES 0–9
  0 Context · 0b Ack · 1 Plan · 2 Review · 3 Implement · 4 Verify
  5 Review · 6 Ship · 7 Hygiene · 8 Close-loop · 9 Compound

FAILURE ROUTER (recommend only)
  coverage→4→3 · local CI→3 · remote CI→6 (max 3)→1 · plan gap→1 · flake→STATE

EXAMPLES
  /agentic-loop --profile springboot-default --repo services/api PROJ-123
  /agentic-loop --mode L1 --pr https://github.com/<org>/<repo>/pull/42
  /agentic-loop --profile ops-incident --pagerduty INC-ABC
  /agentic-loop --profile springboot-default --phase 7 --pr 42

FILES
  Command    .cursor/commands/agentic-loop.md
  Runbook    .cursor/skills/agentic-loop/SKILL.md
  HELP       docs/HELP.md
  Gates      loop-kit/GATES.md
  Standards  .cursor/rules/*.mdc
```
