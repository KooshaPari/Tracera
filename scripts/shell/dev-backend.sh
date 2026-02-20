#!/bin/bash
# Development backend server with hot reload

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting TraceRTM Backend Server (Hot Reload Enabled)${NC}"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}Error: python3 not found. Please install Python 3.12+${NC}"
    exit 1
fi

# Check if we're in the project root
if [ ! -f "src/tracertm/api/main.py" ]; then
    echo -e "${YELLOW}Error: Please run this script from the project root directory${NC}"
    exit 1
fi

# Set environment variables if .env exists
if [ -f ".env" ]; then
    echo -e "${GREEN}Loading environment variables from .env${NC}"
    export $(cat .env | grep -v '^#' | xargs)
fi

# Default CORS origins if not set
if [ -z "$CORS_ORIGINS" ]; then
    export CORS_ORIGINS="http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000"
    echo -e "${YELLOW}Using default CORS origins: $CORS_ORIGINS${NC}"
    echo -e "${YELLOW}Set CORS_ORIGINS environment variable to customize${NC}"
fi

echo ""
echo -e "${GREEN}Backend will be available at:${NC}"
echo "  API:      http://localhost:8000"
echo "  Health:   http://localhost:8000/health"
echo "  WebSocket: ws://localhost:8000/ws"
echo ""
echo -e "${GREEN}Hot reload is enabled - changes will auto-reload${NC}"
echo ""

# Run the backend server
# Set PYTHONPATH to prioritize source code over installed package
# Use absolute path to ensure it works even after cd
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
export PYTHONPATH="${PROJECT_ROOT}/src:${PYTHONPATH:-}"
cd src/tracertm/api
python3 -m uvicorn main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --reload-dir ../../.. \
    --log-level info
