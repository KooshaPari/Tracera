# Security Policy

## Reporting Security Vulnerabilities

If you discover a security vulnerability, please report it responsibly.

### For Maintainers

1. **Dependabot Alerts**: Enabled for all package ecosystems
   - npm (frontend dependencies)
   - pip (Python dependencies)  
   - gomod (Go dependencies)
   - GitHub Actions
   - Docker

2. **Automated Scanning**:
   - Dependency Review Action on PRs
   - CodeQL Analysis (weekly)
   - npm audit / pip-audit
   - Trivy filesystem scanning

3. **Response SLAs**:
   - Critical: 24 hours
   - High: 7 days
   - Medium: 30 days
   - Low: 90 days

## Current Vulnerability Status

| Repo | Critical | High | Medium | Low | Worklog |
|------|----------|------|--------|-----|---------|
| trace | 2 | 13 | 6 | 4 | DEPENDABOT_VULNERABILITY_WORKLOG.md |
| thegent | 0 | 4 | 4 | 12 | THEGENT_DEPENDABOT_WORKLOG.md |
| 4sgm | 1 | 13 | 14 | 2 | 4SGM_DEPENDABOT_WORKLOG.md |
| heliosHarness | 0 | 0 | 1 | 0 | - |
| parpour | 0 | 0 | 1 | 0 | - |
| civ | 0 | 0 | 1 | 0 | - |
| cliproxyapi-plusplus | 0 | 0 | 1 | 0 | - |

## Security Hardening Guidelines

1. Enable Dependabot security updates
2. Use dependency review action on all PRs
3. Run CodeQL on main branch pushes
4. Review vulnerabilities weekly
5. Prioritize fixes by severity
