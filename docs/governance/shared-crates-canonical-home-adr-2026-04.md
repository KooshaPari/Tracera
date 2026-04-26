---
title: ADR — Canonical home for shared Rust infrastructure crates
status: Accepted
date: 2026-04-25
supersedes: cross-project-reuse-audit-2026-04-25.md (triplicate-home finding)
adr-id: SHARED-CRATES-CANONICAL-2026-04
owners: phenotype-org / shared-platform
---

## Background

The 2026-04-25 cross-project reuse audit
(`docs/governance/cross-project-reuse-audit-2026-04-25.md`) flagged a
"three-canonical-home" problem: `phenotype-event-sourcing`,
`phenotype-cache-adapter`, `phenotype-state-machine`, and
`phenotype-policy-engine` are each defined in **multiple parallel Cargo
workspaces** with no single source of truth. Filesystem reconnaissance on
2026-04-25 confirms the crates physically exist in:

| Home | Repo (origin) | Has crates? | Last-touched |
|------|---------------|-------------|--------------|
| `phenoShared` | `KooshaPari/phenoShared` | ES, CA, SM, PE | 2026-04-25 (today) |
| `pheno` | `KooshaPari/pheno` | ES, CA, SM, PE | 2026-03-31 |
| `PhenoProc` | `KooshaPari/PhenoProc` | ES, CA, SM, PE (+ nested `crates/phenotype-shared/crates/*`) | 2026-04-03 |
| `DataKit/rust` | `KooshaPari/DataKit` | ES, CA | 2026-04-05 (snapshot) |
| `HexaKit/crates` + `PhenoKits/HexaKit/crates` | `KooshaPari/HexaKit`, `PhenoKits` | SM, PE (+ ES, CA in PhenoKits) | 2026-03-31 |
| `AuthKit/rust` | `KooshaPari/AuthKit` | PE | snapshot |
| `ResilienceKit/rust` | `KooshaPari/ResilienceKit` | SM | snapshot |
| `hwLedger/vendor` | `KooshaPari/hwLedger` | ES (vendored copy) | snapshot |
| `phenotype-shared` (intended canonical per audit) | `KooshaPari/phenotype-shared` | **none locally; remote `main` has empty `members = []`** | dormant |

ES = event-sourcing, CA = cache-adapter, SM = state-machine, PE = policy-engine.

API drift is already observed (e.g. `phenotype-event-sourcing/src/lib.rs`
is 26 LOC in `pheno` and `PhenoKits/HexaKit`, but 42 LOC in `phenoShared`
and 57 LOC in `PhenoProc`/`DataKit`). All declare `version = "0.2.0"` or
inherit from workspace, so semver alone cannot distinguish them.

External consumers outside these workspaces: **0** (all existing dep
declarations are internal `path = "crates/..."` references). This means
consolidation has near-zero blast radius.

## Decision

**Canonical home: `phenoShared` (`github.com/KooshaPari/phenoShared`).**

Rationale, in order of weight:

1. **Activity:** the only home with same-day commits explicitly evolving
   the crates (`refactor(state): adopt versioning pattern —
   phenotype-event-sourcing`, 2026-04-25).
2. **Completeness:** ships all four target crates plus adjacent shared
   infrastructure (`phenotype-port-interfaces`, `phenotype-domain`,
   `phenotype-application`, `phenotype-health`, `phenotype-retry`,
   `phenotype-policy-engine-py`).
3. **Charter fit:** dedicated org-shared workspace; not coupled to a
   product (unlike `PhenoProc`, `pheno`, `DataKit`, `AuthKit`,
   `ResilienceKit`, `HexaKit`, `hwLedger`).
4. **`phenotype-shared` is paper-only:** remote `main` has
   `members = []`; the local checkout's origin actually points at
   `PhenoKits`. It cannot serve as canonical without first being
   re-bootstrapped, which is strictly more work than adopting the
   already-populated `phenoShared`.

The audit doc's earlier preference for "phenotype-shared" is superseded
by this ADR on the basis of filesystem reality.

## Migration matrix

