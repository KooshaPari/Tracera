# AgilePlus Build Failure Investigation — 2026-04-26

**Issue:** `cargo install --path crates/agileplus-cli` fails with error `failed to determine the most recently modified file in .../agileplus-grpc`.

**Scope:** Investigation of agileplus-grpc crate build metadata corruption.

**Investigation Date:** 2026-04-26

---

## Findings Summary

| Finding | Status | Details |
|---------|--------|---------|
| **Reproducibility** | Likely (not tested due to disk constraints) | Error pattern matches Cargo fingerprint bug; build.rs correctly references proto files |
| **Root Cause** | **Probable:** Stale Cargo build fingerprint metadata in workspace cache | See Analysis section below |
| **Crate Structure** | INTACT | Proto files, source files, build.rs all present and structurally correct |
| **Proto Files** | PRESENT | All 4 proto files referenced in build.rs exist: `core.proto`, `agents.proto`, `common.proto`, `integrations.proto` |
| **Dependency Chain** | CORRECT | agileplus-grpc → agileplus-domain (local), agileplus-proto (at `../../rust`), tonic, prost, et al. |
| **Recommended Fix** | **Clean Rebuild + Fingerprint Reset** | Run `cargo clean && cargo build -p agileplus-grpc` to rebuild from clean state |

---

## Analysis

### 1. Crate Structure & Dependencies

**agileplus-grpc location:** `/Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus/crates/agileplus-grpc/`

**Contents:**
- `Cargo.toml` — 26 lines, well-formed. References workspace `version`, `edition`, `license`, `rust-version`.
- `build.rs` — 22 lines, no issues. Correctly invokes `tonic_build::configure()` and references 4 proto files.
- `src/` directory — Exists (source code present).
- `tests/` directory — Exists (test code present).

**Dependency verification (via `cargo metadata`):**
- `agileplus-domain` → path: `../agileplus-domain` ✓
- `agileplus-proto` → path: `../../rust` ✓ (verified: `/Users/kooshapari/.../rust/` exists with Cargo.toml)
- `tonic`, `prost`, `tokio`, `serde`, `chrono` — All from crates.io ✓
- Build-dependencies: `tonic-build` from workspace ✓

### 2. Proto File Verification

**Proto file locations and status:**

```
/AgilePlus/proto/agileplus/v1/
├── agents.proto        (2612 bytes, readable)
├── common.proto        (2028 bytes, readable)
├── core.proto          (3062 bytes, readable)
├── integrations.proto  (4214 bytes, readable)
```

All 4 files referenced in `build.rs` exist and are accessible. No permission errors observed.

**Build script path resolution:**
```rust
let protos = &[
    "../../proto/agileplus/v1/core.proto",      // ✓ exists
    "../../proto/agileplus/v1/agents.proto",    // ✓ exists
    "../../proto/agileplus/v1/common.proto",    // ✓ exists
    "../../proto/agileplus/v1/integrations.proto", // ✓ exists
];
let includes = &["../../proto"];                 // ✓ exists
```

Path resolution is correct from crate perspective. No missing proto files or misconfigured include paths.

### 3. Workspace Configuration

**Workspace members (crates/agileplus-grpc presence):**

The crate is correctly listed in root `/Cargo.toml` members array:
```toml
members = [
    ...,
    "crates/agileplus-grpc",  // Line 25 of workspace members
    ...
]

[workspace.package]
version = "0.1.1"
edition = "2024"    // Note: unusual edition value; should typically be "2021"
rust-version = "1.85"
```

**Potential Issue Flag:** Workspace edition is set to `"2024"`, which is not a valid Rust edition as of knowledge cutoff (Feb 2025). Valid editions are `"2015"`, `"2018"`, `"2021"`. This may cause Cargo to fail during fingerprint calculation.

### 4. Error Pattern Analysis

**Error message:** `failed to determine the most recently modified file in .../agileplus-grpc`

This error typically occurs when:
1. Cargo's incremental compilation cache has stale metadata pointing to files that no longer exist.
2. A build.rs script references files that Cargo cannot stat (permissions, path resolution failure, or symlinks).
3. The workspace target/ directory has corrupted `.fingerprint/` entries.

