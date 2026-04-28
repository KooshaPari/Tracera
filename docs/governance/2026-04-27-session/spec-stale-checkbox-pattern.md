# AgilePlus spec stale-checkbox pattern (2026-04-27)

## Pattern

AgilePlus specs (013, 021) contain checkboxes that **reference PRs/branches/work items already done**, but were never ticked off when the work landed. The 56-checkbox count in spec 013 and 186-checkbox count in spec 021 are dramatically inflated by this pattern.

## Evidence

### Spec 013 WP-000 (verified 2026-04-27)
- T000-2: "drain PRs #544-#563" → 13 MERGED + 3 CLOSED + 3 not-found (effectively done)
- T000-3: cache-adapter-impl → branch doesn't exist (renamed)
- T000-4: phenotype-crypto-complete-v2 → branch doesn't exist (cleaned up)

### Spec 021 P1.1 lines 1-15 (verified 2026-04-27)
Top 10 incomplete checkboxes are literally:
- Line 6, P1.1: PR #544 — review and merge ← DONE
- Line 7, P1.1: PR #553 — review and merge ← DONE
- Line 8, P1.1: PR #554 — review and merge ← DONE
- Line 9, P1.1: PR #557 — review and merge ← DONE
- Line 10, P1.1: PR #558 — review and merge ← DONE
- Line 11, P1.1: PR #559 — review and merge ← DONE
- Line 12, P1.1: PR #560 — review and merge ← DONE (docs-only)
- Line 13, P1.1: PR #561 — review and merge ← DONE
- Line 14, P1.1: PR #562 — review and merge ← DONE
- Line 15, P1.1: PR #563 — review and merge ← DONE

Verified earlier this session: PRs #544-#563 = 13 MERGED + 3 CLOSED + 3 not-found.

## Implication

**Spec burndown counts are unreliable until checkbox-vs-reality reconciliation runs.** Both spec 013 (56 incomplete) and spec 021 (186 incomplete) are inflated by stale references. Real outstanding work is much smaller.

## Next-session actions

1. Run reconciliation script: for each spec, parse checkboxes referencing GH PR numbers → check if MERGED/CLOSED → batch tick those off in tasks.md.
2. Adopt forward-only convention: when merging a PR that's referenced in a spec, immediately tick the checkbox in same commit (or via post-merge hook).
3. Audit specs 017 (73), 020 (57), 019 (55), 018 (54), 015 (49) for same pattern — all listed in spec heatmap as "active" but likely similarly stale.
