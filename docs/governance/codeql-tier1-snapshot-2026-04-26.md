# CodeQL Tier-1 Snapshot (2026-04-26)

**Date:** 2026-04-26  
**Scope:** KooshaPari tier-1 repositories  
**Status:** CodeQL scanning NOT ENABLED

## Summary

All 11 tier-1 repositories return HTTP 404 on the GitHub CodeQL `/code-scanning/alerts` API endpoint, indicating that **Advanced Security / CodeQL code scanning is not enabled** on any of these repositories.

### Tier-1 Repositories Scanned

| Repo | CodeQL Status | API Response |
|------|---------------|--------------|
| thegent | Disabled | 404 Not Found |
| AgilePlus | Disabled | 404 Not Found |
| hwLedger | Disabled | 404 Not Found |
| PhenoKits | Disabled | 404 Not Found |
| phenoShared | Disabled | 404 Not Found |
| heliosCLI | Disabled | 404 Not Found |
| heliosApp | Disabled | 404 Not Found |
| agentapi-plusplus | Disabled | 404 Not Found |
| AuthKit | Disabled | 404 Not Found |
| Tracera | Disabled | 404 Not Found |
| McpKit | Disabled | 404 Not Found |

## Security Analysis Enablement Status

Per sample query on `thegent`:
```json
{
  "dependabot_security_updates": "enabled",
  "secret_scanning": "disabled",
  "secret_scanning_non_provider_patterns": "disabled",
  "secret_scanning_push_protection": "disabled",
  "secret_scanning_validity_checks": "disabled",
  "code_scanning": "disabled"  // CodeQL
}
```

**Currently Enabled:**
- Dependabot security updates

**Disabled:**
- Secret scanning (GitHub and custom patterns)
- Push protection
- CodeQL code scanning

## Context

Per global instructions (`~/.claude/CLAUDE.md`):
> GitHub Actions billing is a hard constraint. GitHub Actions CI workflows will NOT run on any repo -- jobs fail immediately with a billing error.

The billing/spending-limit constraint on the KooshaPari account likely prevents:
1. CodeQL scanning (paid Advanced Security feature)
2. CI workflow execution

### Workarounds in Place

Per memory (`MEMORY.md`):
- Local CLI tools compensate: **Clippy (Rust)** and **Ruff (Python)** provide SAST-equivalent coverage
- Billing-blocked rulesets restored via manual local scanning tooling
- Security pipeline operates via local static analysis (no GitHub Actions)

## Action Items

1. **No immediate action required** — CodeQL scanning is a paid feature subject to the billing constraint.
2. **Local verification** — Continue using Clippy, Ruff, Semgrep, and other OSS tooling for SAST.
3. **Future enablement** — If billing constraint is lifted, enable CodeQL via org settings and re-scan all tier-1 repos.

## References

- Global Billing Policy: `~/.claude/CLAUDE.md` → GitHub Actions Billing Constraint
- Memory Note: `MEMORY.md` → Billing-blocked rulesets
- Security Pipeline: `docs/governance/security-pipeline-overview.md` (local tooling)
