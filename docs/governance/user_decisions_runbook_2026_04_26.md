# User Decisions Runbook v3 — 2026-04-26 Autonomous Wave (Post W-96 Cleanup)

**Date:** 2026-04-26 (v3 refresh — post W-96 dependabot/cargo-deny cleanup wave)
**Purpose:** Consolidated decision document. v3 prunes 6 newly-resolved items and adds 4 new in-flight items.
**Working dir:** `/Users/kooshapari/CodeProjects/Phenotype/repos`
**Disk budget:** 36 GiB free.
**Push policy:** This runbook does **not** push. All push actions are user-gated.

---

## Priority Index (v3) — 8 items active

### CRITICAL (5)
1. **`/repos` canonical-subdir pack corruption gc** (#8) — needs Bash sandbox permission grant. 36 GiB disk sufficient.
2. **AgilePlus README rebase conflict** (#1) — pre-staged merged file ready, user-gated.
3. **helios-cli rebase decision** (#12) — Strategy 1 (drop `b36643bf2`) RECOMMENDED.
4. **argis-extensions divergence** (#4) — Strategy C (`git merge`) RECOMMENDED.
5. **GDK README conflict** (#3) — `--ours` vs `--theirs` vs 3-way decision needed.

### HIGH (3)
6. **AgilePlus utoipa-axum removal** (#24, NEW) — in flight (commit `ae42527736`); scoping decision on dep removal vs version pin.
7. **AgilePlus PR #416** (#25, NEW) — cargo-deny stale-ignore cleanup, OPEN, awaiting merge.
8. **phenotype-org-governance repo creation** (#26, Lane B) — separate-repo extraction of `repos/docs/governance/` for Lane B governance hub.

### Deferred / Info-only
- **`/repos` canonical commits accumulation** — folded into #8.
- **OpenAI key revocation runbook re-verification** (#6) — likely already revoked; re-check next session.
- **agileplus-plugin-core 404** (#9) — partially mitigated via PR #413 cherry-pick `e076ad3`.

### RESOLVED in v3 wave (close-out — do not re-act)
- ~~#10 PhenoMCP advisories~~ — **RESOLVED 2026-04-26** (no-op; 0 open alerts; the 2 referenced were github-actions PRs all merged).
- ~~#14 FocalPoint templates-registry refactor~~ — **RESOLVED 2026-04-26** (commit `5c4030c`, 13 advisories cleared).
- ~~#20 FocalPoint reqwest 0.11→0.12~~ — **RESOLVED 2026-04-26** (commit `6a601b1`, dep hygiene complete).
- ~~KDV bollard cluster~~ — **RESOLVED 2026-04-26** (commit `15835a2`, PR #11 OPEN).
- ~~eyetracker uniffi cluster~~ — **RESOLVED 2026-04-26** (commit `eedfd49`).
- ~~PhenoObservability surrealdb~~ — **RESOLVED 2026-04-26** (commit `ba25d1e`, dead-dep removal; scoping at `934467e7de`).

### RESOLVED in prior waves (retained for audit)
- ~~#2 BytePort untracked WIP~~ — RESOLVED 2026-04-26 (`c907e3a5` / `54247fc1` / `f7035985`).
- ~~#7 AgentMCP fictional README~~ — RESOLVED 2026-04-26 (remote PR #1 replaced).
- ~~Civis push conflict~~ — RESOLVED 2026-04-26 via PR #253 squash-merge + #254 + local rebase.
- ~~agent-imessage hook stopgap~~ — RESOLVED 2026-04-26 (`37c15cf89e`).
- ~~#13 pheno workspace orphan `phenotype-core`~~ — RESOLVED 2026-04-26 via 5-commit rebase.
- ~~#5 Tracera ARCHIVE/CONFIG/default~~ — folded into broader Tracera classification work; no active blocker.
- ~~#11 PhenoLang vitepress 1→2~~ — superseded by docsite ecosystem migration; not user-gated.
- ~~#15 agent-devops-setups non-FF~~ — superseded by org-wide rebase strategy.
- ~~#16 helios-cli execpolicy-legacy delete~~ — folded into #12.
- ~~#17 ratatui kmobile bump~~ — deferred until kmobile UI locks (still deferred, not user-gated).
- ~~#18 tracera memory classification~~ — bookkeeping completed.
- ~~#19 Tier B repos audit~~ — folded into ORG_DASHBOARD_v53 and per-loop sweeps.
- ~~#21 KDV org-pages enable~~ — completed.
- ~~#22 5 product-domain Pages enables~~ — completed across W-90+ wave.
- ~~#23 helioslab/tracera CF DNS 530~~ — completed via CF zone fix.

---

## 1. AgilePlus README rebase conflict — CRITICAL

**Status:** Pre-staged merged file at `proposals/push_conflict_2026_04_26/AgilePlus_README.merged.md`.
**Decide:** `merge` / `ours` / `theirs`.

```bash
cd /Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus
# Option A (recommended)
cp ../proposals/push_conflict_2026_04_26/AgilePlus_README.merged.md README.md
git add README.md && git rebase --continue
# Option B — keep ours
git checkout --ours README.md && git add README.md && git rebase --continue
# Option C — take upstream
git checkout --theirs README.md && git add README.md && git rebase --continue
```

---

## 3. GDK README conflict — CRITICAL

```bash
cd /Users/kooshapari/CodeProjects/Phenotype/repos/GDK
git checkout --ours README.md   # or --theirs, or 3-way
git add README.md && git rebase --continue
```

---

## 4. argis-extensions divergence — CRITICAL

**Status:** 24-ahead / 11-behind. Manual conflicts in `plugins/contentsafety/plugin.go`, `plugins/contextfolding/folding.go`.
**Recommendation: Strategy C — `git merge origin/main`.**

```bash
cd /Users/kooshapari/CodeProjects/Phenotype/repos/argis-extensions
git fetch origin && git merge origin/main
$EDITOR plugins/contentsafety/plugin.go plugins/contextfolding/folding.go
git add plugins/contentsafety/plugin.go plugins/contextfolding/folding.go && git commit
```

---

## 8. `/repos` canonical-subdir pack corruption — CRITICAL

**Status:** 19+ local commits + pack corruption (10+ missing trees) + duplicate config commit `ddf7e59b` + ongoing canonical-commits accumulation. Disk safe (36 GiB).
**Blocker:** Bash sandbox permission grant for git internals (umbrella for pack-gc) — user-gated.

```bash
cd /Users/kooshapari/CodeProjects/Phenotype/repos
git status --short --branch
git remote -v   # subdir inherits parent remote → Tracera origin (do NOT push there)
git gc --aggressive --prune=now
git rebase -i <commit-before-ddf7e59b>   # mark ddf7e59b as `drop`
git fsck --full
# Push decision (USER-GATED): keep local / fork branch / detach to dedicated repo
```

---

## 12. helios-cli rebase decision — CRITICAL

**Recommendation: Strategy 1 — drop `b36643bf2`** during interactive rebase.

```bash
cd /Users/kooshapari/CodeProjects/Phenotype/repos/helios-cli
git fetch origin && git rebase -i origin/main
# Editor: change `pick b36643bf2 ...` to `drop b36643bf2 ...`
git status   # verify clean; do NOT push without user confirmation
```

---

## 24. AgilePlus utoipa-axum removal — HIGH (NEW)

**Status:** In flight (commit `ae42527736`). Scoping decision: full removal vs pin to compatible version.
**Decide:** approve removal scope; verify no downstream OpenAPI generators depend on it.

```bash
cd /Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus
git show ae42527736 --stat
rg "utoipa_axum|utoipa-axum" --type rust --type toml
cargo build --workspace && cargo test --workspace && cargo deny check
```

---

## 25. AgilePlus PR #416 — HIGH (NEW)

**Status:** OPEN. Cargo-deny stale-ignore cleanup. Awaiting user merge.

```bash
gh pr view 416 -R KooshaPari/AgilePlus --json mergeable,statusCheckRollup
gh pr merge 416 -R KooshaPari/AgilePlus --admin --squash   # CI billing-blocked
```

---

## 26. phenotype-org-governance repo (Lane B) — HIGH (NEW)

**Status:** Lane B extraction proposed — split `repos/docs/governance/` into a dedicated repo.
**Decide:** repo name (`phenotype-org-governance` vs `phenotype-governance`), visibility (public vs internal), and migration order (extract-then-symlink vs subtree).

```bash
gh repo create KooshaPari/phenotype-org-governance --public \
  --description "Phenotype org-wide governance, policies, runbooks"
# Then: git subtree split / git filter-repo to extract repos/docs/governance/ history
```

---

## Deferred / Wait Days–Weeks

| Item | Why | Re-check |
|------|-----|----------|
| #6 OpenAI key runbook | File missing; may already be revoked | Next session |
| #9 agileplus-plugin-core | Partially mitigated via PR #413 | Next session |
| #17 ratatui kmobile | 6-major jump; needs roadmap | When kmobile UI locks |

---

## Summary (v3)

- **Total open items:** 8 (was 17 in v2; –6 newly resolved, –7 prior-wave folded, +4 new)
- **CRITICAL:** 5 (#1, #3, #4, #8, #12)
- **HIGH:** 3 (#24, #25, #26)
- **MEDIUM:** 0 (all rolled up or resolved)
- **Deferred / Info:** 3 (#6, #9, #17)
- **Newly resolved this wave (v2→v3):** 6 (#10 PhenoMCP, #14 templates-registry already-resolved-confirm, #20 FocalPoint reqwest, KDV bollard, eyetracker uniffi, PhenoObservability surrealdb)
- **New this wave:** 4 (#24 utoipa-axum, #25 PR #416, #26 phenotype-org-governance, plus PhenoObservability surrealdb scoping retained as resolved)

**Net user-action items still critical: 5** (unchanged set: #1, #3, #4, #8, #12).
**Disk budget:** 36 GiB free.
**Push policy:** Runbook does **not** push. All push actions remain user-gated.
