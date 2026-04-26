# KDV bollard cluster bump — W-95 advisory leverage

**Date:** 2026-04-27
**Repo:** `KDesktopVirt` (crate: `kvirtualstage v0.2.1`)
**Leverage:** 4 of W-95's remaining 8 advisories (50%) cleared by one parent-dep bump.

## Advisories (all flow through `bollard 0.16.1` → `rustls 0.22.4` → `rustls-webpki 0.102.8`)

| ID                  | Crate         | Severity / Type                    | Fixed in                |
| ------------------- | ------------- | ---------------------------------- | ----------------------- |
| RUSTSEC-2026-0049   | rustls-webpki | (cluster member)                   | >=0.103.x               |
| RUSTSEC-2026-0098   | rustls-webpki | Name-constraint bypass (wildcard)  | >=0.103.12              |
| RUSTSEC-2026-0099   | rustls-webpki | (cluster member)                   | >=0.103.x               |
| RUSTSEC-2026-0104   | rustls-webpki | Reachable panic in CRL parsing     | >=0.103.13              |

All four are transitive through a single root: `bollard 0.16` (pinned in
`Cargo.toml:54`). `bollard 0.16` depends on `rustls 0.22` / `rustls-webpki 0.102`
which is EOL for the 0.102 line. Upstream `bollard 0.20.2` (latest stable,
verified via `cargo search`) tracks current `rustls 0.23` / `rustls-webpki 0.103`.

## Bollard usage scope in KDV

- **Single file:** `src/virtualization.rs` (698 LOC, 25 docker/container refs).
- **Surface area:** 4 imports, ~10 call sites:
  - `Docker::connect_with_local_defaults()`
  - `CreateContainerOptions`, `StartContainerOptions`, `StopContainerOptions`,
    `RemoveContainerOptions`, `AttachContainerOptions`, `AttachContainerResults`
  - `CreateImageOptions`
  - `bollard::models::*` (config types)
- **Public API impact:** None — KDV consumes bollard internally for container
  lifecycle. No re-exports of `bollard::*` types in public surface.
- **Feature flags:** `default-features = false, features = ["ssl"]`.
  Note: `bollard 0.20` reorganized features; `ssl` no longer exists. Replacement
  is the `pipe`/`http` defaults plus optional rustls feature gates. Will need
  feature reselection.

## Migration scope (0.16 → 0.20)

Four minor-version jumps. Known API drift across this range:

1. **Feature flags rename** (ssl → rustls/openssl). One `Cargo.toml` line.
2. **`*Options` builder ergonomics:** several `Default::default()` patterns
   tightened; some option fields renamed (e.g. `force` flag positions).
3. **Stream APIs:** `attach_container` / `create_image` returned types may have
   changed result wrapping (`AttachContainerResults` was unified in 0.18).
4. **Error type:** `bollard::errors::Error` variants reorganized in 0.17.

Estimated touch: ~15-30 LOC across `virtualization.rs`. No structural refactor;
contained to one file. Compile-driven migration (let `cargo check` enumerate
breakage).

## Risk

- **Low–Medium.** Single-file blast radius, no public API leak, internal-only
  consumer. Risk is compile-time discoverable.
- **Test coverage:** moderate — KDV has integration tests but they require a
  live docker daemon, so CI verification is `cargo check` + `cargo build`.
- **Sister crate `kvirtualstage`:** same workspace, same lockfile — bump applies
  cleanly.

## Recommendation

**DO IT — scoped manual bump, not auto-apply.**

This is **not** a 2-line drop-in like the prometheus case. The feature-flag
rename (`ssl` → rustls feature) plus 4 minor-version API drift across one
698-LOC file requires a compile-driven migration pass. Not safe for
unattended automation.

Suggested execution: dispatch a focused subagent with explicit constraints:
- Bump `bollard = "0.20"` in `Cargo.toml`
- Reselect features (likely `default-features = false, features = ["http", "ssl"]`
  with new ssl gate, or whatever 0.20 calls it)
- `cargo check` loop until clean
- Manual review of `attach_container` stream handling (most likely break point)
- Verify advisory clearance: `cargo deny check advisories`

**Effort estimate:** 8-15 tool calls, ~5-8 min wall clock. One subagent.

**Leverage:** clears 4/8 of W-95 remainder in one bump — second-highest leverage
target after the FocalPoint zero already shipped.

## Cross-Project Reuse Opportunities

None identified — `bollard` consumption is unique to KDV/kvirtualstage in the
Phenotype org. No shared docker abstraction to extract.
