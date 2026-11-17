# Agent-harness portfolio authority matrix

Captured 2026-07-31 08:02:10 UTC after preservation snapshots. This is an
evidence index, not a merge or release decision. No reset, clean, delete,
prune, or force-push was used.

## Canonical repositories

| repo | canonical remote(s) | local checkout / branch / HEAD | remote `main` | root status | preservation ref |
|---|---|---|---|---|---|
| Agentora | `origin=git@github.com:KooshaPari/Agentora.git`; `source-agent-platform=git@github.com:KooshaPari/agent-platform.git` | `main` / `c7edae858b264e075210a7b5fc574b3d0da4fe4d` (behind 10) | `18ac86833e48875765ca5ee37a01ce819190bb10` | clean root; provenance worktree dirty | `origin/wip/20260731T0734-18c74f9676ad4a80` -> `32e135466c8a9075acca6b18ae5bda6beba1d733` |
| forgecode | `origin/upstream=git@github.com:tailcallhq/forgecode.git`; `fork=git@github.com:KooshaPari/forgecode.git` | `preserve/workflow-schema-wave-20260729` / `1f039b801b4ed6d5160f4c8c6bf57b2d510056f2` (dirty; behind upstream) | `43d6be453342abbffaea194837665a7a781b823c` (fork `main` `74db8b5b7a4265f62ffb35f9dc452c081f857d73`) | dirty/untracked; Airlock push to upstream denied | `fork/wip/20260731T0727-18c74f31b4e4cf68` -> `1f039b801b4ed6d5160f4c8c6bf57b2d510056f2` |
| helios-cli | `origin=git@github.com:KooshaPari/helios-cli.git`; `upstream=git@github.com:openai/codex.git` | `wip/20260722-helios-harness-preservation` / `d01cafa3a81544c94f8997f0f717506da6158d9d` | `36349bb901482c29dda146ee92bf7a149075f685` | 2 dirty files | `origin/wip/20260731T0727-18c74f32afb47b78` -> `d01cafa3a81544c94f8997f0f717506da6158d9d` |
| Tracera | `origin=git@github.com:KooshaPari/Tracera.git` | `preserve/tracera-dirty-wave-20260729` / `3c264baceae0705adaba667826f587fec83193a7` | `774c0061e8865bb6daf3b549b1f0ec91662d90ef` | dirty/untracked; ahead preservation branch | `origin/wip/20260731T0727-18c74f34b51891d8` -> `3c264baceae0705adaba667826f587fec83193a7` |
| pheno-harness | `origin=git@github.com:KooshaPari/pheno-harness.git` | `main` / `cf318e4fe2a6671c8cabd41bc3b08e30542c8629` | `cf318e4fe2a6671c8cabd41bc3b08e30542c8629` | dirty/untracked | `origin/wip/20260731T0727-18c74f367a1d64d0` -> `cf318e4fe2a6671c8cabd41bc3b08e30542c8629` |

## Worktree/branch inventory

`git worktree list --porcelain` was used for each canonical repository. The
inventory at capture included: Agentora 6 worktrees (including the missing
stale `sdk-ports-align` path); forgecode 13; helios-cli 4; Tracera 19; and
pheno-harness 4. Every existing dirty canonical root or worktree was retained;
the missing Agentora path was recorded as stale metadata and was not removed.
Existing ahead branches remain untouched and their branch names/HEADs are
available from each repository's `git worktree list --porcelain` output.

## Validation and limitations

- Each listed preservation ref was verified with `git ls-remote` against the
  stated remote immediately after creation.
- The forgecode default `origin` is upstream and rejected the Airlock push;
  the locally-created snapshot was then pushed non-force to the configured
  `fork`, and that fork ref was verified. No upstream mutation occurred.
- Snapshot refs preserve repository state at the capture point; they do not
  imply CI, ownership/license, provenance, replay, dogfood, or A+ completion.
- Root snapshots cover dirty root checkouts. Existing clean worktrees and
  already-pushed ahead branches remain reviewable and were not rewritten.
