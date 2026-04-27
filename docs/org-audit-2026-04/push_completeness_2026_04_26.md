# Push Completeness Audit — Round-6 (2026-04-26)

## Summary

KDesktopVirt ratatui bumps (09bff3b, 749df82) successfully pushed to `origin/main` (e2d649f..749df82).

Round-6 swept all repos with commits authored today and ahead of `@{u}`. Verified: 13 of 13 originally-listed active repos have their target commits on origin (plus secondary push-wave below).

## Round-6 Pushes Completed

| Repo | Branch | Range |
|------|--------|-------|
| KDesktopVirt | main | e2d649f..749df82 (ratatui 0.28→0.30) |
| agent-user-status | user-status-next-dag-hardening | 872c5ad..2cec730 |
| cliproxyapi-plusplus | main | 67fae60d..30f1023f (30 commits) |
| heliosApp | main | c22a871..6a09887 |
| McpKit | chore/gitignore-worktrees-2026-04-26 | 96d6a3d..8d41acb |
| Paginary | main | 8d89ac3..f58a036 |

## Verified Pushed (no action needed)

FocalPoint, pheno, PhenoMCP, HeliosLab, Configra, Sidekick, Eidolon, Tracely, hwLedger, PhenoProc, heliosCLI (`fix/deps-handlebars-critical-2026-04-26`).

## Unpushed — Round-7 Targets

### Non-FF (require rebase, dirty trees blocking auto-rebase)

| Repo | Branch | Ahead | Behind | Dirty | Reason |
|------|--------|-------|--------|-------|--------|
| BytePort | main | 3 | 10 | 6 untracked (Cargo.lock, etc.) | Untracked Cargo.lock blocks `git rebase` checkout. Defer until tracked or moved aside. |
| helios-cli | main | 7 | 11 | 2 (CHANGELOG.md, Cargo.toml) | Known HELD per round-3 report. Tracked dirty files block rebase. |
| AgilePlus | main | 1 | 4 | 46 | Heavily dirty; needs commit discipline split before push. |
| argis-extensions | main | 24 | 11 | 0 | Long divergence; needs careful rebase. |
| GDK | main | 6 | 8 | 0 | Non-FF, clean tree — round-7 candidate. |

### FF but Stale @{u} (need fetch+verify)

`@{u}..HEAD` reported ahead with no behind, but push was rejected — origin had moved between fetches:

- Civis (main, ahead=11)
- DevHex (main, ahead=5)
- Httpora (main, ahead=4)
- nanovms (docs, ahead=4)

Round-7: `git fetch && git push` fresh — likely FF after fresh fetch.

### Heavy Worktree-Embedded Repos (defer)

- artifacts (`chore/gitignore-worktrees-2026-04-26`, ahead=32, dirty=157)
- phench (same branch, ahead=32, dirty=157)

These accumulated via worktree gitignore work; review whether commits should move.

### Archived (cannot push — read-only)

- AtomsBot (main, ahead=11) — repo archived on GitHub
- chatta (main, ahead=17) — repo archived on GitHub

Local commits will never reach origin. Archive locally or delete branches.

### Branches with no upstream

- Tracera-recovered (`fix/main-workflow-syntax`) — recovery branch, no upstream-tracking. Defer to recovery workflow.

## Recommended Round-7

1. Fresh `git fetch` + retry FF push: Civis, DevHex, Httpora, nanovms.
2. Clean rebase on GDK (clean tree, modest divergence).
3. Triage AtomsBot/chatta archived state — decide whether to unarchive or drop local commits.
4. Resolve BytePort untracked Cargo.lock (move aside, rebase, push).
5. Investigate Tracera-recovered upstream linkage.
