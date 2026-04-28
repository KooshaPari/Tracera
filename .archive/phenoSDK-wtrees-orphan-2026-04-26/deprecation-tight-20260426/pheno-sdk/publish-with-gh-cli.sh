#!/bin/bash
# Complete script to create repository and publish package using GitHub CLI

set -e

echo "🚀 Complete GitHub Packages Setup for pheno-sdk using GitHub CLI"
echo "================================================================="

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ Error: GitHub CLI (gh) is not installed"
    echo "Please install it from: https://cli.github.com/"
    exit 1
fi

# Check if user is authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Error: Not authenticated with GitHub CLI"
    echo "Please run: gh auth login"
    exit 1
fi

echo "✅ GitHub CLI authenticated"

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
if gh repo view KooshaPari/pheno-sdk &> /dev/null; then
    echo "✅ Repository pheno-sdk already exists"
else
    echo "🏗️  Creating private repository pheno-sdk..."
    gh repo create KooshaPari/pheno-sdk \
        --private \
        --description "ATOMS-PHENO SDK for infrastructure migration and operations - Private Package Repository" \
        --clone=false
    echo "✅ Repository created successfully"

    # Wait a moment for repository to be fully created
    sleep 2
fi

# Step 3: Get GitHub token for twine
echo "🔑 Getting GitHub token for package publishing..."
GITHUB_TOKEN=$(gh auth token)

# Step 4: Publish package
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
echo ""
echo "🔗 Repository: https://github.com/KooshaPari/pheno-sdk"
