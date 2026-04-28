#!/bin/bash
# Script to create and set up GitHub Packages repository

set -e

echo "Setting up GitHub Packages repository for pheno-sdk..."

# Check if GitHub token is provided
if [ -z "$GITHUB_TOKEN" ]; then
    echo "Error: GITHUB_TOKEN environment variable is required"
    echo "Please set it with: export GITHUB_TOKEN=ghp_xxx"
    echo "You can create a token at: https://github.com/settings/tokens"
    echo "Required scopes: write:packages, repo"
    exit 1
fi

echo "GitHub Token: ${GITHUB_TOKEN:0:8}..."

# Check if the repository already exists
echo "Checking if repository exists..."
if curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/repos/KooshaPari/pheno-sdk | grep -q '"name": "pheno-sdk"'; then
    echo "✅ Repository pheno-sdk already exists"
else
    echo "Creating private repository pheno-sdk..."
    curl -X POST \
        -H "Authorization: token $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        https://api.github.com/user/repos \
        -d '{
            "name": "pheno-sdk",
            "description": "ATOMS-PHENO SDK for infrastructure migration and operations - Private Package Repository",
            "private": true,
            "auto_init": false
        }'
    echo "✅ Repository created successfully"
fi

echo ""
echo "Now you can publish the package:"
echo "  ./publish-to-private-github-packages.sh"
