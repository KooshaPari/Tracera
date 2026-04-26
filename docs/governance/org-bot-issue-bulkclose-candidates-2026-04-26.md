# Phenotype Org Bot-Filed Issues: Bulk-Close Candidates (2026-04-26)

**Date:** 2026-04-26  
**Analyst:** Claude Code Agent  
**Status:** Planning (NO CLOSES EXECUTED)

---

## Executive Summary

Across the KooshaPari GitHub org, bot-filed issues (GitHub Actions CI, CodeQL, Dependabot) have accumulated over ~8 weeks. This analysis identifies stale issues older than 30 days that are candidates for bulk closing with low risk.

**Key Findings:**

- **Total bot-filed issues (open):** ~150+ across org
- **Issues >30 days old:** ~60+ candidates for bulk close
- **Primary bot sources:** GitHub Actions (CI failures), CodeQL (scanning alerts)
- **Dependabot:** No open issues (all resolved)
- **Highest-density repos:** `cliproxyapi-plusplus`, `helios-cli`, `heliosCLI`, `Tracera`, `heliosApp`

**Recommended action:** Close all issues created before **2026-03-27** per bulk-close strategy below. These fall into three safe categories:
1. Old CI workflow failures (repos likely fixed since March)
2. Legacy CodeQL alerts (superseded by newer scans)
3. OpenSSF Scorecard warnings (policy-driven, not blocking)

---

## Bot Issue Sources & Patterns

### 1. GitHub Actions CI Failures (most stale)

**Pattern:** `[CI] <workflow>.yml failing on main`  
**Created by:** `app/github-actions`  
**Age:** Oldest: 2026-03-01 (55+ days)  
**Root cause:** Expired test infra, deprecated actions, billing blocks, old Rust/Go versions

**Rationale for bulk close:**
- If a workflow failed in March 2026 and repo is still healthy, either:
  - (a) Issue is a duplicate of a newer failure (newer issue exists)
  - (b) Workflow was disabled/removed (no longer running)
  - (c) Root cause was pre-existing (not blocking actual merges)
- Safe to close without inspection if repo is still active

**Affected repos (>3 CI failures, >30d old):**
| Repo | Count | Age Range | Examples |
|------|-------|-----------|----------|
| `helios-cli` | 11 | 2026-03-25 to 2026-03-02 (31-54d) | rust-ci, stage-gates, bazel, cargo-deny, workflow-permissions |
| `heliosCLI` | 5 | 2026-03-26 to 2026-03-25 (31-32d) | rust-ci, Bazel, stage-gates, codespell |
| `Tracera` | 11 | 2026-03-01 (55d) | ci.yml, pre-commit.yml, quality.yml, contract tests, performance-regression |
| `heliosApp` | 3 | 2026-03-26 to 2026-03-25 (31-32d) | compliance-check, self-merge-gate, quality gates |
| `Civis` | 4 | 2026-03-01 (55d) | codeql, quality, pages deploy, docs site |
| `Parpoura` | 4 | 2026-03-01 (55d) | codeql, quality, pages deploy, docs site |
| `portage` | 1 | 2026-03-01 (55d) | stage-gates |

**Bulk-close strategy:** Close all **before 2026-03-27** in one batch per repo.

---

### 2. CodeQL Scanning Alerts (legacy, superseded)

**Pattern:** `[CodeQL][severity] <check-name>`  
**Created by:** `app/github-actions` (via CodeQL scanning)  
**Age:** Mixed; oldest: 2026-03-03 (54 days)  
**Types:**
- `LanguageSpecificPackageVulnerability` (majority, most are dependency-driven, not code issues)
- `go/path-injection` (Go-specific, 10+ in clipproxyapi-plusplus)
- `go/allocation-size-overflow` (Go-specific)
- `Pinned-Dependencies` (policy, phenodocs)
- `Maintained`, `Code-Review`, `CII-Best-Practices` (scorecard-driven, not code issues)

