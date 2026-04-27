# Phenotype Org Governance Repository Setup (2026-04-27)

## Problem: Canonical-Subdir-Inheritance Trap

The `/repos` canonical directory has accumulated **30+ unpushed governance/audit commits** all targeting `Tracera` origin (a project repo), not the org-level Forgejo instance. This violates separation of concerns: org-scoped governance should not accumulate in project repos.

**Root Cause:** `/repos/docs/` is a subdirectory without its own `.git/`, so commits inherit the parent canonical repo's remote configuration.

## Solution: Extract to phenotype-org-governance

Create a new private GitHub repository (`KooshaPari/phenotype-org-governance`) to hold org-scoped docs, separate from project-scoped governance in individual repos.

### Scope

**Move to phenotype-org-governance:**
- `docs/governance/` (128 files, 768 KB) — policies, ADRs, decision frameworks
- `docs/org-audit-2026-04/` (315 files, 69 MB) — cross-repo audits, metrics, dashboards
- `docs/changes/` (11 files, 68 KB) — per-change proposals and design docs

**Total:** 454 files, ~70 MB

**Remain in project repos:**
- Project-specific README, CLAUDE.md, docs/ with implementation guides
- Feature/change-specific docs stay in the originating project worktree

### Process (User Actions)

**Step 1: Initialize repo locally** (no push)
```bash
bash /Users/kooshapari/CodeProjects/Phenotype/repos/scripts/setup_phenotype_org_governance.sh
```

This creates `/Users/kooshapari/CodeProjects/Phenotype/phenotype-org-governance` with:
- Initial git repo with 454 files committed
- Organized subdirs: `governance/`, `org-audit/`, `changes/`
- Rollback-safe: no remote yet, safe to delete if needed

**Step 2: Create GitHub repo**
```bash
gh repo create KooshaPari/phenotype-org-governance \
  --private \
  --description "Phenotype-org governance, audits, dashboards, and policy" \
  --confirm
```

**Step 3: Connect and push**
```bash
cd /Users/kooshapari/CodeProjects/Phenotype/phenotype-org-governance
git remote add origin git@github.com:KooshaPari/phenotype-org-governance.git
git branch -M main
git push -u origin main
```

### Verification

After push completes:
```bash
gh api repos/KooshaPari/phenotype-org-governance --jq '.name, .private, .description'
# Should output:
# phenotype-org-governance
# true
# Phenotype-org governance, audits, dashboards, and policy
```

### Rollback

If anything goes wrong before user pushes:
```bash
rm -rf /Users/kooshapari/CodeProjects/Phenotype/phenotype-org-governance
```

After push, to delete the remote:
```bash
gh repo delete KooshaPari/phenotype-org-governance --confirm
```

Then re-run Step 1.

## Why This Matters

1. **Separation of Concerns** — Org governance lives in a dedicated repo, not mixed with project code
2. **Cleaner Canonical** — `/repos` canonical tracks only project-level commits (no phantom org doc pushes to Tracera)
3. **Scalable Governance** — As the org grows, governance can be managed independently
4. **Rollback-Safe** — The setup script is idempotent; Step 1 can be re-run if needed

## Timeline

- **2026-04-27T12:00Z** — setup script created, this doc written
- **User action** — Run Step 1, decide on Step 2 timing
- **Post-push** — Once `phenotype-org-governance` is live, new org-scoped docs go there; project docs stay in project repos

## Files

- Setup script: `/Users/kooshapari/CodeProjects/Phenotype/repos/scripts/setup_phenotype_org_governance.sh`
- This doc: `/Users/kooshapari/CodeProjects/Phenotype/repos/docs/governance/phenotype_org_governance_setup_2026_04_27.md`
