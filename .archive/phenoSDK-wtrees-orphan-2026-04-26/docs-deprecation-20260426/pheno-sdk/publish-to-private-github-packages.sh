#!/bin/bash
# Script to publish pheno-sdk to PRIVATE GitHub Packages

set -e

echo "Publishing pheno-sdk to PRIVATE GitHub Packages..."

# Check if GitHub token is provided
if [ -z "$GITHUB_TOKEN" ]; then
    echo "Error: GITHUB_TOKEN environment variable is required"
    echo "Please set it with: export GITHUB_TOKEN=ghp_xxx"
    echo "You can create a token at: https://github.com/settings/tokens"
    echo "Required scopes: write:packages, repo (for private packages)"
    exit 1
fi

# Check if dist directory exists
if [ ! -d "dist" ]; then
    echo "Error: dist directory not found. Please build the package first:"
    echo "  python -m build"
    exit 1
fi

echo "Publishing packages from dist/ to PRIVATE GitHub Packages..."
echo "GitHub Token: ${GITHUB_TOKEN:0:8}..."

# For private GitHub Packages, we use the organization-level endpoint
echo "Publishing to private GitHub Packages..."
python -m twine upload \
    --repository-url https://pypi.pkg.github.com/KooshaPari/ \
    --username __token__ \
    --password "$GITHUB_TOKEN" \
    dist/*

echo "✅ Package published successfully to PRIVATE GitHub Packages!"
echo ""
echo "To install this private package, users need:"
echo "1. A GitHub token with 'read:packages' scope"
echo "2. Configure pip with:"
echo "   pip config set global.index-url https://pypi.pkg.github.com/KooshaPari/simple"
echo "   pip config set global.extra-index-url https://pypi.org/simple"
echo ""
echo "Or use environment variables:"
echo "  export GITHUB_TOKEN=your_token"
echo "  pip install --index-url \"https://__token__:\${GITHUB_TOKEN}@pypi.pkg.github.com/KooshaPari/simple\" --extra-index-url https://pypi.org/simple pheno-sdk"
