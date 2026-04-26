---
name: Security Scan
description: Automated security scanning with Trivy and GitGuardian integration
triggers:
  - security scan
  - vulnerability check
  - dependency audit
  - secret detection
---

# Security Scan Skill

Comprehensive security scanning for dependencies, secrets, and vulnerabilities.

## What This Does

Runs multiple security checks:
1. **Trivy** - Container and dependency vulnerability scanning
2. **GitGuardian** - Secret detection in code and commits
3. **npm/bun audit** - JavaScript dependency vulnerabilities
4. **go mod verify** - Go dependency integrity
5. **pip-audit** - Python dependency vulnerabilities

## Usage

### Manual Invocation
```
/security-scan
```

### Automatic Triggers
- Before commits (via pre-commit hook)
- On dependency file changes
- Weekly scheduled scans
- Before deployments

## What Gets Scanned

### Dependencies
- `package.json` / `bun.lock` (JavaScript/TypeScript)
- `go.mod` / `go.sum` (Go)
- `requirements.txt` / `pyproject.toml` (Python)
- Docker images and containers

### Secrets
- API keys, tokens, passwords in code
- AWS credentials, private keys
- Database connection strings
- OAuth secrets, webhook URLs

### Vulnerabilities
- CVE database matches
- OWASP Top 10 patterns
- Known malware signatures
- License compliance issues

## Output Format

### Summary
```
🔒 Security Scan Results
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Dependencies: 0 critical, 2 high, 5 medium
⚠️ Secrets: 1 potential match found
✅ Vulnerabilities: 0 critical, 1 high
✅ Licenses: All compliant

Total Issues: 9 (0 critical, 3 high, 5 medium, 1 low)
```

### Detailed Report
- File paths and line numbers for each issue
- CVE identifiers with severity ratings
- Remediation suggestions (upgrade versions, remove secrets)
- Links to security advisories

## Severity Levels

- **CRITICAL** - Immediate action required, blocks deployment
- **HIGH** - Fix within 24 hours
- **MEDIUM** - Fix within 1 week
- **LOW** - Fix when convenient

## Integration

### Pre-Commit Hook
Automatically runs on `git commit`:
```bash
# .claude/hooks/pre-commit-security.sh
trivy fs --severity HIGH,CRITICAL .
gitguardian scan commit --pre-commit
```

### CI/CD Pipeline
```yaml
# .github/workflows/security.yml
- name: Security Scan
  run: |
    trivy fs --severity HIGH,CRITICAL .
    bun audit --audit-level=high
```

## Configuration

### Trivy Settings
```yaml
# .trivy.yaml
severity: CRITICAL,HIGH
ignore-unfixed: true
scanners: vuln,secret,config
```

### GitGuardian Settings
```yaml
# .gitguardian.yaml
api-url: https://api.gitguardian.com
matches-ignore:
  - name: "Test fixtures"
    match: test/fixtures/**
```

## Remediation Workflow

1. **Critical/High Severity:**
   - Creates Linear ticket automatically
   - Sends Slack alert to #security channel
   - Blocks deployment if in CI

2. **Medium Severity:**
   - Adds to security backlog
   - Weekly review in security standup

3. **Low Severity:**
   - Documents in security.md
   - Addresses during maintenance cycles

## Common Issues

### False Positives
Add to ignore list:
```yaml
# .security-ignore.yaml
- path: test/fixtures/test-credentials.json
  reason: Test fixture, not real credentials
```

### Outdated CVE Database
Update Trivy database:
```bash
trivy image --download-db-only
```

## Best Practices

1. **Run before every commit** - Catch issues early
2. **Fix critical/high immediately** - Don't let them accumulate
3. **Review medium weekly** - Prioritize in sprint planning
4. **Update dependencies regularly** - Reduce vulnerability surface
5. **Never commit secrets** - Use environment variables

## Performance

- **Scan Time:** ~30 seconds for full codebase
- **Cache:** Uses cached results for unchanged files
- **Incremental:** Only scans modified files in pre-commit

## Resources

- Trivy Documentation: https://aquasecurity.github.io/trivy/
- GitGuardian: https://www.gitguardian.com/
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- CVE Database: https://cve.mitre.org/
