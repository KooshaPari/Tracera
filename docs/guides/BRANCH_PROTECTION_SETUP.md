# Branch Protection Configuration Guide

## Overview

This guide explains how to configure GitHub branch protection rules for the main branch to enforce code quality, testing, and review requirements before merging.

## Quick Start

### Prerequisites

1. **GitHub CLI (gh)** - Install from https://cli.github.com/
2. **GitHub Authentication** - Authenticate with `repo:admin` scope:
   ```bash
   gh auth login --scopes repo:admin
   ```
3. **Admin Access** - You must have admin access to the repository

### Apply Protection Rules

```bash
# Apply default protection rules to main branch
bash backend/scripts/setup-branch-protection.sh

# Test mode (validate without applying)
DRY_RUN=1 bash backend/scripts/setup-branch-protection.sh

# Protect a different branch with custom settings
BRANCH=develop MIN_APPROVALS=2 bash backend/scripts/setup-branch-protection.sh
```

## Protection Rules Explained

### 1. Required Status Checks

All of these CI checks must pass before a pull request can be merged:

| Check | Purpose |
|-------|---------|
| `go-tests` | Go backend unit tests, benchmarks, and linting |
| `python-tests` | Python backend unit tests, linting, and coverage |
| `frontend-packages-test` | Component library and shared package tests |
| `frontend-web-test` | Web application (React) tests and coverage |
| `frontend-docs-test` | Documentation site tests and build verification |
| `frontend-desktop-test` | Electron desktop application tests |
| `quality-guards` | Naming convention and LOC limit enforcement |

**Why:** Prevents broken code from being merged. Ensures all CI pipelines pass successfully before integration.

**Configuration:**
- `strict_required_status_checks_policy: true` - Branches must be up-to-date with base before checks pass
- All 7 checks must pass (not optional)

### 2. Branch Up-to-Date Requirement

Branches must be rebased or synced with the main branch before merge.

**Why:** Prevents stale test results and merge conflicts. Ensures CI runs against the actual merged state.

**Behavior:** GitHub will prevent merge if branch is behind main, requiring developer to sync/rebase first.

### 3. Code Review Requirements

- **Minimum Approvals:** 1 review approval required
- **Dismiss Stale Reviews:** Reviews are automatically dismissed when new commits are pushed
- **Code Owner Review:** Not required (can be enabled per project policy)
- **Last Push Approval:** Not required (any approval counts, even if developer added commits after)

**Why:** Ensures human review of code changes. Dismissing stale reviews prevents bypassing reviews via new commits.

**Configurable via environment:**
```bash
MIN_APPROVALS=2 bash backend/scripts/setup-branch-protection.sh
```

### 4. Admin-Only Restrictions

- **Force Pushes:** Restricted to repository administrators only
- **Direct Commits:** Only admins can push directly to main (all others must use pull requests)
- **Branch Deletion:** Prevented for all users

**Why:** Protects against accidental or malicious modifications to main. Enforces pull request workflow for all contributors.

## Configuration Reference

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `REPO` | auto-detect | GitHub repository (owner/repo) |
| `BRANCH` | `main` | Branch to protect |
| `MIN_APPROVALS` | `1` | Minimum review approvals required |
| `DRY_RUN` | `0` | Set to 1 to validate without applying |
| `VERBOSE` | `0` | Set to 1 for detailed output |

### Examples

```bash
# Protect develop branch
BRANCH=develop bash backend/scripts/setup-branch-protection.sh

# Require 2 approvals instead of 1
MIN_APPROVALS=2 bash backend/scripts/setup-branch-protection.sh

# Verbose output for debugging
VERBOSE=1 bash backend/scripts/setup-branch-protection.sh

# Dry-run to see what would change
DRY_RUN=1 bash backend/scripts/setup-branch-protection.sh

# All options combined
REPO=myorg/myrepo BRANCH=main MIN_APPROVALS=1 VERBOSE=1 bash backend/scripts/setup-branch-protection.sh
```

## Modifying Protection Rules

### Increase Review Approvals

To require 2 approvals instead of 1:

```bash
MIN_APPROVALS=2 bash backend/scripts/setup-branch-protection.sh
```

### Add Additional Status Checks

Edit `backend/scripts/setup-branch-protection.sh` and modify the `REQUIRED_CHECKS` array:

