# SBOM Tracking Policy (2026-04-27)

## Decision

**TRACK** all CycloneDX SBOM artifacts (`sbom/*.cdx.json`, `sbom/*.json`) in
git. SBOMs are security audit deliverables and dependency-state evidence at
commit time, not ephemeral build artifacts.

## Rationale

- Phenotype-org governance treats SBOMs as a security/compliance deliverable
  (5-layer security pipeline, supply-chain audit, OSV-Scanner inputs).
- Locking SBOMs in commits proves the dependency graph at release time, which
  is required for CVE retro-attribution and reproducible audits.
- Cost is trivial: 1–60 small JSON files per repo, churn only on dep changes.
- Aligns with regulated-industry default (CycloneDX recommends VCS tracking).

## Per-Repo State (verified 2026-04-27)

| Workspace      | SBOM count | Tracked | Untracked drift | Gitignore conflict |
|----------------|-----------:|---------|-----------------|--------------------|
| FocalPoint     | 61         | 61      | 0               | none               |
| hwLedger       | 37         | 37      | 0               | none               |
| heliosCLI      | 10         | 10      | 0               | none               |
| HeliosLab      | 6          | 6       | 0               | none               |
| Configra       | 6          | 6       | 0               | none               |
| KDesktopVirt   | 1          | 1       | 0               | none               |
| pheno          | 11         | 11      | 0               | none               |
| **Total**      | **132**    | **132** | **0**           | **0 conflicts**    |

All 132 round-2 bootstrap SBOMs are committed and clean. Earlier reports of
"60+ untracked .cdx.json in FocalPoint" were stale (pre-commit snapshot).

## .gitignore Hygiene

- No workspace currently ignores `sbom/`.
- If a future `.gitignore` adds a broad `*.json` or `sbom/` rule, it MUST be
  paired with `!sbom/*.cdx.json` and `!sbom/*.json` to preserve tracking.

## Regeneration Cadence

- Regenerate when `Cargo.lock` / `go.sum` / `pnpm-lock.yaml` changes.
- Regenerate weekly via `disk-budget-weekly.yml` companion job (proposed).
- Diff-only commits — do not re-commit unchanged SBOMs.
- Generation script lives in each workspace's `scripts/sbom/` (or root tooling
  for monorepos like FocalPoint and pheno).

## Future Work

- Wire SBOM regen into CI for PRs that touch lockfiles (advisory).
- Add `osv-scanner --sbom` to security pipeline layer 5 using these tracked
  artifacts as input.
- Extend tracking to remaining workspaces (Tokn, AgilePlus, PhenoMCP, etc.) as
  they bootstrap CycloneDX in subsequent rounds.

## References

- CycloneDX 1.3 spec: https://cyclonedx.org/specification/overview/
- Phenotype governance: `~/.claude/CLAUDE.md` § Security Pipeline (Layer 5)
- Round-1 bootstrap: `worklogs/GOVERNANCE.md` (sbom-bootstrap-round-1)
- Round-2 bootstrap: 132 SBOMs across 7 workspaces, 2026-04-26
