# CI Gate Billing Exception Policy

**Policy ID**: GOV-CI-001
**Effective**: 2026-04-27
**Applies To**: All Phenotype org repositories

---

## Background

GitHub Actions billing limits can cause CI checks to remain in `QUEUED` state indefinitely or fail to start entirely. This is a **known operational constraint**, not a code quality signal. When billing exhausts, the local development loop (pre-commit hooks, `task quality`) remains authoritative for code readiness.

---

## Policy Statement

**Billing or quota exhaustion is the only documented exception for merge blocks when CI jobs fail to start.**

All other merge gate exceptions (skip checks, override requirements, bypass for convenience) are prohibited unless explicitly authorized by this policy.

---

## Minimum Required Gate Checks

When CI is operational, repos must enforce these checks before merge:

| Check | Purpose | Tool | Timeout |
|-------|---------|------|---------|
| **Lint** | Code style, formatting | `ruff`, `clippy`, `eslint`, `golangci-lint` | < 30s |
| **Type check** | Type safety | `cargo check`, `mypy`, `tsc` | < 60s |
| **Unit tests** | Core logic | `cargo test`, `pytest`, `vitest`, `go test` | < 5m |
| **Security scan** | Vulnerability detection | `semgrep`, `bandit`, `cargo-audit` | < 60s |
| **Policy check** | License compliance, secrets | `gitleaks`, `license-check` | < 30s |

**Fast security scanning** means: `semgrep` (SAST) + `gitleaks` (secrets) — no full container scanning or DAST in the pre-merge gate. Full security scans run on merge or scheduled.

---

## Exception Conditions

A merge block may be bypassed **only when ALL of the following** are true:

1. CI jobs are in `QUEUED` state and have not started within **15 minutes** of the last push
2. The queuing is **confirmed to be billing-related** (runner availability is fine; the job is simply not starting)
3. **Local verification is recorded** — equivalent checks have passed via:
   - `task quality` (full local quality gate)
   - `mise run lint test` (or equivalent task runner)
   - Pre-commit hooks completed successfully
4. A merge comment documents the exception:
   ```
   merge exception: billing — local quality verified (pre-commit + task quality)
   ```

---

## Exception Procedure

When billing blocks CI:

```
1. Verify: Check GitHub Actions → repository → Actions tab → Jobs show "QUEUED" > 15min
2. Record: Run local quality gate: mise run lint test && task quality
3. Document: Add merge comment with exception notation
4. Authorize: Use gh pr merge --admin --squash (bypasses branch protection)
5. Recover: After billing resets, re-run CI normally to validate
```

---

## Billing Prevention Strategy

To minimize billing-related merge blocks:

- **Ubuntu runners only** (cheapest, fastest queue)
- **Skip macOS/Windows** unless explicitly required for the repo
- **Fast gates first** — lint/typecheck run before tests (fail fast)
- **Concurrency limits** — cancel in-progress runs on new push to same PR
- **Scheduled jobs disabled** by default — only run on-demand or on release tags

---

## Fast Security Scanning Specification

Pre-merge security checks must complete in < 60s total. Approved tools:

| Tool | Scope | Speed |
|------|-------|-------|
| `semgrep` | SAST — code patterns, injection, XSS | ~10s |
| `gitleaks` | Secrets in code/commits | ~5s |
| `ruff` | Import sorting, unused imports | ~5s |
| `cargo-audit` | Rust advisory database | ~10s |
| `pip-audit` | Python advisory database | ~10s |

**Prohibited in pre-merge**: Trivy full scans, container scanning, DAST, SAST tools with > 60s runtime.

---

## Enforcement

This policy is enforced by:

- **Pre-commit hooks** — reject non-conventional commits, run fast lint
- **Branch protection rules** — require status checks before merge (when CI is operational)
- **Quality gate** — `task quality` in all repos' task runner
- **Governance audit** — quarterly review of exception usage

---

## Exceptions to This Policy

None. This is a hard constraint. If a repo needs a different configuration, it requires a Kitty-Spec proposal and approval.

---

## Related Documents

- `projects-landing/docs/governance/site-infrastructure.md` — Ubuntu-only runners, billing-aware
- `AgilePlus/CONTRIBUTING.md` — macOS/Windows runners skipped due to billing constraints
- `GOV-CI-EXCEPTIONS.md` — Log of all billing exceptions used (auto-generated)

---

**Policy Owner**: Koosha Pari
**Review**: Annually or when GitHub Actions billing model changes
