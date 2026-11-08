# Duplicate clone salvage audit, 2026-11-07

Audit of the two checkouts of `KooshaPari/Tracera` and the disposition of the uncommitted
work found in the stale one.

| Checkout  | Path                                                     | State at audit                                                                                          |
| --------- | -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| Canonical | `/Users/kooshapari/CodeProjects/Phenotype/repos/Tracera` | clean, `main` at `f4ae670b5d`, up to date with `origin/main`                                            |
| Duplicate | `/Users/kooshapari/CodeProjects/Tracera`                 | `main` at `2c871ff0ea` (2026-10-16), 78 commits behind `origin/main`, with staged and untracked residue |

The duplicate clone was left in place. Nothing was deleted, and no branch or ref in the
duplicate was rewritten.

## Duplicate residue inventory

`git status` in the duplicate reported exactly four staged paths and two untracked paths:

| Path                                               | Index state      | Disposition                                           |
| -------------------------------------------------- | ---------------- | ----------------------------------------------------- |
| `crates/tracera-server/src/router.rs`              | modified, staged | already upstream; not copied                          |
| `crates/tracera-server/src/routes/codex.rs`        | added, staged    | already upstream; not copied                          |
| `crates/tracera-server/src/routes/equivalences.rs` | added, staged    | already upstream; not copied                          |
| `crates/tracera-server/src/routes/libraries.rs`    | added, staged    | already upstream; not copied                          |
| `tracera-w6-export-import-RESULT.md`               | untracked        | **salvaged** to `TRACERA-W6-EXPORT-IMPORT-RECEIPT.md` |
| `.worktrees/`                                      | untracked        | excluded by instruction; contents inventoried below   |

## The four staged source files are byte-identical to merged upstream work

The duplicate's index was written to a tree object and compared with the tree of the
upstream commit that introduced the same change:

```text
duplicate staged tree : 4d6d314a9842b9f8bf22c175f6b875d2e2bda6e4
upstream e0ae7d295 tree: 4d6d314a9842b9f8bf22c175f6b875d2e2bda6e4   (identical)

duplicate HEAD        : 2c871ff0ea6afb599fca62124c59f27e3e668d72
upstream e0ae7d295 parent: 2c871ff0ea6afb599fca62124c59f27e3e668d72 (identical)
```

`e0ae7d295` is `fix(server): enforce honest W8 route contracts (#1144)`, merged into
`origin/main`. The duplicate clone was sitting on that commit's parent with the commit's
own tree staged in the index. The staged work was therefore never unique to the duplicate;
it is upstream commit `e0ae7d295` itself.

Upstream then superseded it. `9977063f9`
(`fix(server): make unresolved route families explicitly unavailable (#1145)`, also merged)
rewrote all three route modules onto the shared `not_implemented` handler and moved module
declaration out of `router.rs` into `routes/w9.rs`. Per-file hashes of the duplicate's
staged blobs matched `e0ae7d295` exactly for `codex.rs`, `equivalences.rs`, `libraries.rs`
and `router.rs`.

### Canonical already carries a strict superset of the route coverage

Route template sets were extracted from each variant. Every path present in the duplicate
is present in canonical, and canonical registers strictly more:

| Module                   | Duplicate (`e0ae7d295`) | Canonical (`origin/main`) | Duplicate paths missing from canonical |
| ------------------------ | ----------------------- | ------------------------- | -------------------------------------- |
| `routes/codex.rs`        | 1 path                  | 4 paths                   | none                                   |
| `routes/equivalences.rs` | 3 paths                 | 17 paths                  | none                                   |
| `routes/libraries.rs`    | 5 paths                 | 5 paths                   | none                                   |

Across the whole `crates/tracera-server/src` tree, canonical registers 535 route
templates against the duplicate's 219. The only paths appearing in the duplicate and not
in canonical are `/api/v1/items/real-id` (a literal in a test assertion) and ten journey
paths that canonical registers dynamically through
`routes/journeys.rs` (`format!("{prefix}/journeys{suffix}")` over the `/api/v1` and
`/api/v1/projects/{project_id}` prefixes), which a static string scan cannot see.

