#!/bin/bash
# Use local package installation as immediate solution

echo "🚀 Using Local Package Installation (Immediate Solution)"
echo "======================================================="

echo "📦 Copying package files to all projects..."

# Copy wheel file to each project
cp dist/pheno_sdk-0.1.2-py3-none-any.whl ../router/
cp dist/pheno_sdk-0.1.2-py3-none-any.whl ../morph/
cp dist/pheno_sdk-0.1.2-py3-none-any.whl ../zen-mcp-server/
cp dist/pheno_sdk-0.1.2-py3-none-any.whl ../atoms_mcp-old/

echo "✅ Package files copied to all projects"

echo ""
echo "📝 Next steps:"
echo "1. Update Dockerfiles to install local package first"
echo "2. Test Docker builds"
echo "3. This provides immediate functionality while we resolve GitHub Packages"

echo ""
echo "🔧 To update Dockerfiles, add this before the main dependency installation:"
echo "COPY pheno_sdk-0.1.2-py3-none-any.whl ./"
echo "RUN pip install pheno_sdk-0.1.2-py3-none-any.whl"
