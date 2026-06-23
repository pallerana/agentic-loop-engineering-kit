# Agentic Loop Engineering Kit

Modular Loop Engineering OS for `your-service-*` repos — feature development and ops troubleshooting.

## Parse arguments

If the user invokes `/agentic-loop` with **no arguments** or **`--help`** only → print the **HELP** section below and **do not start a loop**.

Otherwise → **`SwitchMode(plan)`** then read and follow [`.cursor/skills/agentic-loop/SKILL.md`](../skills/agentic-loop/SKILL.md) (runbook: `agentic-loop-runbook`) with parsed flags and target.

## PLAN MODE REQUIRED

- Loop **always starts in Plan mode** — never autonomous Agent execution
- **Default mode: L1** (Phase 0→2, report-only, no code/git)
- **Stop after Phase 2** until user explicitly approves implementation
- `--mode L2` / `L3-push` require flag **and** user confirmation in chat before Phase 3+
- Failure Router **recommends** next phase — does not auto-re-dispatch

## HELP

```text
Agentic Loop Engineering Kit — modular Loop Engineering OS for your-service-* repos

USAGE
  /agentic-loop --help
  /agentic-loop --profile <id> [options] [target]
  /agentic-loop --profile my-service [options] [target]          # alias: --profile my-service

PROFILES
  my-service              your service MVP (aggregator + central); extends default
  springboot-default   Any Java/Spring Boot repo (Gradle)
  ops-incident             Datadog / PagerDuty investigation (L1 default)
  your-service          your-service assignments API (extends default)
  your-service               your-service http cell router (extends default)
  your-service             your-service cell migrator (extends default)
  your-service            your-service cell discovery (extends default)

MODES (maturity)
  L1   Report only — Phase 0→2, STATE/run-log, no code changes (DEFAULT)
  L2   Implement + review; PR draft; human may push (requires approval after Phase 2)
  L3-push  L2 + squash, push feature branch, babysit CI (max 3); human merge
       Explicit --mode L2|L3-push required; human must approve Phase 3+ and ship

OPTIONS
  --profile <id>           Required except for --help and my-service alias
  --mode L1|L2|L3-push     Override profile default maturity
  --repo <path>            Repo dir under workspace (required for default profile)
  --handoff <profile>      Ops→feature: preload STATE from ops-incident run
  --from-state <path>      Resume from loop-kit/*-state.md
  --phase <n|name>         Start at phase (orchestrator validates prerequisites)
  --dry-run                Print planned phases + gates; no MCP/git writes
  --help                   This reference

TARGET (one of; profile-specific)
  <JIRA-KEY>               e.g. PROJ-123 (feature profiles)
  --datadog-monitor <id>   Ops: Datadog monitor id or query
  --pagerduty <id>         Ops: PagerDuty incident id (INC-…)
  --pr <n>                 PR review (Phase 5) or ship/hygiene (Phase 6/7 with --phase)

PR REVIEW (--pr or GitHub URL → Phase 5 @pr-code-review)
  --pr <n> alone           Phase 5 full review; repo from --profile / --repo
  <PR URL>                 Parse owner/repo/number; infer profile when possible
  --pr <n> + URL           URL wins if numbers differ; warn on conflict
  Default --mode L1        Report-only findings table (no auto-fix)
  pr_type auto-detect      java-only | infra-only | mixed → routed Pass 3 + drill
  Dedup                    Phase 0f registry suppresses repeat of open threads

PHASES (feature profiles; ops-incident uses subset)
  0    Context sync (wiki, Jira/Confluence, knowledge-graph, profile skill)
  0b   Ticket ack (Jira In Progress / PagerDuty note)
  1    Plan or ops hypothesis (ce-plan)
  2    Plan / hypothesis review (incl. ce-testing-reviewer)
  3    Implement (ce-work)
  4    Verify (gradle, JaCoCo, diff coverage, E2E tier)
  5    Code review (@pr-code-review when --pr or PR URL set)
  6    Ship (squash, push, PR, babysit)
  7    PR hygiene (Copilot/CodeQL threads — not full review)
  8    Close-the-loop (Jira comment + PR + tests + SHA)
  9    Wiki + traceability + knowledge-graph update + ce-compound

FAILURE ROUTER (orchestrator; not a separate agent)
  delta/JaCoCo fail     → test-repair pass → implementer
  local CI fail         → implementer (then planner if 2+ arch failures)
  remote CI fail        → ship/babysit (max 3) → planner with logs
  AC/plan gap           → planner
  ops infra/flake       → human inbox in STATE.md

EXAMPLES — Feature (your service)
  /agentic-loop --help
  /agentic-loop --profile my-service PROJ-123
  /agentic-loop --profile my-service --mode L1 PROJ-123
  /agentic-loop --profile my-service PROJ-123

EXAMPLES — Feature (other your-service repo)
  /agentic-loop --profile your-service PROJ-123
  /agentic-loop --profile springboot-default \
    --repo your-service-api PROJ-123

EXAMPLES — Ops (Datadog / PagerDuty)
  /agentic-loop --profile ops-incident --pagerduty INC-ABC123
  /agentic-loop --profile ops-incident --datadog-monitor 12345678

EXAMPLES — Handoff (ops → fix)
  /agentic-loop --profile ops-incident --handoff my-service \
    --repo your-service-api PROJ-123 \
    --from-state loop-kit/ops-incident-state.md

EXAMPLES — Resume / ship only
  /agentic-loop --profile my-service --phase 6 --pr 2

EXAMPLES — PR review (Phase 5, report-only)
  /agentic-loop --profile your-service --mode L1 --pr 78
  /agentic-loop --profile your-service --mode L1 \
    https://github.com/<org>/your-service-api/pull/123
  /agentic-loop --profile my-service --phase 5 --pr 2
  /agentic-loop --profile springboot-default --repo infra/ --mode L1 --pr <n>

EXAMPLES — PR thread hygiene only (Phase 7, after green CI)
  /agentic-loop --profile my-service --phase 7 --pr 2

FILES
  Skill       .cursor/skills/agentic-loop/SKILL.md
  PR review   .cursor/rules/pr-code-review.mdc
  Profiles    loop-kit/profiles/*.yaml
  State       loop-kit/{profile}-state.md, STATE.md, loop-run-log.md
  Gates       loop-kit/GATES.md

SEE ALSO
  pr-code-review.mdc, your-domain-skill skill, service-quality-drill.mdc, docs/wiki/your-loop-wiki.md
```
