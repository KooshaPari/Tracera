# Workflow Dedup Candidates — 2026-04-27

API-only inventory of GitHub Actions workflow files across the KooshaPari org. Source: `gh api users/KooshaPari/repos --paginate` (non-archived only) + `gh api repos/<r>/contents/.github/workflows`.

## Scope

- **Active repos scanned:** 82
- **Repos with `.github/workflows/`:** 80
- **Distinct workflow filenames:** 222
- **Total workflow file occurrences:** 855
- **Filenames present in ≥5 repos (reusable candidates):** 37

## Top Duplicated Workflow Names (≥5 repos)

| Rank | Workflow Filename | Repo Count | Reusable Candidate |
|------|-------------------|-----------:|--------------------|
| 1 | `scorecard.yml` | 65 | YES — OSSF Scorecard, identical config across most repos |
| 2 | `ci.yml` | 53 | PARTIAL — language-specific; reusable per stack (Rust/TS/Python) |
| 3 | `quality-gate.yml` | 40 | YES — quality gate is workflow-agnostic |
| 4 | `codeql.yml` | 34 | YES — GitHub-templated, easy to centralize |
| 5 | `release.yml` | 27 | PARTIAL — split by release strategy (cargo-release / semantic-release) |
| 6 | `fr-coverage.yml` | 27 | YES — FR traceability is org-wide governance |
| 7 | `doc-links.yml` | 26 | YES — markdown link checker, identical |
| 8 | `security-guard.yml` | 22 | YES — Phenotype security policy |
| 9 | `secrets-scan.yml` | 22 | YES — gitleaks/trufflehog scan |
| 10 | `alert-sync-issues.yml` | 21 | YES — Dependabot/CodeQL alert sync |

## Tier 2 (10–20 repos)

| Workflow | Count | Notes |
|----------|------:|-------|
| `legacy-tooling-gate.yml` | 17 | Phenotype legacy tooling gate |
| `security-guard-hook-audit.yml` | 16 | Hook audit, identical |
| `policy-gate.yml` | 16 | Org policy enforcement |
| `coverage.yml` | 16 | Coverage upload (codecov/coveralls) |
| `release-drafter.yml` | 15 | release-drafter config |
| `pages-deploy.yml` | 12 | GitHub Pages deploy |
| `sast.yml` | 11 | SAST (semgrep) |
| `tag-automation.yml` | 10 | Tag-on-merge automation |
| `self-merge-gate.yml` | 10 | Self-merge guard |

## Tier 3 (5–9 repos)

`security.yml` (9), `security-deep-scan.yml` (9), `sbom-refresh.yml` (7), `sast-quick.yml` (7), `sast-full.yml` (7), `publish.yml` (7), `docs.yml` (7), `zap-dast.yml` (6), `trivy-scan.yml` (6), `sonarcloud.yml` (6), `license-compliance.yml` (6), `iac-scan.yml` (6), `fuzzing.yml` (6), `deploy.yml` (6), `workflow-permissions.yml` (5), `snyk-scan.yml` (5), `docs-deploy.yml` (5), `benchmark.yml` (5).

## Recommended Reusable-Workflow Extraction Targets (Phase 1)

Highest-yield, lowest-risk consolidations into a central `KooshaPari/.github` reusable-workflow repo:

1. **`scorecard.yml`** (65×) — single source of truth, callers shrink to ~10 lines
2. **`codeql.yml`** (34×) — language-matrix in caller, logic centralized
3. **`fr-coverage.yml`** (27×) — Phenotype FR-traceability gate
4. **`doc-links.yml`** (26×) — lychee link checker
5. **`secrets-scan.yml`** (22×) — gitleaks/trufflehog
6. **`security-guard.yml`** (22×) — Phenotype security policy
7. **`alert-sync-issues.yml`** (21×) — alert→issue sync
8. **`policy-gate.yml`** (16×) — org policy gate
9. **`security-guard-hook-audit.yml`** (16×) — hook audit
10. **`release-drafter.yml`** (15×) — drafter config

**Estimated savings:** ~280 redundant workflow files reducible to ~10 reusable workflows + thin caller stubs. Net: ~85% YAML reduction across these 10 names.

## Method

```bash
gh api users/KooshaPari/repos --paginate -q '.[] | select(.archived==false) | .name' > active_repos.txt
while read r; do
  gh api "repos/KooshaPari/$r/contents/.github/workflows" --jq '.[].name' 2>/dev/null \
    | while read w; do echo "$w|$r"; done
done < active_repos.txt > all.txt
awk -F'|' '{print $1}' all.txt | sort | uniq -c | sort -rn
```

Raw data: `/tmp/wf_inv/all.txt` (855 rows), `/tmp/wf_inv/dup_candidates.txt` (37 names ≥5 repos).
