# AgilePlus — RUSTSEC-2024-0436 (paste via utoipa-axum) Scope

**Date:** 2026-04-27
**Repo:** AgilePlus
**Advisory:** [RUSTSEC-2024-0436](https://rustsec.org/advisories/RUSTSEC-2024-0436)
**Severity:** Unmaintained (not a CVE — `paste` crate archived by author)

## Advisory Chain

```
paste v1.0.15 (unmaintained, archived 2024)
  └── utoipa-axum v0.2.0  (latest available — no fix released)
      └── agileplus-api v0.1.1
          └── agileplus-contract-tests v0.1.1
```

`paste` is a proc-macro for token pasting; archived upstream with no security
defect — only abandonment. `utoipa-axum 0.2.0` is the latest published version
(verified 2026-04-27 via `cargo info`); upstream `juhaku/utoipa` has not yet
cut a release that swaps to `pastey` or `with_builtin_macros`.

## AgilePlus Usage

- **Direct dep declaration:** root `Cargo.toml` line 95 + `crates/agileplus-api/Cargo.toml`
- **`utoipa_axum::` import sites:** **0** — the codebase only consumes `utoipa::OpenApi`,
  `ToSchema`, `IntoParams` derive macros and the `OpenApi::openapi()` accessor
  (5 files: `openapi.rs`, `main.rs`, `responses.rs`, `routes/features.rs`,
  `routes/events.rs`).
- `utoipa-axum` itself appears to be declared but unused at the source level —
  confirm before bump/removal.

## Migration Options

| Option | Effort | Outcome |
|---|---|---|
| **A. Drop `utoipa-axum`** | 1–2 tool calls | If unused, remove dep entirely → advisory clears. **Recommended pending verify.** |
| **B. Upstream fix wait** | 0 (passive) | utoipa#... — no ETA; advisory persists indefinitely. |
| **C. `[bans] skip` / `advisories.ignore`** | 1 commit | Suppress with TODO. Acceptable only if A unviable. |
| **D. Fork utoipa-axum** | Disproportionate | Reject. |

## Recommendation

**Option A: remove `utoipa-axum`** — 0 import sites suggests it was added
speculatively for `OpenApiRouter` integration that never landed. Verify with
`cargo build -p agileplus-api` after removing both `Cargo.toml` declarations.
If build fails, fall back to **Option C**: add to `deny.toml` `[advisories]
ignore` with reason `"upstream utoipa#TBD — paste→pastey swap pending; no
exploit, archival-only"` and a tracking link.

## Scope

- LOC: ~2 lines (`Cargo.toml` removals)
- API drift: none (no `utoipa_axum::` users)
- Public API impact: none
- Risk: low; verify via `cargo check --workspace` + `cargo deny check advisories`

## Next Step

Implement in a follow-up PR off `AgilePlus-wtrees/security-alerts-20260426`
or `cve-cross-bump`. Out of scope for this proposal.
