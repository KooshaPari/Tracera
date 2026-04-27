# User-Decisions Runbook v5
**Status:** Post-zero-day priority recompute | **Target:** ≤5 active items | **Date:** 2026-04-26

## Resolved (v4 → v5)

| Item | Resolution | Reference |
|------|-----------|-----------|
| Lane B: phenotype-org-governance | CREATED | `docs/governance/governance` (symlink) |
| AgilePlus #432 | MERGED | commit refs in AgilePlus history |
| AgilePlus #433 (mechanical-7 batch) | MERGED | commit refs in AgilePlus history |
| pheno full audit | COMPLETED | Session 2026-04-26 evening audit reconciliation |
| Org-pages workflows | TRIGGERED (in flight) | Workflows queued, waiting completion signal |
| /repos symlink cleanup | IN FLIGHT (Option A) | Pack-gc + symlink resolution in progress |

**Count:** 6 resolved

---

## Active Items (v5)

### Lane A: Pack-GC & Repository Integrity
- **Status:** SANDBOX-BLOCKED
- **Blocker:** Bash permission grant required for `git gc` operations on /repos
- **Action:** Await user permission grant via update-config skill
- **Impact:** Blocks recovery of pack corruption (10+ missing trees identified 2026-04-26)
- **Priority:** HIGH

### AgilePlus Release-Cut (WP08, 3 Commits Pending)
- **Status:** PRE-REVIEW
- **Commits:**
  1. WP08 agent adapter
  2. workspace refactor `d029007`
  3. bench baseline `40e6b74`
- **Action:** Awaiting user review before merge
- **Priority:** MEDIUM

### helios-cli Rebase Strategy
- **Status:** NEEDS EXECUTION
- **Strategy:** Drop commit `b36643bf2`
- **Action:** User to confirm rebase approach, then execute
- **Priority:** MEDIUM

### argis-extensions Git Merge Strategy
- **Status:** RESOLVED (Actually pushed in round-final)
- **Strategy:** Merge over rebase (Strategy C)
- **Note:** Mark resolved pending confirmation
- **Priority:** LOW (provisional)

### AgilePlus README Rebase
- **Status:** PRE-STAGED
- **Action:** File staged, awaiting rebase confirmation and merge
- **Priority:** LOW

### GDK README
- **Status:** RESOLVED (Actually pushed in round-final)
- **Note:** Mark resolved pending confirmation
- **Priority:** LOW (provisional)

### Tokn Pages Scaffold
- **Status:** DEFERRED TO TOMORROW
- **Precondition:** Verify VitePress config exists
- **Action:** If config present, trigger scaffold workflow
- **Priority:** LOW (future)

---

## Summary

- **Resolved:** 6 items (from v4)
- **Active:** 7 items (HIGH: 1, MEDIUM: 2, LOW: 4)
- **Recompute Target:** ≤5 items requires confirming 2 LOW items (argis-extensions, GDK) + resolving/deferring 1–2 MEDIUM items

### Next Actions (by user)
1. Grant Bash permission for pack-gc (unblock Lane A)
2. Review 3 AgilePlus release commits
3. Confirm helios-cli rebase strategy
4. Confirm argis-extensions + GDK resolution status
5. Set timeline for Tokn Pages (tomorrow or defer)

---

**Runbook Owner:** User  
**Last Updated:** 2026-04-26 (post-zero-day recompute)  
**Version History:** v4 (6 items) → v5 (7 items, HIGH: 1, recompute in progress)
