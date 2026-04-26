# PhenoFamily CodeQL Triage — 2026-04-27

API-only audit. None archived. No alerts dismissed.

## Per-repo critical/high counts

| Repo | Crit | High | Notes |
|------|-----:|-----:|-------|
| PhenoLang | 2 | 7 | Dependabot CVEs in lockfiles (uv.lock x2, Cargo.lock) |
| PhenoPlugins | 0 | 3 | Scorecard-only (no CodeQL findings) |
| DataKit | 0 | 0 | Clean |
| ResilienceKit | 0 | 4 | Scorecard-only |
| ObservabilityKit | n/a | n/a | 404 no analysis (CodeQL never ran; needs scope `admin:repo_hook` to introspect) |
| McpKit | 0 | 3 | Scorecard-only |
| PhenoMCP | 0 | 4 | Scorecard + 1 actionlint TokenPermissions in `.github/workflows/ci.yml` |
| PhenoVCS | 0 | 3 | Scorecard-only |

Totals: **2 critical, 24 high** across 7 introspectable repos.

## Hot files

- `python/uv.lock`, `agileplus-mcp/uv.lock` (PhenoLang) — 5 alerts; CVE-2026-32871 (crit) + CVE-2026-27124, -32597 (high). Python transitive deps.
- `Cargo.lock` (PhenoLang) — 4 alerts: GHSA-hppc-g8h3-xhp3, CVE-2026-41681/41678/41676.
- `.github/workflows/ci.yml` (PhenoMCP) — TokenPermissionsID (workflow needs `permissions:` block).
- "no file associated" — 23 alerts; all Scorecard meta-checks (BranchProtection, CodeReview, Maintained, DependencyUpdateTool).

## FP / low-signal candidates

- **Scorecard meta-checks (23/26 highs)** — `MaintainedID`, `CodeReviewID`, `BranchProtectionID`, `DependencyUpdateToolID`. Not code defects; org-policy signals. Suppress via repo settings, not code.
- **CVE-2026-41676/41678/41681 (Cargo.lock)** — verify reachability vs transitive-only before treating as actionable.

## Real action items

1. PhenoLang: bump `python/uv.lock` + `agileplus-mcp/uv.lock` (CVE-2026-32871 critical) + `Cargo.lock`.
2. PhenoMCP: add `permissions: contents: read` to `.github/workflows/ci.yml`.
3. ObservabilityKit: enable CodeQL workflow (no analysis exists).

Output: `/Users/kooshapari/CodeProjects/Phenotype/repos/docs/governance/phenofamily-codeql-triage-2026-04-27.md`
