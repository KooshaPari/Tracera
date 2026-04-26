# FocalPoint reqwest 0.11 → 0.12 Migration Scoping

**Date:** 2026-04-26
**Author:** Investigation agent
**Status:** Proposal — DO NOT EXECUTE without approval
**Goal:** Clear final 6 advisories tied to reqwest 0.11 in FocalPoint workspace.

## TL;DR

**Recommendation: DO IT — trivial, ~2 lines.**

This is the templates-registry pattern again (commit 38510bc657). The "migration"
is two `Cargo.toml` version bumps. focus-plugin-sdk uses only stable reqwest
APIs that did not break across 0.11→0.12. templates-registry has a phantom
declaration with **zero source-level uses**.

## Current State

### Workspace reqwest landscape

```
[workspace.dependencies] reqwest = "0.12" (root Cargo.toml:89)
```

20 crates already use the workspace 0.12 (or pin 0.12 directly).

### The two outliers (pinned to 0.11)

| Crate | File | LOC of usage | Resolved version |
|-------|------|--------------|------------------|
| `focus-plugin-sdk` | `crates/focus-plugin-sdk/Cargo.toml:24` | 4 references in 1 file | 0.11.27 |
| `templates-registry` | `services/templates-registry/Cargo.toml:37` | **0 references** | phantom (other deps resolve 0.12.28) |

### focus-plugin-sdk usage (only consumer)

`crates/focus-plugin-sdk/src/capabilities/http.rs` (251 LOC, 4 reqwest sites):

- `url.parse::<reqwest::Url>()` — stable
- `reqwest::Client::new()` — stable
- `client.get/post/put/delete/patch/head(&url)` — stable
- `request.header(k, v)` — stable
- `request.body(b)` — stable
- `request.timeout(d).build()` — stable
- `client.execute(request).await` — stable
- `response.status().as_u16()` — stable
- `response.headers()` iteration → `to_str()` — stable

No `blocking::`, no `multipart::`, no `Proxy`, no `Identity`, no native-tls API.

## reqwest 0.11 → 0.12 Breaking Changes (vs. our usage)

| Breaking change | Affects us? |
|-----------------|-------------|
| `http` 0.x → 1.x in public API | No — we don't expose `HeaderMap`/`HeaderValue` types directly; we convert via `to_str()` |
| Default TLS backend rename (`default-tls` semantics) | No — focus-plugin-sdk has `features = ["json"]` only, no TLS feature explicitly. Default still works. |
| `Body::wrap_stream` removed | No — we pass `Vec<u8>` |
| `blocking` feature gated | No — async only |
| MSRV bump to 1.63 | No — workspace MSRV already higher |

## Migration Steps

```toml
# crates/focus-plugin-sdk/Cargo.toml line 24
- reqwest = { version = "0.11", features = ["json"] }
+ reqwest = { workspace = true, features = ["json"] }

# services/templates-registry/Cargo.toml line 37
- reqwest = { version = "0.11", features = ["json"] }
+ # removed — no source uses reqwest (verify with `grep -rn reqwest src/`)
# OR if a transitive build script reference exists:
+ reqwest = { workspace = true, features = ["json"] }
```

Then: `cargo update -p reqwest`, `cargo build -p focus-plugin-sdk -p templates-registry`,
`cargo test -p focus-plugin-sdk` (the http.rs file has tests at line 246+).

## Effort Estimate (agent-led)

- **Tool calls:** 3–5 (2 Edits, 1 cargo build, 1 cargo test, optional 1 audit)
- **Wall clock:** 2–4 min including build
- **Risk:** Very low — APIs unchanged, JSON feature unchanged, only TLS default semantics could surprise. Mitigation: if TLS errors appear, add `features = ["json", "default-tls"]` explicitly.

## Risk Assessment

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| TLS feature regression | Low | Plugin HTTP proxy hits external URLs; covered by integration tests |
| Transitive duplicate (some other 0.11 user) | Verified none | `cargo tree -i reqwest` confirms only focus-plugin-sdk pins 0.11 |
| templates-registry phantom dep needed by build script | Low | Confirmed zero `reqwest` references in `services/templates-registry/src/` |

## Recommendation

**DO IT.** Two-line `Cargo.toml` change, zero source edits required. Same pattern
as the templates-registry "migration" (commit 38510bc657) which turned out to
be a trivial bump.

Sequence:
1. Edit `crates/focus-plugin-sdk/Cargo.toml` → `workspace = true`
2. Edit `services/templates-registry/Cargo.toml` → `workspace = true` (or remove)
3. `cargo build --workspace` + `cargo test -p focus-plugin-sdk`
4. `cargo audit` to confirm 6 advisories cleared
5. Commit `chore(deps): bump focus-plugin-sdk + templates-registry to reqwest 0.12 (clears 6 advisories)`

## Cross-Project Reuse Note

Same migration pattern probably applies to other Phenotype repos still on
reqwest 0.11. Worth a follow-up sweep: `rg 'reqwest = .*"0\.11"' --type toml`
across `repos/`.

## Correction 2026-04-27

The scoping prediction above was **wrong on the advisory delta**. Apply agent
(commit `6a601b1`) verified the actual outcome:

- **Predicted:** clear 6 advisories tied to reqwest 0.11.
- **Actual delta:** **0** advisories cleared by the reqwest bump.
- **Why:** reqwest was already resolving to `0.12.28` via the transitive
  graph. The `templates-registry` `0.11` declaration was a **phantom**
  (zero source uses, dedup'd to 0.12.28 by Cargo). Only `focus-plugin-sdk`
  had a real `0.11` pin, and it too co-existed with 0.12.28 transitively
  rather than pulling a duplicate 0.11 tree into the lockfile in a way
  cargo-audit was flagging.
- **Real culprits behind the 6 remaining advisories:** `paste`,
  `derivative`, `protobuf`, `fxhash`, `bincode` — none of which are reqwest
  transitives. These were cleared via separate commits:
  - `c05a60e` — prometheus dep update (paste/protobuf/fxhash path)
  - `187cb41` — starlark suppression (derivative path)
  - `f373073` — uniffi suppression (bincode path)
- **Why the bump still landed:** dependency hygiene and future-proofing.
  reqwest `0.11` is unmaintained upstream; `0.12` is the actively
  maintained line. Two-line change, zero source edits, no regressions —
  worth keeping even though the advisory math was wrong.

### Lesson

Scoping docs that predict a **specific advisory delta** must verify the
prediction against the actual `cargo audit` diff before claiming success.
The fix here is hygiene-positive but advisory-neutral; the proposal
conflated "reqwest 0.11 is referenced" with "reqwest 0.11 is the cause
of the 6 advisories", which `cargo tree -i` would have falsified in
under a minute.

Cross-reference: `feedback_scoping_doc_verify_then_fix.md` (memory).
