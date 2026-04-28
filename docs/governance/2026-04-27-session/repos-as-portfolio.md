# Repos-as-Product-Portfolio (proposed framework)
**Date:** 2026-04-27

## Premise
70+ repo orgs accumulate cruft; treating each repo as an isolated codebase misses portfolio-level decisions.

## Tier definitions

### Tier 1: Active products (~10 repos)
- Daily commits, active issues/PRs
- Full hygiene gates: SECURITY, LICENSE, CHANGELOG, CODEOWNERS, CONTRIBUTING
- Full security: Dependabot, CodeQL, branch protection, ruleset
- Full docs: README, INSTALL, USAGE, ARCHITECTURE, CHANGELOG
- Full CI: test, lint, build, release
- Examples: AgilePlus, thegent, hwLedger, helios family

### Tier 2: Maintained libs (~20 repos)
- Weekly+ activity
- Standard hygiene + security + Dependabot
- Cargo.lock committed if binary; not if pure lib
- Examples: phenoShared, McpKit, DataKit, AuthKit, ResilienceKit

### Tier 3: Experimental / archived-soon (~30 repos)
- Sporadic activity
- Minimum hygiene: LICENSE + README + Dependabot enabled
- No required CI, no required reviews
- Auto-archive trigger: 365 days no commits
- Examples: PhenoLang, KDesktopVirt, Conft, GDK

### Tier 4: Archived (~10 repos)
- Read-only on GitHub
- Documentation references retained
- Examples: heliosCLI (was active, now archived), AtomsBot, chatta

## Assignment criteria
| Tier | Last commit | Open PRs | Has README | Required hygiene |
|------|---|---|---|---|
| 1 | <7d | 1+ | full | full |
| 2 | <30d | optional | yes | standard |
| 3 | <365d | 0 | minimum | minimum |
| 4 | >365d | n/a | reference | none (archived) |

## Migration paths
- Tier 1→2: feature-complete, transitions to lib-style maintenance
- Tier 2→3: maintenance burden exceeds value, signal owners
- Tier 3→4: 365 days idle + no objection from owners
- Tier 4→1: reactivation requires explicit owner re-commit + new SECURITY policy

## Org-wide signals to watch
- New repos: assign tier on creation
- Tier-down candidates: scan monthly
- Tier-up candidates: triggered by sustained activity
- Tier 4 cleanup: yearly, archive bulk-action

## How this session influences tiering
- HexaKit residuals: Tier 1 (active, but residuals need attention)
- pheno: Tier 2 (active maintenance, broken submodule)
- PhenoLang: Tier 3 → Tier 2 (recently active again)
- QuadSGM: Tier 1 (CRIT advisories cleared)
- Tracera: Tier 1 (15 alerts cleared this session)
- byteport: Tier 2 (lockfile clean, residual minor)
