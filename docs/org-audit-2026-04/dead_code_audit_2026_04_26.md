# Cross-Repo Dead-Code / Archive Subdir Audit — 2026-04-26

Pattern follow-up to today's wins:
- KDesktopVirt/`kvirtualstage-legacy/` deleted (commit `0abb04c`, **9** Dependabot alerts closed).
- Tracera/`ARCHIVE/CONFIG/default/` flagged for delete (~12 alerts; pending Tracera-recovered branch direction).

## Methodology

- Scanned all repos for subdirs matching `*legacy*`, `*deprecated*`, `*archive*`, `*backup*`, `*old*` (depth ≤ 3).
- Excluded `.archive/`, `.worktrees/`, `*-wtrees/`, `kitty-specs/`, `vendor/`, `node_modules/`, `target/`.
- Per candidate: collected size, file count, lockfile/manifest exposure (Dependabot risk), git provenance (last commits touching path), live-reference check by basename across `.rs|.toml|.go|.py|.ts|.yml`.

## Candidate Inventory

| # | Repo / Path | Size | Files | Lockfiles / Manifests | Last Commit (subj) | Live Refs (excl. self) | Score |
|---|-------------|------|-------|----------------------|--------------------|------------------------|-------|
| 1 | `helios-cli/codex-rs/execpolicy-legacy/` | 156K | 30 | `Cargo.toml` (workspace member) | `082349d7a sync: merge upstream main (#464)` | listed in `codex-rs/Cargo.toml` members; **0** code refs | **DELETE-CANDIDATE** |
| 2 | `heliosCLI/codex-rs/execpolicy-legacy/` | 156K | 30 | `Cargo.toml` (workspace member) | `acebd69 fix(ci): stabilize pr346 ...` | listed in `codex-rs/Cargo.toml` members; **0** code refs | **DELETE-CANDIDATE** |
| 3 | `phenotype-tooling/crates/legacy-scan/` | 12K | 3 | `Cargo.toml` (workspace member) | `c37538b feat: scaffold phenotype-tooling workspace ...` (only commit) | only listed in workspace `Cargo.toml`; never used; redundant with `tooling/legacy-enforcement` purpose | **NEEDS-AUDIT** (might be intentional scaffold) |
| 4 | `PhenoProc/crates/bifrost-routing-backup/` | 24K | 4 | (no `Cargo.toml`; bare `src/`) | `dcb1b26 fix: restore and fix PhenoProc workspace crates` | **0** refs in workspace; not in `[workspace] members` | **DELETE-CANDIDATE** |
| 5 | `Tracera-recovered/docs/archive/` | 616K | 42 | none | `fefa970f chore(deps): bump fastmcp (#318)` (touch only) | docs only; no source refs | **DELETE-CANDIDATE** |
| 6 | `Tracera-recovered/data/backup/` | 28K | 7 | none | `fefa970f chore(deps): bump fastmcp (#318)` (touch only) | data dump; no refs | **DELETE-CANDIDATE** |
| 7 | `agslag-docs/archive/` | 6.8M | 38 | none | `252ffe0 T` (single commit) | docs only | NEEDS-AUDIT (size; verify content first) |
| 8 | `Dino/docs/archive/` | 924K | 64 | none | `584f0b17 fix: skip catalog and phase7 ...` | docs only | KEEP (recent commit, active project) |
| 9 | `Dino/packs/_archived/` | 176K | 38 | none | `e6b3db42 chore: organize repo artifacts ...` | actively curated game packs archive — deliberate | KEEP |
| 10 | `kwality/memory/backups/` | 2.4M | 7 | none | `a6072bb Initial commit` (genesis only) | runtime backup snapshots | NEEDS-AUDIT (verify with kwality maintainer) |
| 11 | `PhenoSpecs/archive/` | 384K | 38 | `package.json` (Flowra docs) | `180f059 archive: move Flowra docs to HexaKit proper` | docs preserved from deprecated repos | NEEDS-AUDIT (Flowra `package.json` exposes npm Dependabot if still scanned) |
| 12 | `phenotype-journeys-wtrees/shot-deprecate-align/` | 540K | 52 | 3× `Cargo.toml`, 3× `package.json` | `6c753bd512 audit(org): README hygiene ...` (touch only) | this is a worktree branch, NOT a real subdir | KEEP (worktree — out of scope) |
| 13 | `thegent/docs/archives/` | 264K | 11 | none | `ddb63528c Merge chore/thegent-provider-plane-pr3` | docs only | KEEP (active project, archived ADRs are reference) |
| 14 | `tooling/legacy-enforcement/` | 72K | 3 | none (no `Cargo.toml`) | (no git history at this path) | not in any workspace; orphaned dir | **NEEDS-AUDIT** (likely deletable) |
| 15 | `templates/webapp/.archive/` | 4K | 1 | none | `6c753bd512 audit ...` | empty placeholder | KEEP (template scaffold) |
| 16 | `FocalPoint/crates/focus-backup/` | 32K | 5 | `Cargo.toml` | `d07d34f fix(quality)...` | **ACTIVE** — imported by `focus-ffi/src/lib.rs` (8 refs) | KEEP (false positive — `backup` is feature name) |

