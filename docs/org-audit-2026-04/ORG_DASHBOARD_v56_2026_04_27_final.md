# ORG_DASHBOARD v56 — Loop-Resumed-Restart Wave Final

**Date:** 2026-04-27
**Predecessor:** v55 final-final addendum (commit `4f6501d7b5`)
**Wave:** Loop-Resumed-Restart (W-95 → W-96 transition)

---

## Headline

**If KDV + eyetracker land cleanly: org-wide cargo-deny 50 → 2 (-96%).**

The W-95 sweep closed FocalPoint's 5→0 trio (prometheus + starlark suppress + uniffi suppress). With KDV bollard (-4) and eyetracker uniffi 0.27→0.31 (-2) in flight, the next snapshot drops from 8 to 2 — a 96% reduction off the v55 baseline of 50.

---

## Counters (W-95 final → W-96 projected)

| Metric                          | v55 baseline | v55 addendum | W-95 snapshot | W-96 projected |
|---------------------------------|--------------|--------------|---------------|----------------|
| cargo-deny advisories (org)     | 50           | 13           | **8**         | **2** (-96%)   |
| FocalPoint advisories           | 5            | 5            | **0**         | 0              |
| KDV advisories                  | 4            | 4            | 4             | **0**          |
| eyetracker advisories           | 2            | 2            | 2             | **0**          |
| AgilePlus advisories            | 1            | 1            | 1             | 1 (utoipa-axum)|
| PhenoObservability advisories   | 1            | 1            | 1             | 1 (surrealdb)  |
| Open W-95 cluster scopings      | 4            | 4            | **4 done**    | —              |

---

## PRs Today (4)

| Repo               | PR    | Title                                          | State   |
|--------------------|-------|------------------------------------------------|---------|
| Civis              | #253  | (W-95 cluster scoping landing)                 | MERGED  |
| AgilePlus          | #413  | (W-95 cargo-deny baseline cleanup)             | MERGED  |
| PhenoProc          | #21   | Evalora deletion                               | OPEN    |
| AgilePlus          | #416  | cargo-deny stale-ignore cleanup                | OPEN    |

---

## W-95 Cluster Scopings (all 4 done)

- **KDV** — bollard manual bump scoped, apply pending (-4 cargo-deny).
- **eyetracker** — uniffi 0.27 → 0.31 scoped, apply pending (-2 cargo-deny).
- **PhenoObservability** — surrealdb advisory scoped, suppress vs bump decision pending.
- **AgilePlus** — utoipa-axum advisory scoped, suppress staged in #416.

---

## Reclassifications

- **Pack-corruption "regression"** → reclassified as `git fsck` reporting artifact (line-count noise, not actual missing trees). See `feedback_fsck_line_count_artifact.md`.

---

## Memory Codification (14 entries today)

Fork-aware README, scoping verify-then-fix, fsck line-count artifact, agent-imessage hook, sandbox path-scoping, AgilePlus canonical-bare distinction, squash-merge ghost commits, task-oriented status framing, plus 6 supporting entries.

---

## Tomorrow Priorities (ordered)

### 1. Lane C — W-96 sweep (apply scoped fixes)
- KDV bollard apply (-4)
- eyetracker uniffi 0.27 → 0.31 apply (-2)
- AgilePlus utoipa-axum (#416 land)
- PhenoObservability surrealdb (decide + apply)
- **Target:** cargo-deny 8 → 2

### 2. Lane B — phenotype-org-governance repo creation
Prevents `/repos` canonical accumulation of governance docs. Extracts `repos/docs/governance/` to a dedicated repo.

### 3. Lane A — pack-gc on `/repos` canonical
Requires sandbox permission grant. Defer until B is unblocked.

---

## Provenance

- v55 final-final addendum: commit `4f6501d7b5`
- W-95 sweep commits: see `repos/docs/org-audit-2026-04/unmaintained_cluster_audit_2026_04_27.md`
- Memory entries: `~/.claude/projects/-Users-kooshapari-CodeProjects-Phenotype-repos/memory/`
