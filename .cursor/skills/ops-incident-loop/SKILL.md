---
name: ops-incident-loop
description: >-
  Ops-incident profile extension for Agentic Loop Engineering Kit — Datadog/PagerDuty investigation,
  hypothesis docs, graphify ddog slice. L1 default; handoff to feature profile for fixes.
---

# Ops Incident Loop

Thin extension for `ops-incident` profile. Orchestrator: [`agentic-loop`](../agentic-loop/SKILL.md).

## Triggers

```text
/agentic-loop --profile ops-incident --pagerduty INC-…
/agentic-loop --profile ops-incident --datadog-monitor <id>
/agentic-loop --profile ops-incident --mode L1 --datadog-monitor <id>
```

## Phase 0 — Incident context

| Source | Action |
|--------|--------|
| **Datadog MCP** | Monitor, logs, metrics, traces for `service:` tag |
| **PagerDuty MCP** | Incident timeline, services, notes |
| **graphify** | `graphify query` on `ddog__` nodes; path to Java handlers |
| **Wiki** | [`ops-and-oncall.md`](../../../docs/wiki/ops-and-oncall.md), [`observability-ddog.md`](../../../docs/wiki/observability-ddog.md) |
| **Glean** | `/codebase-context` for alert service |
| **DDog repo wiki** | `observability-iac//docs/wiki/` (cross-link only) |

Record in [`ops-incident-state.md`](../../../loop-kit/ops-incident-state.md).

## Phase 1 — Hypothesis doc (not feature plan)

Template in STATE file:

- Symptom (user-visible / SLO)
- Timeline (UTC)
- Suspects (service, deploy, dependency)
- Evidence (DD/PD links, log snippets)
- Next queries (specific MCP calls)

## Phase 2 — Hypothesis review

- Cross-check monitor definition vs actual traffic
- Confirm or rule out infra vs application
- **Human gate** before L2 fix scope (`human_gates: always`)

## L2 fix scope (human approved)

```text
/agentic-loop --profile ops-incident --handoff cell-health \
  --repo your-service-cell-health-aggregator PROJ-153 \
  --from-state loop-kit/ops-incident-state.md
```

Continues feature phases 0–9 on target profile.

## Constraints

- **No push** in L1 (`ship: none`)
- Never `terraform apply` in loop
- Infra-only issues → [`STATE.md`](../../../loop-kit/STATE.md) human inbox

## Query templates (Datadog)

- Logs: `service:<name> status:error @timestamp:>…`
- Traces: `service:<name> @http.status_code:5*`
- Metrics: monitor message + `avg:trace.servlet.request.errors{service:<name>}`

## Query templates (PagerDuty)

- Incident notes: root cause candidates, linked deploys
- Service dependencies: upstream/downstream cell services
