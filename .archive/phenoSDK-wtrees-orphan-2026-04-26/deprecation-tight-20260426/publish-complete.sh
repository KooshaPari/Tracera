#!/bin/bash
# Complete script to create repository and publish package

set -e

echo "🚀 Complete GitHub Packages Setup for pheno-sdk"
echo "=============================================="

# Check if GitHub token is provided
if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ Error: GITHUB_TOKEN environment variable is required"
    echo "Please set it with: export GITHUB_TOKEN=ghp_xxx"
    echo "You can create a token at: https://github.com/settings/tokens"
    echo "Required scopes: write:packages, repo"
    exit 1
fi

echo "GitHub Token: ${GITHUB_TOKEN:0:8}..."

# Step 1: Check if dist directory exists
if [ ! -d "dist" ]; then
    echo "📦 Building package..."
    python -m build
    echo "✅ Package built successfully"
else
    echo "✅ Package already built"
fi

# Step 2: Check if repository exists, create if not
echo "🔍 Checking if repository exists..."
if curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/repos/KooshaPari/pheno-sdk | grep -q '"name": "pheno-sdk"'; then
    echo "✅ Repository pheno-sdk already exists"
else
    echo "🏗️  Creating private repository pheno-sdk..."
    curl -X POST \
        -H "Authorization: token $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        https://api.github.com/user/repos \
        -d '{
            "name": "pheno-sdk",
            "description": "ATOMS-PHENO SDK for infrastructure migration and operations - Private Package Repository",
            "private": true,
            "auto_init": false
        }' > /dev/null
    echo "✅ Repository created successfully"

    # Wait a moment for repository to be fully created
    sleep 2
fi

# Step 3: Publish package
echo "📤 Publishing package to GitHub Packages..."
python -m twine upload \
    --repository-url https://pypi.pkg.github.com/KooshaPari/ \
    --username __token__ \
    --password "$GITHUB_TOKEN" \
    dist/*

echo ""
echo "🎉 SUCCESS! Package published to private GitHub Packages!"
echo ""
echo "📋 Next steps:"
echo "1. Test package availability:"
echo "   pip index versions pheno-sdk --index-url \"https://__token__:\${GITHUB_TOKEN}@pypi.pkg.github.com/KooshaPari/simple\" --extra-index-url https://pypi.org/simple"
echo ""
echo "2. Test Docker builds:"
echo "   cd ../router && ./build-with-github-packages.sh"
echo "   cd ../morph && ./build-with-github-packages.sh"
echo ""
echo "3. Test local installation:"
echo "   pip install pheno-sdk"
