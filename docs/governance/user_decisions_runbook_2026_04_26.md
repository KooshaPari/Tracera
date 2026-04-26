# User Decisions Runbook v2 — 2026-04-26 Autonomous Wave (Post Templates-Registry + Pheno Cleanup)

**Date:** 2026-04-26 (v2 refresh — post templates-registry-fix + post-pheno-cleanup wave)
**Purpose:** Consolidated decision document. v2 prunes resolved items and surfaces remaining user-gated work.
**Working dir:** `/Users/kooshapari/CodeProjects/Phenotype/repos`
**Disk budget:** 36 GiB free (gc on `/repos` now safe).
**Push policy:** This runbook does **not** push. All push actions are user-gated.

---

## Priority Index (v2)

### CRITICAL (only ~5 user-action items remain)
1. **`/repos` canonical-subdir pack corruption gc** (#8) — needs Bash sandbox permission grant for steps 3–7. 36 GiB disk sufficient.
2. **AgilePlus README rebase conflict** (#1) — pre-staged merged file ready, user-gated.
3. **helios-cli rebase decision** (#12) — Strategy 1 (drop `b36643bf2`) RECOMMENDED.
4. **argis-extensions divergence** (#4) — Strategy C (`git merge`) RECOMMENDED.
5. **GDK README conflict** (#3) — `--ours` vs `--theirs` vs 3-way decision needed.

### HIGH
6. **Tracera ARCHIVE/CONFIG/default delete** (#5) — base direction needed.
7. **agent-devops-setups non-FF** (#15) — rebase vs merge decision.
8. **helios-cli execpolicy-legacy delete `54fcdb00` held** (#16) — paired with #12.
9. **FocalPoint reqwest 0.11 → 0.12** (#20, NEW) — final 6 advisories; scoping in flight.
10. **KDV org-pages enable** (#21, NEW) — local scaffold pushed (commit `2426524`); needs `gh api ... pages -X POST`.
11. **5 product-domain Pages enables** (#22, NEW) — PolicyStack, FocalPoint, Tokn, HeliosLab, KDV.

### MEDIUM
12. **Dependabot vitepress 1 → 2 for PhenoLang docs** (#11)
13. **PhenoMCP follow-up — Dependabot advisories on PR #12 baseline** (#10)
14. **ratatui kmobile bump 0.24 → 0.30** (#17) — deferred, scope decision.
15. **Memory: tracera classification correction** (#18) — bookkeeping.
16. **Tier B repos audit follow-up** (#19)
17. **helioslab/tracera CF DNS 530** (#23, NEW) — origin healthy; CF edge issue.

### Deferred / Info-only
- **OpenAI key revocation runbook re-verification** (#6)
- **agileplus-plugin-core 404** (#9) — partially mitigated; AgilePlus PR #413 cherry-picked `e076ad3`.

### RESOLVED (close-out — do not re-act)
- ~~#2 BytePort untracked WIP~~ — RESOLVED 2026-04-26 (`c907e3a5` / `54247fc1` / `f7035985`).
- ~~#7 AgentMCP fictional README~~ — RESOLVED 2026-04-26 (remote PR #1 replaced).
- ~~Civis push conflict~~ — RESOLVED 2026-04-26 via PR #253 squash-merge + rand bump #254 + local rebase.
- ~~agent-imessage hook stopgap~~ — RESOLVED 2026-04-26 (`37c15cf89e`).
- ~~#13 pheno workspace orphan `phenotype-core`~~ — **RESOLVED 2026-04-26** via `e27ba2b` + `4e7fdad` + `1ef4d28` + `2721e0ef3` + `07e2e6a` (pushed via rebase).
- ~~#14 FocalPoint templates-registry refactor~~ — **RESOLVED 2026-04-26** via 2-line fix (commit `5c4030c`, pushed). Was 41% of org cargo-deny burden.
- ~~AgilePlus 2-ahead (partial)~~ — **PARTIALLY RESOLVED** via PR #413 (cherry-pick `e076ad3`); README rebase (#1) still user-gated.

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

**Status:** Conflict on README (and `quality-gate.yml` already covered upstream).
**Decide:** `--ours`, `--theirs`, or 3-way merge.

```bash
cd /Users/kooshapari/CodeProjects/Phenotype/repos/GDK
# Option A — keep local README
git checkout --ours README.md
# Option B — take upstream
git checkout --theirs README.md
# Option C — manual 3-way
$EDITOR README.md
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

## 5. Tracera ARCHIVE/CONFIG/default delete — HIGH

**Decide:** `Tracera-recovered` vs fresh clone, and which base.

```bash
# Option A — Tracera-recovered, target main
cd /Users/kooshapari/CodeProjects/Phenotype/repos/Tracera-recovered
git checkout main && git rm -r ARCHIVE/CONFIG/default
git commit -m "chore(tracera): drop ARCHIVE/CONFIG/default"
# Option B — fresh clone, feature branch
mkdir -p /tmp/tracera-clean && cd /tmp/tracera-clean
git clone git@github.com:KooshaPari/Tracera.git && cd Tracera
git checkout -b chore/drop-archive-default && git rm -r ARCHIVE/CONFIG/default
git commit -m "chore(tracera): drop ARCHIVE/CONFIG/default"
```

---

## 6. OpenAI key revocation — DEFERRED

```bash
ls -la /Users/kooshapari/CodeProjects/Phenotype/repos/docs/security/ 2>&1
# Manual: https://platform.openai.com/api-keys
```

---

## 8. `/repos` canonical-subdir pack corruption — CRITICAL

**Status:** 19+ local commits + pack corruption (10+ missing trees) + duplicate config commit `ddf7e59b`. Disk safe (36 GiB).
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

## 9. agileplus-plugin-core 404 — DEFERRED (partially mitigated)

Partial mitigation via AgilePlus PR #413 cherry-pick `e076ad3`. Full repo recreate / vendor / rebase still pending.

```bash
# Option A — recreate
gh repo create KooshaPari/agileplus-plugin-core --public --description "AgilePlus plugin core"
# Option B — vendor in-tree (edit Cargo.toml: replace git dep with path dep)
# Option C — rebase off main (drop pin)
```

---

## 10. PhenoMCP follow-up — MEDIUM

```bash
gh pr view 12 -R KooshaPari/PhenoMCP --json mergeable,statusCheckRollup
gh api /repos/KooshaPari/PhenoMCP/dependabot/alerts \
  --jq '.[] | {severity, summary: .security_advisory.summary}'
```

---

## 11. Dependabot vitepress 1 → 2 — MEDIUM

```bash
cd /Users/kooshapari/CodeProjects/Phenotype/repos/PhenoLang/docs
git checkout -b chore/vitepress-2-migration
pnpm add -D vitepress@^2 && pnpm install && pnpm docs:build
git add . && git commit -m "chore(docs): migrate vitepress 1 -> 2 (closes 6 dependabot alerts)"
gh pr create --title "chore(docs): vitepress v1 -> v2 migration" --body "Closes 6 dependabot alerts."
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

## 15. agent-devops-setups non-FF — HIGH

```bash
cd /Users/kooshapari/CodeProjects/Phenotype/repos/agent-devops-setups
git fetch origin
git log --oneline @{u}..HEAD && git log --oneline HEAD..@{u}
# Option A — rebase (recommended for atomic local commits)
git rebase origin/main
# Option B — merge
git merge origin/main
```

---

## 16. helios-cli execpolicy-legacy delete `54fcdb00` held — HIGH

```bash
cd /Users/kooshapari/CodeProjects/Phenotype/repos/helios-cli
git show --stat 54fcdb00
# Option A — keep delete, fold into rebase from #12
# Option B — revert delete: git revert 54fcdb00
# Option C — separate PR: git branch chore/drop-execpolicy-legacy 54fcdb00
```

---

## 17. ratatui kmobile bump 0.24 → 0.30 — MEDIUM (DEFERRED)

```bash
cd /Users/kooshapari/CodeProjects/Phenotype/repos/kmobile
rg "ratatui::" --stats | tail -5
git checkout -b chore/ratatui-0.30-migration
# Stepwise (0.24→0.26→0.28→0.30) with cargo check between, OR all-at-once.
```

---

## 18. Memory: tracera classification correction — MEDIUM

```bash
$EDITOR /Users/kooshapari/.claude/projects/-Users-kooshapari-CodeProjects-Phenotype-repos/memory/MEMORY.md
# Correct tracera classification (active vs archive, role).
```

---

## 19. Tier B repos audit follow-up — MEDIUM

```bash
ls /Users/kooshapari/CodeProjects/Phenotype/repos/docs/governance/ | grep -i tier
# Cross-ref ORG_DASHBOARD_v53.
```

---

## 20. FocalPoint reqwest 0.11 → 0.12 — HIGH (NEW)

**Status:** Final 6 cargo-deny advisories on FocalPoint. Scoping in flight.
**Decide:** approve scope (single PR / split per-crate / split per-advisory).

```bash
cd /Users/kooshapari/CodeProjects/Phenotype/repos/FocalPoint
rg -l "reqwest = " --type toml
# Bump in workspace root or per-crate; reqwest 0.12 changes default TLS, Body, blocking client.
cargo build --workspace && cargo test --workspace && cargo deny check
```

---

## 21. KDV org-pages enable — HIGH (NEW)

**Status:** Local scaffold pushed (commit `2426524`). Needs API call to enable Pages.
**User action:**

```bash
gh api repos/KooshaPari/KDesktopVirt/pages -X POST \
  -f source.branch=main -f source.path=/docs-dist
# Or via web: Settings → Pages → Source: branch main /docs-dist
```

---

## 22. 5 product-domain Pages enables — HIGH (NEW)

**Repos ready:** PolicyStack, FocalPoint, Tokn, HeliosLab, KDV. Each has built `docs-dist/` and CNAME staged.

```bash
for repo in PolicyStack FocalPoint Tokn HeliosLab KDesktopVirt; do
  gh api "repos/KooshaPari/$repo/pages" -X POST \
    -f source.branch=main -f source.path=/docs-dist
done
# CNAMEs (already staged): policystack.kooshapari.com, focalpoint.kooshapari.com,
# tokn.kooshapari.com, helioslab.kooshapari.com, kdv.kooshapari.com
```

---

## 23. helioslab/tracera CF DNS 530 — MEDIUM (NEW)

**Status:** Origin healthy; Cloudflare edge returns 530 (CF DNS misalignment fix in flight).
**Decide:** verify CF zone records for helioslab + tracera; remove stale A/CNAME entries; confirm proxy status.

```bash
# Verify origin is healthy:
curl -I https://kooshapari.github.io/HeliosLab/
curl -I https://kooshapari.github.io/Tracera/
# Then check CF dashboard: zones → kooshapari.com → DNS → helioslab/tracera records.
```

---

## Deferred / Wait Days–Weeks

| Item | Why | Re-check |
|------|-----|----------|
| #6 OpenAI key runbook | File missing; may already be revoked | Next session |
| #9 agileplus-plugin-core | Partially mitigated via #413 | Next session |
| #11 vitepress 1→2 | Breaking-change migration | ~7 days |
| #10 PhenoMCP advisories | Informational moderates | ~7 days |
| #17 ratatui kmobile | 6-major jump; needs roadmap | When kmobile UI locks |
| #19 Tier B repos | Aggregate cleanup | Next `/loop` wave |
| #23 CF DNS 530 | Edge-only; non-blocking | Same sitting |

---

## Summary (v2)

- **Total open items:** 17 (was 16; +5 new, –4 newly resolved)
- **CRITICAL:** 5 (#1, #3, #4, #8, #12)
- **HIGH:** 6 (#5, #15, #16, #20, #21, #22)
- **MEDIUM:** 6 (#10, #11, #17, #18, #19, #23)
- **Deferred / Info:** 2 (#6, #9)
- **Newly resolved this wave:** 3 (templates-registry #14, pheno orphan #13, AgilePlus #413 partial)

**Net user-action items still critical: ~5** (matches user note).
**Disk budget:** 36 GiB free.
**Push policy:** Runbook does **not** push. All push actions remain user-gated.
