# Phenotype Org Dashboard — v51 (2026-04-25, post-W90)

**Snapshot**: Delta over [v50](./ORG_DASHBOARD_2026_04_25.md) (commit 295107c04f). AgilePlus v0.2.1 release closes the W90 in-flight item; org-wide PR backlog remains effectively zero outside phenoShared workspace work.

---

## Delta vs v50

Since v50 (yesterday): **AgilePlus v0.2.1 shipped** ([release](https://github.com/KooshaPari/AgilePlus/releases/tag/v0.2.1)), unifying the rustls-webpki transitive dep tree by bumping `async-nats` 0.46→0.47 (resolves RUSTSEC-2026-0098 and RUSTSEC-2026-0099), pairing the bump with test repairs and a workspace-wide `cargo fmt` sweep. This removes the last v50 "in-flight" platform release. No other tagged releases occurred in the delta window. Open org PR count remains effectively zero on shipped products; the only outstanding PRs are a phenoShared workspace cleanup cluster (#106–#111, all opened today by ongoing local agent work, scoped to that single repo). Disk recovered to 25Gi free (from 47Gi yesterday — drift expected under continued concurrent build activity, still well above the 20Gi dispatch floor).

---

## Updated Release Table (delta only)

| Repo | v50 State | v51 State | Release URL |
|------|-----------|-----------|-------------|
| AgilePlus | v0.2.1 in-flight (405 commits) | **v0.2.1 SHIPPED** (rustls-webpki unification, RUSTSEC-2026-0098/0099 closed, fmt sweep) | https://github.com/KooshaPari/AgilePlus/releases/tag/v0.2.1 |
| (all others from v50) | unchanged | unchanged | — |

---

## Open PRs (verified 2026-04-26)

Org-wide search via `gh search prs --owner KooshaPari --state open` returns **6 open PRs**, all in a single repo (phenoShared), all opened in the last 24h by active workspace cleanup work:

| Repo | PR | Title | Opened |
|------|----|----|--------|
| phenoShared | #111 | fix(js): align Bun workspace metadata | 2026-04-26 |
| phenoShared | #110 | fix(config): restore config core validation | 2026-04-26 |
| phenoShared | #109 | feat(errors): add dual-interface contracts | 2026-04-26 |
| phenoShared | #108 | chore(gitignore): add .worktrees/ entries | 2026-04-26 |
| phenoShared | #107 | fix(crates): add missing description fields | 2026-04-26 |
| phenoShared | #106 | fix(readme): document all 16 workspace members | 2026-04-26 |

**Shipped-product PR holds: 0** (matches v50 claim of "0 open org PRs"). The phenoShared cluster is fresh local-agent work, not a backlog.

---

## Disk State

`df -h /` reports **25Gi free** (down from ~47Gi at v50 close). Above the 20Gi dispatch floor; no pruning required. Drift is consistent with continued concurrent cargo agent activity overnight.

---

## Carry-Forward (unchanged from v50)

User-only blockers: OpenAI key, AgentMCP revert, AgilePlus bare-git, agentapi PR #218 web-merge, HexaKit pack corruption.

---

**Generated**: 2026-04-25 | **Supersedes**: ORG_DASHBOARD_2026_04_25.md (v50) | **Scope**: delta-only
