# Tomorrow Start Handoff Playbook — 2026-04-27 (read this FIRST)

**Audience:** First agent in next session.
**Purpose:** Skip rediscovery. Run mechanical checks, pick a lane, go.
**Predecessor artifacts:** `SESSION_CLOSE_2026_04_27.md`, `FINAL_STATE_2026_04_27.md`.

---

## FIRST 5 MINUTES — Mechanical State Checks

Run these four commands in order. Treat each as a gate.

```bash
# 1. Disk floor (expect ~39 GiB free; if <30 GiB, run /tmp prune BEFORE dispatch)
df -h /

# 2. PhenoProc PR #21 — gating signal for pheno workspace full audit
gh pr view 21 -R KooshaPari/PhenoProc --json state,mergeable
#    OPEN  -> still blocked, do NOT start full pheno cargo-deny audit
#    MERGED -> pheno workspace UNBLOCKED for cargo-deny inclusion (W-96 work)

# 3. Canonical /repos branch state (expect ahead 9-15; NOT pushable due to Tracera origin trap)
git -C /Users/kooshapari/CodeProjects/Phenotype/repos status --short --branch

# 4. FocalPoint zero-advisory invariant (expect "advisories ok")
cd /Users/kooshapari/CodeProjects/Phenotype/repos/FocalPoint && \
  cargo deny check advisories 2>&1 | tail -3
```

**Failure modes:**
- `df -h` <30 GiB -> dispatch prune sweep on `/private/tmp` first; do NOT start cargo agents.
- FocalPoint advisories regressed -> stop, treat as P0 regression, identify the dep that drifted.
- `/repos` shows non-canonical branch -> revert to `chore/gitignore-worktrees-2026-04-26`.

---

## FIRST DECISION LANE — 5 to 15 min — Pick ONE

### Lane A — Pack corruption gc on /repos canonical
- **Why:** 109 unique missing trees in `/repos` parent .git; blocks pushes and `git fsck` cleanliness.
- **Blocker:** Bash sandbox refuses `rm -f .git/objects/info/commit-graph` and `git gc --aggressive --prune=now` on the parent.
- **Action:** Request explicit user permission grant for those two commands; once granted, run gc -> fsck -> rebase -> push.
- **Reference:** `pack_corruption_diagnosis_2026_04_26.md`, `feedback_repos_push_blockers.md`.

### Lane B — Address canonical-subdir-inheritance trap (Option C)
- **Why:** /repos canonical subdirs inherit parent remote; common foot-gun (Tracera origin clash, etc.).
- **Action:** Create new `phenotype-org-governance` GitHub repo; migrate `/repos/docs/governance/`, `/repos/worklogs/`, root governance markdown into it as its own git repo.
- **Reference:** `feedback_canonical_subdir_inheritance.md`. Long-term fix to several recurring classes of bugs.

### Lane C — Continue cargo-deny W-96 (default if no decision needed)
- **Why:** FocalPoint at zero; org-wide W-95 = 8 advisories. Direct, mechanical, agent-parallelizable.
- **Targets (priority order):**
  - **KDesktopVirt** — 4 bollard advisories (rustls-webpki cluster; bollard release upstream pending).
  - **AgilePlus** — 1 utoipa-axum advisory.
  - **eyetracker** — 2 bincode/paste advisories.
- **Goal:** 8 -> 4 or fewer.
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

1. `ORG_DASHBOARD_v55_2026_04_27_session_close.md` — final-final addendum / latest snapshot.
2. `user_decisions_runbook_2026_04_26.md` — 16 items, refreshed v2 by `5876b6178d`.
3. `session_2026_04_27_full_digest.md` — memory load-first entry.

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

Yesterday closed FocalPoint to zero advisories and W-95 org-wide to 8. PhenoProc PR #21 is OPEN and gates full pheno workspace audit. /repos canonical still has 109 missing trees (gc blocked by sandbox). Disk healthy at 39 GiB. Default to Lane C (cargo-deny W-96) if no user input. If user is awake, prompt for Lane A (gc permission) or Lane B (org-governance repo) decision first.
