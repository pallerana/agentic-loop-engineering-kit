---
name: agentic-loop-runbook
description: >-
  Agentic Loop Engineering Kit runbook — YAML profiles, phases 0–9, Plan-mode-first, human gates.
  Invoked via /agentic-loop command (not a duplicate slash command).
---

# Agentic Loop Engineering Kit Runbook

Profile-driven loop for your monorepo Java services and ops incidents.

**Catalog:** [`loop-kit/LOOP.md`](../../../loop-kit/LOOP.md) · **Gates:** [`GATES.md`](../../../loop-kit/GATES.md) · **Wiki:** [`cell-health-agent-loop.md`](../../../docs/wiki/your-loop-wiki.md)

## Hard rules (plan-mode-first)

1. **Never start in Agent mode** — call `SwitchMode(plan)` at loop start
2. **Default mode L1** — Phase 0→2 only unless `--mode L2` or `--mode L3-push` **and** user explicitly approves in chat
3. **Stop after Phase 2** until user says e.g. "proceed with implementation" or approves `--mode L2`/`L3-push`
4. **Failure Router recommends only** — do not auto-re-dispatch; present classification and wait for human
5. Phase 4 scripts run only after human approves Phase 3
6. L3-push push/CI babysit only after user explicitly approves ship

## Invocation

```text
/agentic-loop --profile <id> [options] [target]
 [options] [target]   # alias → --profile cell-health
```

### PR review targets (`--pr` or URL)

| Input | Behavior |
|-------|----------|
| `--pr <n>` | Phase **5** PR review; repo from profile / `--repo` |
| `https://github.com/{owner}/{repo}/pull/{n}` | Parse URL → Phase 5; infer profile/repo from workspace folder name |
| `--pr <n>` + URL | **URL wins** if numbers differ; warn in Functional Context |
| `--pr` or URL without `--phase` | Jump to Phase 5 (skip 0–4 unless full loop requested) |

**Default for PR review:** `--mode L1` (report-only per `pr-code-review.mdc`).

Profile inference from repo name: `your-service-*` → matching profile (`cellrouter`, `cellassignments`, etc.); `infra/` → `--repo infra/`.

```text
# Java PR — auto-detects java-only
/agentic-loop --profile cellrouter --mode L1 --pr 78

# URL only — auto-resolves repo + PR number
/agentic-loop --mode L1 https://github.com/<org>/your-service-api/pull/123

# Infra-only PR
/agentic-loop --profile springboot-default --repo infra/ --mode L1 --pr <n>

# Thread hygiene after green CI (Phase 7 — not full review)
/agentic-loop --profile cell-health --phase 7 --pr 2
```

**`--help` or no args:** print help from [`.cursor/commands/agentic-loop.md`](../../commands/agentic-loop.md) and **stop**.

## Profile loading

1. Read `loop-kit/profiles/<profile>.yaml`.
2. If `extends` is set, merge parent profile (child overrides).
3. Resolve `repos`, `jacoco_line_ratio`, `phases_enabled`, `ship`, `context_skill`.
4. For `springboot-default`, require `--repo <workspace-relative-path>` unless a named repo profile sets `repos`.

## Maturity modes

| Mode | Behavior |
|------|----------|
| **L1** (default) | Phases 0→2; update STATE + run-log; **no code/git** |
| **L2** | Through review; PR draft; human may push — **requires explicit approval** |
| **L3-push** | L2 + squash, push feature branch, babysit CI (max 3); **human merge** — **requires explicit ship approval** |

Profile `default_mode` is **L1** unless `--mode` overrides (still needs human gate for Phase 3+).

## Phase machine (feature profiles)

Execute in order unless `--phase` resumes (validate prerequisites).

### Phase 0 — Context sync

Delegate triage: [`loop-triage`](../loop-triage/SKILL.md) or inline:

- Wiki: `version_check.py`, `index.md`, `current-status.md`, `log.md`.
- Profile `pattern_doc` if set → read (workspace-root path; active repo subsection when multi-repo).
- Profile `loop_playbook` if set → read (e.g. cell-health feature loop).
- Profile `context_skill` if set (e.g. `cell-health-mvp` Phase 0).
- Jira/Confluence per profile; `graphify query` for touched repos.
- Record snapshot in `loop-kit/<profile>-state.md`.

