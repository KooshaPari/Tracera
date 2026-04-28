#!/bin/bash
# Script to publish pheno-sdk to GitHub Packages

set -e

echo "Publishing pheno-sdk to GitHub Packages..."

# Check if GitHub token is provided
if [ -z "$GITHUB_TOKEN" ]; then
    echo "Error: GITHUB_TOKEN environment variable is required"
    echo "Please set it with: export GITHUB_TOKEN=ghp_xxx"
    echo "You can create a token at: https://github.com/settings/tokens"
    echo "Required scopes: write:packages"
    exit 1
fi

# Check if dist directory exists
if [ ! -d "dist" ]; then
    echo "Error: dist directory not found. Please build the package first:"
    echo "  python -m build"
    exit 1
fi

echo "Publishing packages from dist/ to GitHub Packages..."
echo "GitHub Token: ${GITHUB_TOKEN:0:8}..."

# Try different repository URLs
echo "Trying different repository configurations..."

# Option 1: Try with the package name as repository
echo "Attempting to publish to package-specific repository..."
python -m twine upload \
    --repository-url https://pypi.pkg.github.com/KooshaPari/pheno-sdk/ \
    --username __token__ \
    --password "$GITHUB_TOKEN" \
    dist/* || {
    echo "Failed with package-specific repository, trying generic repository..."
    
    # Option 2: Try with generic repository
    python -m twine upload \
        --repository-url https://pypi.pkg.github.com/KooshaPari/ \
        --username __token__ \
        --password "$GITHUB_TOKEN" \
        dist/* || {
        echo "Failed with generic repository. Let's try creating the repository first..."
        
        # Option 3: Try to create repository via API
        echo "Creating GitHub Packages repository..."
        curl -X POST \
            -H "Authorization: token $GITHUB_TOKEN" \
            -H "Accept: application/vnd.github.v3+json" \
            https://api.github.com/repos/KooshaPari/pheno-sdk \
            -d '{"name":"pheno-sdk","description":"ATOMS-PHENO SDK for infrastructure migration and operations","private":false}' || true
        
        # Wait a moment for repository creation
        sleep 2
        
        # Try again with package-specific repository
        echo "Retrying with package-specific repository..."
        python -m twine upload \
            --repository-url https://pypi.pkg.github.com/KooshaPari/pheno-sdk/ \
            --username __token__ \
            --password "$GITHUB_TOKEN" \
            dist/*
    }
}

echo "✅ Package published successfully to GitHub Packages!"
echo ""
echo "You can now test the installation:"
echo "  pip index versions pheno-sdk --index-url \"https://__token__:\${GITHUB_TOKEN}@pypi.pkg.github.com/KooshaPari/simple\" --extra-index-url https://pypi.org/simple"
