# Dependabot Configuration Guide

## Overview

TraceRTM uses Dependabot for automated dependency updates across all package ecosystems. This document describes the configuration, auto-merge rules, and best practices.

## Configuration

The Dependabot configuration is located at `.github/dependabot.yml` and covers:

- **Frontend (npm/bun)**: Root monorepo, web app, and desktop app
- **Python (pip)**: Root project and CLI tool
- **Go (gomod)**: Backend and all test modules
- **GitHub Actions**: Workflow dependencies
- **Docker**: Base image updates

## Update Schedules

Updates are scheduled by day to spread the review load:

| Day       | Ecosystem                | Time  |
|-----------|--------------------------|-------|
| Monday    | Frontend (npm)           | 09:00 |
| Tuesday   | Python (pip)             | 09:00 |
| Wednesday | Go (gomod)               | 09:00 |
| Thursday  | GitHub Actions           | 09:00 |
| Friday    | Docker                   | 09:00 |

All times are in America/New_York timezone.

## Auto-Merge Rules

### Automatic Merging

The following updates are **automatically merged** if tests pass:

1. **Patch updates** (`x.y.Z`):
   - Bug fixes
   - Security patches
   - No breaking changes expected

2. **Minor updates** (`x.Y.z`):
   - New features
   - Backward compatible
   - Non-breaking API changes

**Conditions for auto-merge**:
- All CI tests must pass
- No merge conflicts
- Dependabot is the PR author
- Update type is patch or minor

### Manual Review Required

The following updates require **manual review**:

1. **Major updates** (`X.y.z`):
   - Breaking changes
   - API changes
   - Requires changelog review

2. **Critical packages** (always manual):
   - `react` and `react-dom` (major)
   - `typescript` (major)
   - `python` interpreter

3. **Security updates**:
   - Reviewed for impact
   - May be merged immediately if critical

## Dependency Grouping

Related packages are grouped to reduce PR noise:

### Frontend Groups

- **react-ecosystem**: React and related types
- **testing-frameworks**: Vitest, Playwright, Jest, Testing Library
- **build-tools**: Vite, Turbo, TypeScript, Biome
- **ui-libraries**: Radix UI, Tailwind, Lucide

### Python Groups

- **fastapi-ecosystem**: FastAPI, Starlette, Pydantic, Uvicorn
- **database-drivers**: SQLAlchemy, Alembic, Psycopg, Neo4j
- **testing-tools**: Pytest, Coverage, Hypothesis
- **async-libraries**: AIOHTTP, HTTPX, AsyncIO

### Go Groups

- **fiber-ecosystem**: Fiber framework packages
- **database-drivers**: PostgreSQL, Neo4j, GORM
- **temporal-sdk**: Temporal workflow packages
- **aws-sdk**: AWS SDK packages
- **testing-tools**: Testify, Testcontainers

### GitHub Actions Groups

- **setup-actions**: setup-node, setup-python, setup-go
- **cache-actions**: cache, cache-cleanup
- **checkout-actions**: checkout variants

## Version Constraints

### Package Managers

Update your package files with appropriate version constraints:

#### npm/bun (package.json)

```json
{
  "dependencies": {
    "react": "^18.2.0",           // Allow minor and patch updates
    "lodash": "~4.17.21",         // Allow patch updates only
    "critical-lib": "1.2.3"       // Pin exact version
  }
}
```

**Recommendations**:
- Use `^` for most dependencies (minor + patch)
- Use `~` for critical dependencies (patch only)
- Pin exact versions for known problematic packages

#### Python (pyproject.toml)

```toml
[project]
dependencies = [
    "fastapi>=0.104.0,<0.105.0",   # Pin minor version
    "pydantic>=2.5.0",              # Allow minor and patch
    "sqlalchemy==2.0.23",           # Pin exact version
]
```

**Recommendations**:
- Use `>=x.y.z,<x.y+1.0` for stable APIs
- Use `>=x.y.z` for well-maintained packages
- Pin exact versions for critical dependencies

#### Go (go.mod)

```go
require (
    github.com/gofiber/fiber/v2 v2.51.0
    github.com/stretchr/testify v1.8.4
)
```

**Recommendations**:
- Go modules use minimum version selection
- Let Dependabot manage updates
- Review breaking changes in major versions

## Workflow Integration

### Auto-Merge Workflow

The `.github/workflows/dependabot-auto-merge.yml` workflow:

1. **Checks update type** (patch/minor/major)
2. **Runs tests** for affected ecosystems
3. **Auto-approves** patch and minor updates
4. **Enables auto-merge** with squash commits
5. **Comments** on major updates requiring review

### Test Requirements

Before auto-merging, the workflow runs:

- **Frontend**: Linting + unit tests
- **Go**: Short test suite (`go test -short`)
- **Python**: Test suite (`pytest`)

All tests must pass for auto-merge to proceed.

## Managing Dependabot PRs

### Viewing PRs

```bash
# List all Dependabot PRs
gh pr list --author "dependabot[bot]"

# View specific PR
gh pr view <PR_NUMBER>

# View Dependabot metadata
gh pr view <PR_NUMBER> --json labels,author,title
```

### Manual Actions

```bash
# Approve a PR
gh pr review <PR_NUMBER> --approve

# Merge a PR
gh pr merge <PR_NUMBER> --squash

# Close a PR (won't recreate)
gh pr close <PR_NUMBER>

# Rebase Dependabot PR
gh pr comment <PR_NUMBER> --body "@dependabot rebase"

# Recreate PR
gh pr comment <PR_NUMBER> --body "@dependabot recreate"
```

