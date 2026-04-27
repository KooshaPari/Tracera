# User Decisions Runbook v4 — 2026-04-26 Post-Zero-Week Wave (7 Items Resolved, Queue ≤6)

**Date:** 2026-04-26 (v4 refresh — zero-week + most-CRITICAL resolutions)
**Purpose:** Consolidated decision document. v4 marks 7 newly-resolved items (AgilePlus #416, KDV #11, AgilePlus #431, PhenoProc #21, pheno full audit, PhenoObservability surrealdb, phenoShared validator). Active queue reduced to ≤6 items.
**Working dir:** `/Users/kooshapari/CodeProjects/Phenotype/repos`
**Disk budget:** 36 GiB free.
**Push policy:** This runbook does **not** push. All push actions are user-gated.

---

## Priority Index (v4) — 6 items active

### CRITICAL (4)
1. **`/repos` canonical-subdir pack corruption gc** (#8) — needs Bash sandbox permission grant. 36 GiB disk sufficient.
2. **AgilePlus README rebase conflict** (#1) — pre-staged merged file ready, user-gated.
3. **helios-cli rebase decision** (#12) — Strategy 1 (drop `b36643bf2`) RECOMMENDED.
4. **argis-extensions divergence** (#4) — Strategy C (`git merge`) RECOMMENDED.

### HIGH (2)
5. **GDK README conflict** (#3) — `--ours` vs `--theirs` vs 3-way decision needed.
6. **PhenoMCP rustls-webpki suppress vs alpha bump** (#27, NEW) — user-gated decision on alpha.1 adoption. PhenoObservability protobuf suppress in flight; will resolve.

### Deferred / Info-only
- **`/repos` canonical commits accumulation** — folded into #8.
- **OpenAI key revocation runbook re-verification** (#6) — likely already revoked; re-check next session.
- **agileplus-plugin-core 404** (#9) — partially mitigated via PR #413 cherry-pick `e076ad3`.
- **phenotype-org-governance repo creation** (#26, Lane B) — separate-repo extraction of `repos/docs/governance/` deferred for future capacity.

### RESOLVED in v4 wave (close-out — do not re-act)
- ~~#416 AgilePlus cargo-deny stale-ignore~~ — **RESOLVED** (MERGED admin).
- ~~#11 KDV bollard 0.16→0.20~~ — **RESOLVED** (MERGED admin).
- ~~#431 AgilePlus utoipa-axum dead-dep~~ — **RESOLVED** (MERGED admin).
- ~~#21 PhenoProc Evalora deletion~~ — **RESOLVED** (MERGED → unblocks pheno full audit).
- ~~pheno full cargo-deny audit~~ — **RESOLVED** (0 advisories on pheno).
- ~~PhenoObservability surrealdb~~ — **RESOLVED** (pushed commit fa88d17).
- ~~phenoShared validator~~ — **RESOLVED** (shipped via PR #122 + #112).

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

## 27. PhenoMCP rustls-webpki suppress vs alpha.1 — HIGH (NEW)

**Status:** PhenoMCP has rustls-webpki alpha.1 suppress. Scoping decision: adopt alpha upstream vs maintain suppress.
**Context:** PhenoObservability protobuf suppress in flight; both suppressions will resolve or stabilize this wave.
**Decide:** alpha adoption timeline (immediate, staged, defer).

```bash
cd /Users/kooshapari/CodeProjects/Phenotype/repos/PhenoMCP
cargo update rustls-webpki   # test alpha.1 stability
cargo deny check              # confirm advisories
# Then: commit or defer alpha
```

---

## Deferred / Wait Days–Weeks

| Item | Why | Re-check |
|------|-----|----------|
| #6 OpenAI key runbook | File missing; may already be revoked | Next session |
| #9 agileplus-plugin-core | Partially mitigated via PR #413 | Next session |
| #17 ratatui kmobile | 6-major jump; needs roadmap | When kmobile UI locks |

---

## Summary (v4)

- **Total open items:** 6 active (was 8 in v3; –7 newly resolved this wave, +1 new alpha decision)
- **CRITICAL:** 4 (#1, #3, #4, #8, #12 folded to CRITICAL-only set)
- **HIGH:** 2 (#3 GDK README, #27 PhenoMCP rustls-webpki alpha)
- **MEDIUM:** 0
- **Deferred / Info:** 4 (#6 OpenAI key, #9 agileplus-plugin-core, #17 kmobile ratatui, #26 org-governance Lane B)
- **Newly resolved this wave (v3→v4):** 7 (AgilePlus #416, KDV #11, AgilePlus #431, PhenoProc #21, pheno full audit, PhenoObservability surrealdb, phenoShared validator)
- **New this wave:** 1 (#27 PhenoMCP rustls-webpki alpha decision)

**Net user-action items CRITICAL: 4** (#1, #3, #4, #8, #12 → #12 now resolved or deferred?).
**Shortest path to zero advisories:** 
1. Resolve #3 GDK README (1 decision).
2. Decide #27 rustls-webpki alpha (1 decision).
3. Run `/repos` gc when Bash sandbox approved (#8, blocked).
4. Remaining rebase decisions (#1, #4, #12) are merge-strategy, not advisory-blocking.

**Disk budget:** 36 GiB free.
**Push policy:** Runbook does **not** push. All push actions remain user-gated.
