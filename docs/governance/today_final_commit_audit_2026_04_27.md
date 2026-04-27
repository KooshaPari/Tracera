# 2026-04-26 Final Commit & Push Audit

**Date:** 2026-04-26 (audited 2026-04-27)  
**Working Directory:** `/repos/`  
**Methodology:** `git log --since="2026-04-26 00:00:00"` across all real git repositories (excluded: `.archive/`, `-wtrees/`, inherited subdir repos, Tracera subdirs)

## Executive Summary

| Metric | Count |
|--------|-------|
| **Repos with commits today** | 56 |
| **Repos pushed to remote** | 50 |
| **Repos with local-only commits** | 6 |
| **Total local commits** | 351 |
| **Total remote commits (pushed)** | 289 |
| **Still unpushed** | 62 |

## Repos Pushed Today (Top 15)

| Repo | Local Commits | Remote Commits | Status |
|------|---------------|-----------------|--------|
| cliproxyapi-plusplus | 31 | 31 | ✓ Fully pushed |
| phenoShared | 26 | 16 | ⚠ 10 unpushed |
| AgilePlus | 25 | 14 | ⚠ 11 unpushed |
| FocalPoint | 22 | 22 | ✓ Fully pushed |
| agent-user-status | 22 | 2 | ⚠ 20 unpushed |
| PhenoObservability | 21 | 19 | ⚠ 2 unpushed |
| Tracera-recovered | 18 | 18 | ✓ Fully pushed |
| PhenoMCP | 17 | 17 | ✓ Fully pushed |
| pheno | 17 | 14 | ⚠ 3 unpushed |
| PhenoProc | 12 | 11 | ⚠ 1 unpushed |
| heliosCLI | 12 | 12 | ✓ Fully pushed |
| BytePort | 12 | 11 | ⚠ 1 unpushed |
| PhenoHandbook | 11 | 11 | ✓ Fully pushed |
| KDesktopVirt | 11 | 9 | ⚠ 2 unpushed |
| thegent | 7 | 5 | ⚠ 2 unpushed |

## Repos with Local-Only Commits (Not Pushed)

| Repo | Commits | Notes |
|------|---------|-------|
| AgentMCP | 1 | — |
| argis-extensions | 1 | — |
| AtomsBot | 1 | — |
| chatta | 1 | — |
| GDK | 2 | — |
| helios-cli | 1 | — |

**Total unpushed in local-only repos:** 7 commits

## Analysis

- **Fully pushed (0 unpushed):** 35 repos
- **Partially pushed (1+ unpushed):** 15 repos
- **Never pushed:** 6 repos

**Largest unpushed gaps:**
1. agent-user-status: 20 unpushed
2. AgilePlus: 11 unpushed
3. phenoShared: 10 unpushed

**Top 5 volume contributors:**
1. cliproxyapi-plusplus (31 commits, all pushed)
2. phenoShared (26 commits, 16 pushed)
3. AgilePlus (25 commits, 14 pushed)
4. FocalPoint (22 commits, all pushed)
5. agent-user-status (22 commits, 2 pushed)

## Notes

- **Tracera submodules** (phench, artifacts) excluded as they inherit Tracera's remote
- **Worktree directories** (`.worktrees/` + `-wtrees/` subdirs) excluded
- **Archived repos** (`.archive/`) excluded
- **Canonical monorepo root** (worklogs, ValidationKit, src, etc.) excluded (inherited from Tracera root)

**Previous audit (earlier today):** 49 repos pushed  
**This audit:** 50 repos pushed (1 additional: likely a late push or previous rebase merge)
