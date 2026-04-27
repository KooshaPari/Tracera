# /repos Canonical Post-Migration Cleanup (2026-04-27)

## Migration Verification

**Status: COMPLETE**

- phenotype-org-governance repo created: `KooshaPari/phenotype-org-governance`
- Last push: 2026-04-27 03:33:08Z
- Current /repos/docs/ structure:
  - `governance/` — 135 files (800K)
  - `org-audit-2026-04/` — 318 files (69M)
  - `changes/` — 11 files (68K)

Total footprint: ~70MB in /repos canonical that now lives in separate repo.

## Problem

The /repos canonical directory inherits `git remote` from its parent. Files in `/repos/docs/governance`, `/repos/docs/org-audit-2026-04`, and `/repos/docs/changes` are tracked in this worktree's git history, creating the "canonical-subdir-inheritance trap" documented in MEMORY.md.

When agents reference `/repos/docs/governance/X.md`, they see files that are:
- Tracked in the monorepo git history (unnecessary duplication)
- Out of sync with the authoritative copy in phenotype-org-governance
- Cannot be independently versioned or deployed

## Recommended Strategy: Option A (Symlink)

**Breaks the trap while preserving in-tree access.**

### User Commands

```bash
cd /Users/kooshapari/CodeProjects/Phenotype/repos

# 1. Clone phenotype-org-governance as a sibling (one-time)
cd ..
git clone https://github.com/KooshaPari/phenotype-org-governance.git
cd repos

# 2. Remove tracked files from /repos git
git rm --cached -r docs/governance docs/org-audit-2026-04 docs/changes

# 3. Create symlinks
rm -rf docs/governance docs/org-audit-2026-04 docs/changes
ln -s ../phenotype-org-governance/governance docs/governance
ln -s ../phenotype-org-governance/org-audit-2026-04 docs/org-audit-2026-04
ln -s ../phenotype-org-governance/changes docs/changes

# 4. Commit the cleanup
git add .gitignore docs/.gitkeep (or remove empty dirs)
git commit -m "refactor(docs): symlink governance corpus to phenotype-org-governance

- Remove 135 governance files, 318 audit files, 11 change files from canonical
- Create symlinks to authoritative repo at ../phenotype-org-governance
- Breaks canonical-subdir-inheritance trap
- Agents can still access /repos/docs/governance/* via symlink resolution
- All future governance updates flow from single source of truth

Refs: phenotype-org-governance (primary), MEMORY.md#canonical_subdir_inheritance"

# 5. Verify symlinks work
ls -la docs/governance/repos_canonical_post_migration_2026_04_27.md
ls docs/org-audit-2026-04/ | head -5
```

### Alternative: Option B (Delete, No Symlink)

If separation is preferred:

```bash
git rm -r docs/governance docs/org-audit-2026-04 docs/changes
git commit -m "docs(governance): remove corpus—now in phenotype-org-governance repo"
# Agents access via: cd ../phenotype-org-governance/governance/...
```

### Rollback (if needed)

```bash
git reset --soft HEAD~1
git restore --staged .
rm -rf docs/governance docs/org-audit-2026-04 docs/changes
git restore docs/governance docs/org-audit-2026-04 docs/changes
git status  # should show tracked files again
```

## Next Steps

1. Choose Option A or B above
2. Run user commands (do NOT execute via agent)
3. Verify symlinks (Option A) or absence (Option B)
4. All governance updates now centralize in phenotype-org-governance
5. Update MEMORY.md reference to note completion

## Impact

- **Agents**: symlinks (Option A) maintain transparent in-tree access
- **Disk**: no immediate saving (already on disk; removes duplication in .git history)
- **Governance**: single source of truth; reduces sync burden
- **CI/CD**: ensure phenotype-org-governance is cloned as dependency (not yet configured)

---

**Document created**: 2026-04-27  
**Canonical location**: /repos/docs/governance/repos_canonical_post_migration_2026_04_27.md (last write to /repos/docs/governance)  
**Next maintenance**: After user executes cleanup, update MEMORY.md to close the trap reference.
