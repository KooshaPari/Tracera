#!/bin/bash
set -euo pipefail

ARCH=$(uname -m)
BIN_DIR="/usr/local/bin"

echo "Installing Prometheus exporters for Linux..."

# Postgres Exporter
echo "- postgres_exporter"
wget -q https://github.com/prometheus-community/postgres_exporter/releases/latest/download/postgres_exporter-*linux-${ARCH}.tar.gz -O postgres_exporter.tar.gz
tar -xzf postgres_exporter.tar.gz
sudo mv postgres_exporter-*/postgres_exporter $BIN_DIR/
rm -rf postgres_exporter*

# Redis Exporter
echo "- redis_exporter"
wget -q https://github.com/oliver006/redis_exporter/releases/latest/download/redis_exporter-*linux-${ARCH}.tar.gz -O redis_exporter.tar.gz
tar -xzf redis_exporter.tar.gz
sudo mv redis_exporter-*/redis_exporter $BIN_DIR/
rm -rf redis_exporter*

# Node Exporter
echo "- node_exporter"
wget -q https://github.com/prometheus/node_exporter/releases/latest/download/node_exporter-*linux-${ARCH}.tar.gz -O node_exporter.tar.gz
tar -xzf node_exporter.tar.gz
sudo mv node_exporter-*/node_exporter $BIN_DIR/
rm -rf node_exporter*

echo "✅ Exporters installed to $BIN_DIR"
