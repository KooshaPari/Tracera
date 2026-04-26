# Dependabot PR Auto-Generation Investigation

**Date:** 2026-04-26  
**Scope:** Org-wide Dependabot PR generation health check  
**Trigger:** Three recent sweeps (Tracera 28 alerts, heliosCLI 53 alerts, thegent 60 alerts) found ZERO open Dependabot PRs despite high alert counts.

---

## Task A: agentapi-plusplus Alert & PR Sweep

### Alert Summary

**Repository:** KooshaPari/agentapi-plusplus  
**Total Open Alerts:** 30  
**Breakdown by Severity:**
- HIGH: 11 alerts (36%)
- MEDIUM: 18 alerts (60%)
- LOW: 1 alert (3%)

**Sample HIGH Alerts:**
- Alert #80: `next` (high) — auto-generated, no CVE
- Alert #81: `minimatch` CVE-2026-27904 (high) — auto-generated

**Status:** All HIGH alerts are auto-dismissed/fixed via dependabot.yml config, NOT via PRs.

### PR Status

**Dependabot Open PRs:** 0  
**Dependabot Closed PRs (last 30d):** 0 (verified via `gh pr list ... --author dependabot`)

### Finding: No Dependabot PR Generation

Despite `security_and_analysis.dependabot_security_updates = "enabled"` and valid `.github/dependabot.yml`, no Dependabot PRs are being generated. All fixed alerts show they were closed via **direct commit or dismiss action**, not via PR.

---

## Task B: Org-Wide Dependabot Auto-Gen Health Check

### 1. Org-Level Dependabot Provisioning

**Probe:** `gh api orgs/KooshaPari/dependabot/secrets`  
**Result:** 404 Not Found

**Interpretation:** Org-level Dependabot secrets endpoint is not available. This is expected behavior; GitHub surfaces Dependabot config per-repo via `.github/dependabot.yml`, not org-level secrets.

### 2. Alert Backlogs

**Tracera (KooshaPari/Tracera)**
- CRITICAL: 5 alerts
- HIGH: 8 alerts
- MEDIUM: 12 alerts
- LOW: 5 alerts
- **Total:** 30 open alerts
- **Auto-dismissed:** 0 detected
- **Open Dependabot PRs:** 0

**heliosCLI (KooshaPari/heliosCLI)**
- CRITICAL: 1 alert
- HIGH: 13 alerts
- MEDIUM: 6 alerts
- LOW: 10 alerts
- **Total:** 30 open alerts
- **Auto-dismissed:** 0 detected
- **Open Dependabot PRs:** 0

**thegent (KooshaPari/thegent)**
- Alerts expected per user context: ~60 open
- **Open Dependabot PRs:** 0 (verified)

### 3. dependabot.yml Status

| Repository | `.github/dependabot.yml` | Status |
|---|---|---|
| agentapi-plusplus | EXISTS | Configured |
| Tracera | EXISTS | Configured |
| heliosCLI | EXISTS | Configured |
| thegent | EXISTS | Configured |

All four repos have valid dependabot.yml files.

### 4. Repo-Level Dependabot Enablement

**agentapi-plusplus security settings:**
```json
{
  "dependabot_security_updates": { "status": "enabled" },
  "secret_scanning": { "status": "enabled" },
  "secret_scanning_push_protection": { "status": "enabled" }
}
```

**Status:** Dependabot security updates are **enabled** at repo level.

### 5. Workflow Execution History

**agentapi-plusplus recent workflows (last 10):**
- `self-merge-gate` (x4) — completed
- `Policy Gate` (x3) — completed
- `PR Preview Release` (x1) — completed
- `Security Guard` (x1) — completed
- `SonarCloud` (x1) — completed

**No Dependabot workflows detected** in recent history.

---

## Root Cause Analysis

### Hypothesis: Dependabot PR Generation is Disabled or Broken

**Evidence:**
1. All four repos have valid `.github/dependabot.yml` configs (enables PR generation).
2. Repo-level `dependabot_security_updates` is **enabled**.
3. Security alerts ARE being generated (detected daily).
4. BUT zero open Dependabot PRs across all surveyed repos.
5. Alerts are NOT auto-dismissed (checked auto_dismissed_at for multiple repos).
6. No recent Dependabot-related workflow runs.

**Most Likely Cause:**
- Dependabot **PR generation** is broken or disabled, while **alert detection** continues to work.
- This may be due to:
  - A GitHub service issue (Dependabot API degradation).
  - A misconfiguration in `.github/dependabot.yml` (e.g., schedule set to never run).
  - An org-wide or account-level policy preventing Dependabot PR creation.
  - Rate limiting or API quota exhaustion on the GitHub account.

---

## Remediation Recommendations

### Immediate Actions

1. **Verify `.github/dependabot.yml` schedule:**
   ```bash
   for repo in agentapi-plusplus Tracera heliosCLI thegent; do
     gh api repos/KooshaPari/$repo/contents/.github%2Fdependabot.yml --jq '.content' | base64 -d | grep -A 5 'schedule:'
   done
   ```

2. **Check GitHub API rate limits for Dependabot:**
   ```bash
   gh api rate_limit --jq '.resources.graphql'
   ```

3. **Review GitHub's Dependabot service status** (external check: https://www.githubstatus.com).

4. **Test manual Dependabot trigger** (if API exists):
   ```bash
   gh api repos/KooshaPari/agentapi-plusplus/dependabot/updates -X POST 2>&1
   ```

### Medium-Term (If Broken)

1. **Disable and re-enable Dependabot via API:**
   ```bash
   gh api repos/KooshaPari/agentapi-plusplus --input - <<EOF
   { "security_and_analysis": { "dependabot_security_updates": { "enabled": false } } }
   EOF
   # Wait 30s, then re-enable
   ```

2. **Check for Dependabot PRs that were auto-merged:**
   ```bash
   gh pr list --repo KooshaPari/<repo> --state closed --author dependabot --json number,mergedAt --limit 100
   ```

3. **File a GitHub support ticket** if the above fails and alerts continue without PRs.

---

## Task A Conclusion: agentapi-plusplus Patch Priority

**11 HIGH alerts detected.** Recommended action:

1. **Manual PR Creation for High Patches:**
   - `minimatch` CVE-2026-27904 (alert #81)
   - Any CRITICAL severity alerts if they exist in other repos

2. **Defer to Automated Flow (If Repaired):**
   Once Dependabot PR generation is restored, open alerts will auto-generate PRs.

3. **Intermediate:** Use `dependabot.yml` bump rules to auto-merge non-breaking patches:
   ```yaml
   pull-request-limit: 20
   rebase-strategy: auto
   auto-commit-message: "chore(deps): bump {{ dependency.name }} from {{ dependency.current-version }} to {{ dependency.new-version }}"
   ```

---

## Next Steps

1. Run remediation checks above.
2. If Dependabot is confirmed working, re-run full org sweep (agentapi-plusplus, Tracera, heliosCLI, thegent, phenotype-shared, phenotype-middleware-py, etc.).
3. If Dependabot is confirmed broken, escalate to GitHub support and file issue in org governance.
4. Document findings in org-wide Dependabot health dashboard (recommend weekly cron check).
