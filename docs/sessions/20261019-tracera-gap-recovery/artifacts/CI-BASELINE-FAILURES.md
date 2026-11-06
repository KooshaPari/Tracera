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

### Correction: RUSTSEC-2026-0381 needed no pre-release

An earlier version of this note claimed one instance of `RUSTSEC-2026-0381`
remained, pinned by `neo4rs 0.8.0` through `webpki-roots 0.26.11`, and that only
a pre-release `neo4rs` could clear it. **That was wrong, and it was wrong in a
way that produced an unnecessary draft PR.**

The advisory's affected ranges are `[0.0.0-0, 0.26.11)` and
`[0.26.12-0, 1.0.10)`. So `0.26.11` is the _fix_ for the first range, not a
vulnerable version. The copy actually flagged was `webpki-roots 1.0.9`, which
#1203 already bumps to `1.0.10`.

Two independent confirmations, because the first one I ran earlier was misread:

| Source                      | Observed                                                    |
| --------------------------- | ----------------------------------------------------------- |
| `cargo-deny` block for 0381 | names `Cargo.lock:424 │ webpki-roots 1.0.9`                 |
| `api.osv.dev` query         | `webpki-roots@0.26.11` clean; `webpki-roots@1.0.9` affected |

The mistake was reading a `grep` for `webpki-roots <version>` and taking a
definition line from `Cargo.lock` as the flagged line. `cargo-deny` prints the
offending package in its own block; that is the line to read.

Consequence: **#1203 closes all three advisories by itself.** On its branch,
`cargo deny check advisories` reports `ok`. `neo4rs` stays on stable `0.8.0`.
Draft PR #1207, which adopted the `0.9.0-rc.10` pre-release, was built on the
misreading and has been closed.

The captured evidence from that probe is still worth keeping, as a fact about
`neo4rs` rather than a recommendation: upgrading to `0.9.0-rc.10` costs one
manifest line plus removing one `.await`, because `Graph::new()` became
synchronous, and `webpki-roots` leaves the graph entirely. `webpki-roots` is a
non-optional dependency of `neo4rs 0.8.0` with no feature gate, so it cannot be
removed by configuration. None of that is needed now.

What remains true: do not add a `deny.toml` ignore to silence an advisory, and do
not read a red `lint-rust` as a defect in the D-04 work. It is a dependency
finding, separate from the CLI behaviour under audit.

### 10.1 `osv`: npm advisories, all baseline

`osv` fails for two independent reasons. One is the Rust advisory above. The
other is npm advisories that live in `frontend/bun.lock`, a file none of these
PRs touch, so they are pre-existing debt newly surfaced by the scan rather than
anything introduced here. All are closed by PR #1204.

**Do not treat the count as stable.** It was five on the first scan, eight by
the time #1204 was written, and eleven by the per-version check below, because
the advisory database keeps growing. The durable claim is not "N advisories
fixed" but: for every package #1204 touches, the resolved version is clean
under `api.osv.dev`, and the previously-resolved version was not. That is what
the table below now records, and it does not rot when a new id is published
against an old version.

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
Two are a pair: GHSA-xp26-3454-mjgp is specifically a bypass of the fix for
GHSA-qxg6-89mg-rqv8, so taking one without the other is pointless.

Per-version verification, queried against `api.osv.dev` directly rather than
inferred from a scan log. This is the mapping that matters: each resolved
version was queried individually, and the old version alongside it as a control.

| Package                         | Resolved | Verdict | Old version | Verdict      |
| ------------------------------- | -------- | ------- | ----------- | ------------ |
| `follow-redirects`              | 1.16.1   | clean   | 1.16.0      | 2 advisories |
| `vite`                          | 8.2.4    | clean   | 8.2.2       | 6 advisories |
| `storybook` / `@storybook/core` | 8.6.19   | clean   | 8.6.17      | 1 advisory   |
| `vitest` / `@vitest/mocker`     | 4.1.12   | clean   | 4.1.11      | 2 advisories |

`vite` carried six, not the three the earlier table listed. The three extra ids
are also fixed by 8.2.4, so the change already covers them, but the earlier
count understated the work.
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
needs root at all.

What is actually established, and what is not:

| Claim                                                               | Status                    | Evidence                                                                                                                                                                       |
| ------------------------------------------------------------------- | ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| The workflow no longer invokes `sudo`                               | observed                  | `grep -c sudo` is 1 on `main`, 0 on the branch                                                                                                                                 |
| The job's step list is Checkout, Install Prettier, prettier check   | observed                  | workflow content on the branch                                                                                                                                                 |
| The workflow file is valid                                          | observed                  | `actionlint` clean                                                                                                                                                             |
| The job passes with the step removed                                | observed                  | run 39691676041, job 119539098206, 6 steps, success                                                                                                                            |
| The remaining steps run with no `sudo` available                    | **observed by execution** | ran `npm install --global --ignore-scripts prettier@3.6.2` and `prettier --check` in a shell where `sudo -n` reports "a password is required"; install succeeded, check passed |
| The job passes **on `desk-tracera-1`**, the runner it was broken on | **not observed**          | only one run exists, and it landed on a GitHub-hosted runner                                                                                                                   |

The last row is a gap that is externally blocked rather than skipped. The desk
runner registers under the same `ubuntu-latest` label as the hosted ones, and
this workflow has no `workflow_dispatch`, so the desk slot cannot be targeted
and the only way to obtain that observation is scheduling luck.

What does hold is stronger than inspection: the offending step is deleted, the
workflow contains no `sudo` at all, and every remaining command was executed in
a shell with the same constraint and succeeded. The failure mode is removed
rather than worked around, so the result is better even without a desk-slot run.

Worth remembering: this failure looked identical to a real format violation in
the check list. Only reading the step log showed that no formatting check ever
ran. Do not read a red `Lint & Format` on a self-hosted runner as a formatting
result without confirming the job got past step 3.

### 10.4 A stale `bun.lock` breaks frontend CI on every PR

Found while refreshing a branch that had changed nothing under `frontend/` and
still failed `checks` at step 4 ("Install frontend deps") and `smoke` at step 5
("Build frontend bundle").

Reproduced on a clean `origin/main` checkout:

```
$ bun install --frozen-lockfile
error: lockfile had changes, but lockfile is frozen
```

Cause: the last three Dependabot commits that touched
`frontend/apps/web/package.json` touched `frontend/bun.lock` zero times
(`12cf873e2` #1216, `a21c8dfd3` #1222, `72f4c799c` #1219). The manifests moved
ahead of the lock and stayed there, so the frozen install step fails before any
frontend test runs. Every PR touching the frontend is affected, not one branch.

Fixed by PR #1249: the regenerated lockfile only, with both `package.json` files
untouched. Verified `bun install --frozen-lockfile` clean and the full web suite
at 216 files / 4323 tests passing.

The detail worth remembering: **one `bun install` pass does not fix it.** The
first pass rewrites the lock, a second converges, and frozen only passes after
that. That is why the staleness survived: a plain local `bun install` reports
success and hides it. If it recurs, check `bun install --frozen-lockfile`
directly, and consider having Dependabot update the lock or having CI assert it
on `main` itself.