| Crate | Source homes (to deprecate) | Target version source | Consumers to update | Notes |
|-------|------------------------------|------------------------|----------------------|-------|
| `phenotype-event-sourcing` | `pheno`, `PhenoProc` (×2 nested), `DataKit/rust`, `PhenoKits/HexaKit`, `hwLedger/vendor` | `phenoShared/crates/phenotype-event-sourcing` (42 LOC, 2026-04-25) | 6 internal workspace refs; 0 external | Reconcile 26→42→57 LOC variants; `phenoShared` is mid-evolution — finalize API before extraction |
| `phenotype-cache-adapter` | `pheno`, `PhenoProc` (×2), `DataKit/rust`, `PhenoKits/HexaKit` | `phenoShared/crates/phenotype-cache-adapter` | 5 internal | API parity check required |
| `phenotype-state-machine` | `pheno`, `PhenoProc` (×2), `ResilienceKit/rust`, `HexaKit/crates`, `PhenoKits/HexaKit` | `phenoShared/crates/phenotype-state-machine` | 6 internal | `ResilienceKit` is a snapshot; verify no domain-specific divergence |
| `phenotype-policy-engine` | `pheno`, `PhenoProc` (×2), `HexaKit/crates`, `PhenoKits/HexaKit`, `AuthKit/rust` | `phenoShared/crates/phenotype-policy-engine` | 6 internal | `AuthKit` may have auth-specific extensions — capture as feature flag in canonical, do not fork |

Total deduplications: **23 redundant crate copies** across 8 host
workspaces. **Zero external (cross-workspace) consumer Cargo.toml
edits required** — all dependencies are local `path =` refs that will
be replaced by `git = "...phenoShared..."` or path refs to a shared
worktree, depending on workspace strategy chosen at implementation time.

## Deprecation plan

For each non-canonical home listed above, the implementation task MUST:

1. Add `DEPRECATED.md` at the root of each duplicated crate directory:
   ```
   ---
   status: deprecated
   canonical: github.com/KooshaPari/phenoShared/crates/<crate>
   adr: docs/governance/shared-crates-canonical-home-adr-2026-04.md
   replaced-on: <YYYY-MM-DD>
   ---
   This crate has moved to phenoShared. Do not edit here.
   New consumers MUST depend on the canonical version.
   ```
2. Add a top-of-file `// DEPRECATED — see DEPRECATED.md` banner to the
   crate's `src/lib.rs`.
3. Switch the host workspace's `Cargo.toml` `members = [...]` to remove
   the duplicate path; replace any internal `path = "crates/..."`
   dependency with a workspace dep targeting `phenoShared`.
4. Remove the duplicated source tree only **after** all reverse-deps
   inside that host workspace compile against the canonical crate.

The audit doc (`cross-project-reuse-audit-2026-04-25.md`) gets a
trailing one-line "Superseded for canonical-home decision: see
shared-crates-canonical-home-adr-2026-04.md" note as part of the
implementation PR.

## Acceptance criteria

- `find repos -path '*/crates/phenotype-{event-sourcing,cache-adapter,state-machine,policy-engine}' -not -path '*phenoShared*' -not -path '*target*' -not -path '*.archive*' -not -path '*-wtrees*'` returns `0` results.
- All host workspaces (`pheno`, `PhenoProc`, `DataKit`, `HexaKit`, `PhenoKits/HexaKit`, `AuthKit`, `ResilienceKit`, `hwLedger`) build green against the canonical `phenoShared` crates.
- The 4 deprecated crate directories per home each carry a `DEPRECATED.md` with the canonical pointer, until physical removal lands.
- `cargo metadata --workspace` from any host shows exactly one entry per crate name across the resolved graph.
- The cross-project audit doc gets a "superseded" pointer back to this ADR.

## Out of scope (next tasks)

- **No code dedup in this PR.** This is planning only, per the
  Planner-Agents-No-Code rule. A follow-up implementation task per crate
  (4 tasks) will execute the migration matrix.
- API reconciliation between the 26 / 42 / 57 LOC variants of
  `phenotype-event-sourcing` is delegated to the implementation task —
  the canonical baseline is whatever `phenoShared` ships at task-start.
- Re-purposing the dormant `KooshaPari/phenotype-shared` repo (rename,
  archive, or repoint) is a separate org-hygiene task.

## Predecessors / DAG

- depends-on: `cross-project-reuse-audit-2026-04-25.md` (this ADR resolves its §"Three-canonical-home problem")
- enables: 4 implementation work packages (one per crate) — sequential within a host workspace, parallel across workspaces.

## Verification 2026-04-25 (post-discrepancy)

