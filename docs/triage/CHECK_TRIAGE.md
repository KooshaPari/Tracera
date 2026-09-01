# CHECK_TRIAGE - PR Workflow Failure Classification

Scope

- Source: all workflow files in `.github/workflows` containing `pull_request` under `on:`.
- Data source: recent PR-triggered GitHub Actions runs via API (no local build/test execution).
- `Fail frequency` is from sampled recent PR runs for each workflow.

Legend

- `broken-fix-now`: workflow step/config is independently broken and should be repaired in YAML.
- `comply-needed`: check is failing due repository content, lint/type/test debt, or policy outcomes.
- `inactive/path-gated`: runs but is usually skipped/cancelled or not currently red in sampled PR runs.
- `user-gated(SonarCloud)`: blocked by external org/token/billing dependency.

## PR workflow triage

| Workflow file                                     | Outcomes (recent PR sample)           | Always fail on sampled PR runs? | Why                                                                                                            | Category            |
| ------------------------------------------------- | ------------------------------------- | ------------------------------- | -------------------------------------------------------------------------------------------------------------- | ------------------- |
| `.github/workflows/architecture.yml`              | `cancelled:2; failure:3; success:35`  | No                              | `Install dependencies` often fails from external/private dependency fetch behavior.                            | comply-needed       |
| `.github/workflows/benchmarks.yml`                | `cancelled:3; success:37`             | No                              | Stable in sampled PR runs.                                                                                     | inactive/path-gated |
| `.github/workflows/cargo-deny.yml`                | `failure:18; success:16`              | No                              | `Run cargo-deny` fails when fetching private git dependency `traceability-core` (auth/index access).           | comply-needed       |
| `.github/workflows/chromatic.yml`                 | `failure:40`                          | Yes                             | `Setup Node.js` fails because setup-node cache requires npm/yarn lockfile not present at repo root.            | broken-fix-now      |
| `.github/workflows/codeql.yml`                    | `failure:39; success:1`               | No                              | `Perform CodeQL Analysis` failures tied to environment/builded source discovery during analyze stage.          | comply-needed       |
| `.github/workflows/ci-cd.yml`                     | `cancelled:4; failure:8; success:28`  | No                              | `Run tests` fails from repo test/type issues.                                                                  | comply-needed       |
| `.github/workflows/test-validation.yml`           | `cancelled:1; failure:39`             | No                              | `Setup test credentials` / `Comment PR with report` failures in reporting path.                                | comply-needed       |
| `.github/workflows/contract-tests.yml`            | `failure:2; success:38`               | No                              | `Run consumer contract tests` failures.                                                                        | comply-needed       |
| `.github/workflows/contracts.yml`                 | `failure:14; success:26`              | No                              | `Install dependencies` and test steps depend on dependency/service health.                                     | comply-needed       |
| `.github/workflows/dependabot-auto-merge.yml`     | `skipped:40`                          | No                              | PR samples are consistently skipped by trigger/conditions.                                                     | inactive/path-gated |
| `.github/workflows/docs-deploy.yml`               | `cancelled:1; failure:17; success:22` | No                              | `Generate OpenAPI spec` path can fail for current PR state.                                                    | comply-needed       |
| `.github/workflows/openapi-docs.yml`              | `failure:31; success:9`               | No                              | Reporting/comment steps and doc generation unstable in sampled PRs.                                            | comply-needed       |
| `.github/workflows/go-tests.yml`                  | `cancelled:2; failure:38`             | No                              | Service/integration/API tests fail; not workflow-wide constant breakage.                                       | comply-needed       |
| `.github/workflows/governance-gates.yml`          | `failure:5; success:35`               | No                              | `Run antipattern detection gate` depends on code policy state.                                                 | comply-needed       |
| `.github/workflows/journey-gate.yml`              | `success:40`                          | No                              | Passing on sampled PR runs.                                                                                    | inactive/path-gated |
| `.github/workflows/load-test.yml`                 | `skipped:40`                          | No                              | Trigger/path gating means this workflow is skipped in samples.                                                 | inactive/path-gated |
| `.github/workflows/naming-guard.yml`              | `cancelled:1; failure:16; success:23` | No                              | `Check file length limits` fails against current content.                                                      | comply-needed       |
| `.github/workflows/performance-regression.yml`    | `failure:40`                          | Yes                             | `Run database migrations` fails with Alembic config error `No 'script_location' key found` in this repo state. | broken-fix-now      |
| `.github/workflows/policy-gate.yml`               | `cancelled:23; failure:4; success:13` | No                              | `Enforce layered fix PR policy` is failing by policy conditions.                                               | comply-needed       |
| `.github/workflows/pre-commit.yml`                | `cancelled:4; failure:14; success:22` | No                              | `Run pre-commit` fails due formatting/lint findings (`ruff format`, EOF, etc.).                                | comply-needed       |
| `.github/workflows/python-ci.yml`                 | `cancelled:4; failure:33`             | No                              | `Pyright (strict)` strict typing failures (`tests/unit/test_governance_and_models.py` etc.).                   | comply-needed       |
| `.github/workflows/quality.yml`                   | `cancelled:3; failure:15; success:22` | No                              | `Ruff format check` and Python quality gates fail.                                                             | comply-needed       |
| `.github/workflows/rust-tests.yml`                | `failure:19; success:16`              | No                              | `Test each crate feature set` failures and test debt.                                                          | comply-needed       |
| `.github/workflows/schema-validation.yml`         | `failure:10`                          | Yes (sample scope)              | `Run schema validation` and `Check for uncommitted changes` indicate generated artifacts out of sync.          | comply-needed       |
| `.github/workflows/secret-scanning.yml`           | `cancelled:4; failure:5; success:31`  | No                              | `Run secret scanning` failures tied to repo findings.                                                          | comply-needed       |
| `.github/workflows/security-guard.yml`            | `cancelled:3; failure:1; success:36`  | No                              | `Run pre-commit guard checks` failures are policy/tooling outcomes.                                            | comply-needed       |
| `.github/workflows/security-scans.yml`            | `cancelled:3; success:37`             | No                              | Stable in sampled PR runs.                                                                                     | inactive/path-gated |
| `.github/workflows/security-guard-hook-audit.yml` | `failure:20; success:20`              | No                              | `Run security guard hook` fails on hook audit findings.                                                        | comply-needed       |
| `.github/workflows/test-pyramid.yml`              | `cancelled:3; success:37`             | No                              | Stable in sampled PR runs.                                                                                     | inactive/path-gated |
| `.github/workflows/test.yml`                      | `cancelled:3; failure:1; success:36`  | No                              | Startup/test steps can fail based on transient service state or test regressions.                              | comply-needed       |
| `.github/workflows/tests.yml`                     | `cancelled:4; failure:8; success:28`  | No                              | Property/integration/e2e/unit failures and current test breakage.                                              | comply-needed       |
| `.github/workflows/trufflehog.yml`                | `cancelled:4; failure:5; success:31`  | No                              | `Run trufflesecurity/trufflehog` failures are scan content dependent.                                          | comply-needed       |

## User-gated checks

- No `SonarCloud`, `org-token`, or Sonar token references appear in `.github/workflows`.
- No workflow is currently classed as `user-gated(SonarCloud)` from repo configuration.
