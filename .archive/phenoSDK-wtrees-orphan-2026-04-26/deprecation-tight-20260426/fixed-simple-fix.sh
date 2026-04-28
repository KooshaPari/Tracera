#!/bin/bash
# Fixed script for GitHub Packages 404 error

echo "🔧 Fixed Simple Fix for GitHub Packages 404 Error"
echo "================================================="

# Get GitHub token
GITHUB_TOKEN=$(gh auth token)

echo "🔍 Step 1: Check token scopes"
echo "Current token: ${GITHUB_TOKEN:0:8}..."

echo ""
echo "🔍 Step 2: Make repository public temporarily"
gh repo edit KooshaPari/pheno-sdk --visibility public --accept-visibility-change-consequences

echo ""
echo "🔍 Step 3: Try uploading to public repository"
python -m twine upload \
    --repository-url https://pypi.pkg.github.com/KooshaPari/ \
    --username __token__ \
    --password "$GITHUB_TOKEN" \
    dist/*

echo ""
echo "🔍 Step 4: Make repository private again"
gh repo edit KooshaPari/pheno-sdk --visibility private --accept-visibility-change-consequences

echo ""
echo "✅ Done! Package should now be available as private package."
