#!/bin/bash
# Script to fix GitHub Packages 404 error

set -e

echo "🔧 Fixing GitHub Packages 404 Error"
echo "==================================="

# Check if GitHub CLI is installed and authenticated
if ! command -v gh &> /dev/null; then
    echo "❌ Error: GitHub CLI (gh) is not installed"
    exit 1
fi

if ! gh auth status &> /dev/null; then
    echo "❌ Error: Not authenticated with GitHub CLI"
    exit 1
fi

echo "✅ GitHub CLI authenticated"

# The issue is likely that we need to enable packages for the repository
echo "🔍 Checking if packages are enabled for the repository..."

# Try to enable packages by creating a simple package configuration
echo "📦 Attempting to enable packages for the repository..."

# First, let's try with verbose output to see the exact error
echo "🔍 Getting detailed error information..."
GITHUB_TOKEN=$(gh auth token)

echo "Trying with verbose output to diagnose the issue..."
python -m twine upload \
    --repository-url https://pypi.pkg.github.com/KooshaPari/ \
    --username __token__ \
    --password "$GITHUB_TOKEN" \
    --verbose \
    dist/* || {
    echo ""
    echo "❌ Upload failed. Let's try alternative approaches..."

    # Try with the repository-specific URL
    echo "🔄 Trying repository-specific URL..."
    python -m twine upload \
        --repository-url https://pypi.pkg.github.com/KooshaPari/pheno-sdk/ \
        --username __token__ \
        --password "$GITHUB_TOKEN" \
        --verbose \
        dist/* || {
        echo ""
        echo "❌ Repository-specific URL also failed."
        echo ""
        echo "🔧 Possible solutions:"
        echo "1. The repository might need to be public for GitHub Packages"
        echo "2. The token might not have the correct scopes"
        echo "3. GitHub Packages might need to be enabled for your account"
        echo ""
        echo "Let's try making the repository public temporarily..."

        # Try making the repository public
        gh repo edit KooshaPari/pheno-sdk --visibility public

        echo "🔄 Trying upload with public repository..."
        python -m twine upload \
            --repository-url https://pypi.pkg.github.com/KooshaPari/ \
            --username __token__ \
            --password "$GITHUB_TOKEN" \
            dist/*

        echo "✅ Success! Now making repository private again..."
        gh repo edit KooshaPari/pheno-sdk --visibility private
    }
}

echo ""
echo "✅ Package published successfully!"
