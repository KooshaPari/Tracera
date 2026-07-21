# Bounded SQLx Pools Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace unbounded production SQLx startup connections with explicit pool limits and shared SQLite initialization without changing backend selection or API behavior.

**Architecture:** Add focused connection helpers in `crates/tracera-server/src/db.rs`. The helpers build `PgPoolOptions` and `SqlitePoolOptions`, apply finite limits/timeouts, and delegate SQLite pragmas to the existing WAL initializer. `main.rs` keeps scheme selection, migrations, and fatal diagnostics while calling the helpers.

**Tech Stack:** Rust, Tokio, SQLx 0.9, SQLite, PostgreSQL, Cargo tests.

---

### Task 1: Add failing helper contract tests

**Files:**
- Create: `crates/tracera-server/src/db.rs`
- Modify: `crates/tracera-server/src/main.rs` (module declaration only)

- [ ] **Step 1: Define test-visible constants and helper signatures**

Add `pub(crate) async fn connect_sqlite(url: &str) -> Result<SqlitePool, sqlx::Error>` and
`pub(crate) async fn connect_postgres(url: &str) -> Result<PgPool, sqlx::Error>` with tests
that connect to `sqlite::memory:` and assert `PRAGMA busy_timeout = 5000` and
`PRAGMA foreign_keys = 1`.

- [ ] **Step 2: Run the focused test**

Run: `CARGO_TARGET_DIR=/tmp/tracera-target-pools cargo test -p tracera-server db::tests --locked`

Expected: FAIL because the helper implementations are not present.

- [ ] **Step 3: Commit the test scaffold**

```bash
git add crates/tracera-server/src/db.rs crates/tracera-server/src/main.rs
git commit -m "test: specify bounded sqlx pool contracts"
```

### Task 2: Implement bounded connection helpers

**Files:**
- Modify: `crates/tracera-server/src/db.rs`
- Modify: `crates/tracera-server/src/queue/sqlite_init.rs`

- [ ] **Step 1: Configure finite pool policy**

Use `PgPoolOptions::new().max_connections(16).acquire_timeout(Duration::from_secs(5)).idle_timeout(Some(Duration::from_secs(600)))` and the equivalent `SqlitePoolOptions` with `max_connections(8)`. Use `connect_with` and preserve the existing SQLite pragma sequence.

- [ ] **Step 2: Run focused tests**

Run: `CARGO_TARGET_DIR=/tmp/tracera-target-pools cargo test -p tracera-server db::tests queue::sqlite_init::tests --locked`

Expected: PASS with SQLite pragmas asserted.

- [ ] **Step 3: Commit the helper implementation**

```bash
git add crates/tracera-server/src/db.rs crates/tracera-server/src/queue/sqlite_init.rs
git commit -m "fix: bound production sqlx pools"
```

### Task 3: Route production startup through helpers

**Files:**
- Modify: `crates/tracera-server/src/main.rs:436-480`
- Modify: `crates/tracera-server/src/db.rs`

- [ ] **Step 1: Replace raw connects**

Replace only production `PgPool::connect` and `SqlitePool::connect` calls with `db::connect_postgres` and `db::connect_sqlite`; retain existing error messages and migration order.

- [ ] **Step 2: Run server checks**

Run: `cargo fmt --all -- --check` and `CARGO_TARGET_DIR=/tmp/tracera-target-pools cargo clippy -p tracera-server --locked --all-targets -- -D warnings`.

Expected: both commands exit zero.

- [ ] **Step 3: Run targeted server tests**

Run: `CARGO_TARGET_DIR=/tmp/tracera-target-pools cargo test -p tracera-server api_router_rejects_malformed_json_and_oversized_bodies --locked`.

Expected: PASS.

- [ ] **Step 4: Commit integration**

```bash
git add crates/tracera-server/src/main.rs crates/tracera-server/src/db.rs
git commit -m "refactor: centralize tracera database startup"
```

### Task 4: Final verification and handoff

**Files:**
- Verify: `docs/superpowers/specs/2026-07-21-bounded-sqlx-pools-design.md`
- Verify: `crates/tracera-server/src/db.rs`

- [ ] **Step 1: Run complete relevant gates**

Run: `cargo fmt --all -- --check`; `CARGO_TARGET_DIR=/tmp/tracera-target-pools cargo clippy -p tracera-server --locked --all-targets -- -D warnings`; `CARGO_TARGET_DIR=/tmp/tracera-target-pools cargo test -p tracera-server --locked`.

Expected: all commands exit zero.

- [ ] **Step 2: Confirm no raw production connects remain**

Run: `rg -n 'PgPool::connect|SqlitePool::connect' crates/tracera-server/src/main.rs`.

Expected: no matches.

- [ ] **Step 3: Commit and push final change**

```bash
git add crates/tracera-server/src crates/tracera-server/Cargo.toml
git commit -m "harden: bound database connection lifecycle"
git push origin HEAD
```
