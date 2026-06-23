# Agent Loop — Gates

Quality gates and Failure Router reference for the Agentic Loop Engineering Kit orchestrator.

## Phase gates

| Phase | Gate | Block if |
|-------|------|----------|
| 0 | Context | Wiki + Jira/Confluence not synced |
| 0b | Ack | Ticket not In Progress / no PD note |
| 1 | Plan | No `/ce-plan` output or ops hypothesis |
| 2 | Review | `ce-testing-reviewer` fails test matrix (feature) |
| 3 | Implement | — |
| 4 | Verify | Build fail, JaCoCo below profile ratio, delta gap |
| 5 | Review | **With `--pr` or PR URL:** `pr-code-review` complete — `pr_type` set, registry in Functional Context, `net_new_count` reported; no open P0/P1 on net-new findings. **Without `--pr`:** ce-code-review P0/P1 open |
| 6 | Ship | Push/PR fail; CI not green after 3 babysit |
| 7 | Hygiene | Unresolved Copilot/CodeQL threads |
| 8 | Close | No Jira comment with tests + SHA |
| 9 | Wiki | log.md / knowledge-graph not updated |

## JaCoCo

| Profile | Line ratio | Source |
|---------|------------|--------|
| `my-service` | **1.00** | `build.gradle.kts` in aggregator + central |
| `springboot-default` + repo profiles | **0.80** typical | per-repo `build.gradle.kts` |

Script: `.cursor/skills/agentic-loop/scripts/parse-jacoco.sh <repo> <ratio>`

## Phase 5 — PR review gates (`--pr` or PR URL)

When `--pr <n>` or a GitHub PR URL triggers `@pr-code-review`:

| `pr_type` | Pass 3 | Phase 4-style gates (optional L2 verify) |
|-----------|--------|------------------------------------------|
| **java-only** | `java-springboot-standards` + ArchUnit + drill Pass 3a–3d | `./gradlew clean build`, JaCoCo per profile, CI checks |
| **infra-only** | `terraform-standards` + observability wiki when DDog touched | `terraform fmt` / `validate` if `.tf` changed; **no** JaCoCo / gradle; **no** `terraform apply` |
| **mixed** | Segmented Java + infra; `Cross-cutting` for TF↔Java links | Per-segment: Java gates on Java hunks only; infra gates on TF/workflow hunks |

**Functional Context must include:**

- `pr_type` from Phase 0e
- **Existing feedback registry** from Phase 0f (open / resolved / bot counts)
- Findings table with `net_new_count` and `suppressed_count`

**Phase 5 complete when:** net-new findings table delivered; P0/P1 on net-new items addressed or explicitly accepted by human (L1).

**Phase 7 distinction:** `--phase 7 --pr` = thread hygiene (`ce-resolve-pr-feedback`) only — not a substitute for Phase 5 review.

## Delta / diff coverage

New or changed **production** lines in the PR diff must have test coverage unless explicitly excluded in `build.gradle.kts` JaCoCo config.

**On fail:** Failure Router → test-repair (add tests) → implementer.

## CI babysit

- Max **3** remote CI watch cycles per PR (`gh-pr-checks-watch.sh`).
- Required checks: `lint`, `build-and-test`, `Trivy`, `dependency-review`, `gitleaks`, `CodeQL` (per `service-quality-drill.mdc`).

## Mandatory test matrix (Phase 1 / Phase 2)

Every feature `/ce-plan` must include this table. **Phase 2** runs `ce-testing-reviewer` against it.

```markdown
## Test matrix

| ID | Scenario | Type | Layer | Assert |
|----|----------|------|-------|--------|
| T1 | Happy path — primary AC | positive | unit/integration | … |
| T2 | Invalid input / 400 | negative | WebMvcTest/unit | … |
| T3 | Downstream timeout / 503 | exception | WireMock/integration | … |
| T4 | Boundary (empty, max size) | edge | unit | … |
| T5 | Contract / HTTP surface | integration | WebMvcTest or IT | … |
```

**Types:** positive, negative, exception, edge, integration.

**Reviewer checklist (`ce-testing-reviewer`):**

- Every AC row maps to ≥1 test ID
- Negative and exception paths present for new endpoints
- No implementation-only tests without behavior assertion
- ArchUnit / layer rules unchanged or explicitly justified

## Failure Router

| Failure signal | Classification | Restart phase | Max retries |
|----------------|----------------|---------------|-------------|
| JaCoCo below ratio | coverage | 4 → 3 | per loop-budget |
| Delta coverage gap | coverage | 4 → 3 | 5 local builds |
| `./gradlew clean build` fail | local CI | 3 | 5 |
| 2+ architectural compile/design failures | plan gap | 1 | 2 |
| ce-code-review P0/P1 | review | 3 | — |
| Remote CI fail | remote CI | 6 babysit | **3** |
| Remote CI fail after 3 | plan/infra | 1 + STATE | human |
| AC missing from plan | plan gap | 1 | — |
| Datadog/PagerDuty infra flake | ops | STATE human inbox | — |
| Secrets / permissions | human | STATE | — |

## Anti-patterns (do not)

- Skip Phase 0 Confluence/Jira sync
- Push to `main` or `git push --force`
- `terraform apply` inside the loop
- Merge PR without human approval (L3-push stops at green CI)
- Standalone Testing Agent (use matrix + `ce-testing-reviewer` instead)
- Standalone Jira Agent (use Phase 0b + 8)

## Ops-incident gates (L1)

| Phase | Gate |
|-------|------|
| 0 | Datadog + PagerDuty context captured in `ops-incident-state.md` |
| 1 | Hypothesis doc with evidence links |
| 2 | Human review before L2 fix scope |

L2+ uses feature gates after `--handoff`.

## Human gates (plan-mode-first)

Mandatory stops — orchestrator must not proceed without explicit user approval in chat:

| Gate | When | Action if not approved |
|------|------|------------------------|
| Plan review | After Phase 2 | Stop; remain in Plan mode |
| Implementation | Before Phase 3 | Stop; no code changes |
| Verify | Before Phase 4 scripts | Stop; no gradle/jacoco runs |
| Ship | Before Phase 6 push | Stop at PR draft (L2 max) |
| L3-push | Before `git push` | Stop until user says "push" |

**Ambiguity stops** (never guess):

- Ambiguous Jira AC → `STATE.md` inbox
- Repo not in profile `repos` → ask user
- Deferral spike in scope → ask user
- `--mode L3-push` without ship approval → stop at L2

## Failure Router (recommend only)

Router **classifies** and **recommends** — does **not** auto-re-dispatch in plan-mode-first mode. Present recommendation; wait for human.
