# Dependabot Quick Reference

## Common Commands

### Viewing PRs

```bash
# List all Dependabot PRs
gh pr list --author "dependabot[bot]"

# View PR details
gh pr view <PR_NUMBER>

# Check PR status
gh pr checks <PR_NUMBER>
```

### Managing PRs

```bash
# Approve PR
gh pr review <PR_NUMBER> --approve

# Merge PR
gh pr merge <PR_NUMBER> --squash

# Close PR (ignore update)
gh pr close <PR_NUMBER>
```

### Dependabot Commands (via PR comments)

```
@dependabot rebase               # Rebase the PR
@dependabot recreate             # Recreate the PR
@dependabot merge                # Merge if approved
@dependabot squash and merge     # Squash and merge
@dependabot cancel merge         # Cancel auto-merge
@dependabot close                # Close and ignore
@dependabot ignore this minor    # Ignore minor version
@dependabot ignore this major    # Ignore major version
```

## Auto-Merge Behavior

| Update Type | Action          | Review Required |
|-------------|-----------------|-----------------|
| Patch       | Auto-merge      | No              |
| Minor       | Auto-merge      | No              |
| Major       | Manual review   | Yes             |
| Security    | Comment/notify  | Case-by-case    |

## Configuration Locations

| File | Purpose |
|------|---------|
| `.github/dependabot.yml` | Main configuration |
| `.github/workflows/dependabot-auto-merge.yml` | Auto-merge workflow |
| `docs/guides/DEPENDABOT_GUIDE.md` | Full documentation |

## Update Schedules

| Ecosystem | Day | Time |
|-----------|-----|------|
| npm (Frontend) | Monday | 09:00 ET |
| pip (Python) | Tuesday | 09:00 ET |
| gomod (Go) | Wednesday | 09:00 ET |
| GitHub Actions | Thursday | 09:00 ET |
| Docker | Friday | 09:00 ET |

## Dependency Groups

### Frontend
- `react-ecosystem`: React packages
- `testing-frameworks`: Test tools
- `build-tools`: Build system
- `ui-libraries`: UI components

### Python
- `fastapi-ecosystem`: FastAPI stack
- `database-drivers`: DB clients
- `testing-tools`: Test frameworks
- `async-libraries`: Async utils

### Go
- `fiber-ecosystem`: Fiber packages
- `database-drivers`: DB drivers
- `temporal-sdk`: Temporal workflow
- `testing-tools`: Test utilities

## Ignore Rules

Edit `.github/dependabot.yml`:

```yaml
ignore:
  # Ignore major updates
  - dependency-name: "react"
    update-types: ["version-update:semver-major"]

  # Ignore all updates
  - dependency-name: "problematic-package"

  # Ignore specific versions
  - dependency-name: "some-package"
    versions: ["2.x"]
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Too many PRs | Reduce `open-pull-requests-limit` |
| Auto-merge fails | Check branch protection + permissions |
| No PRs created | Verify config syntax + directories |
| Conflicts | Comment `@dependabot rebase` |

## Quick Disable/Enable

**Disable** (edit `.github/dependabot.yml`):
```yaml
open-pull-requests-limit: 0
```

**Enable**:
```yaml
open-pull-requests-limit: 5
```

## Security Alerts

```bash
# View alerts (requires security scope)
gh api repos/:owner/:repo/dependabot/alerts

# View specific alert
gh api repos/:owner/:repo/dependabot/alerts/<ID>
```

## Metrics

```bash
# Merged PRs (last 30)
gh pr list --state merged --author "dependabot[bot]" --limit 30

# Auto-merge workflow runs
gh run list --workflow "dependabot-auto-merge.yml"

# Open PRs by label
gh pr list --label "dependencies"
```

## Version Constraints

### npm/bun
```json
"^1.2.3"   // >=1.2.3 <2.0.0 (minor + patch)
"~1.2.3"   // >=1.2.3 <1.3.0 (patch only)
"1.2.3"    // exact version
```

### Python
```toml
">=1.2.3,<2.0.0"   # Pin major
">=1.2.3"          # Allow all updates
"==1.2.3"          # Exact version
```

### Go
```go
// Uses minimum version selection
require (
    github.com/pkg/name v1.2.3
)
```

## Resources

- [Full Guide](../guides/DEPENDABOT_GUIDE.md)
- [GitHub Docs](https://docs.github.com/en/code-security/dependabot)
- [Configuration Reference](https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file)
