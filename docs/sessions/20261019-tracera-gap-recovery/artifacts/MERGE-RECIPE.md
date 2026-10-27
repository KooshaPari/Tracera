# Verified four-PR merge recipe

Split out of `00_SESSION_OVERVIEW.md` (formerly its section 9). The conflict and its resolution were established by simulation in a throwaway worktree, not by reading diffs.

All four PRs were merged into a throwaway worktree to find conflicts before
the operator hits them. Each PR merges cleanly into `main` on its own. In
combination there is exactly one real conflict, between #1132 and #1158.

The conflict is two files: `docs/audit/TRACERA-GAP-INVENTORY.csv` and
`docs/audit/TRACERA-GAP-ISSUES.md`. It is decidable rather than a judgement
call, because #1158's inventory is a strict subset of #1132's:

| Branch                                          | GAP rows | VIEW rows | GAP ids present  |
| ----------------------------------------------- | -------- | --------- | ---------------- |
| `audit/instinct-live-evidence-20261014` (#1132) | 29       | 44        | GAP-001..GAP-029 |
| `docs/instinct-state-forward-20261017` (#1158)  | 23       | 44        | GAP-001..GAP-023 |

Both files contain exactly `GAP-001..023` on both branches, and #1132 adds
`GAP-024..029`. Nothing is unique to #1158 in either file, in both the CSV
row ids and the `### [Instinct] GAP-nnn` headings.

Verified order, which leaves no conflict to resolve by hand beyond taking
#1132's side on those two files:

1. Merge #1158.
2. Merge #1132, resolving the two gap files with `git checkout --theirs --
docs/audit/TRACERA-GAP-INVENTORY.csv docs/audit/TRACERA-GAP-ISSUES.md`.
3. Merge #1150 and #1173; both apply cleanly.

A note on two workflow files. `.github/workflows/ci.yml` and `ci-agents.yml`
appear to "lose" the PR branches' blacksmith runner options in that merge.
They are not lost by the merge: `main` removed those options itself in
`6f94d38d8` ("ci: gate workflows to self-hosted desk runners", #1202), and
the branches predate that removal, so main's deletion correctly wins the
three-way merge.

Post-merge state of the combined tree, all observed:

| Check                                       | Result                      |
| ------------------------------------------- | --------------------------- |
| `ruff check .`                              | All checks passed           |
| `ruff format --check .`                     | 242 files already formatted |
| `python3 scripts/verify_evidence_hashes.py` | 109/109 verified, PASS      |
| prettier on files changed vs `main`         | clean                       |
| `crates/tracera-cli/src/*` vs #1173         | byte-identical              |

Shared config is deliberately byte-identical across branches so this stays
true: `.prettierignore` in #1132 and #1158, and `.sonarcloud.properties`
plus the `[tool.mypy]` block in #1158 and #1173.

## Land order once the two dependency PRs exist

Two more PRs were opened after the original four-PR simulation, and one of them
changes the recommended order:

| PR    | Purpose                                                                          | State                                               |
| ----- | -------------------------------------------------------------------------------- | --------------------------------------------------- |
| #1205 | delete the unused `jq` install that fails `Lint & Format` on self-hosted runners | MERGEABLE, 61 checks, **0 failing**                 |
| #1203 | three RUSTSEC-2026 TLS patch bumps                                               | MERGEABLE, closes all three advisories              |
| #1204 | npm advisories (count drifts; 11 at last check)                                  | MERGEABLE, red only on `Cargo.lock` Rust advisories |

#1205 is the only fully green PR in the set, so it should land first. It removes
the `sudo` requirement from the `Trunk Check` workflow's `Lint & Format` job,
which is currently producing false red on #1173 and #1204 for a reason unrelated
to their content.

Important detail: a PR's `Lint & Format` check runs the workflow from that PR's
own branch, so #1173 and #1204 keep failing it even after #1205 is approved.
They need to be updated from `main` after #1205 merges before that check can go
green.

#1203 closes all three Rust advisories on its own: `cargo deny check advisories`
reports `ok` against its committed lockfile. An earlier note here said it closed
only two and that the third needed an operator decision on a `neo4rs`
pre-release. That was wrong, and the draft PR built on it (#1207) has been
closed. `RUSTSEC-2026-0381` affects `[0.0.0-0, 0.26.11)` and
`[0.26.12-0, 1.0.10)`, so the `0.26.11` copy that `neo4rs 0.8.0` pins is the fix
for the earlier range; the flagged copy was `webpki-roots 1.0.9`.

#1204 closes the npm set and verifiably drops `osv`'s npm rows to zero. It is
still red on `osv` and `Rust dependency policy` only because those jobs also
scan `Cargo.lock`, so it needs #1203 alongside it to see both sides clean.

## Observed gate results after re-running the advisory PRs

The claims above were originally based on running the gates locally. Re-running
the actual CI jobs gives observed results from the project's own gates, which is
stronger, and it changed one conclusion.

`RUSTSEC-2026-0381`'s affected ranges were revised upstream: the advisory now
covers `[0.0.0-0, 0.26.11)` and `[0.26.12-0, 1.0.10)`. So the `webpki-roots
0.26.11` copy that `neo4rs 0.8.0` pins is the fix for the earlier range, not a
vulnerable version, and the flagged copy was `webpki-roots 1.0.9`. Two
consequences: #1203 closes all three advisories by itself, and the draft
`neo4rs 0.9.0-rc.10` upgrade (#1207) was unnecessary and is closed.

Observed on #1203 after re-running its failed jobs:

| Gate                     | Result                    | What it means                                        |
| ------------------------ | ------------------------- | ---------------------------------------------------- |
| `ci-agents / lint-rust`  | **success**               | `cargo deny check` passes                            |
| `ci-agents / required`   | **success**               | the aggregator agrees                                |
| `Rust dependency policy` | **success**               | second `cargo deny` entry point passes               |
| `osv`                    | failure, **Rust rows: 0** | all remaining rows are npm, from `frontend/bun.lock` |

That last row is the useful one. `osv` on #1203 is red only because it also
scans `frontend/bun.lock`, which #1203 does not touch. Its 12 remaining rows are
all npm (`storybook`, `vite` ×6, `follow-redirects` ×2, `@vitest/mocker` ×2).

The mirror image holds for #1204: its `osv` run reports **zero npm rows**, and
is red only on the Rust advisories from `Cargo.lock`. Neither PR is red on the
surface it changes. Both must land for `osv` to be green overall.

Note the count drift: `vite 8.2.2` alone carries six advisories now, not the
three an earlier table listed. The three extra ids are also fixed by `8.2.4`.
When reporting this work, do not lead with an advisory count — it moves. Lead
with the per-version mapping: the resolved version is clean, the previous one
was not.

## The full advisory chain, verified end to end

Reading each PR's gate result separately was not enough, because every
individual PR is red on a surface it does not change. Building the combined
state and running the real workflow is what settled it.

Combined branch (Rust bumps + npm overrides), `Dependency audit` run
39720656685:

| Job                      | Result                                |
| ------------------------ | ------------------------------------- |
| `Rust dependency policy` | success                               |
| `osv`                    | failure, with **exactly one** finding |

That one finding was:

```
GO-2026-6809 | Go | stdlib | 1.26.9 | sidecar/go/go.mod
```

`GO-2026-6809` **aliases `RUSTSEC-2026-0381`, `-0382` and `-0383`**. It is the
same upstream certificate-distrust event reached through Go stdlib instead of
`rustls`. So the advisory work was always a three-ecosystem problem, and the
third one was invisible while `osv` was failing on the other two.

Bumping `sidecar/go/go.mod` from `go 1.26.9` to `go 1.26.10` closes it. Same
workflow, run 39721425994:

| Job                      | Result                     |
| ------------------------ | -------------------------- |
| `Rust dependency policy` | success                    |
| `osv`                    | **success, zero findings** |

So the complete set is four PRs, not three: #1203 (Rust), #1204 (npm), #1208
(Go stdlib), and #1205 for the workflow hygiene that was masking format results.
Land all four and the dependency gates are green with no suppressions.

Recorded but not fixed: `crates/tracera-go-cli/go.mod` declares `go 1.22`, also
below the fixed versions, but that module is not in `osv`'s scan targets
(`Cargo.lock`, `frontend/bun.lock`, `sidecar/go/go.mod`). Changing it would not
move the gate; widening the scan surface is a separate decision.

## Final shape: one advisory PR, not three

Splitting the advisory work by ecosystem was a mistake worth recording. The
dependency gates scan `Cargo.lock`, `frontend/bun.lock` and `sidecar/go/go.mod`
together, so each ecosystem-split PR was permanently red on the surfaces the
other two fix. None of them could go green alone, which meant the operator would
have had to merge three partially-red PRs to discover whether the combination
worked.

Consolidated into **PR #1209** (`chore/dependency-advisories`), which carries all
four fixes:

| File                                 | Change                                                                                       |
| ------------------------------------ | -------------------------------------------------------------------------------------------- |
| `Cargo.lock`                         | `rustls-webpki` 0.103.16, `webpki-root-certs` 1.0.10, `webpki-roots` 1.0.10                  |
| `frontend/package.json` + `bun.lock` | overrides for `follow-redirects` 1.16.1, `vite` ~8.2.4, `storybook` 8.6.19, `vitest` ^4.1.12 |
| `sidecar/go/go.mod`                  | `go 1.26.9` to `go 1.26.10`                                                                  |

Observed state of #1209: **0 failing, 59 passing**, one pending
(`Kilo Code Review`, a rate-limited third-party bot). The dependency gates
specifically: `osv` pass, `Rust dependency policy` pass, `ci-agents / lint-rust`
pass, `Rust Test` pass.

#1203, #1204 and #1208 are closed as superseded, with commit history preserved
in #1209. Draft #1207 was closed earlier as unnecessary.

One transient worth noting so it is not re-diagnosed: `plan` failed once on
#1209 and passed on re-run. It failed on `desk-tracera-1` with `steps=0` while
the same job on `main` ran 3 steps on a GitHub-hosted runner and succeeded. Same
dead-runner signature as everything else above.

## Refresh note: main gained a fourth advisory

Refreshing the advisory PR onto `main` (`12cf873e2`) exposed a new one that the
branch had never seen, because it arrived on main after the work started.

`cargo deny check` on a clean `origin/main` now reports **four** advisories:

| Advisory          | Crate               | Disposition                |
| ----------------- | ------------------- | -------------------------- |
| RUSTSEC-2026-0381 | `webpki-roots`      | fixed by #1209             |
| RUSTSEC-2026-0382 | `rustls-webpki`     | fixed by #1209             |
| RUSTSEC-2026-0383 | `webpki-root-certs` | fixed by #1209             |
| RUSTSEC-2026-0387 | `crypto-bigint`     | **not fixable downstream** |

So #1209 takes main from 4 advisories to 1. It cannot reach zero, and its
`Rust dependency policy` and `osv` checks will therefore stay red.

0387 is a constant-time timing-variability flaw in `crypto-bigint`; its only
fixed range is `>= 0.7.6`. The offending copy is `0.5.5`, reached through:

```
crypto-bigint 0.5.5 <- aws-sigv4 1.6.3 <- aws-runtime <- aws-sdk-s3 1.155.0 <- tracera-server
```

`aws-sigv4 1.6.3` is the newest published release and still requires
`crypto-bigint ^0.5`, so there is nothing to bump to. The two real options are
waiting for upstream, or a documented `deny.toml` / `osv-scanner.toml`
exception. The second is not done in #1209 on purpose: it is a suppression
decision, the repo has clear precedent for it, and it belongs to the operator
rather than to a dependency-bump PR.

Lesson for the next pass: an advisory branch is only as current as its base.
Refresh it against `main` before declaring the advisory set closed, because new
advisories arrive on `main` independently of the branch.
