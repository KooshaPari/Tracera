# AgilePlus Unpushed Commits Investigation — 2026-04-27

## Summary

Push-count audit (commit `4b25969e11`) flagged 6 today commits in AgilePlus
local with 0 on origin. Investigation finds **0 commits actually need to be
pushed**. All 6 either (a) already landed on `origin/main` via merged PRs as
GitHub-rewritten merge commits, or (b) belong to long-running branches with
unrelated work that pre-dates today.

The "6 unpushed today" signal is a **false positive** from comparing local
SHAs against origin SHAs without patch-id dedup. PR #413 squashed
`e076ad3` into `11789d9` on `origin/main`; PR #410 squashed the README work
that became `a59c681` locally into `6bc7a26` on `origin/main`.

State: `local main` is 2 ahead / 7 behind `origin/main`. `git pull --ff-only`
will not work (diverged); recommend `git fetch && git reset --keep origin/main`
on canonical (bare-tracking) since both ahead-commits already exist as
patch-equivalent merges upstream.

`origin/main` tip: `6387469` (PR #415, today 05:36).
Local `main` tip: `e076ad3` (today 02:50).

## Per-Commit Disposition

| SHA | Time | Branch | Subject | Status | Action |
|-----|------|--------|---------|--------|--------|
| `94f2475` | 01:12 | `agileplus/chore/codex-local-boot` | fix(workspace): remove orphan members from Cargo workspace | UNPUSHED on long-running feature branch | Roll into existing codex-local-boot PR or open new PR if branch is stale; not blocking |
| `a59c681` | 01:18 | `main` (local) | docs(readme): replace stale/fictional content with honest current state | SUPERSEDED by PR #410 → `6bc7a26` (different patch-id but same intent — PR version was rewritten/expanded) | DROP — local commit is now redundant; reset main to origin |
| `e076ad3` | 02:50 | `main` (local) | spec(013): mark phenotype-infrakit-stabilization CANCELLED | MERGED via PR #413 as `11789d9` (GitHub squash rewrote SHA) | DROP — already on origin; reset main to origin |
| `282a8d5` | 02:50 | `spec/013-cancelled` | spec(013): mark … CANCELLED | DUPLICATE of e076ad3 (identical patch-id `b61ca71d`) | DROP — branch can be deleted; PR #413 is its origin |
| `2b3909f` | 04:36 | `spec/013-cancelled` | chore(deny): remove 1 stale ignore (upstream patch landed) | UNPUSHED — small standalone cleanup not on origin | **PR-WORTHY** — open PR from `spec/013-cancelled` rebased onto `origin/main` for just this commit (or cherry-pick onto fresh branch) |
| `657f0af` | 02:50 | `spec/013-cancelled-marker` | spec(013): mark … CANCELLED | DUPLICATE of e076ad3 (identical patch-id `b61ca71d`) | DROP — branch can be deleted |

## Branch-Level View

- **`main` (local)**: 2 commits ahead (a59c681, e076ad3), both superseded
  by merged PRs. Diverged from origin by 7 commits. Recommend
  `git fetch origin && git update-ref refs/heads/main origin/main` from a
  worktree to align (do NOT push from canonical bare).
- **`agileplus/chore/codex-local-boot`**: 6 commits ahead, includes
  multi-day feat(auth)/MCP work. Today's `94f2475` is just a workspace
  cleanup. This branch represents real unmerged work that long predates
  today and is **not** the v0.2.1 release work. Status: integration TBD.
- **`spec/013-cancelled`** and **`spec/013-cancelled-marker`**: scratch
  branches that produced PR #413. The cancelled-marker SHA was rewritten
  by GitHub squash. Both safe to delete after the `2b3909f` cargo-deny
  cleanup is opened as its own PR.

## v0.2.1 Release Status

**No release-prep work is hiding in the 6 commits.** Memory note about
"v0.2.1 release sitting on unpushed branch" is outdated — release was
already shipped (per `reference_session_2026_04_25_releases.md` noting
AgilePlus v0.2.1 prep, and `reference_session_2026_04_26_evening.md` noting
AgilePlus v0.2.1 + observably-macros v0.1.1 released this evening). No
v0.2.2 prep present in any unpushed commit.

## Urgency Flags

- **None urgent.** No CVE, no security fix, no release-blocker among the
  6 commits.
- **Single PR-worthy item**: `2b3909f` (cargo-deny ignore cleanup) — low
  priority, can wait or be folded into next dependency sweep PR.
- Cleanup hygiene: scratch branches `spec/013-cancelled-marker` and
  `spec/013-cancelled` should be retired post-#413.

## Recommended Action Sequence

1. From a worktree (not canonical bare), realign `main` to `origin/main`
   to drop the 2 superseded ahead-commits.
2. Cherry-pick `2b3909f` onto a fresh `chore/cargo-deny-stale-ignore`
   branch off `origin/main`; open PR.
3. Delete `spec/013-cancelled-marker` and `spec/013-cancelled` branches
   after step 2.
4. Leave `agileplus/chore/codex-local-boot` for separate triage — it is
   real unmerged feature work, not part of today's signal.

NO push from canonical (bare). NO force-push.
