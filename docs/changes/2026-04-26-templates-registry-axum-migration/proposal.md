# Proposal: templates-registry — multipart 0.18 + dotenv → axum::Multipart + dotenvy

**Date:** 2026-04-26
**Service:** `FocalPoint/services/templates-registry`
**Leverage target:** FocalPoint cargo-deny advisories 19 → 8 (-11, ~58%); org-wide 27 → 16 (-41%).
**Origin doc:** `docs/governance/focalpoint_advisory_triage_2026_04_26.md` (cluster C1, commit 3e2a09d7f4).

## Current Direct Deps (Cargo.toml)

```toml
multipart = "0.18"        # Pulls iron-era transitive stack (hyper-0.10, time-0.1, idna-0.1)
dotenv    = "0.15"        # Unmaintained; replaced by dotenvy
```

Stack already on axum 0.7 + tokio + tower 0.4. **No iron/nickel direct dep.** All 11 advisories
(iron, nickel, hyper-0.10, time-0.1, idna-0.1, et al.) flow transitively through `multipart 0.18`'s
ancient HTTP-server impl.

## Critical Finding — multipart is a STUB

```text
src/handlers.rs:104:  /// Upload a new template pack (multipart: pack.tar.zst + signature.ed25519).
src/handlers.rs:129:  // TODO: multipart handling for pack.tar.zst + signature.ed25519
src/handlers.rs:133:  "message": "upload endpoint stub (multipart handling not yet implemented)"
```

The `multipart` crate is declared as a dependency but **never imported and never used**. The
`upload_pack` handler is a placeholder returning a stub JSON. Total `multipart` usages in `src/`:
**0 actual call sites** (3 doc-comment/string mentions only).

Total dotenv usage: **1 line** (`src/main.rs:29: dotenv::dotenv().ok();`).

## Service Surface

- 7 source files, 863 LOC total (handlers 169, db 272, ratelimit 124, models 115, main 80, auth 52, error 51).
- 1 unit test (rating validation). No integration tests touching multipart.
- `[dev-dependencies]` reqwest with `json` feature only (no multipart fixtures).

## Migration Steps

1. **Cargo.toml:** delete `multipart = "0.18"`; replace `dotenv = "0.15"` → `dotenvy = "0.15"`.
2. **src/main.rs:29:** `dotenv::dotenv().ok();` → `dotenvy::dotenv().ok();`.
3. **No handler refactor needed** — the multipart endpoint is a stub. When real upload work
   begins (FR-TEMPLATE-MARKETPLACE-001), implement directly against
   `axum::extract::Multipart` (already available via existing `axum = "0.7"` dep, no new crates).
4. `cargo update -p multipart --precise <none>` then `cargo update`; verify `cargo deny check`
   drops the 11 advisories.
5. `cargo check -p templates-registry && cargo clippy -p templates-registry -- -D warnings`.

## Effort Estimate (agent-tool-call terms)

- **Trivial change:** 2-3 tool calls, <2 min wall clock.
- One Edit on Cargo.toml, one Edit on main.rs, one Bash for cargo check + cargo deny verify.

## Risk

- **Public API impact:** zero. Stub endpoint behaviour preserved (still returns placeholder JSON).
- **Breaking change:** none. No callers depend on real multipart parsing yet.
- **Test impact:** none. Existing single unit test is unrelated.
- **Future work:** when implementing FR-TEMPLATE-MARKETPLACE-001 upload, use
  `axum::extract::Multipart` per <https://docs.rs/axum/latest/axum/extract/struct.Multipart.html>.

## Recommendation

**DO IT IMMEDIATELY** — highest leverage / lowest risk advisory cleanup in the org. 11/19
FocalPoint advisories vanish from a 2-line Cargo.toml diff plus a 1-token rename. Defer the
actual axum::Multipart upload implementation to the FR-TEMPLATE-MARKETPLACE-001 work package
(separate spec, separate commit).

The "axum::Multipart refactor" framing in the triage doc is misleading: there is nothing to
refactor. The `multipart` crate is dead weight; deletion is sufficient.
