# Helios Family v2026.05.0 Release — 2026-04-25

**Family Marker Release** coordinating CalVer + SemVer across 6 repos.

## Release Status

| Repo | Previous | Current | Status | Notes |
|------|----------|---------|--------|-------|
| heliosApp | v2026.04A.4 | **v2026.05A.0** | RELEASED | 23 commits: FR tracing, lint hardening, CI gates |
| heliosCLI | v0.2.0 | **v0.2.1** | RELEASED (Apr 25) | PyO3 arm64 dynamic_lookup fix (W29) |
| helios-cli | v0.2.0 | **—** | HELD | Doc-only changes (1 commit), no feature bump |
| helios-router | v0.2.0 | **—** | HELD | Zero commits since v0.2.0 |
| heliosBench | v0.2.0 | **—** | HELD | Doc-only changes (2 commits), +50% README |
| HeliosLab | v0.1.1 | **—** | HELD | Zero commits since v0.1.1 |

## Highlights

### heliosApp v2026.05A.0
- **FR Coverage**: 174/283 FRs traced (61.5%)
- **Quality**: Lint warnings 161 → 0 (100% resolution)
- **CI**: Strict gate enforcement with zero-baseline
- **Tests**: 12 new FR traceability annotations + infrastructure cleanup
- **Governance**: Full phenotype-tooling workflows integration (wave-3)

### heliosCLI v0.2.1 (Previously Released)
- PyO3 arm64 dynamic_lookup compilation fix
- Rust 1.94.1 + Node 25 dependency updates
- Worklog scaffolding (org-wide governance gap closure)

## Coordination Notes

- **Doc-only repos held**: helios-cli, heliosBench, HeliosLab (no feature content; marked for next wave if README improvements warrant minor bump)
- **Zero-change repos held**: helios-router (defer to v2026.05A or next family cycle)
- **CalVer migration**: heliosApp CalVer (v2026.05A.0) while CLI ecosystem remains SemVer (v0.2.x)
- **Family marker**: This release coordinates dual-version strategy; not all repos bump

## Deployment

```bash
# Tag each held repo with marker (no bump):
git tag v2026.05-marker-held helios-cli
git tag v2026.05-marker-held helios-router
git tag v2026.05-marker-held heliosBench
git tag v2026.05-marker-held HeliosLab

# Verify released tags:
git ls-remote --tags origin | grep v2026.05A.0
git ls-remote --tags origin | grep v0.2.1
```

## Next Steps

1. **Wave-2 candidate**: Review README improvements in helios-cli + heliosBench for potential minor bumps
2. **helios-router**: Defer until substantive work lands (feature, API change, refactor)
3. **HeliosLab**: Monitor for post-0.1.1 work; next release when feature-ready
4. **Family release notes**: Update GitHub releases for v2026.05.0 marker event

---

**Release Coordinator**: Claude Code  
**Date**: 2026-04-25  
**Budget**: 35 min (24 min used)
