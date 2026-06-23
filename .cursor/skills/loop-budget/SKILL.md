---
name: loop-budget
description: >-
  Enforce Agentic Loop Engineering Kit budget caps — CI babysit, build retries, planner re-entry.
  Read loop-budget.md; stop and write STATE inbox when exceeded.
---

# Loop Budget

Runtime budget guard for Agentic Loop Engineering Kit. Canonical caps: [`loop-budget.md`](../../../loop-kit/loop-budget.md) (root symlink).

## Caps

| Resource | Cap | On exceed |
|----------|-----|-----------|
| Remote CI babysit | 3 per PR | STATE inbox + recommend Phase 1 with logs |
| Local build retry | 5 per phase | STATE inbox |
| Planner re-entry | 2 arch failures | STATE inbox |
| Ops L1 | 1 session | Handoff or human gate |

## Usage

Before Phase 6 ship or retry loops:

1. Read active profile state + `loop-run-log.md` attempt counts
2. If at cap → stop, append human inbox row in `STATE.md`
3. Log via `update-loop-state.sh`

## Kill switch

If `loop-pause: true` in profile state frontmatter or human inbox has open blocker → **stop loop**.

## Plan-mode

Budget checks run in Plan mode; present cap status to user before approving next phase.