### Phase 0b — Ticket ack

- Jira: transition to **In Progress** (Atlassian MCP or `jira-cli`).
- Ops: PagerDuty incident note with investigation start.

### Phase 1 — Plan

- Feature: `/ce-plan` with mandatory **test matrix** (see GATES.md).
- Ops: hypothesis doc in STATE (symptom, timeline, suspects, next queries).

### Phase 2 — Plan / hypothesis review

- Feature: `ce-testing-reviewer` on test matrix; human gate if profile requires.
- Ops: validate hypothesis against Datadog/PagerDuty evidence.
- **STOP HERE (L1 default)** — wait for human approval before Phase 3.

### Phase 3 — Implement (human-approved only)

- `/ce-work` in target repo; match `java-springboot-standards.mdc` + `service-quality-drill.mdc`.
- **Skipped** in ops L1.

### Phase 4 — Verify (human-approved only)

Delegate: [`loop-verifier`](../loop-verifier/SKILL.md)

```bash
.cursor/skills/agentic-loop/scripts/gradle-build.sh <repo-path>
.cursor/skills/agentic-loop/scripts/parse-jacoco.sh <repo-path> <ratio>
```

- Profile E2E script if defined (e.g. cell-health local E2E).
- Diff coverage: new/changed production lines need tests (delta gate in GATES.md).

### Phase 5 — Code review

**When `--pr <n>` or a GitHub PR URL is set** → mandatory [`pr-code-review.mdc`](../../rules/pr-code-review.mdc):

1. Phase 0a–0d: PR metadata, Jira, scenario matrix, inline thread ingestion
2. Phase 0e: **`pr_type`** classification (`java-only` | `infra-only` | `mixed`) from `gh pr diff --name-only`
3. Phase 0f: **Existing-feedback registry** (inline + conversation + bots) for dedup
4. Pass 1: `ce-code-review` (diff-only `+` hunks; inject registry + `pr_type`)
5. Pass 2: Bugbot (inject registry; do not re-raise known themes)
6. Pass 3 (routed by `pr_type`):
   - **java-only:** `java-springboot-standards` + ArchUnit + SOLID + `service-quality-drill`
   - **infra-only:** `cba-terraform-standards` + observability wiki; **no** JaCoCo/gradle
   - **mixed:** Java segment + infra segment; `Infra` / `Cross-cutting` categories
7. **Synthesis:** merge passes → registry suppress → **net-new findings table** + optional **Already raised** appendix + `net_new_count` / `suppressed_count` + verdict

Resolve repo: profile `repos[0]`, `--repo`, or `gh pr view --json headRepository`.

**Phase 7 + `--pr`** = thread hygiene only (`ce-resolve-pr-feedback`) — not full review.

**When `--pr` / URL absent** → `ce-code-review` vs `main`; fix P0/P1 before ship.

### Phase 6 — Ship (L3-push, human-approved only)

- Check [`loop-budget`](../loop-budget/SKILL.md) before babysit.
- Squash commits on feature branch; push once per batch.
- `gh pr create` or update; `gh-pr-checks-watch.sh` (max 3 babysit cycles).

### Phase 7 — PR hygiene

- Copilot/CodeQL threads: implement → test → reply → resolve (`ce-resolve-pr-feedback`).

### Phase 8 — Close-the-loop

- Jira comment: summary, test names, commit SHA, PR link, AC map.
- Script: `.cursor/skills/agentic-loop/scripts/jira-close-loop.sh <KEY> <PR-url> <SHA> [tests]`

### Phase 9 — Close-the-loop + self-improvement

**9a Wiki:** Append feature-outcome line to `docs/wiki/log.md`; refresh `current-status.md`.

**9b Graphify:** `graphify update <repo>` for changed repos.

**9c Compound:** `/ce-compound` → human-facing wiki only (no agent skill/rule mutation).

**9d Self-improvement** (mirror orchestrator SSOT — see [`.cursor/agents/agentic-loop-orchestrator.md`](../../agents/agentic-loop-orchestrator.md) Phase 9):

