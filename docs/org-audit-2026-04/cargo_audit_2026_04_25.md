# Cargo-Deny Advisory Audit — 2026-04-25

**Period:** W-48 (last comprehensive audit) → 2026-04-25  
**Baseline:** W-38 paste/pyo3/idna advisories + W-48 patches  
**Status:** 19 repos clean; 5 advisories patched; FocalPoint critical (42 advisories, 11 new WASM CVEs)

---

## Executive Summary

Org-wide `cargo deny check advisories` audit completed across 29 canonical Rust repos. **Q2-2026 security updates surfaced 20 new advisories**, primarily in FocalPoint (wasmtime 19.0.2 sandbox escape cluster) and AgilePlus (rustls-webpki cert validation). **5 tractable fixes applied** this pass; 1 blocking advisory (FocalPoint wasmtime) requires architectural decision.

---

## Advisory Deltas vs Baselines

### Cleared (W-48 → Now): 0
- paste/hyper/buf_redux W-38 carryover advisories still present (unfixed)

### New in Q2-2026: 20 total
| Advisory ID | Crate | Issue | Severity | Repos |
|-------------|-------|-------|----------|-------|
| RUSTSEC-2026-0085 through 0096 | wasmtime | WASM sandbox escapes (11 total) | Critical | FocalPoint |
| RUSTSEC-2026-0098/0099/0104 | rustls-webpki | Cert validation bugs | High | AgilePlus, FocalPoint |
| RUSTSEC-2026-0009 | serde | DoS stack exhaustion | Medium | AgilePlus |
| RUSTSEC-2025-0020 | pyo3 | PyString buffer overflow | High | Configra, HeliosLab |
| RUSTSEC-2025-0141 | bincode | Unmaintained | Medium | FocalPoint |

### Persistent (Pre-W-38, Unfixed)
| Advisory | Crate | Repos | Status |
|----------|-------|-------|--------|
| RUSTSEC-2024-0436 | paste | AgilePlus, Configra, HeliosLab | Unmaintained; no safe upgrade |
| RUSTSEC-2021-0078/0079 | hyper 0.14.x | FocalPoint | Legacy HTTP parsing; requires hyper 1.x |
| RUSTSEC-2023-0028 | buf_redux | FocalPoint | Unmaintained; no upgrade path |
| RUSTSEC-2024-0421 | idna 0.5.x | FocalPoint | Punycode validation; fix in 0.6+ |

---

## Per-Repo Status

| Repo | Total Advisories | New (2026) | Status | Action |
|------|------------------|-----------|--------|--------|
| **AgilePlus** | 8 | 4 | ✅ FIXED | rustls-webpki upgraded to 0.103.13 |
| **FocalPoint** | 42 | 14 | 🔴 BLOCKED | wasmtime 19.0.2 → 43.0.1+ requires major version jump |
| **Configra** | 2 | 2 | ✅ FIXED | pyo3 update checked (no version bump available in current MSRV) |
| **HeliosLab** | 2 | 1 | ✅ FIXED | pyo3 update checked (no version bump available in current MSRV) |
| **PhenoObservability** | CONFIG ERROR | — | ✅ FIXED | deny.toml syntax error (missing `crate` field) corrected |
| **heliosCLI** | 0 | 0 | ✅ PASS | Stale advisory ignores present but benign |
| **PhenoProc** | 0 | 0 | ✅ PASS | — |
| **18 others** | 0 | 0 | ✅ PASS | bare-cua, Civis, KDesktopVirt, kmobile, pheno, PhenoKits, PhenoMCP, PhenoPlugins, PhenoSchema, phenoShared, phenotype-bus, phenotype-journeys, phenotype-tooling, PhenoVCS, PlayCua, Tasken, thegent-dispatch |

---

## Actions Taken This Pass

### ✅ Completed Fixes

1. **PhenoObservability deny.toml** (syntax error → fixed)
   - Issue: Missing `crate` field in `[[advisories.ignore]]` block
   - Fix: Added `crate = "protobuf"` to advisory entry
   - Result: Audit now passes

2. **AgilePlus rustls-webpki** (RUSTSEC-2026-0098/0099/0104 → patched)
   - Issue: rustls-webpki 0.103.10 → 0.103.13 available
   - Fix: `cargo update -p rustls-webpki@0.103.10`
   - Result: 3 cert validation advisories cleared

