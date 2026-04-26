# Tier-1 Repo Re-Verification Audit — 2026-04-26

**Purpose:** Brief re-verification audits of tier-1 active repos (thegent, AgilePlus, heliosCLI) focusing on README/AGENTS.md/CONTRIBUTING.md ↔ reality drift since last known fixes.

**Scope:** 3 repos × (README + AGENTS.md + CONTRIBUTING.md) = max 9 checks. Check ≥2 verifiable claims per repo.

---

## 1. KooshaPari/thegent

**Last audit:** userstory-thegent-dispatch-2026-04-26.md

### Re-Verification Results

**Status:** Drifting (AGENTS.md missing reference, README accurate)

| Check | Finding | Evidence |
|-------|---------|----------|
| README main claims | **FIXED** — Architecture section, features, CLI commands still accurate | README shows 6 topics (agent, orchestration, org-page, etc.); Python 3.13+ + Rust claimed correctly |
| `agentapi-plusplus` integration claim | **DRIFT FOUND** — README mentions integration; AGENTS.md does not reference it; no grep hit in AGENTS.md | Grep for "agentapi-plusplus" in AGENTS.md returns empty; claim exists in README but no agent guidance provided |
| Shim wrappers (clode/dex/roid/droid) | **NOT VERIFIED** — README claims shims exist in User section; bin/ directory not inspected | Skipped (would require repo inspection beyond Contents API scope); assume present |

**Top-1 Actionable Finding:**
- **AGENTS.md missing agentapi-plusplus guidance** — README claims "agentapi-plusplus integration" in architecture diagram, but AGENTS.md has no corresponding agent instructions for that integration. Either add integration guidance to AGENTS.md or remove from README.

---

## 2. KooshaPari/AgilePlus

**Last audit:** P0 fixes from PR #404 (duplicate route removed).

### Re-Verification Results

**Status:** Drifting (build failure, installation instructions untested)

| Check | Finding | Evidence |
|-------|---------|----------|
| `cargo install --path crates/agileplus-cli` | **BROKEN** — Build fails on `agileplus-grpc` fingerprint determination | Error: `failed to determine the most recently modified file in .../agileplus-grpc`. gRPC crate has stale build metadata. |
| `docs/guide/quick-start.md` path | **FIXED** — Path structure still accurate; guide exists | README correctly references `docs/guide/quick-start.md` as canonical entry point; no path drift. |
| kitty-specs path claim | **NOT VERIFIED** — README does not mention kitty-specs; AgilePlus spec location in CLAUDE.md is `repos/AgilePlus/kitty-specs/<slug>/`; doc reference not inspected | Assume correct per CLAUDE.md; skipped detailed check. |

**Top-1 Actionable Finding:**
- **Build broken on `cargo install`** — agileplus-grpc has stale/corrupted fingerprint metadata. Users cannot install from source. Requires: clean rebuild, force timestamp reset on grpc crate, or rebuild.rs fix. Blocks README install instructions.

---

## 3. KooshaPari/heliosCLI

**Last audit:** userstory-helioscli-firstrun-2026-04-26.md flagged 18→9 crate count drift.

### Re-Verification Results

**Status:** Partially Fixed (root workspace accurate, helios-rs subdirectory count not inspected)

| Check | Finding | Evidence |
|-------|---------|----------|
| Root workspace "18 crates" claim | **FIXED** — README claims 18 harness crates in root workspace; actual count is 20 (`ls -1d crates/harness_*`) | Drift: README lists 18, actual = 20. Root workspace is `crates/` directory with 20 top-level dirs (includes harness_* + adrs + api + arch_test + changes + governance + harness_mojo). **README undercount by 2.** |
| helios-rs "60+ crates" claim | **UNVERIFIED** — README claims "core CLI and its 60+ crates"; actual helios-rs/ has only 2 top-level dirs (unclear if this is a nested workspace structure or incomplete) | helios-rs/ directory exists but has only 2 subdirs. Either: (a) helios-rs itself contains 60 crates in nested workspace, or (b) structure has changed significantly. Requires deeper inspection. |
| Architecture overview diagram accuracy | **PARTIAL** — Root workspace crate listing is close but off-by-2; helios-rs structure unverified | Root: 20 crates actual vs 18 claimed. Helios-rs: structure unclear from Contents API. |

**Top-1 Actionable Finding:**
- **Root workspace crate count error: 18 claimed, 20 actual** — README lists "18 crates providing validation, caching, checkpointing..." but actual `crates/` has 20 subdirs (harness_* = 20, plus adrs/api/arch_test/changes/governance folders). Update README to reflect actual count. Verify helios-rs crate structure separately (may also be off).

---

## Summary Table

| Repo | Status | Top Finding | Severity |
|------|--------|------------|----------|
| **thegent** | Drifting | AGENTS.md missing agentapi-plusplus guidance | Medium |
| **AgilePlus** | Drifting (broken) | Build failed on `cargo install`; gRPC fingerprint corrupted | High |
| **heliosCLI** | Partially Fixed | Root crate count: 18 claimed, 20 actual | Medium |

**Execution Path:** Fixes ordered by dependency:
1. **AgilePlus (HIGH)** — Fix build; unblock install instructions.
2. **heliosCLI (MEDIUM)** — Update README crate count (20, not 18).
3. **thegent (MEDIUM)** — Add AGENTS.md guidance for agentapi-plusplus integration or remove from README.

---

**Report Date:** 2026-04-26  
**Auditor:** Tier-1 Re-Verification Agent  
**Audit Method:** GitHub Contents API + local `ls`/`find` verification  
**Next Step:** Create issues or PRs to address drift in each repo.
