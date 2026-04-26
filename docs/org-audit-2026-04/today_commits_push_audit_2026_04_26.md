# Today's Commits — Push Completeness Audit (2026-04-26)

**Audit window:** `--since="2026-04-26 00:00:00"` (local, all branches)
**Scope:** All git repos under `/repos` excluding `.archive/`, `.worktrees/`
**Repos scanned:** 100 with `.git/` directories
**Repos with today commits:** 53
**Audit method:** `git log --since` + `git log @{u}..HEAD` per repo
**Push action:** NONE (audit only). Round-8 dispatch follows.

---

## Summary

| Bucket | Count | Notes |
|---|---:|---|
| Repos with today commits | 53 | |
| Fully pushed (today) | 42 | All today commits already on origin |
| Has unpushed today commits | 11 | Detail below |
| `DETACHED_HEAD` (skip) | 2 | AgentMCP, Civis |
| `CANONICAL_INHERITANCE` (skip) | 2 | artifacts (46), phench (46) — origin=Tracera |

---

## Repos with Unpushed Today's Commits

| Repo | Today | Unpushed | Branch | Reason | Round-8 Action |
|---|---:|---:|---|---|---|
| AgilePlus | 3 | 2 | main | DIVERGED ahead=2 behind=4 | Rebase + push |
| argis-extensions | 1 | 1 | main | DIVERGED ahead=24 behind=11 | Rebase + push |
| GDK | 2 | 2 | main | DIVERGED ahead=6 behind=8 | Rebase + push |
| helios-cli | 1 | 1 | main | DIVERGED ahead=7 behind=11 | Rebase + push |
| AtomsBot | 1 | 1 | main | PUSHABLE (clean ahead-only) | Push |
| chatta | 1 | 1 | main | PUSHABLE (clean ahead-only) | Push |
| FocalPoint | 4 | 2 | main | PUSHABLE (clean ahead-only) | Push |
| heliosCLI | 7 | 2 | fix/deps-handlebars-critical-2026-04-26 | PUSHABLE | Push |
| HeliosLab | 2 | 2 | chore/gitignore-worktrees-2026-04-26 | PUSHABLE | Push |
| KDesktopVirt | 5 | 1 | main | PUSHABLE | Push |
| PhenoMCP | 1 | 1 | main | PUSHABLE | Push |

---

## Round-8 Target List (for next dispatch)

### Tier A — Should-be-pushable (clean fast-forward, ahead-only)

These have no upstream divergence; a plain `git push` should succeed.

1. **AtomsBot** `main` — 1 commit (`a71649d docs(readme): add standard badge header`)
2. **chatta** `main` — 1 commit (`d974fb8 docs(readme): add standard badge header`)
3. **FocalPoint** `main` — 2 commits (`d00e542 fix(ios): remove duplicate WeeklyReviewDto`, `906075b docs(ios): smoke-verify Xcode build`)
4. **heliosCLI** `fix/deps-handlebars-critical-2026-04-26` — 2 commits (Cargo.lock refresh + npm batch bump)
5. **HeliosLab** `chore/gitignore-worktrees-2026-04-26` — 2 commits (ratatui 0.30, pyo3 0.24 sec bumps)
6. **KDesktopVirt** `main` — 1 commit (`f99a6ac fix(bin/kvirtualstage): delegate to lib crate`)
7. **PhenoMCP** `main` — 1 commit (`48bc21a docs(readme): re-apply badge header atop #12`)

**Tier A total: 7 repos, 10 commits.**

### Tier B — Diverged (rebase-then-push, may have conflicts)

Local has diverged from `origin/main`. Round-8 must `git fetch && git rebase origin/main` first; if conflicts, flag for manual resolution.

1. **AgilePlus** main — ahead=2 behind=4 (2 today: spec(013) cancel, docs readme)
2. **argis-extensions** main — ahead=24 behind=11 (1 today: badge header — full ahead set is older)
3. **GDK** main — ahead=6 behind=8 (2 today: Cargo.lock dedupe, docs readme)
4. **helios-cli** main — ahead=7 behind=11 (1 today: dead-code execpolicy-legacy removal)

**Tier B total: 4 repos, 6 today commits (plus older ahead commits to also flow).**

---

## Skipped (per policy)

### Detached HEAD (skip per AgentMCP runbook)
- **AgentMCP** — 1 today commit, HEAD detached
- **Civis** — 9 today commits, HEAD detached

### Canonical-subdir inheritance (origin = Tracera, dir != Tracera) — SKIP
- **artifacts** — 46 today commits, origin=Tracera (inherited gitlink)
- **phench** — 46 today commits, origin=Tracera (inherited gitlink)

These directories sit inside the parent monorepo's `.git/` worktree config; pushing from them would target the wrong repo. The actual commits live in their canonical Tracera worktree which has its own push path.

---

## Verification Commands

Per repo (Tier A example):
```bash
cd /Users/kooshapari/CodeProjects/Phenotype/repos/AtomsBot
git log @{u}..HEAD --oneline   # confirm unpushed shas
git push origin main           # round-8 action
```

Per repo (Tier B example):
```bash
cd /Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus
git fetch origin
git rebase origin/main         # resolve conflicts if any
git push origin main
```