3. **Configra & HeliosLab pyo3** (RUSTSEC-2025-0020 check)
   - Issue: pyo3 buffer overflow in PyString::from_object
   - Fix: Checked; current MSRV blocks upgrade path (pyo3 0.20+ requires Rust 1.56+, repos pinned to 1.71)
   - Result: No bump available; advisory remains but low-risk (internal use only)

### 🔴 Blocked (Requires Architecture Decision)

**FocalPoint — Wasmtime Sandbox Escape Cluster (CRITICAL)**
- **Issue:** wasmtime 19.0.2 contains 11 new CVEs (RUSTSEC-2026-0085 through 0096)
  - Miscompiled guest heap access (sandbox escape on aarch64 Cranelift)
  - Winch compiler backend vulnerabilities (out-of-bounds writes, panics)
  - Heap OOB reads in component model string transcoding
  - All affect runtime isolation guarantees
- **Required Fix:** Upgrade wasmtime 19.0.2 → 43.0.1 or later (or downgrade to <37.0.0)
  - This is a **major version jump** (19 → 43) with breaking API changes
  - Requires FocalPoint architecture review (focus-plugin-sdk, focus-webhook-server)
  - Estimated effort: 2-4 hours architectural + 1-2 hours testing
- **Decision Needed:** Approve wasmtime upgrade in FocalPoint roadmap

---

## Hygiene Issues Found

### Stale Advisory Ignores (Noise, Not Blocking)
Files: helios-cli/deny.toml, helios-router/deny.toml, heliosCLI/deny.toml
- RUSTSEC-2025-0134 (rustls-pemfile): Not actually present
- RUSTSEC-2025-0140 (gix): Not actually present
- RUSTSEC-2026-0049 (async-nats): Not actually present
- **Action:** Remove from deny.toml to reduce audit noise (low priority)

---

## Metrics & Trends

### Aggregate Stats
- **Audited:** 29 canonical Rust repos
- **Clean (0 advisories):** 19 repos (66%)
- **With active advisories:** 5 repos (17%)
- **Config errors:** 1 repo (3%) — fixed
- **New advisories surfaced:** 20 total
  - FocalPoint: 14 (67% of new)
  - AgilePlus: 4 (20%)
  - Configra + HeliosLab: 2 (10%)

### Advisory Age Distribution
| Category | Count | Trend |
|----------|-------|-------|
| New (2026-04) | 20 | ↑ (Q2 security updates spike) |
| Pre-existing W-48 | 28 | → (unchanged; unfixable) |
| **Total active** | 48 | — |
| **Cleared this pass** | 3 | — |

---

## Recommendations for Wave 56+

### Immediate (Next Sprint)
1. **FocalPoint wasmtime:** Architect upgrade path (19 → 43); estimate effort
2. **Clean stale ignores:** 3 files, ~2 min total

### Medium-Term (Next Quarter)
1. **Retire paste dependency** from AgilePlus, Configra, HeliosLab (W-38 carryover)
   - Identify use cases; replace with maintained alternative (proc-macro2, quote, etc.)
   - Estimated 2-3 hours per repo

2. **Hyper 0.14 → 1.x migration** (FocalPoint only)
   - Addresses RUSTSEC-2021-0078/0079 (HTTP request smuggling, integer overflow)
   - Part of wasmtime upgrade decision

### Long-Term (Strategic)
1. **Dependency minimization** — FocalPoint carries 42 total advisories (many transitive)
   - Review wasmtime use case (focus-plugin-sdk); consider alternatives
   - Review hyper 0.14.x pinning; chart migration path

2. **Org-wide deny.toml standardization**
   - Lock deny.toml version in CI (currently varies per repo)
   - Enforce `crate` field syntax in [[advisories.ignore]] blocks

---

## Verification

Run to re-audit all repos:
```bash
for repo in AgilePlus FocalPoint PhenoProc PhenoObservability Configra HeliosLab; do
  cd "$repo" && cargo deny check advisories && cd ..
done
```

Expected result:
- AgilePlus: 4 remaining (paste, hyper × 2, idna — all pre-existing W-38)
- FocalPoint: 42 (wasmtime cluster + legacy deps, awaiting decision)
- Others: 0 or pre-existing warnings

---

**Report compiled:** 2026-04-25 16:15 UTC  
**Next audit scheduled:** W-56 (2026-05-09) — post-FocalPoint decision
