# Dependency audit — 2026-10-28

OSV Scanner (local, v2.3.5) scanned every authoritative manifest in the tree.
CI runs the same scan via `google/osv-scanner-action` v2.0.2 in
`.github/workflows/dependency-audit.yml`.

| Manifest                       | Before        | After | State                      |
| ------------------------------ | ------------- | ----- | -------------------------- |
| `Cargo.lock`                   | 4 advisories  | 1     | residual, upstream-blocked |
| `frontend/bun.lock`            | 19 advisories | 1     | residual, no upstream fix  |
| `sidecar/go/go.mod`            | 0             | 0     | clean                      |
| `crates/tracera-go-cli/go.mod` | 38 advisories | 0     | clean                      |

Reproduce:

```bash
osv-scanner scan --lockfile=Cargo.lock
osv-scanner scan --lockfile=frontend/bun.lock
osv-scanner scan --lockfile=sidecar/go/go.mod
osv-scanner scan --lockfile=crates/tracera-go-cli/go.mod
cargo deny check
```

## What was fixed

**Rust — `RUSTSEC-2026-0381/0382/0383`, then `RUSTSEC-2026-0387`.** The first
three closed by patch bumps. `0387` was recorded in an earlier pass as having no
upstream fix; that was wrong. The advisory metadata says
`patched = [">= 0.7.6"]`, and `aws-sigv4 1.6.4` depends on `crypto-bigint
^0.7.10`, so `cargo update -p aws-sigv4 --precise 1.6.4` removes the flagged
`crypto-bigint 0.5.5` outright. Verified by `cargo deny check` (all four gates
ok) and by `cargo check --workspace` on the Desk host (20m 11s, exit 0).

**npm — 19 → 1.** Five overrides were pinned inside their own vulnerable
windows. Each was raised to the version in the OSV record's patched range, not
to "newest":

| Package    | Was     | Now     | Note                                                                    |
| ---------- | ------- | ------- | ----------------------------------------------------------------------- |
| dompurify  | ^3.4.14 | ^3.4.17 | 3 advisories, highest CVSS 9.2                                          |
| fast-uri   | ^3.1.5  | ^3.1.9  | 4 advisories; 3.1.9 is the last fixed 3.x, 4.x would be a major for ajv |
| ip-address | ^10.3.1 | ^10.7.4 | fixed in 10.7.4                                                         |
| undici     | (none)  | ^7.30.1 | 8 advisories; stayed on 7.x deliberately                                |
| zod        | 4.3.6   | ^4.6.6  | fixed in 4.6.6                                                          |

`frontend/bun.lock` regenerated with `bun install`. The frontend was then
verified in the order CI uses (`build`, then `typecheck`, because
`packages/types/dist` must exist first): `bun run build` 5/5 tasks succeeded,
`bun run typecheck` exit 0 including the native typecheck contract probe.

**Go — 38 → 0.** `crates/tracera-go-cli/go.mod` declared `go 1.22`, which
resolves to Go stdlib 1.22.x. The highest fixed version across all 38 findings
is `1.27.3`, so the directive now says exactly that. `go build` succeeds against
the auto-downloaded `go1.27.3` toolchain.

This one had been invisible: it is a second, independent Go module, and the
audit listed only `Cargo.lock`, `frontend/bun.lock` and `sidecar/go/go.mod`.
`scan source` does not recurse into it. The module is now listed explicitly in
`scan-args` so it cannot drift unscanned again.

## Suppressions

**None were added.** Two were removed: `frontend/osv-scanner.toml` carried
`GHSA-vfj7-8cjw-p6xm` (braces) and `GHSA-hp3w-g68c-fv3c` (sprintf-js), both of
which osv-scanner reported as unused ignores against the current lockfile. A
suppression that suppresses nothing is a standing blind spot with a reason
attached, so both were deleted and the file documents that it now holds no
exceptions.

The root `osv-scanner.toml` and `deny.toml` Rust exceptions were not touched.

## Residual 1 — `deepmerge@4.3.1`

- Advisory: `GHSA-gcqx-w48m-w2h4`, CVSS 5.3 — `mergeObject()` allows prototype
  poisoning of returned objects via unvalidated keys.
- Chain: `@tracertm/web` → `swagger-ui-react@5.32.14` → `swagger-client@3.38.0`
  → `deepmerge@~4.3.0`.
- Why it cannot be bumped: `4.3.1` **is** the newest published release and the
  OSV record lists no fixed version in any line. `swagger-client` depends on
  `deepmerge@~4.3.0` in every published version including the latest `3.38.4`.
- Reachability: `swagger-ui-react` is genuinely used —
  `apps/web/src/components/api-docs/swagger-ui-wrapper.tsx`. The merge input is
  our own OpenAPI document served by our own backend, so an attacker would need
  to control the spec to reach the vulnerable path.
- Options, in order of preference:
  1. Replace the API-docs page with a renderer that does not pull
     `swagger-client`. Removes the dependency instead of suppressing it. Cost:
     one component plus its fixtures.
  2. Time-boxed `[[IgnoredVulns]]` entry in `frontend/osv-scanner.toml` with a
     reason and `ignoreUntil`, matching the convention already used for the Rust
     exceptions.

## Residual 2 — `block-buffer@0.10.4`

- Advisory: `GHSA-qwgh-2vcv-g2f7`, CVSS 6.3 — a caught panic can leave the
  `EagerBuffer`/`ReadBuffer` cursor corrupted, allowing out-of-bounds
  reads/writes.
- Chain: `digest@0.10.7` → `sha1@0.10.7` (`axum`, `headers`, `tungstenite`),
  `sha2@0.10.9` (`sqlx-core`), `crc-fast@1.10.0` (`aws-smithy-checksums` →
  `aws-sdk-s3`).
- Why it cannot be bumped here: the fix lands in `block-buffer@0.12.1`, which
  requires `digest@0.11`, which requires `axum`, `sqlx` and
  `aws-smithy-checksums` to migrate first. Every one of those is a third-party
  crate we do not control; our direct dependencies (`axum 0.8.9`, `sqlx 0.9.0`,
  `aws-sdk-s3 1.155.0`) are current and do not accept `digest 0.11` yet.
- Reachability: requires a panic to be caught mid-hash and the buffer reused
  afterwards. No such pattern exists in this repository's code.
- Options: wait for the upstream migration, or a time-boxed ignore with a
  reason and expiry. Nothing in this repo can remove it.

## Unrelated observation

`bun run build` regenerates `frontend/apps/web/src/api/schema.ts` with
~6,000 changed lines, i.e. the committed artifact does not match the current
generator output. It was restored rather than committed; whether the drift
predates this work is **not established**. It is noted here so the next person
does not mistake it for churn introduced by the dependency bumps.
