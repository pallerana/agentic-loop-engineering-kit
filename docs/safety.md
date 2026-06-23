# Loop safety policy

Agentic Loop Engineering Kit safety gates. Canonical gates: [`loop-kit/GATES.md`](loop-kit/GATES.md).

## Auto-merge policy

- **Never** auto-merge to `main` or `master`
- **Never** `git push --force` (enforced by `block-dangerous-git.sh`)
- L3-push may push **feature branches** only after explicit human approval
- Human merge required (2 code-owner reviews per branch protection)

## Plan-mode-first

- Loop **always starts in Plan mode** (`SwitchMode(plan)`)
- Phase 0→2: context, plan, review — **no code changes**
- Phase 3+ (implement, verify, ship) only when user explicitly approves (e.g. "proceed with implementation", `--mode L2`, `--mode L3-push`)
- Ambiguity → stop and ask; record in [`STATE.md`](../STATE.md) human inbox

## Denylist (file edits)

Blocked by `block-denylist-edits.sh` without human gate:

- `.env`, `credentials.json`, `secrets.*`
- Prod deploy workflows (`deploy-prod`, `.github/workflows/deploy`)
- `kubeconfig`, `/prod/` paths

## Denylist (git)

Blocked by `block-dangerous-git.sh`:

- `git push --force`, push to `main`/`master`
- `git reset --hard`, `git clean -fd`

## Terraform / infra

- `terraform fmt` / `validate` / `plan` — allowed with human review of output
- **`terraform apply`** — never inside the loop; human gate only
- See [`terraform-standards.mdc`](../.cursor/rules/terraform-standards.mdc)

## MCP scopes

| Mode | Datadog / PagerDuty | GitHub | Atlassian |
|------|---------------------|--------|-----------|
| Ops L1 | Read: logs, metrics, incidents | Read PRs/issues | Read Jira/Confluence |
| Feature L2+ | As needed for fix validation | PR create/update (approved) | Jira comment, In Progress |

No production config mutations via MCP without explicit user request.

## Kill switch

1. Add item to `STATE.md` human inbox
2. Set `loop-pause: true` in active profile state frontmatter
3. Stop loop; do not auto-re-dispatch Failure Router

## Failure Router

Classifies failures and **recommends** next phase — does **not** auto-re-dispatch without human confirmation (plan-mode-first).
