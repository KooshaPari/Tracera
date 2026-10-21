# CI failures that are baseline, not PR defects

Split out of `00_SESSION_OVERVIEW.md` (formerly its section 10). Three separate causes are recorded here so no future reader attributes any of them to the D-04 work.

PR #1173's latest run failed `ci-agents / lint-rust` on `cargo-deny`
`advisories`. That is unrelated to the D-04 changes: it reproduces on a clean
`origin/main` checkout, and `main` never surfaced it because it skipped the job
(no Rust changes detected, so the advisory database moved on unnoticed).

Three advisories, all published after main's last Rust-touching run:

| Advisory          | Crate               | Installed         | Fix         |
| ----------------- | ------------------- | ----------------- | ----------- |
| RUSTSEC-2026-0382 | `rustls-webpki`     | 0.103.15          | >= 0.103.16 |
| RUSTSEC-2026-0383 | `webpki-root-certs` | 1.0.8             | >= 1.0.10   |
| RUSTSEC-2026-0381 | `webpki-roots`      | 1.0.9 and 0.26.11 | >= 1.0.10   |

PR #1203 (`chore/rustsec-2026-0381-0383`) applies the three patch bumps, which
closes 0382, 0383 and the 1.x instance of 0381. Verified there:
`cargo check --workspace --all-targets` clean, `cargo test --workspace` 378
passed / 0 failed / 1 ignored.

One instance of RUSTSEC-2026-0381 remains: `webpki-roots 0.26.11`, pinned by
`neo4rs 0.8.0` via `tracera-server` and `tracera-neo4j`. It is not suppressed.
`0.8.0` is the latest stable `neo4rs`; only `0.9.0-rc.10`, a pre-release, moves
to `webpki-roots` 1.x, and adopting it means changing the manifest to a release
candidate of a database driver. That is an operator decision, so `lint-rust`
stays red on #1173 and on #1203 until it is made. Do not read that check as a
defect in the D-04 work.

### 10.1 `osv`: five npm advisories, all baseline

`osv` fails for two independent reasons. One is the Rust advisory above. The
other is five npm advisories that live in `frontend/bun.lock`, a file none of
these PRs touch, so they are pre-existing debt newly surfaced by the scan rather
than anything introduced here.

| Advisory            | CVSS | Package                        | Installed | Fixed in |
| ------------------- | ---- | ------------------------------ | --------- | -------- |
| GHSA-q3jh-wrc6-jgq8 | 8.2  | `follow-redirects`             | 1.16.0    | 1.16.1   |
| GHSA-8r9p-f939-6h3c | 8.2  | `follow-redirects`             | 1.16.0    | 1.16.1   |
| GHSA-f2ph-cmg5-wxc8 | 9.4  | `storybook`, `@storybook/core` | 8.6.17    | 8.6.19   |
| GHSA-587h-7wmj-h5pm | 7.5  | `vite` (launch-editor)         | 8.2.2     | 8.2.4    |
| GHSA-698v-4r3x-3vcv | 6.3  | `vite` (launch-editor)         | 8.2.2     | 8.2.4    |
| GHSA-r825-w8mm-5pxw | 6.3  | `vite` (launch-editor)         | 8.2.2     | 8.2.4    |
| GHSA-xp26-3454-mjgp | 5.9  | `@vitest/mocker`               | 4.1.11    | 4.1.12   |
| GHSA-qxg6-89mg-rqv8 | 4.7  | `@vitest/mocker`               | 4.1.11    | 4.1.12   |

The storybook entry surfaced in a later scan run, not the first one: it is a
critical (9.4) missing-origin-validation flaw in the Storybook **preview dev
server**, fixed in 8.6.19. Like the `vite` ids it is dev-server only, but a 9.4
is worth closing rather than leaving to a follow-up.

Fix versions were read from `api.osv.dev`, not assumed. All are patch-level.
Two of the eight are a pair: GHSA-xp26-3454-mjgp is specifically a bypass of
the fix for GHSA-qxg6-89mg-rqv8, so taking one without the other is pointless.
The vitest pair also surfaced only on a later scan, after the first six were
already fixed, which is why the count grew from five to eight across passes.
They were kept out of the Rust advisory PR so a frontend lockfile bump would not
hide inside a `Cargo.lock` change; they are fixed instead in PR #1204
(`chore/frontend-advisory-pins`). Note the repo already documents two other
`osv-scanner.toml` filters with written justifications, so there is precedent for
filtering only where no fix exists; here a fix does exist, so upgrading is the
right remedy.

Two traps in that upgrade, both verified: `follow-redirects` is transitive via
axios, so bumping it directly leaves the axios path on 1.16.0 and adds a second
copy; only an `overrides` entry moves it. And `vite` already carried a
`^8.0.0-beta.11` override, so any 8.x range let bun resolve 8.3.5, dragging
`rolldown` 1.2.6 to 1.2.15 plus 20+ platform bindings. `~8.2.4` is the narrow
range that takes the patch and leaves `rolldown` alone.

### 10.2 A dead self-hosted runner, not a test failure

`ci-agents / test-py (3.13)` failed on PR #1173 while `3.12` passed on the same
commit, and #1158 passed `3.13` entirely. The job's evidence shows why:

| Signal  | Observed                        |
| ------- | ------------------------------- |
| runner  | `desk-tracera-1` (self-hosted)  |
| steps   | empty — no step ever completed  |
| job log | `BlobNotFound` — never uploaded |

A job that produces no steps and no log did not run the tests. Treat
`test-py (3.13)` on this branch as a runner infrastructure failure, distinct from
the advisory failures above. The earlier `Rust Build` failure on #1173 was the
same runner exhibiting the same signature.
