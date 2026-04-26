# Phenotype Org Dashboard — v52 (2026-04-26, post-v51)

**Snapshot**: Delta over [v51](./ORG_DASHBOARD_v51_2026_04_25.md) (commit 232f4da173). Major doc/audit and build-unblock day. Three RED READMEs rewritten honest, ~9.1k phantom links eliminated, badge coverage jumped 50%→78.5%, FocalPoint Rust workspace returned to GREEN, and `phenotype-observably-macros` 0.1.1 now hard-fails non-Result return types at compile time.

---

## What Changed Since v51

Since v51 close, the org executed a high-leverage docs-and-unblocks day. AgilePlus v0.2.1 GitHub release was published (closing the v51 in-flight tag-but-no-release gap). `phenotype-observably-macros` 0.1.1 landed compile_error emission for non-Result return types on `PhenoObservability` (commit 6e23edb), eliminating a recurring W-75 misuse class. FocalPoint Rust workspace `cargo check` returned to GREEN (commit 2f7299f) via tracing dep fix + `SqliteMigration` trait + `async_instrumented` cleanup on non-Result fns. AgilePlus `codex-local-boot` worktree shed 21 orphan workspace members (commit 94f2475); remaining blocker is the private/missing `agileplus-plugin-core` git dep. cliproxyapi-plusplus had 4 sdk/auth files forward-fixed (372aa1a4, 60b2abf8, 8c27f1de, ced413ac) with merge archeology pinning bad squash adef5c2f as root cause of the full 94-error count. On the docs side, the org-wide broken-link total fell from 17,418 to ~8,300 (-9,105) via a single fix to `thegent/scripts/generate-doc-index.sh` (commit 5ddb89fdd). LEGACY README badge coverage advanced 50%→78.5% across rounds 32+33+34 (~31 repos badged); 11/12 round-33 commits pushed (PhenoMCP intentionally skipped pending PR #12 authoritative rewrite). Three RED READMEs were rewritten honestly: AgilePlus (a59c681), BytePort (f564ac60, with credential `ILOVEKUSHPAPI` scrubbed), and GDK (397c9f4). cargo-deny W-91 snapshot dropped 50→23 advisories (-54%) across 4 audited repos (FocalPoint -23, AgilePlus -7).

---

## Releases Shipped Today

| Repo | Tag | URL / Commit |
|------|-----|--------------|
| AgilePlus | v0.2.1 (GitHub release published) | https://github.com/KooshaPari/AgilePlus/releases/tag/v0.2.1 |
| PhenoObservability (`phenotype-observably-macros`) | 0.1.1 | commit 6e23edb (non-Result return → compile_error) |

---

## Updated Metrics

| Metric | v51 | v52 | Delta |
|--------|-----|-----|-------|
| Org-wide broken doc links | 17,418 | ~8,300 | **-9,105 (-52%)** |
| LEGACY README badge coverage | 50% | 78.5% | **+28.5 pp** |
| RED READMEs (honest rewrite) | — | 3 (AgilePlus, BytePort, GDK) | +3 |
| cargo-deny advisories (4 audited repos) | 50 | 23 | **-27 (-54%)** |
| FocalPoint Rust `cargo check` | RED | **GREEN** | unblocked |
| `phenotype-observably-macros` | 0.1.0 | 0.1.1 | compile_error gate live |
| Open org PRs (shipped products) | 0 | 0 | unchanged |
| Open phenoShared cluster PRs | 6 (#106–#111) | tracked separately | — |

---

## Build / Unblock Status

| Stream | State | Notes |
|--------|-------|-------|
| FocalPoint Rust workspace | GREEN | tracing + SqliteMigration + async_instrumented fixes (2f7299f) |
| AgilePlus codex-local-boot | YELLOW | 21 orphan members removed; blocked on private `agileplus-plugin-core` git dep |
| cliproxyapi-plusplus | YELLOW | 4/N sdk+auth files fixed; forward-fix steps 1+2 in flight (will clear 60+ errors) |
| PhenoMCP README | HOLD | round-33 push skipped pending PR #12 authoritative rewrite |

---

## Open User-Only Blockers

These items require user (Koosha) action and cannot be resolved by agents alone:

| # | Item | Detail |
|---|------|--------|
| 1 | **FocalPoint Xcode build** | rustc 1.93.1 jobserver bug + iOS deployment-target mismatch. `zstd-sys` missing `___chkstk_darwin`; ld warns iOS 26.0 objects vs `ios-min=10.0`. Fix agent in flight; user toolchain pin / Xcode min-target update may be needed. |
| 2 | **OpenAI key revocation** | Carry-over from prior session runbook. Key suspected exposed; revoke + rotate. |
| 3 | **AgentMCP fictional README revert** | Carry-over. Prior PR wrote fiction (verify-then-write violation); needs revert + ground-truthed rewrite. |
| 4 | **cliproxyapi forward-fix** | Steps 1+2 in flight via agent; user merge / review needed once PRs land. |

---

## Carry-Forward (unchanged)

phenoShared workspace cleanup cluster (#106–#111) remains scoped local-agent work, not a backlog. HexaKit pack corruption and agentapi PR #218 web-merge unchanged from v51.

---

**Generated**: 2026-04-26 | **Supersedes**: ORG_DASHBOARD_v51_2026_04_25.md | **Scope**: delta-only