**Original verdict (`phenoShared` is canonical) — CONFIRMED.** The supposed contradiction with later "reality-check" claims at commit `e4101c0e8` (asserting `phenotype-shared` had 12 workspace members on `origin/main` and was therefore active, contradicting the "dormant" framing) is **a phantom dispute**: `KooshaPari/phenotype-shared` and `KooshaPari/phenoShared` are **the same GitHub repository**. The repo was renamed `phenotype-shared` → `phenoShared` and GitHub silently redirects API calls under the old name to the new one.

### Direct API evidence (2026-04-25)

```
gh api repos/KooshaPari/phenotype-shared --jq '{full_name, html_url, id}'
→ {full_name: "KooshaPari/phenoShared", html_url: "https://github.com/KooshaPari/phenoShared", id: 1190541801}

gh api repos/KooshaPari/phenoShared --jq '{full_name, html_url, id}'
→ {full_name: "KooshaPari/phenoShared", html_url: "https://github.com/KooshaPari/phenoShared", id: 1190541801}
```

Identical `id`, identical `full_name`. Both names resolve to the same repo (id `1190541801`, created 2026-03-24).

### Side-by-side (both names → one repo)

| Dimension | `phenotype-shared` (alias) | `phenoShared` (canonical name) |
|---|---|---|
| GitHub repo id | 1190541801 | 1190541801 |
| Default branch | `main` | `main` |
| Last commit on `main` | `0756e815d` (2026-04-25T19:17:44Z, "chore(cargo): commit Cargo.lock for Dependabot + audit coverage (#101)") | same |
| Workspace members | 12 (`ffi_utils`, `phenotype-application`, `phenotype-cache-adapter`, `phenotype-domain`, `phenotype-event-sourcing`, `phenotype-http-adapter`, `phenotype-nanovms-client`, `phenotype-policy-engine`, `phenotype-port-interfaces`, `phenotype-postgres-adapter`, `phenotype-redis-adapter`, `phenotype-state-machine`) | same |
| Target crate `lib.rs` sizes | event-sourcing 1236 B, cache-adapter 28 B, policy-engine 1362 B, state-machine 28 B | identical (same blobs) |
| PRs #92–#101 | identical list, all merged | identical list |

**API-drift comparison:** moot — same repo, same blobs.

### Conclusion

- **TRUE canonical:** `KooshaPari/phenoShared` (`https://github.com/KooshaPari/phenoShared`).
- **`phenotype-shared` is an alias** (the previous repository name); it is NOT a separate dormant repo. The remote `pheno` configured locally as `git@github.com:KooshaPari/phenoShared.git` is correct.
- The original ADR verdict stands. The note "remote `main` has empty `members = []`" in the original Background table was based on a stale snapshot taken before `phenoShared` had been populated; that historical observation is no longer true on `main` and should not be cited as evidence of dormancy.

### Spec PRs to revisit

- **PR #406 (heliosApp consolidation):** assumed-correct on canonical home. No directional change required, but any wording that names the repo `phenotype-shared` should be updated to `phenoShared` for clarity.
- **PR #32 (phenotype-shared workspace expansion):** PR is filed against the renamed repo (now `phenoShared`); no canonical-home change needed. Title may be updated to reflect the rename, but is non-blocking.

### Action items

1. Org-hygiene task (out of scope for this ADR): consider redirecting or removing the `phenotype-shared` redirect alias to eliminate future name-collision confusion in audits. Tracked separately.
2. Update any other governance doc that treats `phenotype-shared` and `phenoShared` as distinct repositories — e.g. `dormant-repos-audit-2026-04-25.md`, `org-cargo-audit-2026-04-25.md`, `cross-project-reuse-audit-2026-04-25.md`, `dependabot-rust-coverage.md`, `alert-sync-policy.md` — to refer to the single canonical repo by its current name (`phenoShared`).
3. The "Background" table row marking `phenotype-shared` as "dormant" with `members = []` is retained for historical context but should be read as "the repo's earlier state before being populated under its previous name."

### Reproducible verification

```bash
gh api repos/KooshaPari/phenotype-shared --jq '{full_name, id, default_branch, pushed_at}'
gh api repos/KooshaPari/phenoShared      --jq '{full_name, id, default_branch, pushed_at}'
# both → same id 1190541801, same full_name "KooshaPari/phenoShared"

gh api repos/KooshaPari/phenoShared/contents/Cargo.toml --jq '.content' | base64 -d   # 12 members
gh api repos/KooshaPari/phenoShared/contents/crates --jq '.[].name'                    # 12 crate dirs
gh api repos/KooshaPari/phenoShared/commits/main --jq '{sha,date:.commit.committer.date,msg:.commit.message[:80]}'
```