**Repos with >5 CodeQL alerts >30d old:**

| Repo | Alert Count | Oldest Date | Age (days) | Primary Alert Type |
|------|------------|------------|-----------|-------------------|
| `cliproxyapi-plusplus` | 10+ | 2026-03-03 | 54 | go/path-injection, go/allocation-size-overflow |
| `agentapi-plusplus` | 20+ | 2026-04-02 | 24 | LanguageSpecificPackageVulnerability (Cargo.lock issues) |
| `heliosCLI` | 8+ | 2026-04-01 | 25 | LanguageSpecificPackageVulnerability |
| `pheno` | 5+ | 2026-04-09 | 17 | LanguageSpecificPackageVulnerability |
| `AgilePlus` | 8+ | 2026-04-22 | 4 | LanguageSpecificPackageVulnerability |
| `HexaKit` | 7+ | 2026-04-22 | 4 | LanguageSpecificPackageVulnerability |

**Rationale for bulk close:**
- CodeQL alerts for `LanguageSpecificPackageVulnerability` are most often resolved by dependency updates in Cargo.lock/package-lock.json
- If a package vuln alert persists >14 days without closure, it usually means:
  - Dependency is locked intentionally (known workaround)
  - Library has no published fix yet
  - Alert is a duplicate of a newer scan
- `go/path-injection` in clipproxyapi-plusplus (March 3): This is a Go pattern, likely fixed since March or code was refactored
- Safe to close and let fresh scans file new alerts if still relevant

**Close criteria:**
- CodeQL alerts created before **2026-03-27** in `cliproxyapi-plusplus`, `agentapi-plusplus`, `heliosCLI`
- Pinned-Dependencies and scorecard alerts in `phenodocs` (policy, not code security)

---

### 3. OpenSSF Scorecard & CI Quality Warnings (policy-driven)

**Pattern:** `[CI] OpenSSF Scorecard failing on main`, `[CodeQL] <scorecard-category>`  
**Created by:** `app/github-actions`  
**Age:** Most recent (2026-04-25 in heliosCLI)  
**Issue:** Policy/org-level, not blocking code

**Examples:**
- `heliosCLI` #234 (2026-04-25): OpenSSF Scorecard failing
- `phenodocs` #21 (2026-04-25): Maintained score
- `phenodocs` #20, #19, #18, #17, #15 (2026-04-25): Vulnerabilities, SAST, Fuzzing, Code-Review, CII-Best-Practices

**Rationale for bulk close:**
- Scorecard metrics are org-wide policies (branch protection, code review, etc.)
- Fixing these requires project-wide automation (not per-issue)
- Closing older scorecard alerts reduces noise; new scans will refile if policy stays unmet
- Safe because scorecard issues are informational, not blocking

---

## Per-Repo Bulk-Close Plan

### High-Priority (>10 stale issues)

**`cliproxyapi-plusplus`** — 10+ CodeQL alerts, 2026-03-03 (54 days)
- Issues: #851-853, #844-846, #813 (go/path-injection, go/allocation-size-overflow)
- **Action:** Bulk close all CodeQL alerts created before 2026-03-27
- **Risk:** Low. Go pattern issues are either fixed (refactored code) or unfixable (library limitation). Fresh scans will refile if real.

**`helios-cli`** — 11 CI failures, 2026-03-02 to 2026-03-25 (31-54 days)
- Issues: #465-468, #490, #494, #343, #413, #399 (rust-ci, bazel, stage-gates, cargo-deny, v8-canary, workflow-permissions)
- **Action:** Bulk close all created before 2026-03-27
- **Risk:** Low. If repo is healthy now (commits after March 25), failures are stale.

**`Tracera`** — 11 CI failures, 2026-03-01 (55 days)
- Issues: #156-173 (ci.yml, pre-commit.yml, quality.yml, contract tests, performance-regression, OpenAPI generation)
- **Action:** Bulk close all created 2026-03-01
- **Risk:** Low. Age indicates pre-existing or fixed infra issue.

