# Evalora 404 Diagnosis (2026-04-27)

## Summary

`https://github.com/KooshaPari/Evalora.git` returns HTTP 404. The repo has been **deleted** from the KooshaPari org (not archived, not renamed, not private — it does not exist).

## Verification

| Check | Result |
|-------|--------|
| `gh api repos/KooshaPari/Evalora` | `404 Not Found` |
| `gh api search/repositories?q=user:KooshaPari+Evalora` | empty |
| `gh repo list KooshaPari --json name` filtered `(?i)eval` | empty |
| Local `repos/Evalora/` | does not exist |
| Local `repos/PhenoProc/Evalora/` | exists (full Rust workspace, last commit `e67f2ac3`) |

Conclusion: **deleted**, not archived. No surviving fork or rename in the org. A populated working tree exists only inside `PhenoProc/Evalora/`.

## Dependency Chain (cargo-deny W-94 block)

```
pheno (workspace)
 └─ pheno/crates/phenotype-cache-adapter/Cargo.toml
     └─ phenotype-observability = { git = "https://github.com/KooshaPari/PhenoProc.git", branch = "main" }
         └─ PhenoProc/.gitmodules
             ├─ submodule "worktree-manager"  (OK)
             └─ submodule "Evalora"  → https://github.com/KooshaPari/Evalora.git  → 404
```

`phenotype-observability` itself has zero references to Evalora — the 404 fires during cargo's recursive submodule init when fetching the PhenoProc git dep. The Evalora submodule was added to PhenoProc in commit `d041dc4` (and re-recorded in `3a46de3`).

PhenoProc workspace `members = […]` does **not** include Evalora, so it is dead weight from the build's perspective — only `.gitmodules` makes cargo touch it.

## Impact

- **pheno**: cargo-deny / cargo audit cannot resolve the workspace (W-94).
- **PhenoProc consumers** (any repo with `git = "...PhenoProc.git"`): same blocker. Confirmed: `pheno/crates/phenotype-cache-adapter`. Likely additional consumers across `repos/` that pull PhenoProc as a git dep.
- **Local builds inside PhenoProc**: unaffected (submodule already populated; cargo workspace ignores it).
- **Worktrees**: 4 PhenoProc worktrees carry the same `.gitmodules` and reproduce the failure on fresh clone.

## Recommended Fix (user action)

Remove the dead Evalora submodule from PhenoProc — it is not a workspace member and the upstream repo no longer exists. Run inside the PhenoProc canonical or a worktree:

```bash
cd /Users/kooshapari/CodeProjects/Phenotype/repos/PhenoProc-wtrees/main-clean-20260426
git submodule deinit -f Evalora
git rm -f Evalora
git config -f .gitmodules --remove-section submodule.Evalora || true
git add .gitmodules
git commit -m "chore(submodules): drop Evalora (upstream 404, not a workspace member)"
# push to origin/main, then re-run pheno cargo-deny
```

Alternative if Evalora content is still wanted: push the local `PhenoProc/Evalora/` working tree to a new repo (e.g. `KooshaPari/Evalora-archive`) and update `.gitmodules` URL — but since it is not a workspace member, removal is the cheaper fix.

## Identity-collision note

Per memory `feedback_repo_identity_verification.md`: confirmed no rename / mirror / case-variant exists. This is a clean delete.

## Files referenced

- `/Users/kooshapari/CodeProjects/Phenotype/repos/PhenoProc/.gitmodules`
- `/Users/kooshapari/CodeProjects/Phenotype/repos/pheno/crates/phenotype-cache-adapter/Cargo.toml`
- `/Users/kooshapari/CodeProjects/Phenotype/repos/PhenoProc/libs/phenotype-observability/Cargo.toml`
- PhenoProc commits `d041dc4` (added), `3a46de3` (re-listed)