### Copying the staged files verbatim does not compile

The literal instruction was executed and measured before deciding. Copying all four files
over canonical's produced four compile errors:

```text
error[E0432]: unresolved import `crate::handlers::ingest_api::ingest_agileplus`
error[E0433]: cannot find `w9_routes` in `super`   (routes/graph.rs:302)
error[E0433]: cannot find `w9_routes` in `super`   (routes/items.rs:121)
error[E0603]: constant `MAX_REQUEST_BODY_BYTES` is private
```

The cause is that the duplicate's `router.rs` predates the `w9_routes` module, the
`ingest_agileplus` handler split, and the `pub(crate)` visibility of
`MAX_REQUEST_BODY_BYTES`. Copying it wholesale would have reverted roughly three weeks
of upstream routing, ingest, search, journeys, export/import and auth work.

Copying only the three route modules also failed the test build, because canonical's
`routes/w9.rs` collects `codex::ROUTES`, `equivalences::ROUTES` and `libraries::ROUTES`
into its `templates()` list, and the duplicate's `#1144` modules do not export `ROUTES`:

```text
error[E0425]: cannot find value `ROUTES` in module `codex`
error[E0425]: cannot find value `ROUTES` in module `equivalences`
error[E0425]: cannot find value `ROUTES` in module `libraries`
```

Canonical already declares all three modules in `routes/w9.rs` via `#[path = "..."]` and
merges them through `w9_routes::routes()`. There is no `routes/mod.rs` in canonical, so
no module declarations were added and the existing layout was left untouched.

## Compile verdict on the salvaged branch

The branch content is documentation only, so the compile verdict is that of canonical
`origin/main` unchanged:

| Command                                 | Result                                                  |
| --------------------------------------- | ------------------------------------------------------- |
| `cargo check -p tracera-server`         | exit 0                                                  |
| `cargo check -p tracera-server --tests` | exit 0                                                  |
| `cargo test -p tracera-server`          | exit 0, 279 passed, 0 failed, 3 ignored across 6 suites |

## Excluded from the salvage

`.worktrees/` was excluded by instruction. It holds three receipts for upstream pull
requests that are all merged, none of which exists in canonical:

| File                            | PR    | Merge state                 | Lines not present in the PR body |
| ------------------------------- | ----- | --------------------------- | -------------------------------- |
| `tracera-w5-journeys-RESULT.md` | #1149 | MERGED 2026-10-17T02:00:39Z | 20 of 24 substantive lines       |
| `tracera-w7-search-RESULT.md`   | #1146 | MERGED 2026-10-17T01:54:58Z | 28 of 30 substantive lines       |
| `tracera-w10-auth-RESULT.md`    | #1147 | MERGED 2026-10-17T01:55:38Z | 23 of 23 substantive lines       |

They remain readable in the duplicate clone, which was not deleted. Only the W6 receipt
was salvaged because it was the one residue the instruction named directly.

## Other stale refs in the duplicate

The duplicate's `origin/main` was itself stale until fetched. Local branches that have no
`origin/` counterpart are old points on upstream history rather than unmerged work: each
is 26 to 27 commits behind `origin/main`. Spot checks at file-content level found their
changes already upstream, for example `docs/operations/items-store.md` on
`fix/items-store-prettier` is byte-identical to upstream and upstream passes
`prettier --check` on it. No unique source work was found on them.

## Method notes

Two verification approaches in this audit were unreliable and were discarded in favour of
direct measurement:

- `git patch-id` over all upstream commits computed only 27 unique identifiers, which
  made every branch look non-upstream. The identifier set was incomplete, so the
  conclusion was wrong.
- `git cherry` reports `+` for commits that upstream reached through a squash merge,
  because the squashed upstream commit has a different patch id from the original. It
  reported 12 "unique" patches on `stubs/w5-journeys-20261016` whose subjects are
  plainly upstream merges.

The tree-hash comparison and the file-content comparison are direct measurements and
stand on their own.
