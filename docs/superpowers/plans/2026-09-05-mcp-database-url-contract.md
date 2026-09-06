# MCP Database URL Contract Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the MCP database URL documentation match the existing supported-scheme and bare-filename-rejection contract.

**Architecture:** `build_store_from_url` remains the single dispatcher in the
MCP binary. It will route only documented URL prefixes to the canonical
`tracera_server::datastore` factories; all other inputs take the existing
clear error branch. The regression test stays beside the existing binary URL
tests because it exercises the public binary configuration boundary.

**Tech Stack:** Rust, Tokio, SQLx, rmcp, Cargo.

> **2026-09-06 correction:** HEAD already rejects a bare `.db` value through
> its unsupported-input fallback. The original red-green premise in Tasks 1-2
> was disproved during execution and is superseded: do not add a test that
> falsely claims to introduce this existing behavior, and do not change URL
> dispatch. The executable scope is documentation reconciliation of all nearby
> contract strings, preservation of the existing binary tests, focused build
> checks, and configured non-demo SQLite runtime proof. The remainder of this
> document is retained as the original planning record.

---

### Task 1: Define the unsupported bare-path contract

**Files:**
- Modify: `crates/tracera-mcp/src/bin/mcp-server.rs:348-382`
- Test: `crates/tracera-mcp/src/bin/mcp-server.rs:348-382`

- [ ] **Step 1: Write the failing test**

Add this Tokio test after `sqlite_url_memory_spelling_builds_a_migrated_ready_store`:

```rust
#[tokio::test]
async fn bare_database_filename_is_rejected_as_an_unsupported_url() {
    let error = build_store_from_url("tracera.db")
        .await
        .expect_err("bare filenames are not documented database URLs");

    assert!(error.contains("unrecognized TRACERA_DB_URL scheme"), "{error}");
    assert!(error.contains("sqlite://"), "{error}");
}
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
cargo test --offline --locked -p tracera-mcp --bin tracera-mcp \
  bare_database_filename_is_rejected_as_an_unsupported_url -- --exact --nocapture
```

Expected: FAIL because the dispatcher currently accepts values ending in
`.db` and attempts a SQLite connection.

### Task 2: Restrict dispatch to documented URL schemes

**Files:**
- Modify: `crates/tracera-mcp/src/bin/mcp-server.rs:101-105`
- Test: `crates/tracera-mcp/src/bin/mcp-server.rs:348-395`

- [ ] **Step 1: Implement the minimal dispatcher change**

Replace:

```rust
if url.starts_with("sqlite://") || url.starts_with("sqlite:") || url.ends_with(".db") {
```

with:

```rust
if url.starts_with("sqlite://") || url.starts_with("sqlite:") {
```

Do not add path rewriting or a new URL parser.

- [ ] **Step 2: Run the focused regression test**

Run:

```bash
cargo test --offline --locked -p tracera-mcp --bin tracera-mcp \
  bare_database_filename_is_rejected_as_an_unsupported_url -- --exact --nocapture
```

Expected: PASS.

- [ ] **Step 3: Run the complete binary test module**

Run:

```bash
cargo test --offline --locked -p tracera-mcp --bin tracera-mcp -- --nocapture
```

Expected: PASS for both SQLite in-memory URL forms, bare-path rejection, and
PostgreSQL connector dispatch.

### Task 3: Reconcile comments and validate the configured runtime path

**Files:**
- Modify: `crates/tracera-mcp/src/bin/mcp-server.rs:90-112,139-143`
- Test: runtime JSON-RPC exchange; no source test file

- [ ] **Step 1: Update stale nearby documentation**

Ensure the `build_store_from_url` comment names the accepted prefixes exactly:

```rust
///   - `postgres://` or `postgresql://` → `PgStore`
///   - `sqlite:` or `sqlite://`         → `SqliteStore`
///   - anything else                    → error
```

Remove the obsolete DemoStore comment referring to PostgreSQL/SQLite Cargo
features being off; those feature gates no longer exist.

- [ ] **Step 2: Run focused package and library checks**

Run:

```bash
cargo check --offline --locked -p tracera-mcp --all-targets
cargo test --offline --locked -p tracera-mcp --lib -- --nocapture
git diff --check -- crates/tracera-mcp/src/bin/mcp-server.rs
```

Expected: package check succeeds, all MCP library tests pass, and the scoped
diff check is clean. Record warnings separately; do not suppress or reformat
unrelated workspace files.

- [ ] **Step 3: Exercise the non-demo SQLite MCP protocol**

Run a scripted stdio JSON-RPC exchange with `TRACERA_DEMO` unset and
`TRACERA_DB_URL=sqlite://:memory:`. Send `initialize`,
`notifications/initialized`, and `tools/list`; then call safe
`search {"query":"__contract_absent__","limit":1}`.

Expected: process exits 0 after the complete exchange, negotiates protocol
`2025-06-18`, exposes 15 tools, and returns `isError:false` with no matches.

### Task 4: Review and handoff

**Files:**
- Review: `crates/tracera-mcp/src/bin/mcp-server.rs`
- Review: `docs/superpowers/specs/2026-09-05-mcp-database-url-contract-design.md`
- Review: `docs/superpowers/plans/2026-09-05-mcp-database-url-contract.md`

- [ ] **Step 1: Review scope and remaining gates**

Verify the diff is limited to the documented URL contract, tests, comments,
and these planning records. State separately that live PostgreSQL, file-backed
SQLite persistence, whole-workspace strict lint/format, hosted CI, commit, and
push remain separate gates.

- [ ] **Step 2: Commit only with explicit authorization**

When authorized, stage only the intended paths and create a conventional
commit. Do not include unrelated dirty-worktree changes.
