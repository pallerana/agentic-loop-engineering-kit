# Loop budget

Shared caps for all Agentic Loop Engineering Kit profiles. Orchestrator must stop and record in STATE when exceeded.

| Resource | Cap | Notes |
|----------|-----|-------|
| Remote CI babysit | **3** cycles per PR | Then → planner with logs |
| Local build retry | **5** per phase | Then → human inbox |
| Planner re-entry | **2** arch failures | Then → human inbox |
| Ops L1 duration | **1 session** | Handoff or human gate for L2 |
| `act` local CI | optional | Skip if `act` not installed |
| Token / context | use `CONTINUATION-SUMMARY.md` | After phase boundary |
| Plan-mode sessions | 1 Phase 0–2 block | Human gate before Phase 3+ |

## Model hints (pilot)

| Role | Suggested model |
|------|-----------------|
| Orchestrator | opus thinking |
| Implementer (`ce-work`) | sonnet / codex |
| Review | dedicated review subagents |

Tune after `loop-audit --suggest` and pilot on PROJ-123/156.