## Score Summary

- **DELETE-CANDIDATE** (high confidence): **5** — items #1, #2, #4, #5, #6
- **NEEDS-AUDIT**: **5** — items #3, #7, #10, #11, #14
- **KEEP** (false positive / deliberate): **6** — items #8, #9, #12, #13, #15, #16

## Top 5 DELETE-CANDIDATE Actions

### 1. `helios-cli/codex-rs/execpolicy-legacy/` + `heliosCLI/codex-rs/execpolicy-legacy/`

- Workspace member listed in `codex-rs/Cargo.toml` line 27, **zero** consumer crates depend on it.
- Both repos are full-mirror forks of openai/codex; upstream still ships the legacy crate but Phenotype derivatives don't use it.
- Removal requires: delete dir + remove `"execpolicy-legacy"` line from `codex-rs/Cargo.toml` `members` array.
- Expected Dependabot alert reduction: **~3–6** (legacy crate has older deps; not isolated by Cargo.lock since the dir lacks one but is part of the workspace lock).
- Action (per repo, separate dispatch):

  ```bash
  cd /Users/kooshapari/CodeProjects/Phenotype/repos/heliosCLI
  git rm -r codex-rs/execpolicy-legacy
  # edit codex-rs/Cargo.toml: remove "execpolicy-legacy", line
  cargo check --workspace
  git commit -m "chore: remove dead execpolicy-legacy workspace member"
  ```

### 2. `PhenoProc/crates/bifrost-routing-backup/`

- Bare `src/` directory with no `Cargo.toml`, no workspace registration, zero references.
- Single restoration commit `dcb1b26 fix: restore and fix PhenoProc workspace crates` — restored by mistake.
- Expected alert reduction: **0** (no manifest), but removes phantom code in audits.

### 3. `Tracera-recovered/docs/archive/` (616K, 42 files)

- Pure docs from earlier Tracera recovery.
- No code references; no lockfiles.
- Expected alert reduction: **0**, but pairs with already-flagged `Tracera-recovered/ARCHIVE/CONFIG/` cleanup.

### 4. `Tracera-recovered/data/backup/` (28K, 7 files)

- Genesis-commit data dump, no live refs.
- Combine with #3 in single Tracera-recovered cleanup PR.

### 5. `phenotype-tooling/crates/legacy-scan/` (NEEDS-AUDIT, possible delete)

- Single scaffold commit; `main.rs` has 1 line of comment per scan; no integration; functional overlap with `tooling/legacy-enforcement` (separate repo) suggests duplication.
- Verify with maintainer before delete; if confirmed unused, removal saves a workspace member.

## Aggregate Expected Impact

If top 5 (counting #1+#2 as one categorical action across two mirrored repos) are deleted:

| Source | Est. Dependabot alerts closed |
|--------|-------------------------------|
| `helios-cli/codex-rs/execpolicy-legacy` | ~3 |
| `heliosCLI/codex-rs/execpolicy-legacy` | ~3 |
| `PhenoProc/crates/bifrost-routing-backup` | 0 (hygiene only) |
| `Tracera-recovered/docs/archive` + `data/backup` | 0 (hygiene only) |
| **Total** | **~6 alerts** + ~5 dead workspace artifacts removed |

Combined with already-pending Tracera/`ARCHIVE/CONFIG/` (~12 alerts) and today's KDesktopVirt win (9 alerts), this audit pipeline would land **~27 closed Dependabot alerts** over the week.

## Recommendations

1. Dispatch separate per-repo delete agents for the **DELETE-CANDIDATE** set (#1+#2 paired due to mirror, #4 standalone, #5+#6 as one Tracera-recovered cleanup PR).
2. For NEEDS-AUDIT items, dispatch a single read-only verification agent before any delete:
   - `phenotype-tooling/crates/legacy-scan` — confirm no roadmap reference.
   - `agslag-docs/archive` — sample contents (6.8M is large; might be valuable).
   - `kwality/memory/backups` — confirm not runtime-touched.
   - `PhenoSpecs/archive` — Flowra `package.json` should be `.gitignored` from Dependabot scan even if dir kept.
   - `tooling/legacy-enforcement` — check if it's referenced in any policy doc; orphaned dir likely deletable.
3. Each delete is its own commit + dispatch (per Dirty-Tree Commit Discipline).

## File Provenance

- Generated: 2026-04-26 by audit dispatch (read-only).
- Working dir: `/Users/kooshapari/CodeProjects/Phenotype/repos`.
- No deletions executed in this dispatch.
