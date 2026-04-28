#!/bin/bash

# TraceRTM Phase 3 - Setup Verification Script

echo "🔍 TraceRTM Phase 3 - Setup Verification"
echo "========================================"
echo ""

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: Not in the web app directory"
    echo "   Please run from: frontend/apps/web/"
    exit 1
fi

echo "✅ Directory check passed"
echo ""

# Check Node.js/Bun
echo "📦 Checking runtime..."
if command -v bun &> /dev/null; then
    BUN_VERSION=$(bun --version)
    echo "✅ Bun found: v$BUN_VERSION"
else
    echo "⚠️  Bun not found, checking Node..."
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        echo "✅ Node.js found: $NODE_VERSION"
    else
        echo "❌ Neither Bun nor Node.js found"
        exit 1
    fi
fi
echo ""

# Check package.json dependencies
echo "📋 Checking package.json..."
REQUIRED_DEPS=("react" "vite" "typescript" "@tanstack/react-query" "zustand")
MISSING_DEPS=()

for dep in "${REQUIRED_DEPS[@]}"; do
    if grep -q "\"$dep\"" package.json; then
        echo "✅ $dep found"
    else
        echo "❌ $dep missing"
        MISSING_DEPS+=("$dep")
    fi
done
echo ""

if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    echo "⚠️  Missing dependencies detected. Run: bun install"
    echo ""
fi

# Check critical files
echo "📁 Checking critical files..."
FILES=(
    "src/api/types.ts"
    "src/api/endpoints.ts"
    "src/api/client.ts"
    "src/api/websocket.ts"
    "src/stores/authStore.ts"
    "src/stores/itemsStore.ts"
    "src/stores/websocketStore.ts"
    "src/hooks/useAuth.ts"
    "src/hooks/useItemsQuery.ts"
    "src/hooks/useGraph.ts"
    "src/hooks/useSearch.ts"
    "src/hooks/useWebSocketHook.ts"
    "src/providers/AppProviders.tsx"
)

MISSING_FILES=()
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file missing"
        MISSING_FILES+=("$file")
    fi
done
echo ""

# Check environment
echo "🔧 Checking environment..."
if [ -f ".env.local" ]; then
    echo "✅ .env.local found"
    if grep -q "VITE_API_URL" .env.local; then
        API_URL=$(grep "VITE_API_URL" .env.local | cut -d '=' -f2)
        echo "   API URL: $API_URL"
    fi
else
    echo "⚠️  .env.local not found"
    echo "   Create it with: echo 'VITE_API_URL=http://localhost:8000' > .env.local"
fi
echo ""

# Check build files
echo "🏗️  Checking build configuration..."
BUILD_FILES=("vite.config.ts" "tsconfig.json" "tailwind.config.ts")
for file in "${BUILD_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file missing"
    fi
done
echo ""

# Summary
echo "📊 Summary"
echo "=========="
if [ ${#MISSING_DEPS[@]} -eq 0 ] && [ ${#MISSING_FILES[@]} -eq 0 ]; then
    echo "✅ All checks passed!"
    echo ""
    echo "Ready to start development:"
    echo "  bun run dev"
    echo ""
else
    echo "⚠️  Some issues found:"
    if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
        echo "   - Missing dependencies: ${MISSING_DEPS[*]}"
    fi
    if [ ${#MISSING_FILES[@]} -gt 0 ]; then
        echo "   - Missing files: ${MISSING_FILES[*]}"
    fi
    echo ""
    echo "Run: bun install"
    echo ""
fi

# Check if backend is running
echo "🔌 Checking backend connection..."
if command -v curl &> /dev/null; then
    API_URL=${VITE_API_URL:-"http://localhost:8000"}
    if curl -s -o /dev/null -w "%{http_code}" "$API_URL/health" | grep -q "200"; then
        echo "✅ Backend is running at $API_URL"
    else
        echo "⚠️  Backend not responding at $API_URL"
        echo "   Make sure the backend is running on port 8000"
    fi
else
    echo "⚠️  curl not found, skipping backend check"
fi
echo ""

echo "✨ Verification complete!"
echo ""
echo "Next steps:"
echo "1. Install dependencies: bun install"
echo "2. Set environment: echo 'VITE_API_URL=http://localhost:8000' > .env.local"
echo "3. Start dev server: bun run dev"
echo "4. Open browser: http://localhost:5173"
