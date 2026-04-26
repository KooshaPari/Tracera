# Nested Workspace Embedding Audit — Tracera Pheno* dirs

**Date:** 2026-04-26
**Trigger:** Round-34 LEGACY badge agent flagged 4 top-level dirs whose `git remote -v` resolves to `KooshaPari/Tracera`.
**Working dir audited:** `/Users/kooshapari/CodeProjects/Phenotype/repos`

## TL;DR

The 4 dirs (`PhenoContracts`, `PhenoEvents`, `PhenoKit`, `PhenoSchema`) are NOT independent clones and NOT submodules. They are plain tracked directories inside the `/repos` parent git tree itself. The `git remote -v = Tracera` reading is **misleading inheritance** — it reflects the parent `/repos` tree's `origin`, not a per-dir remote. None of these dirs has its own `.git/`. Their `git rev-parse --show-toplevel` returns `/repos`, confirming they are first-class members of the parent tree.

They are **scaffold/idea dirs** (README-only or thin) — not active workspace members of any canonical Tracera checkout. The real `Tracera/` directory in `/repos` does not contain `PhenoContracts/`, `PhenoEvents/`, `PhenoKit/`, or `PhenoSchema/` subdirs. The dirs are not symlink-able because there is no canonical target to link to.

## Per-Dir Findings

| Dir | `.git/` own? | Tracked count | Has Cargo/pkg? | Real workspace member? | Status |
|-----|--------------|---------------|----------------|------------------------|--------|
| `PhenoContracts` | no | 1 (README only) | no | no | scaffold/idea README |
| `PhenoEvents` | no | 1 (README only) | no | no (`pheno-events/` empty) | scaffold/idea README |
| `PhenoKit` | no | 3 (README + python/colab + rust/patch) | no | no | scaffold/idea README |
| `PhenoSchema` | no | 3 (README + pheno-xdd + pheno-xdd-lib) | no | no | scaffold/idea README |

All four:
- live in the parent `/repos` git tree (toplevel = `/repos`)
- have NO `.git/` of their own
- inherit `origin = git@github.com:KooshaPari/Tracera.git` from `/repos`'s `.git/config`
- contain primarily a README documenting an aspirational/conceptual library

## Recommendations

| Dir | Recommendation | Rationale |
|-----|----------------|-----------|
| `PhenoContracts` | **Document in this audit; leave in place OR move to `docs/concepts/`** | README-only scaffold; not a code dir |
| `PhenoEvents` | **Same — document; consider moving to `docs/concepts/`** | README + empty `pheno-events/` placeholder |
| `PhenoKit` | **Same — document; consider relocating** | README + thin `python/`, `rust/` placeholders |
| `PhenoSchema` | **Same — document; consider relocating** | README + `pheno-xdd*` placeholders |

**Symlink conversion is not applicable** — there is no canonical Tracera workspace member to link to. The flag's premise (these are nested workspace members of Tracera) is **incorrect**. They are top-level scaffold dirs in `/repos` that happen to inherit Tracera's `origin` because `/repos`'s parent git config points to Tracera.

**No structural change executed.** This audit doc is the deliverable.

## Why the Flag Misread

`git remote -v` from inside any subdir of `/repos` returns `Tracera` because:
- `/repos/.git/config` has `[remote "origin"] url = git@github.com:KooshaPari/Tracera.git`
- Subdirs without their own `.git/` resolve to the parent tree
- This is the well-documented "canonical subdir inheritance" gotcha (per memory `feedback_canonical_subdir_inheritance.md`)

The Round-34 LEGACY badge agent likely ran `git -C <dir> remote -v` and assumed each result implied a cloned repo. The actual state is much less dramatic: these are just plain directories tracked in `/repos`.

## Follow-up Items

1. **phenoSDK GitHub state** — RESOLVED 2026-04-26. Reconcile (commit `7c673c6dea`, `docs/org-audit-2026-04/phenoSDK_reconcile_2026_04_26.md`) confirmed phenoSDK was consolidated into `AuthKit` and the GitHub repo was hard-deleted. The local working copy was an orphan with no remote to push to. Action taken: moved `repos/phenoSDK/` → `repos/.archive/phenoSDK-orphan-2026-04-26/` and `repos/phenoSDK-wtrees/` → `repos/.archive/phenoSDK-wtrees-orphan-2026-04-26/` (preserves branches + reflog for audit). Do NOT recreate the GitHub repo.

2. **Scaffold README dirs hygiene** — consider relocating `PhenoContracts/`, `PhenoEvents/`, `PhenoKit/`, `PhenoSchema/` from `/repos` top-level to `/repos/docs/concepts/` to reduce noise in repo listings. They are not code; they are conceptual scaffolds.

3. **LEGACY badge agent fix** — teach Round-N hygiene agents that `git remote -v` inside a subdir of a tracked tree inherits from the parent, and to verify with `git -C <dir> rev-parse --git-dir` (must NOT equal parent's `.git/`) before claiming a dir is a "nested workspace embedding".

## References

- Memory: `feedback_canonical_subdir_inheritance.md` — same root-cause inheritance pattern
- Memory: `feedback_repo_identity_verification.md` — verify repo identity before trusting README/CLAUDE labels
- Parent `/repos/.git/config` origin: `git@github.com:KooshaPari/Tracera.git`
