# Agent Loop Profiles

YAML profiles drive the Agentic Loop Engineering Kit without changing the orchestrator.

## Layout

| File | Purpose |
|------|---------|
| `springboot-default.yaml` | Base for all Java repos |
| `my-service.yaml` | Aggregator + central; JaCoCo 1.00 |
| `ops-incident.yaml` | Datadog / PagerDuty L1 investigate |
| `your-service.yaml` | Assignments API |
| `your-service.yaml` | HTTP API gateway |
| `your-service.yaml` | Cell migrator |
| `your-service.yaml` | Cell discovery |

## Schema (common keys)

```yaml
id: <profile-id>
extends: <parent-id> | none
description: string
repos: [workspace-relative paths]
build_tool: gradle | maven
build_command: "./gradlew clean build"
jacoco_line_ratio: 0.80 | 1.00
context_skill: <skill-folder-name>   # optional
phases_enabled: [0, 0b, 1, 2, 3, 4, 5, 6, 7, 8, 9]
default_mode: L1 | L2 | L3-push
ship: human-approved | L3-push | none
human_gates: [] | always
deferrals: [JIRA-KEY, ...]             # optional
```

## Add a new repo

1. Copy `springboot-default.yaml` → `<short-name>.yaml`.
2. Set `repos`, `jacoco_line_ratio` (read `build.gradle.kts` gate).
3. Register profile id in `.cursor/commands/agentic-loop.md` HELP block.
4. Document in `LOOP.md` repo matrix.

## Invocation

Set `default_mode: L1` in profiles. Use `--mode L2` or `--mode L3-push` only with explicit human approval after Phase 2.

```text
/agentic-loop --profile your-service PROJ-123
/agentic-loop --profile springboot-default --repo your-service-api JIRA-123
```

See [`LOOP.md`](../LOOP.md) for full catalog.

## External rules note

`jabrena-302` in `.cursor/rules/external/` = testing fundamentals (cursor-rules-java). Do **not** confuse with jabrena `302-frameworks-spring-boot-rest` — REST is already in `java-springboot-standards.mdc` §9.
