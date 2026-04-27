# AgilePlus Unpushed Commits Audit — 2026-04-27

## Summary

- **Total unpushed commits**: 15 across 3 worktrees
- **Squash-merge ghosts**: 2 (already in canonical via squash-merge)
- **Genuine unmerged work**: 13 split across 2 active branches

## Per-Commit Classification

### p1-test-fixes (2 commits — BOTH GHOSTS)

| SHA | Status | Reason |
|-----|--------|--------|
| `e076ad3` | GHOST | Already merged as `282a8d5` (canonical) via PR #413 |
| `a59c681` | GHOST | Already merged as `a59c681` (canonical) via PR #410 |

**Action**: These branches are stale and can be discarded or archived. Both specs (013 and readme) are already live on main.

### release-cut-adopt (10 commits — REAL WORK)

| SHA | Title | Status |
|-----|-------|--------|
| `89ea259` | feat(release): adopt phenotype-tooling release-cut workflow | **UNMERGED** |
| `ab03a59` | chore(security): document deferred RUSTSEC advisories | **UNMERGED** |
| `11d26eb` | chore(security): adopt cargo-deny + supply chain baseline | **UNMERGED** |
| `40e6b74` | perf(bench): baseline metrics for event sourcing and API paths | **UNMERGED** |
| `f1c5a73` | docs(dashboard): live deployment verification 2026-04-24 | **UNMERGED** |
| `3de9de0` | chore(deps): align tokio + serde to org baseline | **UNMERGED** |
| `fa09b95` | feat(agent): WP08 — real agent adapter (stub→shipped) | **UNMERGED** |
| `a6cc91e` | chore(ci): adopt phenotype-tooling workflows (wave-3) | **UNMERGED** |
| `49a4de6` | chore(deps): align rusqlite to v0.33 per org baseline | **UNMERGED** |
| `d029007` | fix(workspace): unblock parking_lot_core resolution | **UNMERGED** |

**Scope**: Cross-cutting improvements (release workflow, security baseline, deps alignment, CI modernization, WP08 agent adapter).

### security-alerts-20260426 (3 commits — REAL WORK)

| SHA | Title | Status |
|-----|-------|--------|
| `b4b1a81` | ci(policy): fail closed on unreachable PR head | **UNMERGED** |
| `d9c0eff` | ci(snyk): use token auth in automation | **UNMERGED** |
| `50f63e8` | fix(deps): clear AgilePlus security advisories | **UNMERGED** |

**Scope**: CI robustness and security advisory resolution.

## Recommended Actions

1. **p1-test-fixes (2 ghosts)**
   - Archive or delete; content already shipped on main
   - Alternatively, rebase to current main and verify no additional changes

2. **release-cut-adopt (10 real)**
   - Status: Ready for review and merge or hold pending decision on WP08 agent adapter
   - Dependency: Check if WP08 adapter is feature-gated or blocks other work
   - Recommended: Create PR to surface these; discuss WP08 scope with team

3. **security-alerts-20260426 (3 real)**
   - Status: Ready to merge
   - Recommended: Create PR immediately for security-critical fixes

## Pattern Notes

**Squash-merge ghosts** (AgilePlus canonical pattern):
- Both p1-test-fixes commits were squash-merged into main, losing the original SHAs
- Canonical main shows the merged content but different SHAs (natural for squash)
- This explains why `git log @{u}..HEAD` still shows them—the worktree branch predates the squash-merge

**Why the discrepancy?**
The audit memo reported "11 unpushed", but the actual count is 15. The original count likely:
- Excludes one or more stale worktrees (checked earlier in the day)
- Counts only worktrees modified since snapshot time
- Or uses a different git filter

Real actionable count: **13 unmerged commits** needing review; **2 stale ghosts** for cleanup.