<!-- PHASE-9D-TRANSITIONS:verbatim:start — do not edit in mirrors -->
| Step | Action | Transition |
|------|--------|------------|
| 9a | wiki log + current-status | always |
| 9b | graphify update | always |
| 9c | ce-compound | always |
| 9d-eligible | check L2/L3 + `self_improvement` | skip → end |
| 9d-extract | loop-self-improvement | `NO_LEARNINGS` → end |
| 9d-preflight | `scripts/loop_9d_preflight.sh` | fail closed; run before validate **and** before apply |
| 9d-validate | apply script, no approve | `PENDING_APPROVAL` → STOP |
| 9d-gate | present summary table | **STOP — same-turn approve forbidden** |
| 9d-apply | user approve → `approve` | `APPLY_SUCCESS` / `IDEMPOTENT_SKIP` |
| 9d-promo | promotion contract if any | after learning applied |
<!-- PHASE-9D-TRANSITIONS:verbatim:end -->

1. Invoke [`loop-self-improvement`](../loop-self-improvement/SKILL.md) → TOON contract + rationale.
2. **Preflight:** `scripts/loop_9d_preflight.sh` → must print `loop_9d_preflight: ok`.
3. Validate: `apply-loop-learning.sh --contract ...-learning.json` (no `approve`) → `PENDING_APPROVAL`.
4. Present `docs/loop-learnings/staging/<JIRA>-<UTC-ts>-summary.md`; **STOP** for human.
5. **Preflight again** (same script).
6. On user approve: `apply-loop-learning.sh ... approve` → `loop/skill-update-*` branch + canonical 9d run-log line.
7. If `-promotion.json`: stage after step 6 succeeds.

### Run-log token (canonical — append via `update-loop-state.sh`)

```text
9d-preflight: ok | 9d: PENDING_APPROVAL → APPLY_SUCCESS | staging=<path> | branch=<name>
```

If coverage allowlist active, append `| allowlist=<line>:<reason>:<YYYY-MM-DD>` on the same row.

See [`loop-kit/contracts/README.md`](../../../loop-kit/contracts/README.md) and [`GATES.md`](../../../loop-kit/GATES.md) Phase 9d gates.

## Ops-incident profile

See [`.cursor/skills/ops-incident-loop/SKILL.md`](../ops-incident-loop/SKILL.md).

- Default L1: phases 0, 1, 2 only.
- MCP: Datadog, PagerDuty, Glean, graphify `ddog__` slice.
- Fix scope → `--handoff cell-health` (or repo profile) with `--from-state`.

## Failure Router (recommend only)

| Signal | Recommend |
|--------|-----------|
| JaCoCo / delta coverage | Test-repair (4) → Implementer (3) |
| Local `./gradlew clean build` fail | Implementer (3); planner after 2+ arch failures |
| Remote CI fail | Ship/babysit (6), max 3 → planner with logs |
| AC/plan gap | Planner (1) |
| Infra / flake / secrets | `loop-kit/STATE.md` human inbox |

**Wait for human** before re-dispatching.

## Scripts (repo-adaptive)

| Script | Purpose |
|--------|---------|
| `scripts/gradle-build.sh` | Gradle or Maven detect; `./gradlew clean build` |
| `scripts/parse-jacoco.sh` | Parse JaCoCo HTML; exit non-zero if below ratio |
| `scripts/gh-pr-checks-watch.sh` | Poll `gh pr checks` until green or timeout |
| `scripts/act-run.sh` | Optional local `act` workflow dry-run |
| `scripts/update-loop-state.sh` | Append run-log + touch state frontmatter |
| `scripts/jira-close-loop.sh` | Jira close-the-loop comment template |

## Dry-run

`--dry-run`: print profile, mode, phases, gates, repos — no MCP writes, no git mutations.

## Handoff

`--handoff <profile> --from-state <path>`: copy ops hypothesis + suspects into feature state; continue from Phase 0 or 1 in Plan mode.

## See also

- [`cell-health-mvp`](../cell-health-mvp/SKILL.md) — Cell Health Phase 0 extension
- [`pr-code-review.mdc`](../../rules/pr-code-review.mdc) — Phase 5 when `--pr` or PR URL
- [`service-quality-drill.mdc`](../../rules/service-quality-drill.mdc)
- [`loop-kit/patterns/cell-health-feature-loop.md`](../../../loop-kit/patterns/cell-health-feature-loop.md)
