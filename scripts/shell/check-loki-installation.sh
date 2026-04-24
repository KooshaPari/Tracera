#!/bin/bash
# Check if Loki and Grafana Alloy are installed and provide installation instructions

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "Checking Loki and Grafana Alloy installation..."
echo ""

LOKI_INSTALLED=false
ALLOY_INSTALLED=false

# Check Loki
if command -v loki &> /dev/null; then
    LOKI_VERSION=$(loki --version 2>&1 | head -n 1)
    echo -e "${GREEN}✓${NC} Loki is installed: $LOKI_VERSION"
    LOKI_INSTALLED=true
else
    echo -e "${RED}✗${NC} Loki is not installed"
fi

# Check Grafana Alloy. Another command named "alloy" may exist, so verify the
# Grafana Alloy run flags instead of trusting the binary name.
for candidate in "${GRAFANA_ALLOY_BIN:-}" alloy grafana-alloy "$HOME/.local/bin/grafana-alloy"; do
    [ -z "$candidate" ] && continue
    if command -v "$candidate" &> /dev/null && "$candidate" run --help 2>&1 | grep -q -- "--server.http.listen-addr"; then
        ALLOY_VERSION=$("$candidate" --version 2>&1 | head -n 1)
        echo -e "${GREEN}✓${NC} Grafana Alloy is installed: $ALLOY_VERSION"
        ALLOY_INSTALLED=true
        break
    fi
done

if [ "$ALLOY_INSTALLED" = false ]; then
    echo -e "${RED}✗${NC} Grafana Alloy is not installed or is shadowed by another alloy binary"
fi

echo ""

# Provide installation instructions if needed
if [ "$LOKI_INSTALLED" = false ] || [ "$ALLOY_INSTALLED" = false ]; then
    echo -e "${YELLOW}Installation Instructions:${NC}"
    echo ""
    echo "On macOS (Homebrew):"
    echo "  brew install grafana/grafana/loki"
    echo "  brew install grafana-alloy"
    echo "  # If alloy-analyzer or another binary owns the alloy command:"
    echo "  # install the official Grafana Alloy release as grafana-alloy"
    echo "  export GRAFANA_ALLOY_BIN=/path/to/grafana-alloy"
    echo ""
    echo "On Linux:"
    echo "  # Download Loki"
    echo "  curl -O -L https://github.com/grafana/loki/releases/download/v2.9.3/loki-linux-amd64.zip"
    echo "  unzip loki-linux-amd64.zip"
    echo "  chmod a+x loki-linux-amd64"
    echo "  sudo mv loki-linux-amd64 /usr/local/bin/loki"
    echo ""
    echo "  # Install Alloy using Grafana's package instructions:"
    echo "  # https://grafana.com/docs/alloy/latest/set-up/install/linux/"
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
