# Tier-2 CodeQL Triage — Dino, PolicyStack, Tokn

**Date:** 2026-04-27
**Method:** API-only (`gh api .../code-scanning/alerts?state=open`), high+critical only.
**Pre-flight:** All three repos `archived=false`.
**Action policy:** DO NOT dismiss. Classification only.

## Alert Counts (high+critical, open)

| Repo | Total | TokenPermissions | BinaryArtifacts | Vulnerabilities | Maintained | CodeReview | BranchProtection |
|------|-------|------------------|-----------------|-----------------|------------|------------|------------------|
| Dino | 31 | 16 | 11 | 1 | 1 | 1 | 1 |
| PolicyStack | 21 | 17 | 1 | 1 | 1 | 1 | 1 |
| Tokn | 26 | 23 | 0 | 0 | 1 | 1 | 1 |

## Classification

- **TokenPermissions (56 alerts, dominant):** OSSF Scorecard rule — workflows missing top-level `permissions:` block. Fix: add `permissions: contents: read` (or least-privilege) to each `.github/workflows/*.yml`. Bulk-fixable.
- **BinaryArtifacts (12 alerts, Dino):** Rust `target/release/*.dll.lib`, `*.pyc`, Zig `root.lib` checked into repo. Fix: `.gitignore` `target/`, `__pycache__/`, `*.lib`; `git rm --cached` artifacts. PolicyStack #18 = `wrappers/go/policy-wrapper` compiled binary (same fix).
- **Vulnerabilities / Maintained / CodeReview / BranchProtection (org-wide Scorecard meta):** Repo-policy rules with no file. Addressed via branch-protection ruleset restoration (billing-blocked, see reference_billing_blocked_rules) + CODEOWNERS + dependency hygiene.

## Recommended Order

1. TokenPermissions bulk PR per repo (`permissions: contents: read` top-level). ~3 PRs.
2. Dino BinaryArtifacts: gitignore + cached-rm PR.
3. PolicyStack `wrappers/go/policy-wrapper` binary cleanup.
4. Defer meta-rules until ruleset restore unblocked.

No alerts dismissed.
