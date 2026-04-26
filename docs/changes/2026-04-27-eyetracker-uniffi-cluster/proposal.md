# eyetracker — uniffi 0.27 advisory cluster (bincode + paste)

**Date:** 2026-04-27
**Repo:** `repos/eyetracker`
**Origin:** cargo-deny W-95 / W-92 categorization
**Status:** PROPOSAL — investigation complete, recommendation: BUMP

## Advisories

| ID | Crate | Class | Parent chain |
|----|-------|-------|--------------|
| RUSTSEC-2024-0436 | `paste 1.0.15` | unmaintained | `paste` <- `uniffi_bindgen 0.27.3`, `uniffi_core 0.27.3` <- `uniffi 0.27` <- `eyetracker-ffi` |
| RUSTSEC-2025-0141 | `bincode 1.x` | unmaintained | (transitive via uniffi 0.27 toolchain) |

Both advisories are "unmaintained" class (not vuln). Solution per advisory: "No safe upgrade is available" within the 0.27 line — must bump uniffi.

## Direct dependency

`crates/eyetracker-ffi/Cargo.toml`:

```
uniffi = { version = "0.27", features = ["bindgen"] }       # [dependencies]
uniffi = { version = "0.27", features = ["build"] }         # [build-dependencies]
uniffi = { version = "0.27", features = ["cli", "bindgen"] }# [dev-dependencies]
```

Single direct consumer: `eyetracker-ffi`. No other workspace member references uniffi.

Latest crates.io: `uniffi 0.31.1` (confirmed via `cargo search`).

## Downstream Swift / iOS consumer? **NO**

Investigation:

- `find . -name "*.xcodeproj" -o -name "Package.swift" -o -name "*.xcframework"` -> **zero results**.
- No `apps/ios/`, no Swift Package, no xcframework artifact in tree.
- `bindings/swift/` and `bindings/kotlin/` contain only **pre-generated stub files** (`eyetracker.swift`, `eyetrackerFFI.h`, `.modulemap`) plus README.md.
- Both binding READMEs say: *"Status: Binding generation pending uniffi-bindgen CLI installation."* -> bindings are scaffolding, not yet wired to any consumer app.
- No external iOS app or Android app in the Phenotype org consumes this crate (grep'd, none found).

**Contrast with FocalPoint** (per `2026-04-26-focalpoint-uniffi-31/`): FocalPoint defers because of iOS UAT risk — live Swift binding regen affects shipping app. eyetracker has **no shipping consumer** — bindings are forward-looking placeholders.

## Recommendation: BUMP uniffi 0.27 -> 0.31

Risk profile differs from FocalPoint:

- No live iOS/Android app to UAT.
- Bindings are stubs — regen produces fresh files, no diff to validate against existing consumer.
- Workspace is small (4 crates, 1 ffi consumer).
- Resolves both advisories at the parent level (no need to suppress).

### Migration scope

1. Bump `uniffi = "0.27"` -> `"0.31"` in three sections of `crates/eyetracker-ffi/Cargo.toml`.
2. Rebuild: `cargo build -p eyetracker-ffi --release`.
3. Address API breakage (uniffi 0.28-0.31 deprecated UDL-only flow, encourages procmacro flow; check for compile errors in `eyetracker-ffi/src/lib.rs` + `build.rs` + UDL).
4. Regenerate stub bindings:
   `uniffi-bindgen generate --library target/release/libeyetracker_ffi.dylib --language swift --out-dir bindings/swift`
   (and `--language kotlin --out-dir bindings/kotlin`).
5. `cargo deny check advisories` -> expect 0 errors.

### Estimated effort

- Trivial-to-small: 3-6 tool calls, 1-3 min wall clock if no UDL/procmacro API break.
- Up to 8-15 tool calls if uniffi 0.28+ procmacro migration is required.

### Fallback

If migration breaks unexpectedly (UDL deprecation, async signature changes), defer to suppress-and-track per FocalPoint pattern. Suppression entry would mirror the FocalPoint W-92 wording in `deny.toml`. **Not recommended unless bump fails.**

## DAG

| ID | Task | Depends |
|----|------|---------|
| T1 | Bump uniffi to 0.31 in eyetracker-ffi | — |
| T2 | Fix API breakage (procmacro/UDL) | T1 |
| T3 | Regenerate swift + kotlin stubs | T2 |
| T4 | `cargo deny check advisories` -> 0 errors | T2 |
| T5 | Commit `deps(eyetracker-ffi): bump uniffi 0.27 -> 0.31` | T3, T4 |

## Out of scope

- No new features.
- No iOS/Android app integration (none exists yet).
- No deny.toml suppression (bump resolves at source).
