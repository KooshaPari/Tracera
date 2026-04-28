#!/bin/bash
# Use Git-based installation instead of GitHub Packages

echo "🚀 Using Git-based Installation (Simple & Reliable)"
echo "=================================================="

# Get GitHub token
GITHUB_TOKEN=$(gh auth token)

echo "📦 Publishing to Git repository..."

# First, let's commit and push the current changes to the phenoSDK repository
echo "1️⃣ Committing and pushing changes to phenoSDK repository..."
git add .
git commit -m "Release pheno-sdk v0.1.2 for private package distribution" || echo "No changes to commit"
git push origin main

echo ""
echo "2️⃣ Creating a release tag..."
git tag v0.1.2
git push origin v0.1.2

echo ""
echo "✅ Git repository updated with release tag!"
echo ""
echo "📋 Now update all projects to use Git-based installation:"
echo ""
echo "🔧 Update pyproject.toml in all projects:"
echo "dependencies = ["
echo "    \"pheno-sdk @ git+https://${GITHUB_TOKEN}@github.com/KooshaPari/phenoSDK.git@v0.1.2\","
echo "    # ... other dependencies"
echo "]"
echo ""
echo "🔧 Update Dockerfiles to use Git installation:"
echo "RUN pip install git+https://${GITHUB_TOKEN}@github.com/KooshaPari/phenoSDK.git@v0.1.2"
echo ""
echo "🧪 Test installation:"
echo "pip install git+https://${GITHUB_TOKEN}@github.com/KooshaPari/phenoSDK.git@v0.1.2"