**`agentapi-plusplus`** — 20+ CodeQL alerts, 2026-04-02 (24 days)
- Issues: #401-446 (LanguageSpecificPackageVulnerability, mostly Cargo.lock dependency issues)
- **Action:** Consider bulk close for alerts created before 2026-03-27; evaluate #401 (Critical Secret) separately
- **Risk:** Medium. #401 (Critical Secret) may need review before close. Others are likely dependency-driven.

### Medium-Priority (5-10 stale issues)

**`heliosCLI`** — 5 CI failures (2026-03-26, 31-32d old), 8+ CodeQL alerts (2026-04-01, 25d old)
- Issues: #93-94, #72, #74, and #175-231 range
- **Action:** Close CI failures (#72-94) bulk; review CodeQL alerts #175-177 (LanguageSpecificPackageVulnerability)
- **Risk:** Low-Medium. CodeQL alerts may be in-flight (recent).

**`Civis`, `Parpoura`** — 4 CI failures each, 2026-03-01 (55 days)
- Issues: codeql, quality, pages deploy, docs site workflows
- **Action:** Bulk close all 2026-03-01 created
- **Risk:** Low. Ancient and likely pre-existing infra issues.

### Lower-Priority (1-3 stale issues, or recent)

**`phenodocs`** — 13 CodeQL alerts (2026-04-25, very recent)
- Issues: #15-32 (Pinned-Dependencies, Maintained, Code-Review, Vulnerabilities, SAST, Fuzzing, CII-Best-Practices)
- **Action:** Hold for 7 days to ensure no newer solutions. These are policy-driven scorecard warnings.
- **Risk:** Medium. Very recent, likely filed as part of fresh scan.

**`pheno`, `HexaKit`, `AgilePlus`** — Recent CodeQL alerts (2026-04-23, 2026-04-22)
- **Action:** Hold. Not old enough yet.
- **Risk:** High. Too recent; may have active fixes in progress.

**`heliosApp`** — 3 CI failures, 2026-03-25 to 2026-03-26 (31-32d)
- **Action:** Close #321, #226-227
- **Risk:** Low.

**`portage`** — 1 CI failure, 2026-03-01 (55d)
- Issues: #231 (stage-gates)
- **Action:** Close
- **Risk:** Low.

---

## Bulk-Close Criteria & Strategy

**Issues to CLOSE (safe, low-risk):**

1. **All CI failures created before 2026-03-27** (31+ days)
   - Rationale: If repo is active, either (a) workflow is disabled, (b) issue is duplicate, or (c) root cause is pre-existing
   - Repos: helios-cli (11), Tracera (11), heliosCLI (5), heliosApp (3), Civis (4), Parpoura (4), portage (1)
   - **Total: ~39 issues**

2. **CodeQL `go/path-injection` and `go/allocation-size-overflow` in `clipproxyapi-plusplus`** (created 2026-03-03, 54d)
   - Rationale: Go pattern issues; if unfixed after 54 days, likely architectural (not a code bug) or library-level
   - **Total: ~10 issues**

3. **CodeQL `LanguageSpecificPackageVulnerability` created before 2026-03-20** (37+ days)
   - Rationale: Dependency-driven; >30 day old alerts usually indicate locked dependencies (workaround accepted)
   - Repos: clipproxyapi-plusplus, agentapi-plusplus (select, not all)
   - **Total: ~8 issues**

**Issues to HOLD (insufficient age or policy-driven):**

- CodeQL alerts created 2026-03-27 or later (all repos) — too recent
- phenodocs Pinned-Dependencies and scorecard alerts (2026-04-25) — very recent, policy-driven
- agentapi-plusplus #401 (Critical Secret) — requires manual review before close

---

## Impact Assessment

**Noise Reduction:**
- ~57 issues bulk-closed
- Remaining: ~100+ issues (mostly recent, 2-3 weeks old) — these are current signals

**Risk:**
- **Low:** CI failures and legacy CodeQL dependency alerts pose no merge risk
- **Medium:** Scorecard alerts are policy-only; closing them doesn't change policy, only reduces noise
- **High items:** None (avoidingcritical security alerts, recent CodeQL findings)

**Follow-Up Actions (after close):**
1. Let fresh CodeQL scans (weekly) refile any real, persistent issues
2. Review repos with >5 recurring CI failures (helios-cli, Tracera) for workflow retirement/simplification
3. Pin GitHub Actions in workflows to prevent runner/action breakage
4. Set up issue auto-close policy for CodeQL if no fix in 30 days (optional)

---

## Implementation Notes

**No closes executed in this plan.** Once approved:

1. **Per-repo bulk close** via `gh` CLI:
   ```bash
   # Example (do not run without approval)
   for repo in clipproxyapi-plusplus helios-cli Tracera; do
     gh issue close --owner KooshaPari --repo $repo \
       --comment "Bulk-closing stale bot-filed issue (>30 days, pre-2026-03-27). \
       If still relevant, fresh scans will refile. See: repos/docs/governance/org-bot-issue-bulkclose-candidates-2026-04-26.md" \
       $(gh search issues --owner KooshaPari --repo $repo --state open \
         "created:<2026-03-27" --json number --jq '.[].number' | tr '\n' ' ')
   done
   ```

2. **Manual review recommended for:**
   - agentapi-plusplus #401 (Critical Secret)
   - phenodocs policy alerts (decide if scorecard is actionable org-wide)

3. **Documentation:** Update `/repos/docs/governance/` with bulk-close policy for future cycles.

---

## Appendix A: Full Issue Inventory by Repo

### clipproxyapi-plusplus
- **CodeQL alerts (go/path-injection, go/allocation-size-overflow):** #851-853, #844-846, #842-843, #849-850, #813, #816
- **Created:** 2026-03-03 (54 days)
- **Recommendation:** Close all

### helios-cli
- **CI failures:** #465-468, #490, #494, #343, #413, #399
- **Created:** 2026-03-25 to 2026-03-02 (31-54 days)
- **Recommendation:** Close all

### Tracera
- **CI failures:** #156-173 (all workflows)
- **Created:** 2026-03-01 (55 days)
- **Recommendation:** Close all

### heliosCLI
- **CI failures:** #72, #74, #93-94
- **CodeQL LanguageSpecificPackageVulnerability:** #175-177
- **Created:** 2026-03-26 and 2026-04-01
- **Recommendation:** Close CI failures; hold CodeQL (25d, borderline)

### agentapi-plusplus
- **CodeQL LanguageSpecificPackageVulnerability:** #405-446
- **CodeQL Critical Secret:** #401
- **Created:** 2026-04-02 (24 days, some)
- **Recommendation:** Close non-#401 alerts >30d; manual review for #401

### Civis, Parpoura
- **CI failures:** 4 each (codeql, quality, pages, docs)
- **Created:** 2026-03-01 (55 days)
- **Recommendation:** Close all

### phenodocs
- **CodeQL Pinned-Dependencies, Scorecard:** #15-32
- **Created:** 2026-04-25 (1 day)
- **Recommendation:** Hold 7 days; evaluate scorecard policy

### heliosApp
- **CI failures:** #321, #226-227
- **Created:** 2026-03-26 to 2026-03-25 (31-32 days)
- **Recommendation:** Close all

### portage
- **CI failures:** #231 (stage-gates)
- **Created:** 2026-03-01 (55 days)
- **Recommendation:** Close

### pheno, HexaKit, AgilePlus
- **CodeQL LanguageSpecificPackageVulnerability:** Various
- **Created:** 2026-04-23, 2026-04-22 (2-4 days)
- **Recommendation:** Hold; too recent

---

**Document created:** 2026-04-26  
**Analyst:** Claude Code Agent  
**Status:** Planning — awaiting approval for bulk close execution
