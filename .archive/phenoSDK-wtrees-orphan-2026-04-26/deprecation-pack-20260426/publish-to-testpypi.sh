#!/bin/bash
# Publish to TestPyPI as a temporary solution

echo "🚀 Publishing to TestPyPI (Temporary Solution)"
echo "============================================="

# Get GitHub token
GITHUB_TOKEN=$(gh auth token)

echo "📦 Publishing to TestPyPI..."
python -m twine upload \
    --repository testpypi \
    --username __token__ \
    --password "$GITHUB_TOKEN" \
    dist/*

echo ""
echo "✅ Package published to TestPyPI!"
echo ""
echo "📋 Next steps:"
echo "1. Update all projects to use TestPyPI temporarily:"
echo "   # Update .pip/pip.conf in all projects:"
echo "   [global]"
echo "   index-url = https://test.pypi.org/simple"
echo "   extra-index-url = https://pypi.org/simple"
echo ""
echo "2. Test Docker builds:"
echo "   cd ../router && ./build-with-github-packages.sh"
echo "   cd ../morph && ./build-with-github-packages.sh"
echo ""
echo "3. Test local installation:"
echo "   pip install --index-url https://test.pypi.org/simple --extra-index-url https://pypi.org/simple pheno-sdk"
