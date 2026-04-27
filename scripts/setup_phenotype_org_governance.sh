#!/bin/bash
# Setup phenotype-org-governance repository
# Purpose: Extract governance, audit, and policy docs from /repos canonical
# Usage: bash scripts/setup_phenotype_org_governance.sh

set -euo pipefail

PHENOTYPE_ROOT="${1:-/Users/kooshapari/CodeProjects/Phenotype}"
ORG_GOV_DIR="${PHENOTYPE_ROOT}/phenotype-org-governance"
REPOS_DOCS="${PHENOTYPE_ROOT}/repos/docs"

echo "Preparing phenotype-org-governance repository..."
echo "  Source: ${REPOS_DOCS}"
echo "  Destination: ${ORG_GOV_DIR}"
echo ""

# Create destination directory
mkdir -p "${ORG_GOV_DIR}"
cd "${ORG_GOV_DIR}"

# Initialize git repo
if [ ! -d .git ]; then
  git init
  git config user.name "Forge"
  git config user.email "noreply@kooshapari.com"
fi

# Create directory structure
mkdir -p governance org-audit changes

# Copy governance corpus
echo "Copying governance docs (128 files)..."
cp -r "${REPOS_DOCS}/governance/"* governance/ 2>/dev/null || true

# Copy org-audit corpus
echo "Copying org-audit docs (315 files, ~69 MB)..."
cp -r "${REPOS_DOCS}/org-audit-2026-04/"* org-audit/ 2>/dev/null || true

# Copy changes corpus
echo "Copying changes docs (11 files)..."
cp -r "${REPOS_DOCS}/changes/"* changes/ 2>/dev/null || true

# Create README
cat > README.md << 'EOF'
# Phenotype Org Governance

Governance, audits, dashboards, and policy documentation for the Phenotype organization.

## Contents

- **governance/** — Architectural decisions, policies, decision frameworks
- **org-audit/** — Organization-wide audits, metrics, cross-project analysis
- **changes/** — Per-change design and proposal documentation

## Purpose

This repository prevents canonical `/repos` subdirectory accumulation of org-level governance commits (canonical-subdir-inheritance trap). All org-scoped docs belong here; project-specific docs remain in project repos.

## Setup & First Push (User Action)

```bash
# 1. Create the GitHub repository (requires github-cli with auth)
gh repo create KooshaPari/phenotype-org-governance \
  --private \
  --description "Phenotype-org governance, audits, dashboards, and policy" \
  --confirm

# 2. Connect and push
cd /Users/kooshapari/CodeProjects/Phenotype/phenotype-org-governance
git remote add origin git@github.com:KooshaPari/phenotype-org-governance.git
git branch -M main
git push -u origin main
```

## Rollback

If needed, remove the repo and re-copy from `/repos/docs`:

```bash
rm -rf /Users/kooshapari/CodeProjects/Phenotype/phenotype-org-governance
gh repo delete KooshaPari/phenotype-org-governance --confirm
# Re-run: bash /repos/scripts/setup_phenotype_org_governance.sh
```
EOF

# Create initial commit
echo ""
echo "Creating initial commit..."
git add .
git commit -m "init: import 2026-04 governance corpus from /repos canonical

- governance/ (128 files, 768 KB): policies, decision frameworks, architecture
- org-audit/ (315 files, 69 MB): cross-project audits, metrics, dashboards
- changes/ (11 files, 68 KB): per-change design and proposal docs

This prevents /repos canonical subdirectory accumulation via canonical-subdir-inheritance.
Next step: user runs 'gh repo create' and 'git push -u origin main'
"

echo ""
echo "Setup complete!"
echo ""
echo "Total files: 454"
echo "Total size: ~70 MB"
echo ""
echo "Next steps (USER ACTION):"
echo "  1. cd ${ORG_GOV_DIR}"
echo "  2. gh repo create KooshaPari/phenotype-org-governance --private --description \"Phenotype-org governance, audits, dashboards, and policy\" --confirm"
echo "  3. git remote add origin git@github.com:KooshaPari/phenotype-org-governance.git"
echo "  4. git push -u origin main"
echo ""
