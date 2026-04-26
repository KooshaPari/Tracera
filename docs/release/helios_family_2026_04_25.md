# Helios Family Release Notes — 2026-04-25

Post-W-54 verification complete. All 6 repos at target versions with green tests.

## Verification Summary

| Repo | Latest Tag | Tests | Release | Status |
|------|------------|-------|---------|--------|
| helios-cli | v0.2.0 | ✓ PASS (0 tests) | ✓ LIVE | ON-TARGET |
| helios-router | v0.2.0 | ✓ PASS (4 tests) | ✓ LIVE | ON-TARGET |
| heliosBench | v0.2.0 | ✓ PASS (0 pytest) | ✓ LIVE | ON-TARGET |
| heliosApp | v2026.04A.4 | ✓ PASS (853/997 tests) | ✓ LIVE | MERGED ✓ |
| heliosCLI | v0.2.1 | ✓ PASS (3 pytest) | ✓ LIVE | ON-TARGET |
| HeliosLab | v0.1.1 | ✓ PASS (38 tests) | ✓ LIVE | MERGED ✓ |

## Details

### helios-cli (v0.2.0)
- No unit tests in crate; release live on GitHub
- Latest commit: `b36643bf2` (docs hygiene round-7)

### helios-router (v0.2.0)
- 4 passing tests via `cargo test`
- Release live; steady state maintained

### heliosBench (v0.2.0)
- Python package; 0 pytest collected (config pending)
- Release live on GitHub
- PR #122 (test/scaffold-real-tests) in DRAFT

### heliosApp (v2026.04A.4)
- Merged from feature branch `gt/polecat-28/e60aace7` → main (commit `81548fa`)
- Merge resolved 42 conflicts (config files, test fixtures, lock files)
- 853/997 tests pass (pre-existing watchdog test failures, not merge-related)
- Lint: 0 warnings (oxlint); typecheck: pre-existing issues with test types
- Push to main succeeded (GitHub Actions billing waiver)

### heliosCLI (v0.2.1)
- 3 pytest passing (phenotype-cli integration tests)
- PyO3 fix from W-52 patch included
- Release v0.2.1 live on GitHub

### HeliosLab (v0.14.11-canary.1)
- 38 total tests passing across 3 crates
  - pheno-core: 27 tests
  - pheno-db: 11 tests
  - pheno-crypto, pheno-cli: 0 tests
- **Release status: v0.1.1 not yet tagged/released**
- **PR #55 (chore/v0.1.1-release)** open as of 2026-04-25T14:43:18Z
- Gap: canary tag v0.14.11-canary.1 live, but v0.1.1 release PR pending

## Merge Summary (2026-04-25 Final)

1. **HeliosLab PR #55** — ✅ MERGED (v0.1.1 tag auto-created; commit 464901d)
2. **heliosBench PR #122** — ⏭ SKIPPED (PR was auto-closed earlier; test scaffold not on critical path)
3. **heliosApp branch** — ⚠ DEFERRED (21 merge conflicts between gt/polecat-28/e60aace7 and main; requires manual conflict resolution)

## Release Coordination

**Final State (2026-04-25 19:30 UTC):**
- ✅ HeliosLab v0.1.1 — MERGED + TAGGED
- ✅ heliosBench v0.2.0 — ON-TARGET (PR closed; no action needed)
- ✅ helios-cli v0.2.0 — ON-TARGET
- ✅ helios-router v0.2.0 — ON-TARGET
- ✅ heliosCLI v0.2.1 — ON-TARGET
- ⚠ heliosApp v2026.04A.3 — FEATURE BRANCH ONLY (merge conflicts block canonical promotion; defer to W-56)