### Dependabot Commands

Comment these on Dependabot PRs:

- `@dependabot rebase` - Rebase the PR
- `@dependabot recreate` - Recreate the PR from scratch
- `@dependabot merge` - Merge the PR (if approved)
- `@dependabot squash and merge` - Squash and merge
- `@dependabot cancel merge` - Cancel auto-merge
- `@dependabot close` - Close and ignore this update
- `@dependabot ignore this minor version` - Ignore this minor version
- `@dependabot ignore this major version` - Ignore this major version
- `@dependabot ignore this dependency` - Ignore this dependency

## Security Updates

Dependabot also creates PRs for security vulnerabilities:

- **Always review** security updates
- **High/Critical**: Merge immediately after testing
- **Medium/Low**: Review during weekly update cycle
- **Check changelogs** for security advisories

### Viewing Security Alerts

```bash
# View repository security alerts (requires GitHub CLI with security scope)
gh api repos/:owner/:repo/dependabot/alerts

# View specific alert
gh api repos/:owner/:repo/dependabot/alerts/<ALERT_ID>
```

## Customization

### Adding Ignore Rules

To ignore specific updates, edit `.github/dependabot.yml`:

```yaml
updates:
  - package-ecosystem: "npm"
    directory: "/frontend"
    ignore:
      # Ignore major updates for React
      - dependency-name: "react"
        update-types: ["version-update:semver-major"]

      # Ignore all updates for a package
      - dependency-name: "problematic-package"

      # Ignore specific version
      - dependency-name: "some-package"
        versions: ["2.x", "3.x"]
```

### Adjusting Schedules

Modify the schedule for a package ecosystem:

```yaml
updates:
  - package-ecosystem: "npm"
    directory: "/frontend"
    schedule:
      interval: "daily"        # Options: daily, weekly, monthly
      day: "monday"           # For weekly: monday-sunday
      time: "09:00"           # 24-hour format
      timezone: "UTC"         # Any valid timezone
```

### Pull Request Limits

Adjust the number of concurrent PRs:

```yaml
updates:
  - package-ecosystem: "npm"
    directory: "/frontend"
    open-pull-requests-limit: 10  # Default: 5, Max: 10
```

## Best Practices

### 1. Review Dependencies Regularly

- **Weekly**: Review auto-merged PRs
- **Monthly**: Review open Dependabot PRs
- **Quarterly**: Audit all dependencies for unused packages

### 2. Test Before Merging

- Ensure CI passes completely
- Run integration tests locally for major updates
- Check release notes for breaking changes

### 3. Update Version Constraints

- Keep `package.json` constraints reasonable
- Don't pin everything to exact versions
- Use lock files for reproducibility

### 4. Monitor Dependabot Notifications

- Enable GitHub notifications for Dependabot
- Set up Slack/email alerts for security updates
- Review Dependabot alerts in GitHub Security tab

### 5. Handle Conflicts

```bash
# Rebase conflicting PR
gh pr comment <PR_NUMBER> --body "@dependabot rebase"

# If that fails, close and recreate
gh pr close <PR_NUMBER>
# Wait for Dependabot to recreate
```

### 6. Batch Updates

For major refactoring:

```bash
# Temporarily disable Dependabot
# Edit .github/dependabot.yml and set:
# open-pull-requests-limit: 0

# Re-enable after refactoring
# open-pull-requests-limit: 5
```

## Troubleshooting

### Issue: Too Many PRs

**Solution**: Reduce open PR limits or use grouping

```yaml
open-pull-requests-limit: 3
groups:
  all-dependencies:
    patterns: ["*"]
```

### Issue: Auto-Merge Not Working

**Checks**:
1. Verify branch protection rules allow auto-merge
2. Check workflow permissions in `.github/workflows/dependabot-auto-merge.yml`
3. Ensure `GITHUB_TOKEN` has required permissions
4. Verify tests are passing

### Issue: Dependabot Not Creating PRs

**Solutions**:
1. Check `.github/dependabot.yml` syntax
2. Verify directories exist
3. Check if open PR limit reached
4. Look for ignore rules blocking updates

### Issue: Security Alert Not Creating PR

**Solutions**:
1. Check if dependency is in package file
2. Verify Dependabot security updates enabled in repo settings
3. Check if update is being ignored

## Metrics and Monitoring

### Track Update Success

```bash
# View merged Dependabot PRs (last 30)
gh pr list --state merged --author "dependabot[bot]" --limit 30

# View update frequency
gh pr list --state all --author "dependabot[bot]" --json createdAt,title

# View auto-merge success rate
gh run list --workflow "dependabot-auto-merge.yml"
```

### Dashboard Widgets

Add to GitHub Projects:

- **Open Dependabot PRs**: Filter by `author:dependabot[bot] is:open`
- **Security Updates**: Filter by `label:security`
- **Auto-merged PRs**: Filter by `author:dependabot[bot] is:merged`

## Resources

- [Dependabot Documentation](https://docs.github.com/en/code-security/dependabot)
- [Configuration Options](https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file)
- [Auto-merge PR Actions](https://github.com/dependabot/fetch-metadata)
- [Security Advisories](https://github.com/advisories)

## Support

For issues with Dependabot configuration:

1. Check this guide
2. Review GitHub Dependabot logs
3. Test configuration locally with `dependabot/cli`
4. Open issue in repository with `dependabot` label
