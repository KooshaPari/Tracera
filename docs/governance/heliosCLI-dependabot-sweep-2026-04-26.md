# HeliosCLI Dependabot Sweep Report (2026-04-26)

**Status:** Analysis and alerting complete. No Dependabot PRs currently open; remediation requires manual triage and targeted updates.

**Scope:** 53 open Dependabot security alerts (1 CRITICAL, 22 HIGH, 18 MODERATE, 12 LOW).

---

## Critical Alert (1)

| Alert # | Package | CVE | CVSS | Vulnerable Range | Patch | Ecosystem |
|---------|---------|-----|------|------------------|-------|-----------|
| 40 | handlebars | CVE-2026-33937 | 9.8 (CRITICAL) | >= 4.0.0, <= 4.7.8 | >= 4.7.9 | npm |

**Details:** JavaScript Injection via AST Type Confusion (GHSA-2w6w-674q-4c4q). `NumberLiteral.value` in compiled AST is emitted verbatim without sanitization, allowing RCE via crafted AST injection. **Immediate action required.**

---

## High-Severity Packages (22 alerts across 10 packages)

| Package | Ecosystem | Alert Count | Alert #s |
|---------|-----------|-------------|----------|
| handlebars | npm | 5 | 44, 43, 42, 41, 40 |
| minimatch | npm | 6 | 27, 26, 25, 24, 22, 21 |
| picomatch | npm | 2 | 33, 32 |
| path-to-regexp | npm | 1 | 45 |
| rollup | npm | 1 | 23 |
| flatted | npm | 2 | 29, 28 |
| glob | npm | 1 | 12 |
| @modelcontextprotocol/sdk | npm | 2 | 17, 15 |
| GitPython | pip | 2 | 69, 68 |
| rustls-webpki | rust | 1 | 63 |

**Impact:** 9 npm transitive dependency vulnerabilities, 1 pip (Python), 1 Rust. Most are build-time or tool-chain dependencies; verify runtime exposure before patching.

---

## Current State

**Dependabot PRs (Open):** 0

**Recent Dependabot Merges (2026-04-25):**
- PR #196–190: 7 Dependabot PRs merged same-day (Rust toolchain, Node base image, transitive deps in /codex-rs and /codex-cli)
- Pattern: patch/minor version bumps only; no major-version changes

**Alert Timeline:** Snapshot created 2026-04-26 (1 day post-merge batch)

---

## Assessment

### Why No Dependabot PRs Are Open

1. **Auto-grouped PRs were recently merged.** Dependabot groups related updates; the 2026-04-25 batch cleared earlier alerts.
2. **New alerts may not have triggered PR generation yet.** GitHub Dependabot has a ~24–48h lag for new alert detection → PR creation.
3. **Dependabot may be rate-limited or disabled.** Check repository security settings.
4. **Critical handlebars alert (CVE-2026-33937) is in a transitive dependency.** Requires updates to packages that directly depend on handlebars (e.g., rollup, build toolchain).

### Recommended Triage Path

1. **Immediate (CRITICAL):**
   - Update all npm dependencies to pull handlebars >= 4.7.9
   - Scan pnpm-lock.yaml for handlebars entries; update to >= 4.7.9
   - Force-resolve transitive deps: `pnpm install --force` or modify pnpm-lock.yaml directly
   - Test build; commit lock-file update

2. **High Priority (HIGH):**
   - minimatch (6 alerts): upgrade to latest (3.0.7+)
   - glob (1 alert): upgrade to latest (10.4.0+)
   - GitPython (2 alerts): upgrade pip dep to latest (3.1.44+)
   - @modelcontextprotocol/sdk (2 alerts): verify MCP SDK version in use; upgrade if safe

3. **Medium Priority (MODERATE + LOW):**
   - Batch remaining medium and low alerts; update during next dependency refresh cycle

---

## Residual Alert Summary

| Severity | Count | Estimated Effort |
|----------|-------|-----------------|
| CRITICAL | 1 | < 1h (handlebars transitive) |
| HIGH | 22 | 2–4h (lock-file updates + retesting) |
| MODERATE | 18 | Deferred to next cycle |
| LOW | 12 | Deferred to next cycle |
| **Total** | **53** | ~3–5h (full sweep) |

---

## Merged PRs (2026-04-25)

These PRs were already merged; listed for context:

- PR #196: bump rmcp (0.15.0 → 1.3.0) in /codex-rs
- PR #195: bump webbrowser (1.0.6 → 1.2.0) in /codex-rs
- PR #194: bump cc (1.2.55 → 1.2.59) in /codex-rs
- PR #193: bump inventory (0.3.21 → 0.3.24) in /codex-rs
- PR #192: bump indexmap (2.13.0 → 2.13.1) in /codex-rs
- PR #191: bump node (24-slim → 25-slim) in /codex-cli
- PR #190: bump rust-toolchain (1.93.0 → 1.94.1) in /codex-rs

**Merge Status:** All merged 2026-04-25T14:24–14:25 UTC

---

## Next Steps

1. **Verify Dependabot is enabled** on the repo (Settings → Code security & analysis → Dependabot alerts)
2. **Manual PR for handlebars critical:** Open PR targeting pnpm-lock.yaml with handlebars >= 4.7.9
3. **Wait 48h for Dependabot PRs** on remaining HIGH alerts; if none appear, manually update lock files
4. **Admin-merge** low-risk patch/minor PRs after build verification
5. **Document final state** once resolved

---

**Prepared by:** Claude Agent (API-only sweep, 2026-04-26)
**Repo:** KooshaPari/heliosCLI
**Snapshot Ref:** dependabot-alert-tier1-snapshot-2026-04-26.md
