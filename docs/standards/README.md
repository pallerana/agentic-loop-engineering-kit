# Standards manifest

All **seven** Java / Spring Boot / Terraform Cursor rules shipped with this kit. No optional omissions.

| # | Path | Category | Phases |
|---|------|----------|--------|
| 1 | `.cursor/rules/java-springboot-standards.mdc` | Java / Spring Boot 4 / Gradle | 3, 4, 5 |
| 2 | `.cursor/rules/service-quality-drill.mdc` | Build, JaCoCo, CI, drill | 4, 6, 7 |
| 3 | `.cursor/rules/pr-code-review.mdc` | PR review (Java + infra + mixed) | 5 |
| 4 | `.cursor/rules/terraform-standards.mdc` | Terraform / K8s / workflows | 5 |
| 5 | `.cursor/rules/external/jabrena-302-java-testing-fundamentals.mdc` | Java testing fundamentals | 1, 2, 4 |
| 6 | `.cursor/rules/external/jabrena-311-spring-boot-slice-testing.mdc` | Spring Boot slice tests | 1, 2, 4 |
| 7 | `.cursor/rules/external/jabrena-312-spring-boot-integration-testing.mdc` | Spring Boot integration tests | 1, 2, 4 |

## Profile `rules:` arrays

**`loop-kit/profiles/springboot-default.yaml`** references all six Java/Spring rules (items 1–3, 5–7).

**`loop-kit/profiles/ops-incident.yaml`** includes `terraform-standards.mdc` for L2+ infra handoff paths.

## Verification

```bash
find .cursor/rules -name '*.mdc' | sort
test "$(find .cursor/rules -name '*.mdc' | wc -l | tr -d ' ')" -eq 7
```

Expected output:

```text
.cursor/rules/external/jabrena-302-java-testing-fundamentals.mdc
.cursor/rules/external/jabrena-311-spring-boot-slice-testing.mdc
.cursor/rules/external/jabrena-312-spring-boot-integration-testing.mdc
.cursor/rules/java-springboot-standards.mdc
.cursor/rules/pr-code-review.mdc
.cursor/rules/service-quality-drill.mdc
.cursor/rules/terraform-standards.mdc
```

## Phase mapping

| Rule | When |
|------|------|
| `java-springboot-standards.mdc` | Java/Spring Boot implementation and review |
| `service-quality-drill.mdc` | Local build, JaCoCo, CI babysit, thread hygiene |
| `pr-code-review.mdc` | `--pr` or GitHub PR URL (Phase 5) |
| `terraform-standards.mdc` | Infra-only or mixed PRs |
| `jabrena-302/311/312` | Test matrix design (Phase 1–2) and verify (Phase 4) |
