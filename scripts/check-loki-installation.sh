#!/bin/bash
# Check if Loki and Promtail are installed and provide installation instructions

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "Checking Loki and Promtail installation..."
echo ""

LOKI_INSTALLED=false
PROMTAIL_INSTALLED=false

# Check Loki
if command -v loki &> /dev/null; then
    LOKI_VERSION=$(loki --version 2>&1 | head -n 1)
    echo -e "${GREEN}✓${NC} Loki is installed: $LOKI_VERSION"
    LOKI_INSTALLED=true
else
    echo -e "${RED}✗${NC} Loki is not installed"
fi

# Check Promtail
if command -v promtail &> /dev/null; then
    PROMTAIL_VERSION=$(promtail --version 2>&1 | head -n 1)
    echo -e "${GREEN}✓${NC} Promtail is installed: $PROMTAIL_VERSION"
    PROMTAIL_INSTALLED=true
else
    echo -e "${RED}✗${NC} Promtail is not installed"
fi

echo ""

# Provide installation instructions if needed
if [ "$LOKI_INSTALLED" = false ] || [ "$PROMTAIL_INSTALLED" = false ]; then
    echo -e "${YELLOW}Installation Instructions:${NC}"
    echo ""
    echo "On macOS (Homebrew):"
    echo "  brew install grafana/grafana/loki"
    echo "  brew install grafana/grafana/promtail"
    echo ""
    echo "On Linux:"
    echo "  # Download Loki"
    echo "  curl -O -L https://github.com/grafana/loki/releases/download/v2.9.3/loki-linux-amd64.zip"
    echo "  unzip loki-linux-amd64.zip"
    echo "  chmod a+x loki-linux-amd64"
    echo "  sudo mv loki-linux-amd64 /usr/local/bin/loki"
    echo ""
    echo "  # Download Promtail"
    echo "  curl -O -L https://github.com/grafana/loki/releases/download/v2.9.3/promtail-linux-amd64.zip"
    echo "  unzip promtail-linux-amd64.zip"
    echo "  chmod a+x promtail-linux-amd64"
    echo "  sudo mv promtail-linux-amd64 /usr/local/bin/promtail"
    echo ""
    exit 1
else
    echo -e "${GREEN}All dependencies are installed!${NC}"
    echo ""
    echo "You can now start the services with:"
    echo "  make dev"
    echo ""
    echo "Access Grafana at: http://localhost:3000"
    echo "Query logs with Loki in the Explore tab"
fi
