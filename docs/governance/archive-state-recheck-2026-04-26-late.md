# Archive State Recheck — 2026-04-26 (late)

Source: `gh api users/KooshaPari/repos --paginate` (132 repos). Memory baseline:
`reference_archived_repos_locked.md` (12 entries).

## Memory list verification (12 entries)

All 11 archived entries still `archived=true` on GitHub:

KaskMan, Settly, KodeVibeGo, worktree-manager, phenoXddLib, phenotype-infrakit,
KVirtualStage, kmobile, Logify, Authvault, localbase3.

Pyron → HTTP 404 (deleted, matches memory).

No un-archives detected. No 404s beyond Pyron.

## New archives not in memory (37)

acp, agentapi, agslag-docs, AppGen, argisexec, ccusage, chatta, Eventra,
Frostify, KlipDot, KodeVibe, KommandLineAutomation, kwality, KWatch, odin-calc,
odin-dash, odin-etchasketch, odin-landing, odin-library, odin-recipes, odin-res,
odin-restaurant, odin-Signup, odin-todo, odin-TTT, odin-weather, pheno-sdk,
phenoForge, phenoRouterMonitor, phenotype-dep-guard, PriceyApp, Project-Spyn,
Quillr, RIP-Fitness-App, slickport, Synthia, tehgent, vibe-kanban, Zerokit.

Notable cluster archived 2026-04-26 (today): Authvault, phenoForge,
phenotype-dep-guard, Quillr, Settly, worktree-manager (memory-aligned plus
newly-archived).

## Dormant non-archived (>6mo, pushed before 2025-10-26)

Only `TripleM` (2024-08-19). Candidate for archive review.

## Recommended memory updates

1. Expand `reference_archived_repos_locked.md` from 12 → 48 entries (47 archived
   + Pyron deleted).
2. Add explicit "verified 2026-04-26" timestamp; freshness window <1 week.
3. Flag TripleM for triage (archive or revive).
4. Add the 13 odin-* + 3 odin family as a sub-cluster (legacy coursework).
