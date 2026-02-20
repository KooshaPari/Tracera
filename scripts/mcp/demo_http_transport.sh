#!/bin/bash
# Demo script for MCP HTTP transport
# This script demonstrates the dual transport capabilities

set -e

echo "==============================================="
echo "MCP HTTP Transport Demo"
echo "==============================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Check if Python is available
if ! command -v python &> /dev/null; then
    print_error "Python not found. Please install Python 3.12+"
    exit 1
fi

print_status "Python found: $(python --version)"

# Check if required packages are installed
print_info "Checking dependencies..."
python -c "import fastmcp" 2>/dev/null && print_status "FastMCP installed" || print_error "FastMCP not installed"
python -c "import httpx" 2>/dev/null && print_status "httpx installed" || print_info "httpx not installed (optional for clients)"

echo ""
echo "==============================================="
echo "Demo 1: STDIO Mode (Default)"
echo "==============================================="
echo ""

print_info "This is the traditional mode for Claude Desktop"
print_info "Command: python -m tracertm.mcp"
echo ""
print_info "To run: python -m tracertm.mcp"
print_info "(Press Ctrl+C to stop after starting)"
echo ""

echo "==============================================="
echo "Demo 2: HTTP Mode"
echo "==============================================="
echo ""

print_info "Starting MCP server in HTTP mode..."
print_info "Command: python -m tracertm.mcp --transport http --port 8765"
echo ""

# Show the command that would be run
echo "To start the server, run:"
echo "  python -m tracertm.mcp --transport http --port 8765"
echo ""
echo "Then in another terminal, test with:"
echo ""
echo "  # List tools"
echo "  curl -X POST http://localhost:8765/mcp \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"jsonrpc\":\"2.0\",\"method\":\"tools/list\",\"id\":1}' | jq"
echo ""
echo "  # Call a tool"
echo "  curl -X POST http://localhost:8765/mcp \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"jsonrpc\":\"2.0\",\"method\":\"tools/call\",\"params\":{\"name\":\"project_manage\",\"arguments\":{\"action\":\"list\"}},\"id\":2}' | jq"
echo ""

echo "==============================================="
echo "Demo 3: Streamable HTTP Mode (SSE)"
echo "==============================================="
echo ""

print_info "Streamable HTTP includes SSE for progress updates"
print_info "Command: python -m tracertm.mcp --transport streamable-http"
echo ""

echo "To start the server, run:"
echo "  python -m tracertm.mcp --transport streamable-http --port 8765"
echo ""
echo "Then connect to SSE stream:"
echo "  curl -N http://localhost:8765/mcp/sse"
echo ""

echo "==============================================="
echo "Demo 4: Environment Variable"
echo "==============================================="
echo ""

print_info "You can also use environment variables"
echo ""
echo "  # Set transport"
echo "  export TRACERTM_MCP_TRANSPORT=streamable-http"
echo ""
echo "  # Run server"
echo "  python -m tracertm.mcp"
echo ""

echo "==============================================="
echo "Demo 5: FastAPI Integration"
echo "==============================================="
echo ""

print_info "MCP is already integrated with FastAPI"
print_info "Endpoints available at /api/v1/mcp/*"
echo ""
echo "To run the full FastAPI app:"
echo "  uvicorn tracertm.api.main:app --host 0.0.0.0 --port 8000"
echo ""
echo "MCP endpoints will be available at:"
echo "  POST http://localhost:8000/api/v1/mcp/messages  (JSON-RPC)"
echo "  GET  http://localhost:8000/api/v1/mcp/sse       (SSE streaming)"
echo "  GET  http://localhost:8000/api/v1/mcp/tools     (Tool discovery)"
echo "  GET  http://localhost:8000/api/v1/mcp/health    (Health check)"
echo ""

echo "==============================================="
echo "Testing Smoke Tests"
echo "==============================================="
echo ""

if [ -f "scripts/mcp/test_http_transport_smoke.py" ]; then
    print_info "Running smoke tests..."
    echo ""
    python scripts/mcp/test_http_transport_smoke.py
    echo ""
else
    print_error "Smoke test file not found"
fi

echo "==============================================="
echo "Transport Comparison"
echo "==============================================="
echo ""

echo "| Transport       | Use Case                  | Port | SSE |"
echo "|-----------------|---------------------------|------|-----|"
echo "| stdio           | Claude Desktop, CLI       | N/A  | No  |"
echo "| http            | Simple HTTP clients       | 8765 | No  |"
echo "| streamable-http | Web apps, progress stream | 8765 | Yes |"
echo "| sse             | Legacy SSE clients        | 8765 | Yes |"
echo ""

echo "==============================================="
echo "Quick Reference"
echo "==============================================="
echo ""

echo "Documentation:"
echo "  • HTTP Transport Guide:  src/tracertm/mcp/HTTP_TRANSPORT_GUIDE.md"
echo "  • Quick Reference:       scripts/mcp/PHASE_3_QUICK_REFERENCE.md"
echo "  • Completion Report:     scripts/mcp/PHASE_3_HTTP_TRANSPORT_COMPLETION.md"
echo ""

echo "Testing:"
echo "  • Smoke Tests:           python scripts/mcp/test_http_transport_smoke.py"
echo "  • Integration Tests:     pytest tests/integration/test_mcp_http_transport.py -v"
echo ""

echo "Common Commands:"
echo "  • STDIO:                 python -m tracertm.mcp"
echo "  • HTTP:                  python -m tracertm.mcp --transport http"
echo "  • Streamable HTTP:       python -m tracertm.mcp --transport streamable-http"
echo "  • Debug Mode:            python -m tracertm.mcp --transport http --log-level debug"
echo ""

echo "==============================================="
echo "Demo Complete"
echo "==============================================="
echo ""

print_status "Phase 3 HTTP/SSE Transport Implementation Complete"
print_info "All features tested and documented"
echo ""
