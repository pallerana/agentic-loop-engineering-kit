# Agentic Loop Engineering Kit

Plan-mode-first Loop Engineering OS for Java/Spring Boot monorepos.

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-blue.svg)](LICENSE)

## Contents

- [What it is](#what-it-is) · [Quick start](#quick-start) · [Installation](#installation)
- [Companion setup](#recommended-companion-setup-efficient-agent-behaviour) (LLM-wiki, graphify)
- [Maturity modes](#maturity-modes-l1--l2--l3-push) (L1 / L2 / L3-push)
- [Validate setup](#validate-your-setup) (loop-audit)
- [**Phase reference (0–9)**](#phase-reference-09) — skills, agents, rules per phase
- [Architecture](#architecture) — **7 Mermaid diagrams**
  1. [System layers](#1-system-layers-birds-eye)
  2. [Invocation routing](#2-invocation-routing)
  3. [Phase machine](#3-phase-machine-feature-profiles)
  4. [Phase 5 branch](#4-phase-5-branch---pr-vs-normal)
  5. [Profile model](#5-profile-model)
  6. [Maker/checker split](#6-makerchecker-split-roles)
  7. [Failure Router](#7-failure-router-recommend-only)


<!-- EXPORT:toc:start -->
- [Phase 9d (self-improvement)](#phase-9d-self-improvement) — inside phase reference
- [Recommended workspace layout](#recommended-workspace-layout) — single `.cursor` at workspace root
<!-- EXPORT:toc:end -->

## What it is

- **Slash command** `/agentic-loop` — plan-mode-first; phases 0–9; **L1 default** (Phase 0→2, report-only)
- **Profiles** — YAML in `loop-kit/profiles/` (`springboot-default`, `ops-incident`; extend for your services)
- **Maker/checker** — implementer (`ce-work`) never verifies itself (`loop-verifier`); orchestrator delegates
- **Failure Router** — classifies failures and **recommends** next phase; never auto-re-dispatch
- **Seven standards** — Java, Spring Boot, quality drill, PR review, Terraform, jabrena testing rules

## Quick start

```bash
git clone https://github.com/pallerana/agentic-loop-engineering-kit.git
cd my-platform
cp -R agentic-loop-engineering-kit/loop-kit ./loop-kit
# merge agentic-loop-engineering-kit/.cursor into your .cursor/
cp agentic-loop-engineering-kit/LOOP.md agentic-loop-engineering-kit/STATE.md .
cp agentic-loop-engineering-kit/loop-budget.md agentic-loop-engineering-kit/loop-run-log.md .
cp agentic-loop-engineering-kit/patterns/registry.yaml ./patterns/
npx @cobusgreyling/loop-audit . --suggest
/agentic-loop --help
```

## Installation

1. **Copy or submodule** this repo into your monorepo tooling area.
2. **Merge** `loop-kit/` and `.cursor/` (commands, agents, skills, rules, hooks).
3. **Copy root loop files:** `LOOP.md`, `STATE.md`, `loop-budget.md`, `loop-run-log.md`, `patterns/registry.yaml`.
4. **Enable hooks** — `.cursor/hooks.json` (dangerous-git, denylist-edits, append-run-log).
5. **MCP** — merge `.cursor/mcp.agentic-loop.template.json` into your MCP config.
6. **Consumer profile** — add `loop-kit/profiles/my-service.yaml` extending `springboot-default`.
7. **Validate** — `npx @cobusgreyling/loop-audit . --suggest` (see below).
8. **Recommended** — bootstrap [LLM-wiki](https://github.com/Ss1024sS/LLM-wiki) and [graphify](https://github.com/safishamsi/graphify) for efficient agent behaviour.



<!-- EXPORT:installation-toc:start -->
- [Recommended workspace layout](#recommended-workspace-layout) — single `.cursor` at workspace root (avoid per-repo duplication)
<!-- EXPORT:installation-toc:end -->


<!-- EXPORT:workspace-setup:start -->
### Recommended workspace layout

Use **one Cursor workspace root** with a **single** `.cursor/` tree. Do **not** copy `.cursor/` into each child repo.

**Anti-pattern (do not):**

```
frontend-app/.cursor/
backend-repo/.cursor/
infra/.cursor/
```

Duplicated agents, skills, and hooks drift; `--repo` paths disagree with `CURSOR_PROJECT_DIR`.

**Recommended:**

Open **`my-platform/`** as the workspace. Child folders are repos only — no nested `.cursor/`.

```
my-platform/                          # Cursor workspace root — open THIS folder
├── .cursor/                          # single loop OS (merged from this kit)
│   ├── commands/agentic-loop.md
│   ├── agents/
│   ├── skills/
│   ├── rules/
│   └── hooks.json
├── loop-kit/
├── LOOP.md
├── STATE.md
├── loop-budget.md
├── loop-run-log.md
├── docs/wiki/                        # LLM-wiki (recommended)
├── frontend-app/                     # UI (no .cursor/)
├── backend-repo/                     # Java/Spring Gradle
└── infra/                            # Terraform / platform IaC
```

```mermaid
flowchart TB
  subgraph workspace [my-platform workspace root]
    CURSOR[".cursor/ single loop OS"]
    KIT["loop-kit/ profiles GATES contracts"]
    ROOT["LOOP.md STATE.md loop-budget.md"]
    WIKI["docs/wiki/ LLM-wiki"]
    FE["frontend-app/"]
    BE["backend-repo/"]
    INF["infra/"]
  end
  CURSOR --> KIT
  workspace --> FE
  workspace --> BE
  workspace --> INF
```

**Setup:**

1. Create `my-platform/`; clone `frontend-app`, `backend-repo`, and `infra` as siblings.
2. Merge this kit's `.cursor/`, `loop-kit/`, and root loop files **once** at `my-platform/`.
3. Open Cursor on `my-platform/` (not a child repo).
4. Add `loop-kit/profiles/my-service.yaml` with `repos: [backend-repo]`.
5. Run `npx @cobusgreyling/loop-audit .` from the workspace root.

**Examples:**

```bash
/agentic-loop --profile springboot-default --repo backend-repo PROJ-123
/agentic-loop --profile springboot-default --repo infra --mode L1 --pr 42
```

**graphify:** `graphify update frontend-app`, `graphify update backend-repo`, `graphify update infra`; optional merged graph at `my-platform/graphify-out/`.
<!-- EXPORT:workspace-setup:end -->
## Recommended companion setup (efficient agent behaviour)

This kit orchestrates **what** the agent does each phase. For **durable memory** and **fast codebase navigation**, bootstrap these two projects in the same monorepo:

### [LLM-wiki](https://github.com/Ss1024sS/LLM-wiki) — compile-first project memory

Karpathy-style **wiki-first** knowledge: raw sources → compiled `docs/wiki/` → code. Stops every session from re-explaining decisions.

```bash
git clone https://github.com/Ss1024sS/LLM-wiki.git
python3 LLM-wiki/scripts/bootstrap_knowledge_system.py /path/to/my-platform "Your Project"
```

After bootstrap, Phase 0 reads `docs/wiki/index.md`, `current-status.md`, and `log.md`; Phase 9 writeback appends `log.md` and refreshes status. See [UNIVERSAL.md](https://github.com/Ss1024sS/LLM-wiki/blob/main/UNIVERSAL.md).

### [graphify](https://github.com/safishamsi/graphify) — queryable codebase knowledge graph

Turns repos into `graphify-out/graph.json` so agents answer architecture questions without full-tree search.

```bash
# Install graphify skill / CLI per repo README, then from monorepo root:
graphify update <repo-path>          # or graphify <path> for first build
graphify query "How does auth flow to the API?"
graphify path "Controller" "Repository"
```

Use in **Phase 0** (context sync) and **Phase 9** (update graph after code changes). Optional: merge multi-repo graphs for polyglot monorepos.

| Layer | Tool | Agent benefit |
|-------|------|----------------|
| Decisions & status | LLM-wiki | No amnesia across sessions; mandatory writeback |
| Code structure | graphify | Sub-second `query` / `path` / `explain` vs blind grep |
| Loop discipline | This kit | Plan-mode-first phases, human gates, Failure Router |

## Maturity modes (L1 · L2 · L3-push)

Every run has a **mode** (`--mode` or profile `default_mode`). Modes control how far past Phase 2 the loop may go **without** you approving in chat.

| Mode | Phases | Code / git | Typical use |
|------|--------|------------|-------------|
| **L1** (default) | 0 → 2 | **None** — report-only | Planning, PR review tables, ops hypothesis, safe pilots |
| **L2** | 0 → 5+ (draft) | Implement, verify, review; **PR draft**; you may push manually | Feature work after you approve the plan |
| **L3-push** | 0 → 7+ | L2 + squash, **push feature branch**, CI babysit (max 3 cycles); **you merge** | End-to-end ship with human merge only |

**Rules:**

- Loop **always** starts in Cursor **Plan mode** — even L2/L3 do not auto-run in Agent mode.
- **Stop after Phase 2** until you explicitly approve (e.g. “proceed with implementation” or `--mode L2` / `L3-push` with confirmation).
- **L1 + `--pr`** → Phase 5 findings table only (`pr-code-review.mdc`); no auto-fix.
- **L3-push** never force-pushes or merges to `main` — see `docs/safety.md`.

```text
L0 (loop-audit)  →  missing files; run npx @cobusgreyling/loop-audit . --suggest
L1               →  context + plan + review; STOP before implement
L2               →  implement + verify + review; PR draft
L3-push          →  push branch + babysit CI; human merges PR
```

Examples:

```text
/agentic-loop --profile springboot-default --repo backend-repo PROJ-123
/agentic-loop --mode L1 --profile springboot-default --repo backend-repo PROJ-123
/agentic-loop --mode L2 --profile springboot-default --repo backend-repo PROJ-123
/agentic-loop --mode L3-push --profile springboot-default --repo backend-repo PROJ-123
```

## Validate your setup

After copying this kit into your monorepo, run from the **repository root**:

```bash
npx @cobusgreyling/loop-audit . --suggest
```

- **`--suggest`** prints missing files and recommended fixes (do this first).
- Re-run after adding `loop-kit/profiles/<your-service>.yaml` and merging `.cursor/`.
- Target **L1** before your first `/agentic-loop` pilot; tune `loop-budget.md` per suggestions.

| Signal | Expected path (after merge) |
|--------|----------------------------|
| Loop config | `LOOP.md` (points to `loop-kit/`) |
| Human inbox | `STATE.md` |
| Budget caps | `loop-budget.md` |
| Run history | `loop-run-log.md` |
| Pattern registry | `patterns/registry.yaml` (`id: agentic-loop`) |
| Triage / verifier | `.cursor/skills/loop-triage`, `loop-verifier` |

| Score | Meaning | Next step |
|-------|---------|-----------|
| L0 | Missing loop files or skills | Follow `--suggest` output |
| L1 | Report-only ready | `/agentic-loop --mode L1 --profile springboot-default --repo <path> PROJ-123` |
| L2+ | Implement + verify wired | Human-approved L2/L3-push pilot |

Reference: [loop-engineering](https://github.com/cobusgreyling/loop-engineering) · [loop-audit](https://www.npmjs.com/package/@cobusgreyling/loop-audit)

## Usage

| Goal | Command |
|------|---------|
| Help | `/agentic-loop --help` |
| L1 plan | `/agentic-loop --profile springboot-default --repo backend-repo PROJ-123` |
| PR review | `/agentic-loop --mode L1 --pr 42` |
| Ops | `/agentic-loop --profile ops-incident --pagerduty INC-ABC` |
| Resume ship | `/agentic-loop --profile springboot-default --phase 6 --pr 42` |
| Thread hygiene | `/agentic-loop --profile springboot-default --phase 7 --pr 42` |

---

## Phase reference (0–9)

Each phase is executed by the **`agentic-loop-orchestrator`** agent in **Plan mode**. The orchestrator delegates to skills, external Compound Engineering plugins, and Cursor rules — it never implements code itself.

| Phase | Name | Summary | Agent / skill | Rules applied | Gate / stop |
|-------|------|---------|---------------|---------------|-------------|
| **0** | Context sync | Load wiki, Jira, knowledge graph, profile context; snapshot state | [`loop-triage`](.cursor/skills/loop-triage/SKILL.md) · [`agentic-loop-runbook`](.cursor/skills/agentic-loop/SKILL.md) | — (optional: consumer domain skill) | Wiki + ticket context present |
| **0b** | Ticket ack | Jira → In Progress; PagerDuty investigation note (ops) | Orchestrator · Atlassian / PagerDuty MCP | — | Ticket acknowledged |
| **1** | Plan | Feature: `/ce-plan` + mandatory test matrix. Ops: hypothesis in STATE | `ce-plan` (Compound Engineering) | [jabrena-302](.cursor/rules/external/jabrena-302-java-testing-fundamentals.mdc), [jabrena-311](.cursor/rules/external/jabrena-311-spring-boot-slice-testing.mdc), [jabrena-312](.cursor/rules/external/jabrena-312-spring-boot-integration-testing.mdc) | Test matrix drafted |
| **2** | Plan review | `ce-testing-reviewer` on matrix; ops evidence check | `ce-testing-reviewer` | [jabrena-302](.cursor/rules/external/jabrena-302-java-testing-fundamentals.mdc), [jabrena-311](.cursor/rules/external/jabrena-311-spring-boot-slice-testing.mdc), [jabrena-312](.cursor/rules/external/jabrena-312-spring-boot-integration-testing.mdc) | **L1 STOP** — human approves before Phase 3 |
| **3** | Implement | `/ce-work` in target repo; match standards | `ce-work` | [java-springboot-standards.mdc](.cursor/rules/java-springboot-standards.mdc), [service-quality-drill.mdc](.cursor/rules/service-quality-drill.mdc) | Human approved plan |
| **4** | Verify | Build, JaCoCo, diff coverage; maker/checker split | [`loop-verifier`](.cursor/agents/loop-verifier.md) · [`loop-verifier` skill](.cursor/skills/loop-verifier/SKILL.md) | [service-quality-drill.mdc](.cursor/rules/service-quality-drill.mdc), [jabrena-302](.cursor/rules/external/jabrena-302-java-testing-fundamentals.mdc), [jabrena-311](.cursor/rules/external/jabrena-311-spring-boot-slice-testing.mdc), [jabrena-312](.cursor/rules/external/jabrena-312-spring-boot-integration-testing.mdc) | Build green; JaCoCo ≥ profile ratio |
| **5** | Code review | PR path: [pr-code-review.mdc](.cursor/rules/pr-code-review.mdc). Else: `ce-code-review` vs `main` | `ce-code-review` · Bugbot · [`pr-code-review.mdc`](.cursor/rules/pr-code-review.mdc) | [java-springboot-standards](.cursor/rules/java-springboot-standards.mdc), [service-quality-drill](.cursor/rules/service-quality-drill.mdc), [terraform-standards](.cursor/rules/terraform-standards.mdc) (by `pr_type`) | No open P0/P1 on net-new findings |
| **6** | Ship | Squash, push feature branch, PR, CI babysit (max 3) | `commit-push-pr` + `babysit` · [`loop-budget`](.cursor/skills/loop-budget/SKILL.md) | [service-quality-drill.mdc](.cursor/rules/service-quality-drill.mdc) | **L3-push** + human ship approval |
| **7** | PR hygiene | Copilot/CodeQL threads: fix → test → reply → resolve | `ce-resolve-pr-feedback` | [service-quality-drill.mdc](.cursor/rules/service-quality-drill.mdc) | All review threads resolved |
| **8** | Close-the-loop | Jira comment: summary, tests, SHA, PR link, AC map | `jira-close-loop.sh` | — | Jira updated |
| **9** | Wiki + compound | Append wiki log; refresh status; update knowledge graph | `ce-compound` · [LLM-wiki](https://github.com/Ss1024sS/LLM-wiki) · [graphify](https://github.com/safishamsi/graphify) | — | Durable learnings written back |

### Phase 0 — Context sync (detail)

**Purpose:** Eliminate cold-start amnesia. The agent reads durable state before planning.

**Actions:**
- Read `docs/wiki/index.md`, `current-status.md`, `log.md` ([LLM-wiki](https://github.com/Ss1024sS/LLM-wiki))
- Run `knowledge-graph query "<topic>"` on touched repos ([graphify](https://github.com/safishamsi/graphify))
- Fetch Jira / Confluence via Atlassian MCP
- Load profile `context_skill` if defined
- Write snapshot to `loop-kit/<profile>-state.md`

**Delegated to:** [`loop-triage`](.cursor/skills/loop-triage/SKILL.md)

### Phase 0b — Ticket ack (detail)

**Purpose:** Signal work has started on the tracked ticket.

**Actions:** Jira transition to In Progress; PagerDuty incident note for ops runs.

### Phase 1 — Plan (detail)

**Purpose:** Produce an implementation plan with an explicit **test matrix** (required gate in [`loop-kit/GATES.md`](loop-kit/GATES.md)).

**Delegated to:** `ce-plan` (Compound Engineering)

**Rules:** [`jabrena-302-java-testing-fundamentals.mdc`](.cursor/rules/external/jabrena-302-java-testing-fundamentals.mdc), [`jabrena-311`](.cursor/rules/external/jabrena-311-spring-boot-slice-testing.mdc), [`jabrena-312`](.cursor/rules/external/jabrena-312-spring-boot-integration-testing.mdc) — naming, slice vs integration test design.

**Ops variant:** Hypothesis doc in `STATE.md` (symptom, timeline, suspects, next Datadog/PagerDuty queries).

### Phase 2 — Plan review (detail)

**Purpose:** Independent review of the test matrix and plan quality before any code changes.

**Delegated to:** `ce-testing-reviewer`

**Human gate:** Default **L1 stops here**. User must approve (e.g. “proceed with implementation”) before Phase 3.

### Phase 3 — Implement (detail)

**Purpose:** Execute the approved plan in the target repo.

**Delegated to:** `ce-work`

**Rules:**
- [`java-springboot-standards.mdc`](.cursor/rules/java-springboot-standards.mdc) — layering, ArchUnit, Spring Boot 4 patterns
- [`service-quality-drill.mdc`](.cursor/rules/service-quality-drill.mdc) — build discipline, regression tests per thread

**Skipped** in `ops-incident` L1 (investigate-only).

### Phase 4 — Verify (detail)

**Purpose:** Maker/checker verification — a **different** agent/skill than the implementer.

**Delegated to:** [`loop-verifier`](.cursor/agents/loop-verifier.md) agent + [`loop-verifier`](.cursor/skills/loop-verifier/SKILL.md) skill

**Scripts:**
```bash
.cursor/skills/agentic-loop/scripts/gradle-build.sh <repo>
.cursor/skills/agentic-loop/scripts/parse-jacoco.sh <repo> <ratio>
```

**Rules:** [service-quality-drill.mdc](.cursor/rules/service-quality-drill.mdc) (JaCoCo gate), [jabrena-302](.cursor/rules/external/jabrena-302-java-testing-fundamentals.mdc), [jabrena-311](.cursor/rules/external/jabrena-311-spring-boot-slice-testing.mdc), [jabrena-312](.cursor/rules/external/jabrena-312-spring-boot-integration-testing.mdc) (test coverage alignment)

**Gate:** `./gradlew clean build` green; JaCoCo line ratio ≥ profile `jacoco_line_ratio` (default 0.80).

### Phase 5 — Code review (detail)

**Purpose:** Diff-only review with deduplication against existing PR threads.

**Two paths** (see [Diagram 4](#4-phase-5-branch---pr-vs-normal) below):

| Path | Trigger | Workflow |
|------|---------|----------|
| **PR review** | `--pr <n>` or GitHub PR URL | Full [`pr-code-review.mdc`](.cursor/rules/pr-code-review.mdc): Phase 0a–0f, Pass 1–3 by `pr_type`, synthesis table |
| **Normal** | No `--pr` | `ce-code-review` vs `main`; fix P0/P1 before ship |

**`pr_type` routing (Pass 3):**

| `pr_type` | Pass 3 applies |
|-----------|----------------|
| `java-only` | [java-springboot-standards](.cursor/rules/java-springboot-standards.mdc) + ArchUnit + [service-quality-drill](.cursor/rules/service-quality-drill.mdc) |
| `infra-only` | [terraform-standards](.cursor/rules/terraform-standards.mdc) + observability checks; no JaCoCo |
| `mixed` | Segmented Java + infra; `Cross-cutting` for TF↔Java links |

**Default for `--pr`:** L1 report-only (`net_new_count` / `suppressed_count` table; no auto-fix).

**Phase 7 + `--pr`** = thread hygiene only — not a substitute for Phase 5.

### Phase 6 — Ship (detail)

**Purpose:** Push feature branch, open/update PR, babysit CI.

**Delegated to:** `commit-push-pr` + `babysit` skills; budget check via [`loop-budget`](.cursor/skills/loop-budget/SKILL.md)

**Script:** `gh-pr-checks-watch.sh` — max **3** remote CI cycles per PR

**Rules:** [service-quality-drill.mdc](.cursor/rules/service-quality-drill.mdc) (required checks: lint, build-and-test, Trivy, dependency-review, gitleaks, CodeQL)

**Requires:** `--mode L3-push` + explicit human “push” approval. Never merges to `main`.

### Phase 7 — PR hygiene (detail)

**Purpose:** Close Copilot/CodeQL review threads after green CI.

**Delegated to:** `ce-resolve-pr-feedback` — implement fix → cite test → reply → resolve thread.

### Phase 8 — Close-the-loop (detail)

**Purpose:** Link code, tests, and ticket in one durable Jira comment.

**Script:** `jira-close-loop.sh <JIRA-KEY> <PR-url> <SHA> [test-names]`

### Phase 9 — Wiki + compound (detail)

**Purpose:** Write durable learnings back so the next session starts warm.

**Actions:**
- Append `docs/wiki/log.md`; refresh `current-status.md` (LLM-wiki)
- `knowledge-graph update <repo>` (graphify)
- `/ce-compound` when architectural learnings exist


<!-- EXPORT:phase-table-9d:start -->
| **9d** | Self-improvement | TOON contract → apply engine; local preflight gate | [`loop-self-improvement`](.cursor/skills/loop-self-improvement/SKILL.md) · `apply-loop-learning.sh` | — | L2/L3 · `PENDING_APPROVAL` STOP |
<!-- EXPORT:phase-table-9d:end -->


<!-- EXPORT:phase-9d:start -->
### Phase 9d (self-improvement)

L2/L3 only. TOON contract → `apply-loop-learning.sh --contract`. See `loop-kit/contracts/README.md`.

**Local preflight** (before validate and approve):

```bash
python3 -m venv .venv-loop-9d && .venv-loop-9d/bin/pip install -r scripts/requirements-loop-9d.txt
export CURSOR_PROJECT_DIR="$(pwd)"
./scripts/loop_9d_preflight.sh
```

**Run-log token:**

```text
9d-preflight: ok | 9d: PENDING_APPROVAL → APPLY_SUCCESS | staging=<path> | branch=<name>
```
<!-- EXPORT:phase-9d:end -->


<!-- EXPORT:tools-table:start -->
| Tool | Role |
|------|------|
| `loop_9d_preflight.sh` | Local 9d gate (venv auto-detect) |
| `loop_9d_conformance_check.py` | Doc parity / verbatim blocks |
| `loop_9d_coverage_check.py` | Apply-engine coverage gate |
| `apply-loop-learning.sh` | TOON contract apply |
| `loop-self-improvement` skill | Phase 9d extraction |
| CE: `ce-doc-review`, `ce-debug`, `ce-compound-refresh` | Optional selective plugins |
| LLM-wiki, graphify | Companion setup |
| `npx @cobusgreyling/loop-audit` | Setup validation |
<!-- EXPORT:tools-table:end -->


<!-- EXPORT:diagram-9d-state:start -->
```mermaid
flowchart TD
  preflight[9d_preflight] --> validate[validate PENDING_APPROVAL]
  validate --> stop[Human STOP]
  stop --> preflight2[preflight again]
  preflight2 --> approve[approve APPLY_SUCCESS]
```
<!-- EXPORT:diagram-9d-state:end -->


<!-- EXPORT:diagram-9d-control:start -->
```mermaid
flowchart LR
  applyEngine[apply_loop_learning.py]
  preflight[loop_9d_preflight.sh]
  conformance[loop_9d_conformance_check]
  coverage[loop_9d_coverage_check]
  preflight --> conformance
  preflight --> coverage
  applyEngine --> coverage
```
<!-- EXPORT:diagram-9d-control:end -->


<!-- EXPORT:diagram-export-boundary:start -->
```mermaid
flowchart TB
  kit[agentic-loop-engineering-kit]
  consumer[Consumer monorepo]
  kit -->|copy loop-kit + .cursor| consumer
  consumer -->|docs/loop-learnings runtime| consumer
```
<!-- EXPORT:diagram-export-boundary:end -->

---
## Full HELP

```
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
  /agentic-loop --profile springboot-default --repo backend-repo PROJ-123
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

## Standards index

| Rule | When | Phase |
|------|------|-------|
| [java-springboot-standards.mdc](.cursor/rules/java-springboot-standards.mdc) | Java/Spring Boot code | 3, 4, 5 |
| [service-quality-drill.mdc](.cursor/rules/service-quality-drill.mdc) | Build, JaCoCo, CI | 4, 6, 7 |
| [pr-code-review.mdc](.cursor/rules/pr-code-review.mdc) | PR review target | 5 |
| [terraform-standards.mdc](.cursor/rules/terraform-standards.mdc) | Infra / mixed PRs | 5 |
| [jabrena-302](.cursor/rules/external/jabrena-302-java-testing-fundamentals.mdc), [jabrena-311](.cursor/rules/external/jabrena-311-spring-boot-slice-testing.mdc), [jabrena-312](.cursor/rules/external/jabrena-312-spring-boot-integration-testing.mdc) | Test design | 1, 2, 4 |

Verify rules:

```bash
find .cursor/rules -name '*.mdc' | sort
test "$(find .cursor/rules -name '*.mdc' | wc -l | tr -d ' ')" -eq 7
```

## Folder structure

```text
agentic-loop-engineering-kit/
├── README.md
├── LICENSE
├── LOOP.md
├── STATE.md
├── loop-budget.md
├── loop-run-log.md
├── docs/
│   ├── HELP.md
│   ├── safety.md
│   └── standards/
│       └── README.md
├── loop-kit/
│   ├── ARCHITECTURE.md
│   ├── LOOP.md
│   ├── GATES.md
│   ├── STATE.md
│   ├── loop-budget.md
│   ├── loop-run-log.md
│   ├── feature-state.md
│   ├── ops-incident-state.md
│   ├── patterns/feature-loop-example.md
│   └── profiles/
│       ├── README.md
│       ├── springboot-default.yaml
│       └── ops-incident.yaml
├── patterns/registry.yaml
└── .cursor/
    ├── commands/agentic-loop.md
    ├── agents/
    │   ├── agentic-loop-orchestrator.md
    │   └── loop-verifier.md
    ├── skills/
    │   ├── agentic-loop/SKILL.md + scripts/ (6)
    │   ├── loop-triage/SKILL.md
    │   ├── loop-verifier/SKILL.md
    │   ├── loop-budget/SKILL.md
    │   └── ops-incident-loop/SKILL.md
    ├── rules/
    │   ├── java-springboot-standards.mdc
    │   ├── service-quality-drill.mdc
    │   ├── pr-code-review.mdc
    │   ├── terraform-standards.mdc
    │   └── external/jabrena-302|311|312*.mdc
    ├── hooks.json + hooks/*.sh
    └── mcp.agentic-loop.template.json
```

## Architecture

Seven diagrams describe how the kit fits together. Read top-to-bottom: entry → routing → phase machine → PR branch → profiles → roles → failure handling.

### 1. System layers (bird's-eye)

Shows every layer from slash command to MCP connectors. The orchestrator stays in Plan mode; all implementation is delegated.

```mermaid
flowchart TB
  subgraph entry [Entry]
    CMD["/agentic-loop command"]
    HELP["--help only"]
  end
  subgraph orchestration [Orchestration Plan mode only]
    ORCH["agentic-loop-orchestrator agent"]
    RUNBOOK["agentic-loop-runbook SKILL.md"]
  end
  subgraph config [Configuration]
    PROFILES["YAML profiles loop-kit/profiles/"]
    GATES["GATES.md"]
    BUDGET["loop-budget.md"]
  end
  subgraph state [Durable state]
    STATE["STATE.md"]
    FEAT["feature-state.md"]
    OPS["ops-incident-state.md"]
    LOG["loop-run-log.md"]
  end
  subgraph delegates [Delegated skills]
    TRIAGE["loop-triage"]
    PLAN["ce-plan + ce-testing-reviewer"]
    WORK["ce-work"]
    VERIFY["loop-verifier"]
    PREVIEW["pr-code-review.mdc"]
    CEREV["ce-code-review"]
    SHIP["commit-push-pr + babysit"]
    HYGIENE["ce-resolve-pr-feedback"]
    COMPOUND["ce-compound"]
  end
  subgraph tooling [Scripts and hooks]
    SCRIPTS["gradle-build parse-jacoco gh-pr-checks-watch"]
    HOOKS["block-dangerous-git block-denylist-edits"]
  end
  subgraph external [External MCP]
    JIRA["Atlassian"]
    GH["GitHub"]
    DD["Datadog"]
    PD["PagerDuty"]
  end
  CMD --> ORCH
  HELP --> CMD
  ORCH --> RUNBOOK
  RUNBOOK --> PROFILES
  RUNBOOK --> GATES
  RUNBOOK --> BUDGET
  ORCH --> STATE
  ORCH --> delegates
  delegates --> SCRIPTS
  delegates --> external
  SCRIPTS --> HOOKS
```

| Layer | Artifacts |
|-------|-----------|
| Entry | `.cursor/commands/agentic-loop.md` |
| Orchestration | `.cursor/agents/agentic-loop-orchestrator.md`, `.cursor/skills/agentic-loop/SKILL.md` |
| Config | `loop-kit/profiles/*.yaml`, `loop-kit/GATES.md`, `loop-budget.md` |
| State | `STATE.md`, `loop-kit/*-state.md`, `loop-run-log.md` |
| Delegates | `loop-triage`, `loop-verifier`, `loop-budget`, Compound Engineering plugins |
| Tooling | `agentic-loop/scripts/*`, `.cursor/hooks/*.sh` |

### 2. Invocation routing

How flags and targets determine which phases run and which mode applies.

```mermaid
flowchart LR
  INV["Invocation"] --> PARSE["Parse flags and target"]
  PARSE --> H{"--help or no target?"}
  H -->|yes| HELP["Print HELP stop"]
  H -->|no| PLAN["SwitchMode plan"]
  PLAN --> LOAD["Load profile YAML"]
  LOAD --> TARGET{"Target type?"}
  TARGET -->|JIRA-KEY| FULL["Full loop Phases 0-9"]
  TARGET -->|"--pr or PR URL"| P5["Jump Phase 5 pr-code-review"]
  TARGET -->|"--phase N"| RESUME["Resume at phase N"]
  TARGET -->|ops flags| OPS["ops-incident L1"]
  TARGET -->|handoff| HANDOFF["Ops to feature preload STATE"]
  FULL --> MODE{"--mode?"}
  MODE -->|L1| L1["Phases 0-2 only"]
  MODE -->|L2| L2["Through review"]
  MODE -->|L3-push| L3["Push and CI babysit"]
```

| Target | Route |
|--------|-------|
| `<JIRA-KEY>` | Full feature loop; mode caps depth |
| `--pr` / PR URL | Jump to Phase 5 (`pr-code-review.mdc`) |
| `--phase N` | Resume (orchestrator validates prerequisites) |
| `--pagerduty` / `--datadog-monitor` | `ops-incident` profile, L1 default |
| `--handoff` + `--from-state` | Ops → feature; preload STATE |

### 3. Phase machine (feature profiles)

Full 0–9 sequence with human gates. L1 stops after Phase 2. Failure Router edges are recommend-only (dashed).

```mermaid
flowchart TD
  START(["/agentic-loop --profile X TARGET"]) --> P0
  P0["Phase 0 Context sync"]
  P0b["Phase 0b Ticket ack"]
  P1["Phase 1 Plan"]
  P2["Phase 2 Plan review"]
  P3["Phase 3 Implement"]
  P4["Phase 4 Verify"]
  P5["Phase 5 Code review"]
  P6["Phase 6 Ship"]
  P7["Phase 7 PR hygiene"]
  P8["Phase 8 Close-the-loop"]
  P9["Phase 9 Wiki and compound"]
  P0 --> P0b --> P1 --> P2
  P2 --> GATE1{{"Human gate approve plan?"}}
  GATE1 -->|L1 or no| STOP1["STOP Plan mode"]
  GATE1 -->|yes| P3
  P3 --> GATE2{{"Human gate approve verify?"}}
  GATE2 -->|no| STOP2["STOP"]
  GATE2 -->|yes| P4
  P4 --> P5 --> P6
  P6 --> GATE3{{"Human gate L3-push?"}}
  GATE3 -->|no| STOP3["STOP at PR draft"]
  GATE3 -->|yes| P6RUN["push and CI babysit max 3"]
  P6RUN --> P7 --> P8 --> P9 --> DONE(["Done human merges PR"])
  P4 -.->|fail| FR["Failure Router recommend only"]
  P5 -.->|P0 P1| FR
  P6RUN -.->|CI red| FR
```

| Gate | When | L1 behaviour |
|------|------|--------------|
| After Phase 2 | Plan approved? | **STOP** — no code |
| Before Phase 4 | Implementation approved? | N/A in L1 |
| Before Phase 6 | Ship approved? | N/A unless L3-push |

### 4. Phase 5 branch (--pr vs normal)

Phase 5 splits on whether a PR number or URL was provided.

```mermaid
flowchart TD
  P5IN["Phase 5 entry"] --> PRCHK{"--pr or PR URL?"}
  PRCHK -->|no| CEREV["ce-code-review vs main"]
  PRCHK -->|yes| P0A["0a-0d PR metadata Jira threads"]
  P0A --> P0E["0e pr_type java infra mixed"]
  P0E --> P0F["0f feedback registry dedup"]
  P0F --> PASS1["Pass 1 ce-code-review"]
  PASS1 --> PASS2["Pass 2 Bugbot"]
  PASS2 --> ROUTE{"pr_type"}
  ROUTE -->|java-only| J3["Pass 3 java-springboot ArchUnit drill"]
  ROUTE -->|infra-only| I3["Pass 3 terraform observability"]
  ROUTE -->|mixed| M3["Pass 3 segmented Java and Infra"]
  J3 --> SYNTH
  I3 --> SYNTH
  M3 --> SYNTH["Synthesis net-new table"]
  SYNTH --> VERDICT["Verdict L1 report only default"]
```

| Step | Skill / rule |
|------|----------------|
| 0a–0d | PR metadata, Jira, scenario matrix, thread ingestion |
| 0e | `pr_type` from `gh pr diff --name-only` |
| 0f | Existing-feedback registry (dedup) |
| Pass 1–2 | `ce-code-review`, Bugbot |
| Pass 3 | `java-springboot-standards` / `terraform-standards` / `service-quality-drill` by `pr_type` |
| Synthesis | `net_new_count`, `suppressed_count`, verdict table |

### 5. Profile model

YAML profiles compose behaviour. Extend `springboot-default` for your services.

```mermaid
flowchart LR
  subgraph profiles [YAML profiles]
    DEFAULT["springboot-default JaCoCo 0.80"]
    OPS["ops-incident L1 investigate"]
    CUSTOM["my-service.yaml extends default"]
  end
  DEFAULT --> CUSTOM
  OPS --> OPSSKILL["ops-incident-loop skill"]
  profiles --> REPOS["repos jacoco phases_enabled ship default_mode L1"]
```

| Profile | `default_mode` | Phases | Key fields |
|---------|----------------|--------|------------|
| `springboot-default` | L1 | 0–9 | `jacoco_line_ratio: 0.80`, `rules:` (6 Java/Spring rules) |
| `ops-incident` | L1 | 0–2 (L2+: 0–9) | Datadog/PagerDuty MCP, `terraform-standards` on handoff |
| `my-service.yaml` | inherits | extends parent | `repos`, custom `context_skill` |

### 6. Maker/checker split (roles)

The orchestrator never implements and verifies with the same model instance.

```mermaid
flowchart TB
  subgraph roles [Never same model on implement and verify]
    ORCH2["agentic-loop-orchestrator Plan only"]
    PLANNER["Planner ce-plan"]
    REVIEWER["Plan Reviewer ce-testing-reviewer"]
    IMPL["Implementer ce-work"]
    VERIFIER["Verifier loop-verifier"]
    CODREV["Code Reviewer ce-code-review or pr-code-review"]
    SHIPPER["Ship commit-push-pr babysit"]
  end
  ORCH2 --> PLANNER
  ORCH2 --> REVIEWER
  ORCH2 --> IMPL
  ORCH2 --> VERIFIER
  ORCH2 --> CODREV
  ORCH2 --> SHIPPER
  IMPL -.-> VERIFIER
  IMPL -.-> CODREV
```

| Role | Must not also be |
|------|------------------|
| `ce-work` (implement) | `loop-verifier` (verify) on same change |
| `ce-work` (implement) | `ce-code-review` / `pr-code-review` on same change |

### 7. Failure Router (recommend-only)

Classifies failures and **recommends** the next phase. Never auto-re-dispatch — human confirms in chat.

```mermaid
flowchart LR
  FAIL["Failure signal"] --> CLASSIFY{"Classify"}
  CLASSIFY -->|JaCoCo or delta| T4["Phase 4 then 3"]
  CLASSIFY -->|local build| T3["Phase 3"]
  CLASSIFY -->|arch failures| T1["Phase 1"]
  CLASSIFY -->|review P0 P1| T3b["Phase 3"]
  CLASSIFY -->|remote CI le 3| T6["Phase 6 babysit"]
  CLASSIFY -->|remote CI gt 3| T1b["Phase 1 plus CI logs"]
  CLASSIFY -->|plan gap| T1c["Phase 1"]
  CLASSIFY -->|infra flake| INBOX["STATE.md inbox"]
  T4 --> WAIT["Present recommendation wait for human"]
  T3 --> WAIT
  T1 --> WAIT
  T3b --> WAIT
  T6 --> WAIT
  T1b --> WAIT
  T1c --> WAIT
  INBOX --> WAIT
```

| Signal | Recommend | Typical skill |
|--------|-----------|---------------|
| JaCoCo / delta coverage fail | Phase 4 → 3 (add tests) | `loop-verifier` → `ce-work` |
| Local build fail | Phase 3 | `ce-work` |
| Remote CI fail (≤3 cycles) | Phase 6 babysit | `gh-pr-checks-watch.sh` |
| Remote CI fail (>3) | Phase 1 + CI logs in STATE | `ce-plan` |
| AC / plan gap | Phase 1 | `ce-plan` |
| Infra flake / secrets | `STATE.md` human inbox | — |

---
## Profiles

- springboot-default — Gradle Java/Spring Boot; requires --repo
- ops-incident — Datadog/PagerDuty L1 investigation
- Extend with loop-kit/profiles/my-service.yaml

## External dependencies

| Dependency | Role |
|------------|------|
| [Compound Engineering](https://github.com/compound-engineering) | `ce-plan`, `ce-work`, `ce-code-review`, `ce-compound` |
| [loop-engineering](https://github.com/cobusgreyling/loop-engineering) + [loop-audit](https://www.npmjs.com/package/@cobusgreyling/loop-audit) | L0→L1 readiness scoring |
| [LLM-wiki](https://github.com/Ss1024sS/LLM-wiki) | Wiki-first memory (Phase 0 / 9) — **recommended** |
| [graphify](https://github.com/safishamsi/graphify) | Codebase knowledge graph (Phase 0 / 9) — **recommended** |
| Cursor MCP | Atlassian, GitHub, Datadog, PagerDuty (per profile) |

## License

Apache-2.0 — see LICENSE.


















