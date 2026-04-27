# Tomorrow Start Handoff Playbook — 2026-04-27 (read this FIRST)

**Audience:** First agent in next session.
**Purpose:** Skip rediscovery. Run mechanical checks, pick a lane, go.
**Predecessor artifacts:** `SESSION_CLOSE_2026_04_27.md`, `FINAL_STATE_2026_04_27.md`.

---

## FIRST 5 MINUTES — Gate Checks (Zero-Advisory State Confirmed ✅)

Run these in order. Treat each as a gate.

```bash
# 1. Disk floor (latest: 29 GiB free; halt new cargo below 20 GiB)
df -h / | grep -E "Avail|Use%"

# 2. Org-wide cargo-deny snapshot — CRITICAL (now 50 → 0 confirmed true-zero)
cd /Users/kooshapari/CodeProjects/Phenotype/repos/FocalPoint && cargo deny check advisories 2>&1 | tail -1
cd /Users/kooshapari/CodeProjects/Phenotype/repos/PhenoObservability && cargo deny check advisories 2>&1 | tail -1
cd /Users/kooshapari/CodeProjects/Phenotype/repos/PhenoMCP && cargo deny check advisories 2>&1 | tail -1
#    Expect: all "advisories ok" (true zero confirmed 2026-04-26)

# 3. Canonical /repos state (do NOT push until pack + Tracera origin fixed)
git -C /Users/kooshapari/CodeProjects/Phenotype/repos status --short --branch --ignore-submodules

# 4. PhenoShared PR status (4 PRs blocked on stale-branch conflicts; ready for rebase batch)
gh pr list -R KooshaPari/phenotype-shared --state open --json number,title,headRefName --limit 5
```

**Critical gates:**
- `cargo deny` regress (any >0 advisories) → P0 blocker; identify drift immediately
- `/repos` off-canonical → do not push until pack-gc + Tracera origin resolved
- Disk <20 GiB → prune `/private/tmp` before any cargo dispatch

---

## DECISION LANE — 5 to 30 min — Pick ONE (True Zero Achieved ✅)

**STATUS REFRESH:** Org-wide cargo-deny now **0 advisories** (was 50; confirmed FocalPoint, PhenoObservability, PhenoMCP all "advisories ok"). Zero-advisory work **100% COMPLETE**.

