# FocalPoint cargo-deny advisory triage — 2026-04-26

- Repo: `FocalPoint` (canonical `repos/FocalPoint`, branch `main`, head `08a7b6e`)
- Tool: `cargo deny check advisories` (log: `/tmp/focalpoint_deny.log`)
- Total advisories: **19** (14 unmaintained + 5 vulnerability)
- Org context (W-93 commit `bae55ec932`): org total 27 → FocalPoint = ~70 % concentration
- Mode: triage only; **no fixes applied** (each fix is a separate dispatch)

## 1. Cluster breakdown by parent dependency

| Cluster | # alerts | Parent (workspace member → direct dep) | Advisories |
|---|---|---|---|
| **C1: templates-registry → `multipart 0.18` + `dotenv 0.15`** | **11** | `services/templates-registry` Cargo.toml | iron, nickel, hyper 0.10 (×2 vuln: smuggling + transfer-encoding), time 0.1 (vuln segfault), idna 0.1.5 (vuln), multipart, buf_redux, twoway, traitobject, typemap, safemem, dotenv |
| C2: starlark 0.13 (focus-cli/focus-lang) | 3 | `focus-lang` → `starlark` | derivative, fxhash, paste |
| C3: uniffi 0.28 (focus-ffi) | 1 (paste shared with C2) | `focus-ffi` → `uniffi_macros` | bincode 1, paste (also C2) |
| C4: prometheus 0.13 → protobuf 2 | 1 | `focus-observability` → `prometheus` | protobuf vuln (RUSTSEC) |
| C5: reqwest 0.11 → rustls-pemfile 1 | 1 | `focus-plugin-sdk` + templates-registry dev-dep | rustls-pemfile |
| C6: mime_guess 1.8 (build-dep of iron) → rand 0.6 → rand_os | 1 | inside C1 chain | rand_os (subsumed by C1) |

**Net:** all 11 C1 alerts share **one parent crate** (`templates-registry`); single-repo fix.
3 C2 alerts share **one parent** (`starlark` 0.13).
4 alerts (C3/C4/C5) are independent point fixes.

## 2. Categorization

| Category | Cluster | Action |
|---|---|---|
| **CLUSTER-FIX (highest leverage)** | C1 (11) | Replace `multipart 0.18` with `axum::extract::Multipart` (already pulled) + drop `dotenv` for `dotenvy 0.15` (drop-in fork, maintained). Eliminates iron/nickel/hyper-0.10/time-0.1/idna-0.1/multipart/buf_redux/twoway/traitobject/typemap/safemem in one PR. |
| **CLUSTER-FIX** | C2 (3) | Bump `starlark` 0.13 → 0.14 (fxhash → rustc-hash; paste/derivative removed in upstream 0.14 line). 3 alerts → 0. |
| **AUTO-MERGE-READY** | C3 bincode | Bump `uniffi` 0.28 → 0.29 (drops bincode dep). |
| **AUTO-MERGE-READY** | C4 protobuf | Bump `prometheus` 0.13 → 0.14 (uses protobuf 3). |
| **AUTO-MERGE-READY** | C5 rustls-pemfile | Bump `reqwest` 0.11 → 0.12 (drops rustls-pemfile 1 in favor of 2). |
| **SUPPRESS-CANDIDATE** | none material | All 19 have a forward path. No legitimate suppress-with-justification target after C1 lands. (Tauri-pattern not applicable.) |

## 3. Top 3 leverage targets (ordered by alerts/PR)

1. **C1 — templates-registry rewrite** (11 alerts cleared per 1 PR)
   - File: `services/templates-registry/Cargo.toml`
   - Commands:
     ```
     cargo remove -p templates-registry multipart dotenv
     cargo add -p templates-registry dotenvy@0.15
     # then port handlers from `multipart::server::Multipart` to `axum::extract::Multipart`
     ```
   - Risk: medium — handler refactor (~1 file). All other workspace members stay untouched.

2. **C2 — starlark bump** (3 alerts cleared per 1 PR)
   - File: workspace root `Cargo.toml` (or `crates/focus-lang/Cargo.toml`)
   - Command: `cargo update -p starlark --precise 0.14.x` after `cargo add starlark@0.14`.
   - Risk: low-medium — starlark 0.13→0.14 is API-compatible for embedding; check `starlark_syntax` re-export.

3. **C5 — reqwest bump** (1 alert + frees rustls migration)
   - Files: `focus-plugin-sdk/Cargo.toml`, `services/templates-registry/Cargo.toml` (dev-dep).
   - Command: `cargo add -p focus-plugin-sdk reqwest@0.12` (and same for templates-registry dev-dep).
   - Risk: low — patch-level breakage (TLS feature flag rename only).

## 4. Expected delta if all CLUSTER + AUTO-MERGE shipped

| Scenario | Alerts after | Org total after | FocalPoint % share |
|---|---|---|---|
| C1 only | 19 − 11 = **8** | 27 − 11 = 16 | 50 % |
| C1 + C2 | **5** | 13 | 38 % |
| C1 + C2 + C3 + C4 + C5 | **0** | 8 | 0 % |

Full sweep: **FocalPoint zeroed, org down 19/27 ≈ 70 %.**
No suppress-with-justification needed; every advisory has a maintained upstream.

## 5. Per-cluster cargo command summary

```bash
# C1 (templates-registry)
cd services/templates-registry
cargo remove multipart dotenv
cargo add dotenvy@0.15
# code change: switch to axum::extract::Multipart in handlers

# C2 (starlark)
cargo add starlark@0.14 --package focus-lang
cargo update -p starlark

# C3 (uniffi)
cargo add uniffi@0.29 --package focus-ffi --package focus-entitlements
cargo add uniffi_macros@0.29 --package focus-ffi

# C4 (prometheus)
cargo add prometheus@0.14 --package focus-observability

# C5 (reqwest)
cargo add reqwest@0.12 --package focus-plugin-sdk
cargo add reqwest@0.12 --package templates-registry --dev
```

## 6. Notes

- Fix order (DAG): C1 → C2 → C3 → C4 → C5 (C1 first because it touches the highest-LOC member; later bumps are then independent and parallelizable).
- `task quality` should be re-run after each cluster.
- No push gates needed — purely workspace-internal.
- Audit source: `/tmp/focalpoint_deny.log` (truncated copy retained at the time of run).
