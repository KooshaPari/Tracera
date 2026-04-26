# Tracera CodeQL High-Severity Alert Triage — 2026-04-27

**Repo:** KooshaPari/Tracera (archived: false)
**Source:** `gh api repos/KooshaPari/Tracera/code-scanning/alerts?state=open` (API-only, no dismissals)
**Total open high-severity alerts:** 104 (0 critical)

## Rule Cluster Summary

| Count | Rule ID | Class |
|------:|---------|-------|
| 100 | BinaryArtifactsID | OSSF Scorecard — committed binary artifacts |
| 1 | VulnerabilitiesID | OSSF Scorecard — known CVE in deps |
| 1 | MaintainedID | OSSF Scorecard — repo maintenance signal |
| 1 | CodeReviewID | OSSF Scorecard — code review policy |
| 1 | BranchProtectionID | OSSF Scorecard — branch protection policy |

All 104 alerts originate from the **OSSF Scorecard** integration, not source-level CodeQL queries.

## Path Classification (104 total)

| Bucket | Count | Notes |
|--------|------:|-------|
| ARCHIVE_VENDORED | 97 | `ARCHIVE/CONFIG/default/<pkg>@<ver>` — pnpm/npm cache of vendored prebuilt binaries (`.node`, `.wasm`, `.exe`, prebuilds) checked into archive tree |
| META_REPO_LEVEL | 4 | "no file associated" — repo-policy alerts (Vulnerabilities, Maintained, CodeReview, BranchProtection) |
| REAL_OTHER | 2 | `default/@oxlint-tsgolint/darwin-arm64@0.11.4/tsgolint` (vendored bin, alert #261); `backend/tracertm-setup` (alert #259, likely a setup binary) |
| TEST | 1 | one fixture/test path |

## False-Positive vs Real

- **False-positive (97):** ARCHIVE_VENDORED — pnpm-stored prebuild binaries from upstream packages (tree-sitter, fsevents, clipboardy, app-builder-bin, turbo, web-tree-sitter, source-map, iconv-corefoundation, unwasm, oxlint-tsgolint). These are normal package-manager cache artifacts; BinaryArtifactsID flags any `.node`/`.exe`/`.wasm` regardless of provenance.
- **Likely false-positive (1):** `tsgolint` (oxlint vendored bin, same class).
- **Real-investigate (1):** `backend/tracertm-setup` — non-archive committed binary, verify provenance.
- **Real policy gaps (4):** Repo-level meta alerts — branch protection, code-review policy, maintained signal, dep CVE — actionable via repo config, not code edits.

## Suggested Next Pass

1. **Exclude ARCHIVE/CONFIG from Scorecard scope** — add path filter to workflow or `.github/scorecard.yml` (kills 97/104 in one move).
2. **Inspect alert #259** (`backend/tracertm-setup`) — confirm whether it's a build artifact that should be `.gitignore`'d or a legitimate vendored tool.
3. **Address 4 repo-policy alerts** — enable branch protection on `main`, configure required reviews, run `npm/pnpm audit` for the VulnerabilitiesID hit.
4. **Defer:** dismissals — out of scope for this inventory pass.

## Provenance

- TSV inventory: `/tmp/tracera-high.tsv` (ephemeral)
- Pre-flight: archived=false confirmed
- API-only; no alerts dismissed or modified.
