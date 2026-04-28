#!/bin/bash
# Simple script to create the private repository using GitHub CLI

set -e

echo "🏗️  Creating private repository for GitHub Packages..."

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

# Check if repository already exists
if gh repo view KooshaPari/pheno-sdk &> /dev/null; then
    echo "✅ Repository pheno-sdk already exists"
    echo "🔗 Repository: https://github.com/KooshaPari/pheno-sdk"
else
    echo "Creating private repository pheno-sdk..."
    gh repo create KooshaPari/pheno-sdk \
        --private \
        --description "ATOMS-PHENO SDK for infrastructure migration and operations - Private Package Repository" \
        --clone=false

    echo "✅ Repository created successfully!"
    echo "🔗 Repository: https://github.com/KooshaPari/pheno-sdk"
fi

echo ""
echo "Now you can publish the package:"
echo "  ./publish-to-private-github-packages.sh"
