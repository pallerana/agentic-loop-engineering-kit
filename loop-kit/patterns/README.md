# Agent Loop Patterns

Repo-specific quirks, failures, and AC→test maps for Phase 0 read and Phase 9d write.

## Playbooks

| File | Profile | Role |
|------|---------|------|
| [cell-health-feature-loop.md](./cell-health-feature-loop.md) | `cell-health` | Loop playbook — entry, phases, verify/ship |

## Pattern docs (`*-patterns.md`)

| File | Profile | Repo(s) |
|------|---------|---------|
| [cell-health-patterns.md](./cell-health-patterns.md) | `cell-health` | aggregator, central |
| [cellrouter-patterns.md](./cellrouter-patterns.md) | `cellrouter` | http cell router |
| [cellassignments-patterns.md](./cellassignments-patterns.md) | `cellassignments` | assignments API |
| [celldiscovery-patterns.md](./celldiscovery-patterns.md) | `celldiscovery` | discovery API |
| [cellmigrator-patterns.md](./cellmigrator-patterns.md) | `cellmigrator` | migrator API |
| [cellpersistence-patterns.md](./cellpersistence-patterns.md) | `cellpersistence` | ODP persistence API |
| [ops-incident-patterns.md](./ops-incident-patterns.md) | `ops-incident` | cross-cutting |

## Phase 0

When profile YAML has `pattern_doc` → read it (active repo subsection for multi-repo profiles).

When profile has `loop_playbook` → read it (cell-health today).

## Phase 9d

Learnings append via TOON contract + `apply-loop-learning.sh`. See [`../contracts/README.md`](../contracts/README.md).
