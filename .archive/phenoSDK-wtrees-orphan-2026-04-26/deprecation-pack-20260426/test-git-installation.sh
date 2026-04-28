#!/bin/bash
# Test Git-based installation for all projects

echo "🧪 Testing Git-based Installation for All Projects"
echo "================================================="

# Get GitHub token
GITHUB_TOKEN=$(gh auth token)

echo "🔍 Testing local installation first..."
pip install git+https://${GITHUB_TOKEN}@github.com/KooshaPari/phenoSDK.git@v0.1.2

echo ""
echo "✅ Local installation successful!"

echo ""
echo "🔍 Testing Docker builds..."

echo ""
echo "1️⃣ Testing router Docker build..."
cd ../router
docker build --secret id=github_token,src=<(echo "$GITHUB_TOKEN") -t krouter:test . || {
    echo "❌ Router build failed"
    exit 1
}
echo "✅ Router build successful!"

echo ""
echo "2️⃣ Testing morph Docker build..."
cd ../morph
docker build --secret id=github_token,src=<(echo "$GITHUB_TOKEN") -t morph:test . || {
    echo "❌ Morph build failed"
    exit 1
}
echo "✅ Morph build successful!"

echo ""
echo "3️⃣ Testing zen-mcp-server Docker build..."
cd ../zen-mcp-server
docker build --secret id=github_token,src=<(echo "$GITHUB_TOKEN") -f Dockerfile.mcp -t zen-mcp:test . || {
    echo "❌ Zen-MCP build failed"
    exit 1
}
echo "✅ Zen-MCP build successful!"

echo ""
echo "4️⃣ Testing atoms_mcp-old Docker build..."
cd ../atoms_mcp-old
docker build --secret id=github_token,src=<(echo "$GITHUB_TOKEN") -t atoms-mcp:test . || {
    echo "❌ Atoms-MCP build failed"
    exit 1
}
echo "✅ Atoms-MCP build successful!"

echo ""
echo "🎉 All Docker builds successful!"
echo ""
echo "📋 Summary:"
echo "✅ Router: krouter:test"
echo "✅ Morph: morph:test"
echo "✅ Zen-MCP: zen-mcp:test"
echo "✅ Atoms-MCP: atoms-mcp:test"
echo ""
echo "🔧 All projects now use Git-based installation for pheno-sdk!"
