#!/bin/bash

# Build and serve documentation with a single command
# Usage: ./scripts/build-and-serve.sh

set -e

echo "🔨 Building static documentation..."
npm run build:static

if [ $? -ne 0 ]; then
    echo "❌ Build failed"
    exit 1
fi

echo ""
echo "✅ Build complete!"
echo ""
echo "🚀 Starting local server..."
echo ""

# Serve on port 8000
./scripts/serve-static.sh 8000
