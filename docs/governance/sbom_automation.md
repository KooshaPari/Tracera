# SBOM Automation & Monthly Refresh Policy

## Overview

Software Bill of Materials (SBOM) documents track all direct and transitive dependencies in a project. This governance policy automates monthly regeneration and PR updates across the Phenotype organization to keep SBOMs current and discoverable for security audits.

## Policy

**Monthly refresh:** Every 1st of the month (UTC), each SBOM repo generates a fresh dependency snapshot in CycloneDX format and opens a PR with changes.

**Format:** CycloneDX JSON (ISO/IEC 5962 standard).

**Coverage:** 10 repos tracked:
- Rust: Sidekick, Eidolon, Stashly, PhenoObservability, phenotype-shared, FocalPoint, AgilePlus, thegent
- Node.js: heliosApp, Paginary

## Architecture

### Reusable Workflow

**Location:** `/repos/phenotype-tooling/.github/workflows/sbom-monthly.yml`

**Invocation:**
```yaml
uses: KooshaPari/phenotype-tooling/.github/workflows/sbom-monthly.yml@main
with:
  repo_path: '.'
  build_system: 'rust' | 'node'
```

**Behavior:**
1. Checkout repository
2. Install build-system-specific SBOM tooling (cargo-cyclonedx or npm sbom)
3. Generate fresh SBOM (CycloneDX JSON)
4. Detect changes via `git diff`
5. If changed: Open PR with `chore(sbom): monthly refresh` commit

### Per-Repo Workflow

**Location:** `.github/workflows/sbom-refresh.yml` (in each tracked repo)

**Schedule:** `cron: '0 0 1 * *'` (1st of month, 00:00 UTC)

**Manual trigger:** `workflow_dispatch` for on-demand refresh

## Rollout Status

All 10 SBOM repos opted in; workflows deployed 2026-04-25.

| Repo | Build System | Workflow Status |
|------|--------------|-----------------|
| Sidekick | Rust | Active |
| Eidolon | Rust | Active |
| Stashly | Rust | Active |
| PhenoObservability | Rust | Active |
| phenotype-shared | Rust | Active |
| FocalPoint | Rust | Active |
| AgilePlus | Rust | Active |
| thegent | Rust | Active |
| heliosApp | Node.js | Active |
| Paginary | Node.js | Active |

## Worklog Integration

Track SBOM changes in worklogs:
- **File:** `/repos/worklogs/GOVERNANCE.md`
- **Format:** Monthly entry with repo, old count → new count, tooling version
- **Example:**
  ```
  **2026-05-01 SBOM Refresh (Monthly)**
  - AgilePlus: 47 deps → 49 deps (cargo-cyclonedx 0.5.2)
  - heliosApp: 156 deps → 158 deps (npm sbom 7.0)
  ```

## Manual Refresh

To regenerate SBOMs without waiting for the monthly cron:

**Rust:**
```bash
cd <repo>
cargo cyclonedx --all --output-format json > sbom.cdx.json
git add sbom.cdx.json
git commit -m "chore(sbom): manual refresh"
```

**Node.js:**
```bash
cd <repo>
npm sbom --output sbom.cdx.json  # or: npx @cyclonedx/npm@latest
git add sbom.cdx.json
git commit -m "chore(sbom): manual refresh"
```

## Troubleshooting

| Issue | Resolution |
|-------|-----------|
| Workflow fails (tooling missing) | Workflow handles missing tools gracefully; check logs for fallback behavior |
| PR not created | Ensure `sbom.cdx.json` is tracked in git; check Actions logs for diff failures |
| Stale SBOM in repo | Trigger `workflow_dispatch` manually or wait until next 1st of month |

## Future Improvements

- Integrate SBOM comparison tooling (detect breaking dependency changes)
- Cross-repo dependency conflict detection
- Dashboard view of org-wide dependency trends
- Automated security advisory scanning (Dependabot integration)

---

**Policy Owner:** Phenotype Org
**Last Updated:** 2026-04-25
**Audit Frequency:** Monthly (automated)
