# User Decisions Runbook — 2026-04-26 Autonomous Wave (Late-Evening Refresh)

**Date:** 2026-04-26 (refreshed late evening, post-restart wave)
**Purpose:** Consolidated single-sitting decision document for all open items surfaced by today's autonomous work that genuinely require user judgment.
**Working dir:** `/Users/kooshapari/CodeProjects/Phenotype/repos`
**Disk budget at refresh:** 36 GiB free.
**Push policy:** This runbook does **not** push. All push actions are user-gated.

---

## Priority Index (Refreshed)

### CRITICAL (resolve first; blocks downstream work)
1. **`/repos` canonical-subdir pack corruption gc** (#8) — disk now safe (≥30 GiB) for steps 3–6
2. **AgilePlus README rebase conflict** (#1) — pre-staged merged file ready
3. **agileplus-plugin-core 404 blocking codex-local-boot worktree** (#9)
4. **helios-cli rebase decision** (#12, NEW) — Strategy 1 (drop `b36643bf2`) RECOMMENDED
5. **pheno workspace orphan `phenotype-core` member** (#13, NEW)

### HIGH (resolve same sitting)
6. **GDK quality-gate.yml conflict** (#3) — `--theirs` recommended
7. **argis-extensions divergence** (#4) — Strategy C (`git merge` over rebase) RECOMMENDED
8. **Tracera ARCHIVE/CONFIG/default delete** (#5) — base direction needed
9. **FocalPoint templates-registry refactor** (#14, NEW) — axum::extract::Multipart migration; 41% of org cargo-deny
10. **agent-devops-setups non-FF** (#15, NEW)
11. **helios-cli execpolicy-legacy delete commit `54fcdb00` held** (#16, NEW)

### MEDIUM (this week)
12. **Dependabot vitepress 1→2 major bump for PhenoLang docs** (#11)
13. **PhenoMCP follow-up — Dependabot advisories on PR #12 baseline** (#10)
14. **ratatui kmobile bump 0.24→0.30 (6 majors)** (#17, NEW) — deferred, scope decision
15. **Memory: tracera classification correction** (#18, NEW) — bookkeeping
16. **Tier B repos audit follow-up** (#19, NEW)

### Deferred / Info-only
- **OpenAI key revocation runbook re-verification** (#6)

### RESOLVED Today (close-out, do not re-act)
- ~~#2 BytePort untracked WIP~~ — **RESOLVED 2026-04-26** (commits `c907e3a5` / `54247fc1` / `f7035985`, pushed)
- ~~#7 AgentMCP fictional README~~ — **RESOLVED 2026-04-26** (remote PR #1 already replaced)
- ~~Civis push conflict~~ — **RESOLVED 2026-04-26** via PR #253 (verify-then-write `--ours`)
- ~~agent-imessage hook stopgap~~ — **RESOLVED 2026-04-26** (commit `37c15cf89e`)

---

## 1. AgilePlus README rebase conflict — CRITICAL

**Status:** Pre-staged merged file ready at `proposals/push_conflict_2026_04_26/AgilePlus_README.merged.md`.
**What user decides:** `merge` / `ours` / `theirs`.

```bash
cd /Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus
# Option A — accept staged merge (recommended)
cp ../proposals/push_conflict_2026_04_26/AgilePlus_README.merged.md README.md
git add README.md && git rebase --continue

# Option B — keep ours
git checkout --ours README.md && git add README.md && git rebase --continue

# Option C — take upstream
git checkout --theirs README.md && git add README.md && git rebase --continue
```

---

## 2. ~~BytePort untracked WIP~~ — RESOLVED 2026-04-26

Closed by commits `c907e3a5` / `54247fc1` / `f7035985` (pushed). No action.

---

## 3. GDK quality-gate.yml conflict — HIGH

**Status:** Local 21-line ad-hoc workflow vs upstream standard reusable-workflow call.
**Recommendation:** `--theirs` (adopt upstream).

```bash
cd /Users/kooshapari/CodeProjects/Phenotype/repos/GDK
git checkout --theirs .github/workflows/quality-gate.yml
git add .github/workflows/quality-gate.yml
git rebase --continue
```

---

## 4. argis-extensions divergence — HIGH

**Status:** 24-ahead / 11-behind. Manual conflicts in `plugins/contentsafety/plugin.go`, `plugins/contextfolding/folding.go`.
**Recommendation: Strategy C — `git merge origin/main` rather than rebase.** Rebase replays 24 commits with semantic conflicts in plugin code; merge resolves once and preserves history.

```bash
cd /Users/kooshapari/CodeProjects/Phenotype/repos/argis-extensions
git fetch origin
# Strategy C (RECOMMENDED): merge, not rebase
git merge origin/main
# Resolve once:
$EDITOR plugins/contentsafety/plugin.go
$EDITOR plugins/contextfolding/folding.go
git add plugins/contentsafety/plugin.go plugins/contextfolding/folding.go
git commit  # default merge message OK

# Alternative (NOT recommended): rebase, replays each of 24 commits
# git rebase origin/main
```

---

## 5. Tracera ARCHIVE/CONFIG/default delete — HIGH

**Status:** Pending delete needs direction.
**What user decides:** which checkout (`Tracera-recovered` or fresh clone) and which base.

```bash
# Option A — Tracera-recovered, target main
cd /Users/kooshapari/CodeProjects/Phenotype/repos/Tracera-recovered
git checkout main
git rm -r ARCHIVE/CONFIG/default
git commit -m "chore(tracera): drop ARCHIVE/CONFIG/default"

# Option B — fresh clone, feature branch
mkdir -p /tmp/tracera-clean && cd /tmp/tracera-clean
git clone git@github.com:KooshaPari/Tracera.git && cd Tracera
git checkout -b chore/drop-archive-default
git rm -r ARCHIVE/CONFIG/default
git commit -m "chore(tracera): drop ARCHIVE/CONFIG/default"
```

---

## 6. OpenAI key revocation — DEFERRED

**Status:** `/repos/docs/security/OPENAI_KEY_REVOCATION_RUNBOOK.md` not found at re-verify.
**Action:** confirm next session whether key was revoked; regenerate runbook if needed.

```bash
ls -la /Users/kooshapari/CodeProjects/Phenotype/repos/docs/security/ 2>&1
# Manual: https://platform.openai.com/api-keys
```

---

## 7. ~~AgentMCP fictional README~~ — RESOLVED 2026-04-26

Remote PR #1 already replaced. No action.

---

## 8. `/repos` canonical-subdir pack corruption — CRITICAL

**Status:** 19+ local commits + pack corruption (10+ missing trees) + duplicate config commit `ddf7e59b`. Disk now ≥30 GiB so steps 3–6 are safe.
**Safe sequence (per memory `feedback_repos_push_blockers`):**

```bash
cd /Users/kooshapari/CodeProjects/Phenotype/repos

# 1. Verify workstate (already done — 247 orphan submodule entries cleared)
git status --short --branch

# 2. Diagnose remote (CRITICAL: subdir inherits parent remote → Tracera origin)
git remote -v

# 3. gc to repair pack corruption (NOW SAFE — ≥30 GiB free)
git gc --aggressive --prune=now

# 4. Rebase to drop duplicate config commit ddf7e59b
git rebase -i <commit-before-ddf7e59b>  # mark ddf7e59b as `drop`

# 5. fsck to verify integrity
git fsck --full

# 6. Push decision (USER-GATED) — DO NOT push to Tracera origin
# Option A — keep local only (DEFAULT)
# Option B — push as fork branch
#   git branch -m pre-extract/tracera-sprawl-commit-LOCAL
#   git push origin pre-extract/tracera-sprawl-commit-LOCAL
# Option C — detach to new dedicated repo
```

---

## 9. agileplus-plugin-core 404 — CRITICAL

**Status:** AgilePlus `codex-local-boot` worktree blocked on missing GitHub repo.
**What user decides:** recreate / vendor / rebase-off-main.

```bash
# Option A — recreate empty repo
gh repo create KooshaPari/agileplus-plugin-core --public --description "AgilePlus plugin core"

# Option B — vendor in-tree
cd /Users/kooshapari/CodeProjects/Phenotype/repos/.worktrees/AgilePlus/chore/codex-local-boot
# Edit Cargo.toml: replace git dep with path dep, commit

# Option C — rebase off main (drop pin)
git rebase origin/main
```

---

## 10. PhenoMCP follow-up — MEDIUM

```bash
gh pr view 12 -R KooshaPari/PhenoMCP --json mergeable,statusCheckRollup
gh api /repos/KooshaPari/PhenoMCP/dependabot/alerts \
  --jq '.[] | {severity, summary: .security_advisory.summary}'
```

---

## 11. Dependabot vitepress 1→2 — MEDIUM

```bash
cd /Users/kooshapari/CodeProjects/Phenotype/repos/PhenoLang/docs
git checkout -b chore/vitepress-2-migration
pnpm add -D vitepress@^2 && pnpm install
pnpm docs:build  # fix breakage; https://vitepress.dev/guide/migration-from-v1
git add . && git commit -m "chore(docs): migrate vitepress 1 -> 2 (closes 6 dependabot alerts)"
gh pr create --title "chore(docs): vitepress v1 -> v2 migration" --body "Closes 6 dependabot alerts."
```

---

## 12. helios-cli rebase decision — CRITICAL (NEW)

**Status:** Rebase blocked by problematic commit `b36643bf2`.
**Recommendation: Strategy 1 — drop `b36643bf2`** during interactive rebase. Commit was a stale snapshot superseded by later work; dropping is non-destructive (changes already re-introduced downstream).

```bash
cd /Users/kooshapari/CodeProjects/Phenotype/repos/helios-cli
git fetch origin
git rebase -i origin/main
# In editor: change `pick b36643bf2 ...` to `drop b36643bf2 ...`
# Save, exit, let rebase complete.
git status   # verify clean
# Do NOT push without user confirmation.
```

---

## 13. pheno workspace orphan `phenotype-core` member — CRITICAL (NEW)

**Status:** Workspace `Cargo.toml` references `phenotype-core` as a member but the directory does not exist (separate from already-fixed `phenotype-config-core`).
**What user decides:** drop from members list, or restore directory from history.

```bash
cd /Users/kooshapari/CodeProjects/Phenotype/repos/pheno
ls -la phenotype-core 2>&1   # confirm missing
git log --all --diff-filter=D --summary -- phenotype-core | head -40

# Option A — drop from workspace members (recommended if intentionally removed)
$EDITOR Cargo.toml   # remove "phenotype-core" from [workspace].members
cargo metadata --no-deps   # verify resolves
git add Cargo.toml && git commit -m "chore(pheno): drop orphan phenotype-core workspace member"

# Option B — restore from prior SHA
git checkout <sha-before-deletion> -- phenotype-core
```

---

## 14. FocalPoint templates-registry refactor — HIGH (NEW)

**Status:** axum 0.7 → 0.8 `Multipart` extractor migration required. **11 cargo-deny alerts = 41% of org-wide cargo-deny burden** depend on this.
**Scope:** Update `axum::extract::Multipart` consumers in templates-registry to new API; verify upload flow.

```bash
cd /Users/kooshapari/CodeProjects/Phenotype/repos/FocalPoint
# Locate consumers
rg -l "axum::extract::Multipart|extract::Multipart" crates/templates-registry
# Migrate per axum 0.8 changelog: Multipart now takes &mut self for next_field, etc.
# Run:
cargo build -p templates-registry
cargo test -p templates-registry
cargo deny check
```

---

## 15. agent-devops-setups non-FF — HIGH (NEW)

**Status:** Push rejected non-fast-forward; needs rebase or force-with-lease decision.

```bash
cd /Users/kooshapari/CodeProjects/Phenotype/repos/agent-devops-setups
git fetch origin
git log --oneline @{u}..HEAD
git log --oneline HEAD..@{u}

# Option A — rebase onto upstream (recommended if local commits are atomic)
git rebase origin/main

# Option B — merge upstream into local
git merge origin/main

# Push only after user approves; never --force without --force-with-lease.
```

---

## 16. helios-cli execpolicy-legacy delete `54fcdb00` held — HIGH (NEW)

**Status:** Local commit `54fcdb00` deletes `execpolicy-legacy/` but is held pending user direction (paired with #12 rebase strategy).
**What user decides:** keep delete, revert delete, or scope to a separate PR.

```bash
cd /Users/kooshapari/CodeProjects/Phenotype/repos/helios-cli
git show --stat 54fcdb00

# Option A — keep delete, fold into rebase from #12
# (no extra action; commit rides through rebase)

# Option B — revert delete
git revert 54fcdb00

# Option C — separate PR
git branch chore/drop-execpolicy-legacy 54fcdb00
# (then rebase main excluding 54fcdb00 via interactive `drop`)
```

---

## 17. ratatui kmobile bump 0.24 → 0.30 — MEDIUM (NEW, DEFERRED)

**Status:** 6-major jump (0.24 → 0.25 → 0.26 → 0.27 → 0.28 → 0.29 → 0.30). High-API-churn library. Defer until kmobile UI roadmap is firmer.
**What user decides:** schedule a dedicated migration PR or hold at 0.24.

```bash
cd /Users/kooshapari/CodeProjects/Phenotype/repos/kmobile
# Audit current usage:
rg "ratatui::" --stats | tail -5
# Stage migration in worktree:
git checkout -b chore/ratatui-0.30-migration
# Bump in steps 0.24→0.26→0.28→0.30 with cargo check between, OR all-at-once.
```

---

## 18. Memory: tracera classification correction — MEDIUM (NEW)

**Status:** Memory entry classifies tracera incorrectly (label/state mismatch from earlier audit). Pure bookkeeping fix.
**What user decides:** approve correction wording, then update.

```bash
$EDITOR /Users/kooshapari/.claude/projects/-Users-kooshapari-CodeProjects-Phenotype-repos/memory/MEMORY.md
# Locate tracera reference and correct classification (active vs archive, role).
```

---

## 19. Tier B repos audit follow-up — MEDIUM (NEW)

**Status:** Today's audit surfaced multiple Tier B repos with minor drift (badges, README freshness, dependabot stragglers). Aggregate, not blocking.
**What user decides:** schedule a sweep wave or absorb into next `/loop`.

```bash
# Inventory:
ls /Users/kooshapari/CodeProjects/Phenotype/repos/docs/governance/ | grep -i tier
# Cross-ref ORG_DASHBOARD_v53 for Tier B list.
```

---

## Deferred / Wait Days–Weeks

| Item | Why | Re-check |
|------|-----|----------|
| #6 OpenAI key runbook | File missing; may already be revoked | Next session |
| #11 vitepress 1→2 | Breaking-change migration; non-urgent | ~7 days |
| #10 PhenoMCP advisories | Informational moderates | ~7 days |
| #17 ratatui kmobile | 6-major jump; needs roadmap | When kmobile UI scope locks |
| #19 Tier B repos | Aggregate cleanup | Next `/loop` wave |

---

## Summary (Refreshed)

- **Total open items:** 16 (was 11; +9 new, –4 resolved)
- **CRITICAL:** 5 (#1, #8, #9, #12, #13)
- **HIGH:** 6 (#3, #4, #5, #14, #15, #16)
- **MEDIUM:** 5 (#10, #11, #17, #18, #19)
- **Deferred / Info:** 1 (#6)
- **Resolved today:** 4 (BytePort, AgentMCP, Civis, agent-imessage hook)

**Disk budget at refresh:** 36 GiB free (gc on `/repos` is now safe).
**Push policy:** This runbook does **not** push. All push actions remain user-gated.
