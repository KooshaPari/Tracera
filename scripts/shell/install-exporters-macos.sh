#!/bin/bash
set -euo pipefail

ARCH=$(uname -m)
# Install to user's local bin (no sudo needed)
BIN_DIR="$HOME/.local/bin"
mkdir -p "$BIN_DIR"

# Map architecture names
case $ARCH in
  arm64)
    DOWNLOAD_ARCH="arm64"
    ;;
  x86_64)
    DOWNLOAD_ARCH="amd64"
    ;;
  *)
    echo "Unsupported architecture: $ARCH"
    exit 1
    ;;
esac

echo "Installing Prometheus exporters for macOS ($DOWNLOAD_ARCH)..."
echo ""

# Postgres Exporter
echo "📊 Installing postgres_exporter..."
wget -q "https://github.com/prometheus-community/postgres_exporter/releases/latest/download/postgres_exporter-0.15.0.darwin-${DOWNLOAD_ARCH}.tar.gz" -O postgres_exporter.tar.gz 2>/dev/null || \
  wget -q $(curl -s https://api.github.com/repos/prometheus-community/postgres_exporter/releases/latest | grep "browser_download_url.*darwin-${DOWNLOAD_ARCH}.tar.gz" | cut -d '"' -f 4) -O postgres_exporter.tar.gz
tar -xzf postgres_exporter.tar.gz
mv postgres_exporter-*/postgres_exporter "$BIN_DIR/"
rm -rf postgres_exporter*
echo "✅ postgres_exporter installed"

# Redis Exporter
echo "📊 Installing redis_exporter..."
wget -q "https://github.com/oliver006/redis_exporter/releases/latest/download/redis_exporter-v1.58.0.darwin-${DOWNLOAD_ARCH}.tar.gz" -O redis_exporter.tar.gz 2>/dev/null || \
  wget -q $(curl -s https://api.github.com/repos/oliver006/redis_exporter/releases/latest | grep "browser_download_url.*darwin-${DOWNLOAD_ARCH}.tar.gz" | cut -d '"' -f 4) -O redis_exporter.tar.gz
tar -xzf redis_exporter.tar.gz
mv redis_exporter-*/redis_exporter "$BIN_DIR/"
rm -rf redis_exporter*
echo "✅ redis_exporter installed"

echo ""
echo "✅ All exporters installed to $BIN_DIR"
echo ""
echo "⚠️  Make sure $BIN_DIR is in your PATH"
echo "   Add to ~/.zshrc or ~/.bashrc: export PATH=\"\$HOME/.local/bin:\$PATH\""
echo ""
echo "Verify installation:"
echo "  $BIN_DIR/postgres_exporter --version"
echo "  $BIN_DIR/redis_exporter --version"
