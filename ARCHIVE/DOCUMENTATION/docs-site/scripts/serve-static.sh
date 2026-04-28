#!/bin/bash

# Serve static documentation locally using Python's built-in HTTP server
# Usage: ./scripts/serve-static.sh [port]

PORT="${1:-8000}"
DOCS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/out"

if [ ! -d "$DOCS_DIR" ]; then
    echo "❌ Error: ./out directory not found"
    echo "📝 Please run: npm run build:static"
    exit 1
fi

echo "📚 Starting local documentation server..."
echo "🌐 URL: http://localhost:$PORT"
echo "📁 Serving: $DOCS_DIR"
echo ""
echo "💡 Tip: Visit http://localhost:$PORT in your browser"
echo "🛑 Stop server with: Ctrl+C"
echo ""

cd "$DOCS_DIR"
python3 -m http.server $PORT