```bash
readonly REQUIRED_CHECKS=(
  "go-tests"
  "python-tests"
  "frontend-packages-test"
  "frontend-web-test"
  "frontend-docs-test"
  "frontend-desktop-test"
  "quality-guards"
  "your-new-check"  # Add here
)
```

Then re-run the script:

```bash
bash backend/scripts/setup-branch-protection.sh
```

### Protect Multiple Branches

```bash
# Protect main
bash backend/scripts/setup-branch-protection.sh

# Protect develop
BRANCH=develop bash backend/scripts/setup-branch-protection.sh

# Protect release branch with stricter requirements
BRANCH=release MIN_APPROVALS=2 bash backend/scripts/setup-branch-protection.sh
```

## Troubleshooting

### "Not authenticated"

Solution: Authenticate with GitHub CLI:
```bash
gh auth login --scopes repo:admin
```

### "Permission denied"

Solutions:
1. Verify you have admin access to the repository
2. Check your GitHub token has `repo:admin` scope:
   ```bash
   gh auth status
   ```
3. Re-authenticate:
   ```bash
   gh auth logout
   gh auth login --scopes repo:admin
   ```

### "Repository not found"

Solutions:
1. Verify the repository is accessible:
   ```bash
   gh repo view
   ```
2. Set REPO explicitly:
   ```bash
   REPO=owner/repo bash backend/scripts/setup-branch-protection.sh
   ```
3. Check git remote:
   ```bash
   git remote -v
   ```

### "Failed to apply branch protection rules"

Solutions:
1. Check your GitHub CLI is up-to-date:
   ```bash
   gh version
   gh upgrade
   ```
2. Verify branch exists:
   ```bash
   gh repo view <owner/repo> --json defaultBranchRef
   ```
3. Try dry-run for more details:
   ```bash
   VERBOSE=1 DRY_RUN=1 bash backend/scripts/setup-branch-protection.sh
   ```

## Idempotency

The script is **idempotent** - you can run it multiple times safely:
- Existing rules are **updated**, not duplicated
- No side effects from running multiple times
- Safe for CI/CD automation

## Verification

After running the script, verify protection is applied:

```bash
# View branch protection status
gh api repos/OWNER/REPO/branches/main --jq '.protected'

# View detailed protection rules
gh api repos/OWNER/REPO/branches/main/protection

# In GitHub UI
# Settings → Branches → Branch protection rules
```

## CI/CD Integration

### GitHub Actions Workflow Example

```yaml
name: Setup Branch Protection
on:
  workflow_dispatch:  # Manual trigger
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday

jobs:
  setup-protection:
    runs-on: ubuntu-latest
    permissions:
      admin: true  # Requires GitHub admin access
    steps:
      - uses: actions/checkout@v4

      - name: Setup branch protection
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          bash backend/scripts/setup-branch-protection.sh
```

## Bypassing Protection (Admins Only)

Repository admins can temporarily bypass protection for emergency fixes:

1. In GitHub UI: Settings → Branches → Branch protection rules
2. Temporarily disable rule
3. Make necessary changes
4. Re-enable protection

**Note:** This should only be used for critical hotfixes. All other changes must follow the pull request workflow.

## Related Configuration

### GitHub API Documentation
- [Repository Rules API](https://docs.github.com/en/rest/repos/rules)
- [Branch Protection API](https://docs.github.com/en/rest/branches/branch-protection)

### Project Settings
- CI/CD workflows: `.github/workflows/ci.yml`
- Status check names defined in GitHub Actions
- Code review policy: Adjust `MIN_APPROVALS` as needed

### Script Location
- **Script:** `/backend/scripts/setup-branch-protection.sh`
- **Documentation:** `/docs/guides/BRANCH_PROTECTION_SETUP.md`

## Support

### Common Questions

**Q: Can I require code owner reviews?**
A: Yes, modify the script to set `require_code_owner_reviews=true`

**Q: How do I know which checks are failing?**
A: Click the "Details" link on a pull request to see which CI checks didn't pass

**Q: Can developers merge without approval?**
A: No - minimum 1 approval is required. This can be increased via `MIN_APPROVALS`

**Q: What if a check is broken?**
A: You must either fix the check or temporarily disable it in the script and re-run

### Getting Help

1. Check the script's built-in help: `head -100 backend/scripts/setup-branch-protection.sh`
2. Review GitHub documentation: https://docs.github.com/en/repositories/configuring-branches-and-merges-pull-requests
3. Check GitHub CLI help: `gh help api`
