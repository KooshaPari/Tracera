# PhenoObservability — surrealdb / bincode 1.x advisory

**Date:** 2026-04-27
**Repo:** `repos/PhenoObservability`
**Advisory:** `bincode v1.3.3` — unmaintained (RUSTSEC). No safe upgrade on the 1.x line.
**Parent dependency chain:**

```
bincode 1.3.3
  ├── surrealdb 2.6.5
  │     └── phenotype-surrealdb 0.1.0  (workspace member)
  └── surrealdb-core 2.6.5
        └── surrealdb 2.6.5
```

## Investigation

- `crates/phenotype-surrealdb` is a **116-LOC stub crate** described as a "Fork of
  surrealdb/surrealdb with Pheno extensions", but it does **not** fork surrealdb —
  it depends on `surrealdb = "2.0"` from crates.io with default features off and
  only `protocol-ws` enabled.
- The crate exposes a `PhenoSurreal` struct with `new`, `store_skill`,
  `query_skills`-style stubs that **return synthetic records** without
  connecting to any SurrealDB instance. There is no real persistence,
  no MCP adapter, no skill schema — only placeholder shells.
- **Zero in-workspace consumers.** No other crate in the PhenoObservability
  workspace depends on `phenotype-surrealdb` (verified via grep across
  `Cargo.toml` and `*.rs`). Only references are the workspace member entry
  in the root `Cargo.toml` and the `release-registry.toml` listing.
- Latest crates.io `surrealdb` is `3.0.5`; the 3.x line is expected to have
  migrated to bincode 2.x (closes the advisory) but carries non-trivial API
  drift from 2.x.

## Options

### A. Remove the orphan crate (RECOMMENDED)

Delete `crates/phenotype-surrealdb` from the workspace and registry.

- **Scope:** ~3 line changes (workspace member list, release-registry entry,
  rm crate dir).
- **Risk:** None — no consumers, no real functionality lost.
- **Advisory impact:** Closes the bincode advisory completely (drops both
  surrealdb + surrealdb-core from the lockfile).
- **Reuse impact:** None. If SurrealDB integration is ever needed, build
  it fresh against surrealdb 3.x with a real schema and real connection.

### B. Bump to surrealdb 3.x

Replace `surrealdb = "2.0"` with `"3"` in `crates/phenotype-surrealdb/Cargo.toml`.

- **Scope:** 1-line bump, but the stub never actually calls into surrealdb,
  so the API drift surface is essentially zero. Build will likely succeed.
- **Risk:** Low for compilation, but spends effort upgrading a crate that
  does nothing useful. Defers the real architectural question.
- **Advisory impact:** Closes bincode 1.x advisory if 3.x has moved off it.

### C. Suppress

Reject. Advisory is genuine; suppression hides the orphan-crate problem.

## Recommendation

**Option A — remove the orphan crate.**

Auto-applicable: `git rm -r crates/phenotype-surrealdb`, drop the two-line
references in root `Cargo.toml` and `release-registry.toml`, regenerate
`Cargo.lock`. Closes the advisory and removes ~116 LOC of dead code in
one shot.

If a future workstream genuinely needs SurrealDB, scaffold a new crate
against 3.x with real persistence wiring rather than reviving this stub.
