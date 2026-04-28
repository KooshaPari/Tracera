# Branch Protection Quick Reference

## Quick Start

```bash
# Apply protection to main branch
bash backend/scripts/setup-branch-protection.sh

# Test without applying changes
DRY_RUN=1 bash backend/scripts/setup-branch-protection.sh
```

## Required Status Checks

| Check | Purpose |
|-------|---------|
| `go-tests` | Go backend tests & linting |
| `python-tests` | Python backend tests & linting |
| `frontend-packages-test` | Component library tests |
| `frontend-web-test` | Web app (React) tests |
| `frontend-docs-test` | Docs site tests |
| `frontend-desktop-test` | Electron app tests |
| `quality-guards` | Naming & LOC checks |

## Configuration

| Variable | Default | Example |
|----------|---------|---------|
| `BRANCH` | `main` | `BRANCH=develop` |
| `MIN_APPROVALS` | `1` | `MIN_APPROVALS=2` |
| `DRY_RUN` | `0` | `DRY_RUN=1` |
| `VERBOSE` | `0` | `VERBOSE=1` |
| `REPO` | auto-detect | `REPO=owner/repo` |

## Common Commands

```bash
# Protect main with defaults
bash backend/scripts/setup-branch-protection.sh

# Protect develop branch
BRANCH=develop bash backend/scripts/setup-branch-protection.sh

# Require 2 approvals
MIN_APPROVALS=2 bash backend/scripts/setup-branch-protection.sh

# Verbose output
VERBOSE=1 bash backend/scripts/setup-branch-protection.sh

# Combined options
BRANCH=release MIN_APPROVALS=2 VERBOSE=1 bash backend/scripts/setup-branch-protection.sh
```

## Protection Rules Applied

1. **Status Checks**: All 7 checks must pass
2. **Up-to-Date**: Branch must be synced with main
3. **Code Review**: Minimum 1 approval required
4. **Stale Reviews**: Auto-dismissed on new commits
5. **Force Push**: Admins only
6. **Direct Push**: Admins only

## Prerequisites

```bash
# Install GitHub CLI
# macOS: brew install gh
# Linux/Windows: https://cli.github.com/

# Authenticate with admin scope
gh auth login --scopes repo:admin

# Verify authentication
gh auth status
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Not authenticated" | Run `gh auth login --scopes repo:admin` |
| "Permission denied" | Verify you have admin access to repo |
| "Repository not found" | Set `REPO=owner/repo` explicitly |

## Verify Protection

```bash
# Check if protected
gh api repos/OWNER/REPO/branches/main --jq '.protected'

# View protection rules
gh api repos/OWNER/REPO/branches/main/protection
```

## Full Documentation

See `/docs/guides/BRANCH_PROTECTION_SETUP.md` for:
- Detailed rule explanations
- Modification procedures
- CI/CD integration examples
- Admin override procedures
