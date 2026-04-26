# FocalPoint uniffi 0.28 → 0.31 — Scope & Recommendation

**Date:** 2026-04-26
**Repo:** FocalPoint
**Advisory:** RUSTSEC-2025-0141 (bincode 1.x via uniffi 0.28)
**Status:** SCOPED — recommendation: **DEFER + SUPPRESS** (HIGH iOS risk)
**Predecessor:** `2026-04-26-focalpoint-final-5` (classified MEDIUM, breaking-FFI)

## 1. Current State

| Item                           | Value                                                              |
|--------------------------------|--------------------------------------------------------------------|
| Workspace pin                  | `Cargo.toml:120` → `uniffi = "0.28"`                               |
| `focus-ffi` build-dep          | `uniffi_build = { version = "0.28", features = ["builtin-bindgen"] }` |
| `focus-entitlements` dep       | `uniffi = { workspace = true, features = ["cli"] }`                |
| Binding mode                   | **Pure UDL** (`crates/focus-ffi/src/focus_ffi.udl`, 696 lines)     |
| Proc-macro `#[uniffi::export]` | 1 occurrence in `lib.rs` (3,254 lines)                             |
| Swift bindings                 | Regenerated via `crates/focus-ffi/scripts/ios-bindings.sh`         |
| xcframework                    | Just unblocked today (commits 5c4030c, d00e542, 906075b)           |

Advisory chain: `uniffi 0.28 → bincode 1.3.3` (RUSTSEC-2025-0141). FocalPoint's only remaining advisory after prometheus fix (`c05a60e`).

## 2. Breaking-Change Inventory (0.28 → 0.31)

| Version | Breaking item                                                                | FocalPoint impact                                                                              |
|---------|-------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------|
| 0.29    | Callback interfaces unified with foreign traits; `[Trait]` UDL semantics shift| **HIGH** — UDL has multiple `[Trait]`/callback interfaces; Swift adapter surface will drift    |
| 0.30    | `proc-macro` mode is default; UDL mode deprecated (still supported via `library` mode); error type ABI tweaks; `uniffi-bindgen` CLI flag rename | **HIGH** — pure-UDL pipeline; `build.rs` + `ios-bindings.sh` need flag/mode adjustments         |
| 0.31    | Mostly docs + async polish; minor Result-handling tweaks                      | LOW                                                                                            |

Net: at minimum, **Swift binding surface changes** in 0.29 + **build pipeline changes** in 0.30. Both regenerate the FFI header and Swift wrapper consumed by the iOS Xcode project.

## 3. Estimated Change Surface

- `Cargo.toml`: 1 line (`0.28 → 0.31`)
- `crates/focus-ffi/Cargo.toml`: 1 line (`uniffi_build 0.28 → 0.31`)
- `build.rs`: possibly unchanged (UDL mode preserved) OR migration to `library` mode (~5 lines)
- UDL: callback-interface syntax review across 696 lines (~10–30 lines edited)
- Generated Swift bindings: full regen → header diff propagates to xcframework
- iOS Xcode build: must re-link against new symbol surface; risk of compile errors in `FocalPointCore` Swift adapter

## 4. Risk Assessment

**HIGH (iOS regression)**:
1. xcframework toolchain was unblocked **today** after multi-commit recovery. Bumping uniffi forces a header + Swift-wrapper churn that re-exercises the exact path we just stabilized.
2. Pure-UDL mode is deprecated in 0.30 — likely requires migrating to library/proc-macro mode, which is a structural change far beyond a version bump.
3. No iOS UAT has been performed against the freshly-built xcframework. Regenerating bindings before validating the current build invalidates the recovery work.
4. RUSTSEC-2025-0141 is an **unmaintained-crate** advisory on bincode 1.x — no known exploit, indirect dep, FFI-internal serialization only.

## 5. Recommendation: DEFER + SUPPRESS

Rationale: HIGH iOS regression risk versus LOW exploit risk on an unmaintained-crate advisory.

**Action plan:**
1. Add `RUSTSEC-2025-0141` to `deny.toml` `[advisories].ignore` with justification:
   - Indirect via `uniffi 0.28` (FFI-internal serialization)
   - Bump blocked on iOS UAT of freshly-built xcframework
   - Tracking: this proposal
2. Re-evaluate after:
   - iOS UAT confirms current xcframework is functionally correct
   - At least one independent FocalPoint feature ships against current xcframework
3. When unblocked: schedule as a **dedicated change** (not a hygiene bump) with:
   - 0.28 → 0.29 pass (callback-interface review)
   - 0.29 → 0.30 pass (UDL mode → library mode migration)
   - 0.30 → 0.31 pass (trivial)
   - Each pass: regen Swift bindings + rebuild xcframework + iOS smoke build

**Estimated effort when un-deferred:** 8–15 tool calls or 2–3 parallel subagents, ~10–20 min wall clock; iOS Xcode verification adds an unknown human-loop step (entitlements + device).

## 6. Decision

DEFER. Suppress advisory with tracking link to this proposal. Do not bump until iOS UAT clears the current xcframework.
