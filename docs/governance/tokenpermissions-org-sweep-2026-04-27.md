# TokenPermissions / DangerousWorkflow Org Sweep

**Date:** 2026-04-27
**Scope:** Top 30 active KooshaPari repos by `pushed_at` (archived excluded)
**Method:** API-only — `gh api repos/<r>/code-scanning/alerts?state=open` filtered on `rule.id ~= /TokenPermissions|DangerousWorkflow/i`
**Time-bound:** 10s/repo cap, no clones

## Results (sorted desc)

| Rank | Repo | Alerts |
|------|------|--------|
| 1 | heliosApp | 17 |
| 2 | FocalPoint | 16 |
| 3 | nanovms | 11 |
| 4 | phenodocs | 10 |
| 5 | hwLedger | 8 |
| 6 | phenoDesign | 6 |
| 7 | PhenoProject | 5 |
| 7 | Httpora | 5 |
| 7 | DevHex | 5 |
| 10 | phenoAI | 4 |
| 11 | phenoUtils | 2 |
| 11 | phenotype-ops-mcp | 2 |
| 11 | phenotype-auth-ts | 2 |
| 11 | cliproxyapi-plusplus | 2 |
| 15 | phenotype-omlx | 1 |
| 15 | phenoShared | 1 |

**Zero alerts (10):** PhenoProc, PhenoLang, pheno, McpKit, HeliosLab, heliosCLI, BytePort, AuthKit, AgilePlus, agent-devops-setups

**No code-scanning analysis (4, 404):** phenokits-landing, hwledger-landing, helios-cli, byteport-landing — landing/static repos likely without CodeQL Actions scan; enable workflow scanning to surface alerts.

## Recommended Next Batch (excluding already-PR'd)

Already-PR'd: heliosApp (17), cliproxyapi-plusplus (2)

Next batch by impact:

1. **FocalPoint (16)** — highest unaddressed
2. **nanovms (11)**
3. **phenodocs (10)**
4. **hwLedger (8)**
5. **phenoDesign (6)**
6. **PhenoProject / Httpora / DevHex (5 each)** — group as wave
7. **phenoAI (4)**

Total remediable surface in top-7 batch: **64 alerts** across 7 repos. After heliosApp+cliproxyapi-plusplus close, these account for the majority of org-wide TokenPermissions/DangerousWorkflow exposure.

## Suggested Remediation Pattern

Apply `permissions: { contents: read }` (or minimal scope) at workflow-top in each `.github/workflows/*.yml`; for `DangerousWorkflow`, audit `pull_request_target` + checkout-of-PR-head pairs and gate with `if: github.event.pull_request.head.repo.full_name == github.repository` or use `pull_request` instead.
