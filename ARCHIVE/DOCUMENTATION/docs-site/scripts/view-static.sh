#!/bin/bash

# Open the static documentation in your default browser
# Usage: ./scripts/view-static.sh

DOCS_FILE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/out/index.html"

if [ ! -f "$DOCS_FILE" ]; then
    echo "❌ Error: Documentation not built"
    echo "📝 Please run: npm run build:static"
    exit 1
fi

echo "📖 Opening documentation in your browser..."
echo "📁 File: $DOCS_FILE"

# Use 'open' for macOS, 'xdg-open' for Linux, 'start' for Windows
if [[ "$OSTYPE" == "darwin"* ]]; then
    open "$DOCS_FILE"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    xdg-open "$DOCS_FILE"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    start "$DOCS_FILE"
else
    echo "📋 Please manually open: $DOCS_FILE"
fi
