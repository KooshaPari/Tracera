# Dependency Alert Remediation Session - 2026-04-26

## Goal

Reduce live Tracera dependency alerts without letting the task become a broad
repo cleanup.

## SIZE-DEP: Keep Dependency Remediation Finishable

- **Cap:** one runtime/test dependency surface per PR unless alerts share the
  same lockfile.
- **Current size:** GitPython `uv.lock` hotfix is merged; CI Python compatibility
  is the next bounded task because the hotfix PR exposed workflow pins below the
  repository's `requires-python = ">=3.13"` contract.
- **Stop rule:** keep each PR to one dependency/runtime surface and leave broader
  CI, Go, frontend, and archive cleanup as explicit follow-up lanes.
- **Spillover:** create separate WBS items for Python lower-bound cleanup, Go
  Docker module investigation, frontend package bumps, and archive manifest
  quarantine.

## SIZE-CI-PYTHON-313: Python CI Compatibility

- **Scope:** PR-triggered Python workflow setup and local Python type-tool
  version alignment.
- **Reason:** `CI/CD Pipeline / Python Tests (3.12)` failed because workflows
  installed the project on Python 3.12 while `pyproject.toml` requires Python
  3.13 or newer.
- **Included:** `.github/workflows/ci.yml`, `quality.yml`, `tests.yml`,
  `pre-commit.yml`, `test-pyramid.yml`, `contracts.yml`, `chaos-tests.yml`,
  `architecture.yml`, `dependabot-auto-merge.yml`, `test-validation.yml`,
  `test.yml`, `ci-cd.yml`, and `[tool.ty.environment]`.
- **Excluded:** Go toolchain/race failures, old action-version upgrades,
  shellcheck cleanups, `requirements.txt` workflow migration, contract
  `scripts/.venv` repair, and archive dependency manifests.

## SIZE-CI-GO-TOOLCHAIN: Deferred Go CI Lane

- **Scope:** reusable workflow/toolchain ownership, not this Python PR.
- **Current evidence:** the Go failure used Go 1.23 wrappers while logs resolved
  a Go 1.25.7 target, then failed golangci-lint/covdata/race-test steps.
- **Next action:** inspect the reusable workflow owner and align `go version`,
  `GOTOOLCHAIN`, golangci-lint, coverage, and race-test execution under one
  source of truth.

## Alert Buckets

| Bucket | Scope | Action |
|---|---|---|
| GitPython | `uv.lock` | Patch in this lane. |
| Other Python | `pyproject.toml`, `uv.lock` | Separate Python dependency cleanup lane. |
| Python CI | `.github/workflows/*.yml`, `pyproject.toml` | Align PR-triggered Python setup to 3.13. |
| Go Docker module | `backend/**/go.mod` | Defer until a published fixed module tag or replacement module path is confirmed. |
| Go CI toolchain | reusable workflow / Go wrappers | Separate toolchain lane. |
| Frontend npm | `frontend/**` | Separate frontend dependency lane. |
| Archived npm snapshots | `ARCHIVE/CONFIG/default/**/package.json` | Separate archive quarantine task. |

## Validation Targets

```bash
uv lock --locked
uv run python -m compileall -q src
actionlint -shellcheck= -ignore 'the runner of ".*" action is too old' \
  -ignore 'input "webhook_url" is not defined' \
  -ignore '"needs" section should not be empty' .github/workflows/<changed>.yml
git diff --check
```
