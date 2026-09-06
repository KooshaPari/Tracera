# MCP storage boundary and rmcp adapter evidence

Date: 2026-09-05 UTC. Worktree: `/Users/kooshapari/CodeProjects/Phenotype/repos/Tracera-wtrees/workos-router-state-20260905`. Branch `fix/tracera-workos-router-state-20260905`; HEAD `79436a75e25d7d4db9be95a8873f7a596a114070` plus preserved prior changes and this uncommitted slice.

## Result

- `cargo check --offline --locked -p tracera-server --lib`: **exit 0** after adding the storage-only library.
- `cargo test --offline --locked -p tracera-mcp --lib`: **exit 0, 31 passed, 0 failed, 0 ignored, 0 filtered**. Final session 66437 complete.
- `cargo check --offline --locked -p tracera-mcp`: **exit 101**, binary-only unresolved `tracing_subscriber` import/module at `src/bin/mcp-server.rs:33,42`. Library compiled. Session 46747 complete; captured wrapper printed inner Cargo exit 101 even though diagnostic wrapper itself returned 0.
- `git diff --check`: exit 0.

No live command handles remain. This is not production MCP datastore wiring, live protocol negotiation, full workspace checks, hosted CI, or release proof.

## RED and compiler delta

Before implementation:

```sh
cargo check --offline --locked -p tracera-server --lib
cargo test --offline --locked -p tracera-mcp --lib tests::tool_error_to_mcp_error_maps_codes -- --exact
```

Both exited **101**. Server reported no library targets. MCP reported 16 compilation errors: missing `tracera_server` library, obsolete rmcp macro/model/method paths, missing direct sha2 dependency, local anyhow function invoked as a macro, and generated associated tool routers called as module functions. No test executed: this was compilation RED, not a runtime assertion failure.

First adapter pass made server lib check green and reduced MCP errors to four: `ToolRouter::merge` mutates in place, protocol constant needs `V_2025_06_18`, supported-version Cow must own the temporary vector, and one write helper still needed typed ErrorCode. Fixing these yielded 30/30 existing library tests passing.

Independent reviewer requested actual router registration evidence beyond manifest constants. Added `aggregated_router_exposes_every_declared_tool`, initially compilation RED (missing shared `build_tool_router` helper). Extracted the constructor's unchanged router assembly into that private helper; both constructor and test now use it. Test compares actual `list_all()` output to the full 15-tool manifest and checks count, so lost registration or duplicate output is detected. Final library run: **31/31 pass**.

## Scoped changes

1. New `crates/tracera-server/src/lib.rs` exports only existing `pub mod store`; no duplicated trait or concrete datastore export.
2. `crates/tracera-mcp/Cargo.toml` adds `sha2 = { workspace = true }`. Lockfile changes by one dependency edge, `"sha2 0.11.0"`, in the existing tracera-mcp package. That version was already present; no package version upgrades or downloads.
3. MCP adapter imports `tool_handler` from rmcp root; uses `ErrorCode`, `ContentBlock`, and current metadata constructors. Numeric error values remain unchanged.
4. Uses associated generated router functions and in-place merges for all four tool groups. Shared assembly is checked against actual 15-tool registration.
5. Uses `get_info` and `supported_protocol_versions` for pinned revision `2025-06-18`, tools-only capabilities, retained server metadata/instructions. The SDK's default `initialize` remains responsible for peer metadata registration and protocol negotiation. This replaces the old incorrect signature and unsupported info/version methods.
6. Calls existing `anyhow_lite::anyhow(format!(...))` function, preserving transport-error text without adding anyhow.
7. `tools/write.rs` wraps the existing numeric serialization-error code and removes its unused ko import.

No backend feature branches or placeholder datastore wiring were changed. The existing binary's undeclared `postgres`/`sqlite` cfg warnings and missing `tracing_subscriber` dependency are reported for a later unit. Non-test library warns about currently unused `ko`; existing WorkOS import and macOS native-linker warnings also remain. Passing tests did not produce pristine warning-free output.

## Final input hashes

| File | SHA-256 |
|---|---|
| crates/tracera-server/src/lib.rs | dcba30ac34da526d4f6cdd20e1aea8337105a9b71bae92bf36eb66b1b8532e00 |
| crates/tracera-mcp/Cargo.toml | 4d1e56c1e8b048451953d0c1260dd8d8309d1606d6e3284ffe9b46bf76c76d0b |
| crates/tracera-mcp/src/lib.rs | ffc7fcbe75ac21657fc802cb9ca2a3246e4b7cfa2bf0fdd66511aa89d13ddb9e |
| crates/tracera-mcp/src/tools/write.rs | bc2435235466694e8c8697f15e06bac9b6692f1bb3c8d3415386209d06b737a2 |
| Cargo.lock | 5621a7f1fe321349b0aa62c5ef4337f25d5e2f36c6ee682b8d15a4947c5b7f92 |

