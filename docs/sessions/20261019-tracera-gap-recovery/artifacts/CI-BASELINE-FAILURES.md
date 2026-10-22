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
`neo4rs 0.8.0`, which `crates/tracera-server` depends on. It is not suppressed.

An earlier draft of this note said the pin came via both `tracera-server` and
`tracera-neo4j`. That was wrong: `crates/tracera-neo4j` declares
`neo4rs = "0.7"` but is **not a workspace member**, so it never builds and its
declaration is inert. Only `tracera-server` matters, which means only one
manifest needs to change.

Draft PR #1207 measures what closing it actually costs, rather than leaving it
as an unknown:

| Change                               | Size                                                            |
| ------------------------------------ | --------------------------------------------------------------- |
| `crates/tracera-server/Cargo.toml`   | 1 line, `"0.8"` to `"0.9.0-rc.10"`                              |
| `crates/tracera-server/src/neo4j.rs` | 2 lines: `Graph::new()` is synchronous in 0.9, so `.await` goes |
| `Cargo.lock`                         | `webpki-roots` disappears with its tree                         |

That `.await` was the only compile error in the workspace. On #1207:
`cargo check -p tracera-server --all-targets` clean, `cargo test --workspace`
378 passed / 0 failed / 1 ignored, `cargo deny check advisories` ok, and
`bans`/`licenses`/`sources` ok so the pre-release trips no policy. Applying it
together with #1203's two patch bumps yields `advisories ok` with **zero**
advisories, verified in one probe rather than reasoned about.

It is a draft because adopting a release candidate of a database driver is a
product decision. Until it is made, `lint-rust`, `osv` and
`Rust dependency policy` stay red on every branch including `main`, because
`cargo-deny` reads the lockfile and does not care that the affected TLS path may
be unreachable at runtime. Do not add a `deny.toml` ignore to silence it, and do
not read the check as a defect in the D-04 work.

### 10.1 `osv`: eight npm advisories, all baseline

`osv` fails for two independent reasons. One is the Rust advisory above. The
other is eight npm advisories that live in `frontend/bun.lock`, a file none of
these PRs touch, so they are pre-existing debt newly surfaced by the scan rather
than anything introduced here. All eight are now closed by PR #1204.

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

A job that produces no steps and no log did not run the tests. This is a
runner infrastructure failure, not a test failure.

Four separate jobs have now failed this way, all on `desk-tracera-1`, all with
an empty step list:

| Job                          | PR    | Steps | Result  |
| ---------------------------- | ----- | ----- | ------- |
| `Rust Build`                 | #1173 | 0     | failure |
| `ci-agents / test-py (3.13)` | #1173 | 0     | failure |
| `Detect Languages`           | #1173 | 0     | failure |
| `Analyze (python)`           | #1173 | 0     | failure |

The rotating nature of it matters: each new run of the same commit can fail a
different job, which reads as a fresh regression each time. The signature to
match on is `steps=0` together with a `BlobNotFound` job log, not the job name.

For contrast, the failures that _do_ have steps are different in kind and each
has a real cause: `ci-agents / lint-rust` (12 steps, the RUSTSEC advisory),
`osv` (6 steps, the same advisory plus npm), and `Lint & Format` (7 steps, the
`Install jq` step below).

The runner also fails jobs _after_ they start. `ci-agents / security-scan
(javascript-typescript)` failed on #1204 at its `Upload Trivy SARIF` step, with
the job log truncated in the middle of Trivy's vulnerability-DB download. The
same job, same 8 steps, same workflow commit, succeeded on GitHub-hosted runners
for three other PRs:

| PR    | Runner           | Steps | Result  |
| ----- | ---------------- | ----- | ------- |
| #1150 | GitHub-hosted    | 8     | success |
| #1158 | GitHub-hosted    | 8     | success |
| #1173 | GitHub-hosted    | 8     | success |
| #1204 | `desk-tracera-1` | 8     | failure |

Worth flagging as a near miss: the failure presented as a workflow or action
misconfiguration, and the obvious "fix" would have been to change the SARIF
upload inputs. The comparison above shows there is nothing to fix in the
workflow. Do not modify CI config on the strength of a `desk-tracera-1` failure
alone; first check whether the identical job passes on a GitHub-hosted runner.

### 10.3 A vestigial sudo step failing the format gate

`Lint & Format` failed on runs scheduled to the self-hosted `desk-tracera-1`
runner, before reaching any linting, while passing on GitHub-hosted runners. So
the check's result depended on which runner picked it up, which is why the same
commit could be green on one run and red on the next.

On `desk-tracera-1` the job dies at its third step:

```
sudo: The "no new privileges" flag is set, which prevents sudo from running as root.
##[error]Process completed with exit code 1.
```

That step was `Install jq`, running `sudo apt-get update && sudo apt-get
install -y jq`. Two things were wrong with it: `desk-tracera-1` does not grant
passwordless sudo, and **`jq` is never used by that workflow**. It was a
dependency of `trunk-io/trunk-action`, which the workflow's own header comment
says it replaced with a direct prettier call. `grep -n jq
.github/workflows/trunk-check.yml` returned only the install line itself.

PR #1205 deletes the step rather than making it tolerant, so the job no longer
needs root at all. Verified with `actionlint` and by running the workflow's own
prettier invocation.

Worth remembering: this failure looked identical to a real format violation in
the check list. Only reading the step log showed that no formatting check ever
ran. Do not read a red `Lint & Format` on a self-hosted runner as a formatting
result without confirming the job got past step 3.
