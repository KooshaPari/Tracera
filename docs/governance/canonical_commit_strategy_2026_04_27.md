# /repos Canonical Commit Accumulation Strategy

**Date:** 2026-04-27
**Auditor:** investigation agent
**Status:** RECOMMENDATION — no action taken

## Problem Statement

The `/Users/kooshapari/CodeProjects/Phenotype/repos/` directory is a working tree
with `origin = git@github.com:KooshaPari/Tracera.git` due to the
**canonical-subdir-inheritance trap** (see memory: `feedback_canonical_subdir_inheritance.md`).

This is the parent of ~70 project subdirectories, but `git remote` for `/repos`
itself points at the Tracera repo. Any `git push` from `/repos` would publish
org-wide audit/governance docs to the Tracera fork — content entirely unrelated
to the Tracera project.

## Current State (2026-04-27)

- **Branch:** `chore/gitignore-worktrees-2026-04-26`
- **Origin:** `KooshaPari/Tracera` (inherited)
- **Unpushed commits:** **8** (all under `docs/`)
- **Today's commits land here, not in any project repo**

### Unpushed commit inventory

| SHA | Path | Category |
|-----|------|----------|
| 9f9dddb4 | docs/governance/FINAL_STATE_2026_04_27.md | governance |
| 435cac02 | docs/governance/sbom_tracking_policy_2026_04_27.md | governance |
| d4c634c2 | docs/governance/SESSION_CLOSE_2026_04_27.md | governance |
| 033ebbb5 | docs/org-audit-2026-04/cargo_deny_w95_…md | audit |
| 54efae71 | docs/changes/2026-04-26-focalpoint-final-5/proposal.md | proposal |
| fbac3cf8 | docs/governance/prs_today_2026_04_27_status.md | runbook |
| 97e1198f | docs/changes/2026-04-26-focalpoint-uniffi-31/proposal.md | proposal |
| cbe02ad0 | docs/governance/SESSION_CLOSE_2026_04_27.md | governance |

Plus prior accumulation today (per session memory): ORG_DASHBOARD v53/v54/v55,
cargo_deny W-92/W-93/W-94, dependabot triage, dead-code audit,
proposals (templates-registry, starlark-15, uniffi-31, reqwest-12),
runbooks (user_decisions, evalora_404, archived_repo_triage), policies
(push_completeness, day-end-audit, pack_corruption, sbom_tracking).

**100% of content is org-wide governance/audit. Zero Tracera-relevant.**

## Trade-Off Matrix

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| **A. Leave forever local** | Never push; commits live only in this working tree | Zero pollution; zero work | Single point of failure (disk wipe = lost history); no peer review; not discoverable |
| **B. Push to Tracera fork branch** | `git push origin chore/gitignore-worktrees-2026-04-26` | Cheap; preserves history off-disk | Pollutes Tracera repo with unrelated content; future fetchers confused; violates repo-purpose hygiene |
| **C. Migrate to dedicated `phenotype-org-governance` repo** | Create new repo, init from current tree, push docs/ history | Proper home; discoverable; correct provenance | Multi-step setup (create repo → reset remote → preserve history via filter-repo or fresh init → push) |
| **D. Tarball archive** | `tar czf /tmp/repos-canonical-2026-04-27.tgz docs/ .git/` | Immediate safety; zero remote pollution | Not version-controlled; no peer access; recovery requires manual extract |

## Recommendation

**Long-term: Option C** (`phenotype-org-governance` repo).

This is the only option where:
- Docs have a correct, discoverable home
- Remote history matches local history
- Other agents/sessions can fetch and verify org-wide audit state
- `/repos` canonical can have its remote corrected (or fully detached) without losing work

**Immediate (today): Option D** (tarball snapshot) as a safety net while Option C
is set up. One command, zero risk, preserves history if disk fails before C lands.

**Reject:** Option B (Tracera pollution is irreversible without force-push), Option A
(history loss risk is unacceptable for ≥8 commits/day of audit corpus).

## Action Plan

### Phase 1 — Immediate safety (5 min, 2 tool calls)
1. `tar czf ~/repos-canonical-docs-2026-04-27.tgz -C /repos docs/ .git/HEAD .git/refs/`
2. Verify tarball integrity: `tar tzf ~/repos-canonical-…tgz | wc -l`

### Phase 2 — phenotype-org-governance setup (15 min, 8–12 tool calls)
1. `gh repo create KooshaPari/phenotype-org-governance --private`
2. New worktree directory (NOT in `/repos`): `~/CodeProjects/phenotype-org-governance/`
3. `git init` + `git remote add origin git@github.com:KooshaPari/phenotype-org-governance.git`
4. Copy `/repos/docs/governance/`, `/repos/docs/org-audit-*/`, `/repos/docs/changes/` into new repo
5. Initial commit + push
6. Going forward: write org-wide audits **into that repo**, not `/repos/docs/`

### Phase 3 — /repos canonical hygiene (5 min, 3 tool calls)
1. Decide: detach origin entirely (`git remote remove origin`) **or** retarget to
   a new "repos-meta" remote dedicated to /repos-level metadata only
2. Document the decision in memory + this file
3. Add a top-level `/repos/CLAUDE.md` warning re-stating the canonical-subdir-inheritance trap

### Phase 4 — Backfill (one-time, scope: this session's 8 commits + prior today's commits)
- `git log --since="2026-04-26"` at /repos to identify all audit-class commits
- Cherry-pick or copy file contents into phenotype-org-governance
- Once safely there, optionally `git reset` /repos to upstream (but only after Phase 2
  is verified push-complete)

## Risks

- **Phase 2 race:** if another agent commits to /repos during the migration window,
  cherry-pick window grows. Mitigate: do Phase 1 (tarball) first, do Phase 2 in a
  single uninterrupted batch.
- **Phase 3 detach:** removing origin breaks any tooling that assumes /repos has a
  remote. Audit `.git/hooks/`, agent-orchestrator, and Taskfile before detaching.
- **History bloat:** `/repos/.git` contains Tracera commits + 8 audit commits + N
  prior. A fresh init for phenotype-org-governance avoids importing Tracera history.

## Decision Required

Per investigation-only mandate, no action taken. User to confirm:
- [ ] Approve Option C + Option D combo
- [ ] Approve repo name `phenotype-org-governance` (or alternative)
- [ ] Approve Phase 3 detach vs. retarget

---

**Cross-refs:**
- Memory: `feedback_canonical_subdir_inheritance.md`
- Memory: `feedback_verify_origin_not_canonical.md`
- Memory: `feedback_repos_push_blockers.md` (W-78D — separate issue, /repos pack corruption)
