# Workflow Permissions Re-Verify — 2026-04-27

API-only re-verification of workflow `permissions:` posture across non-archived
KooshaPari repos (re: task #218). Methodology: GitHub Contents API; for each
`.github/workflows/*.{yml,yaml}` file, base64-decode and check for a top-level
`permissions:` block (regex `^permissions:`). No local clones.

## Aggregate

| Metric | Value |
|---|---|
| Repos scanned (non-archived, sources) | 91 |
| Repos with workflows | 89 |
| Workflows scanned | 813 |
| EXPLICIT (top-level `permissions:`) | 366 (45.0%) |
| IMPLICIT (default token) | 447 (55.0%) |
| Repos with >50% IMPLICIT | 57 |

**Drift verdict:** Significant. Majority of workflows still rely on the default
`GITHUB_TOKEN` permissions. Task #218 closure premise (org-wide explicit
posture) does not hold under API re-verify.

## Top-10 Offenders (by IMPLICIT %, min 3 workflows)

| Repo | Workflows | IMPLICIT | % |
|---|---:|---:|---:|
| PhenoDevOps | 6 | 6 | 100.0 |
| PhenoPlugins | 5 | 5 | 100.0 |
| AuthKit | 5 | 5 | 100.0 |
| PlayCua | 4 | 4 | 100.0 |
| PhenoObservability | 9 | 8 | 88.9 |
| BytePort | 7 | 6 | 85.7 |
| Tracely | 6 | 5 | 83.3 |
| ObservabilityKit | 6 | 5 | 83.3 |
| dinoforge-packs | 6 | 5 | 83.3 |
| Sidekick | 5 | 4 | 80.0 |

## Largest Absolute IMPLICIT Counts (volume risk)

HexaKit (29), pheno (28), PhenoLang (28), heliosCLI (28), Tracera (25),
Tokn (17), thegent (13), Stashly (10), PolicyStack (10), Civis (10).

## Recommendations

1. Add a top-level `permissions: {}` (least-privilege baseline) to every
   workflow in the 10 fully-implicit repos first; expand explicit grants per
   job as needed.
2. Treat task #218 as **partially regressed**; re-open with target = 90%
   EXPLICIT org-wide.
3. Add a CI lint (e.g., `actionlint` + custom rule, or `zizmor`) at the
   `phenotype-shared` reusable-workflow layer to fail PRs introducing
   workflows without a top-level `permissions:` block.
4. Bulk-PR campaign: high-volume repos (HexaKit, pheno, PhenoLang, heliosCLI,
   Tracera) account for 138/447 = 30.9% of all IMPLICIT workflows — fix these
   first for max coverage gain.

## Artifacts

- Raw scan: `/tmp/wfperm/scan.tsv` (repo, workflow, posture)
- Per-repo: `/tmp/wfperm/per-repo.tsv`