Original approved staged router diff remains SHA-256 `b9f64dfbf960cc31cfa52df405fc8e1868578082dd2d2659eba0df07c1e783cd`. Events, Atlas, hook, prior mechanical formatting, and canonical dirty work remain preserved. No index changes, commits, push, merge, service restart, or external auth/ingestion occurred. Semantic patch frozen for independent review.

## Follow-up: binary tracing dependency, 2026-09-06 00:33 UTC

Fresh RED: `cargo check --offline --locked -p tracera-mcp` exited 101 (session 88421) with E0432/E0433 for `tracing_subscriber` at binary lines 33/42. Workspace `Cargo.toml:23` already declares `tracing-subscriber = { version = "0.3", features = ["env-filter"] }`; lockfile package is already version **0.3.23**.

Added only `tracing-subscriber = { workspace = true }` to the MCP manifest and `"tracing-subscriber"` to that package's lock dependency list. This slice adds no package version or upgrade. The cumulative lock diff contains exactly two dependency links: the earlier `sha2 0.11.0` link and this existing tracing-subscriber link.

Fresh GREEN:

- `cargo check --offline --locked -p tracera-mcp`: **exit 0**, including library and binary (session 29723).
- `cargo test --offline --locked -p tracera-mcp --lib`: **exit 0, 31 passed, 0 failed, 0 ignored** (session 28297).
- `git diff --check`: exit 0. Staged router diff remains the same approved hash.

There is no next hard binary compilation error in this checked configuration. Existing warnings remain: unused WorkOS ProvisionOutcome import, unused library ko function, unused binary imports, undeclared `postgres`/`sqlite` cfg branches, and macOS linker warnings. No backend feature wiring or datastore behavior was changed; warnings-as-errors, full workspace checks, and production datastore/protocol verification remain separate gates. No live process handles, commit, push, or merge.

Updated SHA-256: MCP Cargo.toml `8ba7131ec6577a3ba22fcbf16e924dd1ce5bc3ca79b569caff6b600db7cfade3`; Cargo.lock `39bb83ce629b725f7fcb92fbd549c20af247a5b1e4d56a5931ebd123c9720f54`.

## Datastore selection gate inspection, 2026-09-06 01:00 UTC

Read-only source inspection and smallest controlled startup check; no source or dependency changes.

Run with `TRACERA_DEMO` removed from the subprocess environment, `TRACERA_DB_URL=sqlite://:memory:`, and stdin closed:

```sh
cargo run --offline --locked -p tracera-mcp --bin tracera-mcp
```

Cargo built successfully; **binary exit 2**. Exact diagnostic:

```text
fatal: failed to construct store: unrecognized TRACERA_DB_URL scheme `sqlite://:memory:`; expected `postgres://…` or `sqlite://…` (or set TRACERA_DEMO=1)
```

Session 12673 completed. The diagnostic wrapper returned 0 while explicitly reporting child exit 2; this is not a successful application startup. No database connection was attempted: both actual branches are compiled out, and the in-memory URL names no disk database.

Independent feature validation:

```sh
cargo check --offline --locked -p tracera-mcp --features sqlite
```

Exit **101**: `the package 'tracera-mcp' does not contain this feature: sqlite`.

Root cause chain:

```text
TRACERA_DEMO unset + TRACERA_DB_URL supplied
  -> build_store_from_url
  -> postgres/sqlite cfg branches omitted (no declared features)
  -> unconditional unrecognized-scheme error
  -> main exits 2 before starting MCP transport
```

Additional source blockers to a complete repair: the guarded code calls nonexistent `tracera_mcp::stores::{pg,sqlite}` exports and assumes `connect(url)` constructors; actual `tracera-server` concrete types provide `PgStore::new(PgPool)` and `SqliteStore::new(SqlitePool)`. The newly added server library deliberately exports only `store`. Merely declaring features is therefore insufficient: a bounded follow-up must wire concrete modules, pool creation and required migrations, validate URL dispatch, then prove a real SQLite storage round-trip. No such changes were made in this inspection. DemoStore remains a non-persistent placeholder; its availability does not satisfy this gate. No live processes, commit, or push.
