# Tomorrow Start Handoff Playbook — 2026-04-27 (read this FIRST)

**Audience:** First agent in next session.
**Purpose:** Skip rediscovery. Run mechanical checks, pick a lane, go.
**Predecessor artifacts:** `SESSION_CLOSE_2026_04_27.md`, `FINAL_STATE_2026_04_27.md`.

---

## FIRST 5 MINUTES — Mechanical State Checks (Refreshed Post-Zero-Week)

Run these commands in order. Treat each as a gate.

```bash
# 1. Disk floor (latest live check: 29 GiB free; if <30 GiB, run /tmp prune BEFORE dispatch)
df -h /

# 2. PR queue regression check (expect [] — zero-drain completed in last session)
gh pr list -R KooshaPari/PhenoProc --state open --json number,title,url
gh pr list -R KooshaPari/eyetracker --state open --json number,title,url
gh pr list -R KooshaPari/KDesktopVirt --state open --json number,title,url
gh pr list -R KooshaPari/Tracera --state open --json number,title,url

# 3. PhenoProc PR #21 — MERGED ✅; pheno workspace UNBLOCKED for cargo-deny inclusion
gh pr view 21 -R KooshaPari/PhenoProc --json state
#    Expected: MERGED (confirmed post-session)

# 4. Org-wide cargo-deny snapshot (CRITICAL: was 50 → now 3 LOW advisories only)
cd /Users/kooshapari/CodeProjects/Phenotype/repos/FocalPoint && \
  cargo deny check advisories 2>&1 | tail -1
cd /Users/kooshapari/CodeProjects/Phenotype/repos/PhenoObservability && \
  cargo deny check advisories 2>&1 | tail -1
cd /Users/kooshapari/CodeProjects/Phenotype/repos/PhenoMCP && \
  cargo deny check advisories 2>&1 | tail -1
#    FocalPoint, PhenoObservability: expect "advisories ok"
#    PhenoMCP: expect "3 warnings" (rustls-webpki only; see FIRST DECISION)

# 5. Canonical /repos branch state; ignore submodules
git -C /Users/kooshapari/CodeProjects/Phenotype/repos status --short --branch --ignore-submodules
git -C /Users/kooshapari/CodeProjects/Phenotype/repos remote -v
#    origin currently points at KooshaPari/Tracera.git; do NOT push /repos canonical.
```

**Failure modes:**
- `df -h` <30 GiB -> dispatch prune sweep on `/private/tmp` first; do NOT start cargo agents.
- PhenoMCP advisories >3 OR FocalPoint/PhenoObservability regressed -> P0; identify drifted dep.
- `/repos` shows non-canonical branch or Tracera `origin` -> do not push; fix after pack cleanup understood.

---

## FIRST DECISION LANE — 5 to 30 min — Pick ONE (REFRESHED POST-ZERO-WEEK)

### Lane A — Pack corruption gc on /repos canonical
- **Why:** 109 unique missing trees in `/repos` parent .git; blocks pushes and `git fsck` cleanliness.
- **Blocker:** Bash sandbox refuses `rm -f .git/objects/info/commit-graph` and `git gc --aggressive --prune=now` on the parent.
- **Action:** Request explicit user permission grant for those two commands; once granted, run gc -> fsck -> rebase -> push.
- **Reference:** `pack_corruption_diagnosis_2026_04_26.md`, `canonical_commit_strategy_2026_04_27.md`.

### Lane B — Address canonical-subdir-inheritance trap (Long-term structural fix)
- **Why:** /repos canonical subdirs inherit parent remote; foot-gun (Tracera origin clash, etc.).
- **Action:** Create new `phenotype-org-governance` GitHub repo; migrate `/repos/docs/governance/`, `/repos/worklogs/`, root governance markdown into it as its own git repo.
- **Reference:** `nested_workspaces.md`, `canonical_commit_strategy_2026_04_27.md`. Solves several recurring bugs.

### Lane C — PhenoMCP rustls-webpki decision (THE 3 REMAINING ADVISORIES)
- **Why:** FocalPoint + PhenoObservability at zero; PhenoMCP has 3 LOW advisories (rustls-webpki only). Org-wide W-95 = 50 → 3 (-94%).
- **Decision point:** Two paths, both ~5–30 min:
  - **Path C1:** Bump PhenoMCP to 0.104.0-alpha.7 (clears all 3, unblock stable once upstream available).
  - **Path C2:** Suppress 3 LOW advisories (awaiting upstream rustls/webpki stable fix, documented with tracking ref).
- **Completed in latest drain:**
  - **KDesktopVirt #9** — bollard 0.20 lane ✅
  - **eyetracker #3** — UniFFI 0.31 lane ✅
  - **Tracera #374** — startup perf unblock ✅
  - **PhenoProc #21** — integration in pheno workspace ✅
- **Pattern:** Use FocalPoint W-93..W-95 commits as template (templates-registry refactor model).

**Recommended default if user asleep:** Lane C (decision + action both mechanical). Lane A requires permission; Lane B requires repo creation (user touchpoint).

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

## Quick reorientation (one-paragraph — Post-Zero-Week Update)

The zero-week wave completed with FocalPoint + PhenoObservability closing to zero advisories.
The post-drain queue landed 4 critical PRs: PhenoProc #21 (pheno workspace unlocked),
eyetracker #3 (UniFFI 0.31), KDesktopVirt #9 (bollard 0.20), and Tracera #374 (startup perf).
Org-wide cargo-deny collapsed from 50 advisories to 3 LOW (PhenoMCP rustls-webpki).
KooshaPari fleet open-PR queue is zero. /repos canonical still has 109 missing trees and
parent remote points at Tracera (do not push). **FIRST DECISION:** PhenoMCP rustls-webpki
(Path C1: alpha bump; Path C2: suppress). Disk 29 GiB; take fresh snapshot before next cargo target.
