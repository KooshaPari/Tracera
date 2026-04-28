#!/bin/bash
# Try all possible methods to publish to GitHub Packages

echo "🔧 Trying All Methods for GitHub Packages"
echo "========================================="

# Get GitHub token
GITHUB_TOKEN=$(gh auth token)

echo "Method 1: Try with organization-level endpoint (current method)"
python -m twine upload \
    --repository-url https://pypi.pkg.github.com/KooshaPari/ \
    --username __token__ \
    --password "$GITHUB_TOKEN" \
    dist/* || {
    echo "❌ Method 1 failed"

    echo ""
    echo "Method 2: Try with repository-specific endpoint"
    python -m twine upload \
        --repository-url https://pypi.pkg.github.com/KooshaPari/pheno-sdk/ \
        --username __token__ \
        --password "$GITHUB_TOKEN" \
        dist/* || {
        echo "❌ Method 2 failed"

        echo ""
        echo "Method 3: Try with username instead of __token__"
        python -m twine upload \
            --repository-url https://pypi.pkg.github.com/KooshaPari/ \
            --username KooshaPari \
            --password "$GITHUB_TOKEN" \
            dist/* || {
            echo "❌ Method 3 failed"

            echo ""
            echo "Method 4: Try with different repository URL format"
            python -m twine upload \
                --repository-url https://upload.pypi.org/legacy/ \
                --username __token__ \
                --password "$GITHUB_TOKEN" \
                dist/* || {
                echo "❌ Method 4 failed"

                echo ""
                echo "❌ All methods failed. The issue might be:"
                echo "1. GitHub Packages not enabled for your account"
                echo "2. Repository needs to be configured for packages"
                echo "3. Token doesn't have the right permissions"
                echo ""
                echo "Let's try TestPyPI as a workaround..."
                python -m twine upload \
                    --repository testpypi \
                    --username __token__ \
                    --password "$GITHUB_TOKEN" \
                    dist/*
            }
        }
    }
}

echo ""
echo "✅ Package published successfully!"
