---
name: loop-triage
description: >-
  Agentic Loop Engineering Kit Phase 0–0b — context sync, wiki/Jira/Confluence, knowledge-graph, ticket ack.
  Delegates to agentic-loop-runbook; used by loop-audit triage signal.
---

# Loop Triage

Thin wrapper for **Phase 0** and **Phase 0b** of the Agentic Loop Engineering Kit.

**Full runbook:** [`.cursor/skills/agentic-loop/SKILL.md`](../agentic-loop/SKILL.md) via `/agentic-loop`.

## Hard rules

- **Plan mode only** — `SwitchMode(plan)` before any work
- **L1 default** — no code or git mutations unless user approves L2+
- Stop on ambiguity → [`STATE.md`](../../../loop-kit/STATE.md) human inbox

## Phase 0 checklist

- [ ] `python3 scripts/version_check.py`
- [ ] Wiki: `index.md`, `current-status.md`, `log.md`
- [ ] Load profile YAML from `loop-kit/profiles/<profile>.yaml`
- [ ] Profile `context_skill` if set (e.g. `your-domain-skill` Phase 0)
- [ ] Jira / Confluence per profile
- [ ] `knowledge-graph query` for touched repos
- [ ] Update `loop-kit/<profile>-state.md`

## Phase 0b — Ticket ack

- Jira: transition to **In Progress** (Atlassian MCP or `acli`)
- Ops: PagerDuty incident note

## Log run

```bash
.cursor/skills/agentic-loop/scripts/update-loop-state.sh <profile> 0|0b <outcome> <target>
```

## Handoff

After triage, stop for human review (plan-mode-first). Continue with `/agentic-loop` Phase 1+ only when user approves.