---

## Notes for Round-8 Dispatcher

- Total target commits: **10 clean + 6 diverged = 16 today commits across 11 repos**
- All Tier A pushes are independent — can run in parallel.
- Tier B should run sequentially or in a smaller parallel batch with conflict detection.
- Do NOT attempt `artifacts` or `phench` — they will fail or push to wrong remote.
- AgentMCP and Civis detached HEADs are deliberate per their runbooks.

---

## Refresh 2026-04-26 late evening (post-restart, post-Round-8/9a)

**Re-audit method:** Same script, all subdirs of `/repos`.
**Repos with today commits this pass:** 56 (up from 53)
**Skipped per policy:** AtomsBot + chatta (archived), AgentMCP (detached), artifacts + phench (Tracera-canonical inheritance, today=57 each).
**Counted scope:** 49 repos.

### Refreshed Summary

| Bucket | Count | Notes |
|---|---:|---|
| Repos with today commits (counted) | 49 | excludes archived/detached/Tracera-canonical |
| Fully pushed (ahead=0, behind=0) | 42 | all today commits on origin |
| Pushable FF (ahead>0, behind=0) | 4 | clean push — Round-9 Tier A |
| Diverged (behind>0) | 3 | rebase-then-push — Round-9 Tier B |
| No upstream set | 2 | HeliosLab, PhenoMCP — branch creation needed |

### Tier A — Pushable (clean fast-forward)

| Repo | Branch | Ahead | Today | Notes |
|---|---|---:|---:|---|
| AgilePlus | spec/013-cancelled | 2 | 6 | feature branch — push to origin or PR. main ahead also includes 2b3909f chore(deny) + 282a8d5 spec(013). |
| Civis | main | 8 | 8 | NOT detached anymore — clean ahead-only on main. Includes YANKED js-sys/wasm-bindgen patch + cargo-deny baseline + governance scaffolding. |
| heliosCLI | fix/deps-handlebars-critical-2026-04-26 | 1 | 9 | tip ahead-only; rest of today commits already pushed. |
| pheno | main | 3 | 7 | clean fast-forward. |

**Tier A total: 4 repos, 14 unpushed commits.**

### Tier B — Diverged (rebase-then-push)

| Repo | Branch | Ahead | Behind | Today | Notes |
|---|---|---:|---:|---:|---|
| argis-extensions | main | 24 | 11 | 1 | wide divergence, mostly older. |
| GDK | main | 6 | 8 | 2 | divergence persisted from earlier audit. |
| helios-cli | main | 7 | 13 | 1 | divergence widened (was 11) — additional upstream commits landed. |

**Tier B total: 3 repos, 4 today commits (plus older ahead set).**

### No-Upstream

| Repo | Branch | Today | Action |
|---|---|---:|---|
| HeliosLab | chore/gitignore-worktrees-2026-04-26 | 3 | `git push -u origin <branch>` to create remote branch |
| PhenoMCP | main | 1 | local main has no tracking — verify origin/main and re-set upstream |

### Delta vs Earlier Audit (commit 5c7b9b1bbd)

| Repo | Earlier Status | Refresh Status | Delta |
|---|---|---|---|
| AtomsBot | Tier A (ahead=11, 1 today) | SKIP (archived) | clarified — archived, not pushable |
| chatta | Tier A (ahead=17, 1 today) | SKIP (archived) | clarified — archived, not pushable |
| FocalPoint | Tier A | PUSHED (ahead=0) | resolved Round-7/8 |
| HeliosLab | Tier A | NO_UPSTREAM (3 today now) | branch never pushed; +1 today commit |
| KDesktopVirt | Tier A | PUSHED | resolved |
| PhenoMCP | Tier A | NO_UPSTREAM | tracking lost |
| AgilePlus | Tier B (ahead=2 behind=4) | Tier A (ahead=2 behind=0) | rebased clean |
| heliosCLI | Tier A (ahead=2) | Tier A (ahead=1) | partial push landed |
| Civis | DETACHED (9 today) | Tier A on main (8 today) | detached resolved, 1 commit reconciled |
| BytePort | not flagged | PUSHED (6 today) | new push wave |
| DevHex/Httpora/nanovms | — | PUSHED | Round-7a confirmed |
| HeliosLab | Tier A (2 today) | NO_UPSTREAM (3 today) | feature-branch progression |

### Round-9 Targets

**Tier A push (parallel-safe):** AgilePlus, Civis, heliosCLI, pheno (4 pushes, 14 commits).
**Tier B rebase-then-push (sequential, conflict-prone):** argis-extensions, GDK, helios-cli (3 repos).
**No-upstream (set tracking):** HeliosLab (push -u feature branch), PhenoMCP (re-establish main tracking).

**Total Round-9 actionable: 9 repos.**

### Skipped (unchanged)

- **Archived:** AtomsBot, chatta (push will fail — repos locked).
- **Detached HEAD:** AgentMCP (deliberate per runbook).
- **Canonical-Tracera inheritance:** artifacts, phench (origin=Tracera, sit inside parent monorepo gitlink — not pushable from these dirs).
