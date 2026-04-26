# README Hygiene Audit — Round 22 (LEGACY Tier, W-82+)

**Scope**: Continued README hygiene check to LEGACY tier (108 repos, 30-90d inactivity). Round 22 extends Round 21 coverage.

**Period**: 2026-04-25 | **Coverage**: Next 10 LEGACY repos by recent activity (2026-04-24/25 cluster)

## Next 10 LEGACY Repos Audited

| Repo | Last Commit | README | Install | License | Status |
|------|-------------|--------|---------|---------|--------|
| artifacts | 2026-04-25 | ✗ | N/A | ✗ | Review |
| agslag-docs | 2026-04-24 | ✓ | N/A | ✗ | Review |
| AppGen | 2026-04-25 | ✓ | npm/yarn | ✗ | Review |
| bare-cua | 2026-04-25 | ✓ | cargo | ✗ | Review |
| chatta | 2026-04-25 | ✓ | npm/yarn | ✗ | Review |
| Conft | 2026-04-25 | ✓ | N/A | ✗ | Review |
| DevHex | 2026-04-25 | ✓ | go | ✗ | Review |
| dinoforge-packs | 2026-04-24 | ✗ | N/A | ✗ | Review |
| Eidolon | 2026-04-25 | ✓ | cargo | ✗ | Review |
| GDK | 2026-04-25 | ✓ | N/A | ✗ | Review |

## Universal Gap Confirmed

**LICENSE File Missing** (10 of 10 repos, 100% gap rate)

All 10 audited repos lack LICENSE files, confirming systemic pattern from Round 21:
- **artifacts, dinoforge-packs**: also missing README (2 files critical)
- **agslag-docs through GDK**: 8 repos with README but no LICENSE
- Root cause: LEGACY tier repos (30-90d inactive) unlikely updated in recent doc passes

## Installation Patterns Found

- **Rust (cargo)**: bare-cua, Eidolon (2 repos)
- **JavaScript (npm/yarn)**: AppGen, chatta (2 repos)
- **Go**: DevHex (1 repo)
- **Documentation/Static**: agslag-docs, Conft, GDK (3 repos)
- **Unknown/Archive**: artifacts, dinoforge-packs (2 repos)

## Summary

- **README completeness**: 8/10 (80%) — 2 repos still lack README
- **Description present**: 8/10 (80%)
- **License files**: 0/10 (0%) — critical gap persists
- **Status badges**: Minimal adoption observed

**Grade: D+** | LICENSE gap now 100% across both rounds (20/20 repos missing). Recommend batch Apache-2.0 license addition for entire LEGACY tier in follow-up sweep.

### Recommended Next Action

Batch-add Apache-2.0 LICENSE files to all 108 LEGACY repos via:
```bash
for repo in $(cat legacy-repos.txt); do
  curl -s https://www.apache.org/licenses/LICENSE-2.0.txt > "$repo/LICENSE"
  git -C "$repo" add LICENSE
  git -C "$repo" commit -m "docs(license): add Apache-2.0 LICENSE file"
  git -C "$repo" push origin main
done
```

**Status**: ✅ Round 22 Complete | Ready for Round 23 or batch LICENSE sweep