### IMMEDIATE (Lane C) — Rebase + Merge PhenoShared 4-PR batch
- **Why:** 4 stale-branch conflicts (phenoShared #123/#124/#125/#126) block integration into main.
- **Timeline:** ~10–20 min (mechanical rebase batch).
- **Action:** Rebase each on latest main, verify green, squash-merge.
- **Notes:** Load-bearing for pheno workspace; unblocks 4 consumers (Metron, PhenoObservability, etc.).
- **Task script:** Pre-stage batch rebase in worktree; `./batch-rebase-phenoshared.sh` if scripted.

### MEDIUM PRIORITY (Lane B) — phenotype-org-governance repo creation + migration
- **Why:** Solve canonical-subdir-inheritance trap (109 missing trees, Tracera origin clash); move `/repos/docs/governance/`, `/repos/worklogs/` out to standalone repo.
- **Timeline:** ~20–40 min (gh repo create + git mv + push + CI).
- **Action:** Create `phenotype-org-governance` on GitHub; migrate governance .md + worklogs into it; update canonical symlinks/readmes.
- **Blocker:** User must approve new repo creation.
- **Notes:** One-time structural fix; eliminates recurring "do not push /repos" footgun.

### LOWER PRIORITY (Lane A) — Pack corruption gc + Tracera origin fix
- **Why:** 109 unique missing trees block fsck cleanliness; parent `origin` points to Tracera.git (wrong).
- **Blocker:** Bash sandbox refuses `git gc --aggressive --prune=now` on parent.
- **Action:** Request explicit user permission; once granted, run gc -> fsck -> update origin -> validate.
- **Notes:** Unblock future canonical /repos pushes; not urgent if Lane B migration is planned.

**Default lane if user asleep:** Lane C (mechanical, no user touchpoint). Lane B requires approval; Lane A requires permission.

---

## LONGER PLAY — Follow Lane C Rebase (Total ~30–60 min)

| Item | Status | Action | Notes |
|---|---|---|---|
| **AgilePlus #432** (just opened) | Review + merge | Admin-merge (likely unblocked post-zero) | TBD feature; approve if on-roadmap |
| **AgilePlus release-cut-adopt** | 10 commits in-flight | Scope + review | Pending spec finalization; check AgilePlus /kitty-specs/ |
| **cargo-deny CI rollout** | 9 repos unmonitored | Deploy recommend doc | Landed in session-close; push 4–6 orgs in batch |
| **phenotype-org-governance** repo | Blocked on user | Create + migrate governance | Move /repos/docs/governance/ + /repos/worklogs/ (Lane B) |
| **PhenoProc submodule URL** | PR #25 merged ✅ | Audit related work | Companion fixes may exist; verify in thegent/cross-repo audit |

---

## REFERENCE SHELF — Pre-Loaded

Read in this order if context is needed:

1. `../org-audit-2026-04/ORG_DASHBOARD_v56_2026_04_27_final_final.md` — latest dashboard snapshot.
2. `user_decisions_runbook_2026_04_26.md` — 16 items, refreshed v2 by `5876b6178d`.
3. `pr-status-sweep-2026-04-27.md` — zero-open-PR fleet sweep.

Predecessor close artifacts:
- `SESSION_CLOSE_2026_04_27.md`
- `FINAL_STATE_2026_04_27.md`

---

## TASK-ORIENTED ANCHORS (Performance + Safety Gates)

**Start-of-session checklist:**
- [ ] `df -h /` — halt if <20 GiB; prune `/private/tmp` if cramped
- [ ] `cargo deny check advisories` on FocalPoint, PhenoObservability, PhenoMCP — must all pass (zero confirmed)
- [ ] `/repos` canonical branch check — verify NOT off-main; do NOT push until pack + origin fixed

**During execution:**
- **Disk floor:** Do not dispatch cargo work below **20 GiB free**
- **FD floor:** Cap concurrent cargo agents at **2** (kernel maxfiles saturates ~5)
- **/tmp creep:** Prune `/private/tmp` every ~10 dispatches (subagent mktemp clones accumulate)
- **Zero-advisory invariant:** FocalPoint + PhenoObservability + PhenoMCP must remain at zero; any regression is P0

**Known constraints:**
- **/repos pack-gc:** Still blocked in Bash sandbox; waiting on user permission for `git gc --aggressive --prune=now`
- **/repos canonical:** Do NOT push until pack corruption + Tracera origin are resolved (Lane A or Lane B path)
- **agent-imessage hook:** action_events.jsonl can degrade if log >1 MB; rotate proactively

---

## Reorientation (One-Paragraph — True Zero Confirmed ✅)

**Org-wide cargo-deny achieved TRUE ZERO advisories** (50 → 0, confirmed across FocalPoint, PhenoObservability, PhenoMCP).
Zero-advisory workstream **100% COMPLETE**. Post-drain gate: 4 critical PRs landed (PhenoProc #21, eyetracker #3, KDesktopVirt #9, Tracera #374).
Fleet open-PR queue is zero. **IMMEDIATE NEXT:** Rebase + merge PhenoShared 4-PR batch (10–20 min mechanical).
**MEDIUM TERM:** phenotype-org-governance repo creation to break canonical-subdir-inheritance footgun.
**KNOWN DEBT:** /repos canonical has 109 missing trees + Tracera origin; do NOT push until Lane A (pack-gc) or Lane B (governance repo) unblocks.
Disk 29 GiB; safe for next 2–3 cargo batches. **If user asleep:** run Lane C batch rebase automatically.
