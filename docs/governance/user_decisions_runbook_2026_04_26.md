# User Decisions Runbook — 2026-04-26 Autonomous Wave

**Date:** 2026-04-26
**Purpose:** Consolidated single-sitting decision document for all open items surfaced by today's autonomous work that genuinely require user judgment.
**Working dir:** `/Users/kooshapari/CodeProjects/Phenotype/repos`

---

## Priority Index

### CRITICAL (resolve first; blocks downstream work)
1. **`/repos` canonical-subdir-inheritance — 19+ unpushed commits going to Tracera origin** (#8)
2. **AgilePlus README rebase conflict** (#1)
3. **agileplus-plugin-core 404 GitHub repo blocking codex-local-boot worktree** (#9)

### HIGH (resolve same sitting)
4. **GDK quality-gate.yml conflict** (#3)
5. **argis-extensions divergence (24-ahead/11-behind, manual conflicts)** (#4)
6. **Tracera ARCHIVE/CONFIG/default delete — needs checkout + base direction** (#5)
7. **BytePort untracked WIP — 6 paths need triage** (#2)

### MEDIUM (this week)
8. **Dependabot vitepress 1→2 major bump for PhenoLang docs** (#11)
9. **PhenoMCP follow-up — verify Dependabot advisories on PR #12 baseline** (#10)

### Deferred / Info-only
- **OpenAI key revocation runbook re-verification** (#6)
- **AgentMCP fictional README — RESOLVED 2026-04-26** (#7, can close)

---

## 1. AgilePlus README rebase conflict — CRITICAL

**Status:** Pre-staged merged file awaiting decision.
**Location:** `proposals/push_conflict_2026_04_26/AgilePlus_README.merged.md` (NOTE: directory not found at write-time; verify or re-stage before executing).
**What I did:** Generated a 3-way merged variant combining local edits with upstream. No commit yet.
**What user decides:** which of `merge` / `ours` / `theirs` to take.

```bash
# Option A — accept staged merge (recommended)
cd /Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus
cp ../proposals/push_conflict_2026_04_26/AgilePlus_README.merged.md README.md
git add README.md && git rebase --continue

# Option B — keep our local
git checkout --ours README.md && git add README.md && git rebase --continue

# Option C — take upstream
git checkout --theirs README.md && git add README.md && git rebase --continue
```

---

## 2. BytePort untracked WIP — HIGH

**Status:** 6 untracked paths in BytePort worktree.
**Paths:**
- `Cargo.toml`
- `Cargo.lock`
- `go.mod`
- `tests/smoke_test.rs`
- `backend/byteport/tests/smoke_test.rs`
- `docs/`

**What I did:** Inventoried only; no commit, no delete.
**What user decides:** commit-all (recommended) / gitignore / delete.

```bash
cd /Users/kooshapari/CodeProjects/Phenotype/repos/BytePort

# Option A — commit all (recommended)
git add Cargo.toml Cargo.lock go.mod tests/smoke_test.rs backend/byteport/tests/smoke_test.rs docs/
git commit -m "feat(byteport): scaffold workspace + smoke tests + docs"

# Option B — gitignore (preserve locally, exclude from repo)
cat >> .gitignore <<'EOF'
Cargo.toml
Cargo.lock
go.mod
tests/smoke_test.rs
backend/byteport/tests/smoke_test.rs
docs/
EOF
git add .gitignore && git commit -m "chore(byteport): ignore scaffolded WIP"

# Option C — delete
rm -rf Cargo.toml Cargo.lock go.mod tests/smoke_test.rs backend/byteport/tests/smoke_test.rs docs/
```

---

## 3. GDK quality-gate.yml conflict — HIGH

**Status:** Local 21-line ad-hoc workflow vs upstream standard reusable-workflow call.
**Recommendation:** `--theirs` (adopt upstream standard).

```bash
cd /Users/kooshapari/CodeProjects/Phenotype/repos/GDK
git checkout --theirs .github/workflows/quality-gate.yml
git add .github/workflows/quality-gate.yml
git rebase --continue
```

---

## 4. argis-extensions divergence — HIGH

**Status:** 24-ahead / 11-behind. Manual conflicts in:
- `plugins/contentsafety/plugin.go`
- `plugins/contextfolding/folding.go`

**What I did:** Did not attempt auto-merge — semantic conflicts require user judgment.
**What user decides:** rebase vs merge; resolve plugin conflicts by hand.

```bash
cd /Users/kooshapari/CodeProjects/Phenotype/repos/argis-extensions
git fetch origin
git rebase origin/main
# Resolve conflicts:
$EDITOR plugins/contentsafety/plugin.go
$EDITOR plugins/contextfolding/folding.go
git add plugins/contentsafety/plugin.go plugins/contextfolding/folding.go
git rebase --continue
# Or, if rebase too painful:
# git rebase --abort && git merge origin/main
```

---

## 5. Tracera ARCHIVE/CONFIG/default delete — HIGH

**Status:** Pending delete needs direction.
**What user decides:**
- (a) which Tracera checkout to operate from: `Tracera-recovered` worktree or a fresh clone?
- (b) which base branch to target?

```bash
# Option A — operate in Tracera-recovered, target main
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

**Status:** Prior-session runbook referenced at `/repos/docs/security/OPENAI_KEY_REVOCATION_RUNBOOK.md` — **NOT FOUND** at re-verify time.
**What user decides:** re-verify if key still needs revocation; if so, regenerate runbook.

```bash
# Re-check
ls -la /Users/kooshapari/CodeProjects/Phenotype/repos/docs/security/ 2>&1
# Manual: visit https://platform.openai.com/api-keys and revoke any leaked key.
```

---

## 7. AgentMCP fictional README — RESOLVED (close)

**Status:** RESOLVED 2026-04-26. Tracked in refresh runbook.
**What user decides:** acknowledge closed; no action.

---

## 8. `/repos` canonical-subdir-inheritance — CRITICAL

**Status:** 19+ unpushed local commits; `/repos` subdir without its own `.git/` inherits parent remote (likely Tracera origin).
**Risk:** A naive `git push` would push these 19 commits to Tracera's remote.
**What user decides:** rebase-detach / push-as-tracera-fork-branch / keep local-only.

```bash
cd /Users/kooshapari/CodeProjects/Phenotype/repos

# Diagnose first
git remote -v
git log --oneline @{u}..HEAD | head -25

# Option A — keep local only (no push) [DEFAULT today; this runbook does NOT push]
echo "(no-op; commits remain local)"

# Option B — push as fork branch on Tracera (rename branch first)
git branch -m pre-extract/tracera-sprawl-commit-LOCAL
git push origin pre-extract/tracera-sprawl-commit-LOCAL

# Option C — detach + create a new dedicated repo
# (manual; create new GitHub repo, change remote, push)
```

---

## 9. agileplus-plugin-core 404 GitHub repo — CRITICAL

**Status:** AgilePlus `codex-local-boot` worktree blocked on missing `agileplus-plugin-core` dependency (404 on GitHub).
**What user decides:** re-create the repo / vendor the code / rebase off main.

```bash
# Option A — re-create empty repo (then push existing local code if any)
gh repo create KooshaPari/agileplus-plugin-core --public --description "AgilePlus plugin core"

# Option B — vendor in-tree
cd /Users/kooshapari/CodeProjects/Phenotype/repos/.worktrees/AgilePlus/chore/codex-local-boot
# Edit Cargo.toml: replace `agileplus-plugin-core = { git = ... }` with path-based dep
# then commit

# Option C — rebase off main (drop this worktree's pin)
git rebase origin/main
```

---

## 10. PhenoMCP follow-up — MEDIUM

**Status:** Already-pushed badge re-applied on PR #12 baseline. Dependabot reports 2 moderate (informational) advisories.
**What user decides:** verify advisories are non-blocking; close PR or address.

```bash
gh pr view 12 -R KooshaPari/PhenoMCP --json mergeable,statusCheckRollup
gh api /repos/KooshaPari/PhenoMCP/dependabot/alerts --jq '.[] | {severity, summary: .security_advisory.summary}'
```

---

## 11. Dependabot vitepress major bump — MEDIUM

**Status:** Closing 6 alerts requires vitepress 1→2 breaking-change migration. Needs separate PR for PhenoLang docs.
**What user decides:** approve scoped PR for vitepress 1→2 migration.

```bash
cd /Users/kooshapari/CodeProjects/Phenotype/repos/PhenoLang/docs
git checkout -b chore/vitepress-2-migration
pnpm add -D vitepress@^2 && pnpm install
pnpm docs:build  # fix breakage; see https://vitepress.dev/guide/migration-from-v1
git add . && git commit -m "chore(docs): migrate vitepress 1 -> 2 (closes 6 dependabot alerts)"
gh pr create --title "chore(docs): vitepress v1 -> v2 migration" --body "Closes 6 dependabot alerts."
```

---

## Deferred / Wait Days–Weeks

| Item | Why Deferred | Re-check |
|------|--------------|----------|
| #6 OpenAI key revocation runbook | File missing; prior session may have already revoked | Confirm next session |
| #7 AgentMCP fictional README | RESOLVED 2026-04-26 | Already closed |
| #11 vitepress 1→2 | Breaking-change migration; non-urgent | Within ~7 days |
| #10 PhenoMCP advisories | Informational moderates | Within ~7 days |

---

## Summary

- **Total items:** 11
- **CRITICAL:** 3 (items #1, #8, #9)
- **HIGH:** 4 (items #2, #3, #4, #5)
- **MEDIUM:** 2 (items #10, #11)
- **Deferred / Info:** 2 (items #6, #7)

**Disk budget at write-time:** 20Gi free.
**Push policy:** This runbook does **not** push (canonical-subdir-inheritance to Tracera). All push actions are user-gated.
