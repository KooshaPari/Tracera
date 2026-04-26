# Tier-3 CodeQL Triage — 2026-04-27

API-only audit (no dismissals). Scope: Civis, Configra, Eidolon, FocalPoint.

## Per-Repo Status

| Repo | Archived | Code Scanning | Critical | High | Notes |
|------|----------|---------------|----------|------|-------|
| Civis | false | DISABLED (403) | n/a | n/a | Code scanning not enabled |
| Configra | false | DISABLED (403) | n/a | n/a | Code scanning not enabled |
| Eidolon | false | DISABLED (403) | n/a | n/a | Code scanning not enabled |
| FocalPoint | false | ENABLED | 0 | 22 | Scorecard-only (no CodeQL queries) |

## FocalPoint Alert Inventory (22 high)

All alerts originate from **OSSF Scorecard**, not CodeQL semantic analysis.

### Cluster 1: TokenPermissionsID (15 alerts)
Workflow files lacking explicit top-level `permissions:` block. Files: `sbom-refresh.yml`, `traceability.yml`, `supply-chain.yml`, `rust.yml`, `release-dry-run.yml`, `quality-gate.yml`, `pr-checks.yml`, `perf-guard.yml`, `fuzz.yml`, `e2e-smoke.yml`, `docs.yml`, `disk-budget-weekly.yml`, `dco.yml`, `connector-manifest.yml`, `cli-demo.yml`, `cargo-doc.yml`. **Real**, low-effort fix (add `permissions: contents: read`).

### Cluster 2: BinaryArtifactsID (2 alerts)
`assets/audio/test_synth`, `assets/audio/gen_cues`. **FP candidate** — audio test fixtures, not executables.

### Cluster 3: Repo-level Scorecard (5 alerts, no file)
`VulnerabilitiesID` (#99), `CodeReviewID` (#93), `MaintainedID` (#92), `BranchProtectionID` (#1), plus duplicates. Policy/meta — not code defects.

## Top Recommendations

- **Enable code scanning** on Civis/Configra/Eidolon to surface real CodeQL findings.
- **FocalPoint TokenPermissions** (15): batch-fix via single PR adding `permissions: contents: read` to each workflow.
- **BinaryArtifacts** (2): verify `assets/audio/*` are non-executable fixtures; if so, mark as FP via `.scorecard.yml` allowlist (no dismissal here).
- **Repo-level meta alerts** (5): governance policy items, not file-scoped fixes.

**No real CodeQL semantic findings across scope.** All FocalPoint alerts are Scorecard supply-chain hygiene.
