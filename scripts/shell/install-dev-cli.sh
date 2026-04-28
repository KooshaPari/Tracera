#!/bin/bash
# Install development CLI dependencies

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Installing TraceRTM Development CLI..."
echo

# Check if virtual environment exists
if [ ! -d "$PROJECT_ROOT/.venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$PROJECT_ROOT/.venv"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "$PROJECT_ROOT/.venv/bin/activate"

# Install dependencies
echo "Installing dev CLI dependencies..."
pip install -r "$SCRIPT_DIR/dev-requirements.txt"

echo
echo "✅ Development CLI installed successfully!"
echo
echo "Usage:"
echo "  ./scripts/dev --help"
echo "  make dev-health"
echo "  make dev-seed"
echo
echo "See scripts/docs/README_DEV_CLI.md for full documentation."
