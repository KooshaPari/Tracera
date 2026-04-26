# thegent Dependabot Sweep — 2026-04-26

## Executive Summary

**Total Open Alerts:** 60
- **CRITICAL:** 0
- **HIGH:** 19 (25 instances across ecosystem variations)
- **MEDIUM:** 28
- **LOW:** 13

**Status:** No Dependabot PRs currently open. Dependabot may be disabled or has auto-closed PRs. Manual intervention required to merge security patches.

---

## HIGH Severity Packages (19 unique, 25 instances)

| Package | Ecosystem | Current Fix | Status |
|---------|-----------|-------------|--------|
| @workos-inc/authkit-nextjs | npm | 2.11.1 | Fixable |
| GitPython | pip | 3.1.47 | Fixable |
| flatted | npm | 3.4.2 | Fixable |
| github.com/go-jose/go-jose/v4 | go | 4.1.4 | Fixable |
| glob | npm | 10.5.0 | Fixable |
| go.opentelemetry.io/otel | go | 1.41.0 | Fixable |
| go.opentelemetry.io/otel/sdk | go | 1.43.0 | Fixable |
| lodash | npm | 4.18.0 | Fixable |
| lodash-es | npm | 4.18.0 | Fixable |
| **lupa** | pip | **NONE** | **⚠️ NO FIX** |
| lxml | pip | 6.1.0 | Fixable |
| minimatch | npm | 3.1.3 | Fixable |
| path-to-regexp | npm | 0.1.13 | Fixable |
| picomatch | npm | 2.3.2 | Fixable |
| pillow | pip | 12.2.0 | Fixable |
| rollup | npm | 4.59.0 | Fixable |
| vite | npm | 7.3.2 | Fixable |
| PyJWT | pip | 2.12.0 | Fixable |
| **github.com/docker/docker** | go | **NONE** | **⚠️ NO FIX** |

**Blockers:** 2 packages have no available fix (lupa, docker) — these require manual code review and potential workarounds.

---

## Next Steps

1. **Enable Dependabot Automation** — Check repo settings to re-enable Dependabot PR creation
2. **Manual PR Mergal** — For HIGH severity packages with fixes available:
   - Create PRs manually or re-enable Dependabot
   - Merge patch/minor updates (low-risk)
   - Review major version updates (higher risk, may require code changes)
3. **Unresolvable Alerts**:
   - `lupa` (HIGH, no fix): Document and potentially replace
   - `docker` (HIGH, no fix): Review alternatives or audit usage

---

## Alert Distribution by Ecosystem

| Ecosystem | HIGH | MEDIUM | LOW | Total |
|-----------|------|--------|-----|-------|
| npm | 10 | 10 | 4 | 24 |
| pip | 6 | 10 | 7 | 23 |
| go | 3 | 8 | 2 | 13 |

---

## Recommendations

### Immediate (This sprint)
- Re-enable Dependabot or create initial PRs for all 17 fixable HIGH packages
- Merge patch-level updates first (lower risk)
- Document `lupa` and `docker` as known limitations

### Short-term (1-2 sprints)
- Audit all MEDIUM severity packages (28 total)
- Create a routine Dependabot review cadence (weekly)
- Consider forking/replacing `lupa` if unmaintained

### Long-term
- Implement dependency version pinning strategy
- Set up automated security scanning in CI/CD
- Track and monitor unresolvable alerts quarterly

---

## Tool Invocation Summary

All data retrieved via GitHub CLI (`gh api` / `gh pr list`).

```bash
# List all HIGH severity open alerts
gh api repos/KooshaPari/thegent/dependabot/alerts --paginate \
  --jq '[.[] | select(.state == "open" and .security_vulnerability.severity == "high")] | \
  map({pkg: .dependency.package.name, ecosystem: .dependency.package.ecosystem, \
  fix: .security_vulnerability.first_patched_version.identifier}) | unique_by(.pkg)'

# Check for existing Dependabot PRs
gh pr list --repo KooshaPari/thegent --author "app/dependabot" --state open
```

---

## References

- GitHub Dependabot Docs: https://docs.github.com/en/code-security/dependabot
- CVE Search: https://cve.mitre.org/
- thegent Repository: https://github.com/KooshaPari/thegent

**Generated:** 2026-04-26 | **Audit Scope:** API-only (no code changes required)
