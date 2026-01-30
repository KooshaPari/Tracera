#!/bin/bash
# BMM MCP - Quick Install (uses current Python environment)

set -e

echo "🚀 BMM MCP Quick Install"
echo "========================"
echo ""

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Use current Python
PYTHON_CMD="python"

echo "Using Python: $(which $PYTHON_CMD)"
echo "Version: $($PYTHON_CMD --version)"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
$PYTHON_CMD -m pip install -q fastmcp==3.0.0b1 mcp==1.25.0 typer rich pyyaml pydantic

echo "✅ Dependencies installed"
echo ""

# Make executable
echo "🔧 Making scripts executable..."
chmod +x "$SCRIPT_DIR/bmm_server.py"
chmod +x "$SCRIPT_DIR/bmm_cli.py"
chmod +x "$SCRIPT_DIR/run_bmm.sh"

echo "✅ Scripts ready"
echo ""

# Test
echo "🧪 Testing..."
if $PYTHON_CMD -c "import fastmcp" 2>/dev/null; then
    echo "✅ FastMCP available"
else
    echo "⚠️  FastMCP import issue (may still work)"
fi

if $PYTHON_CMD -c "import typer, rich" 2>/dev/null; then
    echo "✅ Typer & Rich available"
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "Try: ./scripts/mcp/run_bmm.sh status"
echo "Or:  python scripts/mcp/bmm_cli.py status"