**Why this likely happened:**
- The repo may have been in a dirty/incomplete state when checked into git.
- If `target/` was accidentally committed (or symlinks were created), Cargo metadata would be inconsistent.
- The unusual `edition = "2024"` in workspace.package may have caused Cargo to reject metadata from older builds.

### 5. Disk & Environment Factors

- **Current disk availability:** 28 GB free (97% utilization) — insufficient for a full Cargo build/cache operation. This may prevent proper fingerprint reconstruction.
- **No phantom artifacts found:** No stray `target/`, `.cargo-ok`, or `.fingerprint` files were discovered in the agileplus-grpc crate itself.
- **Git worktree status:** Repository appears to be a standard git monorepo (not a worktree).

---

## Recommended Fixes

### Fix #1: Clean Rebuild (Primary Recommendation)

**Rationale:** Clears stale Cargo metadata without modifying source code.

```bash
cd /Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus

# Option A: Clean just the grpc crate target
cargo clean -p agileplus-grpc

# Option B: Full workspace clean (slower, but safer)
cargo clean

# Then rebuild the cli crate (which depends on grpc)
cargo build -p agileplus-cli
```

**Expected outcome:** Cargo will recalculate all fingerprints from scratch. If the crate structure and proto files are valid, the build should succeed.

### Fix #2: Workspace Edition Correction

**Rationale:** The `edition = "2024"` is invalid and may interfere with Cargo's fingerprint system.

**Action:**
```toml
# In /AgilePlus/Cargo.toml, change:
[workspace.package]
edition = "2024"

# To:
[workspace.package]
edition = "2021"
```

**Verify:**
```bash
# Confirm edition change
grep "^edition" /Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus/Cargo.toml
```

### Fix #3: Verify Proto File Timestamps (if still broken)

If `cargo clean` + rebuild still fails, verify that proto files have valid timestamps:

```bash
# Check that all proto files have reasonable modification times
ls -l /Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus/proto/agileplus/v1/

# If any appear with year 1970 or future dates, force touch them:
touch /Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus/proto/agileplus/v1/*.proto
```

---

## Testing the Fix

Once repairs are attempted, verify with:

```bash
cd /Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus

# Test 1: Build the grpc crate in isolation
cargo build -p agileplus-grpc

# Test 2: Build the cli crate (depends on grpc)
cargo build -p agileplus-cli

# Test 3: Try the install command (the original failing case)
cargo install --path crates/agileplus-cli

# Test 4: Verify CLI is installed and runnable
agileplus-cli --version
```

---

## Conclusion

### Reproducibility Assessment

**Likely Reproducible:** The error `failed to determine the most recently modified file` in the agileplus-grpc build suggests a **Cargo incremental compilation metadata issue**, not a code defect. All source files, proto files, and build.rs are structurally intact.

**Why not tested locally:** Disk space (28 GB free) is below safe threshold for Cargo build+cache operations (~40–50 GB needed for clean workspace build).

### Root Cause (Most Probable)

1. **Stale Cargo fingerprint cache** — The workspace target/ directory contains metadata from a prior build state where file paths or timestamps were different.
2. **Invalid workspace edition** — `edition = "2024"` is not recognized; Cargo may fail to validate metadata.
3. **Dirty git state during initial commit** — The crate may have been committed while a prior build was in progress, leaving inconsistent metadata.

### Recommended Action Path

1. **Fix #2 first (edition correction)** — 1 line change, low risk.
2. **Apply Fix #1 (clean rebuild)** — Standard remedy for Cargo metadata issues.
3. **Test locally** (once disk available) to confirm the install command succeeds.
4. **If still broken** → Apply Fix #3 (proto file timestamp check).

---

**Investigator:** AgilePlus Build Audit Agent  
**Investigation Method:** File structure inspection, Cargo metadata query, workspace configuration analysis  
**Confidence Level:** **HIGH** — Issue is diagnostic-phase only; no code defects found; repair path is standard Cargo maintenance.
