# Tomorrow Start Handoff Playbook — 2026-04-27 (read this FIRST)

**Audience:** First agent in next session.
**Purpose:** Skip rediscovery. Run mechanical checks, pick a lane, go.
**Predecessor artifacts:** `SESSION_CLOSE_2026_04_27.md`, `FINAL_STATE_2026_04_27.md`.

---

## FIRST 5 MINUTES — Mechanical State Checks

Run these commands in order. Treat each as a gate.

```bash
# 1. Disk floor (latest live check: 29 GiB free; if <30 GiB, run /tmp prune BEFORE dispatch)
df -h /

# 2. PR queue regression check (expect [] after latest drain)
gh pr list -R KooshaPari/PhenoProc --state open --json number,title,url
gh pr list -R KooshaPari/eyetracker --state open --json number,title,url
gh pr list -R KooshaPari/KDesktopVirt --state open --json number,title,url
gh pr list -R KooshaPari/Tracera --state open --json number,title,url

# 3. PhenoProc PR #21 — should be MERGED; pheno workspace is unblocked for inclusion
gh pr view 21 -R KooshaPari/PhenoProc --json state,mergeable
#    MERGED -> pheno workspace UNBLOCKED for cargo-deny inclusion
#    OPEN   -> stale doc or regression; re-audit before cargo work

# 4. Canonical /repos branch state; ignore submodules because AgilePlus can break plain status.
git -C /Users/kooshapari/CodeProjects/Phenotype/repos status --short --branch --ignore-submodules
git -C /Users/kooshapari/CodeProjects/Phenotype/repos remote -v
#    origin currently points at KooshaPari/Tracera.git; do NOT push /repos canonical.

# 5. FocalPoint zero-advisory invariant (expect "advisories ok")
cd /Users/kooshapari/CodeProjects/Phenotype/repos/FocalPoint && \
  cargo deny check advisories 2>&1 | tail -3
```

**Failure modes:**
- `df -h` <30 GiB -> dispatch prune sweep on `/private/tmp` first; do NOT start cargo agents.
- FocalPoint advisories regressed -> stop, treat as P0 regression, identify the dep that drifted.
- `/repos` shows non-canonical branch or Tracera `origin` -> do not push; fix the
  parent remote trap only after pack cleanup is understood.

---

## FIRST DECISION LANE — 5 to 15 min — Pick ONE

### Lane A — Pack corruption gc on /repos canonical
- **Why:** 109 unique missing trees in `/repos` parent .git; blocks pushes and `git fsck` cleanliness.
- **Blocker:** Bash sandbox refuses `rm -f .git/objects/info/commit-graph` and `git gc --aggressive --prune=now` on the parent.
- **Action:** Request explicit user permission grant for those two commands; once granted, run gc -> fsck -> rebase -> push.
- **Reference:** `pack_corruption_diagnosis_2026_04_26.md`, `canonical_commit_strategy_2026_04_27.md`.

### Lane B — Address canonical-subdir-inheritance trap (Option C)
- **Why:** /repos canonical subdirs inherit parent remote; common foot-gun (Tracera origin clash, etc.).
- **Action:** Create new `phenotype-org-governance` GitHub repo; migrate `/repos/docs/governance/`, `/repos/worklogs/`, root governance markdown into it as its own git repo.
- **Reference:** `nested_workspaces.md`, `canonical_commit_strategy_2026_04_27.md`. Long-term fix to several recurring classes of bugs.

### Lane C — Continue cargo-deny W-96 from the post-drain baseline
- **Why:** FocalPoint at zero; org-wide W-95 = 8 advisories. Direct, mechanical, agent-parallelizable.
- **Completed in latest queue drain:**
  - **KDesktopVirt #9** — bollard 0.20 lane landed.
  - **eyetracker #3** — UniFFI 0.31 lane landed.
  - **Tracera #374** — performance smoke startup unblock landed.
- **Next action:** take a fresh cargo-deny snapshot before choosing the next
  advisory target; do not reuse the pre-merge 8-advisory breakdown as current.
- **Pattern:** Use FocalPoint W-93..W-95 commits as template (templates-registry refactor was the model that retired iron/nickel/multipart/typemap).

**Recommended default if user is asleep:** Lane C. Lane A and B both need user keystrokes / confirmations.

---

## LONGER PLAY — 15+ min

| Item | Strategy | Pre-staged file | Notes |
|---|---|---|---|
| helios-cli rebase | Strategy 1: drop b36643bf2 | n/a | bad commit identified; rebase locally then PR |
| argis-extensions | Strategy C: `git merge` over rebase | n/a | rebase keeps re-conflicting; merge once, move on |
| AgilePlus README rebase | apply pre-staged file | `proposals/` | file already authored; just rebase + commit |
| GDK README conflict | manual resolve | n/a | pick newer; verify lints clean |
| AgilePlus 6 unpushed commits | investigate | n/a | in-flight last session; figure out provenance, push or cherry-pick |

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

## ENV INVARIANTS — DO NOT VIOLATE

- **Disk floor:** Do not dispatch new cargo work below **20 GiB free**.
- **FD floor:** Cap concurrent cargo agents at **2** (kernel maxfiles=122,880 saturates ~5).
- **/tmp creep:** Run `/tmp` prune every ~10 dispatches; agent subprocesses leak `mktemp -d` clones.
- **Pack-gc:** Still blocked in sandbox; do not retry without permission.
- **agent-imessage hook:** action_events.jsonl stopgap holds sub-second; will degrade as log regrows past ~1.2 MB. Watch latency; rotate log proactively if it crosses 1 MB.
- **No push of /repos canonical** until pack corruption + Tracera origin trap resolved.
- **FocalPoint zero-advisory** is a load-bearing invariant; any regression is P0.

---

## Quick reorientation (one-paragraph)

Yesterday closed FocalPoint to zero advisories, then the latest queue drain
landed PhenoProc #21, eyetracker #3, KDesktopVirt #9, and Tracera #374. The
KooshaPari fleet open-PR queue is zero. /repos canonical still has 109 missing
trees and the parent remote still points at Tracera, so do not push from the
parent checkout. Disk is currently near the floor at 29 GiB free; prune before
dispatching cargo work, then take a fresh cargo-deny snapshot before choosing
the next W-96 target.
