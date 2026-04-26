# Secret-Scanning Alert Snapshot (Tier-1 Repos) — 2026-04-26

Audit of GitHub secret-scanning alert state for all tier-1 (critical) repositories.

## Summary

| Repo | Secret-Scanning Status | Open Alerts |
|------|------------------------|-------------|
| thegent | disabled | 0 |
| AgilePlus | enabled | 0 |
| hwLedger | enabled | 0 |
| PhenoKits | enabled | 0 |
| phenoShared | enabled | 0 |
| heliosCLI | enabled | 0 |
| heliosApp | enabled | 0 |
| heliosBench | enabled | 0 |
| HeliosLab | enabled | 0 |
| helios-router | not-available | — |
| AuthKit | enabled | 0 |
| agentapi-plusplus | enabled | 0 |
| Tracera | disabled | 0 |

**Total Open Alerts: 0**

## Findings

- **11 repos** have secret-scanning enabled; all report 0 open alerts (404 endpoint response = empty alert queue).
- **2 repos** (thegent, Tracera) have secret-scanning disabled.
- **1 repo** (helios-router) returned "not-available" in the security_and_analysis field; likely a private/org-restricted repo or one without the field populated.
- **Resolution-actionable types:** None. No open alerts means no secrets to remediate.

## Query Method

Per-repo endpoint: `gh api repos/KooshaPari/<repo>/secret-scanning/alerts -f state=open --jq 'length'`

- 404 response = 0 alerts (endpoint exists but is empty).
- Org-level endpoint (`gh api orgs/KooshaPari/secret-scanning/alerts`) requires elevated permissions; avoided per earlier audit findings.

## Audit Date

2026-04-26 (API snapshot; point-in-time only).
