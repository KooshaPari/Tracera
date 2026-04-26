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
| Stack | Polyglot (Rust + Go) |

### Manual Audit Results

**Rust (`cargo audit`)**:
- Warnings: 1 (RUSTSEC-2024-0413: gtk-rs GTK3 bindings unmaintained)
  - Crate: atk 0.18.2
  - Path: atk → gtk → wry → tauri-runtime-wry → tauri → tauri-plugin-os → app 0.1.0
  - Severity: Warning (non-blocking, upstream lib no longer maintained)
  - Action: Monitor for replacement or plan gtk-rs removal

**Go (`govulncheck ./...`)**:
- Result: No vulnerabilities found

**Action Items**:
- Evaluate GTK dependency replacement (non-blocking)
- Verify Dependabot is enabled in GitHub settings for future tracking
- Keep Go deps current via `go mod tidy && go mod update`

---

## AgilePlus — Analysis

| Metric | Status |
|--------|--------|
| Active | Yes (pushed 2026-04-26 05:54 UTC) |
| Archived | No |
| Open Issues | 46 |
| Open PRs | 0 (dependency-related) |
| Dependabot Alerts | Not accessible via API |
| Stack | Rust monorepo (704 dependencies) |

### Manual Audit Results

**Rust (`cargo audit --deny warnings`)**:
- Warnings: 1 (RUSTSEC-2024-0436: paste crate unmaintained)
  - Crate: paste 1.0.15
  - Path: paste → utoipa-axum 0.2.0 → agileplus-api 0.1.1 → agileplus-contract-tests 0.1.1
  - Severity: Warning (unmaintained upstream)
  - Action: Evaluate `paste` replacement or plan macro approach refactor
  - Note: utoipa-axum 0.2.0 may have newer versions with updated dependencies

**Dependencies Scanned**: 704 total crate dependencies

**Action Items**:
- Review `utoipa-axum` for newer version (check upstream)
- Evaluate alternatives to `paste` crate for macro generation
- Enable Dependabot in GitHub settings for ongoing monitoring
- Triage 46 open issues for security-labeled items

---

## hwLedger — Analysis

| Metric | Status |
|--------|--------|
| Active | Yes (pushed 2026-04-26 05:54 UTC) |
| Archived | No |
| Open Issues | 0 |
| Open PRs | 0 |
| Dependabot Alerts | Not accessible via API |
| Stack | Rust + Swift (Tauri desktop app) |

### Manual Audit Results

**Rust (`cargo audit`)**:
- Warnings: 1 (RUSTSEC-2024-0413: gtk-rs GTK3 bindings unmaintained)
  - Crate: atk 0.18.2
  - Path: atk → gtk → wry → tauri-runtime-wry → tauri → tauri-plugin-shell → hwledger-tauri 0.0.1
  - Severity: Warning (upstream GUI lib no longer maintained)
  - Action: Monitor for GTK replacement or evaluate alternative GUI frameworks
  - Impact: Desktop app rendering layer

**Dependencies Scanned**: 947 total crate dependencies

**Swift**: No native Dependabot; require manual Package.swift review (not automated)

**Action Items**:
- Plan GTK replacement strategy (note: shared with BytePort)
- Enable Dependabot in GitHub settings for ongoing Rust tracking
- Manual Swift Package Manager audit when WP21 unblocks (codesign prereq)

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

**Current State (2026-04-26 06:10 UTC)**:

| Finding | Severity | Repo | Type | Action |
|---------|----------|------|------|--------|
| gtk-rs (atk 0.18.2) unmaintained | Warning | BytePort, hwLedger | Transitive (wry → tauri) | Monitor for replacement |
| paste crate (1.0.15) unmaintained | Warning | AgilePlus | Transitive (utoipa-axum) | Evaluate version update or replacement |
| 46 open issues | TBD | AgilePlus | Requires manual triage | Review for security labels |

**Disk Status**: 25Gi (tight); no cargo builds initiated

**No actionable HIGH/CRITICAL vulnerabilities** — all findings are warnings on unmaintained upstream libraries.

**Follow-Up**:
1. Enable Dependabot on all three repos via GitHub Settings
2. Re-run sweep query in 24–48 hours post-enablement
3. Evaluate GTK dependency replacement strategy (shared concern: BytePort + hwLedger)
4. Triage AgilePlus open issues for security-labeled items
5. Monitor utoipa-axum for version updates (AgilePlus)
6. Commit next batch of merged PRs with provenance tracking
7. Archive this doc in `docs/governance/dependabot/tier1-secondary-2026-04-26/` once complete

---

**Compiled by**: Claude Code Agent (Haiku 4.5)  
**Date**: 2026-04-26  
**Branch**: pre-extract/tracera-sprawl-commit  
**Disk Snapshot**: 25Gi free (98% used)
