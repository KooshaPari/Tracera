# Tier 1 Secondary Dependabot Sweep — 2026-04-26

## Executive Summary

Checked three secondary targets per disk-constrained dispatch plan (25Gi available):
- **BytePort**: 0 open PRs, active (last push 2026-04-26 01:31 UTC)
- **AgilePlus**: 0 open dependency PRs, 46 open issues, active (last push 2026-04-26 05:54 UTC)
- **hwLedger**: 0 open PRs, active (last push 2026-04-26 05:54 UTC)

**Key Finding**: Dependabot alerts endpoint returned 404 for all three repos. This indicates either:
1. Dependabot is not enabled on these repos
2. API endpoint requires different access scope
3. No HIGH/CRITICAL alerts exist (but API should still return empty list, not 404)

**Recommendation**: Enable Dependabot on secondary targets via GitHub UI or re-check API permissions.

---

## BytePort — Analysis

| Metric | Status |
|--------|--------|
| Active | Yes (pushed 2026-04-26 01:31 UTC) |
| Archived | No |
| Open Issues | 0 |
| Open PRs | 0 |
| Dependabot Alerts | Not accessible via API |

**Action Items**:
- Verify Dependabot is enabled in GitHub settings
- Re-run alerts query once enabled
- Monitor for ecosystem-specific deps (Node.js, Go, Python, Rust depending on stack)

---

## AgilePlus — Analysis

| Metric | Status |
|--------|--------|
| Active | Yes (pushed 2026-04-26 05:54 UTC) |
| Archived | No |
| Open Issues | 46 |
| Open PRs | 0 (dependency-related) |
| Dependabot Alerts | Not accessible via API |

**Note**: 46 open issues may include security-related items. Should audit manually:
```bash
gh issue list -R KooshaPari/AgilePlus --state open --search label:security
```

**Action Items**:
- Enable Dependabot in GitHub settings
- Re-check for security-labeled issues
- Triage and merge low-risk patches when alerts appear

---

## hwLedger — Analysis

| Metric | Status |
|--------|--------|
| Active | Yes (pushed 2026-04-26 05:54 UTC) |
| Archived | No |
| Open Issues | 0 |
| Open PRs | 0 |
| Dependabot Alerts | Not accessible via API |

**Action Items**:
- Verify Dependabot is enabled
- Re-run alerts once enabled
- Given Rust/Swift stack (WP21 blocked on codesign), watch for:
  - Cargo deps (high-impact)
  - Swift Package Manager (iOS dev prereqs)

---

## API Query Results

### BytePort
```
gh api repos/KooshaPari/BytePort/dependabot/alerts -f state=open -f severity=high
=> HTTP 404 Not Found
```

### AgilePlus
```
gh api repos/KooshaPari/AgilePlus/dependabot/alerts -f state=open -f severity=high
=> HTTP 404 Not Found
```

### hwLedger
```
gh api repos/KooshaPari/hwLedger/dependabot/alerts -f state=open -f severity=high
=> HTTP 404 Not Found
```

---

## Troubleshooting & Next Steps

### Enable Dependabot (if not active)
For each repo:
1. Go to **Settings > Code security and analysis**
2. Toggle **Dependabot alerts** ON
3. Wait 15–30 min for initial scan

### Re-Query Post-Enable
```bash
gh api repos/KooshaPari/BytePort/dependabot/alerts -f state=open --jq '.'
```

### Manual Fallback (inspect lock files)
If Dependabot remains unavailable:
- **Node.js**: `package-lock.json` or `pnpm-lock.yaml` (audit with `npm audit` / `pnpm audit`)
- **Rust**: `Cargo.lock` (audit with `cargo audit`)
- **Go**: `go.mod` (audit with `go list -u -m all`)
- **Python**: `requirements.lock` or `uv.lock` (audit with `pip-audit` / `uv audit`)

### Admin Merge Strategy (once alerts exist)
Per original directive:
- Patch versions (x.y.Z → x.y.(Z+1)): admin-merge immediately
- Minor versions (x.Y → x.(Y+1).0): review, likely safe
- Major versions (X → (X+1).0): skip (deferred to next cycle)

---

## Residuals & Tracking

**Current State (2026-04-26 06:00 UTC)**:
- No actionable alerts queued
- 46 open issues in AgilePlus need manual triage
- Disk: 25Gi (tight); do not run concurrent cargo builds

**Follow-Up**:
1. Enable Dependabot on all three repos
2. Re-run sweep query in 24 hours
3. Commit next batch of merged PRs with provenance tracking
4. Archive this doc in `docs/governance/dependabot/tier1-secondary-2026-04-26/` once complete

---

**Compiled by**: Claude Code Agent (Haiku 4.5)  
**Date**: 2026-04-26  
**Branch**: pre-extract/tracera-sprawl-commit  
**Disk Snapshot**: 25Gi free (98% used)
