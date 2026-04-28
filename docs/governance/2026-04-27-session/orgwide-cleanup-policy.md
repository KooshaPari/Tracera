# Org-Wide Cleanup Policy (proposed)
**Date:** 2026-04-27
**Status:** Proposed (refined from this session's branch + bot-issue cleanup work)

## Stale branch deletion
- **Trigger:** Branch's PR is merged or closed AND no commits in last 30 days.
- **Tool:** `branch_cleanup_wide.sh <repo>` (in `repos/docs/scripts/lockfile-regen/`).
- **Cadence:** Weekly cron when GH Actions billing returns; manual until then.
- **Bypass:** Branches matching `release/*`, `hotfix/*`, `prod/*` never auto-deleted.

## Bot-issue dedup (R6 pattern)
- **Trigger:** ≥2 OPEN bot-authored issues with identical titles in same repo.
- **Action:** Close all but the lowest-numbered with auto-comment linking the keep.
- **Bot author whitelist:** `github-actions`, `dependabot`, `renovate`, any `*-bot`.
- **Tool:** `/tmp/issue_dedup.py` (Python orchestrator pattern, sync execution).
- **Safeguards:** Re-verify state=OPEN + bot-author per issue before close.

## Stale-PR closure
- **Trigger:** PR open >90 days, no commits in last 60 days, no required reviewer activity.
- **Action:** Close with comment: "Auto-closed for staleness; reopen if still relevant."
- **Don't auto-close:** Drafts, dependabot, blocked-by-other-PR.

## Archive workflow for dead repos
- **Signal:** No commits in 365 days, no open PRs/issues.
- **Process:** Open issue "Archive proposal", wait 14 days for owner objection, then `gh repo archive`.
- **Reverse:** `gh repo unarchive` keeps history; ownership preserved.

## Disk hygiene (local)
- `/tmp/wave*` — keep latest 30, prune rest.
- `/tmp/<repo>-*` clones — delete after script completes (use `trap cleanup EXIT`).
- `target/` directories in archived/dormant repos — `target-pruner --prune` weekly.
- `.git/objects/pack/*.tmp_*` — clean via `git gc --aggressive` if disk pressure.

## Memory hygiene (per-session)
- Append, don't overwrite, when possible.
- Date-stamp transient memories (e.g., "feedback_<topic>_2026_04_27.md") for aging.
- Mark superseded memories — don't delete; annotate "DEPRECATED 2026-XX-XX, see <new-rule>".
- MEMORY.md stays ≤200 lines (truncation point); push older entries to dated subdirs.

## Throughput-vs-debt tradeoff
- Lockfile-regen PRs: high throughput, low debt — automate aggressively.
- Manifest-edit PRs: lower throughput, higher debt — gate via owner review.
- Stale-branch deletion: zero debt — automate fully.
- Issue dedup: zero debt for bot duplicates; never touch human-authored.
